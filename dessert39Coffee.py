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
folder_path = "dessert39"
filename = f"{folder_path}/menudessert39_{current_date}.json"

# 폴더 경로가 없다면 생성
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# 웹드라이브 설치
options = ChromeOptions()
options.add_argument("--headless")
browser = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), options=options)
browser.get("https://dessert39.com/html/pages/menu_beverage.php")

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "product-container"))
)

# 업데이트된 페이지 소스를 변수에 저장
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 헤드의 타이틀을 가져옴
page_title = soup.head.title.text.strip() if soup.head.title else "No Title"
page_title = page_title.replace(" - 메뉴", "").strip()

# 고정된 주소 설정
address = "https://dessert39.com/"

# 데이터 추출
coffee_data = []
tracks = soup.select("#list_98 .product")

for track in tracks:
    brand = page_title  # 페이지 타이틀을 브랜드로 사용
    title = track.select_one(".product > p.tit").text.strip()
    image_url = track.select_one(".product > .frame > img").get('src')
    desction = track.select_one(".product > p.detail").text.strip()

    coffee_data.append({
        "brand": brand,
        "title": title,
        "imageURL": image_url,
        "desction": desction,
        "address": address
    })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()

print(f"Data successfully saved to {filename}")
