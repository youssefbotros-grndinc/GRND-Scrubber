# GRND Scrubber brief

Read this and the top entry of CHANGELOG.md before any work. Current version: **v7.1.2**. Fallbacks: v7.1 (in the fallbacks folder), v6.0.4 and v5.9.9 (in Youssef's files).

## What the tool is

A single offline HTML file (about 8 MB, dictionary and place list built in) that de-identifies client files before they go into AI tools, and puts names back afterwards with a per-client key. Runs in Chrome from the computer. No server, no accounts, nothing leaves the machine. Inputs: Word, Excel, CSV, TSV, text, pasted text, transcripts. Outputs keep their format and formatting. Scanned and text PDFs are not supported yet.

## Rules Youssef has locked

- Over-scrubbing is safe, leaking a name is not.
- One pass. The scrubber decides; nothing blocks the output waiting for spot-by-spot answers. Every decision is listed afterwards so he can check and fix.
- Context decides what a word is, never spelling alone. In transcripts, transcribers and note-takers misspell constantly, so the sentence around a word decides. A key name that is also a word (Matt, Mark, Bill) is the person when the sentence treats it as a person, and a word otherwise ("a mat on the ground" stays a word).
- Public figures, products, brands, software, languages and nationalities stay readable. The key and roster always win.
- One person, one code, forever. Codes are never renumbered; retired lines stay in the key so old outputs still un-scrub.
- Codes carry no meaning. Every new person gets a P- code in the order found. A person's role, location, and whether they're staff, a customer or both live on their card, never in the code. Existing codes never change.
- Where the business operates stays readable: stores, branches, neighbourhoods, how many locations. Private addresses are always coded. Health-mode clients have stores coded by default, switchable per client.
- Name and contact columns stay in the file, coded. Emails, phones and addresses get their own codes, linked to the person on their card.
- Formatting survives. Excel and Word are edited in place.
- No file size limits. Large runs stay fast.
- Health client mode flags conditions and drugs, not job titles or everyday phrases.
- The vault format "grnd-vault-1" is fixed. Every version reads it as is. Passwords and recovery codes are never affected by an update.
- The scrubber is never described as PIPEDA or PHIPA compliant.
- No em dashes. Plain language, sentence case. No small uppercase label above a big title.
- Nothing may require Excel skills or developer tools from him.

## How it works

Three engines decide; nothing else guesses. **Columns:** a column holding people is coded whole. **Dictionary:** in sentences, a capitalized word not in the English and French dictionary is a name, with typos and prefixed words treated as words. **Lists:** roster, customer lists, pasted names and the key. On top of these, a context engine decides key names that are also words, and a built-in list of public figures (public_figures.txt, also embedded in the build) keeps famous names readable.

The key is a text file per client, kept in the encrypted vault (AES-256-GCM, password plus recovery code, 50 versions per client, 30-minute auto-lock). Five planted fake names must be caught on every scrub or downloads stay locked.

## What's next, in order

**v7.2:**

1. Any column that holds people is read as people, including Reports To. A manager who only appears in Reports To gets a code.
2. Names match in any capitalization.
3. Fix: a two-part first name half replaced; a "First name" header coded. Header rows and column labels are never coded.
4. P- codes for every new person. The same person under an old scheme (EMP-001 and a roster code) merges onto one code.
5. A card per person: full name, nicknames and misspellings, staff, customer or both, role, location and reports to with history, plus their email, phone, home address and other identifiers, each linked to the person. A newer roster updates the card, and the review report shows each change.
6. Shared first names: full name wins; a lone first name is resolved by location, role or reports to; otherwise one [UNRESOLVED-n] placeholder, never two codes side by side.
7. Store locations readable for general clients, coded for health-mode clients, switchable per client. Numbered street addresses always coded unless they're a store address on the client's card.
8. A review report with every run: each replacement and why, each unresolved name, each suspected name not in the key, each card change. Kept with the key, never in a client folder.
9. A legend with every run: each P- code with its current role, location and staff or customer, no names, to paste beside scrubbed text when it helps.
10. Fixing the key inside the tool: click any code or word in the output and say what it is (this person, a new person, same as another code, just a word); edit cards on screen; one-tap fixes beside each line of the review report. No editing raw key text.

**Later:** text PDFs, a file profile before scrubbing, a GRND vocabulary file, the photo scrubber.

## How to work with him

- Full plan first, then one approved step at a time. Lead with the answer in bold.
- Show copy in chat before building anything he'll read.
- Never present a build that hasn't been attacked with fake data shaped like his real files. Reproduce the complaint first, fix, prove the fix, run everything.
- Before shipping: the battery, the differential test against the last build, the vault test, every attack script.
- Ship each build as GRND_Scrubber_vX.Y.Z.html with a change-log entry: what changed, why, what was tested.
- Decisions go on screen; counts and technical notes go behind Details.
- Prefer deleting a rule over adding one.

## Client data

Nothing from a client folder ever enters a chat or this repository. No keys, vaults, review reports, transcripts or exports here. Diagnostics carry no names. All test data is invented.

## This repository

Holds the current build, fallbacks, CHANGELOG.md, this brief, test_pack (fixtures and scripts) and public_figures.txt. After each build, Youssef uploads the new files himself (Add file, Upload files); no access token is shared. Each new chat starts from here.

## Starting a new chat

Add this repository with "Add from GitHub", then send:

> We are continuing the GRND Scrubber. Read BRIEF.md and the top entry of CHANGELOG.md in the attached repository completely before replying. Work the way the brief says. Today's task is: [describe the task].

If the build or the test pack can't be read into the build sandbox through the repository, attach GRND_Scrubber_vX.Y.Z.html and the test_pack folder as files in the same message.

## Testing notes

Headless testing uses Python Playwright. When Playwright can't download its browser, install the npm package @sparticuz/chromium, extract its binary (it lands at /tmp/chromium) and set GRND_CHROME to that path; test_pack/scripts/browser.py reads it. Scripts: battery.py (61 checks), diff.py (seven scenarios, old build against new), tvault.py (vault, 15 steps), attack_transcript.py, attack_transcript2.py, ctx_names.py, health_words.py. Each takes the build path as its argument. The build exposes test helpers on window (__fq, __renderFL, __lastCands, __ctxDecisions, __isDictWord, __isPlaceWord, __publicFigureOf, __vaultDebug, __t7).
