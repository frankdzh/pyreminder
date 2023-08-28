# Now let's fill in the implementation details of the CarReminder class by referencing the original code.
# Since the original code uses some external modules like requests, which can't be run in this environment,
# the relevant methods will be left as placeholders.

import datetime
import time
import os
from dotenv import load_dotenv
import requests
import logging

class CarReminder:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self.pushover_token = os.getenv("PUSHOVER_TOKEN")
        self.pushover_user = os.getenv("PUSHOVER_GROUP")
        self.pushover_device = os.getenv("PUSHOVER_DEVICE_NAME")
        self.pushover_enabled = os.getenv("PUSHOVER_ENABLED", "false")
        self.pushover_enabled = self.pushover_enabled.lower() == "true"

        self.url = os.getenv("CAR_STATUS_URL")
        self.speed_limit = int(os.getenv("SPEED_LIMIT"))
        self.battery_level_limit = int(os.getenv("BATTERY_LEVEL_LIMIT"))
        self.remind_times = [int(x) for x in os.getenv("REMIND_TIMES").split(",")]
        self.car_geofence_limit = os.getenv("CAR_GEOFENCE", "家")

        self.check_interval = float(os.getenv("CHECK_INTERVAL", 60))
        self.log_interval = float(os.getenv("LOG_INTERVAL", 60))
        
        #self.last_reminded_time = None  # To track the last time a reminder was sent        
        self.remind_time_done = []

        # Initialize previous states for boundary checks
        self.prev_state = {
            'car_position': None,
            'date': None,
            #'remind_low_bettery': None
        }
        #self.init_logger()

    def init_logger(self):
        # 创建Logger对象
        logger = logging.getLogger()
        #logger.setLevel(logging.INFO)

        # 创建StreamHandler并设置日志级别
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)

        # 创建Formatter并设置日志格式
        formatter = logging.Formatter('%(message)s')
        stream_handler.setFormatter(formatter)

        # 将StreamHandler添加到Logger
        logger.addHandler(stream_handler)
        
        self.logger = logger

    def set_remind_enterhome(self, bSet):
        self.remind_enterhome = bSet
        if bSet:
            self.check_interval = 1
            #logging.warning(f"self.check_interval={self.check_interval}")
        else:                
            self.check_interval = float(os.getenv("CHECK_INTERVAL", 60))
            #logging.warning(f"self.check_interval={self.check_interval}")

    # Method to check if car's position has entered 'Home'
    def check_car_enterhome(self, current_position):
        bret = False
        if (self.prev_state['car_position'] == None):
            self.prev_state['car_position'] = current_position

        if self.prev_state['car_position'] != current_position:
            # Initialize your variables here            
            if self.prev_state['car_position'] == self.car_geofence_limit:
                #logging.info("触发过一次进小区了，解除提醒")
                bret = False
                self.set_remind_enterhome(False)
            else:
                #logging.info("首次进入小区，设置提醒")
                self.set_remind_enterhome(True)
                
        self.prev_state['car_position'] = current_position
        return bret
    
    # Method to check if the date has crossed to a new day
    def check_date_crossing(self, current_date):
        bret = False
        if self.prev_state['date'] is not None and current_date != self.prev_state['date']:
            bret = True
            logging.info("Date has changed. Initializing variables...")
            # Initialize your variables here
            self.remind_time_done = []
        self.prev_state['date'] = current_date
        return bret

    def send_pushover_message(self, message):
        """
        发送 Pushover 消息
        """
        # Placeholder for sending a Pushover message
        #logging.info(f"Sending Pushover message: {message}")        
        if (self.pushover_enabled):
            # Pushover API url
            url = "https://api.pushover.net/1/messages.json"

            # Send the message to each user
            # Send the message to the group
            payload = {
                "token": self.pushover_token,
                "user": self.pushover_user,
                "message": message,
                "device": self.pushover_device,
                "sound": "pushover",
            }
            #response = requests.post(url, data=data)
            response = requests.post(url, data=payload)
            # if response.status_code == 200:

            #print(f"Sent message to {group}, status: {response.status_code}")
            logging.info(f"{self.get_timestamp()}:发送消息 '{message}', status: {response.status_code}")
        else:
            logging.info(f"{self.get_timestamp()}:禁用了发送消息 '{message}'")

    def get_car_status(self):
        """
        获取车辆状态（电量，速度，位置等）
        """
        # 在常规的 Python 环境中取消下面这行的注释
        response = requests.get(self.url)
        
        # 检查响应是否成功
        if response.status_code == 200:
            car_status = response.json()
            return car_status
        else:
            logging.error(f"获取车辆状态失败：{response.content}")
            return None
        
        #return {"battery_level": 20, "speed": 0, "location": "home", "charging": False}

    def is_car_at_home(self, car_status):
        """
        判断车辆是否在家的地理范围内
        """
        return car_status["data"]["status"]["car_geodata"]['geofence'] == self.car_geofence_limit

    def is_car_parked(self, car_status):
        """
        判断车辆是否停好了
        """
        speed0 = car_status["data"]["status"]["driving_details"]["speed"] == 0
        bParkHead = car_status["data"]["status"]["driving_details"]["heading"] == 182 #todo:头朝里也要判断
        return speed0 and bParkHead

    def is_car_charging(self, car_status):
        """
        判断车辆是否正在充电
        """
        return car_status["data"]["status"]["charging_details"]["plugged_in"]

    def is_car_low_battery_level(self, car_status):
        battery_level = car_status["data"]["status"]["battery_details"]["battery_level"]
        return battery_level < self.battery_level_limit
    
    def get_timestamp(self):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        return timestamp

    def print_condition(self, car_status):
        current_battery = car_status["data"]["status"]["battery_details"]["battery_level"]
        current_speed = car_status["data"]["status"]["driving_details"]["speed"]
        current_cargeo = car_status["data"]["status"]["car_geodata"]['geofence']
        logging.info(
            f"{self.get_timestamp()}: 检查-> 当前电量:{current_battery}% <= 报警电量:{self.battery_level_limit}%, 当前速度:{current_speed} <= 报警速度:{self.speed_limit}, 当前位置:{current_cargeo} == 报警位置:{self.car_geofence_limit}...")
    
    def print_log(self, car_status):
        current_time = time.time()
        self.elapsed_time = int(current_time - self.start_time)

        if self.elapsed_time % 5 == 0 and self.elapsed_time != 0:
            print('.', end='')
            #self.logger.info('.', extra={'end': ''})
        if self.elapsed_time >= self.log_interval:
            self.start_time = time.time()
            print()
            #self.logger.info('', extra={'end': '\r\n'})
            self.print_condition(car_status)

    def should_remind_to_charge(self, car_status):
        """
        判断是否需要提醒充电
        """
        # 每次当车辆首次进入家的地理范围时，需要停车时提醒
        if self.remind_enterhome and self.is_car_parked(car_status):
            self.set_remind_enterhome(False) #提醒过了，就不用再提醒，除非再次出小区
            return True, "进入小区低电量提醒"

        # 根据配置定期提醒
        if self.current_hour in self.remind_times:
            if self.current_hour not in self.remind_time_done:
                self.remind_time_done.append(self.current_hour)
                return True, "定期充电提醒"

        return False, ""

    def remind_to_charge_if_needed(self, car_status):
        """
        如果需要，则提醒充电
        """
        bShouldRemind = False
        msghead = ''
        if self.is_car_low_battery_level(car_status):
            if self.is_car_at_home(car_status):
                if not self.is_car_charging(car_status):        
                    bShouldRemind, msghead = self.should_remind_to_charge(car_status)
                    if bShouldRemind:
                        current_battery = car_status["data"]["status"]["battery_details"]["battery_level"]
                        msg = f"{msghead}，当前电量：{current_battery}% <= 报警电量: {self.battery_level_limit}%"
                        self.send_pushover_message(msg)
                        #self.last_reminded_time = datetime.datetime.now()
                        self.set_remind_enterhome(False)
        if self.is_car_parked(car_status) and self.is_car_at_home(car_status):
            self.set_remind_enterhome(False)
        return bShouldRemind, msghead        

    def run(self):
        """
        主运行函数，周期性地检查车辆状态并发送提醒
        """        
        self.print_condition(self.get_car_status())
        
        self.start_time = time.time()
        while True:
            self.current_hour = datetime.datetime.now().hour
            
            car_status = self.get_car_status()
            # 检测是否跨天
            self.check_date_crossing(datetime.datetime.now().date())
            # 检测位置是否进入小区
            self.check_car_enterhome(car_status["data"]["status"]["car_geodata"]['geofence'])

            self.remind_to_charge_if_needed(car_status)

            self.print_log(car_status)

            time.sleep(self.check_interval)

# Initialize the class with dummy values for demonstration
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    car_reminder = CarReminder()
    car_reminder.run()
