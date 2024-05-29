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
tracks = soup.select("#list_111 .product")

for track in tracks:
    title = track.select_one(".product > p.tit").text.strip()    
    image_url = track.select_one(".product > .frame > img").get('src')
    
    # 상세 정보 팝업 열기
    detail_button = track.select_one(".btn-detail.btn-bubble")
    
    if detail_button:
        detail_button = browser.find_element(By.CSS_SELECTOR, f"button[data-n='{detail_button['data-n']}']")
        browser.execute_script("arguments[0].click();", detail_button)
        
        # 팝업이 열릴 때까지 대기
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".popup-wrap > .popup_view > .info.pdinfo"))
        )
        
        # 팝업 내용 추출
        popup_html_source = browser.page_source
        popup_soup = BeautifulSoup(popup_html_source, 'html.parser')
        
        SubTitle = popup_soup.select_one(".popup-wrap > .popup_view > .info.pdinfo > p.engtit").text.strip()
        content = popup_soup.select_one(".popup-wrap > .popup_view > .info.pdinfo > p.detail").text.strip()
      
        coffee_data.append({
            "title": title,
            "imageURL": image_url,
            "SubTitle": SubTitle,
            "content": content
        })
        
        # 팝업 닫기
        close_button = browser.find_element(By.CSS_SELECTOR, ".popup-wrap .close")
        browser.execute_script("arguments[0].click();", close_button)
        
        # 팝업이 닫힐 때까지 대기
        WebDriverWait(browser, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".popup-wrap > .popup_view > .info.pdinfo"))
        )

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()

print(f"Data successfully saved to {filename}")
