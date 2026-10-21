"""Names that are also words: the sentence decides. Usage: python3 ctx_names.py BUILD.html"""
import asyncio, os, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser import launch
BUILD = sys.argv[1]
KEY = "EMP-01 = Matthew Okafor, Matt\nEMP-02 = Mark Ashdown\nEMP-03 = Bill Quimby\nEMP-04 = Grace Voss\nEMP-06 = Will Branagh, Will\nCUST-01 = Hope Delacroix, Hope\nEMP-07 = Chase Fields, Chase\nEMP-08 = Art Blakely, Art"
# (engine, text, fragments that must be gone = person, fragments that must stay = word)
CASES = [
 ("prose", "Mark Ashdown signed. Mark is the lead on it.", ["Mark Ashdown", "Mark is"], []),
 ("prose", "Mark it done and mark the invoices paid. Please mark them.", [], ["Mark it", "mark the", "mark them"]),
 ("prose", "Bill them on Friday. Bill called twice. The bill is due. Bill of lading attached. Bill To: Acme.", ["Bill called"], ["Bill them", "The bill", "Bill of lading", "Bill To"]),
 ("prose", "Will you send it? Will do. Will Branagh is in. Will, can you cover?", ["Will Branagh", "Will, can"], ["Will you", "Will do"]),
 ("prose", "Hope to see you. Hope everything is fine. Hope is here. I hope so.", ["Hope is here"], ["Hope to", "Hope everything", "I hope"]),
 ("prose", "Grace period ends Friday; the grace period was 30 days. Grace handled the desk. Grace Voss left.", ["Grace handled", "Grace Voss"], ["Grace period", "grace period"]),
 ("prose", "Chase the invoices today. Chase called about the van. We chase them monthly.", ["Chase called"], ["Chase the", "chase them"]),
 ("prose", "Art supplies were ordered; the art class is Tuesday. Art Blakely called. Thanks Art.", ["Art Blakely", "Thanks Art"], ["Art supplies", "art class"]),
 ("prose", "Spoke to Mark re furnace. Mark as paid. With Mark and Grace at 9. Mark's truck. The mark on the wall.", ["to Mark", "With Mark", "and Grace", "Mark's truck"], ["Mark as paid", "The mark"]),
 ("prose", "A new Matt on the floor. Matt Okafor and Matt are here. Matt?", ["Matt Okafor", "and Matt", "Matt?"], ["new Matt"]),
 ("convo", "Youssef  0:01\ni asked matt to cover, matt called back. the matt on the floor is wet. ok matt, can you do it? yeah matt.", ["asked matt", "matt called", "matt, can", "yeah matt"], ["the matt on the floor"]),
 ("convo", "Dana  0:02\nwe will see, it will be fine. Will called. will do. Will is coming. hope so. Hope is coming too. a hope and a prayer.", ["Will called", "Will is coming", "Hope is coming"], ["we will", "it will", "will do", "hope so", "a hope"]),
 ("convo", "Matt  0:03\nSo mark it done, bill them, chase the parts, art supplies are in. Mark Ashdown says hi. Mark says hi. Bill is off.", ["Mark Ashdown", "Mark says", "Bill is off"], ["mark it", "bill them", "chase the", "art supplies"]),
 ("records", "Customer,Notes\nAcme,Spoke to Mark re furnace\nBeta,Mark as paid\nGamma,Bill To Acme\nDelta,Grace period 30 days\n", ["to Mark"], ["Mark as paid", "Bill To", "Grace period"]),
]
async def main():
    fails = 0
    async with async_playwright() as p:
        b = await launch(p)
        for eng, text, gone, stay in CASES:
            pg = await b.new_page(); await pg.goto("file://" + os.path.abspath(BUILD)); await pg.wait_for_timeout(500)
            await pg.fill("#pClient", "Acme Heating"); await pg.fill("#keyBox", KEY)
            if eng == "records":
                await pg.evaluate("(t)=>{ window.__fq().push({name:'n.csv',kind:'csv',text:t}); window.__renderFL(); }", text)
            else:
                await pg.fill("#inBox", text); await pg.select_option("#pasteCt", eng)
            await pg.evaluate("document.getElementById('scrubBtn').click()"); await pg.wait_for_timeout(2500)
            for _ in range(3):
                if await pg.query_selector("#riskyGo"):
                    await pg.eval_on_selector_all("input[data-risky]", "e=>e.forEach(c=>c.checked=true)"); await pg.evaluate("document.getElementById('riskyGo').click()"); await pg.wait_for_timeout(1200)
            out = await pg.input_value("#outBox")
            ctx = await pg.evaluate("window.__ctxCount || 0")
            bad = [g for g in gone if g.lower() in out.lower()] + ["KEPT? " + s for s in stay if s.lower() not in out.lower()]
            if ctx: bad.append(f"{ctx} decisions demanded")
            fails += bool(bad)
            print(("PASS " if not bad else "FAIL ") + eng + ": " + text[:60].replace("\n", " ") + ("" if not bad else "  <- " + str(bad) + " | " + out.replace("\n", " ")[:160]))
            await pg.close()
        await b.close()
    print(f"{len(CASES) - fails} of {len(CASES)} passed on {os.path.basename(BUILD)}"); sys.exit(1 if fails else 0)
asyncio.run(main())
