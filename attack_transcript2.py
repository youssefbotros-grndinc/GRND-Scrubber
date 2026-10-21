import asyncio, os, sys, re
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser import launch
BUILD = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
TXT = open(os.path.join(HERE, "..", "9 Attack transcript 2 (authors, products, typos, labels).txt"), encoding="utf-8").read()
KEY = "EMP-01 = Sam Okafor\nEMP-02 = Will Branagh, Will\nEMP-03 = Matthew Voss, Matt\nOTH-01 = Youssef Botros"
NOT_QUEUE = ["James Clear", "Gino Wickman", "Dan Martell", "Donald Miller", "ThinkPad", "MacBook", "Latitude", "Tagalog", "Punjabi", "Filipino", "unbillable", "non-billable", "rebooked", "recieve", "untill", "definately", "seperate", "Unknown Speaker", "Unknown", "Speaker 2", "Hydro One", "F-150", "Sprinter", "Atomic Habits", "Traction", "StoryBrand"]
MUST_QUEUE = ["Williams", "Matthews", "okafur"]
async def main():
    async with async_playwright() as p:
        b = await launch(p); pg = await b.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://" + os.path.abspath(BUILD)); await pg.wait_for_timeout(600)
        await pg.fill("#pClient", "Acme Heating"); await pg.fill("#keyBox", KEY); await pg.fill("#inBox", TXT); await pg.select_option("#pasteCt", "convo")
        await pg.evaluate("document.getElementById('scrubBtn').click()"); await pg.wait_for_timeout(2500)
        for _ in range(3):
            if await pg.query_selector("#riskyGo"):
                await pg.eval_on_selector_all("input[data-risky]", "e=>e.forEach(c=>c.checked=true)"); await pg.evaluate("document.getElementById('riskyGo').click()"); await pg.wait_for_timeout(1500)
        await pg.wait_for_timeout(1000)
        out = await pg.input_value("#outBox")
        cands = [c for c in await pg.evaluate("window.__lastCands.map(x=>x.name)") if not re.search(r"Fernwhistle|Krellvane|Quorbel|Vexqar|quimbervex", c)]
        low = [c.lower() for c in cands]
        wrong = [n for n in NOT_QUEUE if n.lower() in low]
        missed = [n for n in MUST_QUEUE if not any(n.lower() in c for c in low)]
        print("queue:", cands)
        print(f"should not be in the queue but are (0): {len(wrong)} {wrong}")
        print(f"real names missed by the queue (0): {len(missed)} {missed}")
        print("Williams coded as Will (should be False):", "EMP-02 from" in out, "| Matthews coded as Matt:", "EMP-03 too" in out)
        print("key people replaced:", "Sam Okafor" not in out and "Youssef" not in out)
        print("errors:", errs)
        await b.close()
asyncio.run(main())
