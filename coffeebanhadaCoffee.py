from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "coffeebanhada"
filename = f"{folder_path}/menucoffeebanhada_{current_date}.json"

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

# 수집할 m_idx 값 리스트
m_idx_list = [
    1211, 1077, 1075, 1073, 1071, 1070, 1068, 1066, 1064, 1062, 1060, 1058, 1056, 1054
]

# 데이터 추출을 위한 빈 리스트 생성
coffee_data = []

for m_idx in m_idx_list:
    # 각 m_idx 값에 대해 페이지 로드
    url = f"https://coffeebanhada.com/main/menu/view.php?m_idx={m_idx}"
    browser.get(url)

    # 페이지가 완전히 로드될 때까지 대기
    try:
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "menu_info_top"))
        )
    except:
        print(f"Skipping m_idx={m_idx}, element not found.")
        coffee_data.append({
            "brand": "커피에반하다",
            "title": "",
            "titleE": "",
            "imageURL": "",
            "desction": "",
            "information": {},
            "address": url
        })
        continue

    # 상세 페이지의 소스를 변수에 저장
    detail_page_source = browser.page_source
    soup = BeautifulSoup(detail_page_source, 'html.parser')

    # 고정된 주소 설정
    address = url

    # 데이터 추출
    item = soup.select_one(".sub_content .menu_info .menu_info_in.w1250")

    if item:
        try:
            title = item.select_one(".menu_info_right p.menu_title").contents[0].strip()
            titleE = item.select_one(".menu_info_right p.menu_title span").text.strip()
            image_url = item.select_one(".menu_info_left img").get('src').replace('/data', 'https://coffeebanhada.com/data')
            desction = item.select_one(".menu_info_right p.menu_sub").get_text(separator=" ").strip().replace('\n', ' ').replace('\t', ' ')

            # HOT 영양 정보 추출
            nutrition_info = {}
            rows = item.select("div.nutritional_info_vanada tr")
            for row in rows:
                if "HOT" in row.get_text():
                    cols = row.find_all("td")
                    if cols:
                        nutrition_info = {
                            "열량(Kcal)": cols[1].text.strip(),
                            "당류(g)": cols[2].text.strip(),
                            "단백질(g)": cols[3].text.strip(),
                            "포화지방(g)": cols[4].text.strip(),
                            "나트륨(mg)": cols[5].text.strip(),
                            "카페인(mg)": cols[6].text.strip(),
                        }
                        break

            coffee_data.append({
                "brand": "커피에반하다",
                "title": title,
                "titleE": titleE,
                "imageURL": image_url,
                "desction": desction,
                "information": nutrition_info,
                "address": address
            })
        except Exception as e:
            print(f"Error extracting data from m_idx={m_idx}: {e}")
            coffee_data.append({
                "brand": "커피에반하다",
                "title": "",
                "titleE": "",
                "imageURL": "",
                "desction": "",
                "information": {},
                "address": address
            })
    else:
        coffee_data.append({
            "brand": "커피에반하다",
            "title": "",
            "titleE": "",
            "imageURL": "",
            "desction": "",
            "information": {},
            "address": address
        })

# 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(coffee_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()

print(f"Data successfully saved to {filename}")
