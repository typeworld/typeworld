from typeWorld.client.protocols import *



class TypeWorldProtocol(TypeWorldProtocolBase):


	def initialize(self):
		self.versions = []

	def loadFromDB(self):
		'''Overwrite this'''

		if self.get('versions'):
			for dictData in self.get('versions'):
				api = APIRoot()
				api.parent = self
				api.loadJSON(dictData)
				self.versions.append(api)

	def latestVersion(self):
		if self.versions:
			return self.versions[-1]

	def installableFontsCommand(self):
		return self.latestVersion().response.getCommand()

	def protocolName(self):
		return 'Type.World JSON Protocol'

	def rootCommand(self):
		return self.latestVersion()

	def update(self):

		data = {
			'subscriptionID': self.subscriptionID, 
			'command': 'installableFonts', 
			'anonymousAppID': self.parent.parent.parent.anonymousAppID(), 
			'anonymousTypeWorldUserID': self.parent.parent.parent.user()}
		secretKey = self.getSecretKey()
		if secretKey:
			data['secretKey'] = secretKey

		api, responses = readJSONResponse(self.connectURL(), INSTALLABLEFONTSCOMMAND['acceptableMimeTypes'], data = data)
		if responses['errors']:
			
			self.parent.parent._updatingSubscriptions.remove(self.url)
			self.parent._updatingProblem = '\n'.join(responses['errors'])
			return False, self.parent._updatingProblem

		if api.response.getCommand().type == 'error':
			self.parent.parent._updatingSubscriptions.remove(self.url)
			self.parent._updatingProblem = api.response.getCommand().errorMessage
			return False, self.parent._updatingProblem

		if api.response.getCommand().type in ('temporarilyUnavailable', 'insufficientPermission'):
			self.parent.parent._updatingSubscriptions.remove(self.url)
			self.parent._updatingProblem = '#(response.%s)' % api.response.getCommand().type
			return False, self.parent._updatingProblem

		# Replace latest version
		# TODO: Implement different checking, save additional version
		self.versions[-1] = api
		return True, None


	def removeFont(self, fontID):

		# Get font
		for foundry in self.parent.foundries():
			for family in foundry.families():
				for font in family.fonts():
					if font.uniqueID == fontID:

						# TODO: remove this for final version
						if (hasattr(font, 'requiresUserID') and font.requiresUserID) or (hasattr(font, 'protected') and font.protected):
						
							try:

								data = {
									'command': 'uninstallFont',
									'fontID': urllib.parse.quote_plus(fontID),
									'anonymousAppID': self.parent.parent.parent.anonymousAppID(),
									'anonymousTypeWorldUserID': self.parent.parent.parent.user(),
									'subscriptionID': self.subscriptionID,
									'secretKey': self.getSecretKey(),
									'secretTypeWorldAPIKey': self.parent.parent.parent.secretTypeWorldAPIKey,
								}

								api, messages = readJSONResponse(self.connectURL(), UNINSTALLFONTCOMMAND['acceptableMimeTypes'], data = data)

								proceed = ['unknownInstallation'] # 

								if messages['errors']:
									return False, '\n\n'.join(messages['errors'])

								# Predefined response messages
								elif api.response.getCommand().type != 'error' and api.response.getCommand().type != 'success':
									
									if not api.response.getCommand().type in proceed:
										return False, '#(response.%s)' % api.response.getCommand().type

								return True, font.path(font.installedVersion(), folder)

							except:
								exc_type, exc_value, exc_traceback = sys.exc_info()
								return False, traceback.format_exc()

						else:
							return True, None

		return True, None



	def installFont(self, fontID, version):

		# Get font
		for foundry in self.parent.foundries():
			for family in foundry.families():
				for font in family.fonts():
					if font.uniqueID == fontID:
						
						# Build URL
						try:

							data = {
								'command': 'installFont',
								'fontID': urllib.parse.quote_plus(fontID),
								'fontVersion': str(version),
								'anonymousAppID': self.parent.parent.parent.anonymousAppID(),
								'anonymousTypeWorldUserID': self.parent.parent.parent.user(),
								'subscriptionID': self.subscriptionID,
								'secretKey': self.getSecretKey(),
								'secretTypeWorldAPIKey': self.parent.parent.parent.secretTypeWorldAPIKey,
							}

							if self.parent.get('revealIdentity') and self.parent.parent.parent.userName():
								data['userName'] = self.parent.parent.parent.userName()
							if self.parent.get('revealIdentity') and self.parent.parent.parent.userEmail():
								data['userEmail'] = self.parent.parent.parent.userEmail()

							# print('curl -d "%s" -X POST %s' % ('&'.join(['{0}={1}'.format(k, v) for k,v in data.items()]), url))

							api, messages = readJSONResponse(self.connectURL(), INSTALLFONTCOMMAND['acceptableMimeTypes'], data = data)

							if messages['errors']:
								return False, '\n\n'.join(messages['errors'])

							if api.response.getCommand().type == 'error':
								return False, api.response.getCommand().errorMessage

							# Predefined response messages
							elif api.response.getCommand().type != 'error' and api.response.getCommand().type != 'success':
								return False, ['#(response.%s)' % api.response.getCommand().type, '#(response.%s.headline)' % api.response.getCommand().type]

							elif api.response.getCommand().type == 'success':
								return True, api.response.getCommand()


						except:
							exc_type, exc_value, exc_traceback = sys.exc_info()
							return False, traceback.format_exc()


	def aboutToAddSubscription(self, anonymousAppID, anonymousTypeWorldUserID, secretTypeWorldAPIKey):
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
		}
		api, responses = readJSONResponse(self.url, typeWorld.api.base.INSTALLABLEFONTSCOMMAND['acceptableMimeTypes'], data = data)
		
		# Errors
		if responses['errors']:
			return False, responses['errors'][0]

		# Check for installableFonts response support
		if not 'installableFonts' in api.supportedCommands and not 'installFonts' in api.supportedCommands:
			return False, 'API endpoint %s does not support the "installableFonts" and "installFonts" commands.' % api.canonicalURL

		if not api.response:
			return False, 'API response has only root, no response attribute attached. Expected: installableFonts response.'

		if api.response.getCommand().type == 'error':
			return False, api.response.getCommand().errorMessage

		# Predefined response messages
		if api.response.getCommand().type != 'error' and api.response.getCommand().type != 'success':
			return False, '#(response.%s)' % api.response.getCommand().type

		self.versions.append(api)
#		self.save()

		# Success
		return True, None

	def save(self):
		self.set('versions', [x.dumpJSON() for x in self.versions])

