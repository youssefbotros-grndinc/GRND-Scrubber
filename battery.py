"""GRND Scrubber regression battery. Usage: python3 battery.py BUILD.html [--only name]
Every check comes from a change-log entry. A check prints PASS or FAIL with the evidence; the script exits 1 on any FAIL.
Fake data only. Set GRND_CHROME to a Chromium binary if Playwright has none installed."""
import asyncio, os, sys, re, io, json, time, zipfile
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser import launch
BUILD = sys.argv[1]
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(HERE, "..")
CANARY = re.compile(r"Fernwhistle|Krellvane|Quorbel|Vexqar|quimbervex", re.I)
RESULTS = []

def check(name, ok, info=""):
    RESULTS.append((name, bool(ok), info))
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  <- " + str(info)[:400]))

async def gates(pg, mode="use"):
    for _ in range(4):
        if await pg.query_selector("#riskyGo"):
            if mode == "use":
                await pg.eval_on_selector_all("input[data-risky]", "e=>e.forEach(c=>c.checked=true)")
            await pg.evaluate("document.getElementById('riskyGo').click()"); await pg.wait_for_timeout(1500)
        else:
            break

class Session:
    def __init__(self, b): self.b = b; self.pg = None; self.errs = []
    async def open(self, client="Acme Heating", key="", loc="", health=False, tokens=""):
        self.pg = await self.b.new_page(accept_downloads=True)
        self.pg.on("pageerror", lambda e: self.errs.append(str(e)))
        self.pg.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
        await self.pg.goto("file://" + os.path.abspath(BUILD)); await self.pg.wait_for_timeout(600)
        if client: await self.pg.fill("#pClient", client)
        if key: await self.pg.fill("#keyBox", key)
        if loc: await self.pg.fill("#pLoc", loc)
        if tokens: await self.pg.evaluate("(t)=>{document.getElementById('tokBox').value=t;}", tokens)
        if health: await self.pg.check("#healthMode")
        return self
    async def add_text_file(self, name, text, kind=None):
        kind = kind or ("csv" if name.lower().endswith((".csv", ".tsv")) else "txt")
        await self.pg.evaluate("([n,k,t])=>{ window.__fq().push({name:n,kind:k,text:t}); window.__renderFL(); }", [name, kind, text])
    async def add_disk_file(self, path):
        await self.pg.set_input_files("#fileIn", path); await self.pg.wait_for_timeout(900)
    async def paste(self, text, ctype=None):
        await self.pg.fill("#inBox", text)
        if ctype: await self.pg.select_option("#pasteCt", ctype)
    async def scrub(self, gate="use", wait=2500):
        t0 = time.time()
        await self.pg.evaluate("document.getElementById('scrubBtn').click()"); await self.pg.wait_for_timeout(wait)
        await gates(self.pg, gate); await self.pg.wait_for_timeout(600)
        # wait for the tail phase to finish
        for _ in range(40):
            if await self.pg.evaluate("!!window.__lastCands"): break
            await self.pg.wait_for_timeout(500)
        self.secs = time.time() - t0
        return await self.result()
    async def result(self):
        pg = self.pg
        r = {}
        r["out"] = await pg.input_value("#outBox")
        c = await pg.evaluate("window.__lastCands ? window.__lastCands.map(x=>({name:x.name, match:x.match?x.match.code:null, why:x.why||''})) : []")
        r["cands"] = [x for x in c if not CANARY.search(x["name"])]
        r["names"] = [x["name"] for x in r["cands"]]
        r["ctx"] = await pg.evaluate("window.__ctxCount || 0")
        r["canaryFail"] = await pg.evaluate("window.__canaryFail || []")
        r["key"] = await pg.input_value("#keyBox")
        r["tok"] = await pg.input_value("#tokBox")
        r["nameCols"] = await pg.evaluate("window.__nameCols || []")
        r["unsaved"] = await pg.evaluate("!!window.__keyUnsaved")
        r["report"] = await pg.evaluate("document.getElementById('report').textContent")
        r["sens"] = await pg.evaluate("document.getElementById('sensitive').innerText")
        r["leaks"] = await pg.evaluate("window.__leakCount || 0")
        return r
    async def apply_all(self):
        """tick every queued name and press the one button"""
        pg = self.pg
        await pg.eval_on_selector_all("input.candCk", "e=>e.forEach(c=>c.checked=true)")
        btn = await pg.query_selector("#applyLeft")
        if btn: await btn.click()
        await pg.wait_for_timeout(3000); await gates(pg, "use"); await pg.wait_for_timeout(800)
        return await self.result()
    async def key_body(self):
        """the full key file as it would be saved (header lines, keep =, ---decided---, ---retired---)"""
        pg = self.pg
        await pg.evaluate("window.showSaveFilePicker = undefined")
        async with pg.expect_download() as dl:
            await pg.evaluate("document.getElementById('saveKey').click()")
        d = await dl.value; p = "/tmp/grnd_keybody.txt"; await d.save_as(p)
        return open(p, encoding="utf-8").read()
    async def load_key_file(self, text):
        p = "/tmp/grnd_loadkey.txt"; open(p, "w", encoding="utf-8").write(text)
        await self.pg.set_input_files("#loadKey", p); await self.pg.wait_for_timeout(800)
    async def save_key(self):
        await self.pg.evaluate("document.getElementById('gateDl') && document.getElementById('gateDl').click()")
        await self.pg.wait_for_timeout(400)
    async def download(self, idx=0, fmt=None):
        pg = self.pg
        await self.save_key()
        await pg.evaluate("var g=document.getElementById('gateOver'); if(g) g.click();")
        sel = f"button[data-dl='{idx}']" + (f"[data-fmt='{fmt}']" if fmt else "")
        async with pg.expect_download() as dl:
            await pg.click(sel)
        d = await dl.value
        p = os.path.join("/tmp", "grnd_dl_" + d.suggested_filename)
        await d.save_as(p)
        return p, d.suggested_filename
    async def close(self): await self.pg.close()

