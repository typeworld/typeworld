# Import module
import typeworld.protocol

# Root of Response
root = typeworld.protocol.RootResponse()

# Response for 'availableFonts' command
installableFonts = typeworld.protocol.InstallableFontsResponse()
installableFonts.response = 'success'

###

# Add designer to root of response
designer = typeworld.protocol.Designer()
designer.keyword = 'max'
designer.name.en = 'Max Mustermann'
installableFonts.designers.append(designer)

# Add foundry to root of response
foundry = typeworld.protocol.Foundry()
foundry.name.en = 'Awesome Fonts'
foundry.website = 'https://awesomefonts.com'
foundry.uniqueID = 'awesomefontsfoundry'
installableFonts.foundries.append(foundry)

# Add license to foundry
license = typeworld.protocol.LicenseDefinition()
license.keyword = 'awesomeFontsEULA'
license.name.en = 'Awesome Fonts Desktop EULA'
license.URL = 'https://awesomefonts.com/EULA/'
foundry.licenses.append(license)

# Add font family to foundry
family = typeworld.protocol.Family()
family.name.en = 'Awesome Sans'
family.designerKeywords.append('max')
family.uniqueID = 'awesomefontsfoundry-awesomesans'
foundry.families.append(family)

# Add version to font family
version = typeworld.protocol.Version()
version.number = 0.1
family.versions.append(version)

# Add font to family
font = typeworld.protocol.Font()
font.name.en = 'Regular'
font.postScriptName = 'AwesomeSans-Regular'
font.licenseKeyword = 'awesomeFontsEULA'
font.purpose = 'desktop'
font.format = 'otf'
font.uniqueID = 'awesomefontsfoundry-awesomesans-regular'
family.fonts.append(font)

# Font's license usage
licenseUsage = typeworld.protocol.LicenseUsage()
licenseUsage.keyword = 'awesomeFontsEULA'
font.usedLicenses.append(licenseUsage)

###

# Attach EndpointResponse to RootResponse
root.installableFonts = installableFonts

# Print API response as JSON
print(root.dumpJSON())