import io
import json
import os
import time
import threading
import schedule
from aiotraq import Client
from aiotraq_bot import TraqHttpBot
from aiotraq_message import TraqMessage, TraqMessageManager
from aiotraq.api.stamp import get_stamps, get_stamp_image, change_stamp_image
from aiotraq.models import ChangeStampImageBody
from aiotraq.types import File
import dotenv
from datetime import datetime, timedelta, timezone


dotenv.load_dotenv()
# BOTにない権限を使うのでとりあえずUserCookieを使う
secret_cookie = os.getenv("SECRET_COOKIE") 
base_url = os.getenv("BASE_URL")

bot = TraqHttpBot(verification_token=os.getenv("BOT_VERIFICATION_TOKEN"))
response = TraqMessageManager(bot, os.getenv("BOT_ACCESS_TOKEN"), base_url, os.getenv("BASE_APP_URL"))
stamp_config_filename = os.path.join(os.path.dirname(__file__), "stamp_config.json")
with open(stamp_config_filename, "r") as f:
    stamp_config = json.load(f)


async def get_stamp_file(client: Client, stamp_name: str) -> File:
    stamps = await get_stamps.asyncio_detailed(
        client=client,
    )
    if stamps.status_code != 200 or stamps.parsed is None:
        raise ValueError(f"Failed to get stamps: {stamps.status_code}")

    target_stamp = None
    for stamp in stamps.parsed:
        if stamp.name == stamp_name:
            target_stamp = stamp
            break

    if target_stamp is None:
        raise ValueError(f"Stamp with name {stamp_name} not found")
    
    stamp_image = await get_stamp_image.asyncio_detailed(
        client=client,
        stamp_id=target_stamp.id
    )
    if stamp_image.status_code != 200 or stamp_image.parsed is None:
        raise ValueError(f"Failed to get stamp image: {stamp_image.status_code}")
    
    return stamp_image.parsed


async def eat_component(am: TraqMessage, payload: str) -> None:
    client = Client(base_url, cookies={
        "r_session": secret_cookie
    })
    command = payload.split(" ")
    if len(command) < 2:
        am.write("Usage: /eat <stamp_name>")
        return
    stamp_name = command[1].replace(":", "")
    am.write(f":toshi_test: :arrow_left: :{stamp_name}:")

    with client as c, am.spinner():
        try:
            target_file = await get_stamp_file(c, stamp_name)
            response = await change_stamp_image.asyncio_detailed(
                stamp_id=stamp_config["toshi_test"],
                client=c,
                body=ChangeStampImageBody(
                    File(
                        payload=target_file.payload,
                        file_name="toshi_test.png",
                        mime_type="image/png"
                    )
                )
            )
            if response.status_code != 204:
                raise ValueError(f"Failed to change stamp image: {response.status_code}")
            am.write(":done:")
        except ValueError as e:
            am.write(f"Error: {e}")
            return


@bot.event("MESSAGE_CREATED")
async def on_message_created(payload) -> None:
    channel_id = payload.message.channelId
    message = payload.message.plainText
    print(f"Received message: {message}")

    if message.startswith("/eat"):
        await response(eat_component, channnel_id=channel_id, payload=message)

@bot.event("DIRECT_MESSAGE_CREATED")
async def on_dm_created(payload) -> None:
    channel_id = payload.message.channelId
    message = payload.message.plainText
    print(f"Received message: {message}")

    if message.startswith("/eat"):
        await response(eat_component, channnel_id=channel_id, payload=message)


def run_scheduler():
    # スケジューラーを設定
    # 毎分実行（開発用）
    schedule.every(1).minutes.do(run_update_script)
    
    # 将来的に毎時00分に実行する場合の設定（コメントアウト）
    # schedule.every().hour.at(":00").do(run_update_script)
    
    # 起動時に1回だけスクリプトを実行して最新の状態に更新する
    run_update_script()
    
    # スケジューラーをバックグラウンドで実行
    scheduler_thread = threading.Thread(target=run_scheduler_thread, daemon=True)
    scheduler_thread.start()
    print("Scheduler started.")

def run_scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_update_script():
    jst = timezone(timedelta(hours=9), name="Asia/Tokyo")
    now = datetime.now(jst)
    print(f"Month: {now.month}, Day: {now.day}, Date: {now.weekday()}, Hour: {now.hour}, Minute: {now.minute}")
    
    update_target = {
        "day": now.weekday(),
        "date": now.day,
        "hour": now.hour,
        "month": now.month,
    }
    for target, value in update_target.items():
        if target not in stamp_config:
            print(f"Error: {target} not found in stamp_config.json")
            return
        
        stamp_id = stamp_config[target]
        stamp_image = os.path.join(os.path.dirname(__file__), "assets", target, f"{target}{value}.png")
        if not os.path.exists(stamp_image):
            print(f"Error: {stamp_image} not found")
            return
        
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
                print(f"Failed to update {target} image: {response.status_code}")
    print("Update script executed.")


if __name__ == "__main__":
    run_scheduler()
    bot.run(port=8080)