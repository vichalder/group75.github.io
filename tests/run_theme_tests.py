import os
import sys
import time
from playwright.sync_api import sync_playwright, expect

# List of pages to test
PAGES = [
    "index.html",
    "pages/interactive-risk.html",
    "pages/interactive-hourly.html",
    "pages/interactive-heatmap.html",
    "pages/static-crime-ratio.html"
]

def get_file_url(relative_path):
    current_dir = os.getcwd()
    return f"file://{current_dir}/{relative_path}"

def test_page_theme(page, page_path):
    url = get_file_url(page_path)
    print(f"Testing {page_path}...")

    # 1. Load the page
    try:
        page.goto(url, wait_until="commit", timeout=10000)
    except Exception as e:
        print(f"  Warning: Initial load of {page_path} timed out/failed: {e}")

    page.wait_for_selector("#themeToggle", timeout=5000)

    # 2. Clear localStorage
    page.evaluate("localStorage.clear()")
    try:
        page.reload(wait_until="commit", timeout=10000)
    except Exception as e:
        print(f"  Warning: Reload of {page_path} timed out/failed: {e}")
    page.wait_for_selector("#themeToggle", timeout=5000)

    html = page.locator("html")
    theme_toggle = page.locator("#themeToggle")

    # 3. Test Toggle
    theme_toggle.click()
    expect(html).to_have_attribute("data-theme", "light")
    assert page.evaluate("localStorage.getItem('sf-theme')") == "light"
    print(f"  - Toggle to light: PASSED")

    theme_toggle.click()
    expect(html).to_have_attribute("data-theme", "dark")
    assert page.evaluate("localStorage.getItem('sf-theme')") == "dark"
    print(f"  - Toggle to dark: PASSED")

    # 4. Test Persistence
    theme_toggle.click() # Back to light
    expect(html).to_have_attribute("data-theme", "light")
    try:
        page.reload(wait_until="commit", timeout=10000)
    except Exception as e:
        print(f"  Warning: Persistence reload of {page_path} timed out/failed: {e}")
    page.wait_for_selector("#themeToggle", timeout=5000)
    expect(page.locator("html")).to_have_attribute("data-theme", "light")
    print(f"  - Persistence light: PASSED")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Performance optimizations
        page.route("**/*.html", lambda route: route.abort() if "interactive_plots" in route.request.url else route.continue_())
        page.route("**/fonts.googleapis.com/**", lambda route: route.abort())
        page.route("**/fonts.gstatic.com/**", lambda route: route.abort())

        try:
            for page_path in PAGES:
                test_page_theme(page, page_path)
            print("\nAll theme toggle tests passed successfully!")
        except Exception as e:
            print(f"\nTest failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    main()
