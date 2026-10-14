// Runs in the browser. Switches the page between its states (see SPEC.md section 3).

const startSection = document.getElementById("start");
const previewSection = document.getElementById("preview");
const problemSection = document.getElementById("problem");

const cameraInput = document.getElementById("camera-input");
const libraryInput = document.getElementById("library-input");
const previewImage = document.getElementById("preview-image");
const problemMessage = document.getElementById("problem-message");

// Show one state and hide the others.
function showState(section) {
  startSection.hidden = true;
  previewSection.hidden = true;
  problemSection.hidden = true;
  section.hidden = false;
}

// Some browsers don't report a type for iPhone HEIC photos, so also check the file name.
function isImage(file) {
  const name = file.name.toLowerCase();
  return file.type.startsWith("image/") || name.endsWith(".heic") || name.endsWith(".heif");
}

function handlePhoto(event) {
  const file = event.target.files[0];
  if (!file) {
    return; // The person closed the picker without choosing anything.
  }

  if (!isImage(file)) {
    // Error E1 from SPEC.md section 5.
    problemMessage.textContent = "That file isn't a photo. Please choose a JPG, PNG or HEIC image.";
    showState(problemSection);
    return;
  }

  // Show the photo straight from the device. Nothing is uploaded yet.
  previewImage.src = URL.createObjectURL(file);
  showState(previewSection);
}

function startOver() {
  if (previewImage.src) {
    URL.revokeObjectURL(previewImage.src); // Free the memory used by the preview.
    previewImage.removeAttribute("src");
  }
  // Clear the pickers so choosing the same photo again still works.
  cameraInput.value = "";
  libraryInput.value = "";
  showState(startSection);
}

cameraInput.addEventListener("change", handlePhoto);
libraryInput.addEventListener("change", handlePhoto);

document.querySelectorAll("[data-action='start-over']").forEach(function (button) {
  button.addEventListener("click", startOver);
});
