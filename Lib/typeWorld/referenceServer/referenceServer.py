# -*- coding: utf-8 -*-


import os, sys, plistlib, traceback
from glob import glob

import typeWorld.api, typeWorld.base
from typeWorld.api import *
from typeWorld.base import *














class PlistBasedClass(object):
	def __init__(self, plistPath, keyword = None):
		self.plistPath = plistPath
		self.keyword = keyword

		if os.path.exists(self.plistPath):
			self.plist = plistlib.readPlist(self.plistPath)
		else:
			raise ValueError('The file %s does not exist.' % self.plistPath)

	def save(self):
		plistlib.writePlist(self.plist, self.plistPath)

	def __repr__(self):
		return '<%s "%s">' % (self.__class__.__name__, self.keyword or self.plistPath)

	def dictForAPI(self):
		dictForAPI = copy.copy(self.plist)
		return dictForAPI

	def applyValuesToTypeWorldObjects(self, o, overwriteDict = {}):

		dictForAPI = self.dictForAPI()

		for key in overwriteDict.keys():
			dictForAPI[key] = overwriteDict[key]


		for key in dictForAPI.keys():

			value = dictForAPI[key]

			if not value in ['', None]:

				# Is multi language field
				if type(value) in [dict, plistlib._InternalDict]:
					multiLanguageParameter = o.get(key)
					for locale in value.keys():
						multiLanguageParameter.set(locale, value[locale])

				else:

					if type(value) in [str, unicode] and value.startswith('#'):
						pass
					else:
						try:
							o.set(key, value)
						except:
							print key, value
							print traceback.format_exc()
							raise ValueError



class Publisher(PlistBasedClass):
	def dictForAPI(self):
		dictForAPI = copy.copy(self.plist)
		dictForAPI['canonicalURL'] = self.parent.canonicalURL
		return dictForAPI

class Designer(PlistBasedClass):
	def dictForAPI(self):
		dictForAPI = copy.copy(self.plist)
		dictForAPI['keyword'] = self.keyword
		return dictForAPI

class Foundry(PlistBasedClass):

	def familiesForAllowances(self, seatAllowances):
		families = []

		for family in self.families:
			for font in family.fonts:
				if font.uniqueID() in seatAllowances.keys():
					if not family in families:
						families.append(family)

		return families

	def licensesForAllowances(self, seatAllowances):
		licenses = []

		for family in self.families:
			for font in family.fonts:
				if font.uniqueID() in seatAllowances.keys():
					if not font.getLicense() in licenses:
						licenses.append(font.getLicense())

		return licenses

class Family(PlistBasedClass):
	pass

class License(PlistBasedClass):
	def dictForAPI(self):
		dictForAPI = copy.copy(self.plist)
		dictForAPI['keyword'] = self.keyword
		return dictForAPI

class Version(PlistBasedClass):
	def dictForAPI(self):
		dictForAPI = copy.copy(self.plist)
		dictForAPI['releaseDate'] = float(dictForAPI['releaseDate'])
		dictForAPI['number'] = float(self.keyword)
		return dictForAPI

class Font(PlistBasedClass):
	def uniqueID(self):
		return '%s-%s' % (self.parent.parent.keyword, self.keyword)

	def dictForAPI(self):
		dictForAPI = copy.copy(self.plist)
		dictForAPI['postScriptName'] = self.keyword
		dictForAPI['ID'] = self.uniqueID()
		return dictForAPI

	def getLicense(self):
		return self.parent.parent.licensesByKeyword[self.plist['licenseKeyword']]

class User(PlistBasedClass):
	pass

def subFolders(path):
	return [os.path.basename(x) for x in glob(os.path.join(path, '*'))]

