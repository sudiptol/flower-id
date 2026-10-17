# Flower ID: spec

## 1. Problem statement

I often see flowers I can't name, either on walks or later in photos I've taken. Today, finding out what a flower is means searching around and guessing. I want to point my phone at a flower, or pick a photo I already took, and within a few seconds see its name, how sure the app is, and something interesting about it.

**Who it's for:** just me, in my phone's web browser while out walking, and on my phone or Mac at home with photos I've already taken.

**Success looks like:** I get the flower's name, followed by something interesting to read, quickly and without fuss. When the app isn't sure, it says so honestly instead of pretending.

**What this means for the design:**
- **Phone first:** large buttons, readable outdoors, one screen.
- **Two ways in:** take a new photo with the camera, or choose an existing one.
- **Name first, then the interesting part:** the scientific name is the headline, and the Wikipedia summary comes underneath.
- **Weak signal on walks:** keep pages light and show a clear message when the connection fails.
- **Single user:** no accounts or login. Once it's online (step 7), we still need to stop strangers from using up my 500 identifications per day.

## 2. User stories

Format: *I can [do something] so that [reason]*. Ordered by importance.

1. **Take a photo:** I can take a photo of a flower with my phone camera, right in the app, so that I can identify it on the spot during a walk.
2. **Choose a saved photo:** I can choose a photo I've already taken, so that I can identify flowers later at home.
3. **See the name:** I can see the flower's common name as the headline, with its scientific name in italics underneath, so that I learn what it is at a glance. When there's no common name, the scientific name is the headline. *(Changed in step 4g: the common name was easy to overlook in small grey text.)*
4. **See how sure it is:** I can see the confidence score, labelled "Identified by Pl@ntNet (confidence X%)", straight under the photo, so that I know how much to trust the answer, and where it came from, before I read the name. *(Moved above the name on 2026-10-17.)*
5. **Read something interesting:** I can read a short Wikipedia summary under the name, plus a "Did you know?" fact when the article has one, with a link to the full article and a credit line, so that I learn about the flower and can read more if I want.
6. **Be warned when it's unsure:** when confidence is below 50%, the name is labelled "Best guess:" and the top 3 candidates appear, so that I'm not misled and can compare the options myself. *(Changed on 2026-10-17: the red "Not sure about this one" box was removed; the confidence line now sits where it was.)*
7. **Understand failures:** when something goes wrong (no signal, no flower found, daily limit reached), I can see a plain-English message saying what happened and what to do, so that I'm never left staring at a blank or broken page.
8. **Go again:** I can start a new identification with one tap, so that I can identify several flowers on one walk without reloading.
9. **Only me** *(added in step 7)*: once the app is online, I enter a passcode once on each device, and the app remembers it, so that strangers who find the web address can't use up my 500 identifications per day.

### Decisions

- **Common name:** yes, as the headline when Pl@ntNet provides one, with the scientific name underneath. *(Swapped in step 4g.)*
- **Photos per identification:** one. Sending several photos of the same plant is a later idea (see Out of scope).

## 3. Screen sketch

The app is **one page** that changes between five states. Sketches are phone width.

### A. Start

```
+------------------------------+
|        Flower ID             |
|                              |
|  +------------------------+  |
|  |   [ Take a photo ]     |  |   <- opens the camera
|  +------------------------+  |
|  +------------------------+  |
|  |   [ Choose a photo ]   |  |   <- opens saved photos
|  +------------------------+  |
|                              |
+------------------------------+
```

### B. Working

```
+------------------------------+
|        Flower ID             |
|  +------------------------+  |
|  |   (photo preview)      |  |
|  +------------------------+  |
|      Identifying...          |
+------------------------------+
```

### C. Result: confident (50% or more)

```
+------------------------------+
|  +------------------------+  |
|  |   (photo preview)      |  |
|  +------------------------+  |
|  Identified by Pl@ntNet      |
|  (confidence 92%)            |
|                              |
|  Common daisy                |   <- headline
|  Bellis perennis             |   <- smaller, italics
|  ----------------------------|
|  The daisy is a common       |
|  European species... (short  |
|  Wikipedia summary)          |
|                              |
|  Did you know?               |   <- only when the article has a fun section
|  "Daisy" comes from "day's   |
|  eye": it closes at night.   |
|                              |
|  Reference: Wikipedia        |
|  [Read the full article]     |
|  ----------------------------|
|  [ Identify another flower ] |
+------------------------------+
```

### D. Result: unsure (below 50%)

