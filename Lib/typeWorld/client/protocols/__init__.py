
from typeWorld.client import *



class TypeWorldProtocolBase(object):
	def __init__(self, parent, url):
		self.parent = parent
		self.url = url

		self.customProtocol, self.protocol, self.transportProtocol, self.subscriptionID, self.secretKey, self.restDomain = splitJSONURL(url)

		self.initialize()

	def initialize(self):
		'''Overwrite this'''
		pass

	def loadFromDB(self):
		'''Overwrite this'''
		pass

	def protocolName(self):
		'''Overwrite this
		Human readable name of protocol'''
		return self.__class__.__name__

	def returnRootCommand(self):
		'''Overwrite this
		Return the root of the API call'''
		pass

	def returnInstallableFontsCommand(self):
		'''Overwrite this
		Return the root of the InstallableFonts command'''
		pass

	def rootCommand(self):
		success, command = self.returnRootCommand()
#		command.parent = self
		return success, command

	def installableFontsCommand(self):
		success, command = self.returnInstallableFontsCommand()
#		command.parent = self
		return success, command

	def aboutToAddSubscription(self, anonymousAppID, anonymousTypeWorldUserID, secretTypeWorldAPIKey):
		'''Overwrite this.
		Put here an initial health check of the subscription. Check if URLs point to the right place etc.
		Because this also gets used by the central Type.World server, pass on the secretTypeWorldAPIKey attribute to your web service as well.
		Return False, 'message' in case of errors.'''
		return True, None

	def subscriptionAdded(self):
		'''Overwrite this'''
		pass

	def get(self, key):
		data = self.parent.get('data') or {}
		if key in data:
			return data[key]

	def set(self, key, value):
		data = self.parent.get('data') or {}
		data[key] = value
		self.parent.set('data', data)

	def update(self):
		pass

	def installFont(self, fontID, version):
		pass

	def removeFont(self, fontID):
		pass

	def path(self):
		return self.parent.path()

	def urlIsValid(self):

		if self.url.count('@') > 1:
			return False, 'URL contains more than one @ sign, so don’t know how to parse it.'

		if not '://' in self.url:
			return False, 'URL is malformed.'

		if self.url.split('://')[1].count(':') > 2:
			return False, 'URL contains more than two : signs, so don’t know how to parse it.'

		if not self.url.find('typeworld://') < self.url.find('+') < self.url.find('http') < self.url.find('//', self.url.find('http')):
			return False, 'URL is malformed.'

		if not self.transportProtocol:
			return False, 'No transport protocol defined (http:// or https://).'

		return True, None

	def getSecretKey(self):
		keyring = self.parent.parent.parent.keyring()
		if keyring:
			return keyring.get_password(self.url, self.subscriptionID)
		else:
			return self.secretKey

	def setSecretKey(self, secretKey):
		keyring = self.parent.parent.parent.keyring()
		if keyring:
			keyring.set_password(self.url, self.subscriptionID, secretKey)
		else:
			self.secretKey = secretKey

	def deleteSecretKey(self):
		keyring = self.parent.parent.parent.keyring()
		if keyring:
			keyring.delete_password(self.url, self.subscriptionID)

	def saveURL(self):

		# Both subscriptionID as well as secretKey defined
		if self.subscriptionID and self.secretKey:
			url = self.transportProtocol + self.protocol + '+' + self.subscriptionID + ':' + 'secretKey' + '@' + self.restDomain
		elif self.subscriptionID and not self.secretKey:
			url = self.transportProtocol + self.protocol + '+' + self.subscriptionID + '@' + self.restDomain
		else:
			url = self.transportProtocol + self.protocol + '+' + self.restDomain 

		saveURL = self.url.replace('https://', 'https//').replace('http://', 'http//')

		return saveURL

	def connectURL(self):
		return self.transportProtocol + self.restDomain

	def completeURL(self):

		url = self.url

		if ':secretKey@' in url:
			secretKey = self.getSecretKey()
			if secretKey:
				url = url.replace(':secretKey@', ':%s@' % secretKey)
			else:
				self.parent.parent.parent.log('WARNING: No secret key found for %s' % url)				

		return url		
