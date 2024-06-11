from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "canbus"
filename = f"{folder_path}/menucanbus_{current_date}.json"

# 웹드라이브 설치
options = ChromeOptions()
options.add_argument("--headless")
browser = webdriver.Chrome(options=options)
browser.get("http://canbus.kr/doc/menu1.php")

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "menuList"))
)

html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 헤드의 타이틀을 가져옴
page_title = soup.head.title.text.strip() if soup.head.title else "No Title"
page_title = page_title.replace(" - 메뉴", "").strip()

# 고정된 주소 설정
address = "http://canbus.kr/doc/menu1.php"

# 데이터 추출
coffee_data = []
tracks = soup.select("#pageWrap > ul > li")

for track in tracks:
    brand = page_title
    title = track.select_one("#pageWrap > ul > li > p").text.strip()    
    image_url = track.select_one("#pageWrap > ul > li > img").get('src').replace('/images', 'http://canbus.kr/images')
    coffee_data.append({
        "brand": brand,
        "title": title,
        "imageURL": image_url,
        "address": address
    })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# # 브라우저 종료
# browser.quit()
