import unittest
import tokens
import txn_analysis
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromModule(tokens))
    suite.addTest(unittest.TestLoader().loadTestsFromModule(txn_analysis))
    unittest.TextTestRunner().run(suite)