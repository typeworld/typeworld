import sys, os

print(sys.version)

# if 'TRAVIS' in os.environ:
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import unittest
from typeWorld.client import APIClient, JSON, AppKitNSUserDefaults
import tempfile, os, traceback
tempFolder = tempfile.mkdtemp()
from typeWorld.api import *


freeSubscription = 'typeworld://json+https//typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/'
protectedSubscription = 'typeworld://json+https//s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/'
testUser = ('736b524a-cf24-11e9-9f62-901b0ecbcc7a', 'AApCEfatt6vE5H4m0pevPsQA9P7fYG8Q1uhsNFYV') # test@type.world
testUser2 = ('8d48dafc-d07d-11e9-a3e3-901b0ecbcc7a', 'XPd2QbwHskEDzLeUXZxysGkiJmASHLhXxQfgTZCD') # test2@type.world
testUser3 = ('e865a474-d07d-11e9-982c-901b0ecbcc7a', 'LN1LYRgVYcQhEgulYmUdBgJObq2R4VCgL4rdnnZ5') # test3@type.world



class User(object):
	def __init__(self, login = None):
		self.login = login
		self.prefFile = os.path.join(tempFolder, str(id(self)) + '.json')
		self.client = APIClient(preferences = AppKitNSUserDefaults('world.type.test%s' % id(self)) if MAC else JSON(self.prefFile))

		if self.login:
			self.linkUser()
			self.clearInvitations()
			self.clearSubscriptions()

	def linkUser(self):
		if self.login:
			self.client.linkUser(*self.login)


	def testFont(self):
		if self.client.publishers():
			return self.client.publishers()[0].subscriptions()[-1].protocol.installableFontsCommand().foundries[0].families[0].fonts[0]
		else:
			raise Exception('No test font available')

	def clearSubscriptions(self):
		for publisher in self.client.publishers():
			publisher.delete()

	def clearInvitations(self):
		for invitation in self.client.pendingInvitations():
			invitation.decline()

	def takeDown(self):
		self.clearInvitations()
		self.clearSubscriptions()
		if self.login:
			self.client.unlinkUser()



