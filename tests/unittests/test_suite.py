import unittest
import test_suite
import market_tests
import sales_tests
import order_tests
import historical_data_tests

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromModule(sales_tests))
    suite.addTest(unittest.TestLoader().loadTestsFromModule(market_tests))
    suite.addTest(unittest.TestLoader().loadTestsFromModule(order_tests))
    suite.addTest(unittest.TestLoader().loadTestsFromModule(historical_data_tests))
    unittest.TextTestRunner().run(suite)