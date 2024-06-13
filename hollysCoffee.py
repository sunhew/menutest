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
from urllib.parse import urljoin

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "hollys"
filename = f"{folder_path}/menuhollys_{current_date}.json"

# 웹드라이버 설정
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

# 초기 페이지에서 ID 추출
menu_ids = []
menu_view_divs = soup.select("div.menu_view01")

for div in menu_view_divs:
    menu_id = div.get('id').replace('menuView1_', '')
    menu_ids.append(menu_id)

# 데이터 수집
coffee_data = []

for menu_id in menu_ids:
    menu_item_url = f"https://www.hollys.co.kr/menu/espresso.do?menuView1_{menu_id}"
    browser.get(menu_item_url)
    
    # 상세 페이지가 완전히 로드될 때까지 대기
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "menu_detail"))
    )
    
    detail_html_source = browser.page_source
    detail_soup = BeautifulSoup(detail_html_source, 'html.parser')
    
    # 세부 정보 추출
    brand = "할리스"
    
    title_element = detail_soup.select_one("div.menu_detail > span")
    title = title_element.contents[0].strip() if title_element and title_element.contents else "No title available"
    
    titleE_element = detail_soup.select_one("div.menu_detail > span > br + text")
    titleE = titleE_element.strip() if titleE_element else "No English title available"
    
    image_element = detail_soup.select_one("div.menu_detail > img")
    image_url = image_element.get('src') if image_element else "No image available"
    
    desction_element = detail_soup.select_one("div.menu_detail > p.menu_info")
    desction = desction_element.text.strip() if desction_element else "No description available"
    
    hot_row = detail_soup.select_one("div.tableType01 tr:has(th:contains('HOT'))")
    information = {}
    if hot_row:
        hot_tds = hot_row.select("td.center_t")
        headers = ["1회 제공량 (kcal)", "포화지방 (g)", "단백질 (g)", "지방 (g)", "트랜스지방 (g)", "나트륨 (mg)", "당류 (g)", "카페인 (mg)", "콜레스테롤 (mg)", "탄수화물 (g)"]
        for header, td in zip(headers, hot_tds):
            information[header] = td.text.strip()
    
    address = menu_item_url
    
    coffee_data.append({
        "brand": brand,
        "title": title,
        "titleE": titleE,
        "imageURL": image_url,
        "desction": desction,
        "information": information,
        "address": address
    })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()
