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
folder_path = "tomntom"
filename = f"{folder_path}/menutomntom_{current_date}.json"

# 웹드라이브 설치
options = ChromeOptions()
options.add_argument("--headless")
browser = webdriver.Chrome(options=options)
browser.get("https://www.tomntoms.com/menu/drink")

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 20).until(
    EC.presence_of_element_located((By.CLASS_NAME, "pb-20"))
)

# "더보기" 버튼을 찾아 클릭
try:
    more_button = WebDriverWait(browser, 20).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".custom-button.main-tab"))
    )
    if more_button:
        browser.execute_script("arguments[0].click();", more_button)
        print("Clicked '더보기' button.")
        time.sleep(5)  # 충분한 대기 시간을 줌
except Exception as e:
    print("Error clicking '더보기':", e)

# 업데이트된 페이지 소스를 변수에 저장
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 데이터 추출
coffee_data = []
tracks = soup.select("#root > section.max-w-7xl.p-4.mx-auto.pb-20.w-full > div.grid.gap-6.mt-8.grid-cols-1 .relative.w-full")

for i, track in enumerate(tracks):
    title = track.select_one(".relative.w-full button > div > div > p > span.tracking-wider").text.strip()
    titleE = track.select_one(".relative.w-full button > div > div > h3").text.strip()
    image_url = track.select_one(".relative.w-full button > div > img").get('src')
    
    # Selenium을 사용하여 clickable element 찾기
    clickable_elements = browser.find_elements(By.CSS_SELECTOR, ".relative.w-full")
    if i < len(clickable_elements):
        browser.execute_script("arguments[0].click();", clickable_elements[i])
        
        try:
            # 상세 정보가 로드될 때까지 대기
            WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".menu-container"))
            )
        except TimeoutException as e:
            print(f"TimeoutException while waiting for menu-container: {e}")
            continue
        
        # 상세 페이지 HTML 추출
        detail_html_source = browser.page_source
        detail_soup = BeautifulSoup(detail_html_source, 'html.parser')
        
        description = detail_soup.select_one(".menu-container .flex.flex-col .break-words.text-sm").text.strip()
        
        # 영양 정보 추출
        info_elements = detail_soup.select(".menu-container .min-h-[50%] .flex.justify-between")
        information = {element.select_one("p.text-xs.font-bold.text-gray-500").text.strip(): element.select_one("p.text-xs.font-bold.text-black").text.strip() for element in info_elements}

        coffee_data.append({
            "brand": "탐앤탐",
            "title": title,
            "titleE": titleE,
            "imageURL": image_url,
            "description": description,
            "information": information,
            "address": "https://www.tomntoms.com/menu/drink"
        })
        
        # 팝업 닫기
        close_button = browser.find_element(By.CSS_SELECTOR, ".menu-container button")
        if close_button:
            browser.execute_script("arguments[0].click();", close_button)
        time.sleep(1)  # 팝업이 닫힐 시간을 줌

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()
