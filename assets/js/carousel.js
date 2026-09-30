"use strict";

/* Version 3. Native scroll-snap is the foundation, not a hidden-slide widget.
 * Loaded at the end of <body>; no dependency on site.js, MathJax, or a video CDN.
 * First-frame previews use the video element itself, never a cross-origin canvas.
 */
(function () {
  var version = "3.2.0";
  // Error/retry handling applies to every player, including static-poster players.
  var videos = Array.prototype.slice.call(document.querySelectorAll(".media-video video"));
  var carousels = [];

  function all(root, selector) {
    return Array.prototype.slice.call(root.querySelectorAll(selector));
  }

  function closest(element, selector) {
    if (element && element.nodeType !== 1) element = element.parentElement;
    while (element && element.nodeType === 1) {
      if (element.matches(selector)) return element;
      element = element.parentElement;
    }
    return null;
  }

  function prepareVideo(video, force) {
    if (!video) return;
    // A real, local static poster is preferred, with no video request until play.
    if (!force && (!video.hasAttribute("data-first-frame") || video.getAttribute("poster") || video.dataset.firstFrameState)) return;
    video.dataset.firstFrameState = "loading";
    var figure = closest(video, ".media-video");
    var status = figure && figure.querySelector("[data-video-status]");
    if (status) status.hidden = true;
    video.preload = "metadata";
    try {
      video.load();
    } catch (error) {
      video.dataset.firstFrameState = "error";
      if (status) status.hidden = false;
    }
  }

  function initVideo(video) {
    var figure = closest(video, ".media-video");
    var status = figure && figure.querySelector("[data-video-status]");
    var retry = figure && figure.querySelector("[data-video-retry]");
    var played = false;
    var timer = null;

    function stopTimer() {
      if (timer !== null) window.clearTimeout(timer);
      timer = null;
    }

    function failed() {
      stopTimer();
      video.dataset.firstFrameState = "error";
      if (status) status.hidden = false;
    }

    function ready() {
      stopTimer();
      video.dataset.firstFrameState = played ? "played" : "ready";
      if (status) status.hidden = true;
    }

    function watchPendingMedia() {
      stopTimer();
      if (video.readyState >= 2) return;
      // A slow or unreachable remote file never prevents carousel navigation.
      timer = window.setTimeout(function () {
        if (video.readyState < 2) failed();
      }, 20000);
    }

    video.addEventListener("loadstart", function () {
      stopTimer();
      if (status) status.hidden = true;
      // A preload="none" player may emit loadstart and then suspend without
      // requesting the MP4. An idle static poster is not a loading failure.
      if (video.preload === "none" && video.paused && !played) return;
      watchPendingMedia();
    });
    video.addEventListener("loadedmetadata", function () {
      if (!video.hasAttribute("data-first-frame") || played || !video.paused || video.getAttribute("poster")) return;
      // Seeking into the first frame makes Safari display it without autoplay.
      // Do not add crossorigin: drawing to a canvas is not used or required.
      if (Number.isFinite(video.duration) && video.duration > 0) {
        try {
          video.currentTime = Math.min(0.001, video.duration / 2);
        } catch (_) {
          // Some engines will already have decoded the first frame at time zero.
        }
      }
    });
    video.addEventListener("loadeddata", ready);
    video.addEventListener("seeked", function () { if (video.readyState >= 2) ready(); });
    video.addEventListener("playing", ready);
    video.addEventListener("play", function () {
      played = true;
      video.dataset.firstFrameState = "played";
      watchPendingMedia();
    });
    video.addEventListener("error", failed);
    all(video, "source").forEach(function (source) { source.addEventListener("error", failed); });
    if (retry) retry.addEventListener("click", function () { prepareVideo(video, true); });
  }

  function initCarousel(carousel) {
    if (carousel.dataset.carouselReady === "true") return;
    var track = carousel.querySelector("[data-carousel-slides]");
    var slides = track ? all(track, "[data-carousel-slide]") : [];
    var controls = carousel.querySelector("[data-carousel-controls]");
    var previous = carousel.querySelector("[data-carousel-previous]");
    var next = carousel.querySelector("[data-carousel-next]");
    var select = carousel.querySelector("[data-carousel-select]");
    var counter = carousel.querySelector("[data-carousel-counter]");
    if (slides.length < 2 || !controls || !previous || !next || !select || !counter) return;
    var active = 0;
    var scrolling = false;
    var lastWidth = track.clientWidth;

    function leftFor(index) {
      return slides[index].offsetLeft - slides[0].offsetLeft;
    }

    function nearestIndex() {
      var nearest = 0;
      var distance = Infinity;
      slides.forEach(function (slide, index) {
        var d = Math.abs(leftFor(index) - track.scrollLeft);
        if (d < distance) { distance = d; nearest = index; }
      });
      return nearest;
    }

    function update(index) {
      active = Math.max(0, Math.min(slides.length - 1, index));
      slides.forEach(function (slide, slideIndex) {
        slide.classList.toggle("is-current", slideIndex === active);
        if (slideIndex !== active) {
          all(slide, "video").forEach(function (video) {
            if (!video.paused) video.pause();
          });
        }
      });
      select.value = String(active);
      counter.textContent = (active + 1) + " / " + slides.length;
      counter.setAttribute("aria-label", "Video " + (active + 1) + " of " + slides.length);
      previous.setAttribute("aria-disabled", String(active === 0));
      next.setAttribute("aria-disabled", String(active === slides.length - 1));
      carousel.dataset.activeSlide = String(active + 1);
      // IntersectionObserver lazily previews videos near the viewport. A chosen
      // slide is prepared immediately, but the remaining slides are not fetched.
      if (carousel.dataset.carouselReady === "true") {
        prepareVideo(slides[active].querySelector("video[data-first-frame]"));
      }
    }

    function show(index) {
      index = Math.max(0, Math.min(slides.length - 1, index));
      track.scrollLeft = leftFor(index);
      update(index);
    }

    previous.addEventListener("click", function () { if (active > 0) show(active - 1); });
    next.addEventListener("click", function () { if (active < slides.length - 1) show(active + 1); });
    select.addEventListener("change", function () { show(Number(select.value)); });
    carousel.addEventListener("keydown", function (event) {
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      var focusedVideo = closest(event.target, "video");
      if (focusedVideo) {
        // Before metadata exists, native left/right keys cannot seek and some
        // browsers instead nudge the surrounding scroll track. Keep that idle
        // player anchored; once loaded, leave all native video keys untouched.
        if (focusedVideo.readyState === 0 && (event.key === "ArrowLeft" || event.key === "ArrowRight")) {
          event.preventDefault();
        }
        return;
      }
      if (closest(event.target, "select, input, textarea, [contenteditable]")) return;
      var destination;
      if (event.key === "ArrowLeft") destination = active - 1;
      else if (event.key === "ArrowRight") destination = active + 1;
      else if (event.key === "Home") destination = 0;
      else if (event.key === "End") destination = slides.length - 1;
      else return;
      event.preventDefault();
      show(destination);
    });
    track.addEventListener("scroll", function () {
      if (scrolling) return;
      scrolling = true;
      window.requestAnimationFrame(function () {
        scrolling = false;
        update(nearestIndex());
      });
    }, { passive: true });

    // Touch and trackpad use the native scrollport. Also allow mouse-dragging
    // a caption, without intercepting a video's native playback/seek controls.
    var drag = null;
    track.addEventListener("pointerdown", function (event) {
      if (event.pointerType !== "mouse" || event.button !== 0) return;
      if (closest(event.target, "video, a, button, select, input")) return;
      drag = { x: event.clientX, left: track.scrollLeft, id: event.pointerId, moved: false };
    });
    track.addEventListener("pointermove", function (event) {
      if (!drag || event.pointerId !== drag.id) return;
      var delta = drag.x - event.clientX;
      if (!drag.moved && Math.abs(delta) > 8) {
        drag.moved = true;
        track.classList.add("is-dragging");
        if (track.setPointerCapture) track.setPointerCapture(event.pointerId);
      }
      if (!drag.moved) return;
      event.preventDefault();
      track.scrollLeft = drag.left + delta;
    });
    function endDrag() {
      if (!drag) return;
      var index = nearestIndex();
      var moved = drag.moved;
      drag = null;
      track.classList.remove("is-dragging");
      if (moved) show(index);
    }
    track.addEventListener("pointerup", endDrag);
    track.addEventListener("pointercancel", endDrag);
    track.addEventListener("lostpointercapture", endDrag);

    function resize() {
      if (Math.abs(track.clientWidth - lastWidth) < 1) return;
      lastWidth = track.clientWidth;
      show(active);
    }
    window.addEventListener("resize", resize);
    if (typeof window.ResizeObserver === "function") {
      var observer = new ResizeObserver(resize);
      observer.observe(track);
    }

    // Only hide the link fallback after all enhanced controls are connected.
    controls.hidden = false;
    carousel.classList.add("is-enhanced");
    carousel.setAttribute("aria-roledescription", "carousel");
    update(nearestIndex());
    carousel.dataset.carouselReady = "true";
    carousels.push({ element: carousel, slides: slides, show: show });
  }

  // Published PDF links use the existing figure IDs, not slide numbers or titles.
  // Resolve by ID (not a CSS selector), so malformed/encoded fragments are safe.
  var revealFrame = null;
  var arrival = null;

  function videoTarget(hash) {
    if (!hash || hash === "#") return null;
    var target;
    try { target = document.getElementById(decodeURIComponent(hash.slice(1))); }
    catch (_) { return null; }
    return closest(target, ".media-video");
  }

  function selectTarget(target) {
    carousels.forEach(function (item) {
      item.slides.forEach(function (slide, index) {
        if (slide === target || slide.contains(target)) item.show(index);
      });
    });
  }

  function stopArrival() {
    if (revealFrame !== null) window.cancelAnimationFrame(revealFrame);
    revealFrame = null;
    if (!arrival) return;
    window.clearTimeout(arrival.timer);
    if (arrival.observer) arrival.observer.disconnect();
    arrival = null;
  }

  function alignArrival() {
    if (!arrival) return;
    if (revealFrame !== null) window.cancelAnimationFrame(revealFrame);
    var target = arrival.target;
    revealFrame = window.requestAnimationFrame(function () {
      revealFrame = null;
      if (!arrival || target !== arrival.target || target !== videoTarget(window.location.hash)) return;
      // Native fragment scrolling/history restoration may also move the track.
      // Reuse show() after layout, keeping the selector and counter in sync.
      selectTarget(target);
      var player = target.querySelector("video");
      var view = target.getBoundingClientRect().height > window.innerHeight - 48 && player ? player : target;
      var block = view.getBoundingClientRect().height > window.innerHeight - 48 ? "start" : "center";
      view.scrollIntoView({ behavior: "auto", block: block, inline: "nearest" });
    });
  }

  function revealHash() {
    stopArrival();
    var target = videoTarget(window.location.hash);
    if (!target) return; // Leave normal section anchors and unknown hashes alone.

    selectTarget(target);
    // Returning to a previously played video must not resume it, reset its time,
    // or leave audio playing elsewhere on the page. Never call play() or load().
    videos.forEach(function (video) { if (!video.paused) video.pause(); });

    arrival = { target: target, timer: null, observer: null };
    // Lazy figures above the destination can expand just after the first scroll.
    // Briefly track layout, without waiting for any image, MP4, or MathJax request.
    // Stop immediately on user interaction; never fight the user's scrolling.
    if (typeof window.ResizeObserver === "function") {
      arrival.observer = new window.ResizeObserver(alignArrival);
      arrival.observer.observe(document.querySelector("main") || document.body);
    }
    arrival.timer = window.setTimeout(stopArrival, 3000);
    alignArrival();
  }

  videos.forEach(function (video) {
    try { initVideo(video); } catch (error) { console.error("Video setup failed:", error); }
  });
  all(document, "[data-video-carousel]").forEach(function (carousel) {
    try { initCarousel(carousel); } catch (error) { console.error("Carousel enhancement failed; native scrolling remains available:", error); }
  });

  if (typeof window.IntersectionObserver === "function") {
    var previewObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        prepareVideo(entry.target);
        previewObserver.unobserve(entry.target);
      });
    }, { rootMargin: "250px 0px", threshold: 0.01 });
    videos.forEach(function (video) {
      if (video.hasAttribute("data-first-frame") && !video.getAttribute("poster")) {
        previewObserver.observe(video);
      }
    });
  } else {
    // Older browsers: prepare only standalone videos and each group's first slide.
    videos.forEach(function (video) {
      var slide = closest(video, "[data-carousel-slide]");
      if (!slide || slide.classList.contains("is-current")) prepareVideo(video);
    });
  }

  // load does not bubble; capture handles late/lazy image loads in older browsers
  // too. The bounded arrival guard makes these listeners inert otherwise.
  document.addEventListener("load", function (event) {
    if (event.target && event.target.tagName === "IMG") alignArrival();
  }, true);
  ["pointerdown", "touchstart", "wheel", "keydown", "click", "change"].forEach(function (name) {
    window.addEventListener(name, stopArrival, { capture: true, passive: true });
  });
  window.addEventListener("hashchange", revealHash);
  window.addEventListener("popstate", revealHash);
  window.addEventListener("pageshow", function (event) {
    // Re-apply a bookmarked destination after back/forward-cache restoration.
    // Do not jump back to the hash when a slow external resource finishes loading.
    if (event.persisted) revealHash();
  });
  document.addEventListener("click", function (event) {
    if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) return;
    var anchor = closest(event.target, "a[href]");
    if (!anchor || anchor.hasAttribute("download")) return;
    var browsingTarget = anchor.getAttribute("target");
    if (browsingTarget && browsingTarget.toLowerCase() !== "_self") return;
    var href = anchor.getAttribute("href");
    if (!href) return;
    var hash;
    if (href.charAt(0) === "#") {
      hash = href;
    } else {
      // Accept full, root-relative and page-relative links to this same page;
      // let the browser handle other pages/tabs, including GitHub Pages paths.
      var url;
      try { url = new URL(href, document.baseURI); } catch (_) { return; }
      if (url.origin !== window.location.origin || url.pathname !== window.location.pathname || url.search !== window.location.search) return;
      hash = url.hash;
    }
    if (!videoTarget(hash)) return;
    event.preventDefault();
    // Native hash history supports Back/Forward without inventing a second URL
    // scheme. Re-clicking the same link reselects its video, without a new entry.
    if (window.location.hash !== hash) window.location.hash = hash;
    revealHash();
  });
  // This script is at the end of body, after the video markup. Initialize now,
  // not on DOMContentLoaded/window.load, which may wait for remote MathJax.
  revealHash();
  document.documentElement.dataset.carouselVersion = version;
})();
