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
import os
import re

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "coffeebay"
filename = f"{folder_path}/menucoffeebay_{current_date}.json"

# 폴더 생성
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# 웹드라이브 설치
options = ChromeOptions()
options.add_argument("--headless")
browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
browser.get("https://www.coffeebay.com/product/prd_menu.php?code=001&idx2=001")

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "list_con"))
)

# 업데이트된 페이지 소스를 변수에 저장
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 헤드의 타이틀을 가져옴
page_title = soup.head.title.text.strip() if soup.head.title else "No Title"

# 데이터 추출
coffee_data = []
tracks = soup.select("#sub_con > div > div > .list_con > div > .list_con > ul > li")

for track in tracks:
    brand = page_title  # 페이지 타이틀을 브랜드로 사용
    title = track.select_one(".list_div .title_con .kor_con span").text.strip()
    en_title = track.select_one(".list_div .title_con .eng_con span").text.strip()
    image_style = track.select_one(".list_div .img_con").get('style')
    image_url = re.search(r'url\((.*?)\)', image_style).group(1).replace("/upload", "https://www.coffeebay.com/upload")
    sub__title = track.select_one(".over_con > .contents_con.w_niceScroll_con > .contents_con.m_niceScroll_con > .info01_con > .intro_con span").text.strip()
    content = track.select_one(".over_con > .contents_con.w_niceScroll_con > .contents_con.m_niceScroll_con > .info02_con > .info_con span").text.strip()

    # 'link', rel='canonical' 부분 수정
    canonical_link = soup.find('link', rel='canonical')
    address = canonical_link['href'].strip() if canonical_link else "No Address"
    
    coffee_data.append({
        "brand": brand,
        "title": title,
        "titleE": en_title,
        "imageURL": image_url,
        "desction": sub__title,
        "information": content,
        "address": address
    })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()
