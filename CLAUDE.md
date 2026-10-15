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
5. Wikipedia lookup and two-source display, in small steps:
   - 5a. Explore the Wikipedia API by hand: what does it send back for a flower name, a hybrid with "×", and a name with no article?
   - 5b. `wikipedia.py`: one function that gets a short summary and article link (5-second limit, `User-Agent` header)
   - 5c. `/identify` adds the Wikipedia part for the best guess; W1 and W2 still show the Pl@ntNet result
   - 5d. The page shows the summary under a dividing line, with "Reference: Wikipedia" and the link
   - 5e. Tests with a fake Wikipedia
   - 5f. Real flowers on the phone, then commit and tag
5.5. "Did you know?" fact: Wikipedia summaries are often too technical. **Decided 2026-10-14: no Anthropic/AI API** (no extra accounts or paid services). Tested options: common-name articles mostly redirect back to the same species article (rejected); article sections like Etymology give good facts for common flowers (chosen). Show the first two sentences of the best fun section under the summary, in one Wikipedia request.
6. Error handling and photo shrinking, in small steps:
   - 6a. Shrink photos in the browser (longest side about 1600 px, JPEG) before uploading: faster on mobile data, removes GPS, makes HEIC from the Mac work. If the browser can't read the photo, send the original (the server still guards with E10). Check Pl@ntNet's scores on the same photos before and after, so we know shrinking doesn't hurt accuracy.
   - 6b. A time limit on the page (about 30 seconds), showing E3 instead of spinning forever
   - 6c. **Try again** button for E2, E3, E7, E8, re-sending the same photo
   - 6d. Ignore a late reply if I've already pressed Start over
   - 6e. Go through every error case in SPEC.md section 5 and its acceptance criteria; trigger each one for real where possible
   - 6f. A real test on mobile data (outside home Wi-Fi isn't possible until step 7, so simulate weak signal), then tag
7. Put it online on **Render's free tier** (decided 2026-10-15; deploys from a private GitHub repository). Small steps:
   - 7a. Spec: story 9 "Only me" (remembered passcode), E11, Render notes
   - 7b. Production settings: `debug` off unless running locally; gunicorn instead of Flask's development server (ask before installing)
   - 7c. The passcode lock: checked on the server; remembered with a signed cookie; wrong tries slowed down. `APP_PASSCODE` and `SECRET_KEY` in `.env` / Render settings
   - 7d. App icon (`apple-touch-icon.png`, `favicon.ico`): Safari asks for them, currently getting 404s
   - 7e. Private GitHub repository, after scanning the whole git history for secrets
   - 7f. Render service; I type the secrets into Render's settings myself
   - 7g. A real walk on mobile data, then tag `step-7`
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
4d done: `/identify` calls Pl@ntNet and returns `{"confident": bool, "candidates": [{scientific_name, common_name, confidence}]}`. Pl@ntNet errors map to E3–E8. Percentages round **down**. Tests use a fake Pl@ntNet (22 tests). The page shows a temporary one-line "Best guess".
4e done: result screen for states C and D (italic scientific name, common name, confidence, warning and other candidates linking to Wikipedia, Pl@ntNet acknowledgement). 0% shows as "under 1%". Wikipedia summary still to come (step 5).
4f done: tests for every Pl@ntNet error (E3–E8), the missing key, and a test proving the key never reaches logs or replies (34 tests).
4g done: real flowers on the phone. Feedback led to the common name becoming the headline. A marigold close-up scored only 14–16% (correct answer was 2nd), so accuracy work is parked for phase 2.
**Step 4 complete** (git tag `step-4`).
5a done: Wikipedia API explored (facts below).
5b done: `wikipedia.py` with `fetch_summary(name)` returning status `found` / `no_article` / `unavailable`; 11 tests in `tests/test_wikipedia.py` (45 total). Checked against the real Wikipedia.
5c done: `/identify` adds `"wikipedia": {status, summary, url}` for the best guess only; Pl@ntNet result always returned. 49 tests; real end-to-end check passed.
5d done: the page shows the Wikipedia summary with "Reference: Wikipedia" and the article link, or the W1/W2 message. Only `https://` links are accepted.
5e: covered by the fake-Wikipedia tests written in 5b and 5c.
5f done: real flowers on the phone. Layout fixes: photo is a zoomed-in centred square, acknowledgement at the bottom, smaller title. Feedback: Wikipedia summaries are too technical, so step 5.5 adds an AI plain-language rewrite.
**Step 5 complete** (git tag `step-5`).
5.5 done: "Did you know?" box (server in `wikipedia.py`, page in `app.js`). 53 tests. Checked on the phone.
**Step 5.5 complete** (git tag `step-5.5`).
6a built: `shrinkPhoto()` in `app.js` (longest side 1600 px, JPEG 0.85; strips EXIF/GPS; falls back to the original). Measured on the bouquet: Pl@ntNet gives identical results for the same photo twice; the 1600-px copy (518 KB vs 2.8 MB) gave the same top two guesses. The server log shows "Received photo: N KB". Phone check: 531 KB (was about 2,000), right way up, identification normal.
6b done: the page gives up after 35 s (`PAGE_TIMEOUT_MS`, via `AbortSignal.timeout`) and shows E3, including when the reply stalls mid-download. No signal still shows E2.
6c done: every server error carries `can_retry` (via `error_reply()` in `app.py`); the page shows **Try again** only then (E2, E3, E7, E8) and re-sends the same shrunk photo. Page messages are named constants in `app.js`. 56 tests.
6d done: numbered attempts (`startNewAttempt` / `isOutdated` in `app.js`); late replies and late failures are ignored after Start over; Start over during shrinking means no upload. Race tests in the browser, plus a deliberate-bug check.
6e in progress: all 12 spec messages match the code word for word; E1, E4, E6 (wrong key on a second server, key absent from log), E9, E10 triggered for real from the Mac. Phone: E2 + Try again and E4 confirmed, no technical text anywhere. 6e done.
6f done: "slow lane" throttling proxies (scratchpad, not in the project) at 40, 8 and 2 KB/s. Found and fixed a Safari-only bug: its timeout error isn't named "TimeoutError", so the page showed E2; it now checks `deadline.aborted`. Photo sizes after shrinking vary a lot (151–531 KB seen).
**Step 6 complete** (git tag `step-6`).
7a done: host = Render, lock = remembered passcode; spec story 9 and E11 approved.
Next: 7b, production settings (ask before installing gunicorn).

## Environment notes

- Use `python3` (3.15.0, at `/Library/Frameworks/Python.framework/Versions/3.15/`). An old Python 3.9 is also on the Mac; ignore it.
- Two package lists: `requirements.txt` holds what the app needs to run (also used online), and `requirements-dev.txt` adds tools only needed on the Mac, like pytest. After adding a package, put it in the right file with its exact version, and commit. Rebuild everything with `pip install -r requirements-dev.txt`.
- When breaking code on purpose to prove a test works, commit the file first so `git checkout` can restore it (or undo by hand and search for leftovers).
- When testing the page, check what is **actually drawn** (`element.checkVisibility()`, screenshots), not just the `hidden` property: a CSS `display` rule once overrode `hidden` (fixed with a global `[hidden] { display: none !important; }`). Wait for the page to settle rather than using fixed delays.
- Browsers differ: always confirm page behaviour on my real iPhone (Safari), not only in Chrome. Prefer checking our own state (e.g. `deadline.aborted`) over interpreting browser error names.
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

## Wikipedia API facts (tested in 5a on 2026-10-14)

- **Since step 5.5 the app uses one request:** `GET https://en.wikipedia.org/w/api.php` with `action=query, titles=<name>, redirects=1, prop=extracts|info|pageprops, explaintext=1, inprop=url, ppprop=disambiguation, format=json, formatversion=2`. No key. Must send a descriptive `User-Agent`.
- Reply: `query.pages[0]` has `extract` (whole article as plain text, headings like `== Etymology ==`), `fullurl` (the article link), `pageprops.disambiguation` (present on "may refer to" pages), `missing: true` (no article, but still status **200**).
- (Step 5a used the simpler `rest_v1/page/summary/<name>` endpoint: it gives only the opening paragraph and answers 404 for a missing page.)
- A name with several meanings ("Rosa or De Rosa may refer to:") is treated like no article (W1).
- Redirects happen silently: "Helianthus annuus" returns the "Common sunflower" article. So take the link from `content_urls`, never build it from the name.
- Summary length: about 120–750 characters (1–5 sentences) in tests. Fine to show in full.

## Still to do in later steps

- Commit after each finished small step, with a clear message.
