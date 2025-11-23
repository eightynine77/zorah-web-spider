import json
from flask import Flask, request, jsonify, render_template
from bs4 import BeautifulSoup
import requests
import tldextract
from urllib.parse import urljoin
from collections import deque
import logging
import webbrowser
from threading import Timer

# --- IMPORTS TO HANDLE SSL WARNINGS ---
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# --- Suppress only the InsecureRequestWarning ---
urllib3.disable_warnings(InsecureRequestWarning)


# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# --- Python Backend (Flask Server) ---
# This 'app' object is imported by zorah.py
app = Flask(__name__, 
            template_folder='components', 
            static_folder='components')

# --- Frontend Route ---
@app.route('/')
def index():
    """Serves the main index.html file from the 'components' folder."""
    return render_template('index.html')

# --- API Route ---
def get_page_title(soup):
    """Extracts the page title from the parsed HTML (soup)."""
    title = soup.title.string
    if title:
        return title.strip()
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return og_title["content"].strip()
    meta_title = soup.find("meta", attrs={"name": "title"})
    if meta_title and meta_title.get("content"):
        return meta_title["content"].strip()
    return "[no web page title detected]"

@app.route('/crawl', methods=['POST'])
def crawl():
    """The main spider/crawler API endpoint."""
    data = request.get_json()
    start_url = data.get('url')

    if not start_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        start_info = tldextract.extract(start_url)
        base_domain = f"{start_info.domain}.{start_info.suffix}"
        
        if not base_domain:
             return jsonify({"error": "Could not parse a valid domain from the URL"}), 400

        log.info(f"Starting crawl for base domain: {base_domain}")

        urls_to_crawl = deque([start_url])
        visited_urls = set()
        results = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        crawl_limit = 100 

        while urls_to_crawl and len(results) < crawl_limit:
            current_url = urls_to_crawl.popleft()
            if current_url in visited_urls:
                continue
            
            current_url = current_url.split('#')[0]
            
            try:
                current_info = tldextract.extract(current_url)
                current_base_domain = f"{current_info.domain}.{current_info.suffix}"
            except Exception:
                continue 

            if current_base_domain != base_domain or not current_url.startswith('http'):
                continue

            log.info(f"Visiting: {current_url}")
            visited_urls.add(current_url)

            try:
                # Add 'verify=False' to ignore bad SSL certificates
                response = requests.get(current_url, headers=headers, timeout=5, verify=False)
                
                if response.status_code != 200 or 'text/html' not in response.headers.get('Content-Type', ''):
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                title = get_page_title(soup)
                results.append({"url": current_url, "title": title})

                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    new_url = urljoin(current_url, href).split('#')[0]
                    
                    new_info = tldextract.extract(new_url)
                    new_base_domain = f"{new_info.domain}.{new_info.suffix}"

                    if new_base_domain == base_domain and new_url not in visited_urls and new_url.startswith('http'):
                        urls_to_crawl.append(new_url)
            except requests.RequestException as e:
                log.warning(f"Could not crawl {current_url}: {e}")
            except Exception as e:
                log.error(f"An unexpected error occurred at {current_url}: {e}")

        log.info(f"Crawl finished. Found {len(results)} pages.")
        return jsonify(results)

    except Exception as e:
        log.error(f"Crawl failed entirely: {e}")
        return jsonify({"error": str(e)}), 500

# --- Main execution functions ---
def open_browser(url):
    """Opens the web browser to the specified URL."""
    webbrowser.open_new_tab(url)

# This function is called by zorah.py
def start_server():
    from waitress import serve
    host = '127.0.0.1'
    port = 8080
    app_url = f"http://{host}:{port}"
    
    Timer(1, open_browser, args=[app_url]).start()
    
    # Run the server
    serve(app, host=host, port=port)

if __name__ == '__main__':
    # This allows the file to still be run directly
    # (e.g., for testing)
    start_server()