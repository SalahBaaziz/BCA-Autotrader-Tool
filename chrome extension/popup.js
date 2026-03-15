const openSearchBtn = document.getElementById("openSearch");
const analyzePageBtn = document.getElementById("analyzePage");
const selectCarBtn = document.getElementById("selectCar");
const acceptCookiesBtn = document.getElementById("acceptCookies");
const statusPill = document.getElementById("ocrStatus");
const parsedDetails = document.getElementById("parsedDetails");
const analysisSummary = document.getElementById("analysisSummary");
const priceHistogram = document.getElementById("priceHistogram");
const scatterPlot = document.getElementById("scatterPlot");
const minMileageInput = document.getElementById("minMileage");
const maxMileageInput = document.getElementById("maxMileage");
const minYearInput = document.getElementById("minYear");
const maxYearInput = document.getElementById("maxYear");
const searchUrlEl = document.getElementById("searchUrl");
const copyUrlBtn = document.getElementById("copyUrl");
const debugValuesEl = document.getElementById("debugValues");

let lastParsed = null;
let selectionPoller = null;
let urlWatchId = null;

function setStatus(text) {
  if (statusPill) statusPill.textContent = text;
}

function flashButton(button) {
  if (!button) return;
  button.classList.add("clicked");
  setTimeout(() => button.classList.remove("clicked"), 250);
}

function renderDetails(parsed) {
  if (!parsed) {
    parsedDetails.textContent = "No data yet";
    return;
  }
  const items = [
    ["Title", parsed.title || "n/a"],
    ["Brand", parsed.brand || "n/a"],
    ["Model", parsed.model || "n/a"],
    ["Registration", parsed.registration || "n/a"],
    ["Mileage", parsed.mileage ?? "n/a"],
    ["Price", parsed.price ?? "n/a"],
    ["Year", parsed.year ?? "n/a"],
    ["Engine", parsed.engineSize ?? "n/a"],
    ["Fuel", parsed.fuelType || parsed.fuel || "n/a"],
    ["Doors", parsed.doors || "n/a"],
    ["Transmission", parsed.transmission || parsed.trans || "n/a"],
  ];
  parsedDetails.innerHTML = items
    .map(([label, value]) => `<span><strong>${label}:</strong> ${value}</span>`)
    .join("");
  applyDefaultRanges(parsed);
  lastParsed = parsed;
  startUrlWatch();
}

function buildAutoTraderUrl(parsed) {
  if (!parsed) {
    const urlEl = document.getElementById("searchUrl");
    if (urlEl) urlEl.textContent = "No URL yet";
    return "";
  }
  const minMileageEl = document.getElementById("minMileage");
  const maxMileageEl = document.getElementById("maxMileage");
  const minYearEl = document.getElementById("minYear");
  const maxYearEl = document.getElementById("maxYear");
  const urlEl = document.getElementById("searchUrl");
  const debugEl = document.getElementById("debugValues");
  const template =
    "https://www.autotrader.co.uk/car-search?aggregatedTrim=&body-type=&channel=cars&colour=&distance={INSERT_DISTANCE}&fuel-type={INSERT_FUEL_TYPE}&make={INSERT_MAKE}&max-year={INSERT_MAX_YEAR}&maxPrice={INSERT_MAX_PRICE}&maximum-badge-engine-size={INSERT_MAX_ENGINE_SIZE}&maximum-mileage={INSERT_MAX_MILEAGE}&minPrice={INSERT_MIN_PRICE}&minimum-badge-engine-size={INSERT_MIN_ENGINE_SIZE}&minimum-mileage={INSERT_MIN_MILEAGE}&model={INSERT_MODEL}&postcode=yo1%200sb&quantity-of-doors={INSERT_DOORS}&sort={INSERT_SORT}&transmission={INSERT_TRANSMISSION}&year-from={INSERT_MIN_YEAR}&year-to={INSERT_MAX_YEAR_RANGE}";

  const makeRaw = parsed.brand || "";
  const modelRaw = parsed.model || "";
  const make = makeRaw ? makeRaw[0].toUpperCase() + makeRaw.slice(1).toLowerCase() : "";
  const model = modelRaw;
  const minMileage = Number((minMileageEl && minMileageEl.value) || 0);
  const maxMileage = Number((maxMileageEl && maxMileageEl.value) || 150000);
  const year = parsed.year || 2018;
  const minYear = Number((minYearEl && minYearEl.value) || year - 1);
  const maxYear = Number((maxYearEl && maxYearEl.value) || year + 1);
  const engineSize = Number(parsed.engineSize || 1.0);
  const fuelType = parsed.fuelType || parsed.fuel || "Petrol";
  const doors = parsed.doors || "5";
  const rawTrans = String(parsed.transmission || parsed.trans || "Manual");
  const transmission = /auto/i.test(rawTrans) ? "Automatic" : "Manual";

  const replacements = {
    "{INSERT_DISTANCE}": "",
    "{INSERT_FUEL_TYPE}": encodeURIComponent(fuelType),
    "{INSERT_MAKE}": encodeURIComponent(make),
    "{INSERT_MAX_YEAR}": encodeURIComponent(maxYear),
    "{INSERT_MAX_PRICE}": "",
    "{INSERT_MAX_ENGINE_SIZE}": encodeURIComponent(engineSize.toFixed(1)),
    "{INSERT_MAX_MILEAGE}": encodeURIComponent(maxMileage),
    "{INSERT_MIN_PRICE}": "",
    "{INSERT_MIN_ENGINE_SIZE}": encodeURIComponent(engineSize.toFixed(1)),
    "{INSERT_MIN_MILEAGE}": encodeURIComponent(minMileage),
    "{INSERT_MODEL}": encodeURIComponent(model),
    "{INSERT_DOORS}": encodeURIComponent(doors),
    "{INSERT_SORT}": encodeURIComponent("relevance"),
    "{INSERT_TRANSMISSION}": encodeURIComponent(transmission),
    "{INSERT_MIN_YEAR}": encodeURIComponent(minYear),
    "{INSERT_MAX_YEAR_RANGE}": encodeURIComponent(maxYear),
  };

  let finalUrl = template;
  Object.keys(replacements).forEach((key) => {
    finalUrl = finalUrl.split(key).join(replacements[key]);
  });

  if (urlEl) urlEl.textContent = finalUrl;
  if (debugEl) {
    debugEl.textContent =
      `Debug: make=${make} model=${model} fuel=${fuelType} doors=${doors} ` +
      `minM=${minMileage} maxM=${maxMileage} minY=${minYear} maxY=${maxYear} engine=${engineSize}`;
  }
  return finalUrl;
}

