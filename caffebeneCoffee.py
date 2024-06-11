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
folder_path = "caffebene"
filename = f"{folder_path}/menucaffebene_{current_date}.json"

# 폴더 경로가 없다면 생성
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

# 수집할 seq 값 리스트
seq_list = [
    23, 24, 27, 28, 29, 30, 31, 32, 43, 37, 38, 39, 40, 33, 34, 35, 22, 41, 46, 70,
    71, 72, 266, 267, 268, 96, 271, 331, 325, 329, 328, 327, 324, 323, 326, 322,
    321, 397, 398, 418, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 431, 432,
    435, 436, 443, 475, 474, 477, 512, 511, 513
]

# 데이터 추출을 위한 빈 리스트 생성
coffee_data = []

for seq in seq_list:
    # 각 seq 값에 대해 페이지 로드
    url = f"http://www.caffebene.co.kr/menu/menu_view.html?seq={seq}&pg=1&code=001000&scode="
    browser.get(url)

    # 페이지가 완전히 로드될 때까지 대기
    try:
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "menu-detail"))
        )
    except:
        print(f"Skipping seq={seq}, element not found.")
        continue

    # 상세 페이지의 소스를 변수에 저장
    detail_page_source = browser.page_source
    soup = BeautifulSoup(detail_page_source, 'html.parser')

    # 헤드의 타이틀을 가져옴
    page_title = soup.head.title.text.strip() if soup.head.title else "No Title"
    page_title = page_title.replace(" - 메뉴", "").strip()

    # 고정된 주소 설정
    address = url

    # 데이터 추출
    track = soup.select_one(".menu-detail")

    if track:
        title_tag = track.select_one(".static h2")
        title = title_tag.text.strip() if title_tag else ""
        image_url_tag = track.select_one(".menu-detail-view-photo img")
        image_url = image_url_tag.get('src').replace('/uploads', 'http://www.caffebene.co.kr/uploads') if image_url_tag else ""
        desction_tag = track.select_one(".menu-detail-view-info .t1")
        desction = desction_tag.text.strip().replace('\n', ' ').replace('\t', ' ') if desction_tag else ""

        # tbody의 tr 요소들을 가져옴
        nutrition_info = {}
        tbody = track.select_one(".mdv-tb1 tbody")
        if tbody:
            rows = tbody.find_all("tr")
            for row in rows:
                key = row.find("th").text.strip()
                value = row.find("td").text.strip()
                nutrition_info[key] = value

        # 필수 필드가 모두 존재하는 경우에만 데이터 추가
        if title and image_url and desction:
            coffee_data.append({
                "brand": page_title,
                "title": title,
                "imageURL": image_url,
                "desction": desction,
                "information": nutrition_info,
                "address": address
            })
    else:
        print(f"No data found for seq={seq}")

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()

print(f"Data successfully saved to {filename}")
