import asyncio, os, sys, re
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser import launch
BUILD = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
TXT = open(os.path.join(HERE, "..", "8 Attack transcript (word-like names, celebrities, typos).txt"), encoding="utf-8").read()
KEY = ("EMP-01 = Matthew Okafor, Matt\nEMP-02 = Mark Ashdown\nEMP-03 = Bill Quimby\nEMP-04 = Grace Voss\n"
       "EMP-05 = Dana Whitlock\nEMP-06 = Will Branagh, Will\nCUST-01 = Hope Delacroix, Hope\nOTH-01 = Youssef Botros")

# every mention of a key person that must be replaced (sentence fragments that must not survive in the output)
PERSON = ["Matt called", "asked Matt", "Matt's van", "Thanks Matt", "Did Mark give", "Mark said", "Bill is on vacation", "talk to Bill",
          "Grace handled", "Hope dropped", "Hope's appointment", "Will called", "Will is coming", "thanks Will", "Cheers Dana", "\nMatt  1:02"]
# ordinary uses that must stay readable
WORD = ["mat by the back door", "mark it done", "mark the invoices", "a mark on the wall", "on the bill", "we bill monthly",
        "The bill from", "a grace period", "I hope that", "I hope so", "It will be done", "We will see"]
# the floor mat the transcriber capitalized
THING = ["a Matt on the ground"]
CELEB = ["Auston Matthews", "Wayne Gretzky", "Tom Braidy", "Taylor Swift", "Ryan Reynolds", "Drake", "Justin Trudeau", "Elon Musk",
         "Serena Williams", "lebron james", "Beyonce", "Conor McGregor"]
TYPOS = ["untill", "recieve", "definately", "seperate", "accomodate", "becuase", "thier", "Kinda", "gonna"]
BRANDS = ["Hydro", "Lennox", "Trane", "QuickBooks", "Rogers", "Canada Post", "Leafs", "Raptors"]
NEW_PERSON = ["Priscilla Mwangi"]
MISSPELLED_KEY = ["Dayna", "Okafur"]

async def gates(pg, mode):
    for _ in range(3):
        if await pg.query_selector("#riskyGo"):
            if mode == "use":
                await pg.eval_on_selector_all("input[data-risky]", "e=>e.forEach(c=>c.checked=true)")
            await pg.evaluate("document.getElementById('riskyGo').click()"); await pg.wait_for_timeout(1500)

async def run(mode):
    async with async_playwright() as p:
        b = await launch(p); pg = await b.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://" + os.path.abspath(BUILD)); await pg.wait_for_timeout(800)
        await pg.fill("#pClient", "Acme Heating"); await pg.fill("#keyBox", KEY)
        await pg.fill("#inBox", TXT); await pg.select_option("#pasteCt", "convo")
        await pg.evaluate("document.getElementById('scrubBtn').click()"); await pg.wait_for_timeout(2500)
        await gates(pg, mode)
        await pg.wait_for_timeout(1500)
        out = await pg.input_value("#outBox")
        cands = await pg.evaluate("window.__lastCands ? window.__lastCands.map(x=>x.name) : []")
        cands = [c for c in cands if not re.search(r"Fernwhistle|Krellvane|Quorbel|Vexqar|quimbervex", c)]
        ctx = await pg.evaluate("window.__ctxCount || 0")
        pend = await pg.evaluate("typeof pendingCount==='function' ? pendingCount() : -1")
        await b.close()
    return out, cands, ctx, errs

def report(mode, out, cands, ctx, errs):
    low = out.lower()
    def has(s): return s.lower() in low
    print(f"\n=== gate answered: {mode} ===")
    leaks = [s for s in PERSON if has(s)]
    print(f"key people still readable (should be 0): {len(leaks)}  {leaks}")
    broken = [s for s in WORD if not has(s)]
    print(f"ordinary uses damaged (should be 0): {len(broken)}  {broken}")
    print(f"floor mat replaced as a person (should be 0): {sum(1 for s in THING if not has(s))}")
    cl = [c for c in cands if any(x.lower() in c.lower() or c.lower() in x.lower() for x in CELEB)]
    print(f"celebrities in the queue (should be 0): {len(cl)}  {cl}")
    tq = [c for c in cands if c.lower() in [t.lower() for t in TYPOS]]
    print(f"misspelled ordinary words in the queue (should be 0): {len(tq)}  {tq}")
    bq = [c for c in cands if c.lower() in [t.lower() for t in BRANDS]]
    print(f"brands in the queue (should be 0): {len(bq)}  {bq}")
    kq = [c for c in cands if c.lower() in ["matt","mark","bill","grace","hope","will","dana"]]
    print(f"key names in the queue (should be 0): {len(kq)}  {kq}")
    print(f"spot-by-spot decisions demanded (should be 0): {ctx}")
    npq = [c for c in cands if any(x.lower() in c.lower() for x in NEW_PERSON)]
    print(f"new person caught (should be 1): {len(npq)}  {npq}")
    mq = [c for c in cands if c in MISSPELLED_KEY]
    print(f"misspelled key people flagged for a decision (should be 2): {len(mq)}  {mq}")
    other = [c for c in cands if c not in cl + tq + bq + kq + npq + mq]
    print(f"everything else in the queue: {other}")
    print("errors:", errs)

async def main():
    for mode in ("use", "skip"):
        out, cands, ctx, errs = await run(mode)
        report(mode, out, cands, ctx, errs)
        if "--show" in sys.argv: print(out)
asyncio.run(main())
