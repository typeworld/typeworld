# -*- coding: utf-8 -*-

import datetime
import os, sys, json, platform, urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, re, traceback, json, time, base64, certifi, socket, subprocess
from time import gmtime, strftime


import typeWorld.api, typeWorld.api.base
from typeWorld.api import *
from typeWorld.api.base import *

from typeWorld.client.helpers import *


import platform
WIN = platform.system() == 'Windows'
MAC = platform.system() == 'Darwin'

if MAC:
	import objc
	from AppKit import NSDictionary


class DummyKeyring(object):
	def __init__(self):
		self.passwords = {}

	def set_password(self, key, username, password):
		self.passwords[key] = [username, password]

	def get_password(self, key, username):
		if key in self.passwords and self.passwords[key][0] == username:
			return self.passwords[key][1]

	def delete_password(self, key, username):
		if key in self.passwords and self.passwords[key][0] == username:
			del self.passwords[key]

if 'TRAVIS' in os.environ:
	dummyKeyRing = DummyKeyring()


def readJSONResponse(url, acceptableMimeTypes, data = {}, JSON = None):
	d = {}
	d['errors'] = []
	d['warnings'] = []
	d['information'] = []

	# Take URL apart here
	customProtocol, protocol, transportProtocol, subscriptionID, secretKey, restDomain = splitJSONURL(url)
	url = transportProtocol + restDomain

	# Validate
	api = typeWorld.api.APIRoot()

	try:
		request = urllib.request.Request(url)

		if not 'source' in data:
			data['source'] = 'typeWorldApp'

		data = urllib.parse.urlencode(data)
		data = data.encode('ascii')
		
		if JSON:
			api.loadJSON(JSON)

		try:

			response = urllib.request.urlopen(request, data, cafile=certifi.where())

			if response.getcode() != 200:
				d['errors'].append('Resource returned with HTTP code %s' % response.code)

			incomingMIMEType = response.headers['content-type'].split(';')[0]
			if not incomingMIMEType in acceptableMimeTypes:
				d['errors'].append('Resource headers returned wrong MIME type: "%s". Expected is %s.' % (response.headers['content-type'], acceptableMimeTypes))

			if response.getcode() == 200:

				api.loadJSON(response.read().decode())


		except urllib.request.HTTPError as e:
			d['errors'].append('API endpoint returned with following error: %s' % str(e))

		except:
			d['errors'].append(traceback.format_exc())


		information, warnings, errors = api.validate()

		if information:
			d['information'].extend(information)
		if warnings:
			d['warnings'].extend(warnings)
		if errors:
			d['errors'].extend(errors)

	except:
		d['errors'].append(traceback.format_exc())

	return api, d



def validURL(url):

	protocol = url.split('://')[0]

	if not protocol:
		return False

	if not protocol in typeWorld.api.base.PROTOCOLS:
		return False


def splitJSONURL(url):

	customProtocol = 'typeworld://'
	url = url.replace(customProtocol, '')

	protocol = url.split('+')[0]
	url = url.replace(protocol + '+', '')

	url = url.replace('http//', 'http://')
	url = url.replace('https//', 'https://')
	url = url.replace('HTTP//', 'http://')
	url = url.replace('HTTPS//', 'https://')


	transportProtocol = None
	if url.lower().startswith('https://'):
		transportProtocol = 'https://'
	elif url.lower().startswith('http://'):
		transportProtocol = 'http://'

	urlRest = url[len(transportProtocol):]

	subscriptionID = ''
	secretKey = ''
	if '@' in urlRest:

		credentials, domain = urlRest.split('@')

		# Both subscriptionID as well as secretKey defined
		if ':' in credentials:
			subscriptionID, secretKey = credentials.split(':')
			keyURL = transportProtocol + subscriptionID + ':' + 'secretKey' + '@' + domain
		else:
			subscriptionID = credentials
			secretKey = None
			keyURL = transportProtocol + subscriptionID + '@' + domain

		actualURL = transportProtocol + domain

	# No credentials given
	else:
		keyURL = url
		actualURL = url
		domain = urlRest

	return customProtocol, protocol, transportProtocol, subscriptionID, secretKey, domain


class Preferences(object):
	def __init__(self):
		self._dict = {}

	def get(self, key):
		if key in self._dict:
			return self._dict[key]

	def set(self, key, value):
		self._dict[key] = value
		self.save()

	def remove(self, key):
		if key in self._dict:
			del self._dict[key]

	def save(self):
		pass

	def dictionary(self):
		return self._dict

class JSON(Preferences):
	def __init__(self, path):
		self.path = path
		self._dict = {}

		if self.path and os.path.exists(self.path):
			self._dict = json.loads(ReadFromFile(self.path))

	def save(self):

		if not os.path.exists(os.path.dirname(self.path)):
			os.makedirs(os.path.dirname(self.path))
		WriteToFile(self.path, json.dumps(self._dict))



class AppKitNSUserDefaults(Preferences):
	def __init__(self, name = None):
		NSUserDefaults = objc.lookUpClass('NSUserDefaults')
		if name:
			self.defaults = NSUserDefaults.alloc().initWithSuiteName_(name)
		else:
			self.defaults = NSUserDefaults.standardUserDefaults()

		self.values = {}


	def get(self, key):
		
		if key in self.values:
			return self.values[key]

		else:

			o = self.defaults.objectForKey_(key)

			if o:


				# print('TYPE of', key, ':', o.__class__.__name__)

				if 'Array' in o.__class__.__name__:
					o = list(o)

				elif 'Dictionary' in o.__class__.__name__:
					o = dict(o)
					# print('Converting TYPE of', key, ' to dict()')
					# o['_xzy'] = 'a'
					# del o['_xzy']

				elif 'unicode' in o.__class__.__name__:
					o = str(o)


				self.values[key] = o
				return self.values[key]

	def set(self, key, value):

#		self.defaults.setObject_forKey_(json.dumps(value), key)
		
		# if MAC:
		# 	print(type(value))
		# 	if type(value) == dict:
		# 		value = NSDictionary.alloc().initWithDictionary_(value)

		self.values[key] = value
		self.defaults.setObject_forKey_(value, key)

	def remove(self, key):
		if key in self.values:
			del self.values[key]

		self.defaults.removeObjectForKey_(key)

	def save(self):
		pass

	def dictionary(self):
		return dict(self.defaults.dictionaryRepresentation())



