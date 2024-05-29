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
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
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
menu_items = soup.select("#menuSmallList > li")

for item in menu_items:
    title = item.select_one("li > a").text.strip()    
    image_url = item.select_one("li > a > img").get('src')
    
    # 상대 URL을 절대 URL로 변환
    relative_url = item.select_one("li > a").get('href')
    menu_item_url = urljoin(base_url, relative_url)
    browser.get(menu_item_url)
    
    # 페이지가 완전히 로드될 때까지 대기
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "menu_detail"))
    )
    
    time.sleep(2)  # JavaScript가 실행될 시간을 추가로 대기

    detail_html_source = browser.page_source
    detail_soup = BeautifulSoup(detail_html_source, 'html.parser')
    
    # 메뉴 정보가 존재하는지 확인하고 추출
    subTitle_element = detail_soup.select_one("div.menu_detail p.menu_info")
    if subTitle_element:
        subTitle = subTitle_element.text.strip()
    else:
        subTitle = "No subtitle available"

    # .tableInfo03 내부의 span 요소 추출
    contents = "No contents available"
    contents_element = detail_soup.select_one("div.tableInfo03 span.ft16B")
    if contents_element:
        contents = contents_element.text.strip()

    # HOT 행의 .center_t 클래스 요소 추출
    content_s1 = []
    hot_row = detail_soup.select_one("div.tableType01 tr:has(th:contains('HOT'))")
    if hot_row:
        hot_tds = hot_row.select("td.center_t")
        content_s1 = [td.text.strip() for td in hot_tds]
    
    # ICED 행의 .center_t 클래스 요소 추출
    content_s2 = []
    iced_row = detail_soup.select_one("div.tableType01 tr:has(th:contains('ICED'))")
    if iced_row:
        iced_tds = iced_row.select("td.center_t")
        content_s2 = [td.text.strip() for td in iced_tds]
    
    coffee_data.append({
        "title": title,
        "imageURL": image_url,
        "SubTitle": subTitle,
        "contents": contents,
        "content_s1": content_s1,
        "content_s2": content_s2
    })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()
