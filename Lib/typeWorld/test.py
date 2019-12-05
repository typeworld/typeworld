# -*- coding: utf-8 -*-

import sys, os, copy

# if 'TRAVIS' in os.environ:
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ssl, certifi, urllib
sslcontext = ssl.create_default_context(cafile=certifi.where())


import unittest
from typeWorld.client import APIClient, JSON, AppKitNSUserDefaults
import tempfile, os, traceback
from typeWorld.api import *

freeSubscription = 'typeworld://json+https//typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/'
protectedSubscription = 'typeworld://json+https//s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/'
testUser1 = ('test1@type.world', 'abc')
testUser2 = ('test2@type.world', 'def')
testUser3 = ('test3@type.world', 'ghi')


MOTHERSHIP = 'http://127.0.0.1:8080/api'
if 'TRAVIS' in os.environ:
	MOTHERSHIP = 'https://typeworld.appspot.com/api'


### RootResponse
root = RootResponse()
root.name.en = 'Font Publisher'
root.canonicalURL = 'http://fontpublisher.com/api/'
root.adminEmail = 'admin@fontpublisher.com'
root.supportedCommands = [x['keyword'] for x in COMMANDS] # this API supports all commands
root.backgroundColor = 'AABBCC'
root.licenseIdentifier = 'CC-BY-NC-ND-4.0'
root.logo = 'https://typeworldserver.com/?page=outputDataBaseFile&className=TWFS_Foundry&ID=8&field=logo'
root.privacyPolicy = 'https://type.world/legal/privacy.html'
root.termsOfServiceAgreement = 'https://type.world/legal/terms.html'
root.public = False
root.version = '0.1.7-alpha'
root.website = 'https://typeworldserver.com'

### InstallableFontsResponse
designer = Designer()
designer.description.en = 'Yanone is a type designer based in Germany.'
designer.keyword = 'yanone'
designer.name.en = 'Yanone'
designer.website = 'https://yanone.de'

designer2 = Designer()
designer2.description.en = 'Yanone is a type designer based in Germany.'
designer2.keyword = 'yanone2'
designer2.name.en = 'Yanone'
designer2.website = 'https://yanone.de'

# License
license = LicenseDefinition()
license.URL = 'https://yanone.de/eula.html'
license.keyword = 'yanoneEULA'
license.name.en = 'Yanone EULA'

# Font-specific Version
fontVersion = Version()
fontVersion.description.en = 'Initial release'
fontVersion.description.de = 'Erstveröffentlichung'
fontVersion.number = 1.0
fontVersion.releaseDate = '2004-10-10'

# LicenseUsage
usedLicense = LicenseUsage()
usedLicense.allowanceDescription.en = 'N/A'
usedLicense.dateAddedForUser = '2019-10-01'
usedLicense.keyword = 'yanoneEULA'
usedLicense.seatsAllowed = 5
usedLicense.seatsInstalled = 1
usedLicense.upgradeURL = 'https://yanone.de/buy/kaffeesatz/upgrade?customerID=123456'

# Font
font = Font()
font.dateFirstPublished = '2004-10-10'
font.designers.append('yanone')
font.designers = ['yanone', 'yanone2']
assert len(font.designers) == 2
font.format = 'otf'
font.free = True
font.name.en = 'Regular'
font.name.de = 'Normale'
font.pdf = 'https://yanone.de/fonts/kaffeesatz.pdf'
font.postScriptName = 'YanoneKaffeesatz-Regular'
font.protected = False
font.purpose = 'desktop'
font.setName.en = 'Desktop Fonts'
font.setName.de = 'Desktop-Schriften'
font.status = 'stable'
font.uniqueID = 'yanone-kaffeesatz-regular'
font.usedLicenses.append(usedLicense)
font.usedLicenses = [usedLicense]
assert len(font.usedLicenses) == 1
font.variableFont = False
font.versions.append(fontVersion)
font.versions = [fontVersion]
assert len(font.versions) == 1

# Font 2
font2 = Font()
font2.dateFirstPublished = '2004-10-10'
font2.designers.append('yanone')
font2.designers = ['yanone']
assert len(font2.designers) == 1
font2.format = 'otf'
font2.free = True
font2.name.en = 'Bold'
font2.name.de = 'Fette'
font2.pdf = 'https://yanone.de/fonts/kaffeesatz.pdf'
font2.postScriptName = 'YanoneKaffeesatz-Bold'
font2.protected = False
font2.purpose = 'desktop'
font2.setName.en = 'Desktop Fonts'
font2.setName.de = 'Desktop-Schriften'
font2.status = 'stable'
font2.uniqueID = 'yanone-kaffeesatz-bold'
font2.usedLicenses.append(usedLicense)
font2.usedLicenses = [usedLicense]
assert len(font2.usedLicenses) == 1
font2.variableFont = False
font2.versions.append(fontVersion)
font2.versions = [fontVersion]
assert len(font2.versions) == 1

# Family-specific Version
familyVersion = Version()
familyVersion.description.en = 'Initial release'
familyVersion.description.de = 'Erstveröffentlichung'
familyVersion.number = 1.0
familyVersion.releaseDate = '2004-10-10'

# Family
family = Family()
family.billboards = ['https://typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image']
family.billboards.append('https://typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=6&field=image')
family.dateFirstPublished = '2019-10-01'
family.description.en = 'Kaffeesatz is a free font classic'
family.designers.append('yanone')
family.designers = ['yanone'] # same as above
assert len(family.designers) == 1
family.inUseURL = 'https://fontsinuse.com/kaffeesatz'
family.issueTrackerURL = 'https://github.com/yanone/kaffeesatzfont/issues'
family.name.en = 'Yanone Kaffeesatz'
family.pdf = 'https://yanone.de/fonts/kaffeesatz.pdf'
family.sourceURL = 'https://github.com/yanone/kaffeesatzfont'
family.uniqueID = 'yanone-yanonekaffeesatz'
family.versions.append(familyVersion)
family.versions = [familyVersion]
assert len(family.versions) == 1
family.fonts.append(font)
family.fonts = [font]
assert len(family.fonts) == 1
family.fonts.append(font2)
assert len(family.fonts) == 2
family.fonts = [font, font2]
assert len(family.fonts) == 2

# Foundry
foundry = Foundry()
foundry.backgroundColor = 'AABBCC'
foundry.description.en = 'Yanone is a foundry lead by German type designer Yanone.'
foundry.email = 'font@yanone.de'
foundry.facebook = 'https://facebook.com/pages/YanoneYanone'
foundry.instagram = 'instagram'
foundry.licenses.append(license)
foundry.logo = 'https://typeworldserver.com/?page=outputDataBaseFile&className=TWFS_Foundry&ID=8&field=logo'
foundry.name.en = 'Awesome Fonts'
foundry.name.de = 'Tolle Schriften'
foundry.skype = 'yanone'
foundry.supportEmail = 'support@yanone.de'
foundry.supportTelephone = '+49123456789'
foundry.supportWebsite = 'https://yanone.de/support/'
foundry.telephone = '+49123456789'
foundry.twitter = 'yanone'
foundry.uniqueID = 'yanone'
foundry.website = 'https://yanone.de'
foundry.families.append(family)
foundry.families = [family]
assert len(foundry.families) == 1

# InstallableFontsResponse
installableFonts = InstallableFontsResponse()
installableFonts.designers.append(designer)
installableFonts.designers.append(designer2)
installableFonts.designers.remove(designer2)
installableFonts.designers.extend([designer2])
installableFonts.name.en = 'Commercial Fonts'
installableFonts.name.de = 'Kommerzielle Schriften'
installableFonts.prefersRevealedUserIdentity = True
installableFonts.type = 'success'
installableFonts.userEmail = 'post@yanone.de'
installableFonts.userName.en = 'Yanone'
installableFonts.version = '0.1.7-alpha'
installableFonts.foundries.append(foundry)
print(installableFonts.designers)




class User(object):
	def __init__(self, login = None):
		self.login = login
		self.prefFile = os.path.join(tempFolder, str(id(self)) + '.json')
		self.loadClient()
		self.credentials = ()

		if self.login:
			print('Login for %s: %s/%s' % (self.login[0], self.login[0], self.login[1]))
			print('Deleting user account for %s' % self.login[0])
			success, message = self.client.deleteUserAccount(*self.login)
			if not success and message != '#(response.userUnknown)': raise ValueError(message)
			print('Creating user account for %s' % self.login[0])
			success, message = self.client.createUserAccount('Test User', self.login[0], self.login[1], self.login[1])
			if not success: raise ValueError(message)
			self.credentials = (self.client.user(), self.client.secretKey())
			print('Credentials for %s: %s/%s' % (self.login[0], self.credentials[0], self.credentials[1]))

			self.clearInvitations()
			self.clearSubscriptions()

	# def linkUser(self):
	# 	self.unlinkUser()
	# 	if self.login:
	# 		return self.client.linkUser(*self.credentials)

	def testFont(self):
		return self.client.publishers()[0].subscriptions()[-1].protocol.installableFontsCommand()[1].foundries[0].families[0].fonts[0]

	def clearSubscriptions(self):
		for publisher in self.client.publishers():
			publisher.delete()

	def clearInvitations(self):
		for invitation in self.client.pendingInvitations():
			invitation.decline()

	def takeDown(self):
		self.clearInvitations()
		self.clearSubscriptions()
		self.unlinkUser()
		if self.login:
			self.client.deleteUserAccount(*self.login)

	def unlinkUser(self):
		if self.login:
			if self.client.user():
				self.client.unlinkUser()

	def loadClient(self):
		self.client = APIClient(preferences = AppKitNSUserDefaults('world.type.test%s' % id(self)) if MAC else JSON(self.prefFile), mothership = MOTHERSHIP)


