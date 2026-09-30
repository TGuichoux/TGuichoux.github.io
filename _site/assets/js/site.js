"use strict";

// All interactive behaviour is progressive enhancement. The page content and
// media remain accessible if JavaScript is unavailable.
(function () {
  function initResponsiveChapterMenu() {
    const desktop = window.matchMedia("(min-width: 960px)");
    const chapterMenu = document.querySelector("[data-responsive-details]");
    if (!chapterMenu) return;

    const setMenu = () => {
      chapterMenu.open = desktop.matches;
    };

    setMenu();

    // Modern browsers.
    if (typeof desktop.addEventListener === "function") {
      desktop.addEventListener("change", setMenu);
      return;
    }

    // Compatibility fallback for older Safari versions.
    if (typeof desktop.addListener === "function") {
      desktop.addListener(setMenu);
    }
  }

  function initCopyButtons() {
    document.querySelectorAll("[data-copy-target]").forEach((button) => {
      button.hidden = false;

      button.addEventListener("click", async () => {
        const citation = document.getElementById(button.dataset.copyTarget);
        const status = button.parentElement
          ? button.parentElement.querySelector(".copy-status")
          : null;

        if (!citation) return;

        try {
          if (!navigator.clipboard || !window.isSecureContext) {
            throw new Error("Clipboard unavailable");
          }

          await navigator.clipboard.writeText(citation.textContent);
          if (status) status.textContent = "Citation copied.";
        } catch (_) {
          const selection = window.getSelection();
          const range = document.createRange();
          range.selectNodeContents(citation);
          selection.removeAllRanges();
          selection.addRange(range);
          citation.parentElement.focus();
          if (status) {
            status.textContent = "Citation selected. Press ⌘C on Mac or Ctrl+C to copy.";
          }
        }
      });
    });
  }

  function initSite() {
    // Keep features isolated so a browser compatibility issue in one component
    // cannot disable unrelated components such as the video carousel.
    try {
      initResponsiveChapterMenu();
    } catch (error) {
      console.error("Could not initialize responsive chapter menu:", error);
    }

    try {
      initCopyButtons();
    } catch (error) {
      console.error("Could not initialize copy buttons:", error);
    }

  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSite, { once: true });
  } else {
    initSite();
  }
})();
