if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(function (error) {
    console.error("Service worker registration failed:", error);
  });
}
