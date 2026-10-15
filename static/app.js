// Runs in the browser. Switches the page between its states (see SPEC.md section 3).

// Largest photo the server accepts (10 MB). The same limit is in app.py.
const MAX_PHOTO_BYTES = 10 * 1024 * 1024;

// Photos are shrunk so their longest side is at most this many pixels before uploading.
// Tested in step 6a: Pl@ntNet gave essentially the same answer for a 1600-pixel copy.
const MAX_PHOTO_PIXELS = 1600;
const JPEG_QUALITY = 0.85;

// How long the page waits for an answer before giving up (E3).
// Longer than the server's own worst case (upload ~5 s + Pl@ntNet 20 s + Wikipedia 5 s),
// so the page never gives up on an answer that was about to arrive.
const PAGE_TIMEOUT_MS = 35 * 1000;

// Messages the page shows by itself (SPEC.md section 5). The server sends its own.
const E1_NOT_A_PHOTO = "That file isn't a photo. Please choose a JPG or PNG image.";
const E2_NO_CONNECTION = "Couldn't connect. Check your signal and try again.";
const E3_TOO_SLOW = "Identification is taking too long. Please try again.";
const E8_UNEXPECTED = "Something went wrong. Please try again.";
const E9_TOO_LARGE = "That photo is too large (over 10 MB). Please choose a smaller one.";

// The photo being identified (already shrunk), kept so "Try again" can send it again.
let currentPhoto = null;

// Every new photo, Try again and Start over begins a new numbered attempt.
// A reply that arrives for an older attempt is ignored, so a slow answer for
// the previous flower never appears on top of the next one.
let currentAttempt = 0;

function startNewAttempt() {
  currentAttempt += 1;
  return currentAttempt;
}

function isOutdated(attempt) {
  return attempt !== currentAttempt;
}

const startSection = document.getElementById("start");
const previewSection = document.getElementById("preview");
const resultSection = document.getElementById("result");
const problemSection = document.getElementById("problem");

const cameraInput = document.getElementById("camera-input");
const libraryInput = document.getElementById("library-input");
const previewImage = document.getElementById("preview-image");
const resultImage = document.getElementById("result-image");
const problemMessage = document.getElementById("problem-message");
const tryAgainButton = document.getElementById("try-again");

// Show one state and hide the others.
function showState(section) {
  startSection.hidden = true;
  previewSection.hidden = true;
  resultSection.hidden = true;
  problemSection.hidden = true;
  section.hidden = false;
}

