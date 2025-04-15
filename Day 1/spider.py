import argparse
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

visited_urls = set()

def parse_args():
    parser = argparse.ArgumentParser(description="Web Spider for downloading images")
    parser.add_argument("url", help="URL of the website to crawl")
    parser.add_argument("-r", action="store_true", help="Enable recursive image download")
    parser.add_argument("-l", type=int, default=5, help="Recursion depth limit (default: 5)")
    parser.add_argument("-p", default="./data", help="Download path (default: ./data)")
    return parser.parse_args()

def fetch_html(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SpiderBot/1.0)"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_image_urls(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    image_urls = []
    for img_tag in soup.find_all("img"):
        src = img_tag.get("src")
        if src:
            full_url = urljoin(base_url, src)
            if full_url.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp")):
                image_urls.append(full_url)
    return image_urls

def download_image(url, path):
    try:
        os.makedirs(path, exist_ok=True)
        filename = os.path.basename(urlparse(url).path)
        if not filename:
            print(f"Skipping invalid URL: {url}")
            return

        filepath = os.path.join(path, filename)

        headers = {"User-Agent": "Mozilla/5.0 (compatible; SpiderBot/1.0)"}
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def spider(url, path, recursive=False, depth=5):
    if url in visited_urls or depth == 0:
        return
    visited_urls.add(url)

    html = fetch_html(url)
    if html is None:
        return

    image_urls = extract_image_urls(html, url)
    for img_url in image_urls:
        download_image(img_url, path)

    if recursive:
        soup = BeautifulSoup(html, "html.parser")
        for link_tag in soup.find_all("a", href=True):
            next_url = urljoin(url, link_tag["href"])
            if urlparse(next_url).netloc == urlparse(url).netloc:
                spider(next_url, path, recursive, depth - 1)

if __name__ == "__main__":
    args = parse_args()
    try:
        spider(args.url, args.p, args.r, args.l)
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user. Exiting gracefully.")