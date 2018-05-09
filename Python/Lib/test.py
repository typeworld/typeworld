# -*- coding: utf-8 -*-

from typeWorld.api import *

if __name__ == '__main__':

	# InstallableFonts

	# Root of API
	api = APIRoot()
	api.name.en = 'Font Publisher'
	api.canonicalURL = 'https://fontpublisher.com/api/'
	api.adminEmail = 'admin@fontpublisher.com'
	api.supportedCommands = [x['keyword'] for x in COMMANDS] # this API supports all commands
	print(api)

	# Response for 'availableFonts' command
	response = Response()
	response.command = 'installableFonts'
	responseCommand = InstallableFontsResponse()
	responseCommand.type = 'success'
	response.installableFonts = responseCommand
	api.response = response
	print(response)

	# Add designer to root of response
	designer = Designer()
	designer.keyword = 'max'
	designer.name.en = 'Max Mustermann'
	responseCommand.designers.append(designer)
	print(designer)
	assert designer.parent == responseCommand

	# Add foundry to root of response
	foundry = Foundry()
	foundry.uniqueID = 'yanone'
	foundry.name.en = 'Awesome Fonts'
	foundry.website = 'https://awesomefonts.com'
	responseCommand.foundries.append(foundry)
	print(foundry)

	# Add license to foundry
	license = License()
	license.keyword = 'awesomeFontsEULA'
	license.name.en = 'Awesome Fonts Desktop EULA'
	license.URL = 'https://awesomefonts.com/EULA/'
	foundry.licenses.append(license)
	print(license)
	assert license.parent == foundry

	# Add font family to foundry
	family = Family()
	family.uniqueID = 'yanone-AwesomeSans'
	family.name.en = 'Awesome Sans'
	family.designers.append('max')
	foundry.families.append(family)
	print(family)
	assert family.parent == foundry

	# Add version to font
	version = Version()
	version.number = 0.1
	family.versions.append(version)
	print(version)
	assert version.isFontSpecific() == False
	assert version.parent == family
	assert type(family.getDesigners()) == list
	assert type(family.getAllDesigners()) == list

	# Add font to family
	font = Font()
	font.uniqueID = 'yanone-NonameSans-Regular'
	font.name.en = 'Regular'
	font.postScriptName = 'AwesomeSans-Regular'
	font.licenseKeyword = 'awesomeFontsEULA'
	font.purpose = 'desktop'
	font.type = 'otf'
	family.fonts.append(font)
	print(font)

	# Add version to font
	version = Version()
	version.number = 0.2
	font.versions.append(version)
	print(version)
	assert version.isFontSpecific() == True
	assert version.parent == font

	# Add font to family
	font = Font()
	font.uniqueID = 'yanone-NonameSans-Bold'
	font.name.en = 'Regular'
	font.postScriptName = 'AwesomeSans-Bold'
	font.licenseKeyword = 'awesomeFontsEULA'
	font.purpose = 'desktop'
	font.type = 'otf'
	family.fonts.append(font)
	assert type(font.getSortedVersions()) == list
	assert type(font.getDesigners()) == list

	# Output API response as JSON, includes validation
	json = api.dumpJSON()

	# Let’s see it
	print(json)

	# Load a second API instance from that JSON
	api2 = APIRoot()
	api2.loadJSON(json)

	# Let’s see if they are identical
	assert api.sameContent(api2) == True






	# InstallFont


	# Root of API
	api = APIRoot()
	api.name.en = 'Font Publisher'
	api.canonicalURL = 'https://fontpublisher.com/api/'
	api.adminEmail = 'admin@fontpublisher.com'
	api.supportedCommands = [x['keyword'] for x in COMMANDS] # this API supports all commands
	print(api)

	# Response for 'availableFonts' command
	response = Response()
	response.command = 'installFont'
	responseCommand = InstallFontResponse()
	responseCommand.type = 'success'
	response.installFont = responseCommand
	api.response = response
	print(response)

	responseCommand.font = b'ABC'
	responseCommand.encoding = 'base64'

	# Output API response as JSON, includes validation
	json = api.dumpJSON()





	# UninstallFont


	# Root of API
	api = APIRoot()
	api.name.en = 'Font Publisher'
	api.canonicalURL = 'https://fontpublisher.com/api/'
	api.adminEmail = 'admin@fontpublisher.com'
	api.supportedCommands = [x['keyword'] for x in COMMANDS] # this API supports all commands
	print(api)

	# Response for 'availableFonts' command
	response = Response()
	response.command = 'uninstallFont'
	responseCommand = UninstallFontResponse()
	responseCommand.type = 'success'
	response.uninstallFont = responseCommand
	api.response = response
	print(response)

	# Output API response as JSON, includes validation
	json = api.dumpJSON()



	# Docu



	# Docu
	docu = api.docu()