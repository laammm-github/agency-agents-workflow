"""Real loopback browser acceptance; does not prove ChatGPT plugin activation."""
import importlib.util
import json
import tempfile
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("app",ROOT/"tests/fixtures/teaching_app.py");app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
def main():
 with tempfile.TemporaryDirectory() as directory:
  server=app.make_server(Path(directory)/"app.db");thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   with sync_playwright() as p:
    browser=p.chromium.launch(channel="msedge",headless=True)
    try:
     page=browser.new_page();page.goto(f"http://127.0.0.1:{server.server_port}")
     page.get_by_label("Task title").fill("Ship verified feature");page.get_by_role("button",name="Add task").click()
     expect(page.get_by_role("status")).to_have_text("Saved");expect(page.get_by_role("listitem")).to_have_text("Ship verified feature")
     server.fault=True;page.get_by_label("Task title").fill("Must fail");page.get_by_role("button",name="Add task").click()
     expect(page.get_by_role("status")).to_have_text("Save failed")
     (ROOT/"build").mkdir(exist_ok=True);page.screenshot(path=str(ROOT/"build/browser-smoke.png"))
     print(json.dumps({"browser":"Edge","saved":True,"service_failure_visible":True,"scope":"loopback teaching fixture"}))
    finally:browser.close()
  finally:server.shutdown();server.server_close();thread.join()
if __name__=="__main__":main()