class APIClient(object):
	"""\
	Main Type.World client app object. Use it to load repositories and install/uninstall fonts.
	"""

	def __init__(self, preferences = Preferences(), secretTypeWorldAPIKey = None):
		self.preferences = preferences
		self._publishers = {}
		self._subscriptionsUpdated = []
		self.onlineCommandsQueue = []
		self._syncProblems = []
		self.secretTypeWorldAPIKey = secretTypeWorldAPIKey


		self._systemLocale = None

	def completeSubscriptionURLs(self):

		_list = []

		for publisher in self.publishers():
			for subscription in publisher.subscriptions():
				_list.append(subscription.protocol.completeURL())

		return _list

	def timezone(self):
		return strftime("%z", gmtime())

	def user(self):
		return self.preferences.get('typeWorldUserAccount')

	def syncProblems(self):
		return self._syncProblems

	def addMachineIDToParameters(self, parameters):

		machineModelIdentifier, machineHumanReadableName, machineSpecsDescription = MachineName()

		if machineModelIdentifier:
			parameters['machineModelIdentifier'] = machineModelIdentifier

		if machineHumanReadableName:
			parameters['machineHumanReadableName'] = machineHumanReadableName

		if machineSpecsDescription:
			parameters['machineSpecsDescription'] = machineSpecsDescription

		import platform
		parameters['machineNodeName'] = platform.node()

		osName = OSName()
		if osName:
			parameters['machineOSVersion'] = osName


		return parameters


	def online(self, server = None):

		if 'TRAVIS' in os.environ:
			return True

		if not server:
			server = 'type.world'
#		print('Pinging %s' % server)
		if MAC:
			return os.system('ping %s -c 1 -t 3' % server) == 0
		if WIN:
			CREATE_NO_WINDOW = 0x08000000
			return subprocess.call('ping -n 1 -w 3000 %s' % server, creationflags=CREATE_NO_WINDOW) == 0


	def appendCommands(self, commandName, commandsList = ['pending']):

		# Set up data structure
		commands = self.preferences.get('pendingOnlineCommands')
		if not self.preferences.get('pendingOnlineCommands'):
			commands = {}
		# Init empty
		if not commandName in commands: 
			commands[commandName] = []
		if commandName in commands and len(commands[commandName]) == 0: # set anyway if empty because NSObject immutability
			commands[commandName] = []
		self.preferences.set('pendingOnlineCommands', commands)

		# Add commands to list
		commands = self.preferences.get('pendingOnlineCommands')
		if type(commandsList) == str:
			commandsList = [commandsList]
		for commandListItem in commandsList:
			if not commandListItem in commands[commandName]:
				commands[commandName].append(commandListItem)
		self.preferences.set('pendingOnlineCommands', commands)


	def performCommands(self):

		success, message = True, None
		self._syncProblems = []

		if self.online():

			commands = self.preferences.get('pendingOnlineCommands') or {}

			if 'unlinkUser' in commands and commands['unlinkUser']:
				success, message = self.performUnlinkUser()

				if success:
					commands['unlinkUser'] = []
					self.preferences.set('pendingOnlineCommands', commands)
					self.log('unlinkUser finished successfully')

				else:
					self.log('syncSubscriptions failure:', message)
					self._syncProblems.append(message)


			if 'linkUser' in commands and commands['linkUser']:
				success, message = self.performLinkUser(commands['linkUser'][0])

				if success:
					commands['linkUser'] = []
					self.preferences.set('pendingOnlineCommands', commands)
					self.log('syncSubscriptions finished successfully')

				else:
					self.log('syncSubscriptions failure:', message)
					self._syncProblems.append(message)


			if 'syncSubscriptions' in commands and commands['syncSubscriptions']:
				success, message = self.performSyncSubscriptions(commands['syncSubscriptions'])

				if success:
					commands['syncSubscriptions'] = []
					self.preferences.set('pendingOnlineCommands', commands)
					self.log('syncSubscriptions finished successfully')

				else:
					self.log('syncSubscriptions failure:', message)
					self._syncProblems.append(message)


			if 'uploadSubscriptions' in commands and commands['uploadSubscriptions']:
				success, message = self.perfomUploadSubscriptions(commands['uploadSubscriptions'])

				if success:
					commands['uploadSubscriptions'] = []
					self.preferences.set('pendingOnlineCommands', commands)
					self.log('uploadSubscriptions finished successfully')

				else:
					self.log('uploadSubscriptions failure:', message)
					self._syncProblems.append(message)

			if 'acceptInvitation' in commands and commands['acceptInvitation']:
				success, message = self.performAcceptInvitation(commands['acceptInvitation'])

				if success:
					commands['acceptInvitation'] = []
					self.preferences.set('pendingOnlineCommands', commands)
					self.log('acceptInvitation finished successfully')

				else:
					self.log('acceptInvitation failure:', message)
					self._syncProblems.append(message)

			if 'declineInvitation' in commands and commands['declineInvitation']:
				success, message = self.performDeclineInvitation(commands['declineInvitation'])

				if success:
					commands['declineInvitation'] = []
					self.preferences.set('pendingOnlineCommands', commands)
					self.log('declineInvitation finished successfully')

				else:
					self.log('declineInvitation failure:', message)
					self._syncProblems.append(message)

			if 'downloadSubscriptions' in commands and commands['downloadSubscriptions']:
				success, message = self.performDownloadSubscriptions()

				if success:
					commands['downloadSubscriptions'] = []
					self.preferences.set('pendingOnlineCommands', commands)
					self.log('downloadSubscriptions finished successfully')

				else:
					self.log('downloadSubscriptions failure:', message)
					self._syncProblems.append(message)

			return success, message

		else:

			self._syncProblems.append('#(response.notOnline)')
			return False, '#(response.notOnline)'


	def uploadSubscriptions(self, performCommands = True):

		self.appendCommands('uploadSubscriptions', self.completeSubscriptionURLs() or ['empty'])
		self.appendCommands('downloadSubscriptions')

		if performCommands:
			return self.performCommands()

	def perfomUploadSubscriptions(self, oldURLs):

		userID = self.user()

		if userID:

			self.preferences.set('lastServerSync', int(time.time()))

			self.log('Uploading subscriptions: %s' % oldURLs)

			parameters = {
				'command': 'uploadUserSubscriptions',
				'anonymousAppID': self.anonymousAppID(),
				'anonymousUserID': userID,
				'subscriptionURLs': ','.join(oldURLs or ['empty']),
				'appVersion': typeWorld.api.VERSION,
			}
			# Add user’s secret key
			keyring = self.keyring()
			if keyring:
				parameters['secretKey'] = keyring.get_password('https://type.world', userID)

			data = urllib.parse.urlencode(parameters).encode('ascii')
			url = 'https://type.world/jsonAPI/'

			try:
				response = urllib.request.urlopen(url, data, cafile=certifi.where())
			except urllib.error.HTTPError as e:
				self.log('API endpoint alive HTTP error: %s' % e)
				return False, 'API endpoint alive HTTP error: %s' % e

			response = json.loads(response.read().decode())


			if response['errors']:
				return False, '\n'.join(response['errors'])

		# Success
		return True, None

	def downloadSubscriptions(self, performCommands = True):

		self.appendCommands('downloadSubscriptions')

		if performCommands:
			return self.performCommands()


	def performDownloadSubscriptions(self):

		userID = self.user()

		if userID:

			self.preferences.set('lastServerSync', int(time.time()))

			parameters = {
				'command': 'downloadUserSubscriptions',
				'anonymousAppID': self.anonymousAppID(),
				'anonymousUserID': userID,
				'userTimezone': self.timezone(),
				'appVersion': typeWorld.api.VERSION,
			}
			# Add user’s secret key
			keyring = self.keyring()
			if keyring:
				parameters['secretKey'] = keyring.get_password('https://type.world', userID)

			data = urllib.parse.urlencode(parameters).encode('ascii')
			url = 'https://type.world/jsonAPI/'

			try:
				response = urllib.request.urlopen(url, data, cafile=certifi.where())
			except urllib.error.HTTPError as e:
				self.log('API endpoint alive HTTP error: %s' % e)
				return False, 'API endpoint alive HTTP error: %s' % e

			response = json.loads(response.read().decode())

			print(response)

			if response['errors']:
				return False, '\n'.join(response['errors'])

			self.log('Downloading subscriptions: %s' % response['subscriptions'])

			return self.executeDownloadSubscriptions(response)

		return True, None


	def preloadLogos(self):

		for invitation in self.preferences.get('acceptedInvitations'):
			if 'logoURL' in invitation:
				success, logo, mimeType = self.resourceByURL(invitation['logoURL'], binary = True)
		for invitation in self.preferences.get('pendingInvitations'):
			if 'logoURL' in invitation:
				success, logo, mimeType = self.resourceByURL(invitation['logoURL'], binary = True)

	def executeDownloadSubscriptions(self, response):

		oldURLs = self.completeSubscriptionURLs()

