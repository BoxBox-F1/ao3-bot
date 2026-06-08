import requests
import re
import os

def get_ao3_work_id(url):
    pattern = r'/works/(\d+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def download_ao3_epub(url):
    work_id = get_ao3_work_id(url)
    if not work_id:
        raise ValueError("invalid ao3 link")
    
    download_url = f"https://archiveofourown.org/downloads/{work_id}/work.epub"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(download_url, headers=headers)
    
    if response.status_code == 200:
        filename = f"ao3_work_{work_id}.epub"
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    else:
        raise Exception(f"download failed. ao3 might be down or the work is locked.")
