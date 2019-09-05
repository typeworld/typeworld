import sys, os
if 'TRAVIS' in os.environ:
	sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


import unittest
from typeWorld.client import APIClient, JSON, AppKitNSUserDefaults
import tempfile, os, traceback
tempFolder = tempfile.mkdtemp()

prefs = JSON(os.path.join(tempFolder, 'preferences.json'))
client = APIClient(preferences = prefs)

prefs2 = JSON(os.path.join(tempFolder, 'preferences2.json'))
client2 = APIClient(preferences = prefs)

freeSubscription = 'typeworld://json+https//typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/'
protectedSubscription = 'typeworld://json+https//s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/'
testUser = ('736b524a-cf24-11e9-9f62-901b0ecbcc7a', 'AApCEfatt6vE5H4m0pevPsQA9P7fYG8Q1uhsNFYV')


class TestStringMethods(unittest.TestCase):

	def test_normalSubscription(self):


		## Test a simple subscription of free fonts


		success, message, publisher, subscription = client.addSubscription(freeSubscription)
		print(success, message)

		self.assertEqual(success, True)
		self.assertEqual(publisher.canonicalURL, 'https://typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/')
		self.assertEqual(len(publisher.subscriptions()), 1)
		self.assertEqual(len(publisher.subscriptions()[-1].protocol.installableFontsCommand().foundries), 1)
		self.assertEqual(publisher.subscriptions()[-1].protocol.installableFontsCommand().foundries[0].name.getTextAndLocale(), ('Test Foundry', 'en'))

		for subscription in publisher.subscriptions():
			subscription.delete()


		# Protected subscription, installation on first machine

		client.linkUser(*testUser)

		success, message, publisher, subscription = client.addSubscription(protectedSubscription)
		print(success, message)

		self.assertEqual(success, True)
		self.assertEqual(len(publisher.subscriptions()), 1)
		self.assertEqual(len(publisher.subscriptions()[-1].protocol.installableFontsCommand().foundries), 1)

		client.downloadSubscriptions()

		# Install Font
		font = client.publishers()[0].subscriptions()[-1].protocol.installableFontsCommand().foundries[0].families[0].fonts[0]
		self.assertEqual(client.publishers()[0].subscriptions()[-1].installFont(font.uniqueID, font.getVersions()[-1].number), (False, ['#(response.termsOfServiceNotAccepted)', '#(response.termsOfServiceNotAccepted.headline)']))
		client.publishers()[0].subscriptions()[-1].set('acceptedTermsOfService', True)
		self.assertEqual(client.publishers()[0].subscriptions()[-1].installFont(font.uniqueID, font.getVersions()[-1].number), (False, ['#(response.revealedUserIdentityRequired)', '#(response.revealedUserIdentityRequired.headline)']))
		client.publishers()[0].subscriptions()[-1].set('revealIdentity', True)
		self.assertEqual(client.publishers()[0].subscriptions()[-1].installFont(font.uniqueID, font.getVersions()[-1].number), (True, None))


		# Protected subscription, installation on second machine
		# Supposed to reject because seats are limited to 1

		client2.linkUser(*testUser)
		success, message, publisher, subscription = client2.addSubscription(protectedSubscription)
		print(success, message)

		font2 = client2.publishers()[0].subscriptions()[-1].protocol.installableFontsCommand().foundries[0].families[0].fonts[0]

		# Two versions available
		self.assertEqual(len(client2.publishers()[0].subscriptions()[-1].installFont(font2.uniqueID, font2.getVersions())), 2)

		client2.publishers()[0].subscriptions()[-1].set('acceptedTermsOfService', True)
		client2.publishers()[0].subscriptions()[-1].set('revealIdentity', True)
		self.assertEqual(client2.publishers()[0].subscriptions()[-1].installFont(font2.uniqueID, font2.getVersions()[-1].number), (False, ['#(response.seatAllowanceReached)', '#(response.seatAllowanceReached.headline)']))

		# Uninstall font on first client
		client.publishers()[0].subscriptions()[-1].removeFont(font.uniqueID)

		# Uninstall font on second client
		client2.publishers()[0].subscriptions()[-1].removeFont(font2.uniqueID)

		# Try again on second client
		self.assertEqual(client2.publishers()[0].subscriptions()[-1].installFont(font2.uniqueID, font2.getVersions()[-1].number), (True, None))

		# Uninstall font on second client
		client2.publishers()[0].subscriptions()[-1].removeFont(font2.uniqueID)

		# Install older version on second client
		self.assertEqual(client2.publishers()[0].subscriptions()[-1].installFont(font2.uniqueID, font2.getVersions()[0].number), (True, None))

		# One font must be outdated
		self.assertEqual(client2.amountOutdatedFonts(), 1)

		# Uninstall font on second client
		client2.publishers()[0].subscriptions()[-1].removeFont(font2.uniqueID)



	def test_takedown(self):

		for publisher in client.publishers():
			for subscription in publisher.subscriptions():
				subscription.delete()

		for publisher in client2.publishers():
			for subscription in publisher.subscriptions():
				subscription.delete()

		client.unlinkUser()
		client2.unlinkUser()

if __name__ == '__main__':
	unittest.main()


 # Local
if not 'TRAVIS' in os.environ:
#	os.remove(prefFile)
	os.rmdir(tempFolder)