#		print('executeDownloadSubscriptions():', response)


		if 'appIsRevoked' in response['information']:
			self.uninstallAllProtectedFonts()

		# Subscriptions
		for url in response['subscriptions']:
			if not url in oldURLs:
				success, message, publisher, subscription = self.addSubscription(url, updateSubscriptionsOnServer = False)

				if not success:
					return False, message

		# Invitations
		self.preferences.set('acceptedInvitations', response['acceptedInvitations'])
		self.preferences.set('pendingInvitations', response['pendingInvitations'])
		self.preferences.set('sentInvitations', response['sentInvitations'])

		import threading
		preloadThread = threading.Thread(target=self.preloadLogos)
		preloadThread.start()

		# Add new subscriptions
		for publisher in self.publishers():
			for subscription in publisher.subscriptions():
				if not subscription.protocol.completeURL() in response['subscriptions']:
					subscription.delete(updateSubscriptionsOnServer = False)


		# Success
		return True, len(response['subscriptions']) - len(oldURLs)

	def acceptInvitation(self, ID):

		userID = self.user()
		if userID:
			self.appendCommands('acceptInvitation', [ID])

		return self.performCommands()


	def performAcceptInvitation(self, IDs):

		userID = self.user()
		oldURLs = self.completeSubscriptionURLs()

		if userID:

			self.preferences.set('lastServerSync', int(time.time()))

			parameters = {
				'command': 'acceptInvitations',
				'anonymousAppID': self.anonymousAppID(),
				'anonymousUserID': userID,
				'subscriptionIDs': ','.join([str(x) for x in IDs]),
				'appVersion': typeWorld.api.VERSION,
			}
			# Add user’s secret key
			keyring = self.keyring()
			if keyring:
				parameters['secretKey'] = keyring.get_password('https://type.world', userID)

			data = urllib.parse.urlencode(parameters).encode('ascii')
			url = 'https://type.world/jsonAPI/'

			try:
				response = urllib.request.urlopen(url, data, cafile=certifi.where())
			except urllib.error.HTTPError as e:
				self.log('API endpoint alive HTTP error: %s' % e)
				return False, 'API endpoint alive HTTP error: %s' % e

			response = json.loads(response.read().decode())

			if response['errors']:
				return False, '\n'.join(response['errors'])

			# Success
			return self.executeDownloadSubscriptions(response)

		return True, None

	def declineInvitation(self, ID):

		userID = self.user()
		if userID:
			self.appendCommands('declineInvitation', [ID])

		return self.performCommands()


	def performDeclineInvitation(self, IDs):

		userID = self.user()
		oldURLs = self.completeSubscriptionURLs()

		if userID:

			self.preferences.set('lastServerSync', int(time.time()))

			parameters = {
				'command': 'declineInvitations',
				'anonymousAppID': self.anonymousAppID(),
				'anonymousUserID': userID,
				'subscriptionIDs': ','.join([str(x) for x in IDs]),
				'appVersion': typeWorld.api.VERSION,
			}
			# Add user’s secret key
			keyring = self.keyring()
			if keyring:
				parameters['secretKey'] = keyring.get_password('https://type.world', userID)

			data = urllib.parse.urlencode(parameters).encode('ascii')
			url = 'https://type.world/jsonAPI/'

			try:
				response = urllib.request.urlopen(url, data, cafile=certifi.where())
			except urllib.error.HTTPError as e:
				self.log('API endpoint alive HTTP error: %s' % e)
				return False, 'API endpoint alive HTTP error: %s' % e

			response = json.loads(response.read().decode())

			if response['errors']:
				return False, '\n'.join(response['errors'])

			# Success
			return self.executeDownloadSubscriptions(response)

		return True, None

	def syncSubscriptions(self, performCommands = True):
		self.appendCommands('syncSubscriptions', self.completeSubscriptionURLs() or ['empty'])

		if performCommands:
			return self.performCommands()

	def performSyncSubscriptions(self, oldURLs):

		userID = self.user()

		if userID:

			self.preferences.set('lastServerSync', int(time.time()))

			parameters = {
				'command': 'syncUserSubscriptions',
				'anonymousAppID': self.anonymousAppID(),
				'anonymousUserID': userID,
				'subscriptionURLs': ','.join(oldURLs or ['empty']),
				'appVersion': typeWorld.api.VERSION,
			}
			# Add user’s secret key
			keyring = self.keyring()
			if keyring:
				parameters['secretKey'] = keyring.get_password('https://type.world', userID)

			data = urllib.parse.urlencode(parameters).encode('ascii')
			url = 'https://type.world/jsonAPI/'

			try:
				response = urllib.request.urlopen(url, data, cafile=certifi.where())
			except urllib.error.HTTPError as e:
				self.log('API endpoint alive HTTP error: %s' % e)
				return False, 'API endpoint alive HTTP error: %s' % e

			response = json.loads(response.read().decode())

			if response['errors']:
				return False, '\n'.join(response['errors'])

			# Add new subscriptions
			for url in response['subscriptions']:
				if not url in oldURLs:
					success, message, publisher, subscription = self.addSubscription(url, updateSubscriptionsOnServer = False)

					if not success:
						return False, message

			# Success
			return True, len(response['subscriptions']) - len(oldURLs)

		return True, None


	def userName(self):
		keyring = self.keyring()
		if keyring:
			return keyring.get_password('https://type.world/user/%s' % self.user(), 'userName')

	def userEmail(self):
		keyring = self.keyring()
		if keyring:
			return keyring.get_password('https://type.world/user/%s' % self.user(), 'userEmail')

	def linkUser(self, userID, secretKey):

		# Set secret key now, so it doesn't show up in preferences when offline
		keyring = self.keyring()
		if keyring:
			keyring.set_password('https://type.world', userID, secretKey)

		self.appendCommands('linkUser', userID)
		self.syncSubscriptions(performCommands = False)
		self.downloadSubscriptions(performCommands = False)

		return self.performCommands()


	def performLinkUser(self, userID):

		parameters = {
			'command': 'linkTypeWorldUserAccount',
			'anonymousAppID': self.anonymousAppID(),
			'anonymousUserID': userID,
			'appVersion': typeWorld.api.VERSION,
		}
		# Add user’s secret key
		keyring = self.keyring()
		if keyring:
			parameters['secretKey'] = keyring.get_password('https://type.world', userID)

		parameters = self.addMachineIDToParameters(parameters)
		data = urllib.parse.urlencode(parameters).encode('ascii')
		url = 'https://type.world/jsonAPI/'

		try:
			response = urllib.request.urlopen(url, data, cafile=certifi.where())
		except urllib.error.HTTPError as e:
			self.log('API endpoint alive HTTP error: %s' % e)
			return False, 'API endpoint alive HTTP error: %s' % e
		except urllib.error.URLError as e:
			self.log('API endpoint URL HTTP error: %s' % e)
			return False, 'API endpoint URL HTTP error: %s' % e

		response = json.loads(response.read().decode())