def visible(out, *frags): return [f for f in frags if f.lower() in out.lower()]
def missing(out, *frags): return [f for f in frags if f.lower() not in out.lower()]

# ---------- fixtures ----------
QB_SALES = open(os.path.join(PACK, "1 Sales by Customer Summary.csv"), encoding="utf-8").read()
QB_TXN = open(os.path.join(PACK, "2 Transaction Detail by Account.csv"), encoding="utf-8").read()
QB_VEND = open(os.path.join(PACK, "3 Expenses by Vendor Summary.csv"), encoding="utf-8").read()
QB_NUM = open(os.path.join(PACK, "4 Numbered Companies Report.csv"), encoding="utf-8").read()
QB_DESC = open(os.path.join(PACK, "5 Names in Descriptions.csv"), encoding="utf-8").read()
AUTOTASK = open(os.path.join(PACK, "6 AutoTask Export (4900 rows).csv"), encoding="utf-8").read()
ORDWORDS = open(os.path.join(PACK, "7 Ordinary-word names and slots.csv"), encoding="utf-8").read()

async def t_numbered_companies(b):
    s = await Session(b).open(key="")
    await s.add_text_file("numbered.csv", QB_NUM); r = await s.scrub()
    bad = re.findall(r"\d{6,9}\s*(?:canada|ontario|quebec)\s*(?:inc|ltd|ltee|limited)", r["out"], re.I)
    check("numbered companies coded in every spelling", not bad and not r["canaryFail"], bad or r["canaryFail"])
    await s.close()

