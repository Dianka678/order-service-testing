import functools
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def main():
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1100})
                base = f"http://127.0.0.1:{server.server_port}"
                page.goto(f"{base}/htmlcov/index.html", wait_until="networkidle")
                page.get_by_role("heading", name="Coverage report", exact=False).wait_for()
                page.screenshot(path=str(ROOT / "docs" / "coverage.png"), full_page=True)
                page.goto(f"{base}/allure-report/index.html", wait_until="networkidle")
                summary = json.loads((ROOT / "allure-report/widgets/summary.json").read_text())
                page.get_by_text(str(summary["statistic"]["total"]), exact=True).first.wait_for()
                page.screenshot(path=str(ROOT / "docs" / "allure.png"), full_page=True)
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    main()
