from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com")

    # Wait for a specific element to appear
    page.wait_for_selector("h1")
    print("Page title:", page.title())

    # Wait for a network response
    page.wait_for_response(lambda response: response.url == "https://example.com/api/data" and response.status == 200)
    print("Data loaded")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)