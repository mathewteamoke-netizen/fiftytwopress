(function () {
  // Stress score
  var verdicts = [
    ["Green. You had the week.", "Keep the routine that got you here. Write down what worked."],
    ["Amber. Watch the drift.", "Pick one thing to drop next week before it picks itself."],
    ["Orange. The week is pulling.", "Block recovery into the planner like it's a meeting. It is."],
    ["Red. The week had you.", "Three reds in a row is a trend, not a bad week. Plan the way back."]
  ];
  function band(s) { return s <= 2 ? 0 : s <= 5 ? 1 : s <= 7 ? 2 : 3; }
  document.querySelectorAll("[data-score]").forEach(function (box) {
    var btns = Array.prototype.slice.call(box.querySelectorAll(".score-grid button"));
    var v = box.querySelector("[data-verdict]"), a = box.querySelector("[data-advice]");
    function paint(s) {
      btns.forEach(function (b, i) {
        var on = i <= s, c = b.getAttribute("data-c");
        b.style.background = on ? c : ""; b.style.borderColor = on ? c : "";
        b.setAttribute("aria-pressed", i === s ? "true" : "false");
      });
      var k = verdicts[band(s)]; v.textContent = k[0]; a.textContent = k[1];
    }
    btns.forEach(function (b, i) { b.addEventListener("click", function () { paint(i); }); });
    paint(3);
  });

  // Reveal on scroll
  var els = document.querySelectorAll(".rv");
  if (!("IntersectionObserver" in window)) { els.forEach(function (e) { e.classList.add("in"); }); return; }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.1 });
  els.forEach(function (e) { io.observe(e); });
})();
(function () {
  var cfg = document.getElementById("store-config"); if (!cfg) return;
  cfg = JSON.parse(cfg.textContent);
  var byCode = {}; cfg.stores.forEach(function (s) { byCode[s.code] = s; });
  var picks = Array.prototype.slice.call(document.querySelectorAll(".storepick"));
  if (!picks.length) return;
  function guess() {
    try { var saved = localStorage.getItem("ftp-store"); if (saved && byCode[saved]) return saved; } catch (e) {}
    var langs = (navigator.languages || [navigator.language || ""]);
    for (var i = 0; i < langs.length; i++) {
      var m = /-([A-Z]{2})$/i.exec(langs[i] || ""); if (!m) continue;
      var c = m[1].toUpperCase(); if (c === "UK") c = "GB";
      if (byCode[c]) return c;
      if (["AT","BE","CH","LU","PL","CZ","SE","DK","FI","NO","IE","PT","GR"].indexOf(c) >= 0) return "DE";
      if (c === "NZ") return "AU";
    }
    // No country in the language (common in Facebook/Instagram in-app browsers, which report just "en"):
    // fall back to the device time zone before defaulting to AU.
    try {
      var tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
      var tzMap = { "Europe/London": "GB", "Europe/Paris": "FR", "Europe/Rome": "IT", "Europe/Madrid": "ES",
        "Europe/Amsterdam": "NL", "Asia/Tokyo": "JP", "Pacific/Auckland": "AU" };
      if (tzMap[tz]) return tzMap[tz];
      if (/^America\/(Toronto|Vancouver|Edmonton|Winnipeg|Halifax|St_Johns|Regina|Montreal|Moncton|Whitehorse|Yellowknife|Iqaluit|Glace_Bay|Goose_Bay)$/.test(tz)) return "CA";
      if (/^(America|US)\//.test(tz) || tz === "Pacific/Honolulu") return "US";
      if (/^Australia\//.test(tz)) return "AU";
      if (/^Europe\//.test(tz)) return "DE";
    } catch (e) {}
    return "AU";
  }
  // Attribution: remember which ad sent this visitor (utm_content), for the whole session.
  var adKey = "";
  try {
    var q = new URLSearchParams(location.search), uc = q.get("utm_content"), us = q.get("utm_source");
    if (uc) { adKey = uc.replace(/[^a-z0-9]/gi, "").toLowerCase().slice(0, 12); sessionStorage.setItem("ftp-ad", adKey); sessionStorage.setItem("ftp-src", us || ""); }
    else { adKey = sessionStorage.getItem("ftp-ad") || ""; }
  } catch (e) {}
  // Per-ad Associates tracking ID: fiftytwopress-<adKey>-22 (AU) / -20 (US). Create them in Associates > Manage tracking IDs.
  // Tracking IDs as they actually exist in Associates (US one was created with a typo).
  var tagFix = { "-20": { founderbroll: "founderbrol" } };
  function tagFor(s) {
    if (!s.tag) return "";
    if (!adKey) return s.tag;
    var suffix = s.tag.slice(s.tag.lastIndexOf("-"));
    var key = (tagFix[suffix] && tagFix[suffix][adKey]) || adKey;
    return "fiftytwopress-" + key + suffix;
  }
  function apply(code) {
    var s = byCode[code] || byCode.AU;
    document.querySelectorAll("a.buy").forEach(function (a) {
      var tag = tagFor(s);
      a.href = "https://www." + s.domain + "/dp/" + a.getAttribute("data-asin") + (tag ? "?tag=" + tag : "");
      a.setAttribute("data-store", code);
    });
    document.querySelectorAll("[data-price]").forEach(function (el) {
      var p = (cfg.prices[el.getAttribute("data-price")] || {})[code];
      el.innerHTML = p ? p + "<small>" + s.cur + "</small>" : "Price on Amazon";
    });
    document.querySelectorAll("[data-storename]").forEach(function (el) { el.textContent = s.domain; });
    document.querySelectorAll("a.pick-link").forEach(function (a) {
      a.href = "https://www." + s.domain + "/s?k=" + encodeURIComponent(a.getAttribute("data-q")) + (s.tag ? "&tag=" + s.tag : "");
    });
    picks.forEach(function (pk) {
      pk.querySelector(".sp-flag").src = "/assets/flags/" + code.toLowerCase() + ".svg";
      pk.querySelector(".sp-name").textContent = s.label;
      pk.querySelectorAll("li").forEach(function (li) { li.setAttribute("aria-selected", li.getAttribute("data-code") === code ? "true" : "false"); });
    });
    try { localStorage.setItem("ftp-store", code); } catch (e) {}
  }
  function close(pk) { pk.querySelector(".sp-list").hidden = true; pk.querySelector(".sp-btn").setAttribute("aria-expanded", "false"); }
  picks.forEach(function (pk) {
    var btn = pk.querySelector(".sp-btn"), list = pk.querySelector(".sp-list");
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = list.hidden; picks.forEach(close);
      if (open) { list.hidden = false; btn.setAttribute("aria-expanded", "true"); }
    });
    list.querySelectorAll("li").forEach(function (li) {
      li.tabIndex = 0;
      li.addEventListener("click", function () { apply(li.getAttribute("data-code")); close(pk); });
      li.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); apply(li.getAttribute("data-code")); close(pk); btn.focus(); } });
    });
    pk.addEventListener("keydown", function (e) { if (e.key === "Escape") { close(pk); btn.focus(); } });
  });
  document.addEventListener("click", function () { picks.forEach(close); });
  // Pixel: count people who actually go through to Amazon (the buyer proxy Meta optimises on).
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a.buy"); if (!a || !window.fbq) return;
    fbq("trackCustom", "AmazonClick", { asin: a.getAttribute("data-asin"), store: a.getAttribute("data-store"), ad: adKey });
    fbq("track", "InitiateCheckout", { content_ids: [a.getAttribute("data-asin")], content_type: "product" });
  });
  var sf = document.querySelector("form[data-signup]");
  if (sf) sf.addEventListener("submit", function () { if (window.fbq) fbq("track", "Lead"); });
  apply(guess());
})();

(function () {
  var hdr = document.querySelector(".hdr"); if (!hdr) return;
  var links = Array.prototype.slice.call(document.querySelectorAll(".nav a[href*='#']"));
  var secs = links.map(function (a) { var id = a.getAttribute("href").split("#")[1]; return document.getElementById(id); }).filter(Boolean);
  function onScroll() {
    hdr.classList.toggle("is-scrolled", window.scrollY > 8);
    var y = window.scrollY + 120, cur = null;
    secs.forEach(function (s) { if (s.offsetTop <= y) cur = s.id; });
    links.forEach(function (a) { a.classList.toggle("is-active", cur && a.getAttribute("href").endsWith("#" + cur)); });
  }
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
})();