#		print(response)

		if response['errors']:
			return False, '\n'.join(response['errors'])

		# Success
		self.preferences.set('typeWorldUserAccount', userID)

		if keyring:
			if 'userEmail' in response:
				keyring.set_password('https://type.world/user/%s' % self.user(), 'userEmail', response['userEmail'])
			if 'userName' in response:
				keyring.set_password('https://type.world/user/%s' % self.user(), 'userName', response['userName'])

		return True, None


	def unlinkUser(self):

		self.appendCommands('unlinkUser')

		return self.performCommands()


	def uninstallAllProtectedFonts(self):
		# Uninstall all protected fonts
		for publisher in self.publishers():
			for subscription in publisher.subscriptions():
				for foundry in subscription.protocol.installableFontsCommand().foundries:
					for family in foundry.families:
						for font in family.fonts:
							if font.protected:
								subscription.removeFont(font.uniqueID)


	def performUnlinkUser(self):

		userID = self.user()

		self.uninstallAllProtectedFonts()

		parameters = {
			'command': 'unlinkTypeWorldUserAccount',
			'anonymousAppID': self.anonymousAppID(),
			'anonymousUserID': self.user(),
			'appVersion': typeWorld.api.VERSION,
		}

		# Add user’s secret key
		keyring = self.keyring()
		if keyring:
			parameters['secretKey'] = keyring.get_password('https://type.world', userID)

		data = urllib.parse.urlencode(parameters).encode('ascii')
		url = 'https://type.world/jsonAPI/'

		try:
			response = urllib.request.urlopen(url, data, cafile=certifi.where())
		except urllib.error.HTTPError as e:
			self.log('API endpoint alive HTTP error: %s' % e)
			return False, 'API endpoint alive HTTP error: %s' % e

		response = json.loads(response.read().decode())

		if response['errors']:
			return False, '\n'.join(response['errors'])

		# Success
		self.preferences.set('typeWorldUserAccount', '')
		self.preferences.remove('acceptedInvitations')
		self.preferences.remove('pendingInvitations')
		self.preferences.remove('sentInvitations')
		if self.preferences.get('currentPublisher') == 'pendingInvitations':
			self.preferences.set('currentPublisher', '')

		try:
			keyring = self.keyring()
			keyring.delete_password('https://type.world', userID)
			keyring.delete_password('https://type.world', 'userEmail')
			keyring.delete_password('https://type.world', 'userName')

		except:
			pass

		# Success
		return True, None



	def systemLocale(self):

		if not self._systemLocale:
			if MAC:
				# For Mojave
				if platform.mac_ver()[0].split('.') >= '10.14.0'.split('.'):
					self._systemLocale = Execute('defaults read .GlobalPreferences AppleLanguages | tr -d [:space:] | cut -c3-4').decode()
				else:
					from AppKit import NSLocale
					self._systemLocale = str(NSLocale.autoupdatingCurrentLocale().localeIdentifier().split('_')[0])
			elif WIN:
				import locale
				self._systemLocale = locale.getdefaultlocale()[0].split('_')[0]
			else:
				self._systemLocale = 'en'

		return self._systemLocale

	def locale(self):
		'''\
		Reads user locale from OS
		'''

		if self.preferences.get('localizationType') == 'systemLocale':
			_locale = [self.systemLocale(), 'en']
		elif self.preferences.get('localizationType') == 'customLocale':
			_locale = [self.preferences.get('customLocaleChoice'), 'en']
		else:
			_locale = [self.systemLocale(), 'en']
		return _locale


	def amountOutdatedFonts(self):
		amount = 0
		for publisher in self.publishers():
			amount += publisher.amountOutdatedFonts()
		return amount


	def keyring(self):

		return dummyKeyRing
		if 'TRAVIS' in os.environ:
			return DummyKeyring()

		try:
			import keyring
		except:
			return None

		if MAC:
			from keyring.backends.OS_X import Keyring
			keyring.core.set_keyring(keyring.core.load_keyring('keyring.backends.OS_X.Keyring'))
		if WIN:
			from keyring.backends.Windows import WinVaultKeyring
			keyring.core.set_keyring(keyring.core.load_keyring('keyring.backends.Windows.WinVaultKeyring'))

		return keyring


	def log(self, *argv):
		if MAC:
			from AppKit import NSLog
			NSLog('Type.World Client: %s' % ' '.join(map(str, argv)))

	def prepareUpdate(self):

		self._subscriptionsUpdated = []

	def allSubscriptionsUpdated(self):

		numSubscriptions = 0
		for publisher in self.publishers():
			numSubscriptions += len(publisher.subscriptions())

		if len(self._subscriptionsUpdated) == numSubscriptions:
			return True



	def resourceByURL(self, url, binary = False, update = False, username = None, password = None):
		'''Caches and returns content of a HTTP resource. If binary is set to True, content will be stored and return as a bas64-encoded string'''

		resources = self.preferences.get('resources') or {}

		if url not in resources or update:

			# print('resourceByURL', url)

			request = urllib.request.Request(url)
			if username and password:
				base64string = base64.b64encode(b"%s:%s" % (username, password)).decode("ascii")
				request.add_header("Authorization", "Basic %s" % base64string)   
				# print('with username and password %s:%s' % (username, password))
			response = urllib.request.urlopen(request, cafile=certifi.where())


			if response.getcode() != 200:
				return False, 'Resource returned with HTTP code %s' % response.code

			else:
				content = response.read()
				if binary:
					content = base64.b64encode(content).decode()
				else:
					content = content.decode()

				resources[url] = response.headers['content-type'] + ',' + content
				self.preferences.set('resources', resources)

				return True, content, response.headers['content-type']

		else:

			response = resources[url]
			mimeType = response.split(',')[0]
			content = response[len(mimeType)+1:]

			return True, content, mimeType




	def readGitHubResponse(self, url, username = None, password = None):

		d = {}
		d['errors'] = []
		d['warnings'] = []
		d['information'] = []

		json = ''

		try:

			# print('readGitHubResponse(%s)' % url)

			request = urllib.request.Request(url)
			if username and password:
				base64string = base64.b64encode(b"%s:%s" % (username, password)).decode("ascii")
				request.add_header("Authorization", "Basic %s" % base64string)   
			response = urllib.request.urlopen(request, cafile=certifi.where())

			if response.getcode() == 404:
				d['errors'].append('Server returned with error 404 (Not found).')
				return None, d

			if response.getcode() == 401:
				d['errors'].append('User authentication failed. Please review your username and password.')
				return None, d

			if response.getcode() != 200:
				d['errors'].append('Resource returned with HTTP code %s' % response.code)

			# if not response.headers['content-type'] in acceptableMimeTypes:
			# 	d['errors'].append('Resource headers returned wrong MIME type: "%s". Expected is %s.' % (response.headers['content-type'], acceptableMimeTypes))
			# 	self.log('Received this response with an unexpected MIME type for the URL %s:\n\n%s' % (url, response.read()))

			if response.getcode() == 200:

				json = response.read()

		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for line in traceback.format_exception_only(exc_type, exc_value):
				d['errors'].append(line)
			self.log(traceback.format_exc())

		return json, d


	def addAttributeToURL(self, url, key, value):
		if not key + '=' in url:
			if '?' in url:
				url += '&' + key + '=' + value
			else:
				url += '?' + key + '=' + value
		else:
			url = re.sub(key + '=(\w*)', key + '=' + value, url)

		return url

	def anonymousAppID(self):
		anonymousAppID = self.preferences.get('anonymousAppID')

		if anonymousAppID == None or anonymousAppID == {}:
			import uuid
			anonymousAppID = str(uuid.uuid1())
			self.preferences.set('anonymousAppID', anonymousAppID)


		return anonymousAppID


	def protocol(self, url):

		customProtocol, protocol, transportProtocol, subscriptionID, secretKey, restDomain = splitJSONURL(url)
		if os.path.exists(os.path.join(os.path.dirname(__file__), 'protocols', protocol + '.py')):

			import importlib
			spec = importlib.util.spec_from_file_location('json', os.path.join(os.path.dirname(__file__), 'protocols', protocol + '.py'))
			module = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(module)
			
			protocolObject = module.TypeWorldProtocol(None, url)

			return True, protocolObject
		else:
			return False, 'Protocol %s doesn’t exist in this app (yet).' % protocol


	def addSubscription(self, url, username = None, password = None, updateSubscriptionsOnServer = True, JSON = None, secretTypeWorldAPIKey = None):
		'''
		Because this also gets used by the central Type.World server, pass on the secretTypeWorldAPIKey attribute to your web service as well.
		'''
		try:

			# Check for correct protocol
			found = False
			for protocol in typeWorld.api.base.PROTOCOLS:
				if url.startswith(protocol + '://'):
					found = True
					break
			if not found:
				return False, 'Unknown custom protocol, known are: %s' % (typeWorld.api.base.PROTOCOLS), None, None


			# Get subscription
			success, message = self.protocol(url)
			if success:
				protocol = message
			else:
				return False, message, None, None


			# Initial Health Check
			success, response = protocol.aboutToAddSubscription(anonymousAppID = self.anonymousAppID(), anonymousTypeWorldUserID = self.user(), secretTypeWorldAPIKey = secretTypeWorldAPIKey or self.secretTypeWorldAPIKey)
			if not success:
				return False, response, None, None


			publisher = self.publisher(protocol.rootCommand().canonicalURL)
			subscription = publisher.subscription(protocol.saveURL(), protocol)

			# Check for URL validity
			success, response = protocol.urlIsValid()
			if not success:
				return False, response, None, None


			# Canonical URL
			canonicalURL = protocol.rootCommand().canonicalURL
			if not canonicalURL:
				return False, 'Protocol object doesn’t return a canonicalURL value.', None, None



			publisher.set('type', protocol.protocol)
			publisher.set('currentSubscription', subscription.url)
			subscription.save()
			publisher.save()
			publisher.stillAlive()


			if updateSubscriptionsOnServer:
				success, message = self.uploadSubscriptions()
				if not success:
					return False, message, None, None

			protocol.subscriptionAdded()

			return True, None, self.publisher(protocol.rootCommand().canonicalURL), subscription


			# Outdated (for now)
			# elif url.startswith('typeworldgithub://'):


			# 	url = url.replace('typeworldgithub://', '')
			# 	# remove trailing slash
			# 	while url.endswith('/'):
			# 		url = url[:-1]
				
			# 	if not url.startswith('https://'):
			# 		return False, 'GitHub-URL needs to start with https://', None, None

			# 	canonicalURL = '/'.join(url.split('/')[:4])
			# 	owner = url.split('/')[3]
			# 	repo = url.split('/')[4]
			# 	path = '/'.join(url.split('/')[7:])


			# 	commitsURL = 'https://api.github.com/repos/%s/%s/commits?path=%s' % (owner, repo, path)


			# 	publisher = self.publisher(canonicalURL)
			# 	publisher.set('type', 'GitHub')

			# 	if username and password:
			# 		publisher.set('username', username)
			# 		publisher.setPassword(username, password)

			# 	allowed, message = publisher.gitHubRateLimit()
			# 	if not allowed:
			# 		return False, message, None, None

			# 	# Read response
			# 	commits, responses = publisher.readGitHubResponse(commitsURL)

			# 	# Errors
			# 	if responses['errors']:
			# 		return False, '\n'.join(responses['errors']), None, None

			# 	success, message = publisher.addGitHubSubscription(url, commits), None
			# 	publisher.save()

			# 	return success, message, self.publisher(canonicalURL), None


		except:

			exc_type, exc_value, exc_traceback = sys.exc_info()
			return False, traceback.format_exc(), None, None


	def currentPublisher(self):
		if self.preferences.get('currentPublisher') and self.preferences.get('currentPublisher') != 'None' and self.preferences.get('currentPublisher') != 'pendingInvitations':
			publisher = self.publisher(self.preferences.get('currentPublisher'))
			return publisher

	def publisher(self, canonicalURL):
		if canonicalURL not in self._publishers:
			e = APIPublisher(self, canonicalURL)
			self._publishers[canonicalURL] = e

		if self.preferences.get('publishers') and canonicalURL in self.preferences.get('publishers'):
			self._publishers[canonicalURL].exists = True

		return self._publishers[canonicalURL]

	def publishers(self):
		if self.preferences.get('publishers'):
			return [self.publisher(canonicalURL) for canonicalURL in self.preferences.get('publishers')]
		else:
			return []


