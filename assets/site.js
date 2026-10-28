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
  var sel = document.getElementById("store"); if (!sel) return;
  var byCode = {}; cfg.stores.forEach(function (s) { byCode[s.code] = s; });
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
    return "AU";
  }
  function apply(code) {
    var s = byCode[code] || byCode.AU;
    document.querySelectorAll("a.buy").forEach(function (a) {
      var asin = a.getAttribute("data-asin");
      a.href = "https://www." + s.domain + "/dp/" + asin + (s.tag ? "?tag=" + s.tag : "");
    });
    document.querySelectorAll("[data-price]").forEach(function (el) {
      var p = (cfg.prices[el.getAttribute("data-price")] || {})[code];
      el.innerHTML = p ? p + '<small>' + s.cur + '</small>' : "See price on Amazon";
    });
    document.querySelectorAll("[data-storename]").forEach(function (el) { el.textContent = s.domain; });
    sel.value = code;
    try { localStorage.setItem("ftp-store", code); } catch (e) {}
  }
  var all = document.querySelectorAll("select.store-sync");
  all.forEach(function (x) { x.addEventListener("change", function () { apply(x.value); }); });
  function applyAll(code) { apply(code); all.forEach(function (x) { x.value = code; }); }
  all.forEach(function (x) { x.addEventListener("change", function () { applyAll(x.value); }); });
  applyAll(guess());
})();
