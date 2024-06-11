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
browser = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), options=options)

# seq 값의 범위 설정 (1부터 520까지)
seq_range = range(1, 521)

# 데이터 추출을 위한 빈 리스트 생성
coffee_data = []

for seq in seq_range:
    # 각 seq 값에 대해 페이지 로드
    url = f"http://www.caffebene.co.kr/menu/menu_list.html?code=001000&seq={seq}"
    browser.get(url)
    
    # 페이지가 완전히 로드될 때까지 대기
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "menu-detail"))
        )
    except:
        print(f"Skipping seq={seq}, element not found.")
        continue

    # 업데이트된 페이지 소스를 변수에 저장
    html_source_updated = browser.page_source
    soup = BeautifulSoup(html_source_updated, 'html.parser')

    # 헤드의 타이틀을 가져옴
    page_title = soup.head.title.text.strip() if soup.head.title else "No Title"
    page_title = page_title.replace(" - 메뉴", "").strip()

    # 고정된 주소 설정
    address = url

    # 데이터 추출
    tracks = soup.select(".menu-detail")

    for track in tracks:
        title = track.select_one(".static h2").text.strip()
        image_url = track.select_one(".menu-detail-view-photo img").get('src').replace('/uploads', 'http://www.caffebene.co.kr/uploads')
        desction = track.select_one(".menu-detail-view-info .t1").text.strip()

        # tbody의 tr 요소들을 가져옴
        nutrition_info = {}
        tbody = track.select_one(".mdv-tb1 tbody")
        if tbody:
            rows = tbody.find_all("tr")
            for row in rows:
                key = row.find("th").text.strip()
                value = row.find("td").text.strip()
                nutrition_info[key] = value

        coffee_data.append({
            "brand": page_title,
            "title": title,
            "imageURL": image_url,
            "desction": desction,
            "information": nutrition_info,
            "address": address
        })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()

print(f"Data successfully saved to {filename}")
