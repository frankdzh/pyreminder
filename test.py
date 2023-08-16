import datetime
import unittest
import responses
import os
import main  # Assuming the original code is in a file named main.py
import logging


class IntegrationTest(unittest.TestCase):

    def setUp(self):
        # Setting up environment variables required for the test
        #os.environ['SPEED_LIMIT'] = '50'
        #os.environ['BATTERY_LEVEL_LIMIT'] = '30'
        #os.environ['REMIND_TIMES'] = '10,12'
        # ... set other environment variables as needed
        os.environ['REMIND_TIMES111'] = '10,12'

    @responses.activate
    def test_battery_boundary_reminder(self):
        #logging.getLogger().setLevel(logging.WARN)
        # Mocking the API response for the car status
        #responses.add(responses.GET, main.URL,
        #              json={"data": {"status": {"battery_details": {"battery_level": 30},
        #                                        "driving_details": {"speed": 0},
        #                                        "car_geodata": {'geofence': '家'}}}}, status=200)
        now = datetime.datetime.now()
        hour = now.hour
        today = now.date()

        # 跨越边界========================================================
        main.last_battery = 36
        current_battery = 35
        result = main.check_car_status_and_send_reminders(today, 3, current_battery, 0, "家")
        self.assertEqual(result, "跨越边界提醒已发送")
        #已经通知过了
        main.battery_alarm_triggered = True
        result = main.check_car_status_and_send_reminders(today, 3, current_battery, 0, "家")
        self.assertEqual(result, "无需提醒")
        
        #已经通知过了, 但是过了一段时间后，电池又达到临界条件
        main.last_battery = 36
        main.battery_alarm_triggered = False
        result = main.check_car_status_and_send_reminders(today, 3, current_battery, 0, "家")
        main.last_battery = 36
        current_battery = 35
        result = main.check_car_status_and_send_reminders(today, 3, current_battery, 0, "家")
        self.assertEqual(result, "无需提醒")

        #已经通知过了,第二天充电后，电池又达到临界条件
        main.last_battery = 36        
        main.battery_alarm_triggered = False
        current_battery = 40
        result = main.check_car_status_and_send_reminders(today, 3, current_battery, 0, "家")
        main.last_battery = 36
        day = today + datetime.timedelta(days=1)
        main.last_date = day - datetime.timedelta(days=1)
        current_battery = main.battery_level_limit
        result = main.check_car_status_and_send_reminders(day, 3, current_battery, 0, "家")
        self.assertEqual(result, "跨越边界提醒已发送")
        #=================================================================

        #电量=============================================================
        main.last_battery = 35
        main.battery_alarm_triggered = False
        result = main.check_car_status_and_send_reminders(today, 3, 35, 0, "家")
        self.assertEqual(result, "无需提醒")
        
        main.last_battery = main.battery_level_limit + 1
        result = main.check_car_status_and_send_reminders(today, 3, main.battery_level_limit, 0, "家")
        self.assertEqual(result, "跨越边界提醒已发送")
        # > 
        result = main.check_car_status_and_send_reminders(today, 10, main.battery_level_limit + 10, 0, "家")
        self.assertEqual(result, "无需提醒")
        
        #跨天测试
        main.last_date = today - datetime.timedelta(days=1)
        result = main.check_car_status_and_send_reminders(today, 0, 30, 0, "家")
        self.assertEqual(result, "无需提醒")

    #@responses.activate
    def test_scheduled_reminders(self):
        self.test_reminders()

    def test_reminders(self):
        logging.getLogger().setLevel(logging.WARN)
        # Mocking the API response for the car status
        #responses.add(responses.GET, main.URL,
        #              json={"data": {"status": {"battery_details": {"battery_level": 40},
        #                                        "driving_details": {"speed": 0},
        #                                        "car_geodata": {'geofence': '家'}}}}, status=200)
        now = datetime.datetime.now()
        today = now.date()
        main.last_battery = 35        
        main.current_plugged_in = False
        main.remind_time_done = []
        # Mocking the datetime to be at one of the remind times
        # ...
        main.battery_alarm_triggered = True
        result = main.check_car_status_and_send_reminders(today, 6, 35, 0, "家")
        self.assertEqual(result, "定期充电提醒已发送")
        result = main.check_car_status_and_send_reminders(today, 12, 35, 0, "家")
        self.assertEqual(result, "定期充电提醒已发送")
        result = main.check_car_status_and_send_reminders(today, 18, 35, 0, "家")
        self.assertEqual(result, "定期充电提醒已发送")
        result = main.check_car_status_and_send_reminders(today, 22, 35, 0, "家")
        self.assertEqual(result, "定期充电提醒已发送")

        result = main.check_car_status_and_send_reminders(today, 6, 35, 0, "家")
        self.assertEqual(result, "无需提醒")
        result = main.check_car_status_and_send_reminders(today, 12, 35, 0, "家")
        self.assertEqual(result, "无需提醒")
        result = main.check_car_status_and_send_reminders(today, 18, 35, 0, "家")
        self.assertEqual(result, "无需提醒")
        result = main.check_car_status_and_send_reminders(today, 22, 35, 0, "家")
        self.assertEqual(result, "无需提醒")

        main.battery_alarm_triggered = False
        main.remind_time_done = []
        result = main.check_car_status_and_send_reminders(today, 6, 35, 0, "家")
        self.assertEqual(result, "定期充电提醒已发送")
        result = main.check_car_status_and_send_reminders(today, 12, 35, 0, "家")
        self.assertEqual(result, "定期充电提醒已发送")
        result = main.check_car_status_and_send_reminders(today, 18, 35, 0, "家")
        self.assertEqual(result, "定期充电提醒已发送")
        result = main.check_car_status_and_send_reminders(today, 22, 35, 0, "家")
        self.assertEqual(result, "定期充电提醒已发送")

        result = main.check_car_status_and_send_reminders(today, 6, 35, 0, "家")
        self.assertEqual(result, "无需提醒")
        result = main.check_car_status_and_send_reminders(today, 12, 35, 0, "家")
        self.assertEqual(result, "无需提醒")
        result = main.check_car_status_and_send_reminders(today, 18, 35, 0, "家")
        self.assertEqual(result, "无需提醒")
        result = main.check_car_status_and_send_reminders(today, 22, 35, 0, "家")
        self.assertEqual(result, "无需提醒")
    
    def test_EnterOuterHome(self):
        now = datetime.datetime.now()
        today = now.date()
        main.remind_time_done = []
        # 先出小区，再进小区
        main.current_plugged_in = False
        main.last_geofence = "家"
        result = main.check_car_status_and_send_reminders(today, 21, 35, 30, '')
        main.last_geofence = ''
        result = main.check_car_status_and_send_reminders(today, 21, 35, 30, "家")
        main.last_geofence = "家"
        result = main.check_car_status_and_send_reminders(today, 21, 35, 0, "家")
        self.assertEqual(result, "晚上进入小区时电量低提醒已发送")
        main.last_geofence = "家"
        result = main.check_car_status_and_send_reminders(today, 21, 35, 0, "家")
        self.assertEqual(result, "无需提醒")
        #在外面跑
        main.last_geofence = ""
        result = main.check_car_status_and_send_reminders(today, 11, 35, 50, "")
        self.assertEqual(result, "无需提醒")
        result = main.check_car_status_and_send_reminders(today, 11, 35, 0, "")
        self.assertEqual(result, "无需提醒")
        result = main.check_car_status_and_send_reminders(today, 11, 35, 40, "")
        self.assertEqual(result, "无需提醒")
        

    def test_plugin(self):
        now = datetime.datetime.now()
        today = now.date()
        main.remind_time_done = []
        # 先出小区，再进小区
        main.current_plugged_in = False
        result = main.check_car_status_and_send_reminders(today, 22, 35, 0, "家")
        main.last_geofence = ''
        result = main.check_car_status_and_send_reminders(today, 22, 35, 0, "家")
        self.assertEqual(result, "晚上进入小区时电量低提醒已发送")
        main.last_geofence = "家"
        result = main.check_car_status_and_send_reminders(today, 22, 35, 0, "家")
        self.assertEqual(result, "无需提醒")

    def test_sound(self):        
        last = main.pushover_enabled
        main.pushover_enabled = True
        #main.send_pushover_messages(main.pushover_token, main.pushover_user, "test", "test message")
        main.pushover_enabled = last

# Running the tests
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARN)
    unittest.main()
