from typeWorld.client.protocols import *



def readJSONResponse(url, api, acceptableMimeTypes, data = {}, JSON = None):
	d = {}
	d['errors'] = []
	d['warnings'] = []
	d['information'] = []

	# Take URL apart here
	customProtocol, protocol, transportProtocol, subscriptionID, secretKey, restDomain = splitJSONURL(url)
	url = transportProtocol + restDomain


	request = urllib.request.Request(url)

	if not 'source' in data:
		data['source'] = 'typeWorldApp'

	data = urllib.parse.urlencode(data)
	data = data.encode('ascii')
	
	if JSON:
		api.loadJSON(JSON)

	try:
		response = urllib.request.urlopen(request, data, context=sslcontext)

		if response.getcode() != 200:
			d['errors'].append('Resource returned with HTTP code %s' % response.code)

		incomingMIMEType = response.headers['content-type'].split(';')[0]
		if not incomingMIMEType in acceptableMimeTypes:
			d['errors'].append('Resource headers returned wrong MIME type: "%s". Expected is %s.' % (response.headers['content-type'], acceptableMimeTypes))

		if response.getcode() == 200:
			api.loadJSON(response.read().decode())

	except urllib.request.HTTPError as e:
		d['errors'].append(str(e))

	information, warnings, errors = api.validate()

	if information:
		d['information'].extend(information)
	if warnings:
		d['warnings'].extend(warnings)
	if errors:
		d['errors'].extend(errors)

	return api, d



