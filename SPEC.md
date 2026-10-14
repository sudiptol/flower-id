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
3. **See the name:** I can see the flower's scientific name as the headline, with its common name (when there is one) in smaller text underneath, so that I learn what it is at a glance.
4. **See how sure it is:** I can see the confidence score, labelled "Identified by Pl@ntNet (confidence X%)", so that I know how much to trust the answer and where it came from.
5. **Read something interesting:** I can read a short Wikipedia summary under the name, with a link to the full article and a credit line, so that I learn about the flower and can read more if I want.
6. **Be warned when it's unsure:** when confidence is below 50%, I can see a clear warning and the top 3 candidates, so that I'm not misled and can compare the options myself.
7. **Understand failures:** when something goes wrong (no signal, no flower found, daily limit reached), I can see a plain-English message saying what happened and what to do, so that I'm never left staring at a blank or broken page.
8. **Go again:** I can start a new identification with one tap, so that I can identify several flowers on one walk without reloading.

### Decisions

- **Common name:** yes. Show it in smaller text under the scientific name when Pl@ntNet provides one.
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
|                              |
|  Bellis perennis             |   <- headline
|  Common daisy                |   <- smaller
|                              |
|  Identified by Pl@ntNet      |
|  (confidence 92%)            |
|  ----------------------------|
|  The daisy is a common       |
|  European species... (short  |
|  Wikipedia summary)          |
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
|  ! Not sure about this one.  |   <- visible warning box
|  ! Compare the options below.|
|                              |
|  Best guess:                 |
|  Rosa canina   Dog rose  38% |
|                              |
|  Other candidates:           |
|  Rosa rubiginosa         21% |
|  Rosa arvensis           12% |
|                              |
|  Identified by Pl@ntNet      |
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
- The two sources are always visually separate, divided by a line.
- The Pl@ntNet attribution appears on every result.

### Decision

- **Candidates on the unsure screen:** each candidate's name links to its Wikipedia article in a new tab. Swapping the summary in place is a later idea.

## How I open the app

This is a **web app**, not a native iPhone app: no Xcode, no App Store. I open it in my phone's web browser.

- **While building (steps 2–6):** the app runs on my Mac. My phone opens it by typing the Mac's local address (like `http://192.168.1.20:5000`) into the browser. This only works at home, with both devices on the same Wi-Fi.
- **Once online (step 7):** the app lives on a hosting service with a normal `https://` web address, so it works anywhere, including on walks.
- **App-like feel:** in the phone browser, "Add to Home Screen" gives it an icon like a real app.
