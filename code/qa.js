// QA: open index.html at desktop and phone widths, log console errors, take screenshots to qa/.
// Run from the study root with a static server (python3 -m http.server PORT; set PORT). Leaflet comes from a local npm
// copy (LEAFLET_DIST) because the CDN is not reachable from the build container; map tiles are blocked here.
const { chromium } = require("playwright");
const fs = require("fs");
const LD = process.env.LEAFLET_DIST;
(async () => {
  fs.mkdirSync("qa", { recursive: true });
  const b = await chromium.launch();
  const errs = [];
  for (const [nm, vw, vh] of [["desktop", 1280, 900], ["phone", 390, 844]]) {
    const p = await b.newPage({ viewport: { width: vw, height: vh }, deviceScaleFactor: nm === "phone" ? 2 : 1 });
    await p.route(/arcgisonline|googleapis|gstatic|jsdelivr/, r => r.abort());
    await p.route(/leaflet\.min\.js/, r => r.fulfill({ path: LD + "/leaflet.js", contentType: "application/javascript" }));
    await p.route(/leaflet\.min\.css/, r => r.fulfill({ path: LD + "/leaflet.css", contentType: "text/css" }));
    p.on("console", m => { if (m.type() === "error" && !/ERR_FAILED|net::|Failed to load resource/i.test(m.text())) errs.push(nm + ": " + m.text()); });
    p.on("pageerror", e => errs.push(nm + " pageerror: " + e.message));
    await p.goto("http://localhost:" + process.env.PORT + "/index.html", { waitUntil: "load" });
    await p.waitForTimeout(3000);
    const jpg = f => `qa/${nm}_${f}.jpg`;
    await p.screenshot({ path: jpg("top"), type: "jpeg", quality: 70 });
    const shot = async (sel, f) => { await p.locator(sel).scrollIntoViewIfNeeded(); await p.waitForTimeout(600); await p.locator(sel).screenshot({ path: jpg(f), type: "jpeg", quality: 72 }); };
    await shot("#stage", "map1820");
    const t0 = Date.now();
    for (const v of [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]) { await p.locator("#slider").fill(String(v)); }
    console.log(nm, "slider sweep ms", Date.now() - t0);
    await p.locator("#momRow .btn", { hasText: "AD 1" }).dispatchEvent("click"); await p.waitForTimeout(1500); await shot("#stage", "mapAD1");
    await p.locator("#momRow .btn", { hasText: "10,000 BC" }).dispatchEvent("click"); await p.waitForTimeout(1500); await shot("#stage", "map10000bc");
    await p.locator("#momRow .btn", { hasText: "3,000 BC" }).dispatchEvent("click"); await p.waitForTimeout(1500); await shot("#stage", "map3000bc");
    await p.locator("#momRow .btn", { hasText: "1600" }).dispatchEvent("click"); await p.waitForTimeout(1500); await shot("#stage", "map1600");
    for (const c of ["#lrPc", "#lrPop"]) await shot(c, c.slice(1));
    await p.locator("#momRow .btn", { hasText: "1913" }).dispatchEvent("click"); await p.waitForTimeout(1200); await shot("#stage", "map1913");
    for (const k of ["pc", "share", "growth"]) { await p.locator(`#indRow .btn[data-i="${k}"]`).click(); await p.waitForTimeout(700); await shot("#stage", "ind_" + k); }
    await p.locator(`#indRow .btn[data-i="gdp"]`).click();
    await p.locator("#momRow .btn", { hasText: "2024" }).dispatchEvent("click"); await p.waitForTimeout(1500); await shot("#stage", "map2024");
    await p.locator("#map").click({ position: { x: Math.round(vw * (nm === "phone" ? .7 : .55)), y: 170 } }); await p.waitForTimeout(1200);
    await p.locator("#stage").screenshot({ path: jpg("popup"), type: "jpeg", quality: 72 });
    await p.fill("#q", "Japan"); await p.waitForTimeout(300); await p.keyboard.press("Enter"); await p.waitForTimeout(1800); await shot("#side", "side_japan");
    await p.fill("#cq", "Korea"); await p.waitForTimeout(300); await p.keyboard.press("Enter"); await p.waitForTimeout(800);
    await p.fill("#cq", "United Kingdom"); await p.waitForTimeout(300); await p.keyboard.press("Enter"); await p.waitForTimeout(800); await shot("#side", "side_compare");
    await p.locator(".lyrBtn").click(); await p.waitForTimeout(200);
    await p.locator(`input[data-k="hnames"]`).check(); await p.waitForTimeout(300);
    await p.locator("#momRow .btn", { hasText: "1913" }).dispatchEvent("click"); await p.waitForTimeout(2000); await shot("#stage", "layers");
    await p.locator(".lyrBtn").click();
    await p.locator(`input[data-k="hnames"]`).count();
    for (const c of ["#shareChart", "#leadChart", "#pcChart", "#gapChart", "#t1700"]) await shot(c, c.slice(1));
    await p.locator("#play").click(); await p.waitForTimeout(2500); await p.locator("#play").click(); await shot("#stage", "played");
    if (nm === "phone") {
      await p.click("#theme"); await p.waitForTimeout(800); await shot("#shareChart", "dark_share"); await shot("#stage", "dark_stage");
      await p.locator("#stage .mfs-btn").click(); await p.waitForTimeout(1500); await p.screenshot({ path: jpg("fullscreen"), type: "jpeg", quality: 70 });
    }
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    console.log(nm, "horizontal overflow px:", ov);
    await p.close();
  }
  console.log("errors:", errs.length ? errs : "none");
  await b.close();
})();