class TestStringMethods(unittest.TestCase):


	def test_normalSubscription(self):

		print('test_normalSubscription()')

		self.assertTrue(user0.client.online(MOTHERSHIP.split('//')[1].split('/')[0].split(':')[0]))

		self.assertTrue(user2.client.user())

		parameters = {
			'command': 'verifyCredentials',
			'anonymousAppID': user2.client.anonymousAppID(),
			'anonymousTypeWorldUserID': user2.client.user(),
			'APIKey': 'OgS5nJ8HmJVNirdvAR9QFfLJVpqlnZsV01MipxVU',
		}

		data = urllib.parse.urlencode(parameters).encode('ascii')
		url = MOTHERSHIP

		response = urllib.request.urlopen(url, data, context=sslcontext)
		response = json.loads(response.read().decode())
		self.assertEqual(response['response'], 'success')


		# General stuff
		self.assertEqual(type(user0.client.locale()), list)
		self.assertTrue(typeWorld.client.urlIsValid(freeSubscription)[0])

		## Scenario 1:
		## Test a simple subscription of free fonts without Type.World user account

		result = user0.client.addSubscription(freeSubscription)
		print('Scenario 1:', result)
		success, message, publisher, subscription = result
		self.assertEqual(success, True)
		self.assertEqual(user0.client.publishers()[0].canonicalURL, 'https://typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/')
		self.assertEqual(len(user0.client.publishers()[0].subscriptions()), 1)
		self.assertEqual(len(user0.client.publishers()[0].subscriptions()[-1].protocol.installableFontsCommand()[1].foundries), 1)
		self.assertEqual(user0.client.publishers()[0].subscriptions()[-1].protocol.installableFontsCommand()[1].foundries[0].name.getTextAndLocale(), ('Test Foundry', 'en'))

		# Logo
		user0.client.testScenario = 'simulateProgrammingError'
		success, logo, mimeType = subscription.resourceByURL(user0.client.publishers()[0].subscriptions()[0].protocol.installableFontsCommand()[1].foundries[0].logo)
		self.assertEqual(success, False)

		user0.client.testScenario = None
		success, logo, mimeType = subscription.resourceByURL(user0.client.publishers()[0].subscriptions()[0].protocol.installableFontsCommand()[1].foundries[0].logo)
		self.assertEqual(success, True)
		self.assertTrue(logo.startswith('<?xml version="1.0" encoding="utf-8"?>'))

		# Name
		self.assertEqual(user0.client.publishers()[0].name()[0], 'Test Publisher')
		self.assertEqual(user0.client.publishers()[0].subscriptions()[0].name(), 'Free Fonts')

		# Reload client
		# Equal to closing the app and re-opening, so code gets loaded from disk/defaults
		user0.loadClient()

		user0.clearSubscriptions()




		### ###



		# Scenario 2:
		# Protected subscription, installation on machine without user account
		# This is supposed to fail because accessing protected subscriptions requires a valid Type.World user account, but user0 is not linked with a user account
		result = user0.client.addSubscription(protectedSubscription)
		print('Scenario 2:', result)
		success, message, publisher, subscription = result
		self.assertEqual(success, False)
		self.assertEqual(message, '#(response.validTypeWorldUserAccountRequired)')



		### ###



		# Scenario 3:
		# Protected subscription, installation on first machine with Type.World user account
		result = user1.client.addSubscription(protectedSubscription)
		print('Scenario 3:', result)
		success, message, publisher, subscription = result
		print('Message:', message)

		self.assertEqual(success, True)
		self.assertEqual(len(user1.client.publishers()[0].subscriptions()), 1)
		self.assertEqual(len(user1.client.publishers()[0].subscriptions()[-1].protocol.installableFontsCommand()[1].foundries), 1)


		# saveURL
		self.assertEqual(user1.client.publishers()[0].subscriptions()[-1].protocol.saveURL(), 'typeworld://json+https//s9lWvayTEOaB9eIIMA67:secretKey@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/')
		# completeURL
		self.assertEqual(user1.client.publishers()[0].subscriptions()[-1].protocol.completeURL(), 'typeworld://json+https//s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/')

		# Reload client
		# Equal to closing the app and re-opening, so code gets loaded from disk/defaults
		user1.loadClient()
		self.assertEqual(user1.client.publishers()[0].subscriptions()[-1].protocol.completeURL(), 'typeworld://json+https//s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/')


		user1.client.testScenario = 'simulateCentralServerNotReachable'
		self.assertEqual(
			user1.client.downloadSubscriptions()[0],
			False
			)
		user1.client.testScenario = 'simulateCentralServerProgrammingError'
		self.assertEqual(
			user1.client.downloadSubscriptions()[0],
			False
			)
		user1.client.testScenario = 'simulateCentralServerErrorInResponse'
		self.assertEqual(
			user1.client.downloadSubscriptions()[0],
			False
			)
		user1.client.testScenario = 'simulateNotOnline'
		self.assertEqual(
			user1.client.downloadSubscriptions()[0],
			False
			)
		user1.client.testScenario = None
		self.assertEqual(
			user1.client.downloadSubscriptions()[0],
			True
			)
		success, message, changes = user1.client.publishers()[0].update()
		print('Updating publisher:', success, message, changes)
		self.assertEqual(success, True)
		self.assertEqual(changes, False)
		success, message, changes = user1.client.publishers()[0].subscriptions()[0].update()
		print('Updating subscription 1:', success, message, changes)
		self.assertEqual(success, True)
		self.assertEqual(changes, False)
		self.assertEqual(user1.client.publishers()[0].stillUpdating(), False)
		self.assertEqual(user1.client.publishers()[0].subscriptions()[0].stillUpdating(), False)
		print(user1.client.publishers()[0].updatingProblem())
		self.assertEqual(user1.client.allSubscriptionsUpdated(), True)

		# Install Font
		# First it's meant to fail because the user hasn't accepted the Terms & Conditions
		self.assertEqual(user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number), (False, ['#(response.termsOfServiceNotAccepted)', '#(response.termsOfServiceNotAccepted.headline)']))
		user1.client.publishers()[0].subscriptions()[-1].set('acceptedTermsOfService', True)
		# Then it's supposed to fail because the server requires the revealted user identity for this subscription
		self.assertEqual(user1.client.publishers()[0].subscriptions()[-1].protocol.installableFontsCommand()[1].prefersRevealedUserIdentity, True)
		self.assertEqual(user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number), (False, ['#(response.revealedUserIdentityRequired)', '#(response.revealedUserIdentityRequired.headline)']))
		user1.client.publishers()[0].subscriptions()[-1].set('revealIdentity', True)

		# Finally supposed to pass
		self.assertEqual(user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number), (True, None))
		self.assertEqual(user1.client.publishers()[0].amountInstalledFonts(), 1)
		self.assertEqual(user1.client.publishers()[0].subscriptions()[0].amountInstalledFonts(), 1)

		# Simulations
		user1.client.testScenario = 'simulateNotOnline'
		success, message, changes = user1.client.publishers()[0].update()
		self.assertEqual(success, False)
		success, message, changes = user1.client.publishers()[0].subscriptions()[0].update()
		self.assertEqual(success, False)
		user1.client.testScenario = 'simulateProgrammingError'
		success, message, changes = user1.client.publishers()[0].update()
		self.assertEqual(success, False)
		success, message, changes = user1.client.publishers()[0].subscriptions()[0].update()
		self.assertEqual(success, False)
		user1.client.testScenario = 'simulateInsufficientPermissions'
		success, message, changes = user1.client.publishers()[0].update()
		self.assertEqual(success, False)
		success, message, changes = user1.client.publishers()[0].subscriptions()[0].update()
		self.assertEqual(success, False)
		user1.client.testScenario = 'simulateCustomError'
		success, message, changes = user1.client.publishers()[0].update()
		self.assertEqual(success, False)
		self.assertEqual(message.getText(), 'simulateCustomError')
		success, message, changes = user1.client.publishers()[0].subscriptions()[0].update()
		self.assertEqual(success, False)
		self.assertEqual(message.getText(), 'simulateCustomError')

		# Simulate unexpected empty subscription
		user1.client.testScenario = 'simulateNoFontsAvailable'
		success, message, changes = user1.client.publishers()[0].subscriptions()[0].update()
		print('Updating subscription 2:', success, message, changes)
		self.assertEqual(success, True)
		self.assertEqual(changes, True)
		self.assertEqual(user1.client.publishers()[0].subscriptions()[0].amountInstalledFonts(), 0)
		user1.client.testScenario = None
		success, message, changes = user1.client.publishers()[0].subscriptions()[0].update()

		# Repeat font installation
		user1.client.testScenario = 'simulateProgrammingError'
		success, message = user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number)
		self.assertEqual(success, False)

		user1.client.testScenario = 'simulatePermissionError'
		success, message = user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number)
		self.assertEqual(success, False)

		user1.client.testScenario = 'simulateCustomError'
		success, message = user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number)
		self.assertEqual(success, False)
		self.assertEqual(message.getText(), 'simulateCustomError')

		user1.client.testScenario = 'simulateInsufficientPermissions'
		success, message = user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number)
		self.assertEqual(success, False)


		# Supposed to pass
		user1.client.testScenario = None
		self.assertEqual(
			user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number),
			(True, None)
		)
		self.assertEqual(user1.client.publishers()[0].amountInstalledFonts(), 1)
		self.assertEqual(user1.client.publishers()[0].subscriptions()[0].amountInstalledFonts(), 1)


		# Revoke app instance
		if not 'TRAVIS' in os.environ: authKey = user1.client.keyring().get_password(MOTHERSHIP, 'revokeAppInstance')
		else: authKey = os.environ['REVOKEAPPINSTANCEAUTHKEY']
		parameters = {
			'command': 'revokeAppInstance',
			'anonymousAppID': user1.client.preferences.get('anonymousAppID'),
			'authorizationKey': authKey,
			'anonymousUserID': user1.client.user(),
			'secretKey': user1.client.secretKey(),
		}
		data = urllib.parse.urlencode(parameters).encode('ascii')
		url = MOTHERSHIP
		response = urllib.request.urlopen(url, data, context=sslcontext)
		response = json.loads(response.read().decode())
		self.assertEqual(response['response'], 'success')

		self.assertEqual(user1.client.downloadSubscriptions(), (True, None))
		self.assertEqual(user1.client.publishers()[0].amountInstalledFonts(), 0)

		# Reinstall font, fails
		user1.client.testScenario = None
		self.assertEqual(
			user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number)[0],
			False
		)

		# Reactivate app instance
		parameters = {
			'command': 'reactivateAppInstance',
			'anonymousAppID': user1.client.preferences.get('anonymousAppID'),
			'authorizationKey': authKey,
			'anonymousUserID': user1.client.user(),
			'secretKey': user1.client.secretKey(),
		}
		data = urllib.parse.urlencode(parameters).encode('ascii')
		url = MOTHERSHIP
		response = urllib.request.urlopen(url, data, context=sslcontext)
		response = json.loads(response.read().decode())
		self.assertEqual(response['response'], 'success')

		self.assertEqual(user1.client.downloadSubscriptions(), (True, None))

		# Reinstall font
		user1.client.testScenario = None
		self.assertEqual(
			user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number),
			(True, None)
		)
		self.assertEqual(user1.client.publishers()[0].amountInstalledFonts(), 1)
		self.assertEqual(user1.client.publishers()[0].subscriptions()[0].amountInstalledFonts(), 1)



		# This is also supposed to delete the installed protected font
		user1.client.testScenario = 'simulateCentralServerNotReachable'
		self.assertEqual(
			user1.client.unlinkUser()[0],
			False
			)
		user1.client.testScenario = 'simulateCentralServerProgrammingError'
		self.assertEqual(
			user1.client.unlinkUser()[0],
			False
			)
		user1.client.testScenario = 'simulateCentralServerErrorInResponse'
		self.assertEqual(
			user1.client.unlinkUser()[0],
			False
			)
		user1.client.testScenario = 'simulateNotOnline'
		self.assertEqual(
			user1.client.unlinkUser()[0],
			False
			)
		self.assertTrue(user1.client.syncProblems())
		user1.client.testScenario = None
		success, message = user1.client.unlinkUser()
		self.assertEqual(
			success,
			True
			)
		self.assertFalse(user1.client.syncProblems())
		self.assertEqual(user1.client.userEmail(), None)
		self.assertEqual(user1.client.user(), '')

		self.assertEqual(user1.client.publishers()[0].amountInstalledFonts(), 0)
		self.assertEqual(len(user1.client.publishers()[0].subscriptions()), 1)

		# Delete subscription from user-less app, so that it can be re-added during upcoming user linking
		user1.client.publishers()[0].subscriptions()[0].delete()
		self.assertEqual(len(user1.client.publishers()), 0)

		user1.client.testScenario = 'simulateCentralServerNotReachable'
		self.assertEqual(
			user1.client.linkUser(*user1.credentials)[0],
			False
			)
		user1.client.testScenario = 'simulateCentralServerProgrammingError'
		self.assertEqual(
			user1.client.linkUser(*user1.credentials)[0],
			False
			)
		user1.client.testScenario = 'simulateCentralServerErrorInResponse'
		self.assertEqual(
			user1.client.linkUser(*user1.credentials)[0],
			False
			)
		user1.client.testScenario = 'simulateNotOnline'
		self.assertEqual(
			user1.client.linkUser(*user1.credentials)[0],
			False
			)
		user1.client.testScenario = None
		success, message = user1.client.linkUser(*user1.credentials)
		print('linkUser:', success, message)
		self.assertEqual(
			success,
			True
			)

		# Unlink
		self.assertEqual(
			user1.client.unlinkUser()[0],
			True
			)
		# Log in
		self.assertEqual(
			user1.client.logInUserAccount(*testUser1)[0],
			True
			)

		self.assertEqual(len(user1.client.publishers()[0].subscriptions()), 1)
		self.assertEqual(user1.client.userEmail(), 'test1@type.world')

		# Install again
		user1.client.publishers()[0].subscriptions()[-1].set('acceptedTermsOfService', True)
		user1.client.publishers()[0].subscriptions()[-1].set('revealIdentity', True)
		self.assertEqual(user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number), (True, None))
		self.assertEqual(user1.client.publishers()[0].amountInstalledFonts(), 1)

		# Sync subscription
		user1.client.testScenario = 'simulateCentralServerNotReachable'
		self.assertEqual(
			user1.client.syncSubscriptions()[0],
			False
			)
		user1.client.testScenario = 'simulateCentralServerProgrammingError'
		self.assertEqual(
			user1.client.syncSubscriptions()[0],
			False
			)
		user1.client.testScenario = 'simulateCentralServerErrorInResponse'
		self.assertEqual(
			user1.client.syncSubscriptions()[0],
			False
			)
		user1.client.testScenario = 'simulateNotOnline'
		self.assertEqual(
			user1.client.syncSubscriptions()[0],
			False
			)
		user1.client.testScenario = None
		self.assertEqual(
			user1.client.syncSubscriptions()[0],
			True
			)


		### ###



		# Scenario 4:
		# Protected subscription, installation on second machine


		user2.client.testScenario = 'simulateWrongMimeType'
		success, message, publisher, subscription = user2.client.addSubscription(protectedSubscription)
		self.assertEqual(success, False)
		self.assertEqual(message, 'Response from protocol.aboutToAddSubscription(): Resource headers returned wrong MIME type: "text/html". Expected is "[\'application/json\']".')
		user2.client.testScenario = 'simulateNotHTTP200'
		success, message, publisher, subscription = user2.client.addSubscription(protectedSubscription)
		self.assertEqual(success, False)
		user2.client.testScenario = 'simulateProgrammingError'
		success, message, publisher, subscription = user2.client.addSubscription(protectedSubscription)
		self.assertEqual(success, False)
		user2.client.testScenario = 'simulateInvalidAPIJSONResponse'
		success, message, publisher, subscription = user2.client.addSubscription(protectedSubscription)
		self.assertEqual(success, False)
		user2.client.testScenario = 'simulateFaultyAPIJSONResponse'
		success, message, publisher, subscription = user2.client.addSubscription(protectedSubscription)
		self.assertEqual(success, False)
		user2.client.testScenario = 'simulateCentralServerNotReachable'
		success, message, publisher, subscription = user2.client.addSubscription(protectedSubscription)
		self.assertEqual(success, False)
		user2.client.testScenario = 'simulateCentralServerProgrammingError'
		success, message, publisher, subscription = user2.client.addSubscription(protectedSubscription)
		self.assertEqual(success, False)
		user2.client.testScenario = 'simulateCentralServerErrorInResponse'
		success, message, publisher, subscription = user2.client.addSubscription(protectedSubscription)
		self.assertEqual(success, False)
		user2.client.testScenario = 'simulateNotOnline'
		success, message, publisher, subscription = user2.client.addSubscription(protectedSubscription)
		self.assertEqual(success, False)
		user2.client.testScenario = None
		success, message, publisher, subscription = user2.client.addSubscription(protectedSubscription)
		self.assertEqual(success, True)
		print(success, message)

		# Two versions available
		self.assertEqual(len(user2.client.publishers()[0].subscriptions()[-1].installFont(user2.testFont().uniqueID, user2.testFont().getVersions())), 2)

		# Supposed to reject because seats are limited to 1
		user2.client.publishers()[0].subscriptions()[-1].set('acceptedTermsOfService', True)
		user2.client.publishers()[0].subscriptions()[-1].set('revealIdentity', True)
		self.assertEqual(
			user2.client.publishers()[0].subscriptions()[-1].installFont(user2.testFont().uniqueID, user2.testFont().getVersions()[-1].number), 
			(False, ['#(response.seatAllowanceReached)', '#(response.seatAllowanceReached.headline)'])
			)

		# Uninstall font for user1
		user1.client.testScenario = 'simulatePermissionError'
		success, message = user1.client.publishers()[0].subscriptions()[-1].removeFont(user1.testFont().uniqueID)
		self.assertEqual(success, False)

		# user1.client.testScenario = 'simulateMissingFont'
		# success, message = user1.client.publishers()[0].subscriptions()[-1].removeFont(user1.testFont().uniqueID)
		# self.assertEqual(success, False)

		user1.client.testScenario = 'simulateCustomError'
		success, message = user1.client.publishers()[0].subscriptions()[-1].removeFont(user1.testFont().uniqueID)
		self.assertEqual(success, False)
		self.assertEqual(message.getText(), 'simulateCustomError')

		user1.client.testScenario = 'simulateProgrammingError'
		success, message = user1.client.publishers()[0].subscriptions()[-1].removeFont(user1.testFont().uniqueID)
		self.assertEqual(success, False)

		user1.client.testScenario = 'simulateUnknownFontError'
		success, message = user1.client.publishers()[0].subscriptions()[-1].removeFont(user1.testFont().uniqueID)
		self.assertEqual(success, False)

		user1.client.testScenario = 'simulateInsufficientPermissions'
		success, message = user1.client.publishers()[0].subscriptions()[-1].removeFont(user1.testFont().uniqueID)
		self.assertEqual(success, False)

		user1.client.testScenario = None
		success, message = user1.client.publishers()[0].subscriptions()[-1].removeFont(user1.testFont().uniqueID)
		self.assertEqual(success, True)

		# Uninstall font for user2, must fail because deleting same font file (doesn't make sense in normal setup)
		result = user2.client.publishers()[0].subscriptions()[-1].removeFont(user2.testFont().uniqueID)
		print(result)
		self.assertEqual(result, (False, 'Font path couldn’t be determined'))

		# Try again for user2
		self.assertEqual(user2.client.publishers()[0].subscriptions()[-1].installFont(user2.testFont().uniqueID, user2.testFont().getVersions()[-1].number), (True, None))

		# Uninstall font on for user2
		result = user2.client.publishers()[0].subscriptions()[-1].removeFont(user2.testFont().uniqueID)
		print(result)
		self.assertEqual(result, (True, None))

		# Install older version on second client
		self.assertEqual(user2.client.publishers()[0].subscriptions()[-1].installFont(user2.testFont().uniqueID, user2.testFont().getVersions()[0].number), (True, None))

		# Check amount
		self.assertEqual(user2.client.publishers()[0].amountInstalledFonts(), 1)

		# One font must be outdated
		self.assertEqual(user2.client.amountOutdatedFonts(), 1)
		self.assertEqual(user2.client.publishers()[0].amountOutdatedFonts(), 1)
		self.assertEqual(user2.client.publishers()[0].subscriptions()[0].amountOutdatedFonts(), 1)

		# Uninstall font for user2
		result = user2.client.publishers()[0].subscriptions()[-1].removeFont(user2.testFont().uniqueID)
		print(result)
		self.assertEqual(result, (True, None))

		# Family By ID
		family = user2.client.publishers()[0].subscriptions()[-1].protocol.installableFontsCommand()[1].foundries[0].families[0]
		self.assertEqual(family, user2.client.publishers()[0].subscriptions()[-1].familyByID(family.uniqueID))

		# Font By ID
		font = family.fonts[0]
		self.assertEqual(font, user2.client.publishers()[0].subscriptions()[-1].fontByID(font.uniqueID))

		# Clear
		user2.clearSubscriptions()
		self.assertEqual(len(user2.client.publishers()), 0)




		### ###

		print('STATUS: -14')


		# Invitations
		# Invite to client without linked user account
		success, message, publisher, subscription = user0.client.addSubscription(freeSubscription)
		self.assertEqual(success, True)
		result = user0.client.publishers()[0].subscriptions()[-1].inviteUser('test12345@type.world')
		self.assertEqual(result, (False, 'No source user linked.'))

		# Invite unknown user
		result = user1.client.publishers()[0].subscriptions()[-1].inviteUser('test12345@type.world')
		self.assertEqual(result, (False, ['#(response.unknownTargetEmail)', '#(response.unknownTargetEmail.headline)']))

		# Invite same user
		self.assertEqual(user1.client.userEmail(), 'test1@type.world')
		# self.assertEqual(user1.client.user(), '736b524a-cf24-11e9-9f62-901b0ecbcc7a')
		result = user1.client.publishers()[0].subscriptions()[-1].inviteUser('test1@type.world')
		self.assertEqual(result, (False, ['#(response.sourceAndTargetIdentical)', '#(response.sourceAndTargetIdentical.headline)']))

		print('STATUS: -13')

		# Invite real user
		user1.client.testScenario = 'simulateCentralServerNotReachable'
		result = user1.client.publishers()[0].subscriptions()[-1].inviteUser('test2@type.world')
		self.assertEqual(result[0], False)
		user1.client.testScenario = 'simulateCentralServerProgrammingError'
		result = user1.client.publishers()[0].subscriptions()[-1].inviteUser('test2@type.world')
		self.assertEqual(result[0], False)
		user1.client.testScenario = 'simulateCentralServerErrorInResponse'
		result = user1.client.publishers()[0].subscriptions()[-1].inviteUser('test2@type.world')
		self.assertEqual(result[0], False)
		user1.client.testScenario = 'simulateNotOnline'
		result = user1.client.publishers()[0].subscriptions()[-1].inviteUser('test2@type.world')
		self.assertEqual(result[0], False)
		user1.client.testScenario = None
		result = user1.client.publishers()[0].subscriptions()[-1].inviteUser('test2@type.world')
		print(result)
		self.assertEqual(result[0], True)

		print('STATUS: -12')

		# Update user2
		self.assertEqual(len(user2.client.pendingInvitations()), 0)

		print('STATUS: -11.8')

		self.assertEqual(len(user2.client.publishers()), 0)

		print('STATUS: -11.7')

		self.assertEqual(user2.client.downloadSubscriptions(), (True, None))

		print('STATUS: -11.6')

		self.assertEqual(len(user2.client.pendingInvitations()), 1)

		print('STATUS: -11.5')

		# Decline (exists only here in test script)
		user2.clearInvitations()
		# Invite again
		result = user1.client.publishers()[0].subscriptions()[-1].inviteUser('test2@type.world')
		self.assertEqual(result, (True, None))

		print('STATUS: -11')

		# Accept invitation
		self.assertEqual(user2.client.downloadSubscriptions(), (True, None))

		user2.client.testScenario = 'simulateCentralServerNotReachable'
		success, message = user2.client.pendingInvitations()[0].accept()
		self.assertEqual(success, False)
		user2.client.testScenario = 'simulateCentralServerProgrammingError'
		success, message = user2.client.pendingInvitations()[0].accept()
		self.assertEqual(success, False)
		user2.client.testScenario = 'simulateCentralServerErrorInResponse'
		success, message = user2.client.pendingInvitations()[0].accept()
		self.assertEqual(success, False)
		user2.client.testScenario = 'simulateNotOnline'
		success, message = user2.client.pendingInvitations()[0].accept()
		self.assertEqual(success, False)
		user2.client.testScenario = None
		success, message = user2.client.pendingInvitations()[0].accept()
		print(message)
		self.assertEqual(success, True)

		print('STATUS: -10')

		user2.client.downloadSubscriptions()
		self.assertEqual(len(user2.client.pendingInvitations()), 0)
		self.assertEqual(len(user2.client.publishers()), 1)

		# Invite yet another user
		self.assertEqual(len(user3.client.pendingInvitations()), 0)
		self.assertEqual(len(user3.client.publishers()), 0)
		result = user2.client.publishers()[0].subscriptions()[-1].inviteUser('test3@type.world')
		self.assertEqual(result, (True, None))
		success, message = user2.client.downloadSubscriptions()
		self.assertEqual(success, True)
		self.assertEqual(len(user2.client.sentInvitations()), 1)

		print('STATUS: -9')

		# Decline invitation
		user3.client.downloadSubscriptions()
		self.assertEqual(len(user3.client.pendingInvitations()), 1)

		user3.client.testScenario = 'simulateCentralServerNotReachable'
		success, message = user3.client.pendingInvitations()[0].decline()
		self.assertEqual(success, False)
		user3.client.testScenario = 'simulateCentralServerProgrammingError'
		success, message = user3.client.pendingInvitations()[0].decline()
		self.assertEqual(success, False)
		user3.client.testScenario = 'simulateCentralServerErrorInResponse'
		success, message = user3.client.pendingInvitations()[0].decline()
		self.assertEqual(success, False)
		user3.client.testScenario = 'simulateNotOnline'
		success, message = user3.client.pendingInvitations()[0].decline()
		self.assertEqual(success, False)
		user3.client.testScenario = None
		success, message = user3.client.pendingInvitations()[0].decline()
		self.assertEqual(success, True)

		self.assertEqual(len(user3.client.pendingInvitations()), 0)
		user2.client.downloadSubscriptions()
		self.assertEqual(len(user2.client.sentInvitations()), 0)

		# Invite again
		self.assertEqual(len(user3.client.pendingInvitations()), 0)
		self.assertEqual(len(user3.client.publishers()), 0)
		result = user2.client.publishers()[0].subscriptions()[-1].inviteUser('test3@type.world')
		self.assertEqual(result, (True, None))
		user2.client.downloadSubscriptions()
		self.assertEqual(len(user2.client.sentInvitations()), 1)

		print('STATUS: -8')

		# Accept invitation
		user3.client.downloadSubscriptions()
		self.assertEqual(len(user3.client.pendingInvitations()), 1)
		user3.client.pendingInvitations()[0].accept()
		self.assertEqual(len(user3.client.publishers()), 1)

		print('STATUS: -7')

		# Revoke user
		user2.client.testScenario = 'simulateCentralServerNotReachable'
		success, message = user2.client.publishers()[0].subscriptions()[-1].revokeUser('test3@type.world')
		self.assertEqual(success, False)
		user2.client.testScenario = 'simulateCentralServerProgrammingError'
		success, message = user2.client.publishers()[0].subscriptions()[-1].revokeUser('test3@type.world')
		self.assertEqual(success, False)
		user2.client.testScenario = 'simulateCentralServerErrorInResponse'
		success, message = user2.client.publishers()[0].subscriptions()[-1].revokeUser('test3@type.world')
		self.assertEqual(success, False)
		user2.client.testScenario = 'simulateNotOnline'
		success, message = user2.client.publishers()[0].subscriptions()[-1].revokeUser('test3@type.world')
		self.assertEqual(success, False)
		user2.client.testScenario = None
		success, message = user2.client.publishers()[0].subscriptions()[-1].revokeUser('test3@type.world')
		self.assertEqual(success, True)

		print('STATUS: -6')

		self.assertEqual(result, (True, None))
		user3.client.downloadSubscriptions()
		self.assertEqual(len(user3.client.publishers()), 0)

		print('STATUS: -5')

		# Invite again
		self.assertEqual(len(user3.client.pendingInvitations()), 0)
		self.assertEqual(len(user3.client.publishers()), 0)
		result = user2.client.publishers()[0].subscriptions()[-1].inviteUser('test3@type.world')
		self.assertEqual(result, (True, None))
		user2.client.downloadSubscriptions()
		self.assertEqual(len(user2.client.sentInvitations()), 1)

		print('STATUS: -4')

		# Accept invitation
		user3.client.downloadSubscriptions()
		self.assertEqual(len(user3.client.pendingInvitations()), 1)
		self.assertEqual(len(user3.client.publishers()), 0)
		user3.client.pendingInvitations()[0].accept()
		self.assertEqual(len(user3.client.publishers()), 1)

		print('STATUS: -3')

		# Invitation accepted
		success = user3.client.publishers()[-1].subscriptions()[-1].invitationAccepted()
		self.assertEqual(success, True)


		print('STATUS: -2')

		# Get publisher's logo
		self.assertTrue(user0.client.publishers()[0].subscriptions()[0].protocol.rootCommand()[1].logo)
		success, logo, mimeType = user0.client.publishers()[0].resourceByURL(user0.client.publishers()[0].subscriptions()[0].protocol.rootCommand()[1].logo)
		self.assertEqual(success, True)
		self.assertTrue(logo.startswith('<?xml version="1.0" encoding="utf-8"?>'))

		print('STATUS: -1')

		# Delete subscription from first user. Subsequent invitation must then be taken down as well.
		user1.client.publishers()[0].delete()
		user2.client.downloadSubscriptions()
		user3.client.downloadSubscriptions()
		self.assertEqual(len(user2.client.pendingInvitations()), 0)
		self.assertEqual(len(user3.client.pendingInvitations()), 0)







		# Create user account

		success, message = user0.client.createUserAccount('Test', 'test0@type.world', '', '')
		self.assertEqual(message, '#(RequiredFieldEmpty)')

		success, message = user0.client.createUserAccount('Test', 'test0@type.world', 'abc', 'def')
		self.assertEqual(message, '#(PasswordsDontMatch)')

		user0.client.testScenario = 'simulateCentralServerNotReachable'
		success, message = user0.client.createUserAccount('Test', 'test0@type.world', 'abc', 'def')
		self.assertEqual(success, False)
		user0.client.testScenario = 'simulateCentralServerProgrammingError'
		success, message = user0.client.createUserAccount('Test', 'test0@type.world', 'abc', 'def')
		self.assertEqual(success, False)
		user0.client.testScenario = 'simulateCentralServerErrorInResponse'
		success, message = user0.client.createUserAccount('Test', 'test0@type.world', 'abc', 'def')
		self.assertEqual(success, False)
		user0.client.testScenario = 'simulateNotOnline'
		success, message = user0.client.createUserAccount('Test', 'test0@type.world', 'abc', 'def')
		self.assertEqual(success, False)

		user0.client.testScenario = 'simulateCentralServerNotReachable'
		success, message = user0.client.createUserAccount('Test', 'test0@type.world', 'abc', 'def')
		self.assertEqual(success, False)
		user0.client.testScenario = 'simulateCentralServerProgrammingError'
		success, message = user0.client.createUserAccount('Test', 'test0@type.world', 'abc', 'def')
		self.assertEqual(success, False)
		user0.client.testScenario = 'simulateCentralServerErrorInResponse'
		success, message = user0.client.createUserAccount('Test', 'test0@type.world', 'abc', 'def')
		self.assertEqual(success, False)
		user0.client.testScenario = 'simulateNotOnline'
		success, message = user0.client.createUserAccount('Test', 'test0@type.world', 'abc', 'def')
		self.assertEqual(success, False)

		# Delete User Account

		success, message = user0.client.deleteUserAccount('test0@type.world', '')
		self.assertEqual(message, '#(RequiredFieldEmpty)')

		user0.client.testScenario = 'simulateCentralServerNotReachable'
		success, message = user0.client.deleteUserAccount('test0@type.world', 'abc')
		self.assertEqual(success, False)
		user0.client.testScenario = 'simulateCentralServerProgrammingError'
		success, message = user0.client.deleteUserAccount('test0@type.world', 'abc')
		self.assertEqual(success, False)
		user0.client.testScenario = 'simulateCentralServerErrorInResponse'
		success, message = user0.client.deleteUserAccount('test0@type.world', 'abc')
		self.assertEqual(success, False)
		user0.client.testScenario = 'simulateNotOnline'
		success, message = user0.client.deleteUserAccount('test0@type.world', 'abc')
		self.assertEqual(success, False)

		# Log In User Account

		success, message = user0.client.logInUserAccount('test0@type.world', '')
		self.assertEqual(message, '#(RequiredFieldEmpty)')

		user0.client.testScenario = 'simulateCentralServerNotReachable'
		success, message = user0.client.logInUserAccount(*testUser1)
		self.assertEqual(success, False)
		user0.client.testScenario = 'simulateCentralServerProgrammingError'
		success, message = user0.client.logInUserAccount(*testUser1)
		self.assertEqual(success, False)
		user0.client.testScenario = 'simulateCentralServerErrorInResponse'
		success, message = user0.client.logInUserAccount(*testUser1)
		self.assertEqual(success, False)
		user0.client.testScenario = 'simulateNotOnline'
		success, message = user0.client.logInUserAccount(*testUser1)
		self.assertEqual(success, False)

		user0.client.testScenario = None
		success, message = user0.client.logInUserAccount(*testUser1)
		self.assertEqual(success, True)
		success, message = user0.client.unlinkUser()
		self.assertEqual(success, True)




	def test_RootResponse(self):

		print('test_RootResponse()')

		print(root)
		# Dump and reload
		json = root.dumpJSON()
		root2 = RootResponse()
		root2.loadJSON(json)
		self.assertTrue(root.sameContent(root2))

		# name
		r2 = copy.deepcopy(root)
		r2.name.en = ''
		self.assertEqual(r2.validate()[2], ['<RootResponse>.name is a required attribute, but empty'])

		# canonicalURL
		r2 = copy.deepcopy(root)
		try:
			r2.canonicalURL = 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

		# adminEmail
		r2 = copy.deepcopy(root)
		try:
			r2.adminEmail = 'post_at_yanone.de'
		except ValueError as e:
			self.assertEqual(str(e), 'Not a valid email format: post_at_yanone.de')

		# supportedCommands
		r2 = copy.deepcopy(root)
		try:
			r2.supportedCommands = ['unsupportedCommand']
		except ValueError as e:
			self.assertEqual(str(e), 'Unknown API command: "unsupportedCommand". Possible: [\'installableFonts\', \'installFont\', \'uninstallFont\', \'setAnonymousAppIDStatus\']')

		# backgroundColor
		r2 = copy.deepcopy(root)
		try:
			r2.backgroundColor = 'CDEFGH'
		except ValueError as e:
			self.assertEqual(str(e), 'Not a valid hex color of format RRGGBB (like FF0000 for red): CDEFGH')

		# licenseIdentifier
		r2 = copy.deepcopy(root)
		try:
			r2.licenseIdentifier = 'unsupportedLicense'
		except ValueError as e:
			self.assertEqual(str(e), 'Unknown license identifier: "unsupportedLicense". See https://spdx.org/licenses/')

		# logo
		r2 = copy.deepcopy(root)
		try:
			r2.logo = 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

		# privacyPolicy
		r2 = copy.deepcopy(root)
		try:
			r2.privacyPolicy = 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

		# termsOfServiceAgreement
		r2 = copy.deepcopy(root)
		try:
			r2.termsOfServiceAgreement = 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

		# public
		r2 = copy.deepcopy(root)
		try:
			r2.public = 'True'
		except ValueError as e:
			self.assertEqual(str(e), 'Wrong data type. Is <class \'str\'>, should be: <class \'bool\'>.')

		# version
		r2 = copy.deepcopy(root)
		try:
			r2.version = '0.1.7.2'
		except ValueError as e:
			self.assertEqual(str(e), '0.1.7.2 is not valid SemVer string')

		# website
		r2 = copy.deepcopy(root)
		try:
			r2.website = 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')


	def test_copy(self):

		print('test_copy()')

		i2 = copy.copy(installableFonts)
		self.assertTrue(installableFonts.sameContent(i2))

		i3 = copy.deepcopy(installableFonts)
		self.assertTrue(installableFonts.sameContent(i3))

	def test_InstallableFontsResponse(self):

		print('test_InstallableFontsResponse()')

		print(installableFonts)
		# Dump and reload
		json = installableFonts.dumpJSON()
		installableFonts2 = InstallableFontsResponse()
		installableFonts2.loadJSON(json)
		self.assertTrue(installableFonts.sameContent(installableFonts2))

		# designers
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.designers = 'yanone'
		except ValueError as e:
			self.assertEqual(str(e), 'Wrong data type. Is <class \'str\'>, should be: <class \'list\'>.')

		# name
		# allowed to be emtpy
		i2 = copy.deepcopy(installableFonts)
		i2.name.en = ''
		validate = i2.validate()
		self.assertEqual(validate[2], [])

		# prefersRevealedUserIdentity
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.prefersRevealedUserIdentity = 'True'
		except ValueError as e:
			self.assertEqual(str(e), 'Wrong data type. Is <class \'str\'>, should be: <class \'bool\'>.')

		# type
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.type = 'abc'
		except ValueError as e:
			self.assertEqual(str(e), 'Unknown response type: "abc". Possible: [\'success\', \'error\', \'noFontsAvailable\', \'insufficientPermission\', \'temporarilyUnavailable\', \'validTypeWorldUserAccountRequired\', \'accessTokenExpired\']')

		# userEmail
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.userEmail = 'post_at_yanone.de'
		except ValueError as e:
			self.assertEqual(str(e), 'Not a valid email format: post_at_yanone.de')

		# userName
		i2 = copy.deepcopy(installableFonts)
		i2.userName.en = ''
		validate = i2.validate()
		self.assertEqual(validate[2], [])

		# version
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.version = '1.1.2.3'
		except ValueError as e:
			self.assertEqual(str(e), '1.1.2.3 is not valid SemVer string')

		# foundries
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries = 'yanone'
		except ValueError as e:
			self.assertEqual(str(e), 'Wrong data type. Is <class \'str\'>, should be: <class \'list\'>.')

		i2 = copy.deepcopy(installableFonts)
		i2.name.en = ''
		i2.name.de = ''
		validate = i2.validate()
