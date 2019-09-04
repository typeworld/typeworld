import sys, os
if 'TRAVIS' in os.environ:
	sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


import unittest
from typeWorld.client import APIClient, JSON, AppKitNSUserDefaults
import tempfile, os, traceback
tempFolder = tempfile.mkdtemp()
prefFile = os.path.join(tempFolder, 'preferences.json')

class TestStringMethods(unittest.TestCase):

	def test_client(self):
		prefs = JSON(prefFile)
		client = APIClient(preferences = prefs)

		success, message, publisher, subscription = client.addSubscription('typeworld://json+https//typeworldserver.com/api/toy6FQGX6c368JlntbxR/')

		self.assertEqual(success, True)
		self.assertEqual(publisher.canonicalURL, 'https://typeworldserver.com/api/toy6FQGX6c368JlntbxR/')
		self.assertEqual(len(publisher.subscriptions()), 1)
		self.assertEqual(len(publisher.subscriptions()[0].foundries()), 1)
		self.assertEqual(publisher.subscriptions()[0].foundries()[0].name.getTextAndLocale(), ('Yanone', 'en'))


if __name__ == '__main__':
	unittest.main()


 # Local
if not 'TRAVIS' in os.environ:
	os.remove(prefFile)
	os.rmdir(tempFolder)
