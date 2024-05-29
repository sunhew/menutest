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
import os

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "dessert39"
filename = f"{folder_path}/menudessert39_{current_date}.json"

# 폴더가 존재하지 않으면 생성
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# 웹드라이버 설치
options = ChromeOptions()
options.add_argument("--headless")
browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
browser.get("https://dessert39.com/html/pages/menu_beverage.php")

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "product-container"))
)

# 업데이트된 페이지 소스를 변수에 저장
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 데이터 추출
coffee_data = []
tracks = soup.select("#list_98 .product")

for track in tracks:
    title = track.select_one(".product > p.tit").text.strip()
    image_url = track.select_one(".product > .frame > img").get('src')

    # 여기서는 track 내부에서 찾지 않고, 전체 문서에서 찾도록 변경
    popup = soup.select_one(".popup-wrap > .popup.popup_view")
    
    # None 체크 후 데이터 추출
    if popup:
        SubTitle = popup.select_one(".info.pdinfo > p.engtit").text.strip() if popup.select_one(".info.pdinfo > p.engtit") else "N/A"
        content = popup.select_one(".info.pdinfo > p.detail").text.strip() if popup.select_one(".info.pdinfo > p.detail") else "N/A"
    else:
        SubTitle = "N/A"
        content = "N/A"

    coffee_data.append({
        "title": title,
        "imageURL": image_url,
        "SubTitle": SubTitle,
        "content": content
    })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()

print(f"Data successfully saved to {filename}")