// Show the Problem state (E) with one of the messages from SPEC.md section 5.
// canRetry shows the "Try again" button: only when sending the same photo again might work.
function showProblem(message, canRetry) {
  problemMessage.textContent = message;
  tryAgainButton.hidden = !canRetry;
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

// The Wikipedia part of the result: the summary and link, or a W1/W2 message (SPEC.md section 5).
function showWikipedia(wikipedia) {
  const summary = document.getElementById("wikipedia-summary");
  const reference = document.getElementById("wikipedia-reference");
  const problem = document.getElementById("wikipedia-problem");

  // Only accept normal web links: a link starting with "javascript:" could run code when tapped.
  const found = wikipedia.status === "found" && wikipedia.url.startsWith("https://");

  summary.hidden = !found;
  reference.hidden = !found;
  problem.hidden = found;

  // "Did you know?" only when Wikipedia found a fun fact; otherwise the box stays hidden.
  const funFact = document.getElementById("fun-fact");
  funFact.hidden = !(found && wikipedia.fun_fact);
  document.getElementById("fun-fact-text").textContent = funFact.hidden ? "" : wikipedia.fun_fact;

  if (found) {
    summary.textContent = wikipedia.summary;
    document.getElementById("wikipedia-link").href = wikipedia.url;
  } else if (wikipedia.status === "no_article") {
    problem.textContent = "No Wikipedia article found"; // W1
  } else {
    problem.textContent = "Couldn't load the Wikipedia summary right now"; // W2
  }
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

  showWikipedia(result.wikipedia);

  resultImage.src = previewImage.src;
  showState(resultSection);
}

// Make a smaller JPEG copy of the photo (SPEC.md step 6): much faster to upload on a walk.
// The copy holds only pixels, so hidden data such as GPS location is left behind.
// HEIC photos come out as JPEG too, which is all Pl@ntNet accepts.
// If this browser can't read the photo, send the original; the server still checks it.
async function shrinkPhoto(file) {
  try {
    const image = await createImageBitmap(file); // turned the right way up, as the camera intended
    const scale = Math.min(1, MAX_PHOTO_PIXELS / Math.max(image.width, image.height));

    const canvas = document.createElement("canvas");
    canvas.width = Math.round(image.width * scale);
    canvas.height = Math.round(image.height * scale);
    canvas.getContext("2d").drawImage(image, 0, 0, canvas.width, canvas.height);

    const smaller = await new Promise(function (resolve) {
      canvas.toBlob(resolve, "image/jpeg", JPEG_QUALITY);
    });
    return smaller || file;
  } catch (error) {
    return file;
  }
}

// Send the photo to the server and show its reply, unless a newer attempt has started meanwhile.
async function sendPhoto(photo, attempt) {
  const formData = new FormData();
  formData.append("photo", photo, "photo.jpg");

  let response;
  try {
    response = await fetch("/identify", {
      method: "POST",
      body: formData,
      signal: AbortSignal.timeout(PAGE_TIMEOUT_MS), // cancels the request if it takes too long
    });
  } catch (error) {
    if (isOutdated(attempt)) {
      return;
    }
    if (error.name === "TimeoutError") {
      showProblem(E3_TOO_SLOW, true);
    } else {
      // Otherwise fetch only fails like this when the server can't be reached at all.
      showProblem(E2_NO_CONNECTION, true);
    }
    return;
  }

  if (isOutdated(attempt)) {
    return;
  }

  if (!response.ok) {
    // Our server explains known problems (E1, E3-E7, E9, E10) in an "error" field,
    // and says whether trying again could help. Anything else, such as a crash, is E8.
    let message = E8_UNEXPECTED;
    let canRetry = true;
    try {
      const reply = await response.json();
      if (reply.error) {
        message = reply.error;
        canRetry = reply.can_retry === true;
      }
    } catch (error) {
      // The reply wasn't JSON, so keep the general message.
    }
    if (isOutdated(attempt)) {
      return;
    }
    showProblem(message, canRetry);
    return;
  }

  let result;
  try {
    result = await response.json();
  } catch (error) {
    if (isOutdated(attempt)) {
      return;
    }
    // The deadline can also run out while the reply is still downloading.
    showProblem(error.name === "TimeoutError" ? E3_TOO_SLOW : E8_UNEXPECTED, true);
    return;
  }
  if (isOutdated(attempt)) {
    return;
  }
  showResult(result);
}

async function handlePhoto(event) {
  const file = event.target.files[0];
  if (!file) {
    return; // The person closed the picker without choosing anything.
  }

  const attempt = startNewAttempt();

  if (!isImage(file)) {
    showProblem(E1_NOT_A_PHOTO, false);
    return;
  }

  // Show the photo straight from the device while it's prepared and uploaded.
  previewImage.src = URL.createObjectURL(file);
  showState(previewSection);

  const photo = await shrinkPhoto(file);
  if (isOutdated(attempt)) {
    return; // Start over was pressed while the photo was being shrunk
  }

  // Checked here too, so a huge photo isn't uploaded only to be refused.
  // Checked after shrinking, so a big photo that shrinks small enough is fine.
  if (photo.size > MAX_PHOTO_BYTES) {
    showProblem(E9_TOO_LARGE, false);
    return;
  }

  currentPhoto = photo;
  sendPhoto(photo, attempt);
}

// Send the same photo again, without retaking or choosing it.
function tryAgain() {
  showState(previewSection);
  sendPhoto(currentPhoto, startNewAttempt());
}

function startOver() {
  startNewAttempt(); // any reply still on its way is now outdated
  if (previewImage.src) {
    URL.revokeObjectURL(previewImage.src); // Free the memory used by the photo.
    previewImage.removeAttribute("src");
    resultImage.removeAttribute("src");
  }
  currentPhoto = null;
  // Clear the pickers so choosing the same photo again still works.
  cameraInput.value = "";
  libraryInput.value = "";
  showState(startSection);
}

cameraInput.addEventListener("change", handlePhoto);
libraryInput.addEventListener("change", handlePhoto);
tryAgainButton.addEventListener("click", tryAgain);

document.querySelectorAll("[data-action='start-over']").forEach(function (button) {
  button.addEventListener("click", startOver);
});
