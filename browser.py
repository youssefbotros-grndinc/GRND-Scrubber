# shared launcher: uses the Chromium that Playwright installed, or the one named in GRND_CHROME
import os
def launch(p, **kw):
    exe = os.environ.get("GRND_CHROME")
    args = ["--no-sandbox", "--disable-gpu"]
    if exe: args += ["--no-zygote"]
    return p.chromium.launch(executable_path=exe, args=args, **kw) if exe else p.chromium.launch(args=args, **kw)
