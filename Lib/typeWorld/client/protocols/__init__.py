
from typeWorld.client import *



class TypeWorldProtocolBase(object):
	def __init__(self, parent, url):
		self.parent = parent
		self.url = url

		self.customProtocol, self.protocol, self.transportProtocol, self.subscriptionID, self.secretKey, self.restDomain = splitJSONURL(url)

		self.initialize()

	# def initialize(self):
	# 	'''Overwrite this'''
	# 	pass

	# def loadFromDB(self):
	# 	'''Overwrite this'''
	# 	pass

	# def protocolName(self):
	# 	'''Overwrite this
	# 	Human readable name of protocol'''
	# 	return self.__class__.__name__

	# def returnRootCommand(self):
	# 	'''Overwrite this
	# 	Return the root of the API call'''
	# 	pass

	# def returnInstallableFontsCommand(self):
	# 	'''Overwrite this
	# 	Return the root of the InstallableFonts command'''
	# 	pass

	# def aboutToAddSubscription(self, anonymousAppID, anonymousTypeWorldUserID, secretTypeWorldAPIKey):
	# 	'''Overwrite this.
	# 	Put here an initial health check of the subscription. Check if URLs point to the right place etc.
	# 	Because this also gets used by the central Type.World server, pass on the secretTypeWorldAPIKey attribute to your web service as well.
	# 	Return False, 'message' in case of errors.'''
	# 	return True, None

	def subscriptionAdded(self):
		'''Overwrite this'''
		pass

	# def update(self):
	# 	'''Overwrite this'''
	# 	pass

	# def installFont(self, fontID, version):
	# 	'''Overwrite this'''
	# 	pass

	# def removeFont(self, fontID):
	# 	'''Overwrite this'''
	# 	pass

	# def returnRootCommand(self, testScenario = None):
	# 	'''Overwrite this'''
	# 	return True, None

	# def returnInstallableFontsCommand(self):
	# 	'''Overwrite this'''
	# 	return True, None

	def rootCommand(self, testScenario = None):
		success, command = self.returnRootCommand(testScenario = testScenario)
		command.parent = self
		return success, command

	def installableFontsCommand(self):
		success, command = self.returnInstallableFontsCommand()
		command.parent = self
		return success, command

	def get(self, key):
		data = self.parent.get('data') or {}
		if key in data:
			return data[key]

	def set(self, key, value):
		data = self.parent.get('data') or {}
		data[key] = value
		self.parent.set('data', data)

	def path(self):
		return self.parent.path()

	def getSecretKey(self):
		keyring = self.parent.parent.parent.keyring()
		return keyring.get_password(self.url, self.subscriptionID)

	def setSecretKey(self, secretKey):
		keyring = self.parent.parent.parent.keyring()
		keyring.set_password(self.url, self.subscriptionID, secretKey)

	def deleteSecretKey(self):
		keyring = self.parent.parent.parent.keyring()
		keyring.delete_password(self.url, self.subscriptionID)

	def saveURL(self):

		# Both subscriptionID as well as secretKey defined
		if self.subscriptionID and self.secretKey:
			url = self.customProtocol + self.protocol + '+' + self.transportProtocol + self.subscriptionID + ':' + 'secretKey' + '@' + self.restDomain
		elif self.subscriptionID and not self.secretKey:
			url = self.customProtocol + self.protocol + '+' + self.transportProtocol + self.subscriptionID + '@' + self.restDomain
		else:
			url = self.customProtocol + self.protocol + '+' + self.transportProtocol + self.restDomain 

		saveURL = url.replace('https://', 'https//').replace('http://', 'http//')

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
