import json
import os
import random
import urllib3
import requests
from bs4 import BeautifulSoup
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urljoin

# Suppress SSL certificate verification warnings for NPM requests.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://digitalarchive.npm.gov.tw"
SEARCH_HEADERS = {
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_list(base_url=BASE_URL, total_pages=1200):
    """
    Fetch one random page of painting search results and return all detail links.
    Returns a list of relative href strings (paths to /Collection/Detail/...).
    """
    search_url = f"{base_url}/Collection/Search"
    random_page = random.randint(1, total_pages)
    print(f"[1] Accessing Random Page: {random_page} / {total_pages}")

    payload = {
        "CategoryRegisterType": "'繪畫',",
        "PageInfo": {"PageIndex": random_page, "PageSize": 15, "PageMode": "Grid"}
    }

    print("[1] Fetching search snippet...")
    resp = requests.post(search_url, json=payload, headers=SEARCH_HEADERS, verify=False)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True) if '/Collection/Detail/' in a['href']]
    return links


def get_json(base_url, obj_id, dept):
    """
    Fetch the IIIF manifest JSON for a single object.
    Returns the parsed JSON dict, or None on request/parse failure.
    """
    json_api_url = f"{base_url}/Integrate/GetJson?cid={obj_id}&dept={dept}"
    print(f"[2] Calling JSON API: {json_api_url}")
    try:
        return requests.get(json_api_url, verify=False).json()
    except Exception as e:
        print(f"[!] Error fetching JSON: {e}")
        return None


def parse_json(json_data):
    """
    Extract image URL, label, height and width from an IIIF manifest dict.
    Returns (image_url, label, height, width). image_url is None if no image path is found.
    """
    label = json_data.get('label', 'Unknown')
    image_url = None
    height = None
    width = None

    sequences = json_data.get('sequences', [])
    if sequences:
        canvases = sequences[0].get('canvases', [])
        if canvases:
            print(f"Found {len(canvases)} canvases")
            max_size = 0
            max_canvas = None
            for canvas in canvases:
                canvas_label = canvas.get('label', 'Unknown')
                height = canvas.get('height', 'Unknown')
                width = canvas.get('width', 'Unknown')
                try:
                    size = int(height) * int(width)
                except (ValueError, TypeError):
                    size = 0
                if size > max_size:
                    max_size = size
                    max_canvas = canvas
                print(f"Canvas Label: {canvas_label}, Height: {height}, Width: {width}")
            canvas = max_canvas
            images = canvas.get('images', [])
            if images:
                height = canvas.get('height', 'Unknown')
                width = canvas.get('width', 'Unknown')
                res = images[0].get('resource', {})
                service = res.get('service', {})
                service_id = service.get('@id')

                if service_id:
                    image_url = f"{service_id}/full/max/0/default.jpg"
                else:
                    image_url = res.get('@id')

    print(f"Image URL: {image_url}")
    return (image_url, label, height, width)


def get_random_artifact_data():
    """
    Fetch a random painting and return its data as a dict.
    Returns dict with title, image_url, height, width, label or None on failure.
    """
    links = get_list()
    if not links:
        return None

    link = random.choice(links)
    chosen_index = links.index(link) + 1
    print(f"[+] Chosen link #{chosen_index} (of {len(links)})")
    full_detail_url = urljoin(BASE_URL, link)
    print(f"[+] Selected Artifact: {full_detail_url}")

    params = parse_qs(urlparse(link).query)
    obj_id = params.get('id', [link.split('/')[-1].split('?')[0]])[0]
    dept = params.get('dep', ['P'])[0]

    json_data = get_json(BASE_URL, obj_id, dept)
    if json_data is None:
        return None

    image_url, label, height, width = parse_json(json_data)
    if not image_url:
        return None

    return {
        "cc_title": f"{label} The National Palace Museum, Taipei, CC BY 4.0 @ www.npm.gov.tw",
        "title": label,
        "image_url": image_url,
        "height": height,
        "width": width,
    }


def get_npm_random_image():
    """Fetch a random painting image URL from the National Palace Museum (NPM) digital archive."""
    data = get_random_artifact_data()
    if data:
        print("-" * 50)
        print(f"TITLE: {data['title']}")
        print(f"IMAGE URL: {data['image_url']}")
        print(f"HEIGHT: {data['height']}")
        print(f"WIDTH: {data['width']}")
        print("-" * 50)
        return data["image_url"]
    else:
        print("[-] No artifact data (no links or no image in manifest).")
        return None


class ArtifactHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/random":
            data = get_random_artifact_data()
            if data is None:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Failed to fetch artifact"}).encode("utf-8"))
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        print("[HTTP]", *args)


def run_server(port=None):
    port = port or int(os.environ.get("PORT", 8000))
    server = HTTPServer(("", port), ArtifactHandler)
    print(f"Server at http://localhost:{port}/  (GET / or /random for JSON)")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
