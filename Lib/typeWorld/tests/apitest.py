# -*- coding: utf-8 -*-

from typeWorld.api import *

if __name__ == '__main__':

	# Root of API
	api = APIRoot()
	api.name.en = u'Font Publisher'
	api.canonicalURL = 'https://fontpublisher.com/api/'
	api.adminEmail = 'admin@fontpublisher.com'
	api.supportedCommands = [x['keyword'] for x in COMMANDS] # this API supports all commands

	# Response for 'availableFonts' command
	response = Response()
	response.command = 'installableFonts'
	responseCommand = InstallableFontsResponse()
	responseCommand.type = 'success'
	response.installableFonts = responseCommand
	api.response = response

	# Add designer to root of response
	designer = Designer()
	designer.keyword = u'max'
	designer.name.en = u'Max Mustermann'
	responseCommand.designers.append(designer)

	# Add foundry to root of response
	foundry = Foundry()
	foundry.name.en = u'Awesome Fonts'
	foundry.website = 'https://awesomefonts.com'
	responseCommand.foundries.append(foundry)

	# Add license to foundry
	license = License()
	license.keyword = u'awesomeFontsEULA'
	license.name.en = u'Awesome Fonts Desktop EULA'
	license.URL = 'https://awesomefonts.com/EULA/'
	foundry.licenses.append(license)

	# Add font family to foundry
	family = Family()
	family.name.en = u'Awesome Sans'
	family.designers.append(u'max')
	foundry.families.append(family)

	# Add version to font family
	version = Version()
	version.number = 0.1
	family.versions.append(version)

	# Add font to family
	font = Font()
	font.name.en = u'Regular'
	font.postScriptName = u'AwesomeSans-Regular'
	font.licenseKeyword = u'awesomeFontsEULA'
	font.type = u'desktop'
	family.fonts.append(font)

	# Output API response as JSON
	json = api.dumpJSON()

	# Let’s see it
	print json

	# Load a second API instance from that JSON
	api2 = APIRoot()
	api2.loadJSON(json)

	# Let’s see if they are identical
	print api.sameContent(api2)
