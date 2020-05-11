# Import module
from typeworld.api import *

# Root of Response
root = RootResponse()

# Response for 'availableFonts' command
installableFonts = InstallableFontsResponse()
installableFonts.response = 'success'

###

# Add designer to root of response
designer = Designer()
designer.keyword = 'max'
designer.name.en = 'Max Mustermann'
installableFonts.designers.append(designer)

# Add foundry to root of response
foundry = Foundry()
foundry.name.en = 'Awesome Fonts'
foundry.website = 'https://awesomefonts.com'
foundry.uniqueID = 'awesomefontsfoundry'
installableFonts.foundries.append(foundry)

# Add license to foundry
license = LicenseDefinition()
license.keyword = 'awesomeFontsEULA'
license.name.en = 'Awesome Fonts Desktop EULA'
license.URL = 'https://awesomefonts.com/EULA/'
foundry.licenses.append(license)

# Add font family to foundry
family = Family()
family.name.en = 'Awesome Sans'
family.designerKeywords.append('max')
family.uniqueID = 'awesomefontsfoundry-awesomesans'
foundry.families.append(family)

# Add version to font family
version = Version()
version.number = 0.1
family.versions.append(version)

# Add font to family
font = Font()
font.name.en = 'Regular'
font.postScriptName = 'AwesomeSans-Regular'
font.licenseKeyword = 'awesomeFontsEULA'
font.purpose = 'desktop'
font.format = 'otf'
font.uniqueID = 'awesomefontsfoundry-awesomesans-regular'
family.fonts.append(font)

# Font's license usage
licenseUsage = LicenseUsage()
licenseUsage.keyword = 'awesomeFontsEULA'
font.usedLicenses.append(licenseUsage)

###

# Attach EndpointResponse to RootResponse
root.installableFonts = installableFonts

# Create API response as JSON
jsonResponse = root.dumpJSON()

# Read JSON code back in for pretty printing
import json
print(json.dumps(json.loads(jsonResponse), indent=4, sort_keys=True))
