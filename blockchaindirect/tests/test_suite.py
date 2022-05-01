import unittest
import tokens_tests
import txn_analysis_tests
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromModule(tokens_tests))
    suite.addTest(unittest.TestLoader().loadTestsFromModule(txn_analysis_tests))
    unittest.TextTestRunner().run(suite)