```
+------------------------------+
|  +------------------------+  |
|  |   (photo preview)      |  |
|  +------------------------+  |
|  Identified by Pl@ntNet      |   <- where the warning box was
|  (confidence 38%)            |
|                              |
|  Best guess:                 |
|  Dog rose                    |
|  Rosa canina                 |
|                              |
|  Other candidates:           |
|  Sweet briar (Rosa           |
|    rubiginosa): 21%          |
|  Field rose (Rosa            |
|    arvensis): 12%            |
|  ----------------------------|
|  (Wikipedia summary of the   |
|   best guess, with credit)   |
|  ----------------------------|
|  [ Identify another flower ] |
+------------------------------+
```

### E. Problem

```
+------------------------------+
|        Flower ID             |
|                              |
|  ! Couldn't connect.         |   <- what happened
|    Check your signal and     |   <- what to do
|    try again.                |
|                              |
|  [ Try again ]               |
|  [ Start over ]              |
+------------------------------+
```

### Layout rules

- One column, big tap targets, readable in sunlight (dark text on light background).
- The photo shows as a centred square (about 60% of the screen wide), zoomed in on the middle, because my photos are close-ups. Pl@ntNet's acknowledgement sits at the bottom. Both keep the names and summary in view. *(Added in step 5f: a tall photo pushed the summary off screen.)*
- The two sources are always visually separate, divided by a line.
- The Pl@ntNet attribution appears on every result.
- Under every result, in small print, Pl@ntNet's requested acknowledgement, with the link: "The image-based plant species identification service used, is based on the Pl@ntNet recognition API, regularly updated and accessible through the site https://my.plantnet.org/". Text only, no Pl@ntNet logo.

### Decision

- **Candidates on the unsure screen:** each candidate's name links to its Wikipedia article in a new tab. Swapping the summary in place is a later idea.

## 4. Acceptance criteria

Pass/fail checks for each user story. A story is **done** only when every box can be ticked. The numbers match section 2.

**1. Take a photo**
- [x] On my phone, tapping **Take a photo** opens the camera directly.
- [x] After I take the photo, the app moves to the Working state (B) without any extra taps.
- [x] On my Mac (no camera prompt), **Take a photo** simply opens the file picker, like **Choose a photo**. *(Checked in Safari on 2026-10-17: it opens the Finder file window.)*

**2. Choose a saved photo**
- [x] On my phone, tapping **Choose a photo** opens my photo library.
- [x] On my Mac, the same button opens a file picker.
- [x] Photos straight from my phone work, including iPhone's HEIC format. *(Tested in step 3b: iPhone Safari converts photos to JPEG, about 2 MB, before sending. A HEIC file uploaded from the Mac still arrives as HEIC; step 4 checks whether Pl@ntNet accepts it.)*
- [x] If I pick something that isn't an image (like a PDF), I see a clear message and nothing is sent to Pl@ntNet.
- [x] *(Added in step 3c)* The server checks every upload itself: it refuses non-images (by their first bytes, not their label) and anything over 10 MB.

**3. See the name**
- [x] The top result's common name is the largest text on the result screen, with the scientific name in italics underneath.
- [x] If Pl@ntNet gives no common name, the scientific name becomes the headline, and there's no blank gap or "None".

**4. See how sure it is**
- [x] Confidence shows as a whole-number percentage, for example "92%", not "0.9213". It's always rounded **down**, so 49.97% shows as "49%" and is treated as unsure ("Best guess:" and the other candidates). *(Decided in step 4d.)*
- [x] The exact text "Identified by Pl@ntNet (confidence X%)" appears on every result.

**5. Read something interesting**
- [x] A Wikipedia summary of a few sentences appears under a dividing line, separate from the Pl@ntNet part.
- [x] "Reference: Wikipedia" and a link to the full article appear with it, and the link opens the right article.
- [x] If Wikipedia has no article, the name still shows, with "No Wikipedia article found" instead of a summary. The app doesn't fail.
- [x] *(Step 5.5)* A "Did you know?" fact appears under the summary: the first two sentences of the article's best "fun" section, chosen in this order: Etymology (name origin), then In culture / Folklore / Symbolism, then Uses, then Cultivation / History.
- [x] *(Step 5.5)* When the article has none of those sections, the "Did you know?" box simply doesn't appear (no error message).
- [x] *(Step 5.5)* Getting the fact needs no extra waiting: the summary and the sections come from one Wikipedia request.

**6. Be warned when it's unsure**
- [x] At 49% the "Best guess:" label and the top 3 candidates show. At 50% they don't (the boundary is tested exactly). *(Until 2026-10-17 a red warning box showed too.)*
- [x] If Pl@ntNet returns fewer than 3 candidates, the app shows the ones it has.
- [x] Each candidate's name links to its Wikipedia article in a new tab.

