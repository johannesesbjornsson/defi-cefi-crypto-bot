import unittest
import tokens
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromModule(tokens))
    unittest.TextTestRunner().run(suite)