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
4. Pl@ntNet call
5. Wikipedia lookup and two-source display
6. Error handling, plus shrinking photos to about 1 MB in the browser before upload. Includes: the **Try again** button (E2, E3, E7, E8), time limits, and ignoring a late server reply if I've already pressed Start over.
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
Next: 3c, server-side file checks.

## Environment notes

- Use `python3` (3.15.0, at `/Library/Frameworks/Python.framework/Versions/3.15/`). An old Python 3.9 is also on the Mac; ignore it.
- After installing or upgrading a package, update `requirements.txt` with `pip freeze > requirements.txt` and commit it. Rebuild the environment with `pip install -r requirements.txt`.
- Project packages live in `.venv`. Turn it on with `source .venv/bin/activate` (prompt shows `(.venv)`), off with `deactivate`.
- Find the Mac's Wi-Fi address with `ipconfig getifaddr en0` (it was 192.168.86.23 on 2026-10-14; it can change). The phone opens `http://<that address>:5001`.
- **Testing on the phone (Safari):** after code changes, close the tab and open a fresh one. A plain refresh can keep the old page and make a working change look broken.
- The app runs on port **5001**, not Flask's usual 5000, because macOS's AirPlay Receiver uses 5000.
- Homebrew is installed but too old to run on this macOS version, so don't rely on it.

## Still to do in later steps

- Create a Pl@ntNet account and API key before step 4. The key goes in `.env`. Read their terms for attribution wording and photo handling.
- Step 4: check whether Pl@ntNet accepts HEIC (only matters for HEIC files uploaded from the Mac).
- Create `.env` at step 4 (`.gitignore` already blocks it).
- Commit after each finished small step, with a clear message.
