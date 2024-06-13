from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json
import os

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "tomntom"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
filename = f"{folder_path}/menutomntom_{current_date}.json"

# 웹드라이버 설정
options = ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

browser.get("https://www.tomntoms.com/menu/drink")

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 20).until(
    EC.presence_of_element_located((By.CLASS_NAME, "pb-20"))
)

# "더보기" 버튼을 클릭하여 모든 항목 로드
try:
    while True:
        more_button = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".custom-button.main-tab"))
        )
        if more_button:
            browser.execute_script("arguments[0].click();", more_button)
            print("Clicked '더보기' button.")
            time.sleep(2)  # 충분한 대기 시간을 줌
        else:
            break
except Exception as e:
    print("No more '더보기' button found:", e)

# 페이지 소스를 파싱
html_source = browser.page_source
soup = BeautifulSoup(html_source, 'html.parser')

# 데이터 추출
coffee_data = []
items = soup.select(".grid.gap-6.mt-8.grid-cols-1 .relative.w-full")

for i, item in enumerate(items):
    try:
        title = item.select_one("p span.tracking-wider").text.strip()
        titleE = item.select_one("h3").text.strip()
        image_url = item.select_one("img").get('src')

        # 아이템 클릭하여 상세 정보 로드
        clickable_element = browser.find_elements(By.CSS_SELECTOR, ".grid.gap-6.mt-8.grid-cols-1 .relative.w-full")[i]
        browser.execute_script("arguments[0].click();", clickable_element)

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

        # 설명 추출
        description_element = detail_soup.select_one(".break-words.text-sm")
        description = description_element.text.strip() if description_element else "No description available"

        # 영양 정보 추출
        info_elements = detail_soup.select(".min-h-[50%] .flex.justify-between")
        information = {element.select_one("p.text-xs.font-bold.text-gray-500").text.strip(): element.select_one("p.text-xs.font-bold.text-black").text.strip() for element in info_elements}

        coffee_data.append({
            "brand": "탐앤탐",
            "title": title,
            "titleE": titleE,
            "imageURL": image_url,
            "desction": description,
            "information": information,
            "address": "https://www.tomntoms.com/menu/drink"
        })

        # 팝업 닫기
        close_button = browser.find_element(By.CSS_SELECTOR, ".menu-container button")
        if close_button:
            browser.execute_script("arguments[0].click();", close_button)
        time.sleep(1)  # 팝업이 닫힐 시간을 줌

    except Exception as e:
        print(f"Error processing item {i}: {e}")

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()
