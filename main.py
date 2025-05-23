import io
import json
import os
import time
import threading
import schedule
import httpx
import dotenv
from aiotraq import Client
from aiotraq_bot import TraqHttpBot
from aiotraq_message import TraqMessage, TraqMessageManager
from aiotraq.api.stamp import change_stamp_image
from aiotraq.models import ChangeStampImageBody
from aiotraq.types import File
from datetime import datetime, timedelta, timezone


dotenv.load_dotenv()
# BOTにない権限を使うのでとりあえずUserCookieを使う
secret_cookie = os.getenv("SECRET_COOKIE") 
base_url = os.getenv("BASE_URL")
base_app_url = os.getenv("BASE_APP_URL")
bot_access_token = os.getenv("BOT_ACCESS_TOKEN")
if not secret_cookie or not base_url or not base_app_url or not bot_access_token:
    print("環境変数が設定されていません")
    exit(1)


bot = TraqHttpBot(verification_token=os.getenv("BOT_VERIFICATION_TOKEN"))
response = TraqMessageManager(bot, bot_access_token, base_url, base_app_url)
stamp_config_filename = os.path.join(os.path.dirname(__file__), "stamp_config.json")
with open(stamp_config_filename, "r") as f:
    stamp_config = json.load(f)


def is_now_task(message: str) -> bool:
    return "/now" in message

def now_component(am: TraqMessage):
    am.write(":today_month::today_date::today_day::today_hour:")

def is_update_task(message: str) -> bool:
    return "/update" in message

def update_component(am: TraqMessage):
    with am.spinner("Updating..."):
        message = update_stamp_image()
    
    print(message)
    am.write(message)


def help_component(am: TraqMessage):
    am.write("`/now`で現在の月、日、曜日、時間を表示します。")
    am.write("`/update`で強制的にスタンプの更新を実行します")
    am.write("`/help`でこのメッセージを表示します。")


@bot.event("MESSAGE_CREATED")
async def on_message_created(payload) -> None:
    channel_id = payload.message.channelId
    message = payload.message.plainText
    print(f"Received message: {message}")

    if "/now" in message:
        await response(now_component, channnel_id=channel_id)
    elif "/update" in message:
        await response(update_component, channnel_id=channel_id)
    else:
        await response(help_component, channnel_id=channel_id)
    

@bot.event("DIRECT_MESSAGE_CREATED")
async def on_dm_created(payload) -> None:
    channel_id = payload.message.channelId
    message = payload.message.plainText
    print(f"Received message: {message}")

    if "/now" in message:
        await response(now_component, channnel_id=channel_id)
    elif "/update" in message:
        await response(update_component, channnel_id=channel_id)
    else:
        await response(help_component, channnel_id=channel_id)


def run_scheduler():
    # スケジューラーを設定
    # 毎分実行（開発用）
    # schedule.every(1).minutes.do(
    #     lambda: print(update_stamp_image())
    # )
    
    # 将来的に毎時00分に実行する場合の設定
    schedule.every().hour.at(":00").do(
        lambda: print(update_stamp_image())
    )
    
    # 起動時に1回だけスクリプトを実行して最新の状態に更新する
    message = update_stamp_image()
    print(message)
    
    # スケジューラーをバックグラウンドで実行
    scheduler_thread = threading.Thread(target=run_scheduler_thread, daemon=True)
    scheduler_thread.start()
    print("Scheduler started.")

def run_scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)

def format_temperature(temp):
    """気温を指定されたフォーマットに変換する"""
    temp_int = int(round(temp))
    
    if temp_int <= -10:
        return "m10o"
    elif temp_int < 0:
        return f"m{abs(temp_int)}"
    elif temp_int >= 40:
        return "40u"
    else:
        return str(temp_int)

def get_weather() -> tuple[str, str] | None:
    """天気情報を取得して気温とアイコンを出力する"""
    api_key = os.getenv("OPEN_WEATHER_API_KEY")
    latitude = os.getenv("TARGET_LATITUDE")
    longitude = os.getenv("TARGET_LONGITUDE")
    
    if not api_key or not latitude or not longitude:
        print("環境変数が設定されていません")
        return None
    
    url = f"https://api.openweathermap.org/data/2.5/weather?appid={api_key}&lat={latitude}&lon={longitude}&units=metric"
    
    with httpx.Client() as client:
        try:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # 気温を取得してフォーマット
            temp = data["main"]["temp"]
            formatted_temp = format_temperature(temp)
            
            # アイコンを取得
            icon = data["weather"][0]["icon"]
            
            print(f"気温: {formatted_temp}")
            print(f"アイコン: {icon}")
            return formatted_temp, icon
        except httpx.RequestError as e:
            print(f"リクエストエラー: {e}")
        except httpx.HTTPStatusError as e:
            print(f"HTTPエラー: {e}")
        except KeyError as e:
            print(f"データの解析エラー: {e}")
    return None


def update_stamp_image() -> str:
    # 日付と時刻の更新
    jst = timezone(timedelta(hours=9), name="Asia/Tokyo")
    now = datetime.now(jst)
    print(f"Month: {now.month}, Day: {now.day}, Date: {now.weekday()}, Hour: {now.hour}, Minute: {now.minute}")
 
    update_target = {
        "day": str(now.weekday()),
        "date": str(now.day),
        "hour": str(now.hour),
        "month": str(now.month),
    }
    date_result = apply_stamp_image(update_target)

    # 天気情報の更新
    weather = get_weather()
    if weather is None:
        weather_result = "Error: Weather data not available."
        return date_result + "\n" + weather_result
    
    formatted_temp, icon = weather
    update_weather = {
        "temp": formatted_temp,
        "weather": icon,
    }
    weather_result = apply_stamp_image(update_weather)
    return date_result + "\n" + weather_result

def apply_stamp_image(update_target: dict[str, str]) -> str:
    if base_url is None or secret_cookie is None:
        return "Error: BASE_URL or SECRET_COOKIE is not set."
    
    for target, value in update_target.items():
        if target not in stamp_config:
            return f"Error: {target} not found in stamp_config.json"
        
        stamp_id = stamp_config[target]
        stamp_image = os.path.join(os.path.dirname(__file__), "assets", target, f"{target}{value}.png")
        if not os.path.exists(stamp_image):
            return f"Error: {stamp_image} not found"
        
        with open(stamp_image, "rb") as image_file:
            image_data = image_file.read()
            binary_io = io.BytesIO(image_data)

        client = Client(base_url, cookies={
            "r_session": secret_cookie
        })
        with client as c:
            body = ChangeStampImageBody(
                File(
                    payload=binary_io,
                    file_name=f"{target}{value}.png",
                    mime_type="image/png"
                )
            )

            response = change_stamp_image.sync_detailed(
                stamp_id=stamp_id,
                client=c,
                body=body
            )
            print(response.status_code)
            print(response.parsed)
            if response.status_code == 204:
                print(f"{target} image updated successfully.")
            else:
                return f"Failed to update {target} image: {response.status_code}"
    return "Update script executed."


if __name__ == "__main__":
    run_scheduler()
    bot.run(port=8080)