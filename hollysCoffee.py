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
folder_path = "hollys"
filename = f"{folder_path}/menuhollys_{current_date}.json"

# 웹드라이브 설치
options = ChromeOptions()
options.add_argument("--headless")
browser = webdriver.Chrome(options=options)
browser.get("https://www.hollys.co.kr/menu/espresso.do")

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
    SubTitle = track.select_one("body > .wrap > .contents_wr > .contents > .content > .menu_view01 > .menu_detail > .menu_info").text.strip()
    coffee_data.append({
        "title": title,
        "imageURL": image_url,
        "SubTitle": SubTitle,
    })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# # 브라우저 종료
# browser.quit()