function startUrlWatch() {
  if (urlWatchId) return;
  urlWatchId = setInterval(() => {
    if (!lastParsed) return;
    try {
      const url = buildAutoTraderUrl(lastParsed);
      const urlEl = document.getElementById("searchUrl");
      if (urlEl) urlEl.textContent = url || "No URL yet";
      if (urlEl && url) {
        clearInterval(urlWatchId);
        urlWatchId = null;
      }
    } catch (err) {
      const debugEl = document.getElementById("debugValues");
      if (debugEl) debugEl.textContent = `Debug error: ${err.message}`;
    }
  }, 300);
}

function computeStats(prices) {
  if (!prices.length) return null;
  const logs = prices.map((p) => Math.log(p));
  const meanLog = logs.reduce((a, b) => a + b, 0) / logs.length;
  const variance =
    logs.reduce((a, b) => a + Math.pow(b - meanLog, 2), 0) / logs.length;
  const stdLog = Math.sqrt(variance);
  const meanPrice = Math.exp(meanLog);
  const lowerStd = Math.exp(meanLog - stdLog);
  const upperStd = Math.exp(meanLog + stdLog);
  return { meanPrice, lowerStd, upperStd };
}

function linearRegression(xs, ys) {
  if (xs.length !== ys.length || xs.length < 2) return null;
  const n = xs.length;
  const meanX = xs.reduce((a, b) => a + b, 0) / n;
  const meanY = ys.reduce((a, b) => a + b, 0) / n;
  let num = 0;
  let den = 0;
  for (let i = 0; i < n; i++) {
    num += (xs[i] - meanX) * (ys[i] - meanY);
    den += Math.pow(xs[i] - meanX, 2);
  }
  if (den === 0) return null;
  const slope = num / den;
  const intercept = meanY - slope * meanX;
  let ssTot = 0;
  let ssRes = 0;
  for (let i = 0; i < n; i++) {
    const pred = slope * xs[i] + intercept;
    ssTot += Math.pow(ys[i] - meanY, 2);
    ssRes += Math.pow(ys[i] - pred, 2);
  }
  const r2 = ssTot === 0 ? 0 : 1 - ssRes / ssTot;
  return { slope, intercept, r2 };
}

