import requests
from bs4 import BeautifulSoup
import time

CATEGORY_URL = "https://ses.cloudmeets.jp/category/ses-list/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}

def get_all_list_urls():
    """カテゴリページから各弾のURLを収集"""
    urls = []
    page = 1
    while True:
        url = CATEGORY_URL if page == 1 else f"{CATEGORY_URL}page/{page}/"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            break
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.select("a[href*='/ses-list/']")
        if not links:
            break
        for a in links:
            href = a["href"]
            if href not in urls:
                urls.append(href)
        if not soup.select("a.next"):
            break
        page += 1
        time.sleep(1)
    return urls

def scrape_companies_from_page(url):
    """1ページから企業名・URLを抽出"""
    res = requests.get(url, headers=HEADERS, timeout=10)
    if res.status_code != 200:
        return []
    soup = BeautifulSoup(res.text, "html.parser")
    companies = []
    for a in soup.select("article a[href^='http']"):
        name = a.get_text(strip=True)
        href = a["href"]
        if "cloudmeets.jp" not in href and name:
            companies.append({"企業名": name, "URL": href})
    return companies

def run_scraping(progress_callback=None):
    """全弾をスクレイピングして企業リストを返す"""
    list_urls = get_all_list_urls()
    all_companies = []
    for i, url in enumerate(list_urls):
        companies = scrape_companies_from_page(url)
        all_companies.extend(companies)
        if progress_callback:
            progress_callback(i + 1, len(list_urls), url)
        time.sleep(1)
    # 重複除去
    seen = set()
    unique = []
    for c in all_companies:
        key = c["企業名"]
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique
