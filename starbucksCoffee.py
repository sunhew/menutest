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
import time

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "starbucks"
filename = f"{folder_path}/menustarbucks_{current_date}.json"

# 폴더 생성
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

# 첫 번째 페이지에서 데이터 추출
browser.get("https://www.starbucks.co.kr/menu/drink_list.do?CATE_CD=product_espresso")
WebDriverWait(browser, 20).until(
    EC.presence_of_element_located((By.CLASS_NAME, "product_espresso"))
)
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 데이터 추출
coffee_data = []
tracks = soup.select(".product_list dl dd ul li")

for track in tracks:
    title_element = track.select_one("dd")
    if not title_element:
        continue  # 제목이 없으면 건너뜁니다.
    
    title = title_element.text.strip()
    image_element = track.select_one("dt a img")
    if not image_element:
        continue  # 이미지가 없으면 건너뜁니다.
    
    image_url = image_element.get('src')
    product_cd = track.select_one("dt a").get('prod')
    
    # 스크롤하여 요소가 보이도록 함
    element = browser.find_element(By.CSS_SELECTOR, f'a.goDrinkView[prod="{product_cd}"] img')
    browser.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1)  # 스크롤 후 잠시 대기
    
    try:
        # 요소가 상호작용 가능해질 때까지 대기
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'a.goDrinkView[prod="{product_cd}"] img')))
        
        # 직접 클릭 이벤트 발생
        browser.execute_script("arguments[0].click();", element)
        
        # 새로운 페이지가 로드될 때까지 대기
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product_view_detail"))
        )
        
        detail_page_source = browser.page_source
        detail_soup = BeautifulSoup(detail_page_source, 'html.parser')

        titleE_element = detail_soup.select_one(".myAssignZone span")
        titleE = titleE_element.text.strip() if titleE_element else "No English Title"
        desction_element = detail_soup.select_one(".t1")
        desction = desction_element.text.strip() if desction_element else "No Description"
        information = {}
        for row in detail_soup.select(".product_view_info ul li"):
            key = row.select_one("dt").text.strip()
            value = row.select_one("dd").text.strip()
            information[key] = value

        coffee_data.append({
            "brand": "스타벅스",
            "title": title,
            "titleE": titleE,
            "imageURL": image_url,
            "desction": desction,
            "information": information,
            "address": browser.current_url
        })

        # 다시 첫 번째 페이지로 이동
        browser.back()
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product_espresso"))
        )
    except Exception as e:
        print(f"Error processing product {product_cd}: {e}")
        continue

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()

print(f"Data successfully saved to {filename}")
