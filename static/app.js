// Runs in the browser. Switches the page between its states (see SPEC.md section 3).

// Largest photo the server accepts (10 MB). The same limit is in app.py.
const MAX_PHOTO_BYTES = 10 * 1024 * 1024;

const startSection = document.getElementById("start");
const previewSection = document.getElementById("preview");
const problemSection = document.getElementById("problem");

const cameraInput = document.getElementById("camera-input");
const libraryInput = document.getElementById("library-input");
const previewImage = document.getElementById("preview-image");
const statusNote = document.getElementById("status-note");
const problemMessage = document.getElementById("problem-message");

// Show one state and hide the others.
function showState(section) {
  startSection.hidden = true;
  previewSection.hidden = true;
  problemSection.hidden = true;
  section.hidden = false;
}

// Show the Problem state (E) with one of the messages from SPEC.md section 5.
function showProblem(message) {
  problemMessage.textContent = message;
  showState(problemSection);
}

// Some browsers don't report a type for iPhone HEIC photos, so also check the file name.
function isImage(file) {
  const name = file.name.toLowerCase();
  return file.type.startsWith("image/") || name.endsWith(".heic") || name.endsWith(".heif");
}

// 9282587 bytes -> "8.9 MB", 31599 bytes -> "31 KB"
function formatSize(bytes) {
  const megabytes = bytes / (1024 * 1024);
  if (megabytes >= 1) {
    return megabytes.toFixed(1) + " MB";
  }
  return Math.round(bytes / 1024) + " KB";
}

// Send the photo to the server and show its reply.
async function sendPhoto(file) {
  const formData = new FormData();
  formData.append("photo", file);

  let response;
  try {
    response = await fetch("/identify", { method: "POST", body: formData });
  } catch (error) {
    // fetch only fails like this when the server can't be reached at all.
    showProblem("Couldn't connect. Check your signal and try again."); // E2
    return;
  }

  if (!response.ok) {
    // Our server explains known problems (like E1 or E9) in an "error" field.
    // Anything else, such as a crash, gets the general message E8.
    let message = "Something went wrong. Please try again.";
    try {
      const reply = await response.json();
      if (reply.error) {
        message = reply.error;
      }
    } catch (error) {
      // The reply wasn't JSON, so keep the general message.
    }
    showProblem(message);
    return;
  }

  // For now the server just reports what it received. Pl@ntNet comes in step 4.
  const result = await response.json();
  statusNote.textContent =
    "Server received: " + result.filename + " (" + result.content_type + ", " + formatSize(result.size_bytes) + ")";
}

function handlePhoto(event) {
  const file = event.target.files[0];
  if (!file) {
    return; // The person closed the picker without choosing anything.
  }

  if (!isImage(file)) {
    showProblem("That file isn't a photo. Please choose a JPG or PNG image."); // E1
    return;
  }

  // Checked here too, so a huge photo isn't uploaded only to be refused.
  if (file.size > MAX_PHOTO_BYTES) {
    showProblem("That photo is too large (over 10 MB). Please choose a smaller one."); // E9
    return;
  }

  // Show the photo straight from the device while it uploads.
  previewImage.src = URL.createObjectURL(file);
  statusNote.textContent = "Identifying...";
  showState(previewSection);

  sendPhoto(file);
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
