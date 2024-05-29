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
from urllib.parse import urljoin

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "hollys"
filename = f"{folder_path}/menuhollys_{current_date}.json"

# 웹드라이브 설치
options = ChromeOptions()
options.add_argument("--headless")
browser = webdriver.Chrome(options=options)
base_url = "https://www.hollys.co.kr/menu/espresso.do"
browser.get(base_url)

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "menu_list01.mar_t_40"))
)

html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 데이터 추출
coffee_data = []
tracks = soup.select("#menuSmallList > li")

for track in tracks:
    title = track.select_one("li > a").text.strip()    
    image_url = track.select_one("li > a > img").get('src')
    
    # 상대 URL을 절대 URL로 변환
    relative_url = track.select_one("li > a").get('href')
    track_url = urljoin(base_url, relative_url)
    browser.get(track_url)
    
    # 페이지가 완전히 로드될 때까지 대기
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "menu_detail"))
    )
    
    detail_html_source = browser.page_source
    detail_soup = BeautifulSoup(detail_html_source, 'html.parser')
    
    # 메뉴 정보가 존재하는지 확인하고 추출
    subTitle_element = detail_soup.select_one("div.menu_detail > div.menu_info > p")
    if subTitle_element:
        subTitle = subTitle_element.text.strip()
    else:
        subTitle = ""
    
    coffee_data.append({
        "title": title,
        "imageURL": image_url,
        "SubTitle": subTitle,
    })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()