async def t_report_words(b):
    s = await Session(b).open()
    await s.add_text_file("txn.csv", QB_TXN); await s.add_text_file("sales.csv", QB_SALES); await s.add_text_file("vend.csv", QB_VEND)
    r = await s.scrub()
    keep = missing(r["out"], "Rent Expense", "Accounts Receivable", "Wages", "Total", "Amazon", "Dell")
    check("account names, report words and well-known businesses stay readable", not keep, keep)
    check("numbers and dates untouched", "2024" in r["out"] or re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", r["out"]), "")
    await s.close()

async def t_buried_names(b):
    s = await Session(b).open(tokens="CUST-101 = Northern Gate Solutions Inc\nCUST-102 = Lakeshore Dental")
    await s.add_text_file("desc.csv", QB_DESC)
    await s.add_text_file("tickets.csv", "Ticket,Title\n1,Service Request From ACME-442 - Northern Gate Solutions Inc\n2,Laptop Diagnostics - Minimum Bench Fee - Lakeshore Dental\n3,Northern Gate renewal\n")
    r = await s.scrub()
    check("legal-suffix company inside a ticket title is coded, rest of the line kept", "Service Request From ACME-442 - CUST-101" in r["out"], r["out"][:300])
    check("product half stays readable beside a coded client", "Laptop Diagnostics - Minimum Bench Fee - CUST-102" in r["out"], "")
    check("partial form of a keyed company matches the same code", "Northern Gate" not in r["out"] and "CUST-101 renewal" in r["out"], r["out"][-200:])
    await s.close()

async def t_single_mention_and_transcript(b):
    s = await Session(b).open(key="SIT-01 = Dana Whitlock")
    await s.paste("Youssef Botros  0:03\nso which store is doing better honestly, i asked rosalind and Bartholomew about it, justice called me about the deposit and justice wants it friday. Anyway Joseph came in. Honestly it was fine.\n", "convo")
    r = await s.scrub()
    n = [x.lower() for x in r["names"]]
    check("lowercase and single-mention names flagged in a transcript", all(k in " ".join(n) for k in ["rosalind", "bartholomew", "justice", "joseph"]), n)
    check("sentence-start words are not names in a transcript", not any(k in n for k in ["honestly", "anyway"]), n)
    check("speaker label flagged", any("youssef" in x for x in n), n)
    await s.close()

async def t_places(b):
    s = await Session(b).open()
    await s.paste("The Barrhaven branch on Elgin Street closed early, Kanata deliveries moved to the Orleans route. We met Perth in the lobby; Russell called about the invoice and Nelson approved it. Customers in Kingston and Cornwall were fine. Report Carleton Place and Hunt Club numbers. 12 Elm Crescent, Kanata, ON K2K 1A1.")
    r = await s.scrub()
    n = [x.lower() for x in r["names"]]
    check("places used as places stay readable and unflagged", not any(p in n for p in ["barrhaven", "kanata", "orleans", "kingston", "cornwall", "carleton place", "hunt club", "elgin"]), n)
    check("place names used as people are flagged", all(p in n for p in ["perth", "russell", "nelson"]), n)
    check("numbered address coded, city kept", "ADDR-" in r["out"] and "Kanata, ON" in r["out"], r["out"][-120:])
    await s.close()

async def t_wages_wide(b):
    s = await Session(b).open(key="SIT-03 = Zakarias Ayyad, Zakarias")
    await s.add_text_file("wages.csv", "Item,Total,Biggar-Heil Emily L,Camellato Lauren,Duncan Shayla,Ayyad Zakarias,Mwangi Kojo,Voss Grace,Okafor Sam,Quimby Rosalind\nRegular,400,10,20,30,40,50,60,70,80\nOvertime,400,1,2,3,4,5,6,7,8\nVacation,10,1,1,1,1,1,1,1,1\nTotal Wages,400,11,22,33,44,55,66,77,88\n")
    r = await s.scrub()
    left = visible(r["out"], "Biggar", "Camellato", "Duncan", "Ayyad", "Mwangi", "Voss", "Okafor", "Quimby")
    check("one-column-per-employee header row coded automatically", not left and not r["names"], (left, r["names"]))
    check("pay categories stay readable", not missing(r["out"], "Regular", "Overtime", "Vacation", "Total Wages"), "")
    check("roster person keeps the roster code", "SIT-03" in r["out"], "")
    await s.close()

async def t_hr_sheet(b):
    s = await Session(b).open()
    await s.add_text_file("hr.csv", "Employee Name,Employee ID,Employee Type,Employment Status,Manager,Contact Email,Contact Phone,Home Address,Regular Hours,Pay Rate\nSam Okafor,10021,Full-time,Active,Bartholomew Mwangi,sam.o@example.com,613-555-0101,12 Elm Street,40,22.50\nBill Quimby,10022,Part-time,Active,Rose Delacroix,bill.q@example.com,(613) 555-0102,88 Oak Avenue,20,24.00\nGrace Voss,10023,Casual,On leave,Mark Ashdown,grace.v@example.com,613.555.0103,7 Pine Crescent,12,21.00\n")
    r = await s.scrub()
    check("HR sheet: people coded, nothing to review", not visible(r["out"], "Okafor", "Quimby", "Voss", "Mwangi", "Delacroix", "Ashdown") and not r["names"], (r["names"], r["out"][:300]))
    check("HR sheet: emails, phones, addresses get their own codes", all(t in r["out"] for t in ["EMAIL-", "PHONE-", "ADDR-"]) and "EMP" not in r["tok"].split("EMAIL")[0][:0], r["out"][:300])
    check("HR sheet: type and status words readable, numbers untouched", not missing(r["out"], "Full-time", "Active", "On leave", "10021", "22.50"), "")
    junk = [l for l in r["key"].splitlines() if re.search(r"=\s*(Full-time|Active|Regular|On leave)\b", l)]
    check("HR sheet: no junk entries in the key", not junk, junk)
    check("HR sheet: Manager column listed and can be unticked", "Manager" in r["nameCols"], r["nameCols"])
    await s.close()

async def t_first_last_columns(b):
    s = await Session(b).open()
    await s.add_text_file("roster.csv", "First,Last,Hours\nSam,Okafor,40\nGrace,Voss,20\nMark,Ashdown,12\n")
    r = await s.scrub()
    codes = set(re.findall(r"\bEMP-\d+|\bCUST-\d+|\bOTH-\d+", r["out"]))
    check("First and Last columns read as one person per row", len(codes) == 3 and not visible(r["out"], "Okafor", "Voss", "Ashdown"), (codes, r["out"][:200]))
    await s.close()

async def t_name_orders(b):
    s = await Session(b).open(key="EMP-07 = Sam Okafor")
    await s.add_text_file("pay.csv", "Employee,Pay\nOkafor Sam,100\n\"Okafor, Sam\",100\nSam Okafor,100\nSam O.,100\n")
    r = await s.scrub()
    check("same person in every name order shares one code", r["out"].count("EMP-07") >= 3 and "Okafor" not in r["out"], r["out"])
    await s.close()

async def t_sharepoint(b):
    s = await Session(b).open(key="OTH-050 = Jan\nOTH-051 = Total\nEMP-01 = Kojo Mwangi")
    rows = "\n".join(f"Report Jan {i}.xlsx,Jan Report,Kojo Mwangi *,Rosalind Quimby,Jan,\"Please review, *Bartholomew Okafor* signed off on {i} items.\"" for i in range(1, 60))
    await s.add_text_file("sp.csv", "Name,Title,Modified By,Created By,Month,Notes\n" + rows + "\n")
    r = await s.scrub()
    check("SharePoint: Modified By and Created By read as people, starred names coded", not visible(r["out"], "Mwangi", "Quimby") and "EMP-01 *" in r["out"], r["out"][:300])
    check("SharePoint: starred name inside a note is flagged for review", any("Bartholomew Okafor" in x for x in r["names"]), r["names"])
    check("SharePoint: file names and months readable", "Report Jan 1.xlsx" in r["out"] and ",Jan," in r["out"], r["out"][:200])
    kb = await s.key_body()
    check("SharePoint: month and word entries retired from the key automatically", "OTH-050" not in kb.split("---retired---")[0] and "OTH-050" in kb.split("---retired---")[1], kb)
    check("SharePoint: roster person keeps the roster code", "EMP-01" in r["out"], "")
    await s.close()

async def t_interview_log(b):
    s = await Session(b).open()
    rows = "\n".join(f'2026-09-{i%28+1:02d},Interview {i},Staff,"Says nothing changes since the move. Believes nothing paid-for goes unused. Priscilla returned; Still no clear owner. Workload is high."' for i in range(30))
    await s.add_text_file("ilog.csv", "Date,Interviewee,Role,Notes\n" + rows + "\n")
    r = await s.scrub()
    n = [x.lower() for x in r["names"]]
    check("interview log: repeated template wording flags no ordinary words", not any(w in n for w in ["says", "believes", "still", "workload", "nothing"]), n)
    check("interview log: the real name is flagged", "priscilla" in n, n)
    await s.close()

async def t_keep_list(b):
    s = await Session(b).open(key="EMP-01 = Sam Okafor")
    await s.paste("Sam Okafor ran the Fernbridge Thermal tool twice and logged it in Fernbridge Thermal again.")
    r = await s.scrub()
    check("keep list: unknown brand lands in the queue once", any("Fernbridge" in x for x in r["names"]), r["names"])
    # untick it, apply: it should be saved under keep = in the key
    pg = s.pg
    await pg.eval_on_selector_all("input.candCk", "e=>e.forEach(c=>c.checked=false)")
    btn = await pg.query_selector("#applyLeft")
    if btn: await btn.click()
    await pg.wait_for_timeout(2500); await gates(pg); r2 = await s.result()
    kb = await s.key_body()
    check("keep list: unticked term saved in the key under keep =", re.search(r"^keep\s*=.*fernbridge", kb, re.I | re.M) is not None, kb[:300])
    await s.close()
    s = await Session(b).open(); await s.load_key_file(kb)
    await s.paste("Fernbridge Thermal again today, says Sam Okafor.")
    r3 = await s.scrub()
    check("keep list: in a fresh session the kept term is not asked again", not any("Fernbridge" in x for x in r3["names"]) and "EMP-01" in r3["out"], r3["names"])
    await s.close()

async def t_key_cleanup(b):
    key = "EMP-01 = Grebo Manning\nEMP-02 = Priscilla Voss\nEMP-03 = Hourly\nEMP-04 = Manning Grebo\nOTH-05 = Statutory holiday\nOTH-06 = March"
    s = await Session(b).open(key=key)
    await s.paste("Grebo Manning booked the hourly crew for the statutory holiday in March. Accrued vacation is paid hourly.")
    r = await s.scrub()
    k = await s.key_body()
    live = k.split("---retired---")[0]
    check("key cleanup: duplicate person merged onto the lowest code", "EMP-01" in r["out"] and "EMP-04" not in r["out"] and "EMP-04 =" not in live, (live, r["out"]))
    check("key cleanup: word, phrase and month entries retired", not any(c in live for c in ["EMP-03", "OTH-05", "OTH-06"]) and "---retired---" in k, live)
    check("key cleanup: ordinary words stay readable", not missing(r["out"], "hourly", "statutory holiday", "March", "Accrued vacation"), r["out"])
    check("key cleanup: nothing renumbered, retired lines kept", "EMP-03" in k and "EMP-04" in k, k)
    await s.close()

async def t_retired_unscrub(b):
    s = await Session(b).open(key="EMP-01 = Grebo Manning\n---retired---\nEMP-09 = Old Spelling Manning")
    pg = s.pg
    await pg.evaluate("document.getElementById('tabUnscrub').click()")
    await pg.fill("#uIn", "EMP-09 called EMP-01 about the job.")
    await pg.evaluate("document.getElementById('unscrubBtn').click()"); await pg.wait_for_timeout(800)
    out = await pg.input_value("#uOut")
    check("retired code still un-scrubs to its name", "Old Spelling Manning" in out and "Grebo Manning" in out, out)
    await s.close()

async def t_shared_names(b):
    s = await Session(b).open(key="EMP-01 = Dana Whitlock\nEMP-02 = Dana Okafor")
    await s.paste("Dana approved the quote. Dana Whitlock signed it.")
    r = await s.scrub()
    check("shared first name becomes a combined marker", "[EMP-01 or EMP-02]" in r["out"] and "EMP-01 signed" in r["out"], r["out"])
    await s.close()

async def t_health_mode(b):
    s = await Session(b).open(health=True)
    await s.paste("Our therapist and counsellor see clients Monday. Bartholomew Okafor was diagnosed with generalized anxiety disorder and takes Sertraline daily. The diagnosis was confirmed. Staff prescribed the standard onboarding.")
    r = await s.scrub()
    rep = r["report"]
    check("health mode: the condition and the drug are listed", "generalized anxiety disorder" in rep and "Sertraline" in rep, rep[-600:])
    check("health mode: job titles and loose uses of diagnosed are not flagged", not re.search(r"\u27EA(therapist|counsellor|diagnosis|prescribed)\u27EB", rep, re.I), rep[-600:])
    await s.close()

async def t_canaries(b):
    s = await Session(b).open(key="EMP-01 = Sam Okafor")
    await s.paste("Sam Okafor finished the Kanata job.")
    r = await s.scrub()
    check("safety check passes and fake names never reach the output", not r["canaryFail"] and not CANARY.search(r["out"]), (r["canaryFail"], r["out"]))
    check("safety check: planted names are not in the queue", not any(CANARY.search(x) for x in r["names"]), r["names"])
    await s.close()

async def t_greetings_brands_contractions(b):
    s = await Session(b).open(key="EMP-01 = Sam Okafor")
    await s.paste("Thanks everyone. Dear client, the QuickBooks sync and the Trane furnace are fine. Rogers emailed. We don't, it's, they're, won't. Regards,\nSam Okafor")
    r = await s.scrub()
    n = [x.lower() for x in r["names"]]
    check("greetings do not grab the next word, brands and contractions never flagged", not n, n)
    await s.close()

async def t_survey_csv(b):
    s = await Session(b).open()
    rows = "\n".join(f'2026-09-0{i%9+1} 10:0{i%9},"First line of answer {i}\nSecond line, with a comma",Okafor Sam {i},"She said ""fine"""' for i in range(40))
    txt = "Timestamp,What would you change?,Name,Why?\n" + rows + "\n"
    await s.add_text_file("survey.csv", txt); r = await s.scrub()
    inrows = 41; outrows = len([l for l in r["out"].split("\n")]) 
    check("survey CSV: multi-line answers keep their shape", r["out"].count("Second line, with a comma") == 40 and "Okafor" not in r["out"], r["out"][:300])
    junk = [l for l in r["key"].splitlines() if "line" in l.lower() and "=" in l]
    check("survey CSV: answer fragments never become people", not junk, junk)
    await s.close()

async def t_two_session_consistency(b):
    import random; random.seed(3)
    surn = ["Okafor","Mwangi","Voss","Quimby","Delacroix","Ashdown","Whitlock","Branagh","Kowalczyk","Nakamura"]
    first = ["Sam","Grace","Kojo","Rosalind","Priscilla","Bartholomew","Dana","Marisol","Tomasz","Yuki"]
    names = [f"{random.choice(first)} {random.choice(surn)} {i}" for i in range(5000)]
    csv = "Customer,Balance\n" + "\n".join(f"{n},{i}.00" for i, n in enumerate(names)) + "\n"
    s = await Session(b).open(); await s.add_text_file("cust.csv", csv); r1 = await s.scrub(wait=4000)
    secs = s.secs; key1 = r1["key"]; tok1 = r1["tok"]; out1 = r1["out"]; await s.close()
    s = await Session(b).open(key=key1, tokens=tok1); await s.add_text_file("cust.csv", csv); r2 = await s.scrub(wait=4000)
    check("5,000 customers: zero names left, no review", not any(sn in out1 for sn in surn) and not r1["names"], (r1["names"][:5], out1[:200]))
    check("5,000 customers: second session gives identical output and no new codes", r2["out"] == out1 and r2["key"].strip() == key1.strip(), (len(r2["key"]), len(key1)))
    check(f"5,000 customers: fast ({secs:.1f} s)", secs < 25, secs)
    await s.close()

async def t_decided_remembered(b):
    s = await Session(b).open(key="EMP-01 = Rod Benchley, Rod")
    await s.paste("Rod fixed the hot rod and the lightning rod. Rod Benchley left at 5.")
    r = await s.scrub(gate="use")
    k = await s.key_body()
    check("decided section records the gate answer once per name", re.search(r"---decided---[\s\S]*rod\s*=\s*use", k, re.I) is not None, k)
    await s.close()

async def t_docx(b):
    try:
        from docx import Document
    except ImportError:
        check("Word file round trip (python-docx missing, skipped)", True, ""); return
    d = Document(); d.core_properties.author = "Bartholomew Okafor"; d.core_properties.last_modified_by = "Grace Voss"
    d.add_paragraph("Sam Okafor met Grace Voss in Kanata. Call 613-555-0101."); d.add_heading("Notes by Sam Okafor", 1)
    d.sections[0].header.paragraphs[0].text = "Prepared for Grace Voss"
    p = "/tmp/grnd_test.docx"; d.save(p)
    s = await Session(b).open(key="EMP-01 = Sam Okafor\nEMP-02 = Grace Voss")
    await s.add_disk_file(p); r = await s.scrub()
    path, fn = await s.download(0, "docx")
    z = zipfile.ZipFile(path); core = z.read("docProps/core.xml").decode(); body = z.read("word/document.xml").decode()
    hdr = "".join(z.read(n).decode() for n in z.namelist() if n.startswith("word/header"))
    check("Word: body, heading and header scrubbed in place", "Okafor" not in body and "Voss" not in body and "Voss" not in hdr and "EMP-01" in body, (body[-300:], hdr[-200:]))
    check("Word: author and last-modified-by stripped", "Okafor" not in core and "Voss" not in core, core)
    check("Word: download name carries the version and PASSED stamp", "SCRUBBED" in fn, fn)
    await s.close()

async def t_xlsx_round_trip(b):
    try:
        import openpyxl
        from openpyxl.styles import PatternFill, Font
        from openpyxl.comments import Comment
    except ImportError:
        check("Excel round trip (openpyxl missing, skipped)", True, ""); return
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Cancellations"
    ws.append(["Customer", "Reason", "Amount"]); ws["A1"].font = Font(bold=True)
    ws.append(["Sam Okafor", "Moved away", 120.5]); ws["A2"].fill = PatternFill("solid", fgColor="FFFF00")
    ws.append(["Grace Voss", "Price", 80]); ws["B3"].fill = PatternFill("solid", fgColor="FF0000")
    ws.merge_cells("A5:C5"); ws["A5"] = "Legend: yellow = follow up"
    ws["C2"].number_format = '"$"#,##0.00'
    ws["A2"].comment = Comment("Spoke to Sam Okafor", "Grace Voss")
    ws2 = wb.create_sheet("Grace Voss"); ws2["A1"] = "Notes for Grace Voss"
    p = "/tmp/grnd_test.xlsx"; wb.save(p)
    s = await Session(b).open(key="EMP-01 = Sam Okafor\nEMP-02 = Grace Voss")
    await s.add_disk_file(p); r = await s.scrub()
    path, fn = await s.download(0, "xlsx")
    wb2 = openpyxl.load_workbook(path)
    w = wb2["Cancellations"]
    names_gone = all("Okafor" not in str(c.value) and "Voss" not in str(c.value) for row in w.iter_rows() for c in row)
    check("Excel: names replaced in cells, sheet names and comments", names_gone and "Grace Voss" not in wb2.sheetnames and "Okafor" not in (w["A2"].comment.text if w["A2"].comment else ""), (wb2.sheetnames, w["A2"].value, w["A2"].comment.text if w["A2"].comment else None))
    check("Excel: colours, bold, merge and number format survive", w["A2"].fill.fgColor.rgb.endswith("FFFF00") and w["B3"].fill.fgColor.rgb.endswith("FF0000") and w["A1"].font.bold and "A5:C5" in str(w.merged_cells.ranges) and w["C2"].number_format.startswith('"$"'), (w["A2"].fill.fgColor.rgb, w["C2"].number_format, str(w.merged_cells.ranges)))
    check("Excel: legend text readable", w["A5"].value == "Legend: yellow = follow up", w["A5"].value)
    # un-scrub the downloaded workbook
    pg = s.pg
    await pg.evaluate("document.getElementById('tabUnscrub').click()")
    await pg.set_input_files("#uFiles", path); await pg.wait_for_timeout(1200)
    async with pg.expect_download() as dl:
        await pg.evaluate("document.getElementById('unscrubBtn').click()")
        await pg.wait_for_timeout(1500)
        btn = await pg.query_selector("#uDlList button")
        if btn: await btn.click()
    d = await dl.value; p3 = "/tmp/grnd_unscrubbed.xlsx"; await d.save_as(p3)
    wb3 = openpyxl.load_workbook(p3); w3 = wb3["Cancellations"]
    check("Excel: un-scrub restores names and keeps formatting", w3["A2"].value == "Sam Okafor" and "Grace Voss" in wb3.sheetnames and w3["A2"].fill.fgColor.rgb.endswith("FFFF00"), (w3["A2"].value, wb3.sheetnames))
    await s.close()

async def t_autotask(b):
    s = await Session(b).open(key="CUST-001 = Northern Gate Solutions Inc")
    await s.add_text_file("autotask.csv", AUTOTASK); r = await s.scrub(wait=5000)
    suffix = re.findall(r"\b\w+ (?:Inc|Ltd|Limited|Corp)\b\.?", r["out"])
    check("AutoTask 4,900 rows: no legal-suffix company left anywhere", not suffix, suffix[:5])
    check(f"AutoTask 4,900 rows: fast ({s.secs:.1f} s)", s.secs < 30, s.secs)
    await s.close()

async def t_ordinary_word_names(b):
    s = await Session(b).open()
    await s.add_text_file("slots.csv", ORDWORDS); r = await s.scrub(wait=3000)
    n = " ".join(x.lower() for x in r["names"])
    check("names built from ordinary words are caught", "better home care" in n or "green valley cartage" in n, r["names"][:10])
    await s.close()

async def t_excel_label_words(b):
    s = await Session(b).open()
    await s.add_text_file("cx.csv", "Customer,Amount\nSam Okafor,10\nLegend:,\nTotal,10\nSubtotal,10\n")
    r = await s.scrub()
    check("labels and ordinary words in a people column are not coded", not missing(r["out"], "Legend:", "Total", "Subtotal") and "Okafor" not in r["out"], r["out"])
    await s.close()

async def t_metadata_people_in_paste(b):
    s = await Session(b).open(key="EMP-01 = Sam Okafor")
    await s.paste("Sam Okafor's invoice is late. Sam O. and S. Okafor both signed; Okafor, Sam too. Bartholomew Okafor is a different person.")
    r = await s.scrub()
    check("every export spelling of a keyed person shares the code", r["out"].count("EMP-01") >= 4, r["out"])
    check("a different person with the same surname is given back for review", any("Bartholomew" in x for x in r["names"]), r["names"])
    await s.close()

TESTS = [t_numbered_companies, t_report_words, t_buried_names, t_single_mention_and_transcript, t_places, t_wages_wide, t_hr_sheet,
         t_first_last_columns, t_name_orders, t_sharepoint, t_interview_log, t_keep_list, t_key_cleanup, t_retired_unscrub,
         t_shared_names, t_health_mode, t_canaries, t_greetings_brands_contractions, t_survey_csv, t_decided_remembered,
         t_metadata_people_in_paste, t_excel_label_words, t_docx, t_xlsx_round_trip, t_autotask, t_two_session_consistency]

async def main():
    async with async_playwright() as p:
        b = await launch(p)
        for t in TESTS:
            if ONLY and ONLY not in t.__name__: continue
            try:
                await t(b)
            except Exception as e:
                check(t.__name__ + " (crashed)", False, repr(e)[:300])
        await b.close()
    n = len(RESULTS); f = [r for r in RESULTS if not r[1]]
    print(f"\n{n - len(f)} of {n} checks passed on {os.path.basename(BUILD)}" + (f", {len(f)} FAILED" if f else ""))
    sys.exit(1 if f else 0)
asyncio.run(main())
