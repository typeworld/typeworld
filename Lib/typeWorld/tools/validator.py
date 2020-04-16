import typeWorld.client, typeWorld.api
import traceback
from typeWorld.client.helpers import Garbage


def validateAPIEndpoint(subscriptionURL, responses = {}, endpointURL = 'https://api.type.world/v1'):

	# Initiate 
	if not responses:
		responses = {
			'response': 'success',
		}
		responses['version'] = typeWorld.api.VERSION


	responses['stages'] = []
	responses['information'] = []
	responses['warnings'] = []
	responses['errors'] = []

	typeWorldClient = typeWorld.client.APIClient(mothership = endpointURL)
	typeWorldClient2 = typeWorld.client.APIClient(mothership = endpointURL)
	testUser = (f'{Garbage(20)}@type.world', Garbage(20))
	testUser2 = (f'{Garbage(20)}@type.world', Garbage(20))
	check = None
	stage = None
	stages = ['Setup', 'Free fonts', 'Non-expiring protected fonts', 'Expiring protected fonts', 'Teardown']

	serverRequiresValidUser = False

	class Check(object):
		def __init__(self, description):
			self.description = description

		def success(self, message = None):

			d = {}
			d['description'] = self.description
			d['result'] = 'passed'
			d['comments'] = message or ''
			responses['stages'][-1]['log'].append(d)


		def fail(self, message):

			d = {}
			d['description'] = self.description
			d['result'] = 'failed'
			d['comments'] = message or ''
			responses['stages'][-1]['log'].append(d)

			responses['stages'][-1]['result'] = 'failed'
			responses['response'] = 'failed'
			responses['errors'].append(message)
			typeWorldClient.deleteUserAccount(*testUser)
			typeWorldClient2.deleteUserAccount(*testUser2)


	class Stage(object):
		def __init__(self, description):

			self.description = description
			assert self.description in stages

			# Add previous stage to finished list
			d = {}
			d['name'] = self.description
			d['log'] = []
			d['result'] = 'incomplete'
			responses['stages'].append(d)

		def complete(self):
			responses['stages'][-1]['result'] = 'passed'
			stages.remove(self.description)

		def incomplete(self):
			responses['stages'][-1]['result'] = 'notTested'


	try:

		#############################
		#############################
		stage = Stage('Setup')

		## Check EndpointResponse
		check = Check('Loading `EndpointResponse`')
		success, message = typeWorldClient.rootCommand(subscriptionURL)

		if type(message) == list:
			message = message[0]

		passOnResponses = []

		if success:
			check.success()
		else:
			if message in passOnResponses:
				check.success()
			else:
				check.fail(message)
				return

		## Check normal subscription
		check = Check('Loading subscription with `installableFonts` command')
		success, message, publisher, subscription = typeWorldClient.addSubscription(subscriptionURL)

		if type(message) == list:
			message = message[0]

		passOnResponses = ['#(response.validTypeWorldUserAccountRequired)']

		if success:
			check.success()
		else:
			if message in passOnResponses:
				pass
			else:
				check.fail(message)
				return

		#(response.validTypeWorldUserAccountRequired)
		if message == '#(response.validTypeWorldUserAccountRequired)':

			check.success('Publisher server responded with `validTypeWorldUserAccountRequired`. Need to create valid user account first.')
			serverRequiresValidUser = True

			# Create User Account
			check = Check('Create first Type.World user account')
			success, message = typeWorldClient.createUserAccount('API Validator Test User', testUser[0], testUser[1], testUser[1])

			if type(message) == list:
				message = message[0]

			passOnResponses = []

			if success:
				check.success()
			else:
				if message in passOnResponses:
					check.success()
				else:
					check.fail(message)
					return

			## Retry normal subscription
			check = Check('Loading subscription another time, this time with valid Type.World user account')
			success, message, publisher, subscription = typeWorldClient.addSubscription(subscriptionURL)

			if type(message) == list:
				message = message[0]

			passOnResponses = []

			if success:
				check.success()
			else:
				if message in passOnResponses:
					check.success()
				else:
					check.fail(message)
					return

		## Test for fonts
		freeFonts = []
		protectedFonts = []
		protectedNonExpiringFonts = []
		protectedExpiringFonts = []
		protectedNonExpiringYetTrialFonts = []

		for publisher in typeWorldClient.publishers():
			for subscription in publisher.subscriptions():
				for foundry in subscription.protocol.installableFontsCommand()[1].foundries:
					for family in foundry.families:
						for font in family.fonts:
							if font.free:
								freeFonts.append(font)
							if font.protected:
								protectedFonts.append(font)
								if font.expiryDuration:
									protectedNonExpiringYetTrialFonts.append(font)
								elif font.expiry:
									protectedExpiringFonts.append(font)
								else:
									protectedNonExpiringFonts.append(font)

		check = Check('Looking for fonts')

		protectedNonExpiringFontsVerb = 'is' if len(protectedNonExpiringFonts) == 1 else 'are'
		protectedExpiringFontsVerb = 'is' if len(protectedExpiringFonts) == 1 else 'are'
		protectedNonExpiringYetTrialFontsVerb = 'carries' if len(protectedNonExpiringYetTrialFonts) == 1 else 'carry'

		check.success(f'Found {len(freeFonts)} free fonts, {len(protectedFonts)} protected fonts, of which {len(protectedNonExpiringFonts)} {protectedNonExpiringFontsVerb} not expiring at all, {len(protectedExpiringFonts)} {protectedExpiringFontsVerb} currently expiring, and {len(protectedNonExpiringYetTrialFonts)} {protectedNonExpiringYetTrialFontsVerb} a `expiryDuration` attribute but is/are currently not yet expiring.')


		if protectedFonts and not serverRequiresValidUser:
			check = Check(f'Check if server responded with `validTypeWorldUserAccountRequired` when no Type.World user credentials were given')
			check.fail('The subscription holds protected fonts, but the server didn’t reject requests with the `validTypeWorldUserAccountRequired` response when queried without Type.World user credentials (`anonymousUserID` and `secretKey`). In that case it must serve the `validTypeWorldUserAccountRequired` response for both the `installableFonts` as well as the `installFonts` response.')
			return

		stage.complete()


		# Install Free Font
		if freeFonts:

			#############################
			#############################
			stage = Stage('Free fonts')

			font = freeFonts[0]
			subscription = font.parent.parent.parent.parent.subscription
			check = Check(f'Installing first found free font `{font.postScriptName}`')
			success, message = subscription.installFonts([[font.uniqueID, font.getVersions()[-1].number]])

			if type(message) == list:
				message = message[0]

			passOnResponses = ['#(response.termsOfServiceNotAccepted)']

			if success:
				check.success()
			else:
				if message in passOnResponses:
					check.success()
				else:
					check.fail(message)
					return

			# Agree to terms, repeat
			if message == '#(response.termsOfServiceNotAccepted)':

				subscription.set('acceptedTermsOfService', True)
				check.success('The internal client responded with `termsOfServiceNotAccepted`. So we simulate the click on the acceptance button here and try again.')
				check = Check(f'Installing first valid free font `{font.postScriptName}`')

				# Repeat
				success, message = subscription.installFonts([[font.uniqueID, font.getVersions()[-1].number]])

				if type(message) == list:
					message = message[0]

				passOnResponses = []

				if success:
					check.success()
				else:
					if message in passOnResponses:
						check.success()
					else:
						check.fail(message)
						return


			stage.complete()

		# Install protected fonts
		if protectedFonts:

			# Non-expiring
			if protectedNonExpiringFonts:

				#############################
				#############################
				stage = Stage('Non-expiring protected fonts')

				check = Check(f'Checking for the existence of a non-expiring protected font with installed seats of 0 and a seat limit of 1, so we can test for reaching seat allowances')
				validFont = None
				for font in protectedNonExpiringFonts:
					if len(font.usedLicenses) == 1:
						for usedLicense in font.usedLicenses:
							if usedLicense.seatsAllowed == 1 and usedLicense.seatsInstalled == 0:
								validFont = font
								break

				if not validFont:
					check.fail('For testing purposes, this subscription needs one non-expiring protected font that carries one LicenseUsage with a `seatsInstalled` attribute of `0` and a `seatsAllowed` attribute of `1`. Otherwise, this test needs to install too many fonts.')
					return

				# Install font. Expected to fail because of un-agreed Terms & Conditions
				font = validFont
				fontID = font.uniqueID
				subscription = font.parent.parent.parent.parent.subscription
				check = Check(f'Installing first valid non-expiring protected font `{font.postScriptName}`')
				success, message = subscription.installFonts([[font.uniqueID, font.getVersions()[-1].number]])

				if type(message) == list:
					message = message[0]

				passOnResponses = ['#(response.termsOfServiceNotAccepted)']

				if success:
					check.success()
				else:
					if message in passOnResponses:
						pass
					else:
						check.fail(message)
						return

				# Agree to terms, repeat
				if message == '#(response.termsOfServiceNotAccepted)':
					subscription.set('acceptedTermsOfService', True)
					check.success('The internal client responded with `termsOfServiceNotAccepted`. So we simulate the click on the acceptance button here and try again.')
					check = Check(f'Installing first valid non-expiring protected font `{font.postScriptName}`')

					# Repeat
					success, message = subscription.installFonts([[font.uniqueID, font.getVersions()[-1].number]])

					if type(message) == list:
						message = message[0]

					passOnResponses = ['#(response.revealedUserIdentityRequired)']

					if success:
						check.success()
					else:
						if message in passOnResponses:
							pass
						else:
							check.fail(message)
							return

				# Agree to terms, repeat
				if message == '#(response.revealedUserIdentityRequired)':
					subscription.set('revealIdentity', True)
					check.success('The server requested to have the user’s identity revealed as per the `revealedUserIdentityRequired` response. Let’s agree and try again.')
					check = Check(f'Installing first valid non-expiring protected font `{font.postScriptName}`')

					# Repeat
					success, message = subscription.installFonts([[font.uniqueID, font.getVersions()[-1].number]])

					if type(message) == list:
						message = message[0]

					passOnResponses = []

					if success:
						check.success()
					else:
						if message in passOnResponses:
							check.success()
						else:
							check.fail(message)
							return

				# See if installed Seats changed
				check = Check(f'Check if installed seats of `{font.postScriptName}` license changed from `0` to `1` after font installation')
				# Reload font object
				font = subscription.fontByID(fontID)
				if font.usedLicenses[0].seatsInstalled == 1:
					check.success()
				else:
					check.fail(f'Font’s `seatsInstalled` attribute is `{font.usedLicenses[0].seatsInstalled}`, should be `1`.')
					return

				# Install font on second computer
				# Create User Account
				check = Check('Create second Type.World user account')
				success, message = typeWorldClient2.createUserAccount('API Validator Test User 2', testUser2[0], testUser2[1], testUser2[1])

				if type(message) == list:
					message = message[0]

				passOnResponses = []

				if success:
					check.success()
				else:
					if message in passOnResponses:
						check.success()
					else:
						check.fail(message)
						return

				## Load normal subscription
				check = Check('Loading subscription for second user')
				success, message, publisher2, subscription2 = typeWorldClient2.addSubscription(subscriptionURL)

				if type(message) == list:
					message = message[0]

				passOnResponses = []

				if success:
					check.success()
				else:
					if message in passOnResponses:
						check.success()
					else:
						check.fail(message)
						return

				subscription2.set('acceptedTermsOfService', True)
				subscription2.set('revealIdentity', True)
				font2 = subscription2.fontByID(fontID)

				# See if installed Seats changed
				check = Check(f'Check if installed seats of `{font2.postScriptName}` for second user is also `1`')
				if font2.usedLicenses[0].seatsInstalled == 1:
					check.success()
				else:
					check.fail(f'Font’s `seatsInstalled` attribute is `{font2.usedLicenses[0].seatsInstalled}`, should be `1`.')
					return


				# Install Font
				check = Check(f'Install same `{font2.postScriptName}` for second user, expecting to fail with `seatAllowanceReached` response')
				success, message = subscription2.installFonts([[font2.uniqueID, font2.getVersions()[-1].number]])

				if type(message) == list:
					message = message[0]

				passOnResponses = ['#(response.seatAllowanceReached)']

				if success:
					check.success()
				else:
					if message in passOnResponses:
						check.success()
					else:
						check.fail(message)
						return

				# # Seat allowance reached
				# if message == '#(response.seatAllowanceReached)':
				# 	check.success()

				# Uninstall font for first user
				check = Check(f'Uninstall `{font2.postScriptName}` for first user')
				success, message = subscription.removeFonts([font.uniqueID])

				if type(message) == list:
					message = message[0]

				passOnResponses = []

				if success:
					check.success()
				else:
					if message in passOnResponses:
						check.success()
					else:
						check.fail(message)
						return

				# See if installed Seats changed
				check = Check(f'Check if installed seats of `{font.postScriptName}` license changed from `1` to `0` after font removal')
				# Reload font object
				font = subscription.fontByID(fontID)
				if font.usedLicenses[0].seatsInstalled == 0:
					check.success()
				else:
					check.fail(f'Font’s `seatsInstalled` attribute is `{font.usedLicenses[0].seatsInstalled}`, should be `0`.')
					return

				# See if installed Seats changed
				check = Check(f'Check if installed seats of `{font2.postScriptName}` license changed from `1` back to `0` after subscription update for second user')
				subscription2.update()
				# Reload font object
				font2 = subscription2.fontByID(fontID)
				if font2.usedLicenses[0].seatsInstalled == 0:
					check.success()
				else:
					check.fail(f'Font’s `seatsInstalled` attribute is `{font2.usedLicenses[0].seatsInstalled}`, should be `0`.')
					return

				# Install Font
				check = Check(f'Install `{font2.postScriptName}` again for second user')
				success, message = subscription2.installFonts([[font2.uniqueID, font2.getVersions()[-1].number]])

				if type(message) == list:
					message = message[0]

				passOnResponses = []

				if success:
					check.success()
				else:
					if message in passOnResponses:
						check.success()
					else:
						check.fail(message)
						return

				# Uninstall font for second user
				check = Check(f'Uninstall `{font2.postScriptName}` for second user')
				success, message = subscription2.removeFonts([font2.uniqueID])

				if type(message) == list:
					message = message[0]

				passOnResponses = []

				if success:
					check.success()
				else:
					if message in passOnResponses:
						check.success()
					else:
						check.fail(message)
						return

				# Uninstall font for second user, a second time
				check = Check(f'Uninstall `{font2.postScriptName}` for second user yet again, this time expecting `unknownInstallation` response because font shouldn’t be recorded as installed anymore')
				success, message = subscription2.removeFonts([font2.uniqueID], dryRun = True)

				if type(message) == list:
					message = message[0]

				passOnResponses = ['#(response.unknownInstallation)']

				if success:
					check.success()
				else:
					if message in passOnResponses:
						check.success()
					else:
						check.fail(message)
						return
					

				stage.complete()

	except:
		if stage and check:
			check.fail(traceback.format_exc())
		if stage:
			stage.complete()

		responses['response'] = 'failure'
		responses['errors'] = [traceback.format_exc()]

	#############################
	#############################
	stage = Stage('Teardown')
	check = Check('Uninstall all remaining fonts and delete temporary user accounts (if created)')

	success, message = typeWorldClient.deleteUserAccount(*testUser)
	if type(message) == list:
		message = message[0]

	passOnResponses = ['#(response.userUnknown)']

	if success:
		pass
	else:
		if message in passOnResponses:
			check.success()
		else:
			check.fail(message)
			return

	success, message = typeWorldClient2.deleteUserAccount(*testUser2)
	if type(message) == list:
		message = message[0]

	passOnResponses = ['#(response.userUnknown)']

	if success:
		pass
	else:
		if message in passOnResponses:
			check.success()
		else:
			check.fail(message)
			return

	check.success()
	stage.complete()

	for stage in stages:
		stage = Stage(stage)
		stage.incomplete()

	return responses

