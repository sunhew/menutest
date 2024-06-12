from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "starbucks"
filename = f"{folder_path}/menustarbucks_{current_date}.json"

# 폴더 생성
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# 웹드라이브 설치
options = ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
service = ChromeService(executable_path=ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=options)

# 첫 번째 페이지에서 데이터 추출
browser.get("https://www.starbucks.co.kr/menu/drink_list.do")
WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "product_espresso"))
)
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 데이터 추출
coffee_data = []
tracks = soup.select(".product_list dl dd ul li")

for track in tracks:
    title = track.select_one("dd").text.strip()
    image_url = track.select_one("dt a img").get('src')
    product_cd = track.select_one("dt a").get('prod')
    detail_url = f"https://www.starbucks.co.kr/menu/drink_view.do?product_cd={product_cd}"
    
    # 두 번째 페이지에서 상세 정보 추출
    browser.get(detail_url)
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product_view_detail"))
    )
    detail_page_source = browser.page_source
    detail_soup = BeautifulSoup(detail_page_source, 'html.parser')

    titleE = detail_soup.select_one(".myAssignZone span").text.strip()
    desction = detail_soup.select_one(".t1").text.strip() if detail_soup.select_one(".t1") else "No Description"
    information = {}
    for row in detail_soup.select(".product_view_info ul li"):
        key = row.select_one("dt").text.strip()
        value = row.select_one("dd").text.strip()
        information[key] = value

    coffee_data.append({
        "brand": "스타벅스",
        "title": title,
        "titleE": titleE,
        "imageURL": image_url,
        "desction": desction,
        "information": information,
        "address": detail_url
    })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()

print(f"Data successfully saved to {filename}")
