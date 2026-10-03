from html.parser import HTMLParser


class WebsiteHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()

        self.start_tags: set[str] = set()
        self.end_tags: set[str] = set()

        self.stylesheets: list[str] = []
        self.scripts: list[str] = []
        self.ids: list[str] = []
        self.internal_links: list[str] = []

    def handle_starttag(self, tag, attrs):

        tag = tag.lower()

        self.start_tags.add(tag)

        attrs_dict = dict(attrs)

        if tag == "a":

            href = attrs_dict.get("href")

            if href and href.startswith("#") and len(href) > 1:
                self.internal_links.append(href[1:])

        if tag == "link":

            rel = attrs_dict.get("rel", "")
            href = attrs_dict.get("href")

            if "stylesheet" in rel.lower().split() and href:
                self.stylesheets.append(href)

        if tag == "script":

            src = attrs_dict.get("src")

            if src:
                self.scripts.append(src)

        element_id = attrs_dict.get("id")

        if element_id:
            self.ids.append(element_id)

    def handle_endtag(self, tag):

        self.end_tags.add(tag.lower())