class APIPublisher(object):
	"""\
	Represents an API endpoint, identified and grouped by the canonical URL attribute of the API responses. This API endpoint class can then hold several repositories.
	"""

	def __init__(self, parent, canonicalURL):
		self.parent = parent
		self.canonicalURL = canonicalURL
		self.exists = False
		self._subscriptions = {}

		self.stillAliveTouched = None

		self._updatingSubscriptions = []

	def folder(self):

		if WIN:
			return os.path.join(os.environ['WINDIR'], 'Fonts')

		if MAC:

			from os.path import expanduser
			home = expanduser("~")
			folder = os.path.join(home, 'Library', 'Fonts', 'Type.World App', '%s (%s)' % (self.subscriptions()[0].protocol.rootCommand().name.getText(), self.subscriptions()[0].protocol.protocolName()))

			return folder

	def stillUpdating(self):
		return len(self._updatingSubscriptions) > 0


	def updatingProblem(self):

		problems = []

		for subscription in self.subscriptions():
			problem = subscription.updatingProblem()
			if problem and not problem in problems:
				problems.append(problem)

		if problems:
			return problems


	def stillAlive(self):


		def stillAliveWorker(self):

			try:
				# Register endpoint

				data = urllib.parse.urlencode({
					'command': 'registerAPIEndpoint',
					'url': self.canonicalURL,
				}).encode('ascii')

				url = 'https://type.world/jsonAPI/'

				try:
					response = urllib.request.urlopen(url, data, cafile=certifi.where())
				except urllib.error.HTTPError as e:
					self.parent.log('API endpoint alive HTTP error: %s' % e)
					return

				response = json.loads(response.read().decode())

				if not response['errors']:
					self.parent.log('API endpoint alive success.')
				else:
					self.parent.log('API endpoint alive error: %s' % response['message'])
			except:
				self.parent.log(traceback.format_exc())

		# Touch only once
		if not self.stillAliveTouched:

			import threading
			stillAliveThread = threading.Thread(target=stillAliveWorker, args=(self, ))
			stillAliveThread.start()

			self.stillAliveTouched = time.time()			


	def gitHubRateLimit(self):

		limits, responses = self.readGitHubResponse('https://api.github.com/rate_limit')

		if responses['errors']:
			return False, '\n'.join(responses['errors'])

		limits = json.loads(limits)

		if limits['rate']['remaining'] == 0:
			return False, 'Your GitHub API rate limit has been reached. The limit resets at %s.' % (datetime.datetime.fromtimestamp(limits['rate']['reset']).strftime('%Y-%m-%d %H:%M:%S'))

		return True, None


	def readGitHubResponse(self, url):

		if self.get('username') and self.getPassword(self.get('username')):
			return self.parent.readGitHubResponse(url, self.get('username'), self.getPassword(self.get('username')))
		else:
			return self.parent.readGitHubResponse(url)

	def name(self, locale = ['en']):
		return self.subscriptions()[0].protocol.rootCommand().name.getTextAndLocale(locale = locale)

	def getPassword(self, username):
		keyring = self.parent.keyring()
		return keyring.get_password("Type.World GitHub Subscription %s (%s)" % (self.canonicalURL, username), username)

	def setPassword(self, username, password):
		keyring = self.parent.keyring()
		keyring.set_password("Type.World GitHub Subscription %s (%s)" % (self.canonicalURL, username), username, password)

	def resourceByURL(self, url, binary = False, update = False):
		'''Caches and returns content of a HTTP resource. If binary is set to True, content will be stored and return as a bas64-encoded string'''

		# Save resource
		resourcesList = self.get('resources') or []
		if not url in resourcesList:
			resourcesList.append(url)
			self.set('resources', resourcesList)

		if self.get('username') and self.getPassword(self.get('username')):
			return self.parent.resourceByURL(url, binary = binary, update = update, username = self.get('username'), password = self.getPassword(self.get('username')))
		else:
			return self.parent.resourceByURL(url, binary = binary, update = update)

	def amountInstalledFonts(self):
		return len(self.installedFonts())

	def installedFonts(self):
		l = []

		for subscription in self.subscriptions():
			for font in subscription.installedFonts():
				if not font in l:
					l.append(font)

		return l

	def amountOutdatedFonts(self):
		return len(self.outdatedFonts())

	def outdatedFonts(self):
		l = []

		for subscription in self.subscriptions():
			for font in subscription.outdatedFonts():
				if not font in l:
					l.append(font)

		return l

	def currentSubscription(self):
		if self.get('currentSubscription'):
			subscription = self.subscription(self.get('currentSubscription'))
			if subscription:
				return subscription
			else:
				return self.subscriptions()[0]

	def get(self, key):
		preferences = dict(self.parent.preferences.get(self.canonicalURL) or self.parent.preferences.get('publisher(%s)' % self.canonicalURL) or {})
		if key in preferences:

			o = preferences[key]

			if 'Array' in o.__class__.__name__:
				o = list(o)

			elif 'Dictionary' in o.__class__.__name__:
				o = dict(o)

			return o

	def set(self, key, value):

		preferences = dict(self.parent.preferences.get(self.canonicalURL) or self.parent.preferences.get('publisher(%s)' % self.canonicalURL) or {})
		preferences[key] = value
		self.parent.preferences.set('publisher(%s)' % self.canonicalURL, preferences)


	def addGitHubSubscription(self, url, commits):

		self.parent._subscriptions = {}

		subscription = self.subscription(url)
		subscription.set('commits', commits)
		self.set('currentSubscription', url)
		subscription.save()

		return True, None


	def subscription(self, url, protocol = None):
		if url not in self._subscriptions:

			# Load from DB
			loadFromDB = False
			if not protocol:
				success, message = self.parent.protocol(url)
				if success:
					protocol = message
					loadFromDB = True
				else:
					raise Exception(message)

			e = APISubscription(self, protocol)
			if loadFromDB:
				protocol.loadFromDB()



			self._subscriptions[url] = e

		if self.get('subscriptions') and url in self.get('subscriptions'):
			self._subscriptions[url].exists = True

		return self._subscriptions[url]

	def subscriptions(self):
		return [self.subscription(url) for url in self.get('subscriptions') or []]

	def update(self):

		if self.online():

			for subscription in self.subscriptions():
				success, message = subscription.update()
				if not success:
					return success, message

			return True, None

		else:
			return False, '#(response.notOnline)'

	def save(self):
		publishers = self.parent.preferences.get('publishers') or []
		if not self.canonicalURL in publishers:
			publishers.append(self.canonicalURL)
		self.parent.preferences.set('publishers', publishers)

	def delete(self):

		for subscription in self.subscriptions():
			subscription.delete(calledFromParent = True)

		# Path
		try:
			os.rmdir(self.path())
		except:
			pass

		# Old
		self.parent.preferences.remove(self.canonicalURL)
		# New
		self.parent.preferences.remove('publisher(%s)' % self.canonicalURL)

		# Resources
		resources = self.parent.preferences.get('resources') or {}
		for url in self.get('resources') or []:
			if url in resources:
				del resources[url]
		self.parent.preferences.set('resources', resources)


		publishers = self.parent.preferences.get('publishers')
		publishers.remove(self.canonicalURL)
		self.parent.preferences.set('publishers', publishers)
		self.parent.preferences.set('currentPublisher', '')

		self.parent._publishers = {}



