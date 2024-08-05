from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com/login")

    # Fill out a login form
    page.fill("#username", "myusername")
    page.fill("#password", "mypassword")
    page.click("button[type=submit]")

    # Wait for navigation after login
    page.wait_for_navigation()
    print("Logged in and navigated to:", page.url())

    browser.close()

with sync_playwright() as playwright:
    run(playwright)