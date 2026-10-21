"""Health client mode: conditions and drugs flagged, everyday phrases with take/taking not. Usage: python3 health_words.py BUILD.html"""
import asyncio, os, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser import launch
TXT = ("I would also take time outside of those hours to build the tools. Take care of the invoices. We take notes on Fridays and take Uber to site. "
       "Taking Friday off. Take Kanata first. She takes Sertraline daily. He is taking metformin. They prescribed Lisinopril. Takes 20 mg Zorvexa at night. "
       "Was diagnosed with generalized anxiety disorder last year. Take ownership of the schedule.")
FLAG = ["Sertraline", "metformin", "Lisinopril", "Zorvexa", "generalized anxiety disorder"]
NOFLAG = ["take time", "Take care", "take notes", "take Uber", "Taking Friday", "Take Kanata", "Take ownership"]
async def main():
    async with async_playwright() as p:
        b = await launch(p); pg = await b.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://" + os.path.abspath(sys.argv[1])); await pg.wait_for_timeout(600)
        await pg.fill("#pClient", "Acme Clinic"); await pg.check("#healthMode"); await pg.fill("#inBox", TXT)
        await pg.evaluate("document.getElementById('scrubBtn').click()"); await pg.wait_for_timeout(3000)
        for _ in range(3):
            if await pg.query_selector("#riskyGo"):
                await pg.evaluate("document.getElementById('riskyGo').click()"); await pg.wait_for_timeout(1200)
        rep = await pg.evaluate("document.getElementById('report').textContent")
        i = rep.find("Health details mentioned"); block = rep[i:i + 3000] if i >= 0 else ""
        missed = [f for f in FLAG if f not in block]
        wrong = [n for n in NOFLAG if ("\u27EA" + n) in block or (n.split()[1] + "\u27EB") in block]
        print("health flags:", block[:60]); print(f"conditions and drugs missed (0): {len(missed)} {missed}"); print(f"everyday phrases flagged (0): {len(wrong)} {wrong}"); print("errors:", errs)
        await b.close(); sys.exit(1 if missed or wrong or errs else 0)
asyncio.run(main())
