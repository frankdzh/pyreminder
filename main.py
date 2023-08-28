import requests
import time
import datetime
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()
logging.basicConfig(level=logging.INFO)

pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user = os.getenv("PUSHOVER_GROUP")
pushover_device = os.getenv("PUSHOVER_DEVICE_NAME")

URL = os.getenv("CAR_STATUS_URL")
speed_limit = int(os.getenv("SPEED_LIMIT"))
battery_level_limit = int(os.getenv("BATTERY_LEVEL_LIMIT"))
REMIND_TIMES = [int(x) for x in os.getenv("REMIND_TIMES").split(",")]
car_geofence_limit = os.getenv("CAR_GEOFENCE", "家")

pushover_enabled = os.getenv("PUSHOVER_ENABLED", "false")
pushover_enabled = pushover_enabled.lower() == "true"

check_interval = float(os.getenv("CHECK_INTERVAL", 60))
battery_alarm_triggered = False  # 只在跨越临界值时通知一次
last_battery = 0
last_date = datetime.datetime.now().date() - datetime.timedelta(days=1)
current_plugged_in = False
current_doors_open = False
current_shift_state = ""

remind_enter_geofence = int(os.getenv("REMIND_ENTER_GEOFENCE", 20))
last_geofence = car_geofence_limit
is_enter_home = False
#old_interver = check_interval;

def get_timestamp():
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp

def reset_check_interval():
    global check_interval
    check_interval = float(os.getenv("CHECK_INTERVAL", 60))
    return check_interval

def set_check_interval(new_interval):
    global check_interval
    check_interval = new_interval
    return check_interval


def send_pushover_messages(token, user, device, message):
    reset_check_interval() #发消息就重置
    if (pushover_enabled):
        # Pushover API url
        url = "https://api.pushover.net/1/messages.json"

        # Send the message to each user
        # Send the message to the group
        data = {
            "token": token,
            "user": user,
            "message": message,
            "device": device,
            "sound": "pushover",
        }
        response = requests.post(url, data=data)
        #print(f"Sent message to {group}, status: {response.status_code}")
        logging.info(f"{get_timestamp()}:发送消息 '{message}' to {user}, status: {response.status_code}")
    else:
        logging.info(f"{get_timestamp()}:禁用了发送消息 '{message}' to {user}")

def check_car_status_and_send_reminders(
    today, hour, current_battery, current_speed, current_cargeo
):
    global last_date, battery_alarm_triggered, remind_time_done, last_battery, last_geofence, is_enter_home
    # 记录出入小区标记，只在进出小区时触发一次
    if (last_geofence != current_cargeo):
        if (last_geofence == car_geofence_limit):
            is_enter_home = False #自从上次离开了小区后，触发过一次进小区了，解除
        else:
            is_enter_home = True
    
    if (is_enter_home):        
        set_check_interval(1) #临时设置为1秒，发送消息后重置
    else:
        reset_check_interval()
    
    if(current_plugged_in):
        reset_check_interval()

    if (
        current_speed <= speed_limit  # 0
        and current_battery <= battery_level_limit  # 35
        and current_cargeo == car_geofence_limit  # "家"
        and not current_plugged_in
    ):
        #now = datetime.datetime.now()
        #hour = now.hour
        #today = now.date()


        if (last_date != today):
            remind_time_done = []
            last_date = today

        bTriggerOnce = current_battery < last_battery and current_battery == battery_level_limit and battery_alarm_triggered == False
        bPeriodic_reminder = hour in REMIND_TIMES and hour not in remind_time_done
        #只要电量低并且在家，并且距离上次提醒超过5分钟
        #bTriggerManyTimes = hour >= remind_manytime and datetime.datetime.now() >= (last_manytime_trigger_time + datetime.timedelta(seconds=repeat_warning_interval))
        bTriggerEnterHome = hour >= remind_enter_geofence and is_enter_home and current_doors_open# and last_geofence != car_geofence_limit #如果进小区时，速度超过speed_limt，这里永远都不会报警
        
        if bTriggerOnce:
            msg = f"跨越边界提醒，当前电量：{current_battery}% <= 报警电量: {battery_level_limit}%"
            logging.info(f"{get_timestamp()}: {msg}")
            send_pushover_messages(pushover_token, pushover_user, pushover_device, msg)
            battery_alarm_triggered = True
            return "跨越边界提醒已发送"

        if bPeriodic_reminder:
            msg = f"定期充电提醒，当前电量：{current_battery}% <= 报警电量: {battery_level_limit}%"
            logging.info(f"{get_timestamp()}: {msg}")
            send_pushover_messages(pushover_token, pushover_user, pushover_device, msg)
            remind_time_done.append(hour)
            return "定期充电提醒已发送"
        
        if (bTriggerEnterHome):
            msg = f"进小区电量低充电提醒，当前电量：{current_battery}% <= 报警电量: {battery_level_limit}%"
            logging.info(f"{get_timestamp()}: {msg}")
            send_pushover_messages(pushover_token, pushover_user, pushover_device, msg)
            #last_manytime_trigger_time = datetime.datetime.now()
            is_enter_home = False
            return "晚上进入小区时电量低提醒已发送"
    
        if (current_battery > battery_level_limit):
            battery_alarm_triggered = False
    return "无需提醒"

def main():
    # Main loop (will be executed in the actual environment)
    global last_battery, current_plugged_in, last_geofence, current_doors_open, current_shift_state

    while True:
        response = requests.get(URL)
        data = response.json()
        
        current_plugged_in = data["data"]["status"]["charging_details"]["plugged_in"]
        
        current_battery = data["data"]["status"]["battery_details"]["battery_level"]
        current_speed = data["data"]["status"]["driving_details"]["speed"]
        current_cargeo = data["data"]["status"]["car_geodata"]['geofence']
        current_doors_open = data["data"]["status"]["car_status"]['doors_open'] #需要验证能否获取
        current_shift_state = data["data"]["status"]["driving_details"]["shift_state"] #需要验证能否获取以及获取的内容是什么
        #"charging_details": {"plugged_in": true,}

        logging.info(
            f"{get_timestamp()}: 检查-> 当前电量:{current_battery}% <= 报警电量:{battery_level_limit}%, 当前速度:{current_speed} <= 报警速度:{speed_limit}, 当前位置:{current_cargeo} == 报警位置:{car_geofence_limit}...")
        
        now = datetime.datetime.now()
        hour = now.hour
        today = now.date()
        check_car_status_and_send_reminders(today, hour, current_battery, current_speed, current_cargeo)

        last_battery = current_battery
        last_geofence = current_cargeo
        time.sleep(check_interval)

if __name__ == "__main__":
    main()