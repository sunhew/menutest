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
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
browser.get("https://www.tomntoms.com/menu/drink")

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "pb-20"))
)

# "더보기" 버튼을 찾아 클릭
try:
    more_button = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".custom-button.main-tab"))
    )
    if more_button:
        browser.execute_script("arguments[0].click();", more_button)
        print("Clicked '더보기' button.")
        time.sleep(3)
except Exception as e:
    print("Error clicking '더보기':", e)

# 데이터 추출
coffee_data = []
tracks = browser.find_elements(By.CSS_SELECTOR, "#root > section.max-w-7xl.p-4.mx-auto.pb-20.w-full > div.grid.gap-6.mt-8.grid-cols-1 .relative.w-full")

for track in tracks:
    # 항목 클릭
    clickable_element = track.find_element(By.CSS_SELECTOR, ".group.block.flex.flex-col.items-center.overflow-hidden")
    browser.execute_script("arguments[0].click();", clickable_element)
    
    # 메뉴 컨테이너가 나타날 때까지 대기
    WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".menu-container"))
    )
    
    # 세부 정보 가져오기
    html_source_detail = browser.page_source
    detail_soup = BeautifulSoup(html_source_detail, 'html.parser')
    
    brand = "톰앤톰스"
    title = detail_soup.select_one(".menu-container .text-xl.font-bold").text.strip()
    titleE = detail_soup.select_one(".menu-container .text-sm.text-gray-400").text.strip() if detail_soup.select_one(".menu-container .text-sm.text-gray-400") else ""
    image_url = track.find_element(By.CSS_SELECTOR, "img").get_attribute('src')
    desction = detail_soup.select_one(".menu-container .flex.flex-col.whitespace-normal.break-words .break-words.text-sm").text.strip()
    
    information = {}
    info_elements = detail_soup.select(".menu-container .min-h-[50%] .flex.justify-between")
    for info in info_elements:
        key = info.select_one("p.text-xs.font-bold.text-gray-500").text.strip()
        value = info.select_one("p.text-xs.font-bold.text-black").text.strip()
        information[key] = value
    
    address = browser.current_url
    
    coffee_data.append({
        "brand": brand,
        "title": title,
        "titleE": titleE,
        "imageURL": image_url,
        "desction": desction,
        "information": information,
        "address": address
    })
    
    # 뒤로가기 버튼 클릭 (또는 이전 페이지로 이동)
    browser.back()
    # 페이지가 완전히 로드될 때까지 대기
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "pb-20"))
    )

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()