class APISubscription(object):
	"""\
	Represents a subscription, identified and grouped by the canonical URL attribute of the API responses.
	"""

	def __init__(self, parent, protocol):
		self.parent = parent
		self.exists = False
		self.secretKey = None
		self.protocol = protocol
		self.protocol.parent = self
		self.url = self.protocol.saveURL()

		self._updatingProblem = None

		# print('<API SUbscription %s>' % self.url)

	def invitationAccepted(self):

		if self.parent.parent.user():
			if self.parent.parent.preferences.get('acceptedInvitations'):
				for invitation in self.parent.parent.preferences.get('acceptedInvitations'):
					if self.url == invitation['url']:
						return True

		return False


	def stillUpdating(self):
		return self.url in self.parent._updatingSubscriptions


	def name(self, locale = ['en']):
		return self.protocol.installableFontsCommand().name.getText(locale) or '#(Unnamed)'

	def resourceByURL(self, url, binary = False, update = False):
		'''Caches and returns content of a HTTP resource. If binary is set to True, content will be stored and return as a bas64-encoded string'''

		# Save resource
		resourcesList = self.get('resources') or []
		if not url in resourcesList:
			resourcesList.append(url)
			self.set('resources', resourcesList)

		if self.parent.get('username') and self.parent.getPassword(self.get('username')):
			return self.parent.parent.resourceByURL(url, binary, self.parent.get('username'), self.parent.getPassword(self.get('username')))
		else:
			return self.parent.parent.resourceByURL(url, binary)


	def familyByID(self, ID):
		for foundry in self.protocol.installableFontsCommand().foundries:
			for family in foundry.families:
				if family.uniqueID == ID:
					return family

	def fontByID(self, ID):
		for foundry in self.protocol.installableFontsCommand().foundries:
			for family in foundry.families:
				for font in family.fonts:
					if font.uniqueID == ID:
						return family

	def amountInstalledFonts(self):
		return len(self.installedFonts())

	def installedFonts(self):
		l = []
		# Get font
		for foundry in self.protocol.installableFontsCommand().foundries:
			for family in foundry.families:
				for font in family.fonts:
					if self.installedFontVersion(font.uniqueID):
						if not font in l:
							l.append(font.uniqueID)
		return l

	def amountOutdatedFonts(self):
		return len(self.outdatedFonts())

	def outdatedFonts(self):
		l = []
		# Get font
		for foundry in self.protocol.installableFontsCommand().foundries:
			for family in foundry.families:
				for font in family.fonts:
					installedFontVersion = self.installedFontVersion(font.uniqueID)
					if installedFontVersion and installedFontVersion != font.getVersions()[-1].number:
						if not font in l:
							l.append(font.uniqueID)
		return l

	def installedFontVersion(self, fontID = None):

		folder = self.parent.folder()
		for foundry in self.protocol.installableFontsCommand().foundries:
			for family in foundry.families:
				for font in family.fonts:
					if font.uniqueID == fontID:

						for version in font.getVersions():
							path = os.path.join(folder, font.filename(version.number))
							if os.path.exists(path):
								return version.number

	def fontIsOutdated(self, fontID):
		for foundry in self.protocol.installableFontsCommand().foundries:
			for family in foundry.families:
				for font in family.fonts:
					if font.uniqueID == fontID:

						installedVersion = self.installedFontVersion(fontID)
						return installedVersion and installedVersion != font.getVersions()[-1].number


	def removeFont(self, fontID, folder = None):

		folder = self.parent.folder()
		path = None
		for foundry in self.protocol.installableFontsCommand().foundries:
			for family in foundry.families:
				for font in family.fonts:
					if font.uniqueID == fontID:
						if self.installedFontVersion(font.uniqueID):
							path = os.path.join(folder, font.filename(self.installedFontVersion(font.uniqueID)))
		if not path:
			return False, 'Font path couldn’t be determined'

		success, payload = self.protocol.removeFont(fontID)

		if success:


			if os.path.exists(path):

				try:
					os.remove(path)
					return True, None

				except PermissionError:
					return False, "Insufficient permission to delete font."

			else:

				return False, 'Font doesn’t exist.'



		else:
			return False, payload



	def installFont(self, fontID, version, folder = None):

		# Terms of Service
		if self.get('acceptedTermsOfService') != True:
			return False, ['#(response.termsOfServiceNotAccepted)', '#(response.termsOfServiceNotAccepted.headline)']


		folder = self.parent.folder()
		path = None
		for foundry in self.protocol.installableFontsCommand().foundries:
			for family in foundry.families:
				for font in family.fonts:
					if font.uniqueID == fontID:
						path = os.path.join(folder, font.filename(version))
		if not path:
			return False, 'Font path couldn’t be determined'


		success, payload = self.protocol.installFont(fontID, version)		

		if success:

			command = payload


			if MAC or WIN:

				try:
					# Create folder if it doesn't exist
					if not os.path.exists(os.path.dirname(path)):
						os.makedirs(os.path.dirname(path))

					# Put future encoding switches here
					f = open(path, 'wb')
					f.write(base64.b64decode(command.font))
					f.close()
				except PermissionError:
					return False, "Insufficient permission to install font."


				# Ping
				self.parent.stillAlive()

				if os.path.exists(path):
					return True, None
				else:
					return False, 'Font file could not be written: %s' % path

		else:
			return False, payload



		# elif self.parent.get('type') == 'GitHub':

		# 	allowed, message = self.parent.gitHubRateLimit()
		# 	if allowed:

		# 		# Get font
		# 		for foundry in self.foundries():
		# 			for family in foundry.families():
		# 				for font in family.fonts():
		# 					if font.uniqueID == fontID:

		# 						for commit in json.loads(self.get('commits')):
		# 							if commit['commit']['message'].startswith('Version: %s' % version):
		# 								# print('Install version %s, commit %s' % (version, commit['sha']))

		# 								owner = self.url.split('/')[3]
		# 								repo = self.url.split('/')[4]
		# 								urlpath = '/'.join(self.url.split('/')[7:]) + '/fonts/' + font.postScriptName + '.' + font.format


		# 								url = 'https://api.github.com/repos/%s/%s/contents/%s?ref=%s' % (owner, repo, urlpath, commit['sha'])
		# 								# print(url)
		# 								response, responses = self.parent.readGitHubResponse(url)
		# 								response = json.loads(response)


		# 								# Write file
		# 								path = font.path(version, folder)

		# 								# Create folder if it doesn't exist
		# 								if not os.path.exists(os.path.dirname(path)):
		# 									os.makedirs(os.path.dirname(path))

		# 								f = open(path, 'wb')
		# 								f.write(base64.b64decode(response['content']))
		# 								f.close()

		# 								return True, None
		# 	else:
		# 		return False, message



		# return False, 'No font was found to install.'


	def update(self):

		self.parent._updatingSubscriptions.append(self.url)


		if self.parent.parent.online(self.protocol.restDomain.split('/')[0]):


			success, message = self.protocol.update()

			# elif self.parent.get('type') == 'GitHub':

			# 	owner = self.url.split('/')[3]
			# 	repo = self.url.split('/')[4]
			# 	path = '/'.join(self.url.split('/')[7:])

			# 	commitsURL = 'https://api.github.com/repos/%s/%s/commits?path=%s/fonts' % (owner, repo, path)
			# 	# print('commitsURL', commitsURL)

			# 	# Read response
			# 	commits, responses = self.parent.readGitHubResponse(commitsURL)
			# 	self.set('commits', commits)


			self.parent._updatingSubscriptions.remove(self.url)
			self._updatingProblem = None
			self.parent.parent._subscriptionsUpdated.append(self.url)

			self.save()
			return True, None

		else:
			self.parent._updatingSubscriptions.remove(self.url)
			self.parent.parent._subscriptionsUpdated.append(self.url)
			self._updatingProblem = '#(response.serverNotReachable)'
