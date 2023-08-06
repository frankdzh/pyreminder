import requests
import time
import datetime
import os
from dotenv import load_dotenv
import logging


pushover_enabled = os.getenv("PUSHOVER_ENABLED", "false")
pushover_enabled = pushover_enabled.lower() == "true"

def send_pushover_messages(token, group, device, message):
    import requests

    # Pushover API url
    url = "https://api.pushover.net/1/messages.json"

    # Send the message to each user
    # Send the message to the group
    data = {
        "token": token,
        "user": group,
        "message": message,
        "device": device,
    }

    if (pushover_enabled):
        response = requests.post(url, data=data)
    print(f"Sent message to {group}, status: {response.status_code}")

# Load the .env file
load_dotenv()

pushover_token = os.getenv("PUSHOVER_TOKEN", "azt8e3gnx1zdhicdg7kuz9y64mbznn")
pushover_group = os.getenv("PUSHOVER_GROUP", "gbcw19yoe42yikdsxitetfcwc82557")
pushover_device = os.getenv("PUSHOVER_DEVICE_NAME", "yz_iphonexsmax")

# Define constants
# Interval to check the car status in seconds
check_interval = float(os.getenv("CHECK_INTERVAL", 60))
URL = "http://10.168.1.115:8081/api/v1/cars/1/status"  # URL to fetch car status

REMIND_TIMES = [8, 12, 20]  # Times to remind every day
# Convert environment variables to appropriate data types
speed_limit = float(os.getenv("SPEED_LIMIT", 0))
battery_level_limit = float(os.getenv("BATTERY_LEVEL_LIMIT", 35))
geofence = os.getenv("GEOFENCE", "家")
REMIND_TIMES = list(map(int, os.getenv("REMIND_TIMES", "8,12,20").split(",")))

logging.basicConfig(level=logging.INFO)

last_remind = None  # The time of the last remind

# Define a list to hold the remind times
remind_done = []

logging.info(f"启动检查电量 <= {battery_level_limit}%...")
while True:

    # Fetch car status
    response = requests.get(URL)
    data = response.json()

    # Check the conditions
    driving_details = data["data"]["status"]["driving_details"]
    battery_details = data["data"]["status"]["battery_details"]
    car_geodata = data["data"]["status"]["car_geodata"]
    
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"{timestamp}: 检查-> 当前电量:{battery_details['battery_level']}% <= 报警电量:{battery_level_limit}%, 当前速度:{driving_details['speed']} <= 报警速度:{speed_limit}, 当前位置:{car_geodata['geofence']} == 报警位置:{geofence}...")

    if (
        driving_details["speed"] <= speed_limit  # 0
        and battery_details["battery_level"] <= battery_level_limit  # 35
        and car_geodata["geofence"] == geofence  # "家"
    ):
        # Check if it's time to remind
        now = datetime.datetime.now()
        hour = now.hour
        today = now.date()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        battery_level = battery_details["battery_level"]

        print(f"{timestamp}: 条件满足，检查是否需要发出提醒...", end="")
        logging.info(f"{timestamp}: 条件满足，检查是否需要发出提醒...")

        if (today not in remind_done) or (
            hour in REMIND_TIMES and today not in remind_done
        ):
            msg = f"充电提醒，当前电量：{battery_level}%"
            print(msg)
            logging.info(msg)
            send_pushover_messages(pushover_token, pushover_group, pushover_device, msg)
            remind_done.append(today)
        else:
            print("不需要提醒")
            logging.info("不需要提醒")

    # Sleep until the next check
    time.sleep(check_interval)
