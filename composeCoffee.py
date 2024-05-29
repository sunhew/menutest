from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver.chrome.options import Options as ChromeOptions
import json
import os

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "compose"
filename = f"{folder_path}/menucompose_{current_date}.json"

# 폴더 경로가 없다면 생성
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# 웹드라이버 초기화 (Chrome 사용)
options = ChromeOptions()
options.add_argument("--headless")
browser = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), options=options)

# 방문할 URL 리스트
urls = [
    "https://composecoffee.com/menu/category/185?page=1",
    "https://composecoffee.com/menu/category/185?page=2",
]

# 데이터 추출을 위한 빈 리스트 생성
compose_data = []

for url in urls:
    # 페이지 로드
    browser.get(url)
    
    # 페이지의 끝까지 스크롤 내리기
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # 잠시 대기 (로딩 완료를 위해)
    browser.implicitly_wait(5)

    # 업데이트된 페이지 소스를 변수에 저장
    html_source_updated = browser.page_source
    soup = BeautifulSoup(html_source_updated, 'html.parser')

    # 데이터 추출
    items = soup.select(".itemBox")
    for item in items:
        name = item.select_one(".title").text.strip()
        image_url = item.select_one(".rthumbnailimg").get('src').replace('/files', 'https://composecoffee.com/files')

        # 각 메뉴 상세 페이지로 이동
        detail_url = item.select_one("a").get('href')
        browser.get(detail_url)
        detail_page = browser.page_source
        detail_soup = BeautifulSoup(detail_page, 'html.parser')

        # 영양 성분 정보 추출
        nutritional_info = detail_soup.select(".info-g-0 > .extra")
        nutrients = {}
        for info in nutritional_info:
            try:
                key, value = info.text.split(" : ")
                nutrients[key.strip()] = value.strip()
            except ValueError:
                continue  # 값을 올바르게 분리할 수 없으면 건너뜀

        compose_data.append({
            "title": name,
            "imageURL": image_url,
            "content": nutrients
        })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(compose_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()

print(f"Data successfully saved to {filename}")
