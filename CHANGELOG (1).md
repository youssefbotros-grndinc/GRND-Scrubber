# GRND Scrubber change log

## v7.1.2 — 21 October 2026

### What this changes
**Health client mode no longer flags everyday phrases with "take".** The rule for drugs after take, takes, taking or prescribed matched any word of four or more letters, because the search ignored capitals: "take time", "take care", "take notes", "take ownership" were all listed as health details. A word after those verbs now counts as a drug only when it has a dose ("takes 20 mg Zorvexa"), a drug ending (sertraline, metformin, lisinopril), or a real capital on a word that is not an ordinary word, a brand, a first name, a weekday or a place ("takes Sertraline" yes, "takes Uber", "Taking Friday", "Take Kanata" no). Conditions and the other health rules are unchanged.

### Tested
New script health_words.py: 5 of 5 conditions and drugs still flagged, 0 of 7 everyday phrases flagged (v7.1.1 flagged all 7). Battery 61 of 61. Seven differential scenarios byte-identical to v7.1.1. Vault test, all 15 steps. Attack transcripts 1 and 2 and the 14 word-name sentence sets unchanged and clean. Confirmed the v7.1 "Names that are also words, needs a decision" panel no longer appears: on the same five-mention transcript v7.1 shows the panel and leaves Matt readable, v7.1.2 replaces all five and lists them under Details.

## v7.1.1 — 9 October 2026