function drawHistogram(canvas, prices, stats) {
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (!prices.length) return;

  const padding = 30;
  const plotW = canvas.width - padding * 2;
  const plotH = canvas.height - padding * 2;

  const bins = 20;
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const step = (max - min) / bins || 1;
  const counts = new Array(bins).fill(0);
  for (const p of prices) {
    const idx = Math.min(bins - 1, Math.floor((p - min) / step));
    counts[idx] += 1;
  }
  const maxCount = Math.max(...counts, 1);

  // Axes
  ctx.strokeStyle = "#94a3b8";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding, padding);
  ctx.lineTo(padding, padding + plotH);
  ctx.lineTo(padding + plotW, padding + plotH);
  ctx.stroke();

  // Bars
  ctx.fillStyle = "#38bdf8";
  const barWidth = plotW / bins;
  counts.forEach((count, i) => {
    const x = padding + i * barWidth + 2;
    const height = (count / maxCount) * (plotH - 4);
    ctx.fillRect(x, padding + plotH - height, barWidth - 4, height);
  });

  // Mean / Std lines
  if (stats) {
    const lines = [
      { value: stats.meanPrice, color: "#f97316" },
      { value: stats.lowerStd, color: "#ef4444" },
      { value: stats.upperStd, color: "#ef4444" },
    ];
    lines.forEach((line) => {
      const x =
        padding + ((line.value - min) / (max - min || 1)) * plotW;
      ctx.strokeStyle = line.color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x, padding);
      ctx.lineTo(x, padding + plotH);
      ctx.stroke();

      // Label value near axis
      ctx.fillStyle = line.color;
      ctx.font = "10px sans-serif";
      ctx.fillText(String(Math.round(line.value)), x - 10, padding + plotH + 14);
    });
  }

  // Labels
  ctx.fillStyle = "#94a3b8";
  ctx.font = "10px sans-serif";
  ctx.fillText(String(Math.round(min)), padding, canvas.height - 6);
  ctx.fillText(String(Math.round(max)), padding + plotW - 24, canvas.height - 6);
}

function drawHeatmap(canvas, mileages, prices, stats, selectedPoint) {
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (!mileages.length || !prices.length) return;
  const minX = Math.min(...mileages);
  const maxX = Math.max(...mileages);
  const minY = Math.min(...prices);
  const maxY = Math.max(...prices);

  const padding = 30;
  const plotW = canvas.width - padding * 2;
  const plotH = canvas.height - padding * 2;

  const binsX = 20;
  const binsY = 20;
  const grid = Array.from({ length: binsX }, () => Array(binsY).fill(0));

  for (let i = 0; i < Math.min(mileages.length, prices.length); i++) {
    const x = mileages[i];
    const y = prices[i];
    const ix = Math.min(
      binsX - 1,
      Math.floor(((x - minX) / (maxX - minX || 1)) * binsX)
    );
    const iy = Math.min(
      binsY - 1,
      Math.floor(((y - minY) / (maxY - minY || 1)) * binsY)
    );
    grid[ix][iy] += 1;
  }

  const maxCount = Math.max(...grid.flat());
  for (let ix = 0; ix < binsX; ix++) {
    for (let iy = 0; iy < binsY; iy++) {
      const count = grid[ix][iy];
      if (!count) continue;
      const intensity = count / (maxCount || 1);
      const x = padding + (ix / binsX) * plotW;
      const y = padding + plotH - (iy / binsY) * plotH;
      const w = plotW / binsX;
      const h = plotH / binsY;
      ctx.fillStyle = `rgba(56, 189, 248, ${0.1 + intensity * 0.8})`;
      ctx.fillRect(x, y - h, w, h);
    }
  }

  // Axes
  ctx.strokeStyle = "#94a3b8";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding, padding);
  ctx.lineTo(padding, padding + plotH);
  ctx.lineTo(padding + plotW, padding + plotH);
  ctx.stroke();

  // Mean/std horizontal lines (price axis)
  if (stats) {
    const lines = [
      { value: stats.meanPrice, color: "#f97316" },
      { value: stats.lowerStd, color: "#22c55e" },
      { value: stats.upperStd, color: "#ef4444" },
    ];
    lines.forEach((line) => {
      const y =
        padding + plotH - ((line.value - minY) / (maxY - minY || 1)) * plotH;
      ctx.strokeStyle = line.color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(padding + plotW, y);
      ctx.stroke();

      // Label value on Y axis
      ctx.fillStyle = line.color;
      ctx.font = "10px sans-serif";
      ctx.fillText(String(Math.round(line.value)), 4, y - 2);
    });
  }

  if (selectedPoint && selectedPoint.price) {
    const x =
      padding + ((selectedPoint.price - min) / (max - min || 1)) * plotW;
    ctx.strokeStyle = "#22c55e";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x, padding);
    ctx.lineTo(x, padding + plotH);
    ctx.stroke();
    ctx.fillStyle = "#22c55e";
    ctx.font = "10px sans-serif";
    ctx.fillText(String(Math.round(selectedPoint.price)), x - 10, padding + 10);
  }
  if (selectedPoint && selectedPoint.mileage && selectedPoint.price) {
    const sx = padding + ((selectedPoint.mileage - minX) / (maxX - minX || 1)) * plotW;
    const sy =
      padding + plotH - ((selectedPoint.price - minY) / (maxY - minY || 1)) * plotH;
    ctx.fillStyle = "#fbbf24";
    ctx.strokeStyle = "#0f172a";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(sx, sy, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  }

  // Axis labels
  ctx.fillStyle = "#94a3b8";
  ctx.font = "10px sans-serif";
  ctx.fillText(String(Math.round(minX)), padding, canvas.height - 6);
  ctx.fillText(String(Math.round(maxX)), padding + plotW - 24, canvas.height - 6);
  ctx.fillText(String(Math.round(minY)), 4, padding + plotH);
  ctx.fillText(String(Math.round(maxY)), 4, padding + 10);
}