class TestStringMethods(unittest.TestCase):


	def test_normalSubscription(self):



		# General stuff
		self.assertEqual(type(user0.client.locale()), list)
		self.assertTrue(typeWorld.client.validURL(freeSubscription))










		## Scenario 1:
		## Test a simple subscription of free fonts without Type.World user account

		success, message, publisher, subscription = user0.client.addSubscription(freeSubscription)
		print(success, message)

		self.assertEqual(success, True)
		self.assertEqual(user0.client.publishers()[0].canonicalURL, 'https://typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/')
		self.assertEqual(len(user0.client.publishers()[0].subscriptions()), 1)
		self.assertEqual(len(user0.client.publishers()[0].subscriptions()[-1].protocol.installableFontsCommand().foundries), 1)
		self.assertEqual(user0.client.publishers()[0].subscriptions()[-1].protocol.installableFontsCommand().foundries[0].name.getTextAndLocale(), ('Test Foundry', 'en'))

		# Logo
		success, logo, mimeType = subscription.resourceByURL(user0.client.publishers()[0].subscriptions()[0].protocol.installableFontsCommand().foundries[0].logo)
		self.assertEqual(success, True)
		self.assertTrue(logo.startswith('<?xml version="1.0" encoding="utf-8"?>'))


		user0.clearSubscriptions()



		### ###



		# Scenario 2:
		# Protected subscription, installation on machine without user account
		# This is supposed to fail because accessing protected subscriptions requires a valid Type.World user account, but user0 is not linked with a user account
		result = user0.client.addSubscription(protectedSubscription)
		print(result)
		success, message, publisher, subscription = result

		self.assertEqual(success, False)
		self.assertEqual(message, '#(response.insufficientPermission)')



		### ###



		# Scenario 3:
		# Protected subscription, installation on first machine with Type.World user account
		result = user1.client.addSubscription(protectedSubscription)
		print(result)
		success, message, publisher, subscription = result

		self.assertEqual(success, True)
		self.assertEqual(len(user1.client.publishers()[0].subscriptions()), 1)
		self.assertEqual(len(user1.client.publishers()[0].subscriptions()[-1].protocol.installableFontsCommand().foundries), 1)

		user1.client.downloadSubscriptions()
		user1.client.publishers()[0].update()
		self.assertEqual(user1.client.publishers()[0].stillUpdating(), False)
		print(user1.client.publishers()[0].updatingProblem())
		self.assertEqual(user1.client.allSubscriptionsUpdated(), True)

		# Install Font
		# First it's meant to fail because the user hasn't accepted the Terms & Conditions
		self.assertEqual(user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number), (False, ['#(response.termsOfServiceNotAccepted)', '#(response.termsOfServiceNotAccepted.headline)']))
		user1.client.publishers()[0].subscriptions()[-1].set('acceptedTermsOfService', True)
		# Then it's supposed to fail because the server requires the revealted user identity for this subscription
		self.assertEqual(user1.client.publishers()[0].subscriptions()[-1].protocol.installableFontsCommand().prefersRevealedUserIdentity, True)
		self.assertEqual(user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number), (False, ['#(response.revealedUserIdentityRequired)', '#(response.revealedUserIdentityRequired.headline)']))
		user1.client.publishers()[0].subscriptions()[-1].set('revealIdentity', True)
		# Finally supposed to pass
		self.assertEqual(user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number), (True, None))

		# This is also supposed to delete the installed protected font
		user1.client.unlinkUser()
		user1.linkUser()

		# Install again
		self.assertEqual(user1.client.publishers()[0].subscriptions()[-1].installFont(user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number), (True, None))



		### ###



		# Scenario 4:
		# Protected subscription, installation on second machine

		# Supposed to reject because seats are limited to 1
		success, message, publisher, subscription = user2.client.addSubscription(protectedSubscription)
		print(success, message)

		# Two versions available
		self.assertEqual(len(user2.client.publishers()[0].subscriptions()[-1].installFont(user2.testFont().uniqueID, user2.testFont().getVersions())), 2)

		# Attempt to install font for user2, supposed to fail
		user2.client.publishers()[0].subscriptions()[-1].set('acceptedTermsOfService', True)
		user2.client.publishers()[0].subscriptions()[-1].set('revealIdentity', True)
		self.assertEqual(user2.client.publishers()[0].subscriptions()[-1].installFont(user2.testFont().uniqueID, user2.testFont().getVersions()[-1].number), (False, ['#(response.seatAllowanceReached)', '#(response.seatAllowanceReached.headline)']))

		# Uninstall font for user1
		result = user1.client.publishers()[0].subscriptions()[-1].removeFont(user1.testFont().uniqueID)
		print(result)
		self.assertEqual(result, (True, None))

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

		# Uninstall font for user2
		result = user2.client.publishers()[0].subscriptions()[-1].removeFont(user2.testFont().uniqueID)
		print(result)
		self.assertEqual(result, (True, None))

		# Clear
		user2.clearSubscriptions()
		self.assertEqual(len(user2.client.publishers()), 0)




		### ###



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
		self.assertEqual(user1.client.userEmail(), 'test@type.world')
		result = user1.client.publishers()[0].subscriptions()[-1].inviteUser('test@type.world')
		self.assertEqual(result, (False, ['#(response.sourceAndTargetIdentical)', '#(response.sourceAndTargetIdentical.headline)']))

		# Invite real user
		result = user1.client.publishers()[0].subscriptions()[-1].inviteUser('test2@type.world')
		self.assertEqual(result, (True, None))

		# Update third user
		self.assertEqual(len(user2.client.pendingInvitations()), 0)
		self.assertEqual(len(user2.client.publishers()), 0)
		user2.client.downloadSubscriptions()
		self.assertEqual(len(user2.client.pendingInvitations()), 1)

		# Accept invitation
		user2.client.pendingInvitations()[0].accept()
		user2.client.downloadSubscriptions()
		self.assertEqual(len(user2.client.pendingInvitations()), 0)
		self.assertEqual(len(user2.client.publishers()), 1)

		# Invite yet another user
		self.assertEqual(len(user3.client.pendingInvitations()), 0)
		self.assertEqual(len(user3.client.publishers()), 0)
		result = user2.client.publishers()[0].subscriptions()[-1].inviteUser('test3@type.world')
		self.assertEqual(result, (True, None))
		user2.client.downloadSubscriptions()
		self.assertEqual(len(user2.client.sentInvitations()), 1)

		# Decline invitation
		user3.client.downloadSubscriptions()
		self.assertEqual(len(user3.client.pendingInvitations()), 1)
		user3.client.pendingInvitations()[0].decline()
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

		# Accept invitation
		user3.client.downloadSubscriptions()
		self.assertEqual(len(user3.client.pendingInvitations()), 1)
		user3.client.pendingInvitations()[0].accept()
		self.assertEqual(len(user3.client.publishers()), 1)

		# Delete subscription from first user. Subsequent invitation must then be taken down as well.
		user1.client.publishers()[0].subscriptions()[-1].delete()
		user2.client.downloadSubscriptions()
		user3.client.downloadSubscriptions()
		self.assertEqual(len(user2.client.pendingInvitations()), 0)
		self.assertEqual(len(user3.client.pendingInvitations()), 0)








	def test_api(self):



		# InstallableFonts

		# Root of API
		root = RootResponse()
		docu = root.docu()
		root.name.en = 'Font Publisher'
		root.canonicalURL = 'https://fontpublisher.com/api/'
		root.adminEmail = 'admin@fontpublisher.com'
		root.supportedCommands = [x['keyword'] for x in COMMANDS] # this API supports all commands

		# Create API response as JSON
		json = root.dumpJSON()

		# Let’s see it
		print(json)



		# Response for 'availableFonts' command
		# Response for 'availableFonts' command
		installableFonts = InstallableFontsResponse()
		installableFonts.type = 'success'
		print(installableFonts)

		# Add designer to root of response
		designer = Designer()
		designer.keyword = 'max'
		designer.name.en = 'Max Mustermann'
		installableFonts.designers.append(designer)
		print(designer)
		assert designer.parent == installableFonts

		installableFonts.designers.extend([designer])
		installableFonts.designers.remove(installableFonts.designers[-1])
		assert len(installableFonts.designers) == 1
		print(installableFonts.designers)

		# Add foundry to root of response
		foundry = Foundry()
		foundry.uniqueID = 'yanone'
		foundry.name.en = 'Awesome Fonts'
		foundry.name.de = 'Tolle Schriften'
		foundry.website = 'https://awesomefonts.com'
		installableFonts.foundries.append(foundry)
		print(foundry)
		print(foundry.name.getTextAndLocale('en'))
		print(foundry.name.getTextAndLocale('ar'))
		assert foundry.name.getTextAndLocale('en') == ('Awesome Fonts', 'en')
		assert foundry.name.getTextAndLocale(['en']) == ('Awesome Fonts', 'en')
		assert foundry.name.getTextAndLocale('de') == ('Tolle Schriften', 'de')
		assert foundry.name.getTextAndLocale(['de']) == ('Tolle Schriften', 'de')

		# Add license to foundry
		license = LicenseDefinition()
		license.keyword = 'awesomeFontsEULA'
		license.name.en = 'Awesome Fonts Desktop EULA'
		license.URL = 'https://awesomefonts.com/EULA/'
		foundry.licenses.append(license)
		print(license)
		assert license.parent == foundry

		# Add font family to foundry
		family = Family()
		family.uniqueID = 'yanone-AwesomeSans'
		family.name.en = 'Awesome Sans'
		family.designers.append('max')
		foundry.families.append(family)
		print(family)
		assert family.parent == foundry

		# Add version to font
		version = Version()
		version.number = 0.1
		family.versions.append(version)
		print(version)
		assert version.isFontSpecific() == False
		assert version.parent == family
		assert type(family.getDesigners()) == list
		assert type(family.getAllDesigners()) == list

		# Add font to family
		font = Font()
		font.uniqueID = 'yanone-NonameSans-Regular'
		font.name.en = 'Regular'
		font.postScriptName = 'AwesomeSans-Regular'
		font.purpose = 'desktop'
		print(font.format)
		font.format = 'otf'
		font.designers.append('max')
		font.dateAddedForUser = '2018-04-01'
		family.fonts.append(font)
		print(font.validate())
		print(font.getDesigners())
		usedLicense = LicenseUsage()
		usedLicense.keyword = 'awesomeFontsEULA'
		font.usedLicenses.append(usedLicense)
		print(usedLicense)
		print(font)
		assert usedLicense.parent == font


		# Add font to family
		font = Font()
		font.uniqueID = 'yanone-NonameSans-Bold'
		font.name.en = 'Regular'
		font.postScriptName = 'AwesomeSans-Bold'
		font.purpose = 'desktop'
		font.format = 'otf'
		usedLicense = LicenseUsage()
		usedLicense.keyword = 'awesomeFontsEULA'
		font.usedLicenses.append(usedLicense)
		family.fonts.append(font)
		assert usedLicense.parent == font
		assert font.parent == family

		# Add version to font
		version = Version()
		version.number = 0.2
		font.versions.append(version)
		print(version)
		assert version.isFontSpecific() == True
		assert version.parent == font

		assert len(font.getVersions()) == 2
		assert type(font.getDesigners()) == list

		# Output API response as JSON, includes validation
		print(installableFonts.validate())
		information, warnings, critical = installableFonts.validate()
		# Supposed to contain a warning about how the name of the InstallableFontsResponse shouldn't be empy
		assert information == []
		assert warnings != []
		assert critical == []

		json = installableFonts.dumpJSON()

		# Let’s see it
		print(json)

		# Load a second API instance from that JSON
		installableFontsInput = InstallableFontsResponse()
		installableFontsInput.loadJSON(json)

		# Let’s see if they are identical
		assert installableFontsInput.sameContent(installableFonts) == True

		installableFontsInput.validate()





		# Check for errors

		try: 
			root.licenseIdentifier = 'abc'
		except ValueError:
		 	pass
		root.licenseIdentifier = 'CC-BY-NC-ND-4.0'

		try: 
			font.format = 'abc'
		except ValueError:
			pass


		try: 
			font.uniqueID = 'a' * 500
		except ValueError:
			pass


		font.uniqueID = 'a' * 255
		filename = font.filename(font.versions[-1].number)
		print(filename, len(filename))
		information, warnings, critical = installableFonts.validate()
		assert critical != []

		font.uniqueID = 'abc:def'
		information, warnings, critical = installableFonts.validate()
		assert critical != []

		# Back to normal
		font.uniqueID = 'yanone-NonameSans-Bold'
		information, warnings, critical = installableFonts.validate()
		assert critical == []


		try:
			# Too long name
			foundry.name.en = 'abc' * 1000
			# Output API response as JSON, includes validation
			json = installableFonts.dumpJSON()
		except ValueError:
			pass
		foundry.name.en = 'abc'
		


		# InstallFont

		responseCommand = InstallFontResponse()
		docu = responseCommand.docu()
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
		docu = responseCommand.docu()
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
		docu = responseCommand.docu()
		responseCommand.type = 'success'
		print(responseCommand)

		# Output API response as JSON, includes validation
		json = responseCommand.dumpJSON()

		responseCommandInput = UninstallFontResponse()
		responseCommandInput.loadJSON(json)

		# Let’s see if they are identical
		assert responseCommandInput.sameContent(responseCommand) == True

		responseCommandInput.validate()














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


		try:
			font.type = 'abc'
		except:
			pass

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

if __name__ == '__main__':


	user0 = User()
	user1 = User(testUser)
	user2 = User(testUser2)
	user3 = User(testUser3)

	unittest.main()

	#Takedown
	user0.takeDown()
	user1.takeDown()
	user2.takeDown()
	user3.takeDown()

	 # Local
	if not 'TRAVIS' in os.environ:
	#	os.remove(prefFile)
		os.rmdir(tempFolder)
