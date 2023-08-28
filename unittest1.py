import unittest
from unittest.mock import Mock, patch
import logging

# Import your CarReminder class here
from refactored_main import CarReminder

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
        }


        test_cases = [
            #先出小区，在进小区 0-5
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 19, 'speed': 0, 'geofence': '家', 'heading': 182, 'expected1': False, 'expected2': ''},
            {'geofence': '', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'expected1': True, 'expected2': '进入小区低电量提醒'},
            {'geofence': '家', 'expected1': False, 'expected2': ''},
            {'geofence': '', 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'expected1': True, 'expected2': '进入小区低电量提醒'},
            #检查跨天，第一天低电量提醒过，第二天再次提醒 6-10
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 19, 'speed': 0, 'geofence': '家', 'heading': 182, 'expected1': False, 'expected2': ''},
            {'date': 1, 'hour': 18, 'expected1': True, 'expected2': '定期充电提醒'},
            {'date': 1, 'hour': 18, 'expected1': False, 'expected2': ''},
            {'date': 2, 'expected1': True , 'expected2': '定期充电提醒'},
            {'date': 2, 'expected1': False, 'expected2': ''},
            # 条件不满足时，不会提醒 11-17
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 39, 'speed': 0, 'geofence': '家', 'heading': 182, 'expected1': False, 'expected2': ''},
            {'plugged_in': True},
            {'date': 2},
            {'hour': 15},
            {'battery_level': 2},
            {'geofence': ''},
            {'heading': ''},
            # 条件满足时
            {'plugged_in': False, 'date': 1, 'hour': 11, 'battery_level': 39, 'speed': 0, 'geofence': '', 'heading': 182, 'expected1': False, 'expected2': ''},
            {'geofence': '家', 'expected1': True, 'expected2': '进入小区低电量提醒'},
            {'hour': 12, 'expected1': True, 'expected2': '定期充电提醒'},
        ]
        
        current_case = {}
        for i, test_case in enumerate(test_cases):
            with self.subTest(i=i):                
                car_status = {}
                current_case.update(test_case)
                for short_key, value in current_case.items():
                    if short_key != 'expected1' or short_key != 'expected2':
                        if short_key == 'hour':
                            self.car_reminder.current_hour = current_case['hour']
                        elif short_key == 'date':
                            self.current_date = current_case['date']
                        else:              
                            full_path = key_to_nested_path.get(short_key)
                            if full_path:
                                self.set_nested_dict_value(car_status, full_path, value)
                
                # ... 进行测试
                if i == 15:
                    test = True
                self.car_reminder.check_date_crossing(self.current_date)
                self.car_reminder.check_car_enterhome(car_status["data"]["status"]["car_geodata"]['geofence'])
                result1, result2 = self.car_reminder.should_remind_to_charge(car_status)
                try:
                    self.assertEqual(result1, current_case['expected1'])
                    self.assertEqual(result2, current_case['expected2'])                    
                except AssertionError:
                    logging.error(f"Test case {i}# failed: result1={result1}, result2={result2}, testcase= {current_case}")
                    raise  # 重新抛出断言错误，以便测试结果能反映这个失败


        # Verify that the mocked methods were called
        #mock_get_car_status.assert_called()
        #mock_check_date_crossing.assert_called_with("2023-08-28")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARN)
    unittest.main()
