import meteobot
import unittest

class TestForecast(unittest.TestCase):
    def test_function(self):
        forecast = meteobot.Forecast()
        self.assertEqual(forecast.func_for_testing(5, 3), 8, '5 + 3 should be 8')

    def test_user(self):
        user = meteobot.User()
        self.assertEquals(user.return_hello(), 'hello', 'shoud be hello')

if __name__ == '__main__':
    unittest.main()