#			print('Error updating %s' % self)
			return False, self._updatingProblem

	def updatingProblem(self):
		return self._updatingProblem

	def get(self, key):
		preferences = dict(self.parent.parent.preferences.get('subscription(%s)' % self.url) or {})
		if key in preferences:

			o = preferences[key]

			if 'Array' in o.__class__.__name__:
				o = list(o)

			elif 'Dictionary' in o.__class__.__name__:
				o = dict(o)

			return o

	def set(self, key, value):

		preferences = dict(self.parent.parent.preferences.get('subscription(%s)' % self.url) or {})
		preferences[key] = value
		self.parent.parent.preferences.set('subscription(%s)' % self.url, preferences)

	def save(self):
		subscriptions = self.parent.get('subscriptions') or []
		if not self.url in subscriptions:
			subscriptions.append(self.url)
		self.parent.set('subscriptions', subscriptions)

		self.protocol.save()


	def delete(self, calledFromParent = False, updateSubscriptionsOnServer = True):

		self.parent.parent.log('Deleting %s, updateSubscriptionsOnServer: %s' % (self, updateSubscriptionsOnServer))

		# Delete all fonts
		for foundry in self.protocol.installableFontsCommand().foundries:
			for family in foundry.families:
				for font in family.fonts:
					self.removeFont(font.uniqueID)

		# Key
		try:
			self.protocol.deleteSecretKey()
		except:
			pass

		# Resources
		resources = self.parent.parent.preferences.get('resources') or {}
		for url in self.get('resources') or []:
			if url in resources:
				# print('Deleting resource', url)
				resources.pop(url)
		self.parent.parent.preferences.set('resources', resources)


		# New
		self.parent.parent.preferences.remove('subscription(%s)' % self.url)

		# Subscriptions
		subscriptions = self.parent.get('subscriptions')
		subscriptions.remove(self.url)
		self.parent.set('subscriptions', subscriptions)
		self.parent._subscriptions = {}

		# currentSubscription
		if self.parent.get('currentSubscription') == self.url:
			if len(subscriptions) >= 1:
				self.parent.set('currentSubscription', subscriptions[0])


		if len(subscriptions) == 0 and calledFromParent == False:
			self.parent.delete()

		self.parent._subscriptions = {}

		if updateSubscriptionsOnServer:
			self.parent.parent.uploadSubscriptions()