class TypeWorldProtocol(TypeWorldProtocolBase):


	def initialize(self):
		self.versions = []
		self._rootCommand = None
		self._installableFontsCommand = None

	def loadFromDB(self):
		'''Overwrite this'''

		if self.get('installableFontsCommand'):
			api = InstallableFontsResponse()
			api.parent = self
			api.loadJSON(self.get('installableFontsCommand'))
			self._installableFontsCommand = api

	def latestVersion(self):
		return self._installableFontsCommand

	def returnRootCommand(self, testScenario):

		if not self._rootCommand:

			# Read response
			data = {
				'appVersion': typeWorld.api.VERSION,
			}
			if testScenario:
				data['testScenario'] = testScenario
			api, responses = readJSONResponse(self.url, typeWorld.api.RootResponse(), typeWorld.api.base.INSTALLABLEFONTSCOMMAND['acceptableMimeTypes'], data = data)
			
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

		print('Updating...')

		data = {
			'subscriptionID': self.subscriptionID, 
			'command': 'installableFonts', 
			'anonymousAppID': self.parent.parent.parent.anonymousAppID(), 
			'anonymousTypeWorldUserID': self.parent.parent.parent.user(),
			'appVersion': typeWorld.api.VERSION,
		}
		if self.parent.parent.parent.testScenario:
			data['testScenario'] = self.parent.parent.parent.testScenario
		secretKey = self.getSecretKey()
		if secretKey:
			data['secretKey'] = secretKey

		print ('data: %s' % data)

		api, responses = readJSONResponse(self.connectURL(), typeWorld.api.InstallableFontsResponse(), INSTALLABLEFONTSCOMMAND['acceptableMimeTypes'], data = data)

		if responses['errors']:
			
			if self.url in self.parent.parent._updatingSubscriptions:
				self.parent.parent._updatingSubscriptions.remove(self.url)
			self.parent._updatingProblem = '\n'.join(responses['errors'])
			return False, self.parent._updatingProblem, False

		if api.type == 'error':
			if self.url in self.parent.parent._updatingSubscriptions:
				self.parent.parent._updatingSubscriptions.remove(self.url)
			self.parent._updatingProblem = api.errorMessage
			return False, self.parent._updatingProblem, False

		if api.type in ('temporarilyUnavailable', 'insufficientPermission'):
			if self.url in self.parent.parent._updatingSubscriptions:
				self.parent.parent._updatingSubscriptions.remove(self.url)
			self.parent._updatingProblem = '#(response.%s)' % api.type
			return False, self.parent._updatingProblem, False


		# Detect installed fonts now not available in subscription anymore and delete them
		if api.type == typeWorld.api.NOFONTSAVAILABLE:
			for foundry in self._installableFontsCommand.foundries:
				for family in foundry.families:
					for font in family.fonts:
						self.removeFont(font.uniqueID)


		identical = self._installableFontsCommand.sameContent(api)
		self._installableFontsCommand = api
		return True, None, not identical


	def removeFont(self, fontID):

		success, installableFontsCommand = self.installableFontsCommand()

		# Get font
		for foundry in installableFontsCommand.foundries:
			for family in foundry.families:
				for font in family.fonts:
					if font.uniqueID == fontID:

						# TODO: remove this for final version
						if (hasattr(font, 'requiresUserID') and font.requiresUserID) or (hasattr(font, 'protected') and font.protected):
						
							data = {
								'command': 'uninstallFont',
								'fontID': urllib.parse.quote_plus(fontID),
								'anonymousAppID': self.parent.parent.parent.anonymousAppID(),
								'anonymousTypeWorldUserID': self.parent.parent.parent.user(),
								'subscriptionID': self.subscriptionID,
								'secretKey': self.getSecretKey(),
								'secretTypeWorldAPIKey': self.parent.parent.parent.secretTypeWorldAPIKey,
								'appVersion': typeWorld.api.VERSION,
							}
							if self.parent.parent.parent.testScenario:
								data['testScenario'] = self.parent.parent.parent.testScenario

							api, messages = readJSONResponse(self.connectURL(), typeWorld.api.UninstallFontResponse(), UNINSTALLFONTCOMMAND['acceptableMimeTypes'], data = data)

							proceed = ['unknownInstallation'] # 

							if messages['errors']:
								return False, '\n\n'.join(messages['errors'])

							# Predefined response messages
							elif api.type != 'error' and api.type != 'success':
								
								if not api.type in proceed:
									return False, '#(response.%s)' % api.type

							return True, None

						else:
							return True, None

		return True, None



	def installFont(self, fontID, version):

		success, installableFontsCommand = self.installableFontsCommand()

		# Get font
		for foundry in installableFontsCommand.foundries:
			for family in foundry.families:
				for font in family.fonts:
					if font.uniqueID == fontID:
						
						# Build URL

						data = {
							'command': 'installFont',
							'fontID': urllib.parse.quote_plus(fontID),
							'fontVersion': str(version),
							'anonymousAppID': self.parent.parent.parent.anonymousAppID(),
							'anonymousTypeWorldUserID': self.parent.parent.parent.user(),
							'subscriptionID': self.subscriptionID,
							'secretKey': self.getSecretKey(),
							'secretTypeWorldAPIKey': self.parent.parent.parent.secretTypeWorldAPIKey,
							'appVersion': typeWorld.api.VERSION,
						}
						if self.parent.parent.parent.testScenario:
							data['testScenario'] = self.parent.parent.parent.testScenario

						if self.parent.get('revealIdentity') and self.parent.parent.parent.userName():
							data['userName'] = self.parent.parent.parent.userName()
						if self.parent.get('revealIdentity') and self.parent.parent.parent.userEmail():
							data['userEmail'] = self.parent.parent.parent.userEmail()

						# print('curl -d "%s" -X POST %s' % ('&'.join(['{0}={1}'.format(k, v) for k,v in data.items()]), url))

						api, messages = readJSONResponse(self.connectURL(), typeWorld.api.InstallFontResponse(), INSTALLFONTCOMMAND['acceptableMimeTypes'], data = data)

						if messages['errors']:
							return False, '\n\n'.join(messages['errors'])

						if api.type == 'error':
							return False, api.errorMessage

						# Predefined response messages
						elif api.type != 'error' and api.type != 'success':
							return False, ['#(response.%s)' % api.type, '#(response.%s.headline)' % api.type]

						elif api.type == 'success':
							return True, api


	def aboutToAddSubscription(self, anonymousAppID, anonymousTypeWorldUserID, secretTypeWorldAPIKey, testScenario):
		'''Overwrite this.
		Put here an initial health check of the subscription. Check if URLs point to the right place etc.
		Return False, 'message' in case of errors.'''

		# Read response
		data = {
			'subscriptionID': self.subscriptionID, 
			'secretKey': self.secretKey, 
			'anonymousAppID': anonymousAppID, 
			'anonymousTypeWorldUserID': anonymousTypeWorldUserID, 
			'secretTypeWorldAPIKey': secretTypeWorldAPIKey,
			'command': 'installableFonts',
			'appVersion': typeWorld.api.VERSION,
		}
		if testScenario:
			data['testScenario'] = testScenario

		api, responses = readJSONResponse(self.url, typeWorld.api.InstallableFontsResponse(), typeWorld.api.base.INSTALLABLEFONTSCOMMAND['acceptableMimeTypes'], data = data)
		
		# Errors
		if responses['errors']:
			return False, responses['errors'][0]

		# Check for installableFonts response support
		success, rootCommand = self.rootCommand(testScenario = testScenario)

		if not 'installableFonts' in rootCommand.supportedCommands or not 'installFont' in rootCommand.supportedCommands:
			return False, 'API endpoint %s does not support the "installableFonts" or "installFont" commands.' % rootCommand.canonicalURL

		if api.type == 'error':
			return False, api.errorMessage

		# Predefined response messages
		if api.type != 'error' and api.type != 'success':
			return False, '#(response.%s)' % api.type

		self._installableFontsCommand = api

		# Success
		if self.secretKey:
			self.setSecretKey(self.secretKey)
		return True, None

	def save(self):
		self.set('installableFontsCommand', self._installableFontsCommand.dumpJSON())

