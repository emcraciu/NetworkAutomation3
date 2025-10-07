import time
import os
from playwright.sync_api import sync_playwright


FTD_URL = "https://192.168.200.40/"
USERNAME = "admin"
PASSWORD = "Cisco@135"
HEADLESS = True
SLOW_MO_MS = 0
WAIT_TIMEOUT = 200000
SCREENSHOT_DIR = "screenshots"

def save_screenshot(page, name):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    path = f"{SCREENSHOT_DIR}/{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"[screenshot] {path}")


def save_page_html(page, name):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    path = f"{SCREENSHOT_DIR}/{name}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(page.content())
    print(f"[html dump] saved: {path}")


def click_text(page, text, timeout=WAIT_TIMEOUT, snap_name=None):
    selector = f"text={text}"
    page.wait_for_selector(selector, timeout=timeout)
    page.click(selector)
    save_screenshot(page, snap_name or f"click_{text.replace(' ', '_')}")
    print(f"[click_text] {text}")
    return True


def wait_and_click_text(page, text, timeout=WAIT_TIMEOUT, snap_name=None):
    """Wait until the button is enabled before clicking."""
    selector = f"text={text}"
    loc = page.locator(selector).first
    page.wait_for_selector(selector, timeout=timeout)

    start = time.time()
    while time.time() - start < (timeout / 1000):
        if loc.is_enabled():
            loc.click()
            save_screenshot(page, snap_name or f"click_{text.replace(' ', '_')}")
            print(f"[wait_and_click_text] {text}")
            return True
        time.sleep(2)

    print(f"[wait_and_click_text] Timeout: {text} remained disabled")
    return False


def try_click_first(page, selectors, timeout=WAIT_TIMEOUT, snap_name=None):
    for sel in selectors:
        el = None
        try:
            el = page.wait_for_selector(sel, timeout=timeout)
        except:
            continue
        if el:
            page.click(sel)
            time.sleep(1)
            save_screenshot(page, snap_name or f"click_{sel.replace(':', '_')}")
            print(f"[click] {sel}")
            return True
    return False

def login(page):
    print("[step] login")
    save_screenshot(page, "before_login")
    save_page_html(page, "after_goto")

    # username
    for sel in ["input[name='username']", "input#username", "input#user", "input[type='text']"]:
        try:
            page.wait_for_selector(sel, timeout=5000)
            page.fill(sel, USERNAME)
            print(f"[found] username field -> {sel}")
            break
        except:
            continue

    # password
    for sel in ["input[name='password']", "input#password", "input[type='password']"]:
        try:
            page.wait_for_selector(sel, timeout=5000)
            page.fill(sel, PASSWORD)
            print(f"[found] password field -> {sel}")
            break
        except:
            continue

    for b in [
        "button:has-text('Log In')",
        "button:has-text('Login')",
        "button:has-text('Sign In')",
        "button[type='submit']",
        "input[type='submit']",
    ]:
        if page.query_selector(b):
            print(f"[found] login button -> {b}")
            page.click(b)
            save_screenshot(page, "after_login_click")
            break

    try:
        page.wait_for_load_state("networkidle", timeout=60000)
    except:
        print("[warn] networkidle not reached, continuing")

    time.sleep(1.5)
    save_screenshot(page, "after_login")
    print("[ok] login flow finished")

def perform_full_wizard(page):
    """Full flow: Next -> Next -> Evaluation -> Pick a Tier -> Recommended -> Finish -> Got it"""
    print("[wizard] full flow")

    # NEXT 1
    wait_and_click_text(page, "Next", timeout=200000, snap_name="after_next1")
    time.sleep(1)

    # NEXT 2
    wait_and_click_text(page, "Next", snap_name="after_next2")
    time.sleep(1)

    # Evaluation license
    if click_text(page, "Continue with evaluation period", snap_name="after_eval_click"):
        time.sleep(1)

    # Pick a Tier dropdown
    if not try_click_first(
            page,
            selectors=[
                "text=Pick a Tier",
                "button:has-text('Pick a Tier')",
                "div[role='combobox']",
                "div[aria-haspopup='listbox']",
                "button[aria-haspopup='listbox']",
                "xpath=//label[contains(.,'Performance Tier')]/following::*[self::div or self::button][1]"
            ],
            timeout=5000,
            snap_name="tier_dropdown_open"
    ):
        print("[warn] could not find the 'Pick a Tier' dropdown")
    time.sleep(1)

    # Select Recommended Tier (or fallback)
    if not try_click_first(
            page,
            selectors=[
                "text=Recommended Tier",
                "li:has-text('Recommended Tier')",
                "div[role='option']:has-text('Recommended Tier')"
            ],
            timeout=5000,
            snap_name="tier_recommended_click"
    ):
        print("[warn] could not find 'Recommended Tier' -> trying fallback...")
        try_click_first(
            page,
            selectors=[
                "li[role='option']",
                "div[role='option']",
                "xpath=(//div[@role='option'] | //li[@role='option'])[1]"
            ],
            timeout=3000,
            snap_name="tier_first_option_click"
        )
    time.sleep(1)

    # FINISH
    if wait_and_click_text(page, "Finish", snap_name="after_finish"):
        time.sleep(2)

    # # GOT IT (optional)
    # if click_text(page, "Got It", timeout=3000, snap_name="after_got_it"):
    #     print("[wizard] got-it clicked")

    save_screenshot(page, "full_wizard_done")
    print("[wizard] completed successfully")


def perform_wizard_steps(page):
    print("[step] wizard flow")
    save_page_html(page, "wizard_before")
    perform_full_wizard(page)


# ============== MAIN ==============
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO_MS)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        print(f"[open] {FTD_URL}")
        try:
            page.goto(FTD_URL, wait_until="domcontentloaded", timeout=60000)
            print("[goto ok]")
            save_page_html(page, "after_goto")
        except Exception as e:
            print("[warn] goto error:", e)
            save_page_html(page, "goto_failed")

        login(page)

        # give extra time for the wizard to fully load
        print("[info] waiting 10 seconds for the wizard to fully load...")
        time.sleep(10)

        perform_wizard_steps(page)

        print("[done] Wizard finished")
        browser.close()


if __name__ == "__main__":
    main()
