# Flower ID web app

A personal learning project. It's a phone-friendly web page where I take or upload a flower photo. The app then shows the flower's scientific name, a confidence score and a short Wikipedia summary.

## Decisions made

- **Stack:** Python + Flask. One small app serves both the page and the backend.
- **Web app, not native:** opened in the phone's browser. No Xcode or App Store. During development the phone reaches the Mac over home Wi-Fi; after step 7 it has a public `https://` address.
- **Identification:** Pl@ntNet API (free tier, 500 requests per day). It needs an account and an API key, and their terms require an attribution line.
- **Reference text:** Wikipedia API (no key needed). Link to the article and credit Wikipedia. Requests must send a descriptive `User-Agent` header, or Wikipedia returns 403 Forbidden.
- **Two sources, always shown separately:**
  - "Identified by Pl@ntNet (confidence X%)"
  - "Reference: Wikipedia [link]"
- **Low confidence (below 50%):** show the best guess with a visible warning, plus the top 3 candidates.
- **Secrets:** API keys go in a `.env` file. Never put them in code and never paste them in chat. `.env` must be listed in `.gitignore`.

## About me / how to work with me

- I'm a beginner coder (never professional) and I use a Mac.
- **My real goal is learning how good software is written and the best practices behind it.** Always act as a guide: before each step, explain *why* we're doing it and which practice it teaches. Break work into small sub-steps and say which one is next.
- Explain every file you create in 2–3 sentences.
- Prefer simple code over clever code.
- **Ask before installing anything** (Python packages, Homebrew, tools).
- Build one small slice at a time.
- Show Mac Terminal commands only.

## Roadmap

1. Spec, in small steps:
   - 1a. Start version control (git)
   - 1b. Problem statement: what and who it's for
   - 1c. User stories: what I can do with the app
   - 1d. Screen sketch in text
   - 1e. Acceptance criteria: how we know each part works
   - 1f. Error cases
   - 1g. Out of scope: what we're not building
   - 1h. Review, answer open questions, sign off, commit
2. Photo-picker page (no API calls), in small steps:
   - 2a. Create a virtual environment (`.venv`)
   - 2b. Install Flask into it (ask first) and record it in `requirements.txt`
   - 2c. Smallest possible Flask app: "Hello" on the Mac
   - 2d. Open it from the phone over home Wi-Fi
   - 2e. Start screen (state A): the two photo buttons
   - 2f. Photo preview after picking, plus the non-image message (E1) and Start over
   - 2g. Check against acceptance criteria 1 and 2 on phone and Mac, then commit
3. Backend receives the image, in small steps:
   - 3a. Server route `/identify` that accepts a photo and replies with its details (no Pl@ntNet yet)
   - 3b. Browser sends the photo, shows "Identifying..." and displays the server's reply
   - 3c. Server double-checks the file: images only, size limit (never trust the browser). Check the file's actual first bytes, not its `content_type` label: curl sent a real HEIC as `application/octet-stream`.
   - 3d. First automated tests with pytest (ask before installing)
   - 3e. Check on phone (including a real HEIC photo) and commit
4. Pl@ntNet call, in small steps:
   - 4a. I create a Pl@ntNet account and API key; Claude reads the API docs and terms (attribution, size limits, HEIC, what happens to photos)
   - 4b. Put the key in `.env` (I type it myself, never in chat) and load it with python-dotenv (ask first)
   - 4c. `plantnet.py`: one function that sends a photo to Pl@ntNet; try it once from Terminal and study the raw reply
   - 4d. `/identify` returns the name, common name, confidence and top 3
   - 4e. The page shows the Pl@ntNet part of states C and D (50% rule)
   - 4f. Tests that don't use the real API (no quota used, work offline)
   - 4g. Real flowers on the phone, then commit and tag
5. Wikipedia lookup and two-source display
6. Error handling, plus shrinking photos to about 1 MB **and converting them to JPEG** in the browser before upload (this also removes E10, the HEIC refusal). Includes: the **Try again** button (E2, E3, E7, E8), time limits, and ignoring a late server reply if I've already pressed Start over.
7. Put it online
8. Review

## Current step

