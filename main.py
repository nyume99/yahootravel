import time
import json
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


app = Flask(__name__)

# ブラウザの設定
def create_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    #options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Flaskエンドポイントの定義
@app.route('/get_data', methods=['GET'])
def get_data():
    # リクエストパラメータから宿コードを取得
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "code is required"}), 400

    # リクエストパラメータから月を取得
    month = request.args.get('month')
    if not month:
        return jsonify({"error": "month is required"}), 400

    # リクエストパラメータから食事条件を取得
    mtc = request.args.get('mtc')
    if not mtc:
        return jsonify({"error": "mtc is required"}), 400

    # リクエストパラメータから人数を取得
    ppc = request.args.get('ppc')
    if not ppc:
        return jsonify({"error": "ppc is required"}), 400

    # データを取得
    results = get_travel_data(code, month, mtc, ppc)
    return jsonify({'month': month, 'meal': mtc, 'people': ppc, 'name': results[0], "results": results[1]})

def get_travel_data(code, month, mtc, ppc):

    URL = f'https://travel.yahoo.co.jp/{code}/?cid={month}01&mtc={mtc}&ppc={ppc}'


    driver = create_chrome_driver()

    try:
        driver.get(URL)

        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//div[contains(@class, "absolute inset-0 flex flex-col items-center whitespace-nowrap justify-start mt-1")]')
            )
        )

        name = driver.find_element(By.XPATH, '//h1[contains(@class, "mb-2 text-4xl font-bold")]').text

        data = []
        for element in elements:

            date = element.find_element(By.XPATH, './time').text
            if date == '':
                continue
            price = element.find_element(By.XPATH, './small').text
            data.append({"date": f"{month}{str(date).zfill(2)}", "price": price.replace("円～", "").replace("空室\nなし", "none")})

        return name, data

    except Exception as e:
        return "Error", [{"error": str(e)}]
    finally:
        driver.quit()

# アプリケーションを起動
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
