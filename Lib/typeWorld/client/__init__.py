# -*- coding: utf-8 -*-


import os, sys, json, platform, urllib2, re, traceback, json, time

import typeWorld.api, typeWorld.base
from typeWorld.api import *
from typeWorld.base import *





class Preferences(object):
	pass

class JSON(Preferences):
	def __init__(self, path):
		self.path = path

	def get(self, key):
		pass

	def set(self, key, value):
		pass

	def save(self):
		pass

class AppKitNSUserDefaults(Preferences):
	def __init__(self, name):
		from AppKit import NSUserDefaults
		self.defaults = NSUserDefaults.alloc().initWithSuiteName_(name)

	def get(self, key):
		if self.defaults.has_key(key):
			try:
				return json.loads(self.defaults.objectForKey_(key))
			except:
				return {}

	def set(self, key, value):
		self.defaults.setObject_forKey_(json.dumps(value), key)

	def save(self):
		pass


class APIRepository(object):
	u"""\
	Represents a font repository under a specific API endpoint.

	The values stored in self.repositoryVersions are the typeWorld.api.APIRoot() objects.
	"""

	def __init__(self, url, _dict = None):
		self.url = url
		self.repositoryVersions = []
		self.timeAdded = time.time()

		# Load from preferences
		if _dict:
			_dict = dict(_dict)
			for v in _dict['repositoryVersions']:
				api = typeWorld.api.APIRoot()
				api.loadDict(v)
				api.parent = self
				self.repositoryVersions.append(api)

			if _dict.has_key('timeAdded'):
				self.timeAdded = _dict['timeAdded']

	def latestVersion(self):
		if self.repositoryVersions:
			v = self.repositoryVersions[-1]
			v.parent = self
			return v

	def updateWithAPIObject(self, api):
		
		# List is empty, just append
		if not self.repositoryVersions:
			self.repositoryVersions.append(api)


		# otherwise only append if new API object differs from last one
		else:
			# For now, replace latest version
			# TODO: Add new version only if fonts are deleted
			# if not api.sameContent(self.repositoryVersions[-1]):
			# 	self.repositoryVersions.append(api)
			# 	print 'New data appended'
			# else:
			# 	print 'No new data available'
			self.repositoryVersions[-1] = api

	def dict(self):
		_dict = {}
		_dict['timeAdded'] = self.timeAdded
		_dict['repositoryVersions'] = []
		for repositoryVersion in self.repositoryVersions:
			_dict['repositoryVersions'].append(repositoryVersion.dumpDict())
		return _dict

	def removeFont(self, fontID, folder = None):

		api = self.latestVersion()

		# User fonts folder
		if not folder:
			from os.path import expanduser
			home = expanduser("~")
			folder = os.path.join(home, 'Library', 'Fonts', 'Type.World App', api.name.getText('en'))

		# Create folder if it doesn't exist
		if not os.path.exists(folder):
			os.makedirs(folder)

		# Get font
		for foundry in api.response.getCommand().foundries:
			for family in foundry.families:
				for font in family.fonts:
					if font.uniqueID == fontID:
						
						# Build URL
						url = self.url
						url = self.parent.parent.addAttributeToURL(url, 'command', 'uninstallFont')
						url = self.parent.parent.addAttributeToURL(url, 'fontID', fontID)
						url = self.parent.parent.addAttributeToURL(url, 'anonymousAppID', self.parent.parent.anonymousAppID())
