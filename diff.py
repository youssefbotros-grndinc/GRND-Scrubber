import asyncio,os,sys,json,random
from playwright.async_api import async_playwright
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser import launch
builds=[sys.argv[1], sys.argv[2]]
random.seed(7)
scen=[]
scen.append(("prose","Findings. Bartholomew Okafor reviewed the Trane furnace with Priscilla. Grace Voss signed the Toyota lease. Thanks everyone. We met Perth in the lobby; Russell called about the invoice. The Barrhaven branch on Elgin Street closed early. 12 Elm Crescent, Kanata, ON K2K 1A1. Call 613-555-0101 or sam.o@example.com.",""))
scen.append(("wages_wide","Item,Total,Biggar-Heil Emily L,Camellato Lauren,Duncan Shayla,Ayyad Zakarias\nRegular,400,10,20,30,40\nOvertime,400,1,2,3,4\nTotal Wages,400,11,22,33,44\n","SIT-03 = Zakarias Ayyad, Zakarias"))
scen.append(("hr","Employee Name,Employee ID,Employee Type,Employment Status,Manager,Contact Email,Contact Phone,Home Address,Regular Hours,Pay Rate\nSam Okafor,10021,Full-time,Active,Bartholomew Mwangi,sam.o@example.com,613-555-0101,12 Elm Street,40,22.50\nBill Quimby,10022,Part-time,Active,Rose Delacroix,bill.q@example.com,(613) 555-0102,88 Oak Avenue,20,24.00\nGrace Voss,10023,Casual,On leave,Mark Ashdown,grace.v@example.com,613.555.0103,7 Pine Crescent,12,21.00\n",""))
scen.append(("ilog","Date,Interviewee,Role,Notes\n"+"\n".join(f"2026-09-{i%28+1:02d},Interview {i},Staff,\"Says nothing changes since the move. Believes nothing paid-for goes unused. Priscilla returned; Still no clear owner.\"" for i in range(20))+"\n",""))
scen.append(("sharepoint","Name,Title,Modified By,Created By,Month,Notes\nReport Jan 1.xlsx,Jan Report,Kojo Mwangi *,Rosalind Quimby,Jan,\"Please review, *Bartholomew Okafor* signed off.\"\n","OTH-050 = Jan\nOTH-051 = Total"))
scen.append(("convo","Youssef Botros  0:03\nSo which store is doing better, Calgary NE or calgary south?\n\nDana Whitlock  0:11\nHonestly Calgary NE. i asked rosalind and Bartholomew about it, justice called me about the deposit and justice wants it friday.\n",""))
scen.append(("health","Our therapist and counsellor see clients Monday. Bartholomew Okafor was diagnosed with generalized anxiety disorder and takes Sertraline daily. She is on medication.",""))
async def run(build):
    out={}
    async with async_playwright() as p:
        b=await launch(p); pg=await b.new_page(); errs=[]
        pg.on("pageerror",lambda e: errs.append(str(e)))
        for name,text,key in scen:
            await pg.goto("file://"+os.path.abspath(build)); await pg.fill("#pClient","Acme")
            if name=="health": await pg.check("#healthMode")
            if key: await pg.fill("#keyBox",key)
            if "," in text.split("\n")[0] and name!="prose" and name!="health" and name!="convo":
                await pg.evaluate("(t)=>{window.__fq().push({name:'f.csv',kind:'csv',text:t}); window.__renderFL();}",text)
            else:
                await pg.fill("#inBox",text)
                if name=="convo": await pg.select_option("#pasteCt","convo")
            await pg.evaluate("document.getElementById('scrubBtn').click()"); await pg.wait_for_timeout(2500)
            for _ in range(3):
                if await pg.query_selector("#riskyGo"):
                    await pg.eval_on_selector_all("input[data-risky]","e=>e.forEach(c=>c.checked=true)"); await pg.evaluate("document.getElementById('riskyGo').click()"); await pg.wait_for_timeout(1200)
            o=await pg.input_value("#outBox"); c=await pg.evaluate("window.__lastCands ? window.__lastCands.map(x=>x.name) : []")
            sens=await pg.evaluate("document.getElementById('sensitive').innerText")
            out[name]={"out":o,"cands":sorted(c),"sens":sens}
        await b.close()
    return out,errs
async def main():
    r1,e1=await run(builds[0]); r2,e2=await run(builds[1])
    same=True
    for k in r1:
        for f in ("out","cands","sens"):
            if r1[k][f]!=r2[k][f]:
                same=False; print("DIFF",k,f); print("  A:",str(r1[k][f])[:300]); print("  B:",str(r2[k][f])[:300])
    print("identical across", len(r1), "scenarios:", same, "| errs:", e1, e2)
    for k in r1: print(" ",k,"cands:",r1[k]["cands"][:8])
asyncio.run(main())
