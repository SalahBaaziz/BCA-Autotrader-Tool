function parsePrice(text) {
  if (!text) return null;
  const match = text.replace(/\s/g, "").match(/£?(\d{1,3}(?:,\d{3})*|\d+)/);
  if (!match) return null;
  return parseInt(match[1].replace(/,/g, ""), 10);
}

function parseMileage(text) {
  if (!text) return null;
  const match = text.replace(/,/g, "").match(/(\d{1,6})\s*miles?/i);
  if (!match) return null;
  return parseInt(match[1], 10);
}

function extractListingsFromCards(cards) {
  const prices = [];
  const mileages = [];

  cards.forEach((card) => {
    const priceEl =
      card.querySelector("[data-testid='search-listing-price']") ||
      card.querySelector("[data-testid='search-listing-price'] span") ||
      card.querySelector("[class*='price']");
    const mileageEl =
      card.querySelector("[data-testid='mileage']") ||
      card.querySelector("[class*='mileage']");

    const price = parsePrice(priceEl ? priceEl.textContent : "");
    const mileage = parseMileage(mileageEl ? mileageEl.textContent : "");

    if (price !== null) prices.push(price);
    if (mileage !== null) mileages.push(mileage);
  });

  return { prices, mileages };
}

function extractAutoTraderCards() {
  const cardSelector =
    "div.sc-c2svtm-4.bTbQPt > div.sc-c2svtm-5.coDaak > section > section";
  const priceSelector =
    "div:nth-child(2) > div.sc-1n64n0d-5.sc-1mc7cl3-13.chLhgW.lbKegd > span";
  const mileageSelector = "div:nth-child(1) > ul > li:nth-child(2)";

  const cards = Array.from(document.querySelectorAll(cardSelector));
  if (!cards.length) return null;

  const prices = [];
  const mileages = [];

  cards.forEach((card) => {
    const priceEl = card.querySelector(priceSelector);
    const mileageEl = card.querySelector(mileageSelector);
    const price = parsePrice(priceEl ? priceEl.textContent : "");
    const mileage = parseMileage(mileageEl ? mileageEl.textContent : "");
    if (price !== null) prices.push(price);
    if (mileage !== null) mileages.push(mileage);
  });

  return { prices, mileages };
}

function extractListingsFallback() {
  const prices = [];
  const mileages = [];

  document.querySelectorAll("[data-testid='search-listing-price']").forEach((el) => {
    const price = parsePrice(el.textContent);
    if (price !== null) prices.push(price);
  });

  document.querySelectorAll("[data-testid='price'], [class*='Price'], [class*='price']").forEach(
    (el) => {
      const price = parsePrice(el.textContent);
      if (price !== null) prices.push(price);
    }
  );

  document.querySelectorAll("[data-testid='mileage']").forEach((el) => {
    const mileage = parseMileage(el.textContent);
    if (mileage !== null) mileages.push(mileage);
  });

  document.querySelectorAll("[class*='Mileage'], [class*='mileage']").forEach((el) => {
    const mileage = parseMileage(el.textContent);
    if (mileage !== null) mileages.push(mileage);
  });

  return { prices, mileages };
}

function extractData() {
  const autoTraderData = extractAutoTraderCards();
  if (autoTraderData) {
    return autoTraderData;
  }

  const cards = Array.from(
    document.querySelectorAll("[data-testid='search-listing'], article, li.search-page__result")
  );

  if (cards.length > 0) {
    const data = extractListingsFromCards(cards);
    if (data.prices.length === 0 || data.mileages.length === 0) {
      const prices = [...data.prices];
      const mileages = [...data.mileages];
      cards.forEach((card) => {
        const text = card.innerText || "";
        const price = parsePrice(text);
        const mileage = parseMileage(text);
        if (price !== null) prices.push(price);
        if (mileage !== null) mileages.push(mileage);
      });
      return { prices, mileages };
    }
    return data;
  }

  return extractListingsFallback();
}

