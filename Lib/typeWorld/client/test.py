import sys, os
if 'TRAVIS' in os.environ:
	sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


import unittest
from typeWorld.client import APIClient, JSON, AppKitNSUserDefaults
import tempfile, os, traceback
tempFolder = tempfile.mkdtemp()
prefFile = os.path.join(tempFolder, 'preferences.json')
prefs = JSON(prefFile)
client = APIClient(preferences = prefs)

class TestStringMethods(unittest.TestCase):

	def test_normalSubscription(self):

		success, message, publisher, subscription = client.addSubscription('typeworld://json+https//typeworldserver.com/api/toy6FQGX6c368JlntbxR/')
		print(success, message, publisher, subscription)

		self.assertEqual(success, True)
		self.assertEqual(publisher.canonicalURL, 'https://typeworldserver.com/api/toy6FQGX6c368JlntbxR/')
		self.assertEqual(len(publisher.subscriptions()), 1)
		self.assertEqual(len(publisher.subscriptions()[-1].protocol.installableFontsCommand().foundries), 1)
		self.assertEqual(publisher.subscriptions()[-1].protocol.installableFontsCommand().foundries[0].name.getTextAndLocale(), ('Yanone', 'en'))

		for subscription in publisher.subscriptions():
			subscription.delete()


		# Protected subscription

		client.linkUser('736b524a-cf24-11e9-9f62-901b0ecbcc7a', 'AApCEfatt6vE5H4m0pevPsQA9P7fYG8Q1uhsNFYV')

		success, message, publisher, subscription = client.addSubscription('typeworld://json+https//SeQQvpPEo9MxfBLmiGOm:AxYZcH9MV4vFrttVFEKY@typeworldserver.com/api/toy6FQGX6c368JlntbxR/')
		print(success, message, publisher, subscription)

		self.assertEqual(success, True)
		self.assertEqual(publisher.canonicalURL, 'https://typeworldserver.com/api/toy6FQGX6c368JlntbxR/')
		self.assertEqual(len(publisher.subscriptions()), 1)
		self.assertEqual(len(publisher.subscriptions()[-1].protocol.installableFontsCommand().foundries), 1)
		self.assertEqual(publisher.subscriptions()[-1].protocol.installableFontsCommand().foundries[0].name.getTextAndLocale(), ('Yanone', 'en'))

		# Sync subscription
		client.downloadSubscriptions()

		# Install Font
		font = publisher.subscriptions()[-1].protocol.installableFontsCommand().foundries[0].families[0].fonts[0]
		self.assertEqual(publisher.subscriptions()[-1].installFont(font.uniqueID, font.getVersions()[-1].number), (False, ['#(response.termsOfServiceNotAccepted)', '#(response.termsOfServiceNotAccepted.headline)']))
		publisher.subscriptions()[-1].set('acceptedTermsOfService', True)
		self.assertEqual(publisher.subscriptions()[-1].installFont(font.uniqueID, font.getVersions()[-1].number), (False, ['#(response.revealedUserIdentityRequired)', '#(response.revealedUserIdentityRequired.headline)']))
		publisher.subscriptions()[-1].set('revealIdentity', True)
		self.assertEqual(publisher.subscriptions()[-1].installFont(font.uniqueID, font.getVersions()[-1].number), (True, None))

		publisher.subscriptions()[-1].removeFont(font.uniqueID)

	def test_takedown(self):

		for subscription in client.publishers()[0].subscriptions():
			subscription.delete()

		client.unlinkUser()

if __name__ == '__main__':
	unittest.main()


 # Local
if not 'TRAVIS' in os.environ:
	os.remove(prefFile)
	os.rmdir(tempFolder)
