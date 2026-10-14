// Runs in the browser. Switches the page between its states (see SPEC.md section 3).

// Largest photo the server accepts (10 MB). The same limit is in app.py.
const MAX_PHOTO_BYTES = 10 * 1024 * 1024;

const startSection = document.getElementById("start");
const previewSection = document.getElementById("preview");
const resultSection = document.getElementById("result");
const problemSection = document.getElementById("problem");

const cameraInput = document.getElementById("camera-input");
const libraryInput = document.getElementById("library-input");
const previewImage = document.getElementById("preview-image");
const resultImage = document.getElementById("result-image");
const problemMessage = document.getElementById("problem-message");

// Show one state and hide the others.
function showState(section) {
  startSection.hidden = true;
  previewSection.hidden = true;
  resultSection.hidden = true;
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

// 92 -> "92%", 0 -> "under 1%" (a 0.8% candidate shouldn't look like it scored nothing)
function formatConfidence(percent) {
  if (percent < 1) {
    return "under 1%";
  }
  return percent + "%";
}

// "Iris × hollandica" -> "https://en.wikipedia.org/wiki/Iris_%C3%97_hollandica"
function wikipediaLink(scientificName) {
  return "https://en.wikipedia.org/wiki/" + encodeURIComponent(scientificName.replaceAll(" ", "_"));
}

// Fill in the result screen: state C when confident, state D when not.
// Names come from another service, so they're always set with textContent, never as HTML.
function showResult(result) {
  const best = result.candidates[0];

  // Common name as the headline, scientific name underneath.
  // Without a common name, the scientific name becomes the headline instead.
  const mainName = document.getElementById("main-name");
  const secondName = document.getElementById("second-name");
  if (best.common_name) {
    mainName.textContent = best.common_name;
    mainName.classList.remove("scientific");
    secondName.textContent = best.scientific_name;
    secondName.hidden = false;
  } else {
    mainName.textContent = best.scientific_name;
    mainName.classList.add("scientific");
    secondName.textContent = "";
    secondName.hidden = true; // no blank line
  }

  document.getElementById("confidence").textContent = formatConfidence(best.confidence);

  // State D extras: the warning, the "Best guess" label and the other candidates.
  const unsure = !result.confident;
  document.getElementById("unsure-warning").hidden = !unsure;
  document.getElementById("best-guess-label").hidden = !unsure;

  const others = result.candidates.slice(1);
  const list = document.getElementById("candidate-list");
  list.replaceChildren();
  for (const candidate of others) {
    const link = document.createElement("a");
    link.href = wikipediaLink(candidate.scientific_name);
    link.target = "_blank"; // opens in a new tab
    link.rel = "noopener";
    link.textContent = candidate.scientific_name;

    // "African marigold (Tagetes erecta): 7%", or "Tagetes erecta: 7%" without a common name
    const item = document.createElement("li");
    if (candidate.common_name) {
      item.append(candidate.common_name + " (", link, ")");
    } else {
      item.append(link);
    }
    item.append(": " + formatConfidence(candidate.confidence));
    list.append(item);
  }
  document.getElementById("other-candidates").hidden = !(unsure && others.length > 0);

  resultImage.src = previewImage.src;
  showState(resultSection);
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
    // Our server explains known problems (E1, E3-E7, E9, E10) in an "error" field.
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

  showResult(await response.json());
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
  showState(previewSection);

  sendPhoto(file);
}

function startOver() {
  if (previewImage.src) {
    URL.revokeObjectURL(previewImage.src); // Free the memory used by the photo.
    previewImage.removeAttribute("src");
    resultImage.removeAttribute("src");
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