### What this changes
**Names that are also words are decided by the sentence, in one pass.** A key name that is also a dictionary word (Matt, Mark, Bill, Grace, Hope, Will, Chase, Art, and any other) used to wait under Details for a spot-by-spot decision on every scrub, and stayed readable in the output until you answered. Now the scrubber decides each spot itself. The person: a speaker label, a possessive (Matt's van), a greeting (Thanks Matt), a person word before it (asked Matt, talk to Bill, with Mark and Grace), a person verb after it (Mark said, Bill is on vacation, Will called), a known surname or code beside it, or a mid-sentence capital in written text. The word: a determiner before it (the bill, a mat, a new Matt), a subject or helper before it (I hope, we bill, it will be), a verb's object after it (mark it done, bill them, Bill To, Mark as paid), a fixed phrase (grace period), or a phrase the same written files use in lowercase elsewhere (the art class makes Art supplies a word). In a transcript a lowercase mention with no sign of a person stays a word. Details shows "Names that are also words: 15 replaced as the person, 12 kept as words" with the reason beside each spot and a Flip button for any spot decided wrong. Nothing blocks the downloads.

**Public figures stay readable.** A built-in list of 1,382 people: hockey, basketball, football, baseball, soccer, tennis, golf, fighters and racers; musicians; film, TV and comedy; Canadian, American and world politicians and royalty; business and tech figures; business authors (Hormozi, Martell, Wickman, Miller, Clear, Sinek, Covey, Lencioni and more); novelists; internet personalities; home renovation hosts. A full name matches with one transcription slip per word (Tom Braidy stays Tom Brady), single names only when listed alone (Drake, Beyonce), and the bare surname of a public figure named in full in the same file (Matthews after Auston Matthews). The key and the roster always win: a staff member who shares a famous name is still coded. The list lives in public_figures.txt beside the test pack so it can be read and grown.

**Products, languages and nationalities stay readable.** Laptop, phone and tablet models (ThinkPad, MacBook, Latitude, Surface, Galaxy, Pixel), vehicle models (F-150, Sprinter, Corolla, Silverado), HVAC, plumbing and tool brands, SMB software (Buildertrend, Procore, Lightspeed, GoHighLevel, ClickUp, Loom, Fireflies, Fathom), GRND vocabulary (StoryBrand, EOS, Booked55, Wispr Flow, e-transfer, reno), language names, and demonyms (Filipino, Lebanese, Quebecois).

**Transcript typos are words.** A lowercase word that is one slip from a dictionary word (recieve, untill, accomodate, becuase, thier) and a word built from a prefix or suffix and a dictionary word (unbillable, non-billable, rebooked, pre-approve) no longer land in the queue, unless the sentence treats it as a person ("told okafur", "with okafur" are still flagged).

**Machine labels are not people.** Unknown Speaker, Speaker 2, Interviewer, Participant, Otter, and any speaker label made only of plain words with no first name in it.

**Two bugs the rebuilt battery found.** The automatic key cleanup retired a person whose first and last names are both dictionary words when the first name is unusual (Grebo Manning), and the person then leaked: a key line of two or three capitalized words with no label, month or accounting word in it is now always a name. A label cell in a customer column ("Legend: yellow = follow up") had its first word coded as a customer: a cell with a colon or equals sign is never a person and its words are never split off.

**One leak removed.** The plural rule (a first name plus s is the same person) turned "Matthews" into Matthew's code and would have turned every "Williams" into any William in the key. The rule is deleted; possessives were already handled by the word boundary.

**Half of a two-word brand is not a name.** "Hydro One emailed", "Canada Post dropped off": the second word no longer lands in the queue through the person-verb rule.

### Known limits
A surname that is itself a dictionary word (Voss, Price, Hunter), typed lowercase in a transcript with no sign of a person around it, is missed unless the person is in the key. True since v7.0.

### Tested
Attack transcript 1 (eight-person key, Matt the person and a Matt on the ground, mark/bill/grace/hope/will as words and as people, 12 celebrities including a misspelled one, seven typos): 15 of 15 key-person mentions replaced, 12 of 12 ordinary uses readable, floor mat kept, 0 celebrities, 0 typos, 0 brands and 0 key names in the queue, 0 decisions demanded, the new dispatcher caught, the two misspelled key people flagged with their match. Attack transcript 2 (business authors, laptop models, languages, prefixed words, Unknown Speaker and Speaker 2 labels, Williams and Matthews as other people's surnames): 0 wrong queue entries, Williams and Matthews not coded as Will or Matt. Fourteen sentence sets for names that are also words across written text, transcripts and CSV cells: 14 of 14. The rebuilt regression battery (61 checks from the change log: numbered companies, report words, buried companies, transcript names, places, wages layout, HR sheet, First and Last columns, name orders, SharePoint export, interview log, keep list across sessions, key cleanup, retired codes, shared names, health mode, safety check, greetings and brands, survey CSV, decided section, export spellings, label cells, Word round trip with author stripping, formatted Excel round trip with un-scrub, AutoTask 4,900 rows in 6 seconds, 5,000 customers in two sessions): 61 of 61. Seven scrubbing scenarios byte-identical on v7.1 and v7.1.1. Vault test, all 15 steps. Chrome only (file handles and the Flip matcher use Chrome features).

### Test pack
New in test_pack: fixtures 8 and 9 (the two attack transcripts), scripts/battery.py (the rebuilt battery), scripts/attack_transcript.py, scripts/attack_transcript2.py, scripts/ctx_names.py, scripts/browser.py (shared launcher; set GRND_CHROME to a Chromium binary when Playwright has none installed). diff.py and tvault.py now take the build path as an argument.

## v7.1 — 30 September 2026

### The client vault
One encrypted file holds every client's key. Open it, pick the client, let your password manager fill the password, click Unlock. The key loads exactly as if you had opened the key file, and every change saves back to the vault by itself.

- **Strong by design.** Each client's key is sealed with a random 256-bit content key (AES-256-GCM). That content key is sealed twice: once with the client's password and once with a recovery code, each stretched through PBKDF2-SHA256 at 600,000 rounds. Passwords need 12 characters or more. Client names are readable in the file; nothing else is.
- **Recovery code.** Shown once when a client is created. It resets the password without knowing the old one. If both the password and the code are lost, that client's key cannot be opened by anyone, by design.
- **Version history per client.** The last 50 versions of each client's key are kept inside the vault, encrypted, with date and time, and a "Restore this version" button. A password change never rewrites history.
- **Lock.** A Lock button, and an automatic lock after 30 minutes without activity, which clears the key and files from the page.
- **Change password, remove client, add the current key as a new client.**
- **Old key files still work.** Load key file, Save key file and the key history beside the key are unchanged. Moving a client into the vault is: load the key, click "Add the current key as a new client", set a password, save the recovery code.
- **The format is fixed.** The vault file says "grnd-vault-1" inside, and every future version of the tool reads that format as is. A newer tool never rewrites a vault it does not understand.
- Chrome and Edge write the vault file back directly. Other browsers download an updated copy on each change.

### Tested
Two clients with different passwords; wrong password refused with nothing loaded; right password restores the key, locations and client name exactly; the password field clears after unlock; a scrub that adds codes saves a new version automatically and unlocks downloads; restore brings an earlier version back; change password (old refused, new works); reset by recovery code, typed in lowercase; wrong recovery code changes nothing; one client's password does not open another; a tampered vault is refused; a plain key file still loads; a formatted Excel scrub under the vault keeps its colours and saves a version. Seven scrubbing scenarios produce byte-identical output on v7.0.12 and v7.1, so the scrubbing engine is untouched.

## v7.0.12 — 29 September 2026

### What this changes
**Excel files keep their formatting.** The Excel download is now the original workbook with only its text changed: cell colours, legends, bold, merged cells, number formats, column widths, conditional formatting, pivot tables, charts and images all stay exactly as they were. Names are replaced in cells, rich-text cells, sheet names, comments and comment authors, chart and text-box text, pivot table caches and field names, headers and footers, and the file's author and last-modified-by properties. Un-scrub works the same way, so a restored workbook keeps its formatting too. The old rebuild is kept only as a fallback if a workbook cannot be edited in place.

Also: a label or an ordinary word sitting in a people column ("Legend:", "Total", "Subtotal") is no longer coded as a person.

### Tested
A cancellation log with a colour legend, bold headers, a merged title, currency formatting, a comment with an author, a second sheet named after a customer, a rich-text cell, and author properties: every name gone from every part of the file, every colour and format intact, legend and reasons readable, and the un-scrubbed copy back to the original names with formatting kept. Full suite passing.

## v7.0.11 — 29 September 2026

### What this fixes
**Health client mode flags the condition, not the word "diagnosed".** "Diagnosed", "diagnosis", "medication" and "prescribed" on their own are not health information. What follows them is. The health check now captures the thing named after "diagnosed with", "suffers from", "treated for", "prescribed", "takes" or "on" (for example "generalized anxiety disorder", "Sertraline", "migraines", "Amitriptyline") and lists that for review, along with the fixed list of conditions and drugs. A sentence like "the diagnosis was confirmed" or "staff prescribed the standard onboarding" no longer trips it.

### Tested
A clinic note with two real diagnoses and two medications, plus the words diagnosed, diagnosis and medication used loosely: only the conditions and drugs were listed. Full suite and the day's attack tests passing.

## v7.0.10 — 29 September 2026

### What this fixes
**Health client mode flagged job titles and service names.** Therapist, counsellor, therapy, counselling, rehab and "mental health" as a field describe the business, not anyone's condition, so they no longer trigger the health warning or the health review list. Conditions, diagnoses, medications, prescriptions and the rest still do. Surgery as a word was also removed from the list, since in a clinic's documents it is the service, not a person's history.

### Tested
A clinic note mixing job titles and service words with one real health detail: v7.0.9 flagged eight words, v7.0.10 flags only "diagnosed", "asthma" and "medication". Full suite passing.

## v7.0.9 — 29 September 2026

### What this adds
**Places around Ottawa, read in context.** A built-in list of about 2,500 places: every town and city within 500 km of Ottawa (Ontario, Quebec and the nearby US states), Ottawa and Gatineau neighbourhoods, and the major roads. Context decides what happens to a place word:
- Kept readable when it is used as a place: after in, at, near, from, to, downtown; before Street, Road, Avenue, chemin, rue and the like; before a place noun (branch, office, store, area, deliveries, route, customers...); in an address line or beside a postal code; alone in a spreadsheet cell; or paired with another place ("Kingston and Cornwall").
- Treated as a person when it is used as one: "Russell called about the invoice", "Nelson approved it", "We met Perth in the lobby" are all flagged for review, because those words are surnames too.
- Any capitalized word followed by a road word is a street, whatever the word is.
- Numbered addresses still get the ADDR code; the city after them stays readable.

### Also fixed
1. Two different people with the same surname across files ("Grace Voss" in a list, "Priscilla Voss" in a report) no longer collapse into one. The surname is given back to the new person so the review sees the full name.
2. Retired key lines were being re-counted as junk on every scrub, which kept the key health count from ever reaching zero.
3. A column whose header is already a person's code (a wide layout after scrubbing) is never read as a list of people.

### Tested
A report and a customer export mixing Kanata, Stittsville, Barrhaven, Hunt Club, Elgin Street, Merivale Road, Sandy Hill, Orleans, Gatineau, Bank Street, Carleton Place, Kingston, Cornwall, Montreal and a full address, alongside Russell, Nelson and Perth used as people: every place readable, every person flagged, the address number coded and the city kept. Full battery passing, 1.0 seconds on the speed test.

## v7.0.8 — 29 September 2026

### What this fixes
**Shared-name picks looked like they did nothing.** Picking which person a shared first name meant ("Dana" is Dana Whitlock or Dana Okafor) only changed the text on screen. Any re-scrub, including the one that runs when you code ticked names, brought the [BA-01 or BA-02] markers back, and Word and Excel downloads were built from the original file, so they never had the picks at all. Picks now live for the session, are applied inside the scrubber on every pass, and carry into every download. The panel shows what you picked, and the button says so.

### Tested
A Word file with a shared first name and an unknown name: pick applied, names coded afterwards, pick still in place on screen and inside the downloaded Word file. Full battery passing.

## v7.0.7 — 29 September 2026

### What this changes
1. **Key cleanup is automatic.** The same name under two codes is merged onto one code (the roster code wins), and entries that are months, phrases, or ordinary words are retired, every scrub, without a panel to click. The summary card says what was done, and the version of the key from before the cleanup is kept in the key history beside the key, so one click restores it.
2. **"Hourly", "accrued", "statutory" and similar are treated as words.** A single-word entry or alias is retired when it is a frequent English word, a word actually used in lowercase in the files being scrubbed, or a word shape surnames rarely take (hourly, accrued, statutory, vacation, deductions). Rare dictionary words that are someone's surname (Grebo, Manning, Voss) are kept.
3. A word-like first name that is genuinely part of a person's name (Able Waters, May Lin) is still checked spot by spot rather than skipped.

### Tested
A key polluted with duplicate codes, month entries and word aliases scrubbed against a wages note: duplicates merged, "hourly", "Accrued vacation" and "Statutory holiday" readable, Grebo and Manning still coded, the pre-cleanup key in history. Full battery passing.

## v7.0.6 — 29 September 2026

### What this fixes (from the SharePoint export)
1. **Month abbreviations and basic words at the "could damage normal words" gate.** Jan, Mar, Fri, "the" and similar are skipped without asking. A month word that is genuinely part of a person's name (May Lin, Jan Kowalski) still gets the spot-by-spot check. The cleanup panel now proposes retiring key entries that are just a month, a weekday, or a single ordinary word.
2. **SharePoint and CRM columns.** Modified By, Created By, Author, Editor, Assigned, Reviewer, Approver, Requester, Sender, Recipient, From, To and similar headers are read as people. File-name columns (anything ending .xlsx, .docx, .pdf and so on, or containing a path) and date or month columns are never read as people.
3. **Names with stars or markers.** "Bartholomew Okafor*", "*Priscilla Voss*", "Kojo Mwangi *" and names wrapped in † ‡ • # are found and replaced, in cells and in sentences, and the marker stays where it was.

### Tested
A 300-row SharePoint-style export with file names, month columns, starred names in cells and notes, and a key polluted with Jan, Total and Mar entries: no month or word asked at the gate, cleanup proposed the three junk entries, Modified By and Created By read as people, file names and months readable, every starred name coded, roster person kept the roster code. Full battery passing, including the 5,000-customer two-session test.

## v7.0.5 — 29 September 2026

### What this fixes
1. **Roster people no longer get a second code.** A roster person in another spelling (order swapped, middle initial added, "Last, First") is matched by name parts and attached to their roster code. The cleanup panel also finds existing duplicates of this kind, keeps the roster code, and moves the other spellings onto it.
2. **The cleanup panel appears whenever the key needs it**, not only when the key also has "risky" word-like names, and it never pauses a scrub. Company names made of ordinary words, names with "(25)", "& Sons" or "Inc." are not called junk.
3. **Less noise from a 14-file batch:** a first name on one mention only counts when that word is never used in lowercase in the files (Hope, Grace, Bill as words pass); greetings no longer grab the next word ("Thanks everyone", "Dear client"); a built-in list of common software, tools, vehicle and HVAC brands, provinces and major cities stays readable.
4. **Names that are also words** ("Grace Voss") are caught by a first-name-plus-capitalized-partner rule.
5. **Document properties never name a person.** Author, last modified by, comment authors, tracked-change authors, company and manager are stripped from Word files, and the file properties of Excel outputs are blanked, whether or not the person is in the key.

### Tested
Full battery on this build: 32-check suite, conversation, records, survey, grammar and transcript attack suites, roster and payroll layouts (wide header, First/Last columns, both name orders, roster people in other spellings), interview log with repeated wording, noise batch with greetings, brands and places, keep list across Clear and sessions, key cleanup, AutoTask review, 5,000-customer two-session, billing cleanup, list import and checkup, Word metadata stripping, speed at 1.0 seconds.

## v7.0.4 — 29 September 2026

### What this fixes (the payroll file that never came clean)
**Names in the header row were never scrubbed.** The tool kept the first row of a spreadsheet untouched so column headers stay readable. In a wages report laid out one column per employee, the employee names ARE the header row, so "Code ticked names" put them in the key and the next scrub left the header exactly as it was. That is why the same list came back every time.

Two changes:
1. Header rows are scrubbed like any other text. Key names and detectors apply; ordinary header words are not in the key, so they stay readable.
2. A header row that is mostly people (three or more, half the row or more) is read as a list of staff and coded automatically, no review needed.

Also: a sentence sitting in a cell (a note like "so-and-so has 2 names in QB") is no longer mistaken for a column header.

### Tested
A wide wages layout with eight employees as column headers in "Last First Middle" form and pay categories as rows: v7.0.3 reproduced the bug exactly (apply changed nothing); v7.0.4 codes all eight in the header automatically, keeps Regular, Overtime, Vacation and Total Wages readable, and leaves nothing to review. Full battery passing; one long-standing check was updated because a surname in a header row is now replaced instead of merely flagged.

## v7.0.3 — 29 September 2026

### What this fixes (from the interview log and the payroll file)
1. **Ordinary words flagged as names in logs with repeated wording.** Two rules were fooled by the same sentence appearing in many rows: "nothing paid-for" counted as a person because "paid" is a person-verb, and words like Still, Says, Believes and Workload counted because they were capitalized at the start of every row. Now a person-verb only counts on a distinct sentence and, in written text, only for a capitalized word; a repeated capitalized word needs at least one mid-sentence use or three different sentences.
2. **"Code ticked names" looked like it did nothing.** Long lists were paged 25 at a time and the hidden rows were left for the next round, so the list came back looking unchanged. The pager is gone: every name is in one scrollable list and Apply handles all of them.
3. **Words from a previous file came back.** Unticking a word only lasted the session, and Clear wiped it. Unticked words are now saved in the client's key as a keep list, survive Clear, and load with the key next time.
4. **Same person, both name orders.** "Okafor Sam" and "Sam Okafor" (and "Okafor, Sam") share one code in exports.
5. Hyphenated words made of ordinary words (follow-up, part-time) are ordinary words.

### Tested
An interview log with 30 rows of repeated note templates: only the two real names flagged, no ordinary words; Apply cleared the list in one click. Keep list: a term unticked on file one stayed readable and unasked on file two after Clear, and again in a fresh session from the saved key. Payroll sheet with both name orders: one code per person. Full battery passing.

## v7.0.2 — 29 September 2026

### What this fixes (from the second real wages report)
1. **Columns wrongly treated as people.** A header only marks a name column if it names people and the values inside look like people. Headers about a type, status, ID, number, rate, hours, date, pay, email, phone or address never do, and a column whose values are mostly plain words (Full-time, Active, Regular) is left alone even if the header says Employee.
2. **Emails, phones, addresses and numbers never become EMP codes.** They go to their own detectors (EMAIL, PHONE, ADDR) as before, and you control removal or coding with the existing options.
3. **You choose the columns.** The summary card lists every column treated as people, each with a tick. Untick one and it stays off for that client (saved in the key), and the codes made from that column are retired on the spot, so nothing keeps coming back.
4. **One person, one code, bare surname included.** A person's own first and last names are spellings of their code, not separate codes. A surname two people share still gets its own code.
5. **Diagnostics button at the top of the page**, always visible. The report now lists which column headers were treated as people and which you switched off (headers only, never values).
6. **Code legend** on the summary card: EMP staff, CUST customer, VEND vendor, OTH other person, LOC location, EMAIL, PHONE, ADDR.

### Tested
A realistic HR wages sheet (Employee Name, Employee ID, Employee Type, Employment Status, Manager, Contact Email, Contact Phone, Home Address, hours, rates, dates): people coded with one code each, emails, phones and addresses coded by their own detectors, type and status words readable, numbers and dates untouched, no junk in the key; unticking the Manager column restored it and kept it off. Full battery passing.

## v7.0.1 — 29 September 2026

### What this fixes (from the first real wages report on v7.0)
1. **Names grouped wrongly in spreadsheets.** A first name that is also a word (Sam, Bill, Grace, Mark) was not counted as part of the person, so the tool paired the surname with the first name in the next cell. Fixed: a first name beside an unknown surname joins it, and a bare comma between cells is never a name boundary.
2. **First-name and last-name columns.** "First" and "Last" (and surname, given name, prénom, nom) side by side now read as one person per row, with both halves sharing the person's code.
3. **More column headers recognized.** Employee, manager, supervisor, technician, contact, owner, rep, driver, applicant, prepared by, approved by and many more now mark a name column; product, item, service, plan, sku, location, title, memo and similar never do. Wages, salary, pay, overtime and hours-worked contexts code as staff.
4. **Key cleanup catches ordinary words hung on people.** The cleanup panel now also proposes retiring single dictionary words attached to a person that are not part of their name ("Regular", "Survey"), each with its own tick so a real nickname can be kept. A person's own first or last name is never proposed.
5. **Diagnostics no longer include file names**, and now include key health counts (duplicate names, junk entries, ordinary-word aliases).

### Tested
Three wages layouts (First Last cells, "Last, First" cells, First and Last columns), each with word-like first names: zero review needed, zero surnames visible, one code per person across both halves. A polluted key with phrases and ordinary words on employees: cleanup proposed exactly the bad entries, kept the nickname that was unticked, and ordinary text read normally afterwards. Full battery unchanged and passing.

## v7.0 — 29 September 2026

### What this is
A rebuild of the part of the tool that decides what is a name. The stack of guessing rules built up over sixty iterations is gone. In its place: three engines, a results screen built around decisions, and key safety features a professional developer would insist on.

### The three engines
1. **Columns.** In spreadsheets and exports, every value in a name or contact column is coded, whatever it looks like. "Better Home Care", "9876543 Canada Inc." and "quiet meadow consulting" are all coded because of where they sit, not what they look like.
2. **Dictionary.** In sentences, every word is checked against a 600,000-word English and French dictionary. A word that is not plain English or French is coded (Okafor, Bartholomew, Marisol, Kanata). Ordinary words never get flagged, because it is a lookup, not a guess. Contractions, plurals, possessives and accents are handled.
3. **Lists.** Roster, customer lists and Paste names replace every known name, including names that are also words. Two extra list-based signals stay: a known first name on a single mention (Joseph, Priscilla) and a compact grammar check (Justice's appointment, Thanks Justice, "justice called" twice, speaker labels, sign-offs).

Transcripts run in any casing: "i asked rosalind" is caught. Sentence-start words like Honestly and Anyway are not.

### Keys can't take junk
A saved spelling must be name-shaped: five words or fewer, no sentence punctuation, and anchored by a word that is not plain dictionary or is a capitalized first name. "I said", "you know" and "off for Bram" are refused however they arrive. Nicknames like "Survey" on a real person still pass.

### Speed
Three slow spots that grew with file size were found and fixed: token lookups that rescanned the whole key for every cell, near-miss matching against every key entry, and two grammar patterns written the expensive way round. A 900 KB export went from 76 seconds to 6. An 8 MB three-file run (1.4 MB transcript, 5.7 MB export, 1 MB report) that previously never finished now scrubs in 16 seconds and re-scrubs after review in 21.

### The results screen
One summary card: files scrubbed, identifiers replaced, safety check result, and how many names need a decision. Below it, only the queue: every name ticked, one button ("Code ticked names, keep the rest as words"). Everything else, counts, checks and technical notes, sits behind one collapsed Details line.

### Key safety
- **Undo last apply**: one click restores the key and re-scrubs.
- **Key history**: every save keeps the last 12 versions in this browser, restorable from a dropdown beside the key.
- **Lock on any change**: names added through the review list now lock downloads until the key is saved. This gap existed in every earlier version.
- **Copy diagnostics**: a report with counts, timings and shapes only, never names, to paste back for debugging.
- **Quick start** card at the top of the page.

### Still to come (v7.1)
The client vault with one password per client and 1Password autofill; text-PDF reading; dated vault backups.

### Tested
Every attack from the issue history rebuilt with fake data and passing: single-mention names including the Italian-to-English case, lowercase transcript names, sentence fragments, filler words, Justice and Bill, plural nouns, sign-off noise, contractions, the multi-line survey export, messy locations and location codes, double spaces, comma names, junk-in-key, ordinary reports with place names (zero flags). Plus the 32-check suite, 4,900-row AutoTask review, seeded list run, 5,000-customer two-session, Excel round trip, billing key cleanup, list import and checkup, roster import, un-scrub, and the 8 MB multi-file run. v6.0.4 and v5.9.9 remain in your files as fallbacks.

## v6.0.4 — 28 September 2026

### What changed
1. **Each location gets its own code.** Stores and addresses now become LOC-001, LOC-002 and so on, instead of all turning into the same blank [LOCATION]. A transcript comparing two stores stays comparable, and un-scrubbing puts each real name back. The codes are saved in the key, so the same store gets the same code every session. Spellings that count as the same place ("Calgary NE" and "calgary ne") share one code; a different place ("Calgary Northeast") is left alone unless it is on the list.
2. **Existing keys upgrade themselves.** Loading an older key merges duplicate location spellings, and the first scrub gives every location its code. The key then asks to be saved, like any time new codes are added. No hand editing.
3. **The job titles field is gone.** It was pre-filled with an old client's labels and duplicated what the roster already sets. Staff labels now come from the roster and the key, with plain defaults (OWN, MGR, EMP) for a new client.

### Limit
Files scrubbed before v6.0.4 still say [LOCATION]. That blank never recorded which store it was, so un-scrubbing can't tell them apart. Re-scrub from the original file if you need the stores separated.

### Tested
Attack transcript comparing two stores with messy spellings, a double space, a possessive ("Calgary NE's manager"), a street address, and a different company with a similar name: three places, three codes, duplicates merged, nothing blank, similar-name company untouched, same codes in a second session from the saved key. Old key with duplicate locations and an old client's staff labels: duplicates merged on load, labels kept, codes added on first scrub, save prompt shown, un-scrub restored each store. Full battery: 32-check suite, conversation, records, survey, grammar and transcript attack suites, roster locations, AutoTask review, 5,000-customer two-session, Excel round trip, billing cleanup, list import and checkup, 1.0 seconds on the speed test.

## v6.0.3 — 28 September 2026

### What this fixes
Two problems on a real call transcript: the review list filled with whole sentences marked "name slot", and real names were missed, including a name the transcription turned into its English version.

### Causes found
1. **Sentence fragments as name slots.** The name-slot finder, built for repeating rows in exports ("Service Request From BD-563 - Faye Parsons"), was also running on transcripts. In a transcript every speaker line starts with a code, so it treated whatever followed as a name to review.
2. **Single mentions missed.** A lone word needed two capitalized mentions to be flagged. People on a call are often named once in passing, so "Joseph came in" or "i asked rosalind" slipped through.
3. **Sentence starts looked like mid-sentence capitals.** In transcripts the line before each sentence is a timestamp, so the tool thought every sentence-starting word ("Honestly", "Anyway") was capitalized mid-sentence, which is a name signal.

### What changed
1. Name slots now come only from list and export content, and a slot value has to look like a name: five words or fewer, starting with a capital, mostly capitalized words, no sentence punctuation.
2. A known first name in written or spoken sentences is flagged on a single mention. In transcripts this also works in lowercase. Guards keep places out: a name after "the", or after "in", "at", "from" and similar ("in Victoria and Georgia", "the Paris supplier"), is not flagged.
3. A line break now counts as the start of a sentence, and in transcripts a word only ever capitalized at the start of a sentence is not treated as a name.
4. Pasted text that is really rows and columns is read as a list, and comma-heavy paragraphs are no longer mistaken for one.
5. Four-letter names ticked in a transcript are replaced in both spellings, like longer names.

### Tested
New attack transcripts built like an Otter export: rambling speech with commas everywhere, every name mentioned exactly once, one in lowercase. On v6.0.2 all three names leaked and the review list held six sentence fragments; on v6.0.3 all three were flagged, zero fragments, zero sentence-start noise, zero leaks after one apply. An ordinary report containing Victoria, Georgia, Paris and Jordan as places: zero flags. Full battery: 32-check suite, conversation, records, survey and grammar attack suites, location roster, AutoTask review, 5,000-customer two-session, billing cleanup, list import and checkup, 1.0 seconds on the speed test.

## v6.0.2 — 28 September 2026

### What this fixes
1. **Roster locations duplicated on small differences.** Importing a roster listed "Calgary" and "calgary" as two locations. Cause: new locations were checked against the locations box, but never against each other. Now capitals, extra spaces, and trailing punctuation count as the same place, the first spelling wins, and genuinely different places ("Calgary NE") stay separate. Applies to the people tab location column, the business tab location list, and merging into the locations box.
2. **Names and locations typed with double spaces.** "Calgary  South" in a file only had "Calgary" replaced. Multi-word names and locations now match with any run of spaces between the words.
3. **Found by attack testing: a ticked name containing a comma could break one-name-one-code.** Key lines use commas to separate spellings, so ticking a candidate like "Drop-off for Bram, Faye - Screen Replacement" wrote a line the key read as two separate spellings, and two people could end up sharing one. Ticked names now never carry a comma into the key: "Bram, Faye" is stored as Faye Bram (text written as "Bram, Faye" is still replaced), and anything else keeps its longest clean part. This existed since v5.9.9.

### Testing note
While fixing item 3, I found the billing-cleanup test had been pointing at an older build, so the v6.0 and v6.0.1 notes overstated that one check. Every test script now points at the build being shipped.

### Tested
New attack roster: seven people with Calgary, calgary, "Calgary ", CALGARY., Calgary NE, calgary ne, and "Calgary  South" against an existing "Calgary south". Result: three distinct places, first spellings kept, NE separate, re-import adds nothing, every spelling in text replaced. Full battery on this exact build: 32-check suite, conversation and records attack suites, survey CSV attack, Justice grammar cases, AutoTask review, 5,000-customer two-session, billing cleanup (0 duplicates, 0 surnames), list import and checkup, 2.4 seconds on the speed test.

## v6.0.1 — 22 September 2026

### What this fixes
A survey CSV came out corrupted. Cause found and reproduced: survey exports put line breaks inside quoted answer cells, and every CSV reader in the tool split rows on line breaks without checking quotes. A multi-line answer's second line was treated as its own row, its commas split it into fake columns, and worse, the name detector coded answer fragments as fake people ("which is too long." became OTH-002 in the key).

### What changed
1. **Quote-aware row splitting everywhere.** One shared splitter now keeps a line break inside quotes as part of its cell. Applied to the output writer, the name-list detector, the file-type reader, the list importer, and the prose-column extractor. Multi-line answers stay one cell, escaped quotes survive, row and column counts match the input exactly.
2. **Survey results is its own dropdown type.** Auto-detected when two or more headers end in a question mark, or a Timestamp-style header sits beside one. Reads as records with the free-text answer columns treated as prose, so names inside answers still get caught.

### If a key was polluted by the bug
Junk entries created from answer fragments are caught by the key cleanup panel on the next scrub: retire them there, then re-scrub from the original file, not from the corrupted output.

### Tested
New attack fixture: 192-row survey with multi-line answers, embedded commas, and escaped quotes. Shape preserved, answers verbatim, all 48 names coded, zero junk people, auto-detected as Survey results. Full battery: 32-check suite, both v6.0 attack suites, AutoTask, 5,000-customer two-session, Excel round trip, billing cleanup, list import. All pass at 2.6 seconds on the big-file speed test.

## v6.0 — 22 September 2026

### What this is
The content-aware release. The scrubber now reads what each file IS before it scrubs, and applies the right rules to each kind of content. Built in four approved steps, each attacked with make-it-fail tests before moving on.

### What changed

**1. Every file gets a document-type dropdown, auto-selected, correctable by you.**
The types: Conversation or transcript, Report letter or notes, List or export, Invoice, Receipt, Account or merchant statement, Policy process or agreement, HR document. Detection runs on content signals (invoice number + HST + amount due says invoice; statement period + closing balance says statement; speaker labels say transcript), never on the file format. Pasted text gets the same selector. Spreadsheets are also read column by column: a memo or notes column full of sentences is treated as prose even inside a list file.

**2. Grammar layer: the sentence around a word can say "person".**
Person-verbs (Justice called), possessives (Justice's appointment), greetings and sign-offs (Thanks Justice / Regards, Marisol), and speaker labels now flag names even when the word is an ordinary dictionary word with lowercase uses elsewhere. Grammar beats lowercase evidence. One strong signal flags on a single mention; verb-only evidence is held to a higher bar so plural nouns like "Customers called" stay out of review.

**3. Conversation mode: transcripts work in any casing.**
For files read as conversations, capitalization rules and lowercase evidence switch off. Speaker labels and grammar catch names typed fully lowercase ("justice called me", "dana whitlock 0:31"). A ticked transcript name is replaced in both its lowercase and capitalized spellings, but only inside conversation files, so a report in the same batch keeps its ordinary lowercase words readable.

**4. Records mode: list columns skip sentence scanning.**
Pure list columns no longer feed the grammar layer, which removes a class of false flags and keeps big exports fast. The counts-based name detection still scans everything, so buried names in spreadsheets are caught exactly as before.

### What the attack tests broke and got fixed before shipping
"The company's invoice" flagging company as a person; a ticked lowercase name leaving its capitalized twin behind; the fix for that over-scrubbing prose files; the tool's own codes (OTH-04) re-flagged as names in two shapes; "monday called" flagging Monday; "Best, / Practices" sign-off noise; duplicate single-word rows beside speaker pairs; verb-shaped noise in records columns.

### Unchanged on purpose
The key format, code assignment, one-name-one-code, canaries, the save lock, and every v5.9.x decision rule. v5.9.9 remains in your files untouched as the fallback.

### Tested
Full adversarial suites for conversation and records modes, the Justice and Bill grammar cases, the 32-check regression suite, 4,900-row AutoTask single-round review, seeded-list run, 5,000-customer two-session code consistency, billing key cleanup, list import idempotency, key checkup, canaries, and the freeze test at 2.3 seconds. All pass.

## v5.9.9 — 18 September 2026

### What this fixes
Two follow-ups from real use: assigning a flagged word to an existing person ("Add to SIT-02") didn't stick, and the question of whether common-word protection is limited to a fixed list.

### What changed

**1. Your assignment always sticks.**
The "Add to [existing person]" and "Existing person" actions now (a) override the ordinary-words filter, because an explicit human assignment outranks it, and (b) record the decision in the key, so the word is replaced everywhere from that scrub on and in every future session. Before, a word on the internal junk list (Ticket, Survey, Mobile and the like) was silently refused even when you assigned it on purpose, and words that are also dictionary words were rerouted to a second review. Both gone. Single letters are still refused, months, weekdays and very common words still keep the spot-by-spot check, and the automatic paths still refuse ordinary words on their own.

**2. Common words pass on evidence, not just on a list.**
The word lists are one layer (function words, a large dictionary, accounting and report words, trade words, your business line). New second layer with no list at all: if a capitalized word also appears in lowercase in the same files at least as often, it is being used as an ordinary word and is not flagged. "Harvest" the event beside "we harvest feedback" passes automatically; "Bloom" that only ever appears capitalized is still flagged, because that is how surnames behave. The same evidence check clears repeated all-dictionary phrases.

### Unchanged on purpose
Everything else, including code assignment, the key format, and the 5.9.8 rule that a ticked name is replaced everywhere.

### Tested
New case: a misspelled customer assigned to an existing person via "Add to SIT-02" replaced all mentions and saved to the key; "Survey" as a deliberate nickname on the same person was honoured despite being on the junk list; "Harvest" with lowercase uses was not flagged while capital-only "Bloom" was; ordinary sentences stayed untouched; zero pending and zero spot-by-spot leftovers after one apply.
Full regression: 32-check suite, 4,900-row AutoTask single-round review, the four v5.9.5 cases, canaries, v5.9.8 cases, billing key cleanup, list import idempotency, key checkup, the 5,000-customer two-session test, and the freeze test (2.3 seconds). All pass.

## v5.9.8 — 18 September 2026

### What this fixes
Two complaints from real use: ticked names in the Possible names section were not being replaced, and everyday words like therapy and therapist were being flagged as possible names.

### What changed

**1. A ticked name is replaced everywhere. One rule change to make that true.**
Ticking a name in the Possible names list, or at the "could damage normal words" question, now means exactly what it says: it really is a name, so every mention is replaced, with no second per-spot question. Before, single names that were also dictionary words quietly moved to a second collapsed review, which looked like the tool ignoring your tick. Your decision is saved in the key, so it holds in every future session.
Two guardrails stay: month and weekday names (May, June, Mon) and very common words always keep the spot-by-spot check even after a tick, because "in May" is usually a date; and unticked stays untouched. The spot-by-spot review still exists for word-like key aliases you have never answered, like a staff nickname from the team list.
Also fixed: names you tick no longer re-trigger the "could damage normal words" question on the re-scrub, which could silently stall the apply.

**2. Everyday trade words are never flagged and never coded on their own.**
About 120 service-business words joined the protected list: therapy, therapist, counselling, session, treatment, assessment, appointment, booking, inspection, installation, grooming, lesson, membership, warranty, technician, patient, and the like. They cannot be flagged alone or become codes alone, but they still count inside real names: "Marlow Therapy" is still flagged, because Marlow is not an everyday word.

### Unchanged on purpose
Everything else: code assignment, key format, list import, key cleanup, canaries, the gate.

### Tested
New case: a note with therapy, therapist, appointments and treatments repeated throughout flagged none of them; "Marlow Therapy" was flagged; ticking Bloom, Kip and Marlow replaced every mention immediately with no stall and no leftover spot-by-spot rows; the decisions saved into the key and a fresh session replaced them again with no questions. Suite check updated for the new rule ("in May" still protected, undecided word-names still spot-by-spot, selective replace still works): 32 of 32 pass.
Full regression: 5-file pack with identical codes across sessions, 4,900-row AutoTask single-round review, seeded-list run (0 name flags, 0 suffixes), the four v5.9.5 cases, canaries, billing key cleanup, list import and checkup, the 5,000-customer two-session test, and the freeze test. All pass.

## v5.9.7 — 18 September 2026

### What's new

**Customer and vendor list import (optional).**
A new "Import list files" control in the key section takes a client's customer or vendor list up front, several files at once, in mixed formats: Excel, CSV, TSV, Word, plain text, or pasted names. Not PDF; export from the source system as Excel or CSV instead. Every listed name gets a code before the first scrub, with all existing rules applied: one name one code, existing codes never change, junk words refused, partial forms and name-order variants on the same code, numbered companies and legal suffixes recognized. Each file is auto-detected as customers or vendors from its own title, customers as the fallback; pasted names have a one-click type picker. A per-file summary shows names found, new codes created, and how many were already in the key. The key locks until saved. Importing the same file twice creates zero new codes.

**Key checkup against the imported list.**
After an import, the tool compares the key to the list and proposes, for your approval only:
- Complete these names: a bare surname in the key that matches exactly one full name on the list gets the full spelling attached to its existing code. Two matches on the list means it is left alone.
- Worth knowing: a key entry filed as an outside person that appears on the customer list is pointed out, no change made.
- In the key but not on the list: shown with a per-line retire tick, kept by default, so walk-ins and real people stay and misspellings go. Retired lines move to the retired section, so files already scrubbed still un-scrub.
Nothing changes until Apply, and nothing is ever renumbered.

### Unchanged on purpose
Everything else: scrubbing, detection, canaries, the gate, code assignment, key format.

### Tested
Import: three mixed files at once (QuickBooks-style Excel contact list, vendor CSV, plain text) coded 12 names to the right prefixes, kept Amazon readable, and a re-import created zero new codes. Seeded quality test: importing the 180-company list before scrubbing the 4,900-row AutoTask file left zero company names and zero legal suffixes with NO name review needed; the 37 name flags from the unseeded run dropped to 0, leaving only product phrases to keep. Checkup: a dirty key (bare surname, wrong-type entry, misspelling, walk-in) produced the right three proposals; after apply, the surname was completed on its code, the walk-in kept, the misspelling retired, and old scrubbed text with the retired code un-scrubbed correctly.
Full regression: 31-check suite, 5-file pack in two sessions with identical codes, AutoTask single-round review, the four v5.9.5 cases, canaries, remembered decisions, key cleanup on the 3,600-row billing test, the 5,000-customer two-session test, Excel round trip, team list import, and the freeze test. All pass.

## v5.9.6 — 18 September 2026

### What this fixes
The Bill and Dave run that polluted the key and made the results page scroll endlessly: one name held two or three codes, phrases like "Ticket C" were coded as people with auto-made nicknames like "Ticket" and "T", and the review page showed one row per occurrence plus rows with 0 mentions.

### What changed

**1. One name, one code, everywhere.**
Every path that can create a code (the review list, list detection, name slots, company detection) now checks the whole key first and reuses the existing code instead of making a new one. Duplicates can no longer be created.

**2. Ordinary words can never become a person.**
Words like Ticket, Case, Invoice, Survey, Mobile and single letters are refused as names and as aliases from every path. Names added from the review list no longer get auto-made nicknames. A ticked entry the tool refuses is kept as words instead, so your decision is still honoured.

**3. Key cleanup, one time, with your approval.**
When a key holds duplicates or word-entries, a "This key needs a cleanup" panel lists exactly what it wants to do: each duplicated name keeps its LOWEST code, the other codes are retired, and word-entries are retired. Retired lines move to a new ---retired--- section: nothing is renumbered, and files you already scrubbed still un-scrub correctly (verified: old text with a retired code restores to the right name).

**4. A review page you can finish.**
Word-name decisions are one row per name with a count ("Rod, 14 places"), with a per-name choice (person everywhere / word everywhere / spot by spot) and the individual spots tucked behind "show the spots". The possible-names list shows 25 rows at a time with "Show 25 more". Shared-name rows with 0 mentions are gone. The tool also looks one step ahead: things that would only surface after your first decisions are flagged in the same round, so one review pass settles the file.

### Unchanged on purpose
Code assignment, the scrub order, all detection from v5.9.5, canaries, and the gate. The key format gains one ---retired--- section; old keys load unchanged.

### Tested
A 3,600-row billing file against a deliberately polluted key (one surname under three codes, another under two, plus Mobile, Survey and Ticket entries): the cleanup panel listed 2 merges and 3 retirements, produced a key with zero duplicates, kept the real person (Rod), left "mobile survey follow up" readable in text, showed 0 multi-code markers, paged 146 candidates at 25 per page, and finished with every surname coded after one review pass. Old scrubbed text with retired codes un-scrubbed correctly.
Full regression: 31-check suite, the 5-file pack (two sessions, same codes), the 4,900-row AutoTask test now settling in ONE review round (pending 0 after apply), the four v5.9.5 cases, canary pass and fail paths, remembered risky decisions, the 5,000-customer two-session test, Excel round trip, team list import, and the freeze test. All pass.

## v5.9.5 — 17 September 2026

### What changed

**Change 1: names built from ordinary words get caught.**
The leftover scan now looks at runs of 2 to 5 capitalized words and skips a phrase only when EVERY word is common or protected, not when any one is. A phrase made entirely of dictionary words is flagged once it repeats. This is what catches business names like "Better Home Care".

**Change 2: name slots.**
When the same text template repeats in a file (like "PPT# - Service Request From CODE - Y" or "Contract Name: CODE Y"), whatever sits in the variable spot beside the code is treated as a possible name, even lowercase, even ordinary words, even a single word. Slot position outranks the word lists.

**Change 3: the business line.**
A new one-line question in the client profile: "What does this client do and sell?" It is saved in the key file header as business = and used as vocabulary: phrases made of the client's own shop talk pass as readable, and phrases that do not fit are flagged no matter how often they repeat. Frequency alone never clears a phrase.

**Safety net 1: the gate always blocks.**
Nothing can be copied or downloaded while any candidate is unresolved. Each candidate is either ticked (coded) or left unticked (kept as words). The "Ignore all of these" button and the "Untick all shown" link are gone; "Tick all shown" stays, because bulk-coding is the safe direction.

**Safety net 2: canaries.**
Every run silently plants 5 fake names in awkward spots: mid-sentence, beside a code, lowercase, in a header row, and mixed with common words. If the scan misses any, the run shows "Safety check failed", names the missed spot, and locks copy and downloads. The fakes are always stripped from the output and the review list. When the safety check passes, the review list is empty, and the key is saved, downloaded files are named "SCRUBBED v5.9.5 PASSED - ...".

### Unchanged on purpose
Code assignment and the key format (a name that is CUST-025 stays CUST-025; the header gains one business = line), the scrub order, the numbered-company pattern, the company suffix walking, the matcher, the xlsx and docx writers, the brand and accounting protections, and the review gate.

### Tested
New cases, and which change caught each:
- Two-word ordinary-word business name repeating 40 times in ticket titles ("Better Home Care"): flagged. Change 1.
- Lowercase name beside a code in a repeating template ("quiet meadow consulting"): flagged. Change 2.
- Name made entirely of dictionary words ("Green Valley Cartage"): flagged. Change 1.
- Rare service name ("Thermal Recalibration Bench Service") with the business line filled in: NOT flagged, stays readable. Change 3.
Canaries: pass path and fail path both verified; a deliberately blinded run failed, named the missed spot, and locked.
Full regression, before and after: 31-check suite, the 5-file v5.9.2 pack in two sessions with identical codes, the 4,900-row AutoTask test (zero suffixes and zero names after one review pass, products readable), the 5,000-customer two-session test, Excel round trip, team list import, remembered risky decisions, and the 8,000-name freeze test. All pass.

Known limits: text sitting beside a code in a repeating template is flagged even when it is a product, until the business line or a Keep decision clears it; that is deliberate. The output file-section order can vary between runs when several files are scrubbed together (contents and codes do not).

## v5.9.4 — 17 September 2026

### What changed

**1. Names added from the review list default to OTH.**
The "Possible names" dropdown now defaults to Other person (OTH) instead of the client's first staff role, so ticked names stop landing under codes like CEO. Customer (CUST) and Staff or owner are one pick away, and the role list only appears when Staff or owner is chosen.

**2. The "could damage normal words" question is asked once per name, per client.**
Your tick or untick is written into the key file under a new ---decided--- section. The next scrub for that client, and every one after, skips the question for names you already answered. Because the decision lives in the key, answering it counts as a key change, so save the key when prompted. Older key files load fine; they just have no saved decisions yet.

### Unchanged on purpose
Existing code numbering, and the per-occurrence review of word-like names (May, Don, Rod as a word vs Rod the person) inside documents. That review is a locked product rule and still runs; only the repeated key-entry question went away.

### Tested
Bill-and-Dave-shaped case: a key with Mobile, Rod and Survey under CEO codes. The question appeared once; Rod ticked, Mobile and Survey unticked; the key saved with mobile = skip, rod = use, survey = skip; a fresh session loading that key scrubbed with no question. Review-list default confirmed as OTH.
Regression: check suite 31 of 31, the 5-file pack, and the 4,900-row AutoTask test (all pass).

## v5.9.3 — 17 September 2026

### What changed

**1. Names inside longer text are found and coded (the AutoTask problem).**
Company names buried in ticket titles, service descriptions and group header rows are now coded in place, with the rest of the sentence left intact. "Service Request From ACME-442 - Northern Gate Solutions Inc" becomes "Service Request From ACME-442 - CUST-101". Every character of every cell is scanned, in every column and row.

**2. Legal-suffix companies are treated as names.**
Any text ending in Inc, Inc., Incorporated, Ltd, Ltée, Limited, Corp, Corporation, Co., LLC, LLP or Enterprises is coded, along with numbered companies like "1234567 Canada inc" in any spacing or capitalization.

**3. Partial forms match the key.**
A key entry "Northern Gate Solutions Inc" now also catches "Northern Gate Solutions" and "Northern Gate" on the same code. This only works for names already in the key; a client who was never coded is caught by the review list instead.

**4. Products and services stay readable.**
Product, licence, bundle, rate and fee wording is protected from coding, and words that belong to a known client name are protected from that protection, so "Laptop Diagnostics - Minimum Bench Fee - Lakeshore Dental" keeps the product half readable while the client half is coded.

**5. When in doubt, it codes and tells you.**
Everything coded out of longer text is listed in a new results section, "Company names found inside longer text - coded, check none are products," so an over-scrub is visible and reversible from the key.

**6. Run summary.**
The results now state how many identifiers were replaced, how many new codes this run created, and everything flagged for review. Flagged names still lock Copy and downloads until handled.

### Unchanged on purpose
Existing code numbering. A name already in the key keeps its code; new names continue from the highest number.

### Tested
AutoTask-style file: 4,900 rows, 797 unique item titles, 180 companies (60 already keyed, some without suffixes), plus products and numbered companies. After one review pass of the 37 flagged no-suffix companies: zero Inc, Ltd, Limited, Corp or key names anywhere in any cell; products readable; numbers and dates untouched; a second session from the saved key produced identical output with zero new codes. Full run 1.4 seconds.
Regression: check suite 31 of 31, the 5-file v5.9.2 pack (all nine checks), the 5,000-customer two-session test, Excel round trip, team list import, and the 8,000-name freeze test.

Known limits: a client that is not in the key and has no legal suffix lands on the review list rather than being auto-coded; when several files are scrubbed together, the order of file sections in the output can vary between runs (contents and codes do not).

## v5.9.2 — 17 September 2026

### Fixed

**1. Numbered companies now get coded (bug 1).**
Names like `1234567 Canada Inc`, `12345678 Ontario Ltd`, `7654321  QUEBEC LTEE` and `1234567Canada inc` are picked up anywhere they appear, not only in a name column. The pattern allows 6 to 9 digits, no space or extra spaces, any capitalization, the province or country word, and Inc, Inc., Incorporated, Ltd, Ltée, Limited, Corp, Corporation, Co, LLC, Enr or SENC. A trailing period no longer creates a second code for the same company.
Affects checks: 1, 2, 3.

**2. Report words and account names are no longer coded (bug 2).**
- Around 120 accounting and report words are never turned into codes, on their own or as part of a name: Sales, Rent Expense, Wages, Accounts Receivable, Accounts Payable, Payroll, Cash, Revenue, Inventory, Depreciation, Invoice, Summary, Detail, Total and so on.
- Column headers and product or service values are protected the same way.
- Account-style reports (Profit and Loss, Balance Sheet, Trial Balance, General Ledger, Transaction Detail by Account, Chart of Accounts) no longer use the "first column is a name list" rule, which is what turned account names into vendor codes.
- A short list of well-known businesses stays readable: Amazon, Dell, Home Depot, Bell Canada, Canadian Tire, UPS, the banks, CRA and similar.
Affects checks: 6, 7, 8.

**3. Every text field is scanned (bug 3).**
Known names are matched in all fields, including memos, descriptions, item titles and report titles, not only name columns. Description and note columns are no longer treated as "safe" columns, so names buried in them still surface for review when they are not in the key.
Affects checks: 1, 2, 3.

**4. The key file can be saved anywhere except beside the scrubbed files.**
Save key file now opens a Save dialog so the folder is chosen on purpose, with a reminder to keep the key in the client's own folder. The key is never written automatically alongside a scrubbed download.
Affects check: 4.

### Unchanged on purpose
Existing code numbering. A name already in the key keeps its code. New names continue from the highest number in the key. Spelling variants, name order and trailing periods attach to the code the key already holds.
Affects check: 3.

### Tested
Test pack of five fake-data files: customer summary, transaction detail with account names, vendor report with real business names, numbered companies report, and names buried in descriptions.

| Check | Result |
|---|---|
| 1 No client, customer or company name survives anywhere | Pass |
| 2 Nicknames, lowercase names, names inside longer text | Pass |
| 3 Same name gets the same code as the key | Pass (two sessions, identical output and codes) |
| 4 Key never written to the output folder | Pass (folder chosen in a Save dialog; browser cannot verify the folder itself) |
| 5 Flagged names locked until reviewed | Pass (5 flags, copy and downloads locked) |
| 6 Report titles and headers readable | Pass |
| 7 Account names readable | Pass |
| 8 Well-known business names readable | Pass |
| 9 Numbers and dates untouched | Pass |

Regression: full check suite 31 of 31; 5,000-customer plus 1,500-vendor plus payroll run in 1.8 seconds with zero names left and identical codes in a second session; Excel scrub and restore with no names left; team list import; 8,000-name freeze test under one second.

Known limits: spelling variants restore to the first spelling found in the list; a name column headed only "Name" is coded as a customer unless the report title says otherwise.
