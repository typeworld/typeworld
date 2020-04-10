import urllib
import typeWorld.client.protocols
import typeWorld.api
from typeWorld.api import VERSION, NOFONTSAVAILABLE

def readJSONResponse(url, responses, acceptableMimeTypes, data = {}):
	d = {}
	d['errors'] = []
	d['warnings'] = []
	d['information'] = []

	root = typeWorld.api.RootResponse()

	request = urllib.request.Request(url)

	if not 'source' in data:
		data['source'] = 'typeWorldApp'

	# gather commands
	commands = [response._command['keyword'] for response in responses]
	data['commands'] = ','.join(commands)

	data = urllib.parse.urlencode(data)
	data = data.encode('ascii')
	
	try:
		import ssl, certifi
		sslcontext = ssl.create_default_context(cafile=certifi.where())
		response = urllib.request.urlopen(request, data, context=sslcontext)

		incomingMIMEType = response.headers['content-type'].split(';')[0]
		if not incomingMIMEType in acceptableMimeTypes:
			d['errors'].append('Resource headers returned wrong MIME type: "%s". Expected is "%s".' % (response.headers['content-type'], acceptableMimeTypes))

		if response.getcode() != 200:
			d['errors'].append(str(response.info()))

		if response.getcode() == 200:
			# Catching ValueErrors
			try:
				root.loadJSON(response.read().decode())
				information, warnings, errors = root.validate()

				if information: d['information'].extend(information)
				if warnings: d['warnings'].extend(warnings)
				if errors: d['errors'].extend(errors)
			except ValueError as e:
				d['errors'].append(str(e))


	except urllib.request.HTTPError as e:
		d['errors'].append('Error retrieving %s: %s' % (url, e))

	return root, d



class TypeWorldProtocol(typeWorld.client.protocols.TypeWorldProtocolBase):


	def initialize(self):
		self.versions = []
		self._rootCommand = None
		self._installableFontsCommand = None

	def loadFromDB(self):
		'''Overwrite this'''

		if self.get('installableFontsCommand'):
			api = typeWorld.api.InstallableFontsResponse()
			api.parent = self
			api.loadJSON(self.get('installableFontsCommand'))
			self._installableFontsCommand = api

		if self.get('rootCommand'):
			api = typeWorld.api.EndpointResponse()
			api.parent = self
			api.loadJSON(self.get('rootCommand'))
			self._rootCommand = api

	def latestVersion(self):
		return self._installableFontsCommand


	def updateRootCommand(self):
		self._rootCommand = None
		success, rootCommand = self.rootCommand()


	def returnRootCommand(self, testScenario):

		if not self._rootCommand:

			# Read response
			data = {
				'subscriptionID': self.url.subscriptionID, 
				'appVersion': VERSION,
			}
			if testScenario:
				data['testScenario'] = testScenario
			root, responses = readJSONResponse(self.connectURL(), [typeWorld.api.EndpointResponse()], typeWorld.api.INSTALLABLEFONTSCOMMAND['acceptableMimeTypes'], data = data)
			api = root.endpoint
			
			# Errors
			if responses['errors']:
				return False, responses['errors'][0]

			self._rootCommand = api

		# Success
		return True, self._rootCommand


	def returnInstallableFontsCommand(self):
		return True, self.latestVersion()

	def protocolName(self):
		return 'Type.World JSON Protocol'

	def update(self):

		self.updateRootCommand()

		data = {
			'subscriptionID': self.url.subscriptionID, 
			'anonymousAppID': self.client.anonymousAppID(), 
			'anonymousTypeWorldUserID': self.client.user(),
			'appVersion': VERSION,
			'mothership': self.client.mothership,
		}
		if self.client.testScenario:
			data['testScenario'] = self.client.testScenario
		secretKey = self.getSecretKey()
		if secretKey:
			data['secretKey'] = secretKey

		root, responses = readJSONResponse(self.connectURL(), [typeWorld.api.InstallableFontsResponse()], typeWorld.api.INSTALLABLEFONTSCOMMAND['acceptableMimeTypes'], data = data)
		api = root.installableFonts

		if responses['errors']:
			
			if self.url.unsecretURL() in self.subscription.parent._updatingSubscriptions:
				self.subscription.parent._updatingSubscriptions.remove(self.url.unsecretURL())
			self.subscription._updatingProblem = '\n'.join(responses['errors'])
			return False, self.subscription._updatingProblem, False

		if api.response == 'error':
			if self.url.unsecretURL() in self.subscription.parent._updatingSubscriptions:
				self.subscription.parent._updatingSubscriptions.remove(self.url.unsecretURL())
			self.subscription._updatingProblem = api.errorMessage
			return False, self.subscription._updatingProblem, False

		if api.response in ('temporarilyUnavailable', 'insufficientPermission', 'loginRequired'):
			if self.url.unsecretURL() in self.subscription.parent._updatingSubscriptions:
				self.subscription.parent._updatingSubscriptions.remove(self.url.unsecretURL())
			self.subscription._updatingProblem = '#(response.%s)' % api.response
			return False, self.subscription._updatingProblem, False


		# # Detect installed fonts now not available in subscription anymore and delete them
		# hasFonts = False
		# removeFonts = []
		# if api.response == NOFONTSAVAILABLE:
		# 	for foundry in self._installableFontsCommand.foundries:
		# 		for family in foundry.families:
		# 			for font in family.fonts:
		# 				hasFonts = True
		# 				removeFonts.append(font.uniqueID)
		# 	if removeFonts:
		# 		success, message = self.subscription.removeFonts(removeFonts)
		# 		if not success:
		# 			return False, 'Couldn’t uninstall previously installed fonts: %s' % message, True

		# Previously available fonts
		oldIDs = []
		for foundry in self._installableFontsCommand.foundries:
			for family in foundry.families:
				for font in family.fonts:
					oldIDs.append(font.uniqueID)
		# Newly available fonts
		newIDs = []
		for foundry in api.foundries:
			for family in foundry.families:
				for font in family.fonts:
					newIDs.append(font.uniqueID)

		# Deleted
		deletedFonts = list( set(oldIDs) - set(newIDs) )
		if deletedFonts:
			for fontID in deletedFonts:
				success, message = self.subscription.removeFonts([fontID])
				# if success == False:
				# 	return False, message, False

		identical = self._installableFontsCommand.sameContent(api)
		self._installableFontsCommand = api

		self.save()

		return True, None, not identical

	def setInstallableFontsCommand(self, command):
		self._installableFontsCommand = command
