from typeworld.client import URL


class TypeWorldProtocolBase(object):
    def __init__(self, url):
        self.url = URL(url)

        # References to objects this is attached to
        self.client = None
        self.subscription = None

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

    # def aboutToAddSubscription(self, anonymousAppID, anonymousTypeWorldUserID,
    # secretTypeWorldAPIKey):
    # 	'''Overwrite this.
    # 	Put here an initial health check of the subscription. Check if URLs point to
    # the right place etc.
    # 	Because this also gets used by the central Type.World server, pass on the
    # secretTypeWorldAPIKey attribute to your web service as well.
    # 	Return False, 'message' in case of errors.'''
    # 	return True, None

    def subscriptionAdded(self):
        """Overwrite this"""
        pass

    # def update(self):
    # 	'''Overwrite this'''
    # 	return True, False, changes

    # def installFonts(self, fontID, version):
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

    def rootCommand(self, testScenario=None):
        success, command = self.returnRootCommand(testScenario=testScenario)
        if success:
            command.parent = self
        return success, command

    def installableFontsCommand(self):
        success, command = self.returnInstallableFontsCommand()
        if success:
            command.parent = self
        return success, command

    def get(self, key):
        data = self.subscription.get("data") or {}
        if key in data:
            return data[key]

    def set(self, key, value):
        data = self.subscription.get("data") or {}
        data[key] = value
        self.subscription.set("data", data)

    def keychainKey(self):
        return "%s, App:%s" % (self.unsecretURL(), self.client.anonymousAppID())

    def getSecretKey(self):
        if self.client:
            keyring = self.client.keyring()
            return keyring.get_password(self.keychainKey(), self.url.subscriptionID)

    def setSecretKey(self, secretKey):
        keyring = self.client.keyring()
        keyring.set_password(self.keychainKey(), self.url.subscriptionID, secretKey)

    def deleteSecretKey(self):
        keyring = self.client.keyring()
        keyring.delete_password(self.keychainKey(), self.url.subscriptionID)

    def connectURL(self):
        return self.url.transportProtocol + self.url.restDomain

    def unsecretURL(self):
        return self.url.unsecretURL()

    def secretURL(self):

        url = self.url.secretURL()
        if ":secretKey@" in url:
            url = url.replace(":secretKey@", ":" + self.getSecretKey() + "@")
        return url
