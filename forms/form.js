const STORAGE_KEY = "appendix4NominationForm";
const form = document.getElementById("appendix4-form");
const saveButton = document.getElementById("saveButton");
const clearButton = document.getElementById("clearButton");
const status = document.getElementById("status");

function showStatus(message) {
  status.textContent = message;
}

function getFormData() {
  const fields = form.querySelectorAll("input, textarea");
  const data = {};
  fields.forEach((field) => {
    if (field.name) {
      data[field.name] = field.value;
    }
  });
  return data;
}

function setFormData(data) {
  const fields = form.querySelectorAll("input, textarea");
  fields.forEach((field) => {
    if (field.name && Object.prototype.hasOwnProperty.call(data, field.name)) {
      field.value = data[field.name] || "";
    }
  });
}

function saveData() {
  const data = getFormData();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  showStatus(`Saved ${new Date().toLocaleString()}`);
}

function loadData() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return;
  }

  try {
    const saved = JSON.parse(raw);
    setFormData(saved);
    showStatus("Restored saved draft");
  } catch {
    showStatus("Saved draft could not be read");
  }
}

function clearData() {
  localStorage.removeItem(STORAGE_KEY);
  form.reset();
  showStatus("Saved draft cleared");
}

saveButton.addEventListener("click", saveData);
clearButton.addEventListener("click", clearData);

// Keep an always-current draft while the user types.
form.addEventListener("input", () => {
  const data = getFormData();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
});

document.addEventListener("DOMContentLoaded", loadData);