#		print(validate)
		self.assertEqual(validate[1], ['<InstallableFontsResponse> --> The response has no .name value. It is not required, but highly recommended, to describe the purpose of this subscription to the user (such as "Commercial Fonts", "Free Fonts", etc. This is especially useful if you offer several different subscriptions to the same user.'])


	def test_Designer(self):

		print('test_Designer()')

		# name
		i2 = copy.deepcopy(installableFonts)
		i2.designers[0].name.en = ''
		self.assertEqual(i2.validate()[2], ['<InstallableFontsResponse> --> <Designer "None">.name is a required attribute, but empty'])

		# description
		# is optional, so this will pass
		i2 = copy.deepcopy(installableFonts)
		i2.designers[0].description.en = ''
		self.assertEqual(i2.validate()[2], [])

		# keyword
		i2 = copy.deepcopy(installableFonts)
		i2.designers[0].keyword = ''
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Designer "Yanone">.keyword is a required attribute, but empty', '<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> --> <Font "YanoneKaffeesatz-Regular"> has designer "yanone", but <InstallableFontsResponse>.designers has no matching designer.', '<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> --> <Font "YanoneKaffeesatz-Bold"> has designer "yanone", but <InstallableFontsResponse>.designers has no matching designer.', '<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> has designer "yanone", but <InstallableFontsResponse>.designers has no matching designer.'])

		# name
		i2 = copy.deepcopy(installableFonts)
		i2.designers[0].name.en = ''
		self.assertEqual(i2.validate()[2], ['<InstallableFontsResponse> --> <Designer "None">.name is a required attribute, but empty'])

		# website
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.designers[0].website = 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

	def test_LicenseDefinition(self):

		print('test_LicenseDefinition()')

		# name
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].licenses[0].name.en = ''
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <LicenseDefinition "None">.name is a required attribute, but empty'])

		# URL
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].licenses[0].URL= 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

		# keyword
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].licenses[0].keyword = ''
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <LicenseDefinition "Yanone EULA">.keyword is a required attribute, but empty', '<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> --> <Font "YanoneKaffeesatz-Regular"> --> <LicenseUsage "yanoneEULA"> has license "yanoneEULA", but <Foundry "Awesome Fonts"> has no matching license.', '<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> --> <Font "YanoneKaffeesatz-Bold"> --> <LicenseUsage "yanoneEULA"> has license "yanoneEULA", but <Foundry "Awesome Fonts"> has no matching license.'])


		i2 = copy.deepcopy(installableFonts)
		print(i2.foundries[0].licenses[0])
		assert i2.foundries[0].licenses[0].parent == i2.foundries[0]

	def test_Version(self):

		print('test_Version()')

		# description
		# is optional, so this will pass
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].families[0].versions[0].description.en = ''
		i2.foundries[0].families[0].versions[0].description.de = ''
		self.assertEqual(i2.validate()[2], [])

		# number
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].versions[0].number = '1.1.2.3'
		except ValueError as e:
			self.assertEqual(str(e), '1.1.2.3 is not valid SemVer string')

		# releaseDate
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].versions[0].releaseDate = '2010-20-21'
		except ValueError as e:
			self.assertEqual(str(e), 'ValueError: time data \'2010-20-21\' does not match format \'%Y-%m-%d\'')

		i2 = copy.deepcopy(installableFonts)
		print(i2.foundries[0].families[0].versions[0])
		assert i2.foundries[0].families[0].versions[0].isFontSpecific() == False
		assert i2.foundries[0].families[0].versions[0].parent == i2.foundries[0].families[0]
		assert i2.foundries[0].families[0].fonts[0].versions[0].isFontSpecific() == True
		assert i2.foundries[0].families[0].fonts[0].versions[0].parent == i2.foundries[0].families[0].fonts[0]

		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].fonts[0].filename(i2.foundries[0].families[0].fonts[0].getVersions()[-1])
		except ValueError as e:
			self.assertEqual(str(e), 'Supplied version must be str or int or float')



	def test_LicenseUsage(self):

		print('test_LicenseUsage()')

		# allowanceDescription
		# is optional, so this will pass
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].families[0].fonts[0].usedLicenses[0].allowanceDescription.en = None
		self.assertEqual(i2.validate()[2], [])

		# dateAddedForUser
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].fonts[0].usedLicenses[0].dateAddedForUser = '2010-20-21'
		except ValueError as e:
			self.assertEqual(str(e), 'ValueError: time data \'2010-20-21\' does not match format \'%Y-%m-%d\'')

		# keyword
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].families[0].fonts[0].usedLicenses[0].keyword = ''
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> --> <Font "YanoneKaffeesatz-Regular"> --> <LicenseUsage "">.keyword is a required attribute, but empty'])

		# seatsAllowed
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].fonts[0].usedLicenses[0].seatsAllowed = '5,0'
		except ValueError as e:
			self.assertEqual(str(e), 'invalid literal for int() with base 10: \'5,0\'')
		# try the same, but modify the json string, the re-import
		json = installableFonts.dumpJSON()
		json = json.replace('"seatsAllowed": 5', '"seatsAllowed": "5,0"')
		try:
			i2.loadJSON(json)
		except ValueError as e:
			self.assertEqual(str(e), 'invalid literal for int() with base 10: \'5,0\'')

		# seatsInstalled
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].fonts[0].usedLicenses[0].seatsInstalled = '1,0'
		except ValueError as e:
			self.assertEqual(str(e), 'invalid literal for int() with base 10: \'1,0\'')

		# URL
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].fonts[0].usedLicenses[0].upgradeURL= 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')


		i2 = copy.deepcopy(installableFonts)
		print(i2.foundries[0].families[0].fonts[0].usedLicenses[0])

	def test_Font(self):

		print('test_Font()')

		# dateAddedForUser
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].fonts[0].dateFirstPublished = '2010-20-21'
		except ValueError as e:
			self.assertEqual(str(e), 'ValueError: time data \'2010-20-21\' does not match format \'%Y-%m-%d\'')

		# designers
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].families[0].fonts[0].designers = ['gfknlergerg']
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> --> <Font "YanoneKaffeesatz-Regular"> has designer "gfknlergerg", but <InstallableFontsResponse>.designers has no matching designer.'])

		# format
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].fonts[0].format = 'abc'
		except ValueError as e:
			self.assertTrue('Unknown font extension: "abc".' in str(e))

		# free
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].fonts[0].free = 'True'
		except ValueError as e:
			self.assertEqual(str(e), 'Wrong data type. Is <class \'str\'>, should be: <class \'bool\'>.')

		# name
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].families[0].fonts[0].name.en = ''
		i2.foundries[0].families[0].fonts[0].name.de = ''
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> --> <Font "YanoneKaffeesatz-Regular">.name is a required attribute, but empty'])

		# pdf
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].fonts[0].pdf = 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

		# postScriptName
		# TODO: write check for postScriptName
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].families[0].fonts[0].postScriptName = 'YanoneKaffeesatzRegular'
		validate = i2.validate()
		self.assertEqual(validate[2], [])

		# protected
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].fonts[0].protected = 'True'
		except ValueError as e:
			self.assertEqual(str(e), 'Wrong data type. Is <class \'str\'>, should be: <class \'bool\'>.')

		# purpose
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].fonts[0].purpose = 'anything'
		except ValueError as e:
			self.assertEqual(str(e), 'Unknown font type: "anything". Possible: [\'desktop\', \'web\', \'app\']')

		# setName
		# allowed to be emtpy
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].families[0].fonts[0].setName.en = ''
		validate = i2.validate()
		self.assertEqual(validate[2], [])

		#status
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].fonts[0].status = 'instable'
		except ValueError as e:
			self.assertEqual(str(e), "Unknown API command: \"instable\". Possible: [\'prerelease\', \'trial\', \'stable\']")

		# uniqueID
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].families[0].fonts[0].uniqueID = ''
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> --> <Font "YanoneKaffeesatz-Regular">.uniqueID is a required attribute, but empty'])
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].families[0].fonts[0].uniqueID = 'a' * 255
		validate = i2.validate()
		# TODO: The error message gets put out twice here. This is faulty
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> --> The suggested file name is longer than 255 characters: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa_1.0.otf', '<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> --> The suggested file name is longer than 255 characters: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa_1.0.otf'])
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].families[0].fonts[0].uniqueID = 'abc:def'
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> --> uniqueID must not contain the character : because it will be used for the font\'s file name on disk.'])



		# usedLicenses
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].families[0].fonts[0].usedLicenses = []
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> --> <Font "YanoneKaffeesatz-Regular">.usedLicenses is a required attribute, but empty'])
		try:
			i2.foundries[0].families[0].fonts[0].usedLicenses = ['hergerg']
		except ValueError as e:
			self.assertEqual(str(e), "Wrong data type. Is <class 'str'>, should be: <class 'typeWorld.api.LicenseUsage'>.")

		# variableFont
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].fonts[0].variableFont = 'True'
		except ValueError as e:
			self.assertEqual(str(e), 'Wrong data type. Is <class \'str\'>, should be: <class \'bool\'>.')

		# versions
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].families[0].versions = []
		i2.foundries[0].families[0].fonts[0].versions = []
		try:
			validate = i2.validate()
		except ValueError as e:
			self.assertEqual(str(e), '<Font "YanoneKaffeesatz-Regular"> has no version information, and neither has its family <Family "Yanone Kaffeesatz">. Either one needs to carry version information.')

		# other
		i2 = copy.deepcopy(installableFonts)
		print(i2.foundries[0].families[0].fonts[0])
		assert i2.foundries[0].families[0].fonts[0].parent == i2.foundries[0].families[0]
		assert type(i2.foundries[0].families[0].fonts[0].getDesigners()) == list

		# filename and purpose
		i2 = copy.deepcopy(installableFonts)
		self.assertEqual(i2.foundries[0].families[0].fonts[0].filename(i2.foundries[0].families[0].fonts[0].getVersions()[-1].number), 'yanone-kaffeesatz-regular_1.0.otf')
		i2.foundries[0].families[0].fonts[0].format = ''
		self.assertEqual(i2.foundries[0].families[0].fonts[0].filename(i2.foundries[0].families[0].fonts[0].getVersions()[-1].number), 'yanone-kaffeesatz-regular_1.0')
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> --> <Font "YanoneKaffeesatz-Regular"> is a desktop font (see .purpose), but has no .format value.'])


	def test_Family(self):

		print('test_Family()')

		# billboards
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].billboards[0] = 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

		# dateFirstPublished
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].dateFirstPublished = '2010-20-21'
		except ValueError as e:
			self.assertEqual(str(e), 'ValueError: time data \'2010-20-21\' does not match format \'%Y-%m-%d\'')

		# description
		# allowed to be empty
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].families[0].description.en = ''
		validate = i2.validate()
		self.assertEqual(validate[2], [])

		# designers
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].designers = 'yanone'
		except ValueError as e:
			self.assertEqual(str(e), 'Wrong data type. Is <class \'str\'>, should be: <class \'list\'>.')
		i2.foundries[0].families[0].designers = ['awieberg']
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "Yanone Kaffeesatz"> has designer "awieberg", but <InstallableFontsResponse>.designers has no matching designer.'])

		# inUseURL
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].inUseURL = 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

		# issueTrackerURL
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].issueTrackerURL = 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

		# name
		i2.foundries[0].families[0].name.en = ''
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "Awesome Fonts"> --> <Family "None">.name is a required attribute, but empty'])

		# pdf
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].pdf = 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

		# sourceURL
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].families[0].sourceURL = 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

		# uniqueID
		# TODO

		# versions
		# already check at font level

		i2 = copy.deepcopy(installableFonts)
		print(i2.foundries[0].families[0])
		assert i2.foundries[0].families[0].parent == i2.foundries[0]
		assert type(i2.foundries[0].families[0].getDesigners()) == list
		assert type(i2.foundries[0].families[0].getAllDesigners()) == list

		# Set Names
		i2 = copy.deepcopy(installableFonts)
		self.assertEqual(i2.foundries[0].families[0].setNames('de'), ['Desktop-Schriften'])
		self.assertEqual(i2.foundries[0].families[0].setNames('en'), ['Desktop Fonts'])
		self.assertEqual(i2.foundries[0].families[0].formatsForSetName('Desktop-Schriften', 'de'), ['otf'])
		self.assertEqual(i2.foundries[0].families[0].formatsForSetName('Desktop Fonts', 'en'), ['otf'])


	def test_Foundry(self):

		print('test_Foundry()')

		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].backgroundColor = 'CDEFGH'
		except ValueError as e:
			self.assertEqual(str(e), 'Not a valid hex color of format RRGGBB (like FF0000 for red): CDEFGH')

		# description
		# allowed to be empty
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].description.en = ''
		validate = i2.validate()
		self.assertEqual(validate[2], [])

		# email
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].email = 'post_at_yanone.de'
		except ValueError as e:
			self.assertEqual(str(e), 'Not a valid email format: post_at_yanone.de')

		# licenses
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].licenses = 'yanoneEULA'
		except ValueError as e:
			self.assertEqual(str(e), 'Wrong data type. Is <class \'str\'>, should be: <class \'list\'>.')

		# logo
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].logo = 'typeworldserver.com/?page=outputDataBaseFile&className=TWFS_FamilyBillboards&ID=2&field=image'
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

		# name
		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].name.en = ''
		i2.foundries[0].name.de = ''
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "None">.name is a required attribute, but empty'])

		# supportEmail
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].supportEmail = 'post_at_yanone.de'
		except ValueError as e:
			self.assertEqual(str(e), 'Not a valid email format: post_at_yanone.de')

		# facebook
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].facebook = 1
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')

		# instagram
		# TODO: test this value, can't currently be tested

		# skype
		# TODO: test this value, can't currently be tested

		# twitter
		# TODO: test this value, can't currently be tested

		# telephone
		# TODO: test this value, can't currently be tested

		# supportTelephone
		# TODO: test this value, can't currently be tested

		# website
		i2 = copy.deepcopy(installableFonts)
		try:
			i2.foundries[0].website = 1
		except ValueError as e:
			self.assertEqual(str(e), 'Needs to start with http:// or https://')


		i2 = copy.deepcopy(installableFonts)
		print(i2.foundries[0])
		assert i2.foundries[0].name.getTextAndLocale('en') == ('Awesome Fonts', 'en')
		assert i2.foundries[0].name.getTextAndLocale(['en']) == ('Awesome Fonts', 'en')
		assert i2.foundries[0].name.getTextAndLocale('de') == ('Tolle Schriften', 'de')
		assert i2.foundries[0].name.getTextAndLocale(['de']) == ('Tolle Schriften', 'de')
		assert i2.foundries[0].name.getTextAndLocale(['ar']) == ('Awesome Fonts', 'en')

		i2 = copy.deepcopy(installableFonts)
		i2.foundries[0].name.en = 'abc' * 1000
		validate = i2.validate()
		self.assertEqual(validate[2], ['<InstallableFontsResponse> --> <Foundry "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"> --> abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc.en is too long. Allowed are 100 characters.'])

		i2 = copy.deepcopy(installableFonts)
		foundry2 = copy.deepcopy(i2.foundries[0])
		i2.foundries.append(foundry2)
		validate = i2.validate()
		self.assertEqual(validate[2], ["<InstallableFontsResponse> --> Duplicate unique foundry IDs: ['yanone']", "<InstallableFontsResponse> --> Duplicate unique family IDs: ['yanone-yanonekaffeesatz']", "<InstallableFontsResponse> --> Duplicate unique family IDs: ['yanone-kaffeesatz-regular', 'yanone-kaffeesatz-bold']"])


	def test_otherStuff(self):

		print('test_otherStuff()')

		assert type(root.supportedCommands.index('installableFonts')) == int
		assert installableFonts.designers[0].parent == installableFonts

		success, rootCommand = user1.client.rootCommand(protectedSubscription)
		self.assertTrue(success)
		success, rootCommand = user1.client.rootCommand(protectedSubscription[1:])
		self.assertFalse(success)

		# TODO: Invite user to subscription with API endpoint as source

		self.assertEqual(typeWorld.client.helpers.addAttributeToURL('https://type.world?hello=world#xyz', 'hello=type&world=type'), 'https://type.world?hello=type&world=type#xyz')

	def test_InstallFontResponse(self):

		print('test_InstallFontResponse()')

		installFont = InstallFontResponse()
		try:
			installFont.type = 'abc'
		except ValueError as e:
			self.assertEqual(str(e), 'Unknown response type: "abc". Possible: [\'success\', \'error\', \'unknownFont\', \'insufficientPermission\', \'temporarilyUnavailable\', \'duplicateInstallation\', \'seatAllowanceReached\', \'validTypeWorldUserAccountRequired\', \'revealedUserIdentityRequired\']')

		installFont = InstallFontResponse()
		installFont.type = 'success'
		installFont.font = b'ABC'
		#installFont.encoding = 'base64'
		validate = installFont.validate()
		self.assertEqual(validate[2], ['<InstallFontResponse> --> <InstallFontResponse>.font is set, but <InstallFontResponse>.encoding is missing'])

		installFont = InstallFontResponse()
		installFont.type = 'success'
		#installFont.font = b'ABC'
		installFont.encoding = 'base64'
		validate = installFont.validate()
		self.assertEqual(validate[2], ['<InstallFontResponse> --> <InstallFontResponse>.type is set to success, but <InstallFontResponse>.font is missing'])

		installFont = InstallFontResponse()
		installFont.type = 'error'
		validate = installFont.validate()
		self.assertEqual(validate[2], ['<InstallFontResponse> --> <InstallFontResponse>.type is "error", but <InstallFontResponse>.errorMessage is missing.'])

		installFont = InstallFontResponse()
		installFont.type = 'error'
		try:
			d = installFont.dumpDict()
		except ValueError as e:
			self.assertEqual(str(e), '<InstallFontResponse> --> <InstallFontResponse>.type is "error", but <InstallFontResponse>.errorMessage is missing.')

	def test_UninstallFontResponse(self):

		print('test_UninstallFontResponse()')

		uninstallFont = UninstallFontResponse()
		try:
			uninstallFont.type = 'abc'
		except ValueError as e:
			self.assertEqual(str(e), 'Unknown response type: "abc". Possible: [\'success\', \'error\', \'unknownFont\', \'unknownInstallation\', \'insufficientPermission\', \'temporarilyUnavailable\', \'validTypeWorldUserAccountRequired\']')



	def test_SetAnonymousAppIDStatus(self):

		print('test_SetAnonymousAppIDStatus()')

		status = SetAnonymousAppIDStatusResponse()
		try:
			status.type = 'abc'
		except ValueError as e:
			self.assertEqual(str(e), 'Unknown response type: "abc". Possible: [\'success\', \'error\', \'insufficientPermission\', \'temporarilyUnavailable\']')


	def test_InstallableFontsResponse_Old(self):

		print('test_InstallableFontsResponse_Old()')


		# InstallFont

		responseCommand = InstallFontResponse()
		responseCommand.type = 'success'
		print(responseCommand)

		responseCommand.font = b'ABC'
		responseCommand.encoding = 'base64'

		# Output API response as JSON, includes validation
		json = responseCommand.dumpJSON()


		responseCommandInput = InstallFontResponse()
		responseCommandInput.loadJSON(json)

		# Let’s see if they are identical
		assert responseCommandInput.sameContent(responseCommand) == True

		responseCommandInput.validate()





		# UninstallFont

		responseCommand = UninstallFontResponse()
		responseCommand.type = 'success'
		print(responseCommand)

		# Output API response as JSON, includes validation
		json = responseCommand.dumpJSON()

		responseCommandInput = UninstallFontResponse()
		responseCommandInput.loadJSON(json)

		# Let’s see if they are identical
		assert responseCommandInput.sameContent(responseCommand) == True

		responseCommandInput.validate()




		# SetAnonymousAppIDStatusResponse

		responseCommand = SetAnonymousAppIDStatusResponse()
		responseCommand.type = 'success'
		print(responseCommand)

		# Output API response as JSON, includes validation
		json = responseCommand.dumpJSON()

		responseCommandInput = UninstallFontResponse()
		responseCommandInput.loadJSON(json)

		# Let’s see if they are identical
		assert responseCommandInput.sameContent(responseCommand) == True

		responseCommandInput.validate()



		## DOCU
		docu = RootResponse().docu()
		docu = InstallableFontsResponse().docu()
		docu = InstallFontResponse().docu()
		docu = UninstallFontResponse().docu()
		docu = SetAnonymousAppIDStatusResponse().docu()


		# Data types
		try:
			BooleanDataType().put('abc')
		except ValueError:
			pass

		try:
			IntegerDataType().put('abc')
		except ValueError:
			pass

		try:
			FloatDataType().put('abc')
		except ValueError:
			pass

		try:
			FontEncodingDataType().put('abc')
		except ValueError:
			pass

		try:
			VersionDataType().put('0.1.2.3')
		except ValueError:
			pass

		try:
			WebURLDataType().put('yanone.de')
		except ValueError:
			pass

		try:
			EmailDataType().put('post@yanone')
		except ValueError:
			pass

		try:
			HexColorDataType().put('ABCDEF') # pass
			HexColorDataType().put('ABCDEX') # error
		except ValueError:
			pass

		try:
			HexColorDataType().put('012345678')
		except ValueError:
			pass

		try:
			DateDataType().put('2018-02-28') # pass
			DateDataType().put('2018-02-30') # error
		except ValueError:
			pass


		text = MultiLanguageText()
		self.assertEqual(bool(text), False)
		text.en = 'Hello'
		self.assertEqual(bool(text), True)

		text.en = 'Hello'
		self.assertEqual(text.customValidation()[2], [])

		# HTML in Text
		text.en = 'Hello, <b>world</b>'
		self.assertNotEqual(text.customValidation()[2], [])

		# Markdown in Text
		text.en = 'Hello, _world_'
		self.assertNotEqual(text.customValidation()[2], [])


		description = MultiLanguageLongText()
		self.assertEqual(bool(description), False)
		description.en = 'Hello'
		self.assertEqual(bool(description), True)

		description.en = 'Hello'
		self.assertEqual(description.customValidation()[2], [])

		# HTML in Text
		description.en = 'Hello, <b>world</b>'
		self.assertNotEqual(description.customValidation()[2], [])

		# Markdown in Text
		description.en = 'Hello, _world_'
		self.assertEqual(description.customValidation()[2], [])

		i2 = copy.deepcopy(installableFonts)
		font = i2.foundries[0].families[0].fonts[0]

		# __repr__
		print(font.uniqueID)

		l = FontListProxy()
		print(l)
		l.append(Font())
		l[0] = Font()

		l = font.nonListProxyBasedKeys()

		font.doesntHaveThisAttribute = 'a'
		print(font.doesntHaveThisAttribute)
		try:
			print(font.doesntHaveThatAttribute)
		except:
			pass


		font.postScriptName = ''

		font.name = MultiLanguageText()
		font.name.en = None
		print(font.name.parent)
		try:
			print(api.validate())
		except:
			pass


		usedLicense = LicenseUsage()
		usedLicense.keyword = 'awesomeFontsEULAAAAA'
		font.usedLicenses.append(usedLicense)
		try:
			print(api.validate())
		except:
			pass


		font.versions = []
		font.parent.versions = []
		try:
			print(api.validate())
		except:
			pass


		font.designers.append('maxx')
		try:
			print(api.validate())
		except:
			pass




	def test_helpers(self):

		print('test_helpers()')


		# urlIsValid()
		self.assertEqual(typeWorld.client.urlIsValid('typeworld://json+https//s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/')[0], True)
		self.assertEqual(typeWorld.client.urlIsValid('https//s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/')[0], False)
		self.assertEqual(typeWorld.client.urlIsValid('typeworldjson://json+https//s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/')[0], False)

		# splitJSONURL()
		self.assertEqual(typeWorld.client.splitJSONURL('typeworld://json+https//s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/'), (
			'typeworld://',
			'json',
			'https://',
			's9lWvayTEOaB9eIIMA67',
			'bN0QnnNsaE4LfHlOMGkm',
			'typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/',
			))
		self.assertEqual(typeWorld.client.splitJSONURL('typeworld://json+https//s9lWvayTEOaB9eIIMA67@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/'), (
			'typeworld://',
			'json',
			'https://',
			's9lWvayTEOaB9eIIMA67',
			'',
			'typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/',
			))
		self.assertEqual(typeWorld.client.splitJSONURL('typeworld://json+https//typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/'), (
			'typeworld://',
			'json',
			'https://',
			'',
			'',
			'typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/',
			))
		self.assertEqual(typeWorld.client.splitJSONURL('typeworld://json+http//typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/'), (
			'typeworld://',
			'json',
			'http://',
			'',
			'',
			'typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/',
			))


		# Locale
		self.assertEqual(user0.client.locale(), ['en'])
		user0.client.preferences.set('localizationType', 'systemLocale')
		self.assertEqual(user0.client.locale(), ['en'])
		user0.client.preferences.set('localizationType', 'customLocale')
		self.assertEqual(user0.client.locale(), ['en'])
		user0.client.preferences.set('customLocaleChoice', 'de')
		self.assertEqual(user0.client.locale(), ['de', 'en'])

		from typeWorld.client.helpers import addAttributeToURL
		self.assertEqual(addAttributeToURL('https://type.world/', 'hello=world'), 'https://type.world/?hello=world')
		self.assertEqual(addAttributeToURL('https://type.world/?foo=bar', 'hello=world'), 'https://type.world/?foo=bar&hello=world')


	def test_simulateExternalScenarios(self):

		print('test_simulateExternalScenarios()')

		user0.takeDown()

		user0.client.testScenario = 'simulateEndpointDoesntSupportInstallFontCommand'
		success, message, publisher, subscription = user0.client.addSubscription(freeSubscription)
		self.assertEqual(success, False)

		user0.client.testScenario = 'simulateEndpointDoesntSupportInstallableFontsCommand'
		success, message, publisher, subscription = user0.client.addSubscription(freeSubscription)
		self.assertEqual(success, False)

		user0.client.testScenario = 'simulateCustomError'
		success, message, publisher, subscription = user0.client.addSubscription(freeSubscription)
		self.assertEqual(success, False)
		self.assertEqual(message.getText(), 'simulateCustomError')

		user0.client.testScenario = 'simulateNotOnline'
		success, message, publisher, subscription = user0.client.addSubscription(freeSubscription)
		self.assertEqual(success, False)

		user0.client.testScenario = 'simulateProgrammingError'
		success, message, publisher, subscription = user0.client.addSubscription(freeSubscription)
		self.assertEqual(success, False)
		self.assertEqual(message, 'Response from protocol.aboutToAddSubscription(): Error retrieving https://typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/: HTTP Error 500: Internal Server Error')

		success, message, publisher, subscription = user0.client.addSubscription('typeworld://unknownprotocol+https//typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/')
		self.assertEqual(success, False)
		self.assertEqual(message, 'Protocol unknownprotocol doesn’t exist in this app (yet).')

		success, message, publisher, subscription = user0.client.addSubscription('typeworld://json+https://s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/@')
		self.assertEqual(success, False)
		self.assertEqual(message, 'URL contains more than one @ sign, so don’t know how to parse it.')

		success, message, publisher, subscription = user0.client.addSubscription('typeworldjson://json+https://s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/')
		self.assertEqual(success, False)
		self.assertEqual(message, "Unknown custom protocol, known are: ['typeworld']")

		success, message, publisher, subscription = user0.client.addSubscription('typeworldjson//json+https://s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/')
		self.assertEqual(success, False)
		self.assertEqual(message, "Unknown custom protocol, known are: ['typeworld']")

		success, message, publisher, subscription = user0.client.addSubscription('typeworld://json+https://s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/:')
		self.assertEqual(success, False)
		self.assertEqual(message, "URL contains more than one :// combination, so don’t know how to parse it.")

		success, message, publisher, subscription = user0.client.addSubscription('typeworld://json+s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/')
		self.assertEqual(success, False)
		self.assertEqual(message, "URL is malformed.")



def setUp():

	global user0, user1, user2, user3, tempFolder
	tempFolder = tempfile.mkdtemp()
	user0 = User()
	user1 = User(testUser1)
	user2 = User(testUser2)
	user3 = User(testUser3)

	print('setUp()')

def tearDown():

	global user0, user1, user2, user3, tempFolder
	user0.takeDown()
	user1.takeDown()
	user2.takeDown()
	user3.takeDown()

	print('tearDown()')

	 # Local
	if not 'TRAVIS' in os.environ: os.rmdir(tempFolder)


if __name__ == '__main__':

	setUp()

	unittest.main(exit=False)

	tearDown()