#						url = self.parent.parent.addAttributeToURL(url, 'fontVersion', version)

						print 'Uninstalling %s in %s' % (fontID, folder)
						print url

						acceptableMimeTypes = UNINSTALLFONTCOMMAND['acceptableMimeTypes']

						try:
							response = urllib2.urlopen(url)

							if response.getcode() != 200:
								return False, 'Resource returned with HTTP code %s' % response.code

							if not response.headers.type in acceptableMimeTypes:
								return False, 'Resource headers returned wrong MIME type: "%s". Expected is %s.' % (response.headers.type, acceptableMimeTypes)


							api = APIRoot()
							_json = response.read()
							api.loadJSON(_json)

							# print _json

							if api.response.getCommand().type == 'error':
								return False, api.response.getCommand().errorMessage
							elif api.response.getCommand().type == 'seatAllowanceReached':
								return False, 'seatAllowanceReached'
							

							# REMOVE
							installedFontVersion = self.installedFontVersion(font.uniqueID)

							if installedFontVersion:
								# Delete file
								filename = '%s_%s.%s' % (font.uniqueID, installedFontVersion, font.type)

								if os.path.exists(os.path.join(folder, filename)):
									os.remove(os.path.join(folder, filename))

							return True, None


						except:
							exc_type, exc_value, exc_traceback = sys.exc_info()
							return False, traceback.format_exc()
		return True, ''


	def installFont(self, fontID, version, folder = None):

		api = self.latestVersion()

		# User fonts folder
		if not folder:
			from os.path import expanduser
			home = expanduser("~")
			folder = os.path.join(home, 'Library', 'Fonts', 'Type.World App', api.name.getText('en'))

		# Create folder if it doesn't exist
		if not os.path.exists(folder):
			os.makedirs(folder)

		# Get font
		for foundry in api.response.getCommand().foundries:
			for family in foundry.families:
				for font in family.fonts:
					if font.uniqueID == fontID:
						
						# Build URL
						url = self.url
						url = self.parent.parent.addAttributeToURL(url, 'command', 'installFont')
						url = self.parent.parent.addAttributeToURL(url, 'fontID', fontID)
						url = self.parent.parent.addAttributeToURL(url, 'anonymousAppID', self.parent.parent.anonymousAppID())
						url = self.parent.parent.addAttributeToURL(url, 'fontVersion', version)

						print 'Installing %s in %s' % (fontID, folder)
						print url

						acceptableMimeTypes = INSTALLFONTCOMMAND['acceptableMimeTypes']

						try:
							response = urllib2.urlopen(url)

							if response.getcode() != 200:
								return False, 'Resource returned with HTTP code %s' % response.code

							if not response.headers.type in acceptableMimeTypes:
								return False, 'Resource headers returned wrong MIME type: "%s". Expected is %s.' % (response.headers.type, acceptableMimeTypes)

							# Expect an error message
							if response.headers.type == 'application/json':

								api = APIRoot()
								_json = response.read()
								api.loadJSON(_json)

								# print _json

								if api.response.getCommand().type == 'error':
									return False, api.response.getCommand().errorMessage
								elif api.response.getCommand().type == 'seatAllowanceReached':
									return False, 'seatAllowanceReached'
								

							else:

								if not font.type in MIMETYPES[response.headers.type]['fileExtensions']:
									return False, "Returned MIME type (%s) does not match file type (%s)." % (response.headers.type, font.type)

								# Write file
								filename = '%s_%s.%s' % (font.uniqueID, version, font.type)

								print 'filename', filename

								binary = response.read()
								f = open(os.path.join(folder, filename), 'wb')
								f.write(binary)
								f.close()

								return True, None

						except:
							exc_type, exc_value, exc_traceback = sys.exc_info()
							return False, traceback.format_exc()


		return False, 'No font was found to install.'

	def installedFontVersion(self, fontID = None, font = None, folder = None):

		api = self.latestVersion()

		# User fonts folder
		if not folder:
			from os.path import expanduser
			home = expanduser("~")
			folder = os.path.join(home, 'Library', 'Fonts', 'Type.World App', api.name.getText('en'))

		# Create folder if it doesn't exist
		if not os.path.exists(folder):
			os.makedirs(folder)

		# font given
		if font:
			for version in font.getSortedVersions():
				filename = filename = '%s_%s.%s' % (font.uniqueID, version.number, font.type)
				if os.path.exists(os.path.join(folder, filename)):
					return version.number

		# fontID given
		else:
			for foundry in api.response.getCommand().foundries:
				for family in foundry.families:
					for font in family.fonts:
						if font.uniqueID == fontID:

							for version in font.getSortedVersions():
								filename = filename = '%s_%s.%s' % (font.uniqueID, version.number, font.type)
								if os.path.exists(os.path.join(folder, filename)):
									return version.number

	def amountInstalledFonts(self):
		amount = 0
		# Get font
		for foundry in self.latestVersion().response.getCommand().foundries:
			for family in foundry.families:
				for font in family.fonts:
					if self.installedFontVersion(font = font):
						amount += 1
		return amount


class APIEndPoint(object):
	u"""\
	Represents an API endpoint, identified and grouped by the canonical URL attribute of the API responses. This API endpoint class can then hold several repositories.
	"""

	def __init__(self, canonicalURL, _dict = None):
		self.canonicalURL = canonicalURL
		self.repositories = {}
		self.activeRepository = None

		# Load from preferences
		if _dict:
			_dict = dict(_dict)
			for key in _dict['repositories'].keys():
				repo = APIRepository(key, _dict = _dict['repositories'][key])
				repo.parent = self
				self.repositories[key] = repo

			if _dict.has_key('activeRepository'):
				self.activeRepository = _dict['activeRepository']

		if not self.activeRepository and self.repositories:
			self.activeRepository = self.repositories[self.repositories.keys()[0]].url


	def update(self):
		u"""\
		Check repository for updated data.
		"""

		activeRepository = self.activeRepository

		for url, repo in self.repositories.items():
			success, message, repo = self.parent.addRepository(repo.url)
			self.activeRepository = activeRepository
			if success == False:
				return success, message, repo
		return success, message, repo

	def addRepository(self, url, api):

		# Add if new
		if not self.repositories.has_key(url):
			newRepo = APIRepository(url)
			newRepo.parent = self
			self.repositories[url] = newRepo

		# Update fonts
		self.repositories[url].updateWithAPIObject(api)

		self.activeRepository = url

	def active(self):
		if self.activeRepository:
			return self.repositories[self.activeRepository]

	def latestVersion(self):
		if self.repositories:
			repo = self.repositories[self.repositories.keys()[0]]
			if repo.latestVersion():
				return repo.latestVersion()

	def remove(self):
		del self.parent.endpoints[self.canonicalURL]
		self.parent.savePreferences()

	def dict(self):
		_dict = {}
		_dict['activeRepository'] = self.activeRepository
		_dict['repositories'] = {}
		for key in self.repositories:
			_dict['repositories'][key] = self.repositories[key].dict()
		return _dict

	def amountInstalledFonts(self):
		amount = 0
		# Get font

		for url, repo in self.repositories.items():
			amount += repo.amountInstalledFonts()

		return amount