**7. Understand failures**
- [x] Each problem (no connection, no flower found, daily limit reached, Pl@ntNet or Wikipedia down) shows its own plain-English message saying what happened and what to do. *(Step 6e: all 12 messages checked word for word against the code; E1, E2, E4, E6, E9, E10 triggered for real.)*
- [x] No error ever shows technical text such as a code dump or "500 Internal Server Error".
- [x] *(Added in step 6c)* **Try again** appears only for E2, E3, E7 and E8, and re-sends the same photo.
- [x] My API key never appears on the page, in the page source, or in any error message. *(Automated test since step 4f.)*

**8. Go again**
- [x] **Identify another flower** returns to the Start state (A) in one tap, without reloading the page.

**9. Only me** *(step 7)*
- [x] Without the passcode, the app shows only a passcode box. The server itself refuses identifications without it (not just the page), so nobody can get round it by calling the server directly. *(Checked online 2026-10-17: `/identify` answers 401 without the cookie.)*
- [x] After entering the right passcode once, that device goes straight to the app for about a year. *(Phone: Safari and the home-screen icon both go straight in.)*
- [x] A wrong passcode shows E11, and each wrong try is slowed down by a second or so, to make guessing impractical. *(Online: 401 after about 1.8 s, no cookie given.)*
- [x] The passcode lives in `.env` on the Mac and in a separate `.env` on PythonAnywhere, never in the code, git or chat (like the Pl@ntNet key).

**Overall**
- [x] On home Wi-Fi, a result appears within 10 seconds of choosing a photo. *(Seen throughout testing; on a simulated weak signal of 40 KB/s, about 15 seconds.)*
- [x] *(Added in step 6)* On a very weak signal the page gives up after 35 seconds with "taking too long" and Try again, in both Chrome and Safari.
- [x] Everything fits the phone screen width with no sideways scrolling.
- [x] *(Added in step 6)* Photos are shrunk in the browser to about 1 MB and converted to JPEG before uploading, so results come quickly on weak mobile signal and HEIC files from the Mac work. *(Step 6a: longest side 1600 px; a real iPhone photo arrived at 531 KB instead of about 2,000 KB.)*
- [x] *(Added in step 6)* The hidden location data (GPS) that phones store inside photos is removed before uploading. Shrinking the photo in the browser does this automatically; we check it. *(Step 6a: tested with a photo carrying fake GPS data.)*

**Before step 4**
- [x] Pl@ntNet's terms are read, and the attribution wording matches what they require. *(Done in step 4a; see the layout rules in section 3.)*

## 5. Error cases

Every way the app can fail, and exactly what I see. The exact error codes Pl@ntNet sends are confirmed in step 4.

### Full failures (show the Problem state, E)

