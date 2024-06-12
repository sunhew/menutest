from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import json
import os
from datetime import datetime

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

# 첫 번째 페이지에서 이미지 URL 가져오기
product_cd_list = [
    "30", "25", "110563", "94", "110582", "126197", "110601", "38", "9200000004119", 
    "9200000001939", "9200000002095", "9200000004732", "9200000004728", "128692", 
    "9200000004120", "9200000001941", "9200000004734", "9200000004730", "128695", 
    "9200000005285", "110569", "9200000005284", "41", "110566", "110572", "46", 
    "9200000004313", "128192", "9200000005181", "9200000005178", "110612", 
    "9200000002950", "9200000003505", "9200000003506", "9200000002953", "20", 
    "110611", "9200000001631", "110614"
]

browser.get("https://www.starbucks.co.kr/menu/drink_list.do?CATE_CD=product_espresso")
WebDriverWait(browser, 20).until(
    EC.presence_of_element_located((By.CLASS_NAME, "product_espresso"))
)
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 이미지 URL 추출
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
    
    if product_cd in product_cd_list:
        coffee_data.append({
            "title": title,
            "imageURL": image_url,
            "product_cd": product_cd
        })

# 상세 정보 수집
detailed_coffee_data = []

for coffee in coffee_data:
    product_cd = coffee["product_cd"]
    detail_url = f"https://www.starbucks.co.kr/menu/drink_view.do?product_cd={product_cd}"
    response = requests.get(detail_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    titleE_element = soup.select_one(".myAssignZone span")
    titleE = titleE_element.text.strip() if titleE_element else "No English Title"
    desction_element = soup.select_one(".t1")
    desction = desction_element.text.strip() if desction_element else "No Description"
    information = {}
    for row in soup.select(".product_view_info ul li"):
        key = row.select_one("dt").text.strip()
        value = row.select_one("dd").text.strip()
        information[key] = value

    detailed_coffee_data.append({
        "brand": "스타벅스",
        "title": coffee["title"],
        "titleE": titleE,
        "imageURL": coffee["imageURL"],
        "desction": desction,
        "information": information,
        "address": detail_url
    })

# 상세 정보를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(detailed_coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()

print(f"Data successfully saved to {filename}")