function acceptCookies() {
  const selectors = [
    "button#onetrust-accept-btn-handler",
    "button[aria-label='Accept All']",
    "button[title='Accept All']",
    "button[data-testid*='cookie']",
    "button[class*='cookie']",
    "button[class*='accept']",
    "a.cookie-accept",
  ];
  for (const selector of selectors) {
    const btn = document.querySelector(selector);
    if (btn && btn.offsetParent !== null) {
      btn.click();
      return true;
    }
  }
  return false;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function scrapeAutoTrader(options = {}) {
  const maxScrolls = options.maxScrolls || 30;
  const pauseMs = options.pauseMs || 1200;

  acceptCookies();

  const priceSet = new Set();
  const mileageSet = new Set();
  let lastHeight = 0;
  let sameCount = 0;

  for (let i = 0; i < maxScrolls; i++) {
    const data = extractData();
    data.prices.forEach((p) => priceSet.add(p));
    data.mileages.forEach((m) => mileageSet.add(m));

    const newHeight = document.body.scrollHeight;
    if (newHeight === lastHeight) {
      sameCount += 1;
    } else {
      sameCount = 0;
    }
    lastHeight = newHeight;

    if (sameCount >= 2) break;

    window.scrollTo(0, document.body.scrollHeight);
    await sleep(pauseMs);
  }

  return {
    prices: Array.from(priceSet),
    mileages: Array.from(mileageSet),
  };
}

function findListingRoot(el) {
  if (!el) return null;
  return (
    el.closest("[data-testid='search-listing']") ||
    el.closest("[class*='VehicleResultCardDesktop']") ||
    el.closest("a[class*='card-link-desktop']") ||
    el.closest("article") ||
    el.closest("li.search-page__result")
  );
}

function getText(el) {
  return el ? el.textContent.trim() : "";
}

function extractListingDetails(root) {
  if (!root) return null;
  const text = root.innerText || "";
  const lines = text.split("\n").map((l) => l.trim()).filter(Boolean);
  const titleEl =
    root.querySelector("div.sc-aXZVg.gwONok > a") ||
    root.querySelector("div.sc-aXZVg.gGCdyN a") ||
    root.querySelector("[data-testid='search-listing-title']") ||
    root.querySelector("h2") ||
    root.querySelector("h3");

  const priceEl =
    root.querySelector(
      "div.sc-aXZVg.PricingAndVATDesktop__PricingBox-sc-1ycs9pb-0 div.sc-aXZVg.PricingAndVATDesktop___StyledBox2-sc-1ycs9pb-3 p"
    ) ||
    root.querySelector("div.sc-aXZVg.PricingAndVATMobile___StyledBox-sc-6d7h4m-2") ||
    root.querySelector("[data-testid='search-listing-price']") ||
    root.querySelector("[class*='price']");

  const mileageEl =
    root.querySelector("div.sc-aXZVg.gwONok > div.sc-aXZVg.hTOsOS > ul > li:nth-child(1)") ||
    root.querySelector("div.sc-aXZVg.cNrkdx > ul > li:nth-child(1)") ||
    root.querySelector("[data-testid='mileage']") ||
    root.querySelector("[class*='mileage']");

  const yearEl =
    root.querySelector("div.sc-aXZVg.cNrkdx > ul > li:nth-child(2)") ||
    root.querySelector("[data-testid='year']") ||
    null;

  const fuelEl =
    root.querySelector("div.sc-aXZVg.cNrkdx > ul > li:nth-child(5)") ||
    root.querySelector("[data-testid='fuelType']") ||
    null;

  const transmissionEl =
    root.querySelector("div.sc-aXZVg.cNrkdx > ul > li:nth-child(6)") ||
    root.querySelector("[data-testid='transmission']") ||
    null;

  const doorsEl =
    root.querySelector("div.sc-aXZVg.cNrkdx > ul > li:nth-child(7)") ||
    root.querySelector("[data-testid='doors']") ||
    null;

  const engineEl = root.querySelector("[data-testid='engineSize']") || null;

  const regEl =
    root.querySelector("div.sc-aXZVg.sc-kgOKUu.jCacqK.jLHFeA") || null;

  const yearMatch = text.match(/\b(19[7-9]\d|20[0-2]\d)\b/);
  const fuelMatch = text.match(/\b(Diesel|Petrol|Electric|Hybrid)\b/i);
  const transMatch = text.match(/\b(Manual|Automatic|Auto Clutch)\b/i);
  const doorsMatch = text.match(/\b(\d)\s*doors?\b/i);
  const engineMatch = text.match(/\b(\d+\.\d+)\s*(?:L|TSI|TDI|TFSI|HDI|CC|V)?\b/i);
  const regMatch = text.match(/\b[A-Z]{2}[0-9]{2}\s?[A-Z]{3}\b/i);
  const transText = `${getText(transmissionEl)} ${text}`;
  const normalizedTrans = /auto/i.test(transText) ? "Automatic" : "Manual";
  const priceMatchNearCap = (() => {
    const capIndex = text.indexOf("CAP Clean");
    if (capIndex !== -1) {
      const tail = text.slice(capIndex, capIndex + 200);
      const m = tail.match(/£\s?(\d{1,3}(?:,\d{3})*|\d+)/);
      if (m) return parseInt(m[1].replace(/,/g, ""), 10);
    }
    return null;
  })();
  const priceMatchAny = (() => {
    const m = text.match(/£\s?(\d{1,3}(?:,\d{3})*|\d+)/);
    return m ? parseInt(m[1].replace(/,/g, ""), 10) : null;
  })();
  const mileageFromText = parseMileage(text);
  const mileageFromLi = parseMileage(getText(mileageEl));
  const titleFromLines = (() => {
    const bad = ["Recently Added", "Online Auction", "CAP Clean", "VAT"];
    for (const line of lines) {
      if (bad.some((b) => line.includes(b))) continue;
      if (line.match(/\bmiles?\b/i)) continue;
      if (line.length >= 12) return line;
    }
    return lines[0] || "";
  })();
  const titleValue = getText(titleEl) || titleFromLines;
  const titleParts = titleValue ? titleValue.split(/\s+/) : [];
  const brand = titleParts.length ? titleParts[0].toUpperCase() : "";
  let engineIndex = -1;
  for (let i = 1; i < titleParts.length; i++) {
    if (titleParts[i].match(/^\d+\.\d+$/)) {
      engineIndex = i;
      break;
    }
  }
  let modelParts = [];
  if (engineIndex > 1) {
    modelParts = titleParts.slice(1, engineIndex);
  } else if (titleParts.length > 1) {
    modelParts = [titleParts[1]];
  }
  const model = modelParts.join(" ").toUpperCase();

  return {
    title: titleValue,
    brand,
    model,
    price: parsePrice(getText(priceEl)) || priceMatchNearCap || priceMatchAny,
    mileage: mileageFromLi || mileageFromText,
    year: getText(yearEl) || (yearMatch ? yearMatch[1] : ""),
    fuel: getText(fuelEl) || (fuelMatch ? fuelMatch[1] : ""),
    transmission: normalizedTrans || (transMatch ? transMatch[1] : ""),
    doors: getText(doorsEl) || (doorsMatch ? doorsMatch[1] : ""),
    engineSize: getText(engineEl) || (engineMatch ? engineMatch[1] : ""),
    registration: getText(regEl) || (regMatch ? regMatch[0].replace(/\s/g, "") : ""),
  };
}

let selecting = false;
let lastHighlight = null;
let previousCursor = "";
let overlay = null;

function clearHighlight() {
  if (lastHighlight) {
    lastHighlight.style.outline = "";
    lastHighlight = null;
  }
}

function highlightEl(el) {
  clearHighlight();
  if (el) {
    el.style.outline = "2px solid #2563eb";
    lastHighlight = el;
  }
}

function ensureOverlay() {
  if (overlay) return overlay;
  overlay = document.createElement("div");
  overlay.style.position = "fixed";
  overlay.style.bottom = "16px";
  overlay.style.right = "16px";
  overlay.style.zIndex = "2147483647";
  overlay.style.background = "rgba(15, 23, 42, 0.9)";
  overlay.style.color = "#fff";
  overlay.style.padding = "8px 10px";
  overlay.style.borderRadius = "6px";
  overlay.style.fontSize = "12px";
  overlay.style.fontFamily = "ui-monospace, monospace";
  overlay.textContent = "Selection mode: hover a card, click to pick.";
  document.body.appendChild(overlay);
  return overlay;
}

function removeOverlay() {
  if (overlay && overlay.parentNode) {
    overlay.parentNode.removeChild(overlay);
  }
  overlay = null;
}

function startSelection(sendResponse) {
  selecting = true;
  clearHighlight();
  previousCursor = document.body.style.cursor;
  document.body.style.cursor = "crosshair";
  ensureOverlay();

  const onMove = (event) => {
    if (!selecting) return;
    const root = findListingRoot(event.target);
    highlightEl(root);
  };

  const onClick = (event) => {
    if (!selecting) return;
    event.preventDefault();
    event.stopPropagation();
    const root = findListingRoot(event.target);
    const details = extractListingDetails(root);
    selecting = false;
    clearHighlight();
    document.body.style.cursor = previousCursor;
    document.removeEventListener("mousemove", onMove, true);
    document.removeEventListener("click", onClick, true);
    document.removeEventListener("keydown", onKeydown, true);
    removeOverlay();
    try {
      chrome.storage.local.set({ lastSelection: details || {} });
    } catch (_) {}
    sendResponse({ ok: true, data: details });
  };

  const onKeydown = (event) => {
    if (!selecting) return;
    if (event.key === "Escape") {
      selecting = false;
      clearHighlight();
      document.body.style.cursor = previousCursor;
      document.removeEventListener("mousemove", onMove, true);
      document.removeEventListener("click", onClick, true);
      document.removeEventListener("keydown", onKeydown, true);
      removeOverlay();
      sendResponse({ ok: false });
    }
  };

  document.addEventListener("mousemove", onMove, true);
  document.addEventListener("click", onClick, true);
  document.addEventListener("keydown", onKeydown, true);
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message && message.type === "extractData") {
    const data = extractData();
    sendResponse({ ok: true, data });
  }
  if (message && message.type === "scrapeAutoTrader") {
    (async () => {
      try {
        const data = await scrapeAutoTrader(message.options || {});
        sendResponse({ ok: true, data });
      } catch (err) {
        sendResponse({ ok: false, error: err ? err.message : "scrape failed" });
      }
    })();
    return true;
  }
  if (message && message.type === "acceptCookies") {
    const ok = acceptCookies();
    sendResponse({ ok });
  }
  if (message && message.type === "startSelect") {
    startSelection(sendResponse);
  }
  return true;
});