Setup done: Python 3.15.0 installed from python.org, with certificates set up.
1a done: git started (branch `main`), `.gitignore` created.
1b done: problem statement approved, in `SPEC.md` section 1.
1c done: user stories approved, in `SPEC.md` section 2 (show common name too; one photo per identification).
1d done: screen sketch approved, in `SPEC.md` section 3, plus "How I open the app".
1e done: acceptance criteria approved, in `SPEC.md` section 4 (photo shrinking deferred to step 6).
1f done: error cases approved, in `SPEC.md` section 5.
1g done: out of scope approved, in `SPEC.md` section 6.
**Step 1 complete:** spec signed off (git tag `spec-v1`). `SPEC.md` is the source of truth; check work against it.
2a done: virtual environment created in `.venv` (Python 3.15.0, ignored by git).
2b done: Flask 3.1.3 installed in `.venv`; exact versions pinned in `requirements.txt`.
2c done: `app.py` shows "Hello from Flower ID"; tested by me in the Mac browser.
2d done: the phone opens the app over home Wi-Fi (`host="0.0.0.0"`).
2e done: start screen with two photo buttons (`templates/index.html`, `static/style.css`); camera and library tested on the phone.
2f done: photo preview, non-image message (E1) and Start over (`static/app.js`).
**Step 2 complete** (git tag `step-2`): acceptance boxes ticked in `SPEC.md`. Still open: "Take a photo" on the Mac, and the full HEIC check in step 3.
3a done: `POST /identify` receives a photo and replies with JSON (filename, type, size); tested with curl.
3b done: the page uploads the photo with `fetch` and shows the server's reply; E2 and E8 messages wired up. Phone test: iPhone Safari sends **JPEG, about 2 MB** (it converts HEIC itself).
3c done: server checks first bytes (JPEG, PNG, HEIC) and a 10 MB limit; new error E9 in the spec. The page also checks size before uploading. `MAX_PHOTO_BYTES` lives in both `app.py` and `static/app.js`: change both together.
3d done: pytest 9.1.1 installed; 11 tests in `tests/test_app.py`; dev-only tools pinned in `requirements-dev.txt`.
3e done: real iPhone photos (camera and library) pass the server checks.
**Step 3 complete** (git tag `step-3`).
4a done: I have a Pl@ntNet account and key. Docs read (facts below). Decisions: Pl@ntNet's acknowledgement sentence goes under every result (text, no logo); the server refuses HEIC for now (E10) until step 6 converts photos to JPEG.
4b done: key saved in `.env` (26 characters, checked without displaying it); `.env.example` is the template in git; python-dotenv 1.2.4 loads it in `app.py`.
4c done: `plantnet.py` + `scripts/try_plantnet.py`. Real call with a mixed bouquet (`samples/IMG_2570.jpg`, ignored by git): status 200, top score only **2.6%** (Lisianthus), then Dutch Iris 1.6% and Bastard speedwell 0.8%. A real-world example of the under-50% case.
Next: 4d, `/identify` returns the name, common name, confidence and top 3.

## Environment notes

- Use `python3` (3.15.0, at `/Library/Frameworks/Python.framework/Versions/3.15/`). An old Python 3.9 is also on the Mac; ignore it.
- Two package lists: `requirements.txt` holds what the app needs to run (also used online), and `requirements-dev.txt` adds tools only needed on the Mac, like pytest. After adding a package, put it in the right file with its exact version, and commit. Rebuild everything with `pip install -r requirements-dev.txt`.
- **Run the tests before every commit:** `python -m pytest` (with `.venv` active). Add tests for each new behaviour, including failures.
- Project packages live in `.venv`. Turn it on with `source .venv/bin/activate` (prompt shows `(.venv)`), off with `deactivate`.
- Find the Mac's Wi-Fi address with `ipconfig getifaddr en0` (it was 192.168.86.23 on 2026-10-14; it can change). The phone opens `http://<that address>:5001`.
- **Testing on the phone (Safari):** after code changes, close the tab and open a fresh one. A plain refresh can keep the old page and make a working change look broken.
- The app runs on port **5001**, not Flask's usual 5000, because macOS's AirPlay Receiver uses 5000.
- Homebrew is installed but too old to run on this macOS version, so don't rely on it.

## Pl@ntNet API facts (read from their docs on 2026-10-14)

- `POST https://my-api.plantnet.org/v2/identify/all?api-key=KEY`, photos sent as form field `images`; optional `organs` (`auto`, `flower`, ...), `lang` (e.g. `en`), `nb-results`.
- **The key goes in the URL**, so never log or show full request URLs or raw request errors (they can contain the URL).
- Accepts **JPEG and PNG only** (no HEIC). Up to 5 images, 50 MB per request.
- Reply: `results` sorted by `score` (0 to 1); each has `species.scientificNameWithoutAuthor` and `species.commonNames`; also `bestMatch` and `remainingIdentificationRequests`.
- Quota: 500 per day, resets **00:00 UTC**; going over gives **HTTP 429**. Only one free account per person.
- Photos aren't stored: kept in memory during identification only. A query history (date, time) is kept.
- Suggested acknowledgement: "The image-based plant species identification service used, is based on the Pl@ntNet recognition API, regularly updated and accessible through the site https://my.plantnet.org/". Don't use their logo without checking its terms.
- Fields to use: `results[i].score`, `results[i].species.scientificNameWithoutAuthor` (headline, may contain "×", e.g. "Iris × hollandica"), `results[i].species.commonNames[0]` (the list can be empty).
- **Tested in 4c:** a bad key gives **401** (`"message": "Bad token"`); a photo with no plant gives **404** (`"message": "Species not found"`).

## Still to do in later steps

- Commit after each finished small step, with a clear message.
