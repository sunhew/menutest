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
    EC.presence_of_element_located((By.CLASS_NAME, "menu_list01"))
)

html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# ID 목록
menu_ids = [
    "menuView1_877", "menuView2_877",
    "menuView1_876", "menuView2_876",
    "menuView1_932", "menuView2_932",
    "menuView1_633", "menuView2_633",
    "menuView1_632", "menuView2_632",
    "menuView1_631", "menuView2_631",
    "menuView1_549", "menuView2_549",
    "menuView1_209", "menuView2_209",
    "menuView1_208", "menuView2_208",
    "menuView1_13", "menuView2_13",
    "menuView1_10", "menuView2_10",
    "menuView1_7", "menuView2_7",
    "menuView1_11", "menuView2_11",
    "menuView1_12", "menuView2_12",
    "menuView1_6", "menuView2_6",
    "menuView1_2", "menuView2_2",
    "menuView1_14", "menuView2_14"
]

# 중복 방지를 위한 수집된 타이틀 저장소
collected_titles = set()
coffee_data = []

for i in range(0, len(menu_ids), 2):
    view1_id = menu_ids[i]
    view2_id = menu_ids[i + 1]
    
    view1_element = soup.find(id=view1_id)
    view2_element = soup.find(id=view2_id)
    
    if view1_element and view2_element:
        brand = "할리스"
        
        # menuView1 정보 추출
        image_element = view1_element.find("img")
        image_url = image_element.get('src') if image_element else "No image available"
        
        title_element = view1_element.select_one(".menu_detail p span")
        title = title_element.contents[0].strip() if title_element and title_element.contents else "No title available"
        
        # 중복 확인
        if title in collected_titles:
            continue
        
        titleE = title_element.next_sibling.strip() if title_element and title_element.next_sibling else "No English title available"
        
        desction_element = view1_element.select_one(".menu_detail p.menu_info")
        desction = desction_element.text.strip() if desction_element else "No description available"
        
        # menuView2 정보 추출
        information = {}
        hot_row = view2_element.select_one(".tableType01 tbody tr:has(th:contains('HOT'))")
        if hot_row:
            hot_tds = hot_row.select("td.center_t")
            headers = ["1회 제공량 (kcal)", "당류 (g)", "단백질 (g)", "포화지방 (g)", "나트륨 (mg)", "카페인 (mg)"]
            for header, td in zip(headers, hot_tds):
                information[header] = td.text.strip()
        
        address = base_url
        
        coffee_data.append({
            "brand": brand,
            "title": title,
            "titleE": titleE,
            "imageURL": image_url,
            "desction": desction,
            "information": information,
            "address": address
        })
        
        # 타이틀을 중복 확인 리스트에 추가
        collected_titles.add(title)

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()