| # | What went wrong | Message I see | Buttons |
|---|---|---|---|
| E1 | The file isn't an image (like a PDF) | "That file isn't a photo. Please choose a JPG or PNG image." | Start over |
| E2 | My phone can't reach the app (no signal) | "Couldn't connect. Check your signal and try again." | Try again, Start over |
| E3 | Pl@ntNet takes too long (no reply within 20 seconds) | "Identification is taking too long. Please try again." | Try again, Start over |
| E4 | Pl@ntNet finds no plant in the photo | "No flower recognised. Try a closer, sharper photo with the flower filling the frame." | Start over |
| E5 | Daily limit reached (500 used) | "Daily limit reached. Identification will work again tomorrow." | Start over |
| E6 | Pl@ntNet rejects the API key (missing, wrong or expired) | "Setup problem: the Pl@ntNet key isn't working. Check the .env file." | Start over |
| E7 | Pl@ntNet is down | "Pl@ntNet isn't responding right now. Try again in a few minutes." | Try again, Start over |
| E8 | Anything unexpected | "Something went wrong. Please try again." | Try again, Start over |
| E9 | The photo is over 10 MB *(added in step 3c)* | "That photo is too large (over 10 MB). Please choose a smaller one." | Start over |
| E10 | A HEIC file, e.g. uploaded from the Mac; Pl@ntNet only accepts JPEG and PNG *(added in step 4a; since step 6a the page converts photos to JPEG, so this only appears in a browser that can't read HEIC, such as Chrome on the Mac. The server keeps the check as a safety net)* | "HEIC photos can't be identified yet. Please use a JPG or PNG." | Start over |
| E11 | Wrong passcode *(added in step 7)* | "That passcode isn't right. Please try again." | (stays on the passcode box) |

### Partial failures (still show the result)

If Pl@ntNet worked but Wikipedia didn't, the identification is still useful, so I still see it.

| # | What went wrong | What I see |
|---|---|---|
| W1 | Wikipedia has no article for this name | Result as usual, with "No Wikipedia article found" in place of the summary |
| W2 | Wikipedia is slow (no reply within 5 seconds) or down | Result as usual, with "Couldn't load the Wikipedia summary right now" in place of the summary |

### Rules for all errors

- **Two audiences:** I see a short, friendly message. The full technical details are written to the server's log (the Terminal window running the app) so I can investigate. Technical details never go on the page.
- **Never show secrets:** error messages and logs never include the API key.
- **Always a way out:** every error screen has at least a **Start over** button.
- **Try again** only appears when trying again might actually help (E2, E3, E7, E8). It re-sends the same photo, so I don't have to retake it.
- **Time limits:** the app always gives up waiting after a set time (20 seconds for Pl@ntNet, 5 for Wikipedia) instead of hanging forever.

## 6. Out of scope

What this version deliberately does **not** do. If a new idea comes up while building, it goes on the "Later ideas" list instead of into the current step.

### Later ideas (phase 2, after version 1.0)

- **Better accuracy (phase 2).** Real-world tests in step 4g gave low confidence. A cut marigold head on a patterned cushion came back as *Anacyclus valentinus* ("Valentine's Sunflower") at 14–25%, with African marigold 2nd. Pl@ntNet's own website gave the **same wrong answer** (42%) for the same photo, so the cause is the photo and the model, not our app. Ideas to try, measuring scores before and after each change on the same test photos, and checking that the **right** answer gains, not just any answer:
  - Photograph the flower on the plant, with leaves in the frame (marigold leaves are a key clue).
  - Tell Pl@ntNet the photo shows a flower (`organs=flower` instead of `auto`).
  - **Several photos per identification** (flower plus leaf, and so on). Pl@ntNet allows up to 5.
  - Let me crop to the flower before sending.
  - Photo tips on the start screen ("one flower, filling the frame, in focus").
  - Use a regional plant list instead of the whole world, for where I live.
  - Show **genus-level** confidence too (Pl@ntNet's `detailed=true` option), e.g. "Marigold (Tagetes): 85%", when it's unsure which exact species. *(Prompted by a marigold close-up that scored only 16%.)*
- **Tap a candidate** on the unsure screen to swap in its Wikipedia summary.
- **History** of flowers I've identified, with photos and dates.
- **Location:** where I saw each flower, on a map.
- **Share** a result with someone.
- **Other languages** for names and summaries.
- **A native iPhone app** built in Xcode.
- *(Added in step 8)* **Let a friend use it.** Today one shared passcode can't be taken back from one person without logging everyone out (changing `SECRET_KEY`). Friends would need their own passcodes, and a check of Pl@ntNet's terms for sharing one free key. Story 9 ("Only me") would change.
- *(Added in step 8)* **Stronger protection against passcode guessing:** for example, pause the lock after several wrong tries. Each wrong guess currently waits 1 second, which also briefly stalls the app for me.
- *(Added in step 8)* **Automated tests for the page itself** (`app.js`). Today its behaviour is checked by hand in the browser and on the phone; browser tests need a new tool (ask before installing).
- *(Added in step 8)* **Easier updates to the live app.** Today: `git pull` on PythonAnywhere, then Reload, by hand.

### Not in this version

- **User accounts or sign-up.** It's just me. (A simple passcode lock to protect my daily limit *is* in scope: story 9.)
- **Working offline.** Identification needs Pl@ntNet, so there's no signal, no result. The app only has to fail clearly (error E2).
- **Saving my photos.** My app passes each photo to Pl@ntNet and keeps no copy. Pl@ntNet's terms say they don't store photos either: they're kept in memory only during identification.
- **Polished visual design**, such as custom fonts, animations or dark mode. Clean and readable is enough.
- **English only:** English Wikipedia and English common names.

## 7. How I open the app

This is a **web app**, not a native iPhone app: no Xcode, no App Store. I open it in my phone's web browser.

- **While building (steps 2–6):** the app runs on my Mac. My phone opens it by typing the Mac's local address (like `http://192.168.1.20:5001`) into the browser. This only works at home, with both devices on the same Wi-Fi.
- **Once online (step 7):** the app lives on **PythonAnywhere's free plan** at `https://sudiptol.pythonanywhere.com`, so it works anywhere, including on walks. It's always on (no waiting for it to wake). *(Changed from Render on 2026-10-17: Render's free tier asked for a card; PythonAnywhere's doesn't.)* Its catches:
  - The free plan only lets the app contact sites on PythonAnywhere's allowlist. Pl@ntNet (`my-api.plantnet.org`) and Wikipedia are on it (checked 2026-10-17).
  - I must click **"Run until 3 months from today"** on the Web tab every 3 months, or the app stops. PythonAnywhere emails a reminder.
  - Updating the live app is by hand: `git pull` in a PythonAnywhere console, then **Reload** on the Web tab.
- **App-like feel:** in the phone browser, "Add to Home Screen" gives it an icon like a real app.
