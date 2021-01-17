"""
Steel Eye Test Runner
"""
import logging
import os
import sys
import unittest

logger = logging.getLogger(__name__)
sh = logging.StreamHandler()
fmt = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s', '%y/%m/%d %H:%M:%S')
sh.setLevel(logging.ERROR)
sh.setFormatter(fmt)
logger.setLevel(logging.ERROR)
logger.addHandler(sh)

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

directory = sys.argv[1].lower()
logger.info('Running unit tests for client: %s', directory)


loader = unittest.TestLoader()
allTests = unittest.TestSuite()
pattern = '[T|t]est*.py'
suite = loader.discover(directory, pattern, '.')
allTests.addTests(suite)

runner = unittest.TextTestRunner(verbosity=0)
result = runner.run(allTests)
if result.wasSuccessful():
    exit(0)
logger.error('Some tests failed.')
exit(1)