if (selectCarBtn) selectCarBtn.addEventListener("click", async () => {
  flashButton(selectCarBtn);
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) {
    setStatus("No active tab.");
    return;
  }
  setStatus("Hover a listing and click to select.");

  const sendSelectMessage = () =>
    new Promise((resolve) => {
      chrome.tabs.sendMessage(tab.id, { type: "startSelect" }, (response) => {
        resolve(response);
      });
    });

  let response = await sendSelectMessage();

  if (!response) {
    try {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ["content.js"],
      });
      response = await sendSelectMessage();
    } catch (err) {
      setStatus("Unable to inject selection script.");
      return;
    }
  }

  if (selectionPoller) {
    clearInterval(selectionPoller);
  }

  selectionPoller = setInterval(async () => {
    const result = await chrome.storage.local.get(["lastSelection"]);
    if (result && result.lastSelection) {
      clearInterval(selectionPoller);
      selectionPoller = null;
      lastParsed = result.lastSelection;
      renderDetails(lastParsed);
      startUrlWatch();
      openSearchBtn.disabled = false;
      setStatus("Car selected.");
    }
  }, 500);
});

if (acceptCookiesBtn) acceptCookiesBtn.addEventListener("click", async () => {
  flashButton(acceptCookiesBtn);
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) {
    setStatus("No active tab.");
    return;
  }
  chrome.tabs.sendMessage(tab.id, { type: "acceptCookies" }, () => {
    setStatus("Cookie check sent.");
  });
});

if (openSearchBtn) openSearchBtn.addEventListener("click", async () => {
  flashButton(openSearchBtn);
  if (!lastParsed) return;
  if (!lastParsed.brand || !lastParsed.model) {
    setStatus("Missing brand/model. Select a card first.");
    return;
  }
  const url = buildAutoTraderUrl(lastParsed);
  if (searchUrlEl) searchUrlEl.textContent = url;
  chrome.runtime.sendMessage({ type: "openTab", url }, (response) => {
    if (chrome.runtime.lastError || !response || !response.ok) {
      setStatus("Failed to open AutoTrader tab. Copying URL.");
      navigator.clipboard.writeText(url).catch(() => {});
      return;
    }
    setStatus("Opened AutoTrader search.");
  });
  chrome.tabs.create({ url }, () => {
    if (chrome.runtime.lastError) {
      setStatus("Failed to open AutoTrader tab. Copying URL.");
      navigator.clipboard.writeText(url).catch(() => {});
      return;
    }
    setStatus("Opened AutoTrader search.");
  });
});

if (copyUrlBtn) copyUrlBtn.addEventListener("click", () => {
  if (!searchUrlEl || !searchUrlEl.textContent || searchUrlEl.textContent === "No URL yet") {
    setStatus("No URL to copy.");
    return;
  }
  navigator.clipboard.writeText(searchUrlEl.textContent).then(
    () => setStatus("URL copied."),
    () => setStatus("Failed to copy URL.")
  );
});

