import requests
from bs4 import BeautifulSoup
import time

CATEGORY_URL = "https://ses.cloudmeets.jp/category/ses-list/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}


def get_all_list_urls():
    """カテゴリページから第1弾〜第38弾のURLを収集する"""
    urls = []
    page = 1
    while True:
        url = CATEGORY_URL if page == 1 else f"{CATEGORY_URL}page/{page}/"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            break
        soup = BeautifulSoup(res.text, "html.parser")
        # 記事リンクを抽出（サイト構造に合わせて調整）
        links = soup.select("a[href*='/ses-list/']")
        if not links:
            break
        for a in links:
            href = a["href"]
            if href not in urls:
                urls.append(href)
        # 次ページがなければ終了
        if not soup.select("a.next"):
            break
        page += 1
        time.sleep(1)
    return urls


def scrape_companies_from_page(url):
    """各弾のページから企業名とURLを抽出する"""
    res = requests.get(url, headers=HEADERS, timeout=10)
    if res.status_code != 200:
        return []
    soup = BeautifulSoup(res.text, "html.parser")
    companies = []
    # 企業名はリンク or テキストで記載されていることが多い
    # <a>タグのうち企業サイトへのリンクを抽出
    for a in soup.select("article a[href^='http']"):
        name = a.get_text(strip=True)
        href = a["href"]
        # 自サイトのリンクは除外
        if "cloudmeets.jp" not in href and name:
            companies.append({"企業名": name, "URL": href})
    # リンクなしのテキスト企業名も取得（<li>や<p>タグ内）
    # ※サイト構造によって調整が必要
    return companies


def run_scraping():
    list_urls = get_all_list_urls()
    all_companies = []
    for url in list_urls:
        companies = scrape_companies_from_page(url)
        all_companies.extend(companies)
        time.sleep(1)  # サーバー負荷軽減
    # 重複除去
    seen = set()
    unique = []
    for c in all_companies:
        key = c["企業名"]
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique