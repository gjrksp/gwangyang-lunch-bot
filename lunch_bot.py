import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

POSWEL_API = "https://www.poswel.co.kr/api/rest/todayMealList"
REGION = "K"
RESTAURANT_ID = "10"
MEAL_TYPE = "002"
MEAL_TYPE_NM = "점심"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = "54679475"

today = datetime.now(ZoneInfo("Asia/Seoul"))
meal_date = today.strftime("%Y-%m-%d")

payload = {
    "region": REGION,
    "restaurantId": RESTAURANT_ID,
    "mealDate": meal_date,
    "mealType": MEAL_TYPE,
    "mealTypeNm": MEAL_TYPE_NM
}

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 17) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/140.0 Mobile Safari/537.36"
    ),
    "Referer": "https://www.poswel.co.kr/rest/todayMeal",
    "Origin": "https://www.poswel.co.kr",
    "X-Requested-With": "XMLHttpRequest"
}

response = requests.post(
    POSWEL_API,
    data=payload,
    headers=headers,
    timeout=30
)

print("POSWEL HTTP:", response.status_code)
response.raise_for_status()

data = response.json()

menus = []
detail_map = data.get("detailMap", {})

for key, menu_list in detail_map.items():
    if not isinstance(menu_list, list):
        continue

    for menu in menu_list:
        menu_name = menu.get("menuName", "")

        if menu_name == "4크레딧":
            continue

        if not menu_name:
            continue

        course_name = menu.get("courseName", "")
        course_name = course_name.replace("2F_", "")

        menus.append({
            "courseName": course_name,
            "menuName": menu_name,
            "detail": menu.get("mainDishDetail", "")
        })

if not menus:
    message = (
        "🍚 광양 점심비서\n\n"
        f"📅 {today.year}년 {today.month}월 {today.day}일\n\n"
        "오늘 점심 메뉴를 가져오지 못했습니다."
    )
else:
    message = (
        "🍚 광양 복지센터대식당\n"
        f"📅 {today.year}년 {today.month}월 {today.day}일 점심\n\n"
    )

    for index, menu in enumerate(menus):
        course = menu["courseName"]

        if course == "한식":
            icon = "🇰🇷"
        elif course == "일품":
            icon = "🍽"
        elif course == "직화":
            icon = "🔥"
        elif course == "TAKEOUT":
            icon = "🥗"
        else:
            icon = "🍽"

        message += f"{icon} {course}\n"
        message += f"{menu['menuName']}\n"

        if menu["detail"]:
            message += f"└ {menu['detail']}\n"

        if index < len(menus) - 1:
            message += "\n"

telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

telegram_response = requests.post(
    telegram_url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    },
    timeout=30
)

print("Telegram HTTP:", telegram_response.status_code)
print(message)

telegram_response.raise_for_status()

print("✅ 광양 점심비서 전송 완료")