analyzePageBtn.addEventListener("click", async () => {
  flashButton(analyzePageBtn);
  analysisSummary.textContent = "Analyzing...";
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) {
    analysisSummary.textContent = "No active tab.";
    return;
  }

  let targetTabId = tab.id;
  const activeUrl = tab.url || "";
  const isAutoTrader = activeUrl.includes("autotrader.co.uk/car-search");

  if (!isAutoTrader) {
    const url = buildAutoTraderUrl(lastParsed);
    const resp = await new Promise((resolve) =>
      chrome.runtime.sendMessage({ type: "openTab", url }, (response) => resolve(response))
    );
    if (!resp || !resp.ok || !resp.tabId) {
      analysisSummary.textContent = "Could not open AutoTrader tab.";
      return;
    }
    targetTabId = resp.tabId;
    await waitForTabComplete(targetTabId, 15000);
  }

  chrome.tabs.sendMessage(targetTabId, { type: "acceptCookies" }, () => {});
  chrome.tabs.sendMessage(
    targetTabId,
    { type: "scrapeAutoTrader", options: { maxScrolls: 40, pauseMs: 1200 } },
    (response) => {
      if (!response || !response.ok) {
        analysisSummary.textContent = "Could not extract data from this page.";
        return;
      }
      const { prices, mileages } = response.data;
      if (!prices.length || !mileages.length) {
        analysisSummary.textContent = "No prices/mileages found.";
        return;
      }

      const stats = computeStats(prices);
      const avgMileage = mileages.reduce((a, b) => a + b, 0) / mileages.length;
    const summaryItems = [
      ["Sample size", prices.length],
      ["Avg mileage", Math.round(avgMileage)],
      ["Mean price", stats ? Math.round(stats.meanPrice) : "n/a"],
      ["-1 Std", stats ? Math.round(stats.lowerStd) : "n/a"],
      ["+1 Std", stats ? Math.round(stats.upperStd) : "n/a"],
    ];

      analysisSummary.innerHTML = summaryItems
        .map(([label, value]) => `<span><strong>${label}:</strong> ${value}</span>`)
        .join("");

    drawHistogram(priceHistogram, prices, stats);
    drawHeatmap(scatterPlot, mileages, prices, stats, {
      mileage: Number(lastParsed && lastParsed.mileage),
      price: Number(lastParsed && lastParsed.price),
    });
    }
  );
});

chrome.storage.local.get(["lastSelection"], (result) => {
  if (result && result.lastSelection) {
    lastParsed = result.lastSelection;
    renderDetails(lastParsed);
    openSearchBtn.disabled = false;
    startUrlWatch();
  }
});

window.addEventListener("unload", () => {
  if (selectionPoller) clearInterval(selectionPoller);
});

function waitForTabComplete(tabId, timeoutMs) {
  return new Promise((resolve) => {
    let done = false;
    const timer = setTimeout(() => {
      if (!done) {
        done = true;
        chrome.tabs.onUpdated.removeListener(listener);
        resolve(false);
      }
    }, timeoutMs);
    function listener(updatedTabId, info) {
      if (updatedTabId === tabId && info.status === "complete") {
        if (!done) {
          done = true;
          clearTimeout(timer);
          chrome.tabs.onUpdated.removeListener(listener);
          resolve(true);
        }
      }
    }
    chrome.tabs.onUpdated.addListener(listener);
  });
}

["input", "change"].forEach((evt) => {
  if (minMileageInput) minMileageInput.addEventListener(evt, () => buildAutoTraderUrl(lastParsed));
  if (maxMileageInput) maxMileageInput.addEventListener(evt, () => buildAutoTraderUrl(lastParsed));
  if (minYearInput) minYearInput.addEventListener(evt, () => buildAutoTraderUrl(lastParsed));
  if (maxYearInput) maxYearInput.addEventListener(evt, () => buildAutoTraderUrl(lastParsed));
});

function applyDefaultRanges(parsed) {
  const minMileageEl = document.getElementById("minMileage");
  const maxMileageEl = document.getElementById("maxMileage");
  const minYearEl = document.getElementById("minYear");
  const maxYearEl = document.getElementById("maxYear");
  const mileage = Number(parsed.mileage || 0);
  const year = Number(parsed.year || 0);
  if (!Number.isNaN(mileage) && mileage > 0) {
    const minM = Math.max(0, mileage - 50000);
    const maxM = mileage + 50000;
    if (minMileageEl) minMileageEl.value = minM;
    if (maxMileageEl) maxMileageEl.value = maxM;
  }
  if (!Number.isNaN(year) && year > 0) {
    if (minYearEl) minYearEl.value = year - 1;
    if (maxYearEl) maxYearEl.value = year + 1;
  }
  setTimeout(() => updateUrl(), 0);
}

function updateUrl() {
  if (!lastParsed) {
    const urlEl = document.getElementById("searchUrl");
    if (urlEl) urlEl.textContent = "No URL yet";
    return;
  }
  buildAutoTraderUrl(lastParsed);
}
