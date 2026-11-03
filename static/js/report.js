const form = document.getElementById("report-form");
const description = document.getElementById("description");
const cell = document.getElementById("reporter_cell");

function showError(field, errorId, message) {
  const errorBox = document.getElementById(errorId);

  errorBox.textContent = message;

  if (message) {
    field.classList.add("is-invalid");
  } else {
    field.classList.remove("is-invalid");
  }
}

// Check description length
function checkDescription() {
  const length = description.value.trim().length;

  if (length < 10 || length > 500) {
    showError(
      description,
      "description-error",
      "Your description must be between 10 and 500 characters. Currently: " +
        length +
        ".",
    );
    return false;
  }

  showError(description, "description-error", "");
  return true;
}

// Check South African cell number
function checkCell() {
  if (!/^0\d{9}$/.test(cell.value.trim())) {
    showError(
      cell,
      "cell-error",
      "Your cell number must contain 10 digits starting with 0.",
    );
    return false;
  }

  showError(cell, "cell-error", "");
  return true;
}

// Check fields while the resident types
description.addEventListener("input", checkDescription);
cell.addEventListener("input", checkCell);

// Check both fields before submitting
form.addEventListener("submit", function (event) {
  const descriptionOk = checkDescription();
  const cellOk = checkCell();

  if (!descriptionOk || !cellOk) {
    event.preventDefault();
  }
});

// Save and restore report drafts
const DRAFT_KEY = "ward42-report-draft";
const draftFields = ["category", "street", "description"];

function saveDraft() {
  const draft = {};

  draftFields.forEach(function (id) {
    const field = document.getElementById(id);
    if (field) {
      draft[id] = field.value;
    }
  });

  try {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
  } catch (error) {
    // Storage unavailable or full; the form still works.
  }
}

function restoreDraft() {
  try {
    const saved = localStorage.getItem(DRAFT_KEY);
    if (!saved) return;

    const draft = JSON.parse(saved);

    draftFields.forEach(function (id) {
      const field = document.getElementById(id);

      if (field && typeof draft[id] === "string") {
        field.value = draft[id];
      }
    });
  } catch (error) {
    localStorage.removeItem(DRAFT_KEY);
  }
}

draftFields.forEach(function (id) {
  const field = document.getElementById(id);

  if (field) {
    field.addEventListener("input", saveDraft);
    field.addEventListener("change", saveDraft);
  }
});

restoreDraft();