#		self.client.delegate.subscriptionWasUpdated(self.subscription.parent, self.subscription)


	def removeFonts(self, fonts, updateSubscription = False):

		data = {
			'fonts': ','.join(fonts),
			'anonymousAppID': self.client.anonymousAppID(),
			'anonymousTypeWorldUserID': self.client.user(),
			'subscriptionID': self.url.subscriptionID,
			'secretKey': self.getSecretKey(),
			'secretTypeWorldAPIKey': self.client.secretTypeWorldAPIKey,
			'appVersion': VERSION,
			'mothership': self.client.mothership,
		}
		if self.client.testScenario:
			data['testScenario'] = self.client.testScenario

		commands = [typeWorld.api.UninstallFontsResponse()]
		if updateSubscription:
			commands.append(typeWorld.api.InstallableFontsResponse())

		root, messages = readJSONResponse(self.connectURL(), commands, typeWorld.api.UNINSTALLFONTSCOMMAND['acceptableMimeTypes'], data = data)
		api = root.uninstallFonts


		if messages['errors']:
			return False, '\n\n'.join(messages['errors'])

		if updateSubscription and root.installableFonts:
			self.setInstallableFontsCommand(root.installableFonts)

		return True, api


	def installFonts(self, fonts, updateSubscription = False):

		# Build URL

		data = {
			'fonts': ','.join([f'{x[0]}/{x[1]}' for x in fonts]),
			'anonymousAppID': self.client.anonymousAppID(),
			'anonymousTypeWorldUserID': self.client.user(),
			'subscriptionID': self.url.subscriptionID,
			'secretKey': self.getSecretKey(),
			'secretTypeWorldAPIKey': self.client.secretTypeWorldAPIKey,
			'appVersion': VERSION,
			'mothership': self.client.mothership,
		}
		if self.client.testScenario:
			data['testScenario'] = self.client.testScenario

		if self.subscription.get('revealIdentity') and self.client.userName():
			data['userName'] = self.client.userName()
		if self.subscription.get('revealIdentity') and self.client.userEmail():
			data['userEmail'] = self.client.userEmail()

		# print('curl -d "%s" -X POST %s' % ('&'.join(['{0}={1}'.format(k, v) for k,v in data.items()]), url))

		commands = [typeWorld.api.InstallFontsResponse()]
		if updateSubscription:
			commands.append(typeWorld.api.InstallableFontsResponse())

		root, messages = readJSONResponse(self.connectURL(), commands, typeWorld.api.INSTALLFONTSCOMMAND['acceptableMimeTypes'], data = data)
		api = root.installFonts

		if messages['errors']:
			return False, '\n\n'.join(messages['errors'])

		if root.installableFonts:
			self.setInstallableFontsCommand(root.installableFonts)

		return True, api


	def aboutToAddSubscription(self, anonymousAppID, anonymousTypeWorldUserID, accessToken, secretTypeWorldAPIKey, testScenario):
		'''Overwrite this.
		Put here an initial health check of the subscription. Check if URLs point to the right place etc.
		Return False, 'message' in case of errors.'''

		# Read response
		data = {
			'subscriptionID': self.url.subscriptionID, 
			'secretKey': self.url.secretKey, 
			'anonymousAppID': anonymousAppID, 
			'anonymousTypeWorldUserID': anonymousTypeWorldUserID, 
			'accessToken': accessToken, 
			'secretTypeWorldAPIKey': secretTypeWorldAPIKey,
			'appVersion': VERSION,
			'mothership': self.client.mothership,
		}
		if testScenario:
			data['testScenario'] = testScenario

		root, responses = readJSONResponse(self.connectURL(), [typeWorld.api.InstallableFontsResponse()], typeWorld.api.INSTALLABLEFONTSCOMMAND['acceptableMimeTypes'], data = data)
		api = root.installableFonts
		
		# Errors
		if responses['errors']:
			return False, responses['errors'][0]

		# Check for installableFonts response support
		success, message = self.rootCommand(testScenario = testScenario)
		if success:
			rootCommand = message
		else:
			return False, 'Error when getting rootCommand: %s' % message

		if not 'installableFonts' in rootCommand.supportedCommands or not 'installFonts' in rootCommand.supportedCommands:
			return False, 'API endpoint %s does not support the "installableFonts" or "installFonts" commands.' % rootCommand.canonicalURL

		if api.response == 'error':
			return False, api.errorMessage

		# Predefined response messages
		if api.response != 'error' and api.response != 'success':
			return False, ['#(response.%s)' % api.response, '#(response.%s.headline)' % api.response]

		# Success

		self._installableFontsCommand = api

		if self.url.secretKey:
			self.setSecretKey(self.url.secretKey)
		return True, None

	def save(self):
		if self._installableFontsCommand:
			self.set('installableFontsCommand', self._installableFontsCommand.dumpJSON())
		if self._rootCommand:
			self.set('rootCommand', self._rootCommand.dumpJSON())

