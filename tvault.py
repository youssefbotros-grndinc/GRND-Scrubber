import asyncio,os,json,time
from playwright.async_api import async_playwright
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser import launch
APP="file://"+os.path.abspath(sys.argv[1] if len(sys.argv)>1 else "v710.html")
KEY_A="SIT-01 = Dana Whitlock, Dana\nBA-02 = Bill Quimby, Bill"
KEY_B="EMP-01 = Kojo Mwangi\nEMP-02 = Rosalind Quimby, Roz"
async def gates(pg):
    for _ in range(3):
        if await pg.query_selector("#riskyGo"):
            await pg.eval_on_selector_all("input[data-risky]","e=>e.forEach(c=>c.checked=true)"); await pg.evaluate("document.getElementById('riskyGo').click()"); await pg.wait_for_timeout(1200)
async def main():
    async with async_playwright() as p:
        b=await launch(p); pg=await b.new_page(accept_downloads=True); errs=[]
        pg.on("pageerror",lambda e: errs.append(str(e)))
        pg.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
        await pg.goto(APP)
        # a fake file handle so headless Chromium can "write back"
        await pg.evaluate("""() => { window.__disk = ''; window.__vaultDebug.setHandle({ createWritable: () => Promise.resolve({ write: (t) => { window.__disk = t; return Promise.resolve(); }, close: () => Promise.resolve() }) }); window.__vaultDebug.load(JSON.stringify({format:'grnd-vault-1', created:'', updated:'', clients:[]}), 'test.grndvault'); }""")
        # add client A with key A
        await pg.fill("#pClient","Acme Plumbing"); await pg.fill("#keyBox",KEY_A); await pg.fill("#pLoc","Kanata")
        await pg.evaluate("document.getElementById('vAddClient').click()"); await pg.wait_for_timeout(300)
        await pg.fill("#vNewPw","correct horse battery staple"); await pg.fill("#vNewPw2","correct horse battery staple")
        await pg.evaluate("document.getElementById('vNewGo').click()"); await pg.wait_for_timeout(2500)
        rc=await pg.evaluate("(document.querySelector('#vaultDialog div[style*=monospace]')||{}).textContent||''")
        print("a) recovery code shown once:", len(rc.replace('-',''))==30, rc[:11]+"…")
        await pg.evaluate("document.getElementById('vRcDone').click()")
        disk1=await pg.evaluate("window.__disk"); v1=json.loads(disk1)
        print("b) vault written, key encrypted (no plaintext names):", v1["clients"][0]["name"]=="Acme Plumbing" and "Whitlock" not in disk1 and "Kanata" not in disk1)
        # add client B with a different password
        await pg.evaluate("window.__vaultDebug.lock('')"); await pg.wait_for_timeout(200)
        await pg.fill("#pClient","Beta Clinic"); await pg.fill("#keyBox",KEY_B)
        await pg.evaluate("document.getElementById('vAddClient').click()"); await pg.wait_for_timeout(300)
        await pg.fill("#vNewPw","another-strong-password-9"); await pg.fill("#vNewPw2","another-strong-password-9")
        await pg.evaluate("document.getElementById('vNewGo').click()"); await pg.wait_for_timeout(2500)
        await pg.evaluate("document.getElementById('vRcDone').click()")
        disk2=await pg.evaluate("window.__disk"); v2=json.loads(disk2)
        print("c) two clients listed by name:", [c["name"] for c in v2["clients"]])
        # lock, "reopen" the vault from disk in a fresh page (simulates a new day)
        pg2=await b.new_page(accept_downloads=True); pg2.on("pageerror",lambda e: errs.append(str(e))); pg2.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
        await pg2.goto(APP)
        await pg2.evaluate("(t)=>{ window.__disk=t; window.__vaultDebug.setHandle({ createWritable: () => Promise.resolve({ write: (x) => { window.__disk = x; return Promise.resolve(); }, close: () => Promise.resolve() }) }); window.__vaultDebug.load(t,'test.grndvault'); }", disk2)
        names=await pg2.evaluate("[...document.querySelectorAll('#vClient option')].map(o=>o.textContent)")
        print("d) dropdown on open:", names, "| key box empty before unlock:", (await pg2.input_value("#keyBox"))=="")
        idA=v2["clients"][0]["id"]
        await pg2.select_option("#vClient", idA); await pg2.fill("#vPass","wrong password here!!")
        await pg2.evaluate("document.getElementById('vaultForm').requestSubmit()"); await pg2.wait_for_timeout(2500)
        print("e) wrong password refused:", "did not open" in (await pg2.inner_text("#vaultStatus")), "| key still empty:", (await pg2.input_value("#keyBox"))=="")
        await pg2.fill("#vPass","correct horse battery staple"); await pg2.evaluate("document.getElementById('vaultForm').requestSubmit()"); await pg2.wait_for_timeout(2500)
        kb=await pg2.input_value("#keyBox"); loc=await pg2.input_value("#pLoc"); cl=await pg2.input_value("#pClient")
        print("f) right password restores key, location, client exactly:", kb.strip()==KEY_A and loc.strip()=="Kanata" and cl.startswith("Acme Plumbing"), "| password field cleared:", (await pg2.input_value("#vPass"))=="")
        # scrub something that adds a code -> auto-save creates a version
        await pg2.fill("#inBox","Bartholomew Okafor called Dana."); await pg2.evaluate("document.getElementById('scrubBtn').click()"); await pg2.wait_for_timeout(2500); await gates(pg2)
        await pg2.evaluate("document.querySelectorAll('#leftover input.candCk').forEach(c=>c.checked=true); document.getElementById('applyLeft').click()"); await pg2.wait_for_timeout(3500)
        v3=json.loads(await pg2.evaluate("window.__disk")); cA=[c for c in v3["clients"] if c["id"]==idA][0]
        print("g) auto-saved after coding a name: versions kept =", len(cA["versions"]), "| unsaved flag:", await pg2.evaluate("!!window.__keyUnsaved"), "| status:", (await pg2.inner_text("#vaultStatus"))[:60])
        print("   downloads unlocked:", await pg2.evaluate("[...document.querySelectorAll('#dlList button')].every(b=>!b.disabled)"))
        # restore the earlier version
        await pg2.select_option("#vVersions","0"); await pg2.evaluate("document.getElementById('vRestore').click()"); await pg2.wait_for_timeout(2500)
        print("h) restore brings the first version back:", (await pg2.input_value("#keyBox")).strip()==KEY_A, "| versions now:", len([c for c in json.loads(await pg2.evaluate("window.__disk"))["clients"] if c["id"]==idA][0]["versions"]))
        # change password, lock, unlock with the new one
        await pg2.evaluate("document.getElementById('vChangePw').click()"); await pg2.wait_for_timeout(200)
        await pg2.fill("#vCp1","brand new password 2026"); await pg2.fill("#vCp2","brand new password 2026"); await pg2.evaluate("document.getElementById('vCpGo').click()"); await pg2.wait_for_timeout(2000)
        await pg2.evaluate("document.getElementById('vaultLockBtn').click()"); await pg2.wait_for_timeout(300)
        print("i) lock clears the key from the page:", (await pg2.input_value("#keyBox"))=="" and (await pg2.input_value("#outBox"))=="")
        await pg2.select_option("#vClient", idA); await pg2.fill("#vPass","correct horse battery staple"); await pg2.evaluate("document.getElementById('vaultForm').requestSubmit()"); await pg2.wait_for_timeout(2500)
        old_refused="did not open" in (await pg2.inner_text("#vaultStatus"))
        await pg2.fill("#vPass","brand new password 2026"); await pg2.evaluate("document.getElementById('vaultForm').requestSubmit()"); await pg2.wait_for_timeout(2500)
        print("j) old password refused, new one works:", old_refused and (await pg2.input_value("#keyBox")).strip()==KEY_A)
        # recovery code resets the password
        await pg2.evaluate("document.getElementById('vaultLockBtn').click()"); await pg2.wait_for_timeout(300)
        await pg2.select_option("#vClient", idA); await pg2.evaluate("document.getElementById('vReset').click()"); await pg2.wait_for_timeout(200)
        await pg2.fill("#vRcIn", rc.lower()); await pg2.fill("#vRp1","recovered password now 1"); await pg2.fill("#vRp2","recovered password now 1"); await pg2.evaluate("document.getElementById('vRcGo').click()"); await pg2.wait_for_timeout(2500)
        await pg2.fill("#vPass","recovered password now 1"); await pg2.evaluate("document.getElementById('vaultForm').requestSubmit()"); await pg2.wait_for_timeout(2500)
        print("k) recovery code reset works (typed lowercase):", (await pg2.input_value("#keyBox")).strip()==KEY_A)
        # wrong recovery code refused
        await pg2.evaluate("document.getElementById('vaultLockBtn').click()"); await pg2.wait_for_timeout(300)
        await pg2.select_option("#vClient", idA); await pg2.evaluate("document.getElementById('vReset').click()"); await pg2.wait_for_timeout(200)
        await pg2.fill("#vRcIn","AAAAA-BBBBB-CCCCC-DDDDD-EEEEE-FFFFF"); await pg2.fill("#vRp1","should not work at all"); await pg2.fill("#vRp2","should not work at all"); await pg2.evaluate("document.getElementById('vRcGo').click()"); await pg2.wait_for_timeout(2500)
        await pg2.fill("#vPass","should not work at all"); await pg2.evaluate("document.getElementById('vaultForm').requestSubmit()"); await pg2.wait_for_timeout(2500)
        print("l) wrong recovery code changes nothing:", "did not open" in (await pg2.inner_text("#vaultStatus")))
        # client B still opens with its own password, and A's password does not open B
        await pg2.select_option("#vClient", v2["clients"][1]["id"]); await pg2.fill("#vPass","recovered password now 1"); await pg2.evaluate("document.getElementById('vaultForm').requestSubmit()"); await pg2.wait_for_timeout(2500)
        crossed="did not open" in (await pg2.inner_text("#vaultStatus"))
        await pg2.fill("#vPass","another-strong-password-9"); await pg2.evaluate("document.getElementById('vaultForm').requestSubmit()"); await pg2.wait_for_timeout(2500)
        print("m) passwords are per client:", crossed and (await pg2.input_value("#keyBox")).strip()==KEY_B)
        # tampered vault: flip a byte in the ciphertext
        vt=json.loads(await pg2.evaluate("window.__disk")); ct=vt["clients"][1]["current"]["ct"]; vt["clients"][1]["current"]["ct"]=ct[:-6]+("AAAA" if ct[-6:-2]!="AAAA" else "BBBB")+ct[-2:]
        pg3=await b.new_page(); pg3.on("dialog", lambda d: asyncio.ensure_future(d.accept())); await pg3.goto(APP)
        await pg3.evaluate("(t)=>{ window.__vaultDebug.load(t,'t.grndvault'); }", json.dumps(vt))
        await pg3.select_option("#vClient", v2["clients"][1]["id"]); await pg3.fill("#vPass","another-strong-password-9"); await pg3.evaluate("document.getElementById('vaultForm').requestSubmit()"); await pg3.wait_for_timeout(2500)
        print("n) tampered vault refused, nothing loaded:", "did not open" in (await pg3.inner_text("#vaultStatus")) and (await pg3.input_value("#keyBox"))=="")
        # a plain key file still loads the old way with the vault closed
        open("/tmp/plain_key.txt","w").write("GRND Scrubber key v3. Keep this file out of AI tools.\nclient = Gamma\n---people---\nOTH-01 = Lena Krebs\n---tokens---\n")
        pg4=await b.new_page(); await pg4.goto(APP); await pg4.set_input_files("#loadKey","/tmp/plain_key.txt"); await pg4.wait_for_timeout(800)
        print("o) plain key file still loads without a vault:", "Lena Krebs" in (await pg4.input_value("#keyBox")))
        print("errs", errs); await b.close()
asyncio.run(main())
