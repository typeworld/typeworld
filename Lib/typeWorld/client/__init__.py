# -*- coding: utf-8 -*-


import os, sys, json, platform, urllib2, re, traceback

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
			return self.defaults.objectForKey_(key)

	def set(self, key, value):
		self.defaults.setObject_forKey_(value, key)

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

		# Load from preferences
		if _dict:
			_dict = dict(_dict)
			for v in _dict['repositoryVersions']:
				api = typeWorld.api.APIRoot()
				api.loadDict(v)
				self.repositoryVersions.append(api)

	def latestVersion(self):
		if self.repositoryVersions:
			return self.repositoryVersions[-1]

	def updateWithAPIObject(self, api):
		
		# List is empty, just append
		if not self.repositoryVersions:
			self.repositoryVersions.append(api)


		# otherwise only append if new API object differs from last one
		else:
			if not api.sameContent(self.repositoryVersions[-1]):
				self.repositoryVersions.append(api)
				print 'New data appended'
			else:
				print 'No new data available'

	def update(self):
		u"""\
		Check repository for updated data.
		"""
		self.parent.parent.addRepository(self.url)

	def dict(self):
		_dict = {}
		_dict['repositoryVersions'] = []
		for repositoryVersion in self.repositoryVersions:
			_dict['repositoryVersions'].append(repositoryVersion.dumpDict())
		return _dict

class APIEndPoint(object):
	u"""\
	Represents an API endpoint, identified and grouped by the canonical URL attribute of the API responses. This API endpoint class can then hold several repositories.
	"""

	def __init__(self, canonicalURL, _dict = None):
		self.canonicalURL = canonicalURL
		self.repositories = {}

		# Load from preferences
		if _dict:
			_dict = dict(_dict)
			for key in _dict['repositories'].keys():
				self.repositories[key] = APIRepository(key, _dict['repositories'][key])

	def addRepository(self, url, api):

		# Add if new
		if not self.repositories.has_key(url):
			newRepo = APIRepository(url)
			newRepo.parent = self
			self.repositories[url] = newRepo

		# Update fonts
		self.repositories[url].updateWithAPIObject(api)


	def name(self):
		if self.repositories:
			repo = self.repositories[self.repositories.keys()[0]]
			if repo.latestVersion():
				return repo.latestVersion().name


	def dict(self):
		_dict = {}
		_dict['repositories'] = {}
		for key in self.repositories:
			_dict['repositories'][key] = self.repositories[key].dict()
		return _dict

class APIClient(object):
	u"""\
	Main Type.World client app object. Use it to load repositories and install/uninstall fonts.
	"""

	def __init__(self, preferences = None):

		self.endpoints = {}
		self.preferences = preferences

		self.loadPreferences()

	def savePreferences(self):
		if self.preferences:
			self.preferences.set('preferences', self.dict())

	def loadPreferences(self):
		if self.preferences:
			_dict = self.preferences.get('preferences')
			# import json
			# print(json.dumps(_dict, indent=4, sort_keys=True))
			
			# Load from preferences
			_dict = dict(_dict)
			for key in _dict['endpoints'].keys():
				self.endpoints[key] = APIEndPoint(key, _dict['endpoints'][key])


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

	def addCommandToURL(self, url, command):
		if not 'command' in url:
			if '?' in url:
				url += '&command=' + command
			else:
				url += '?command=' + command
		else:
			url = re.sub(r'command=(\w*)', 'command=' + command, url)

		return url

	def addRepository(self, url):

		# Read response
		api, responses = self.readResponse(url, INSTALLABLEFONTSCOMMAND['acceptableMimeTypes'])

		# Errors
		if responses['errors']:
			raise ValueError('\n'.join(responses['errors']))

		# Check for installableFonts response support
		if not 'installableFonts' in api.supportedCommands and not 'installFonts' in api.supportedCommands:
			raise ValueError('API endpoint %s does not support the "installableFonts" and "installFonts" commands.' % api.canonicalURL)

		# Tweak url to include "installableFonts" command
		url = self.addCommandToURL(url, 'installableFonts')

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


if __name__ == '__main__':

	client = APIClient(preferences = AppKitNSUserDefaults('world.type.clientapp'))

#	client.addRepository('http://192.168.56.102/type.world/api/wsqmRxRmY3C8vtrutfIr/?command=installableFonts&user=zFiZMRY3QHbq537RKL87')

	for key in client.endpoints.keys():
		endpoint = client.endpoints[key]

		for key2 in endpoint.repositories.keys():
			repo = endpoint.repositories[key2]
			print repo.latestVersion().name.getText()
	# 		repo.update()

