try {
  localStorage.removeItem("ward42-report-draft");
} catch (error) {
  // Storage unavailable; nothing else is needed.
}
