import datetime
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

option = Options()
option.add_argument("--headless")
option.add_argument("--disable-gpu")
option.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=option)
driver.set_window_size(950, 800)


def get_hotel_names_and_urls():
    """ボタンをクリックし，その後表示されるサイトからホテル名，urlを取得．"""
    # 設定
    driver.get("https://www.hoshinoresorts.com/sp/kaitabi20s/")

    # reserveボタンをクリック
    elem = driver.find_element(By.XPATH, '//*[@id="js-reservebtn"]')
    elem.click()

    # ホテル名・リンク部分のhtmlを取得
    html = driver.page_source.encode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all(class_="cm-reserve__bodyListItem js-reserve__item")

    # htmlからホテル名，リンクを取得し格納
    hotel_names = []
    urls = []
    for result in results:
        hotel_name = result.find("h4").text
        url = result.find("a").get("href")
        hotel_names.append(hotel_name)
        urls.append(url)
    return hotel_names, urls


def get_reservable_info(hotel_names, urls):
    """予約可能な施設名・年月日・空き部屋数を取得．"""
    # いつまで予約可能かを確認
    last_reservation_date = (datetime.datetime.now() + datetime.timedelta(days=44)).date().strftime("%Y月%m月%d日")
    #
    reservable_info = {}
    for hotel_name, url in zip(hotel_names, urls):
        # カレンダー部分のhtmlを取得
        driver.get(url)
        time.sleep(5)
        html = driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        calendars = soup.find_all(class_="c-calendar")

        # カレンダーから空いている日，部屋数を抽出 ({ホテル名： {空室年月日：　空室数}})
        dates = []
        room_cnts = []
        for calendar in calendars:
            # htmlから該当箇所を探す
            ym = calendar.find_all(class_="header")[0].text
            reservable_days = calendar.find_all(class_="date date-defalut")
            reservable_room_cnts = calendar.find_all(class_="roomcount")
            # 必要な情報を抽出
            if reservable_days and reservable_room_cnts:
                dates += [ym + day.text.replace("\n", "").replace(" ", "") + "日" for day in reservable_days]
                room_cnts += [room_cnt.text for room_cnt in reservable_room_cnts]
        # 格納
        reservable_info[hotel_name] = {d: r for d, r in zip(dates, room_cnts)}
    return last_reservation_date, reservable_info


def scrape_reservable_info_from_website():
    """空室情報をスクレイピングでWebサイトから取得"""
    # 全施設の名称とリンクを取得
    hotel_names, urls = get_hotel_names_and_urls()
    # それぞれの施設の空室情報を取得
    last_reservation_date, reservable_info = get_reservable_info(hotel_names, urls)
    return last_reservation_date, reservable_info


def convert_reservable_info_into_text(last_reservation_date: str, reservable_info: dict):
    """予約可能なホテル名・年月日・空室数をテキストにして返す."""
    text = f"いつまで予約が可能か：{last_reservation_date} \n"
    for k, v in reservable_info.items():
        if v:
            text += f"{k}\n"
            for reservable_date, room_cnt in v.items():
                text += f"{reservable_date}: {room_cnt} \n"
    return text


def get_reservable_info_as_text():
    # 予約関連情報を取得
    last_reservation_date, reservable_info = scrape_reservable_info_from_website()
    # テキストに整形
    reservable_info_as_txt = convert_reservable_info_into_text(last_reservation_date, reservable_info)
    return reservable_info_as_txt
