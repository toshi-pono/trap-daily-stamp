import dotenv
import os
import random
import io
import json
from datetime import datetime, timedelta, timezone
from aiotraq import Client
from aiotraq.models import ChangeStampImageBody
from aiotraq.api.stamp import change_stamp_image
from aiotraq.types import File


def main():
    stamp_config_filename = os.path.join(os.path.dirname(__file__), "stamp_config.json")
    with open(stamp_config_filename, "r") as f:
        stamp_config = json.load(f)
        print(stamp_config)

    # 現在の month, day, date, hour (JST) を取得して printする
    jst = timezone(timedelta(hours=9), name="Asia/Tokyo")
    now = datetime.now(jst)
    print(f"Month: {now.month}, Day: {now.day}, Date: {now.weekday()}, Hour: {now.hour}, Minute: {now.minute}")

def random_test():
    # とりあえずランダムにスタンプを切り替えてみる
    secret_cookie = os.getenv("SECRET_COOKIE")
    base_url = "https://q.trap.jp/api/v3"
    stamp_id = "0196eced-c64c-7a27-a60b-d7f848166ba0"

    client = Client(base_url, cookies={
        "r_session": secret_cookie
    })

    image_hour_dir = os.path.join(os.path.dirname(__file__), "assets", "hour")
    # 0-23までの乱数を生成
    random_hour = random.randint(0, 23)
    target_image_path = os.path.join(image_hour_dir, f"hour{random_hour}.png")

    with open(target_image_path, "rb") as image_file:
        image_data = image_file.read()
        binary_io = io.BytesIO(image_data)

    with client as c:
        body = ChangeStampImageBody(
            File(
                payload=binary_io,
                file_name=f"hour{random_hour}.png",
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
            print("Stamp image updated successfully.")
        else:
            print(f"Failed to update stamp image: {response.status_code}")
    


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
    random_test()
