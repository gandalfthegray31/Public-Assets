#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import requests
import sys
import re

def check_robots_meta(sitemap_url):
    response = requests.get(sitemap_url)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    
    # Handle namespace
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    
    for url_elem in root.findall('.//ns:loc', namespace):
        url = url_elem.text.strip()
        try:
            headers = {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
            response = requests.get(url, headers=headers, timeout=10)
            matches = re.findall(r'meta name="robots" content="[^"]*"', response.text, re.IGNORECASE)
            if matches:
                colored_matches = [match.replace('noindex', '\033[91mnoindex\033[0m') for match in matches]
                print(f"FOUND: {url} - {len(matches)} instances: {colored_matches}")
            else:
                print(f"NOT FOUND: {url}")
        except Exception as e:
            print(f"ERROR: {url} - {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sitemap_robots_checker.py <sitemap_url>")
        sys.exit(1)
    
    check_robots_meta(sys.argv[1])
