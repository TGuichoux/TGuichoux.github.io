"use strict";

// Modern Kramdown emits MathJax delimiters directly. Also normalize legacy
// script[type="math/tex"] output before the deferred MathJax script executes.
document.querySelectorAll('script[type^="math/tex"]').forEach((source) => {
  const display = source.type.includes("mode=display");
  const equation = document.createElement(display ? "div" : "span");
  equation.className = display ? "equation equation--display" : "equation";
  equation.textContent = (display ? "\\[" : "\\(") + source.textContent + (display ? "\\]" : "\\)");
  source.replaceWith(equation);
});
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true
  },
  svg: { fontCache: "global" },
  options: { skipHtmlTags: ["script", "noscript", "style", "textarea", "pre", "code"] }
};
