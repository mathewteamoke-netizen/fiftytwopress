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
