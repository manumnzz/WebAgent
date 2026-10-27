"""Capture only a project's public static site; never start Calendar or submit forms."""

from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

from PIL import Image
from visual.models import BrowserFinding, CaptureReport, Screenshot

VIEWPORTS = {
    "desktop": (1440, 1000),
    "tablet": (768, 1024),
    "mobile": (390, 844),
    "narrow": (360, 800),
}
MAX_HEIGHT = 14000


class SiteHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_head(self):
        root = Path(self.directory).resolve()
        target = Path(self.translate_path(self.path)).resolve()
        if (
            not target.is_relative_to(root)
            or target.is_dir()
            and not (target / "index.html").is_file()
        ):
            self.send_error(404)
            return None
        return super().send_head()


@contextmanager
def serve_site(website: Path):
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(SiteHandler, directory=str(website.resolve()))
    )
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=2)


DIAGNOSTICS = r"""() => {
 const visible = e => { const s=getComputedStyle(e), r=e.getBoundingClientRect();
   return s.display!=='none' && s.visibility!=='hidden' && r.width>0 && r.height>0; };
 const label = e => e.tagName.toLowerCase()+(e.id?'#'+e.id:'')+
   (typeof e.className==='string'?'.'+e.className.trim().split(/\s+/).join('.'):'');
 const elements=[...document.querySelectorAll('main *, header *, footer *')];
 return {
  overflow: Math.max(document.documentElement.scrollWidth,document.body.scrollWidth)>innerWidth+2,
  outside: elements.filter(e=>{const r=e.getBoundingClientRect(); return visible(e)&&
    (r.left < -2 || r.right > innerWidth+2);}).slice(0,12).map(label),
  broken_images:[...document.images].filter(e=>visible(e)&&(!e.complete||!e.naturalWidth))
    .map(e=>e.getAttribute('src')),
  small_text:elements.filter(e=>visible(e)&&e.childElementCount===0&&e.textContent.trim()&&
    parseFloat(getComputedStyle(e).fontSize)<14).slice(0,12).map(label),
  hidden_content:elements.filter(e=>e.matches('h1,h2,p,a')&&visible(e)&&e.textContent.trim()&&
    [e,...(function*(x){while(x.parentElement){x=x.parentElement;yield x;}})(e)]
      .some(x=>Number(getComputedStyle(x).opacity)===0)).slice(0,12).map(label),
  height:document.documentElement.scrollHeight
 };
}"""


def capture_site(website: Path, output: Path) -> CaptureReport:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError(
            "Instala requirements-visual.txt y ejecuta python -m playwright install chromium."
        ) from error
    if not (website / "index.html").is_file():
        raise FileNotFoundError("Falta website/index.html.")
    output.mkdir(parents=True, exist_ok=False)
    report = CaptureReport()
    with serve_site(website) as origin, sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for name, (width, height) in VIEWPORTS.items():
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1,
                    reduced_motion="reduce",
                    service_workers="block",
                )

                # Only local public files and font resources. No backend, analytics or form submission.
                def route_request(route):
                    request = route.request
                    parsed = urlparse(request.url)
                    allowed = (
                        request.url.startswith(origin + "/")
                        or parsed.hostname
                        in {"fonts.googleapis.com", "fonts.gstatic.com"}
                        or parsed.scheme in {"data", "blob"}
                    )
                    if allowed and request.method in {"GET", "HEAD"}:
                        route.continue_()
                    else:
                        route.abort()

                context.route("**/*", route_request)
                page = context.new_page()
                page.on(
                    "pageerror",
                    lambda error, viewport=name: report.findings.append(
                        BrowserFinding(
                            code="javascript_error",
                            viewport=viewport,
                            detail=str(error),
                            blocking=True,
                        )
                    ),
                )
                page.goto(origin, wait_until="load", timeout=20000)
                page.evaluate(
                    "() => Promise.race([document.fonts.ready, new Promise(r=>setTimeout(r,3000))])"
                )
                # Trigger lazy images and observers without forcing hidden content visible.
                total = min(
                    page.evaluate("document.documentElement.scrollHeight"), MAX_HEIGHT
                )
                for y in range(0, total, height):
                    page.evaluate("(y) => window.scrollTo(0,y)", y)
                    page.wait_for_timeout(60)
                page.evaluate("window.scrollTo(0,0)")
                page.wait_for_timeout(250)
                diagnostic = page.evaluate(DIAGNOSTICS)
                for code, key, blocking in [
                    ("horizontal_overflow", "overflow", True),
                    ("broken_images", "broken_images", True),
                    ("small_text", "small_text", False),
                    ("hidden_content", "hidden_content", True),
                ]:
                    if diagnostic[key]:
                        detail = str(
                            diagnostic["outside"]
                            if key == "overflow"
                            else diagnostic[key]
                        )
                        report.findings.append(
                            BrowserFinding(
                                code=code,
                                viewport=name,
                                detail=detail,
                                blocking=blocking,
                            )
                        )
                if diagnostic["height"] > MAX_HEIGHT:
                    report.findings.append(
                        BrowserFinding(
                            code="capture_truncated",
                            viewport=name,
                            detail=f"Página de {diagnostic['height']}px; captura limitada a {MAX_HEIGHT}px.",
                            blocking=True,
                        )
                    )
                if name in {"desktop", "mobile"}:
                    hero = output / f"{name}-hero.png"
                    page.screenshot(path=str(hero), animations="disabled")
                    report.screenshots.append(
                        Screenshot(
                            name=f"{name}-hero",
                            path=hero.name,
                            width=width,
                            height=height,
                        )
                    )
                    full = output / f"{name}-full.png"
                    page.screenshot(
                        path=str(full),
                        full_page=True,
                        clip={
                            "x": 0,
                            "y": 0,
                            "width": width,
                            "height": min(diagnostic["height"], MAX_HEIGHT),
                        },
                        animations="disabled",
                    )
                    report.screenshots.append(
                        Screenshot(
                            name=f"{name}-full",
                            path=full.name,
                            width=width,
                            height=min(diagnostic["height"], MAX_HEIGHT),
                        )
                    )
                    with Image.open(full) as image:
                        image.thumbnail((1440, 2400))
                        image.save(output / f"{name}-overview.png")
                context.close()
            # Check progressive enhancement independently of reduced-motion CSS.
            context = browser.new_context(
                viewport={"width": 390, "height": 844}, java_script_enabled=False
            )
            context.route("**/*", route_request)
            page = context.new_page()
            page.goto(origin, wait_until="load", timeout=20000)
            hidden = page.evaluate(DIAGNOSTICS)["hidden_content"]
            if hidden:
                report.findings.append(
                    BrowserFinding(
                        code="no_js_hidden_content",
                        viewport="mobile-no-js",
                        detail=str(hidden),
                        blocking=True,
                    )
                )
            page.screenshot(path=str(output / "mobile-no-js.png"), full_page=False)
            context.close()
        finally:
            browser.close()
    (output / "capture.json").write_text(
        report.model_dump_json(indent=2), encoding="utf-8"
    )
    return report


def review_images(output: Path) -> list[Path]:
    # Detailed first screens plus overviews: bound image token cost and preserve legibility.
    return [
        output / name
        for name in (
            "desktop-hero.png",
            "mobile-hero.png",
            "desktop-overview.png",
            "mobile-overview.png",
            "mobile-no-js.png",
        )
    ]


def check_browser() -> None:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            browser.close()
    except Exception as error:
        raise RuntimeError(
            "Instala .venv/bin/python -m pip install -r requirements-visual.txt "
            "y .venv/bin/python -m playwright install chromium."
        ) from error