class ReferenceServer(object):
	u"""\
	Main Server.
	"""

	def __init__(self, dataPath, canonicalURL):
		self.dataPath = dataPath
		self.canonicalURL = canonicalURL

		if not os.path.exists(self.dataPath):
			raise ValueError('The data path %s does not exist.' % self.dataPath)

		self.fontsByID = {}

		# Read Users
		self.users = []
		self.usersByID = {}
		for userKeyword in subFolders(os.path.join(self.dataPath, 'users')):
			user = User(os.path.join(self.dataPath, 'users', userKeyword, 'user.plist'), userKeyword)
			user.parent = self
			self.users.append(user)
			self.usersByID[user.plist['anonymousID']] = user

		# Read Publisher
		self.publisher = Publisher(os.path.join(self.dataPath, 'publisher.plist'))
		self.publisher.parent = self

		# Read Designers
		self.designers = []
		self.designersByKeyword = {}
		for keyword in subFolders(os.path.join(self.dataPath, 'designers')):
			designer = Designer(os.path.join(self.dataPath, 'designers', keyword, 'designer.plist'), keyword)
			designer.parent = self
			self.designers.append(designer)
			self.designersByKeyword[keyword] = designer

		# Read Foundries
		self.foundries = []
		for foundryKeyword in subFolders(os.path.join(self.dataPath, 'foundries')):
			foundry = Foundry(os.path.join(self.dataPath, 'foundries', foundryKeyword, 'foundry.plist'), foundryKeyword)
			foundry.parent = self
			self.foundries.append(foundry)

			# Read Licenses
			foundry.licenses = []
			foundry.licensesByKeyword = {}
			for licenseKeyword in subFolders(os.path.join(self.dataPath, 'foundries', foundryKeyword, 'licenses')):
				license = License(os.path.join(self.dataPath, 'foundries', foundryKeyword, 'licenses', licenseKeyword, 'license.plist'), licenseKeyword)
				license.parent = foundry
				foundry.licenses.append(license)
				foundry.licensesByKeyword[licenseKeyword] = license

			# Read Families
			foundry.families = []
			for familyKeyword in subFolders(os.path.join(self.dataPath, 'foundries', foundryKeyword, 'families')):
				family = Family(os.path.join(self.dataPath, 'foundries', foundryKeyword, 'families', familyKeyword, 'family.plist'), familyKeyword)
				family.parent = foundry
				foundry.families.append(family)

				# Read Family-Level Versions
				family.versions = []
				for versionKeyword in subFolders(os.path.join(self.dataPath, 'foundries', foundryKeyword, 'families', familyKeyword, 'versions')):
					version = Version(os.path.join(self.dataPath, 'foundries', foundryKeyword, 'families', familyKeyword, 'versions', versionKeyword, 'version.plist'), versionKeyword)
					version.parent = family
					family.versions.append(version)

				# Read Fonts
				family.fonts = []
				for fontKeyword in subFolders(os.path.join(self.dataPath, 'foundries', foundryKeyword, 'families', familyKeyword, 'fonts')):
					font = Font(os.path.join(self.dataPath, 'foundries', foundryKeyword, 'families', familyKeyword, 'fonts', fontKeyword, 'font.plist'), fontKeyword)
					font.parent = family
					family.fonts.append(font)
					self.fontsByID[font.uniqueID()] = font

					# Read Font-Level Versions
					font.versions = []
					for versionKeyword in subFolders(os.path.join(self.dataPath, 'foundries', foundryKeyword, 'families', familyKeyword, 'fonts', fontKeyword, 'versions')):
						version = Version(os.path.join(self.dataPath, 'foundries', foundryKeyword, 'families', familyKeyword, 'fonts', fontKeyword, 'versions', versionKeyword, 'version.plist'), versionKeyword)
						version.parent = font
						font.versions.append(version)

	def foundriesForAllowances(self, seatAllowances):
		foundries = []

		for foundry in self.foundries:
			for family in foundry.families:
				for font in family.fonts:
					if font.uniqueID() in seatAllowances.keys():
						if not foundry in foundries:
							foundries.append(foundry)

		return foundries

	def designersForAllowances(self, seatAllowances):
		designers = []

		for foundry in self.foundries:
			for family in foundry.families:
				for font in family.fonts:
					if font.uniqueID() in seatAllowances.keys():

						for designerKeyword in font.plist['designers']:
							designer = self.designersByKeyword[designerKeyword]
							if not designer in designers:
								designers.append(designer)

						for designerKeyword in font.parent.plist['designers']:
							designer = self.designersByKeyword[designerKeyword]
							if not designer in designers:
								designers.append(designer)

		return designers

	def api(self, command = None, userID = None, fontID = None, anonymousAppID = None):

		api = typeWorld.api.APIRoot()

		# Put in root publisher data
		self.publisher.applyValuesToTypeWorldObjects(api)

		# InstallableFonts Command
		if command == 'installableFonts':
			api.response = typeWorld.api.Response()
			api.response.command = command
			api.response.installableFonts = typeWorld.api.InstallableFontsResponse()

			# userID is empty
			if not userID:
				api.response.installableFonts.type = 'error'
				api.response.installableFonts.errorMessage.en = 'No userID supplied'
				api.response.installableFonts.errorMessage.de = u'Keine userID übergeben'

			# userID doesn't exist
			elif not self.usersByID.has_key(userID):
				api.response.installableFonts.type = 'error'
				api.response.installableFonts.errorMessage.en = 'This userID is unknown'
				api.response.installableFonts.errorMessage.de = 'Diese userID is unbekannt'

			# userID exists, proceed
			else:
				api.response.installableFonts.type = 'success'

				user = self.usersByID[userID]
				seatAllowances = user.plist['seatAllowances']

				for rsDesigner in self.designersForAllowances(seatAllowances):
					twDesigner = typeWorld.api.Designer()
					rsDesigner.applyValuesToTypeWorldObjects(twDesigner)
					api.response.installableFonts.designers.append(twDesigner)

				for rsFoundry in self.foundriesForAllowances(seatAllowances):
					twFoundry = typeWorld.api.Foundry()
					rsFoundry.applyValuesToTypeWorldObjects(twFoundry)
					api.response.installableFonts.foundries.append(twFoundry)

					for rsLicense in rsFoundry.licensesForAllowances(seatAllowances):
						twLicense = typeWorld.api.License()
						rsLicense.applyValuesToTypeWorldObjects(twLicense)
						twFoundry.licenses.append(twLicense)

					for rsFamily in rsFoundry.familiesForAllowances(seatAllowances):
						twFamily = typeWorld.api.Family()
						rsFamily.applyValuesToTypeWorldObjects(twFamily)
						twFoundry.families.append(twFamily)

						for rsFont in rsFamily.fonts:
							seatAllowance = 0
							if seatAllowances.has_key(rsFont.uniqueID()):
								seatAllowance = seatAllowances[rsFont.uniqueID()]

							if seatAllowance:
								twFont = typeWorld.api.Font()
								rsFont.applyValuesToTypeWorldObjects(twFont, {'seatsAllowedForUser': seatAllowance})
								twFamily.fonts.append(twFont)

						for rsVersion in rsFamily.versions:
							twVersion = typeWorld.api.Version()
							rsVersion.applyValuesToTypeWorldObjects(twVersion)
							twFamily.versions.append(twVersion)





		# Return JSON code
		return api.dumpJSON()


if __name__ == '__main__':

	server = ReferenceServer(os.path.join(os.path.dirname(__file__), 'data'), 'http://localhost:88/api/')

#	print server.usersByID

	print server.api(command = 'installableFonts', userID = '5hXmdNNvywkHe2asYLXqJR2T')
