import sys
import re
import csv
import time
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

def run(playwright, url, take_screenshot):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto(url)

    if take_screenshot:
        __capture_screenshot(page, url)
    else:
        __save_page_text(page, "main", url)

    browser.close()


def process_url(url, take_screenshot, retries=2, backoff_factor=1):
    for attempt in range(retries + 1):
        try:
            with sync_playwright() as playwright:
                run(playwright, url, take_screenshot)
            break
        except Exception as e:
            if attempt < retries:
                sleep_time = backoff_factor * (2 ** attempt)
                print(f"Error processing URL {url}, retrying in {sleep_time} seconds... ({attempt + 1}/{retries})")
                time.sleep(sleep_time)  # Exponential backoff
            else:
                print(f"Failed to process URL {url} after {retries + 1} attempts: {e}")


def __save_page_text(page, selector, url):
    title = page.title()
    main_content = page.query_selector(selector)
    main_text = (
        main_content.inner_text() if main_content else "No requested selector found"
    )

    filename = __safe_filename_from(title)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"URL: {url}\n")
        f.write(f"Title: {title}\n\n")
        f.write(main_text)

    print(f"Data saved as {filename}")


def __safe_filename_from(title):
    safe_title = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_")
    return f"{safe_title}.txt"


def __capture_screenshot(page, url):
    filename = __safe_filename_from(page.title()) + ".png"
    page.screenshot(path=filename, full_page=True)
    print(f"Screenshot saved as {filename}")


def read_urls_from_csv(file_path):
    urls = []
    with open(file_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            urls.append(row['loc'])
    return urls


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <csv_file> [--screenshot]")
        sys.exit(1)

    csv_file = sys.argv[1]
    take_screenshot = "--screenshot" in sys.argv

    urls = read_urls_from_csv(csv_file)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_url, url, take_screenshot) for url in urls]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error processing URL: {e}")
