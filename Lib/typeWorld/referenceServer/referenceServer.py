# -*- coding: utf-8 -*-


import os, sys, plistlib, traceback
from glob import glob

import typeWorld.api, typeWorld.base
from typeWorld.api import *
from typeWorld.base import *

import flask











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
	def fontsForAllowances(self, seatAllowances):
		fonts = []

		for font in self.fonts:
			if font.uniqueID() in seatAllowances.keys():
				if not font in fonts:
					fonts.append(font)

		return fonts

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

	def seatsInstalledForUser(self, userID, fontID, anonymousAppID = None):
		seats = 0

		if anonymousAppID:
			compareString = '%s %s %s' % (userID, fontID, anonymousAppID)
		else:
			compareString = '%s %s' % (userID, fontID)

		for line in open(os.path.join(self.dataPath, 'seatTracking', 'seats.txt'), 'r').readlines():
			if line.startswith('%s %s' % (userID, fontID)):
				seats += 1
		return seats

	def addInstallation(self, userID, fontID, anonymousAppID):

		# This installation is already registered; do nothing
		if self.seatsInstalledForUser(userID, fontID, anonymousAppID) == 1:
			pass

		# Add this installation
		else:
			string = '%s %s %s\n' % (userID, fontID, anonymousAppID)
			f = open(os.path.join(self.dataPath, 'seatTracking', 'seats.txt'), 'a')
			f.write(string)
			f.close()

	def removeInstallation(self, userID, fontID, anonymousAppID):

		string = '%s %s %s\n' % (userID, fontID, anonymousAppID)

		lines = open(os.path.join(self.dataPath, 'seatTracking', 'seats.txt'), 'r').readlines()

		f = open(os.path.join(self.dataPath, 'seatTracking', 'seats.txt'), 'w')
		for line in lines:
			if line != string:
				f.write(string)
		f.close()


	def seatsAllowedForUser(self, userID, fontID):

		if self.usersByID[userID].plist['seatAllowances'].has_key(fontID):
			return self.usersByID[userID].plist['seatAllowances'][fontID]
		else:
			return 0


	def api(self, command = None, userID = None, fontID = None, anonymousAppID = None, fontVersion = None):

		api = typeWorld.api.APIRoot()
		mimeType = None
		content = None



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
				return flask.Response(api.dumpJSON(), mimetype = 'application/json')

			# userID doesn't exist
			elif not self.usersByID.has_key(userID):
				api.response.installableFonts.type = 'error'
				api.response.installableFonts.errorMessage.en = 'This userID is unknown'
				api.response.installableFonts.errorMessage.de = 'Diese userID is unbekannt'
				return flask.Response(api.dumpJSON(), mimetype = 'application/json')

			# userID exists, proceed
			else:
				api.response.installableFonts.type = 'success'

				# Fetch user
				user = self.usersByID[userID]
				seatAllowances = user.plist['seatAllowances']

				# Designers
				for rsDesigner in self.designersForAllowances(seatAllowances):
					twDesigner = typeWorld.api.Designer()
					rsDesigner.applyValuesToTypeWorldObjects(twDesigner)
					api.response.installableFonts.designers.append(twDesigner)

				# Foundries
				for rsFoundry in self.foundriesForAllowances(seatAllowances):
					twFoundry = typeWorld.api.Foundry()
					rsFoundry.applyValuesToTypeWorldObjects(twFoundry)
					api.response.installableFonts.foundries.append(twFoundry)

					# Licenses
					for rsLicense in rsFoundry.licensesForAllowances(seatAllowances):
						twLicense = typeWorld.api.License()
						rsLicense.applyValuesToTypeWorldObjects(twLicense)
						twFoundry.licenses.append(twLicense)

					# Families
					for rsFamily in rsFoundry.familiesForAllowances(seatAllowances):
						twFamily = typeWorld.api.Family()
						rsFamily.applyValuesToTypeWorldObjects(twFamily)
						twFoundry.families.append(twFamily)

						# Fonts
						for rsFont in rsFamily.fontsForAllowances(seatAllowances):
							if seatAllowances.has_key(rsFont.uniqueID()):
								seatAllowance = seatAllowances[rsFont.uniqueID()]
							else:
								seatAllowance = 0
							twFont = typeWorld.api.Font()
							rsFont.applyValuesToTypeWorldObjects(twFont, {'seatsAllowedForUser': seatAllowance, 'seatsInstalledByUser': self.seatsInstalledForUser(userID, rsFont.uniqueID(), anonymousAppID)})
							twFamily.fonts.append(twFont)

							# Font-Level Versions
							for rsVersion in rsFont.versions:
								twVersion = typeWorld.api.Version()
								rsVersion.applyValuesToTypeWorldObjects(twVersion)
								twFont.versions.append(twVersion)

						# Family-Level Versions
						for rsVersion in rsFamily.versions:
							twVersion = typeWorld.api.Version()
							rsVersion.applyValuesToTypeWorldObjects(twVersion)
							twFamily.versions.append(twVersion)

				return flask.Response(api.dumpJSON(), mimetype = 'application/json')
			

		# InstallFont Command
		elif command == 'installFont':
			api.response = typeWorld.api.Response()
			api.response.command = command
			api.response.installFont = typeWorld.api.InstallFontResponse()

			# fontID is empty
			if not fontID:
				api.response.installFont.type = 'error'
				api.response.installFont.errorMessage.en = 'No fontID supplied'
				api.response.installFont.errorMessage.de = u'Keine fontID übergeben'
				return flask.Response(api.dumpJSON(), mimetype = 'application/json')

			# fontID doesn't exist
			elif not self.fontsByID.has_key(fontID):
				api.response.installFont.type = 'error'
				api.response.installFont.errorMessage.en = 'No font found for fontID'
				api.response.installFont.errorMessage.de = u'Kein Font für fontID gefunden'
				return flask.Response(api.dumpJSON(), mimetype = 'application/json')

			# fontVersion is empty
			elif not fontVersion:
				api.response.installFont.type = 'error'
				api.response.installFont.errorMessage.en = 'No fontVersion supplied'
				api.response.installFont.errorMessage.de = u'Keine fontVersion übergeben'
				return flask.Response(api.dumpJSON(), mimetype = 'application/json')

			# all set, output fonts
			else:
				font = self.fontsByID[fontID]

				# Font is free, no authentication required. Give it away
				if font.plist['trackSeatAllowance'] == False:

					fileName = '%s_%s.otf' % (font.keyword, fontVersion)
					fontPath = os.path.join(os.path.dirname(font.parent.plistPath), 'fontfiles', fileName)

					# File exists
					if os.path.exists(fontPath):
						b = open(fontPath, 'rb').read()

						response = flask.make_response(b)
						response.headers['Content-Type'] = 'font/otf'
						response.headers['Content-Disposition'] = 'attachment; filename=%s' % fileName
						return response

					# File does not exist
					else:
						api.response.installFont.type = 'error'
						api.response.installFont.errorMessage.en = 'Font file could not be found.'
						api.response.installFont.errorMessage.de = u'Die Font-Datei konnte nicht gefunden werden.'
						return flask.Response(api.dumpJSON(), mimetype = 'application/json')

				# Font is commercial. Need to check, if we're allowed to give it away
				else:

					# userID is empty
					if not userID:
						api.response.installFont.type = 'error'
						api.response.installFont.errorMessage.en = 'No userID supplied'
						api.response.installFont.errorMessage.de = u'Keine userID übergeben'
						return flask.Response(api.dumpJSON(), mimetype = 'application/json')

					# userID doesn't exist
					if not self.usersByID.has_key(userID):
						api.response.installFont.type = 'error'
						api.response.installFont.errorMessage.en = 'This userID is unknown'
						api.response.installFont.errorMessage.de = 'Diese userID is unbekannt'
						return flask.Response(api.dumpJSON(), mimetype = 'application/json')


					seatsInstalledForUser = self.seatsInstalledForUser(userID, fontID)
					seatsAllowedForUser = self.seatsAllowedForUser(userID, fontID)
			
					# User still has seat allowance
					if seatsInstalledForUser < seatsAllowedForUser:

						fileName = '%s_%s.otf' % (font.keyword, fontVersion)
						fontPath = os.path.join(os.path.dirname(font.parent.plistPath), 'fontfiles', fileName)

						# File exists
						if os.path.exists(fontPath):

							# Add installation to ledger
							self.addInstallation(userID, fontID, anonymousAppID)

							# Put out font
							b = open(fontPath, 'rb').read()
							response = flask.make_response(b)
							response.headers['Content-Type'] = 'font/otf'
							response.headers['Content-Disposition'] = 'attachment; filename=%s' % fileName
							return response

						# File does not exist
						else:
							api.response.installFont.type = 'error'
							api.response.installFont.errorMessage.en = 'Font file could not be found.'
							api.response.installFont.errorMessage.de = u'Die Font-Datei konnte nicht gefunden werden.'
							return flask.Response(api.dumpJSON(), mimetype = 'application/json')

					# User's seat allowance has been reached
					else:
						api.response.installFont.type = 'seatAllowanceReached'
						return flask.Response(api.dumpJSON(), mimetype = 'application/json')

		# InstallFont Command
		elif command == 'uninstallFont':
			api.response = typeWorld.api.Response()
			api.response.command = command
			api.response.uninstallFont = typeWorld.api.UninstallFontResponse()

			# fontID is empty
			if not fontID:
				api.response.uninstallFont.type = 'error'
				api.response.uninstallFont.errorMessage.en = 'No fontID supplied'
				api.response.uninstallFont.errorMessage.de = u'Keine fontID übergeben'
				return flask.Response(api.dumpJSON(), mimetype = 'application/json')

			# fontID doesn't exist
			if not self.fontsByID.has_key(fontID):
				api.response.uninstallFont.type = 'error'
				api.response.uninstallFont.errorMessage.en = 'No font found for fontID'
				api.response.uninstallFont.errorMessage.de = u'Kein Font für fontID gefunden'
				return flask.Response(api.dumpJSON(), mimetype = 'application/json')

			# installation not found
			if self.seatsInstalledForUser(userID, fontID, anonymousAppID) != 1:
				api.response.uninstallFont.type = 'error'
				api.response.uninstallFont.errorMessage.en = 'This font installation for this appID is unknown'
				api.response.uninstallFont.errorMessage.de = u'Diese Font-Installation für diese appID ist unbekannt.'
				return flask.Response(api.dumpJSON(), mimetype = 'application/json')

			# all set, remove font
			else:
				font = self.fontsByID[fontID]

				# Font is free; do nothing
				if font.plist['trackSeatAllowance'] == False:
					pass

				# Font is commercial, need to remove license from ledger
				else:

					# userID is empty
					if not userID:
						api.response.uninstallFont.type = 'error'
						api.response.uninstallFont.errorMessage.en = 'No userID supplied'
						api.response.uninstallFont.errorMessage.de = u'Keine userID übergeben'
						return flask.Response(api.dumpJSON(), mimetype = 'application/json')

					# userID doesn't exist
					if not self.usersByID.has_key(userID):
						api.response.uninstallFont.type = 'error'
						api.response.uninstallFont.errorMessage.en = 'This userID is unknown'
						api.response.uninstallFont.errorMessage.de = 'Diese userID is unbekannt'
						return flask.Response(api.dumpJSON(), mimetype = 'application/json')

					# Add installation to ledger
					self.removeInstallation(userID, fontID, anonymousAppID)

					api.response.uninstallFont.type = 'success'
					return flask.Response(api.dumpJSON(), mimetype = 'application/json')


