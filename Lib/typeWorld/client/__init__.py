# -*- coding: utf-8 -*-


import os, sys, json, platform, urllib2, re

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
			return self.defaults[key]

	def set(self, key, value):
		self.defaults[key] = value

	def save(self):
		pass


class APIRepository(object):
	u"""\
	Represents a font repository under a specific API endpoint.

	The values stored in self.repositoryVersions are the typeWorld.api.APIRoot() objects.
	"""

	def __init__(self, url):
		self.url = url
		self.repositoryVersions = []

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


class APIEndPoint(object):
	u"""\
	Represents an API endpoint, identified and grouped by the canonical URL attribute of the API responses. This API endpoint class can then hold several repositories.
	"""

	def __init__(self, canonicalURL):
		self.canonicalURL = canonicalURL
		self.repositories = {}

	def addRepository(self, url, api):

		# Add if new
		if not self.repositories.has_key(url):
			newRepo = APIRepository(url)
			newRepo.parent = self
			self.repositories[url] = newRepo

		# Update fonts
		self.repositories[url].updateWithAPIObject(api)


class APIClient(object):
	u"""\
	Main Type.World client app object. Use it to load repositories and install/uninstall fonts.
	"""

	def __init__(self, preferences = None):

		self.endpoints = {}
		self.preferences = preferences


	def readResponse(self, url):
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

			if response.headers.type != 'application/json':
				d['errors'].append('Resource headers returned wrong MIME type: "%s". Expected is "application/json".' % response.headers.type)

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
		api, responses = self.readResponse(url)

		# Errors
		if responses['errors']:
			raise ValueError('\n'.join(responses['errors']))

		# Check for installableFonts response support
		if not 'installableFonts' in api.supportedCommands and not 'installFonts' in api.supportedCommands:
			raise ValueError('API endpoint %s does not support the "installableFonts" and "installFonts" commands.' % api.canonicalURL)

		# Tweak url to include "installableFonts" command
		url = self.addCommandToURL(url, 'installableFonts')

		# Read response again, this time with installableFonts command
		api, responses = self.readResponse(url)

		# Add endpoint if new
		if not self.endpoints.has_key(api.canonicalURL):
			newEndpoint = APIEndPoint(api.canonicalURL)
			newEndpoint.parent = self
			self.endpoints[api.canonicalURL] = newEndpoint

		# Add repository to endpoint
		self.endpoints[api.canonicalURL].addRepository(url, api)



if __name__ == '__main__':

	client = APIClient(preferences = AppKitNSUserDefaults('world.type.clientapp'))

	client.addRepository('http://192.168.56.102/type.world/api/wsqmRxRmY3C8vtrutfIr/?user=0Dm07Y9vQpGQHh1kwUY7')

	for key in client.endpoints.keys():
		endpoint = client.endpoints[key]
		print endpoint

		for key2 in endpoint.repositories.keys():
			repo = endpoint.repositories[key2]
			print repo
			repo.update()

#			print repo.latestVersion()
	
