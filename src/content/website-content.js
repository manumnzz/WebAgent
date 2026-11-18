(() => {
  "use strict";

  const script = document.currentScript;
  const weekdays = {
    monday: "Lunes",
    tuesday: "Martes",
    wednesday: "Miércoles",
    thursday: "Jueves",
    friday: "Viernes",
    saturday: "Sábado",
    sunday: "Domingo"
  };

  const collections = {
    services: content => content.services ?? [],
    opening_hours: content => (content.opening_hours ?? []).map(entry => ({
      day: weekdays[entry.weekday],
      hours: entry.hours
    })),
    gallery: content => (content.gallery ?? []).filter(image =>
      /^assets\/[A-Za-z0-9_-]+\.(?:jpg|jpeg|png|webp)$/.test(image.path)
    )
  };

  function setText(element, value) {
    element.textContent = typeof value === "string" ? value : "";
    element.hidden = !element.textContent;
  }

  function renderList(list, items) {
    const template = list.querySelector(":scope > template[data-content-item]");
    if (!template) return;

    for (const item of items) {
      const fragment = template.content.cloneNode(true);
      if (item.id && fragment.firstElementChild) {
        fragment.firstElementChild.dataset.serviceId = item.id;
      }
      for (const element of fragment.querySelectorAll("[data-content-field]")) {
        setText(element, item[element.dataset.contentField]);
      }
      for (const image of fragment.querySelectorAll("img[data-content-image]")) {
        image.src = new URL(item.path, script.src).href;
        image.alt = item.alt ?? "";
      }
      list.append(fragment);
    }
    list.hidden = items.length === 0;
  }

  function contactTargets(contact) {
    const phone = contact.phone?.replace(/[^\d+]/g, "");
    const whatsapp = contact.whatsapp?.replace(/\D/g, "");
    const email = contact.email?.trim();
    const address = contact.address?.trim();
    const encodedAddress = address ? encodeURIComponent(address) : "";
    return {
      tel: /^\+?\d+$/.test(phone ?? "") ? `tel:${phone}` : "",
      whatsapp: whatsapp ? `https://wa.me/${whatsapp}` : "",
      email: email && /^[^\s@,;<>]+@[^\s@,;<>]+$/.test(email)
        ? `mailto:${encodeURIComponent(email).replace("%40", "@")}` : "",
      maps: encodedAddress
        ? `https://www.google.com/maps/search/?api=1&query=${encodedAddress}`
        : "",
      mapsEmbed: encodedAddress
        ? `https://www.google.com/maps?q=${encodedAddress}&output=embed`
        : ""
    };
  }

  async function render() {
    const response = await fetch(new URL("content.json", script.src), { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const content = await response.json();
    if (content.schema_version !== 2) throw new Error("Versión de contenido incompatible.");

    const contact = content.contact ?? {};
    const text = {
      business_name: content.business_name,
      phone: contact.phone,
      whatsapp: contact.whatsapp,
      email: contact.email,
      address: contact.address
    };
    for (const element of document.querySelectorAll("[data-content-text]")) {
      setText(element, text[element.dataset.contentText]);
    }

    const targets = contactTargets(contact);
    for (const element of document.querySelectorAll("[data-content-link]")) {
      const key = element.dataset.contentLink;
      const url = Object.hasOwn(targets, key) ? targets[key] : "";
      const attribute = element.matches("form") ? "action" : "href";
      if (url) element.setAttribute(attribute, url);
      else element.removeAttribute(attribute);
      element.hidden = !url;
    }

    for (const map of document.querySelectorAll("iframe[data-content-map]")) {
      if (targets.mapsEmbed) map.src = targets.mapsEmbed;
      else map.removeAttribute("src");
      map.hidden = !targets.mapsEmbed;
    }

    for (const list of document.querySelectorAll("[data-content-list]")) {
      const name = list.dataset.contentList;
      if (Object.hasOwn(collections, name)) {
        renderList(list, collections[name](content));
      }
    }
  }

  render().catch(error => console.error("No se pudo cargar el contenido de la web.", error));
})();
