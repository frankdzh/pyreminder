import unittest
from unittest.mock import Mock, patch
import logging
import os

# Import your CarReminder class here
from main import CarReminder

class MyTextTestResult(unittest.TextTestResult):
    fail_count = 0
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def addSuccess(self, test):
        super().addSuccess(test)

    def addFailure(self, test, err):
        self.fail_count += 1
        #super(MyTestRunner, self).addFailure(test, err)
        super().addFailure(test, err)
    
    def shouldStop(self):
        return super().shouldStop(self)
        #return False

class MyTestRunner(unittest.TextTestRunner):
    def __init__(self, *args, **kwargs):
        super(MyTestRunner, self).__init__(*args, **kwargs)
        self.resultclass = MyTextTestResult


class TestCarReminder(unittest.TestCase):
    
    def setUp(self):
        self.car_reminder = CarReminder()

    def test_should_remind_to_charge(self):
       return True
       """  test_cases = [
            {'battery': 19, 'position': 'Home', 'speed': 0, 'expected': True},
            {'battery': 20, 'position': 'Home', 'speed': 0, 'expected': False},
            {'battery': 19, 'position': 'Away', 'speed': 0, 'expected': False},
            {'battery': 19, 'position': 'Home', 'speed': 5, 'expected': False},
        ]

        for i, test_case in enumerate(test_cases):
            with self.subTest(i=i):
                car_status = {
                    'battery': test_case['battery'],
                    'position': test_case['position'],
                    'speed': test_case['speed']
                }
                result = self.car_reminder.should_remind_to_charge(car_status)
                self.assertEqual(result, test_case['expected'])
        """        
    # 辅助函数，用于设置嵌套字典的值
    def set_nested_dict_value(self, dct, keys, value):
        keys = keys.split('.')
        for key in keys[:-1]:
            dct = dct.setdefault(key, {})
        dct[keys[-1]] = value
    
    #@patch('refactored_main.CarReminder.get_car_status')
    #@patch('refactored_main.CarReminder.check_date_crossing')
    #def test_run_method(self, mock_check_date_crossing, mock_get_car_status):
    def test_run_method(self):
        # Mocking methods and return values
        #mock_get_car_status.return_value = {'battery': 19, 'position': 'Home', 'speed': 0}
        #mock_check_date_crossing.return_value = None  # Assuming it returns None

        self.car_reminder.current_hour = 18
        self.car_reminder.remind_enterhome = False

        # 映射简短的变量名到嵌套字典中的完整路径
        key_to_nested_path = {
            'battery_level': 'data.status.battery_details.battery_level',
            'speed': 'data.status.driving_details.speed',
            'geofence': 'data.status.car_geodata.geofence',
            'plugged_in': 'data.status.charging_details.plugged_in',
            'heading': 'data.status.driving_details.heading',
            'shift_state': 'data.status.driving_details.shift_state',
        }
        self.default_check_interval = self.car_reminder.check_interval
        test_cases = [
            #先出小区，在进小区 0-5
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 19, 'speed': 20, 'shift_state': 'D', 'geofence': '家', 'heading': 178, 'check_interval': -1, 'expected1': False, 'expected2': ''},
            {'geofence': '', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'speed': 0, 'shift_state': '', 'heading': 177, 'expected1': True, 'expected2': '进入小区低电量提醒'},
            {'geofence': '家', 'shift_state': 'D', 'expected1': False, 'expected2': ''},
            {'geofence': '', 'shift_state': 'D', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'shift_state': '', 'expected1': True, 'expected2': '进入小区低电量提醒'},
            #检查跨天，第一天低电量提醒过，第二天再次提醒 6-10
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 19, 'speed': 0, 'geofence': '家', 'heading': 182, 'check_interval': -1, 'expected1': False, 'expected2': ''},
            {'date': 1, 'hour': 18, 'expected1': True, 'expected2': '定期充电提醒'},
            {'date': 1, 'hour': 18, 'expected1': False, 'expected2': ''},
            {'date': 2, 'expected1': True , 'expected2': '定期充电提醒'},
            {'date': 2, 'expected1': False, 'expected2': ''},
            # 条件不满足时，不会提醒 11-17
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 39, 'speed': 0, 'shift_state': '', 'geofence': '家', 'heading': 178, 'check_interval': -1, 'expected1': False, 'expected2': ''},
            {'plugged_in': True},
            {'date': 2},
            {'hour': 15},
            {'battery_level': 2},
            {'geofence': ''},
            {'heading': ''},
            # 条件满足时 18-20
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 39, 'speed': 0, 'shift_state': '', 'geofence': '', 'heading': 179, 'check_interval': -1, 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'battery_level': 30, 'expected1': True, 'expected2': '进入小区低电量提醒'},
            {'hour': 12, 'expected1': True, 'expected2': '定期充电提醒'},
            # 检查间隔自动调整 21-31
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 19, 'speed': 30, 'shift_state': 'd', 'geofence': '', 'heading': 178, 'check_interval': -1, 'expected1': False, 'expected2': ''},
            {'geofence': '', 'speed': 0, 'expected1': False, 'expected2': ''},
            {'geofence': '', 'speed': 30, 'expected1': False, 'expected2': ''},
            {'geofence': '', 'geofence': '', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'speed': 0, 'shift_state': '', 'expected1': True, 'expected2': '进入小区低电量提醒'},
            {'geofence': '家', 'expected1': False, 'expected2': ''},
            {'geofence': '', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'expected1': True, 'expected2': '进入小区低电量提醒'},
            # 检查间隔自动调整 32-42
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 19, 'speed': 0, 'shift_state': 'd', 'geofence': '家', 'heading': 180, 'check_interval': -1, 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'speed': 30, 'expected1': False, 'expected2': ''},
            {'geofence': '', 'geofence': '', 'speed': 40, 'expected1': False, 'expected2': ''},
            {'geofence': '', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'speed': 0, 'shift_state': '', 'expected1': True, 'expected2': '进入小区低电量提醒'},
            {'geofence': '家', 'expected1': False, 'expected2': ''},
            {'geofence': '', 'speed': 50, 'expected1': False, 'expected2': ''},
            {'geofence': '', 'speed': 50, 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'speed': 0, 'shift_state': '', 'expected1': True, 'expected2': '进入小区低电量提醒'},
            #定时提醒与进小区提醒是否冲突 43-48
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 19, 'speed': 50, 'shift_state': 'd', 'geofence': '家', 'heading': 182, 'check_interval': -1, 'expected1': False, 'expected2': ''},
            {'geofence': '', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'expected1': False, 'expected2': ''},
            {'date': 2},
            {'date': 3, 'hour': 0, 'expected1': True, 'expected2': '定期充电提醒'},
            {'speed': 0, 'shift_state': '', 'expected1': True, 'expected2': '进入小区低电量提醒'},
            #检查出小区是否取消了提醒 49~54
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 19, 'speed': 0, 'shift_state': '', 'geofence': '家', 'heading': 182, 'check_interval': -1, 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'speed': 30, 'shift_state': 'd', 'expected1': False, 'expected2': ''},
            {'geofence': '', 'geofence': '', 'speed': 40, 'expected1': False, 'expected2': ''},
            {'geofence': '', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'speed': 0, 'shift_state': '', 'expected1': True, 'expected2': '进入小区低电量提醒'},
            #在电量足够情况下，在停车了以后，不提醒，但是检查间隔也要恢复 55-61
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 59, 'speed': 0, 'shift_state': '', 'geofence': '家', 'heading': 181, 'check_interval': -1, 'expected1': False, 'expected2': ''},
            {'geofence': '', 'speed': 30, 'shift_state': 'd', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'speed': 30, 'expected1': False, 'expected2': '', 'check_interval': 1},
            {'geofence': '家', 'speed': 20, 'expected1': False, 'expected2': '', 'check_interval': 1},
            {'geofence': '家', 'speed': 10, 'expected1': False, 'expected2': '', 'check_interval': 1},
            {'geofence': '家', 'speed': 5, 'expected1': False, 'expected2': '', 'check_interval': 1},
            {'geofence': '家', 'speed': 0, 'shift_state': '', 'expected1': False, 'expected2': '', 'check_interval': self.default_check_interval},
            #在外面切换了不同地址 62-
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 59, 'speed': 50, 'shift_state': 'd', 'geofence': '', 'heading': 11, 'check_interval': self.default_check_interval, 'expected1': False, 'expected2': ''},
            {'geofence': '商业街', 'expected1': False, 'expected2': ''},
            {'geofence': '', 'speed': 19, 'battery_level': 35, 'expected1': False, 'expected2': ''},
            {'geofence': '地址2','expected1': False, 'expected2': ''},
            {'geofence': '地址3','expected1': False, 'expected2': ''},
            {'geofence': '家', 'speed': 50, 'expected1': False, 'expected2': '', 'check_interval': 1},
        ]
        
        current_case = {}
        for plugin_i in (1, 2):
            print()
            logging.debug(f"test loop {plugin_i} Start...")
            for i, test_case in enumerate(test_cases):
                with self.subTest(i=i):                
                    car_status = {}
                    current_case.update(test_case)
                    self.assert_check_interval = -1
                    for short_key, value in current_case.items():
                        if short_key != 'expected1' or short_key != 'expected2':
                            if short_key == 'hour':
                                self.car_reminder.current_hour = current_case['hour']
                            elif short_key == 'date':
                                self.current_date = current_case['date']
                            elif short_key == 'check_interval':
                                self.assert_check_interval = current_case['check_interval']
                            else:              
                                full_path = key_to_nested_path.get(short_key)
                                if full_path:
                                    self.set_nested_dict_value(car_status, full_path, value)
                    
                    # ... 进行测试
                    if i == 63:
                        test = True
                        #logging.warning(f'{i}...')
                    if (plugin_i == 2): #测试所有的插电的情况下，应该所有testcase不会提醒
                        car_status['data']['status']['charging_details']['plugged_in'] = True
                        current_case['expected1'] = False
                        self.assert_check_interval= -1

                    self.car_reminder.check_date_crossing(self.current_date)
                    self.car_reminder.check_car_enterhome(car_status["data"]["status"]["car_geodata"]['geofence'])
                    bShouldRemind, msghead = self.car_reminder.remind_to_charge_if_needed(car_status)
                    
                    #发现在家里停好车位了，如果没有触发提醒，也该恢复正常检测间隔了
                    if self.car_reminder.is_car_at_home(car_status) and self.car_reminder.is_car_parked(car_status):
                        self.car_reminder.reset_check_interval(True)

                    try:
                        self.assertEqual(bShouldRemind, current_case['expected1'])
                        if (current_case['expected1'] == True):
                            self.assertEqual(msghead, current_case['expected2'])
                        
                        if (bShouldRemind != current_case['expected1']):
                            test = True
                        
                        if (self.assert_check_interval > 0):
                            self.assertEqual(self.assert_check_interval ,self.car_reminder.check_interval)

                        #logging.warning(f"{i}# self.check_interval={self.car_reminder.check_interval}")
                        if (self.car_reminder.check_interval == 1):
                            print("-", end="")
                        else:
                            print("+", end="")
                    except AssertionError:
                        logging.error(f"\r\nTest case loop:{plugin_i}[{i}#] failed: result1={bShouldRemind}, result2={msghead}, testcase= {current_case}")
                        raise  # 重新抛出断言错误，以便测试结果能反映这个失败            
            print()
            logging.debug(f"test loop {plugin_i} End")
        ##
        print()
        logging.debug(f"Ran {len(test_cases)} Test cases\r\n")#, Total failed tests: {runner.resultclass.fail_count}\r\n")
        # Verify that the mocked methods were called
        #mock_get_car_status.assert_called()
        #mock_check_date_crossing.assert_called_with("2023-08-28")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARN)
    #logging.getLogger().setLevel(logging.INFO)

    runner = MyTestRunner()#verbosity=2)
    unittest.main(testRunner=runner)