# Anonymous App ID, will later be different for every installation
anonymousAppID = 'H625npqamfsy2cnZgNSJWpZm'

# Start web server
app = flask.Flask(__name__)

ip = '127.0.0.1'
port = 5000


# Print test links
url = 'http://%s:%s/' % (ip, port)
dataPath = os.path.join(os.path.dirname(__file__), 'data')
server = ReferenceServer(dataPath, url)
print server.fontsByID
print '####################################################################'
print
print '  Type.World Reference Server'
print '  General API information:'.ljust(45), url
print '  Official Type.World App link for user1:'.ljust(45), '%s?userID=%s' % (url, server.users[0].plist['anonymousID'])
print '  installableFonts command for user1:'.ljust(45), '%s?command=installableFonts&userID=%s&anonymousAppID=%s' % (url, server.users[0].plist['anonymousID'], anonymousAppID)
print '  Install free font:'.ljust(45), '%s?command=installFont&fontID=awesomefonts-YanoneKaffeesatz-Bold&fontVersion=1.0' % (url)
print '  Install commercial font:'.ljust(45), '%s?command=installFont&userID=%s&fontID=awesomefonts-YanoneKaffeesatz-Regular&fontVersion=1.0&anonymousAppID=H625npqamfsy2cnZgNSJWpZm' % (url, server.users[0].plist['anonymousID'])
print '  Uninstall commercial font:'.ljust(45), '%s?command=uninstallFont&userID=%s&fontID=awesomefonts-YanoneKaffeesatz-Regular&anonymousAppID=H625npqamfsy2cnZgNSJWpZm' % (url, server.users[0].plist['anonymousID'])
print
print '####################################################################'
print

@app.route('/', methods=['GET'])
def root():


	# Instantiate reference server
	# Read it new every time to reflect changes in the data base (file structure)
	server = ReferenceServer(dataPath, url)

	# Get JSON (or font) output
	response = server.api(command = flask.request.args.get('command'), userID = flask.request.args.get('userID'), anonymousAppID = flask.request.args.get('anonymousAppID'), fontID = flask.request.args.get('fontID'), fontVersion = flask.request.args.get('fontVersion'))

	# Send output
	return response
	

if __name__ == '__main__':
	app.run(host=ip, port=port, debug=True)
