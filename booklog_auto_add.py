from playwright.sync_api import sync_playwright
import csv
import time

BOOKLOG_URL = "https://booklog.jp/"
LOGIN_URL = "https://booklog.jp/users/sign_in"
COOKIE_FILE = "booklog_cookies.json"
CSV_FILE = "scanned_isbn.csv"  # 1列でISBNを並べる想定

def load_isbns(path):
    isbns = []
    with open(path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                isbns.append(row[0].strip())
    return isbns

def save_cookies(context):
    import json
    cookies = context.cookies()
    with open(COOKIE_FILE, "w") as f:
        json.dump(cookies, f)

def load_cookies(context):
    import json, os
    if not os.path.exists(COOKIE_FILE):
        return False
    with open(COOKIE_FILE) as f:
        cookies = json.load(f)
    context.add_cookies(cookies)
    return True

def ensure_logged_in(page):
    try:
        if page.query_selector("a[href='/logout'], a[href*='logout'], a.my-page, a[href*='mypage'], .user-menu"):
            return True
    except Exception:
        pass
    return False

def add_book_by_isbn(page, isbn):
    page.goto("https://booklog.jp/search")
    page.fill("input[name='q'], input#search-input, input.search-input", isbn)
    page.click("button[type='submit'], input[type='submit'], button.search-button")
    page.wait_for_load_state("networkidle")
    time.sleep(1)
    btn = page.query_selector("a.add-to-shelf, button.add-to-shelf, a[data-add-shelf], button[data-add-shelf]")
    if not btn:
        first = page.query_selector("a.item-title, a[href*='/items/'], div.item a")
        if first:
            first.click()
            page.wait_for_load_state("networkidle")
            btn = page.query_selector("a.add-to-shelf, button.add-to-shelf, a[data-add-shelf], button[data-add-shelf]")
    if btn:
        btn.click()
        page.wait_for_timeout(1000)
        return True
    return False

def main():
    isbns = load_isbns(CSV_FILE)
    if not isbns:
        print("No ISBNs found in", CSV_FILE)
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Try load cookies; if none, open login page for manual login and save cookies
        if not load_cookies(context):
            print("Please log in manually; closing this script will save cookies if you press 's' in console.")
            page.goto(LOGIN_URL)
            page.wait_for_load_state("networkidle")
            input("Log in in the opened browser window, then press Enter here to continue and save cookies...")
            save_cookies(context)

        page.goto(BOOKLOG_URL)
        if not ensure_logged_in(page):
            print("Not logged in after loading cookies. Open the browser and log in manually, then rerun.")
            browser.close()
            return

        for isbn in isbns:
            print("Adding:", isbn)
            ok = add_book_by_isbn(page, isbn)
            print("OK" if ok else "Failed:", isbn)
            time.sleep(1)  # サイト負荷軽減

        browser.close()

if __name__ == "__main__":
    main()