class APIClient(object):
	u"""\
	Main Type.World client app object. Use it to load repositories and install/uninstall fonts.
	"""

	def __init__(self, preferences = None):

		self.endpoints = {}
		self.preferences = preferences

		self.loadPreferences()

	def log(self, message):

		from AppKit import NSLog
		NSLog('Type.World Client: %s' % message)


	def savePreferences(self):
		if self.preferences:
			_dict = self.dict()
			self.preferences.set('preferences', _dict)

	def loadPreferences(self):
		if self.preferences:
			_dict = self.preferences.get('preferences')
			# import json
			# print(json.dumps(_dict, indent=4, sort_keys=True))
			
			# Load from preferences
			if _dict:
				_dict = dict(_dict)
				for key in _dict['endpoints'].keys():
					
					apiEndPoint = APIEndPoint(key, _dict = _dict['endpoints'][key])
					apiEndPoint.parent = self
					self.endpoints[key] = apiEndPoint


	def dict(self):

		_dict = {'endpoints': {}}

		for key in self.endpoints.keys():
			_dict['endpoints'][key] = self.endpoints[key].dict()

		return _dict

	def readResponse(self, url, acceptableMimeTypes):
		d = {}
		d['errors'] = []
		d['warnings'] = []
		d['information'] = []

		# Validate
		api = typeWorld.api.APIRoot()

		try:
			response = urllib2.urlopen(url)

			if response.getcode() != 200:
				d['errors'].append('Resource returned with HTTP code %s' % response.code)

			if not response.headers.type in acceptableMimeTypes:
				d['errors'].append('Resource headers returned wrong MIME type: "%s". Expected is %s.' % (response.headers.type, acceptableMimeTypes))
				self.log('Received this response with an unexpected MIME type for the URL %s:\n\n%s' % (url, response.read()))

			if response.getcode() == 200:

				api.loadJSON(response.read())

				information, warnings, errors = api.validate()

				if information:
					d['information'].extend(information)
				if warnings:
					d['warnings'].extend(warnings)
				if errors:
					d['errors'].extend(errors)

		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for line in traceback.format_exception_only(exc_type, exc_value):
				d['errors'].append(line)

		return api, d

	def addAttributeToURL(self, url, key, value):
		if not key in url:
			if '?' in url:
				url += '&' + key + '=' + value
			else:
				url += '?' + key + '=' + value
		else:
			url = re.sub(key + '=(\w*)', key + '=' + value, url)

		return url

	def anonymousAppID(self):
		if self.preferences:
			anonymousAppID = self.preferences.get('anonymousAppID')

			if anonymousAppID == None or anonymousAppID == {}:
				import uuid
				anonymousAppID = str(uuid.uuid1())
				self.preferences.set('anonymousAppID', anonymousAppID)

		else:
			anonymousAppID = 'undefined'


		return anonymousAppID

	def addRepository(self, url):

		# Read response
		api, responses = self.readResponse(url, INSTALLABLEFONTSCOMMAND['acceptableMimeTypes'])

		# Errors
		if responses['errors']:
			return False, '\n'.join(responses['errors']), None

		# Check for installableFonts response support
		if not 'installableFonts' in api.supportedCommands and not 'installFonts' in api.supportedCommands:
			return False, 'API endpoint %s does not support the "installableFonts" and "installFonts" commands.' % api.canonicalURL, None

		# Tweak url to include "installableFonts" command
		url = self.addAttributeToURL(url, 'command', 'installableFonts')

		# Read response again, this time with installableFonts command
		api, responses = self.readResponse(url, INSTALLABLEFONTSCOMMAND['acceptableMimeTypes'])

		# Add endpoint if new
		if not self.endpoints.has_key(api.canonicalURL):
			newEndpoint = APIEndPoint(api.canonicalURL)
			newEndpoint.parent = self
			self.endpoints[api.canonicalURL] = newEndpoint

		# Add repository to endpoint
		self.endpoints[api.canonicalURL].addRepository(url, api)

		# Save
		self.savePreferences()

		return True, None, self.endpoints[api.canonicalURL]


if __name__ == '__main__':

	client = APIClient(preferences = AppKitNSUserDefaults('world.type.clientapp'))

	print 'anonymousAppID', client.anonymousAppID()

	for key, endpoint in client.endpoints.items():


		for key2 in endpoint.repositories.keys():
			repo = endpoint.repositories[key2]
			print repo.latestVersion().response.getCommand().description.getText()
	# 		repo.update()

