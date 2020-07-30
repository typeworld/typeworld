# -*- coding: utf-8 -*-

import sys
import os
import copy
import time
import urllib.request
import urllib.parse
import ssl
import certifi
import json
import unittest
import tempfile

path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(path)

import typeworld.client  # noqa: E402

from typeworld.client import (  # noqa: E402
    APIClient,
    JSON,
    AppKitNSUserDefaults,
    performRequest,
)

# Data Types
from typeworld.api import (  # noqa: E402
    HexColorDataType,
    FontEncodingDataType,
    EmailDataType,
    BooleanDataType,
    WebURLDataType,
    IntegerDataType,
    FloatDataType,
    DateDataType,
    VersionDataType,
    MultiLanguageText,
    MultiLanguageLongText,
)

# Classes
from typeworld.api import (  # noqa: E402
    InstallFontAsset,
    UninstallFontAsset,
    FontListProxy,
    RootResponse,
    EndpointResponse,
    Designer,
    LicenseDefinition,
    Version,
    LicenseUsage,
    Font,
    Family,
    Foundry,
    InstallableFontsResponse,
    InstallFontsResponse,
    UninstallFontsResponse,
    FontPackage,
)

from typeworld.api import (  # noqa: E402
    LanguageSupportDataType,
    OpenTypeFeatureDataType,
    OpenSourceLicenseIdentifierDataType,
    SupportedAPICommandsDataType,
    FontPurposeDataType,
    FontMimeType,
    FontStatusDataType,
    InstallableFontsResponseType,
    InstallFontAssetResponseType,
    InstallFontResponseType,
    UninstallFontAssedResponseType,
    UninstallFontResponseType,
)

# Constants
from typeworld.api import COMMANDS, MAC  # noqa: E402

# Methods
from typeworld.api import makeSemVer  # noqa: E402

from inspect import currentframe, getframeinfo  # noqa: E402


ONLINE = True

print("Started...")

sslcontext = ssl.create_default_context(cafile=certifi.where())


# Inspection/Interactive shell
# import code; code.interact(local=locals())


freeSubscription = (
    "typeworld://json+https//typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
)
flatFreeSubscription = (
    "typeworld://json+https//typeworldserver.com/flatapi/q8JZfYn9olyUvcCOiqHq/"
)
protectedSubscription = (
    "typeworld://json+https//s9lWvayTEOaB9eIIMA67:OxObIWDJjW95SkeL3BNr:"
    "qncMnRXZLvHfLLwteTsX@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
)
protectedSubscriptionWithoutAccessToken = (
    "typeworld://json+https//s9lWvayTEOaB9eIIMA67:OxObIWDJjW95SkeL3BNr@"
    "typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
)
freeNamedSubscription = (
    "typeworld://json+https//s9lWvayTEOaB9eIIMA67@"
    "typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
)
testUser1 = ("test1@type.world", "12345678")
testUser2 = ("test2@type.world", "01234567")
testUser3 = ("test3@type.world", "23456789")


# Travis CI
if "TRAVIS" in os.environ:
    MOTHERSHIP = "https://api.type.world/v1"

# Local testing
else:
    MOTHERSHIP = "https://api.type.world/v1"  # nocoverage (for local testing only)

    # Testing specific version
    if len(sys.argv) >= 2:  # nocoverage (for local testing only)
        MOTHERSHIP = sys.argv[
            1
        ]  # .replace('-dot-', '.') #nocoverage (for local testing only)
        del sys.argv[1:]  # nocoverage (for local testing only)

        if not MOTHERSHIP.endswith("/v1"):  # nocoverage (for local testing only)
            MOTHERSHIP += "/v1"  # nocoverage (for local testing only)


print("Testing on %s" % MOTHERSHIP)

global errors, failures
errors = []
failures = []

print("setting up objects started...")


# EndpointResponse
root = EndpointResponse()
root.name.en = "Font Publisher"
root.canonicalURL = "http://fontpublisher.com/api/"
root.adminEmail = "admin@fontpublisher.com"
root.supportedCommands = [
    x["keyword"] for x in COMMANDS
]  # this API supports all commands
root.backgroundColor = "AABBCC"
root.licenseIdentifier = "CC-BY-NC-ND-4.0"
root.logoURL = (
    "https://typeworldserver.com/?page=outputDataBaseFile&"
    "className=TWFS_Foundry&ID=8&field=logo"
)
root.privacyPolicyURL = "https://type.world/legal/privacy.html"
root.termsOfServiceURL = "https://type.world/legal/terms.html"
root.public = False
root.version = "0.1.7-alpha"
root.websiteURL = "https://typeworldserver.com"

# InstallableFontsResponse
designer = Designer()
designer.description.en = "Yanone is a type designer based in Germany."
designer.keyword = "yanone"
designer.name.en = "Yanone"
designer.websiteURL = "https://yanone.de"

designer2 = Designer()
designer2.description.en = "Yanone is a type designer based in Germany."
designer2.keyword = "yanone2"
designer2.name.en = "Yanone"
designer2.websiteURL = "https://yanone.de"

# License
license = LicenseDefinition()
license.URL = "https://yanone.de/eula.html"
license.keyword = "yanoneEULA"
license.name.en = "Yanone EULA"

# Font-specific Version
fontVersion = Version()
fontVersion.description.en = "Initial release"
fontVersion.description.de = "Erstveröffentlichung"
fontVersion.number = 1.0
fontVersion.releaseDate = "2004-10-10"

# FontPackage
desktopFontsPackage = FontPackage()
desktopFontsPackage.keyword = "desktop"
desktopFontsPackage.name.en = "Desktop Fonts"
desktopFontsPackage.name.de = "Desktop-Schriften"

# LicenseUsage
usedLicense = LicenseUsage()
usedLicense.allowanceDescription.en = "N/A"
usedLicense.dateAddedForUser = "2019-10-01"
usedLicense.keyword = "yanoneEULA"
usedLicense.seatsAllowed = 5
usedLicense.seatsInstalled = 1
usedLicense.upgradeURL = "https://yanone.de/buy/kaffeesatz/upgrade?customerID=123456"

# Font
font = Font()
font.dateFirstPublished = "2004-10-10"
font.designerKeywords.append("yanone")
font.designerKeywords = ["yanone", "yanone2"]
assert len(font.designerKeywords) == 2
font.format = "otf"
font.free = True
font.name.en = "Regular"
font.name.de = "Normale"
font.pdfURL = "https://yanone.de/fonts/kaffeesatz.pdf"
font.postScriptName = "YanoneKaffeesatz-Regular"
font.protected = False
font.purpose = "desktop"
font.packageKeywords.append("desktop")
font.status = "stable"
font.uniqueID = "yanone-kaffeesatz-regular"
font.usedLicenses.append(usedLicense)
font.usedLicenses = [usedLicense]
assert len(font.usedLicenses) == 1
font.variableFont = False
font.versions.append(fontVersion)
font.versions = [fontVersion]
assert len(font.versions) == 1
font.languageSupport = {"latn": ["DEU"]}
font.features = ["aalt", "liga"]

# Font 2
font2 = Font()
font2.dateFirstPublished = "2004-10-10"
font2.designerKeywords.append("yanone")
font2.designerKeywords = ["yanone"]
assert len(font2.designerKeywords) == 1
font2.format = "otf"
font2.free = True
font2.name.en = "Bold"
font2.name.de = "Fette"
font2.pdfURL = "https://yanone.de/fonts/kaffeesatz.pdf"
font2.postScriptName = "YanoneKaffeesatz-Bold"
font2.protected = False
font2.purpose = "desktop"
font.packageKeywords.append("desktop")
font2.status = "stable"
font2.uniqueID = "yanone-kaffeesatz-bold"
font2.usedLicenses.append(usedLicense)
font2.usedLicenses = [usedLicense]
assert len(font2.usedLicenses) == 1
font2.variableFont = False
font2.versions.append(fontVersion)
font2.versions = [fontVersion]
assert len(font2.versions) == 1

# Family-specific Version
familyVersion = Version()
familyVersion.description.en = "Initial release"
familyVersion.description.de = "Erstveröffentlichung"
familyVersion.number = 1.0
familyVersion.releaseDate = "2004-10-10"

# Family
family = Family()
family.billboardURLs = [
    (
        "https://typeworldserver.com/?page=outputDataBaseFile&"
        "className=TWFS_FamilyBillboards&ID=2&field=image"
    )
]
family.billboardURLs.append(
    (
        "https://typeworldserver.com/?page=outputDataBaseFile&"
        "className=TWFS_FamilyBillboards&ID=6&field=image"
    )
)
family.dateFirstPublished = "2019-10-01"
family.description.en = "Kaffeesatz is a free font classic"
family.designerKeywords.append("yanone")
family.designerKeywords = ["yanone"]  # same as above
assert len(family.designerKeywords) == 1
family.galleryURL = "https://fontsinuse.com/kaffeesatz"
family.issueTrackerURL = "https://github.com/yanone/kaffeesatzfont/issues"
family.name.en = "Yanone Kaffeesatz"
family.pdfURL = "https://yanone.de/fonts/kaffeesatz.pdf"
family.sourceURL = "https://github.com/yanone/kaffeesatzfont"
family.uniqueID = "yanone-yanonekaffeesatz"
family.versions.append(familyVersion)
family.versions = [familyVersion]
assert len(family.versions) == 1
family.fonts.append(font)
family.fonts = [font]
assert len(family.fonts) == 1
family.fonts.append(font2)
assert len(family.fonts) == 2
family.fonts = [font, font2]
assert len(family.fonts) == 2
family.packages.append(desktopFontsPackage)
assert len(family.packages) == 1

# Foundry
foundry = Foundry()
foundry.backgroundColor = "AABBCC"
foundry.description.en = "Yanone is a foundry lead by German type designer Yanone."
foundry.email = "font@yanone.de"
foundry.licenses.append(license)
foundry.name.en = "Awesome Fonts"
foundry.name.de = "Tolle Schriften"

foundry.socialURLs.append("https://facebook.com/pages/YanoneYanone")
foundry.socialURLs.append("https://twitter.com/yanone")

foundry.supportEmail = "support@yanone.de"
foundry.supportTelephone = "+49123456789"
foundry.supportURL = "https://yanone.de/support/"
foundry.telephone = "+49123456789"
foundry.twitter = "yanone"
foundry.uniqueID = "yanone"
foundry.websiteURL = "https://yanone.de"
foundry.families.append(family)
foundry.families = [family]
assert len(foundry.families) == 1
foundry.styling = json.loads(
    """{"light": {
            "headerColor": "F20D5E",
            "headerTextColor": "000000",
            "headerLinkColor": "E5F20D",

            "backgroundColor": "E5F20D",
            "textColor": "000000",
            "linkColor": "F7AD22",

            "selectionColor": "0D79F2",
            "selectionTextColor": "E5F20D",

            "buttonColor": "197AA3",
            "buttonTextColor": "FFFFFF",

            "informationViewBackgroundColor": "469BF5",
            "informationViewTextColor": "000000",
            "informationViewLinkColor": "E5F20D",

            "informationViewButtonColor": "E5F20D",
            "informationViewButtonTextColor": "000000"

        }, "dark": {
            "headerColor": "B10947",
            "headerTextColor": "000000",
            "headerLinkColor": "E5F20D",

            "backgroundColor": "1A1A1A",
            "textColor": "E5F20D",
            "linkColor": "C07F07",

            "selectionColor": "B10947",
            "selectionTextColor": "E5F20D",

            "buttonColor": "22A4DC",
            "buttonTextColor": "000000",

            "informationViewBackgroundColor": "000000",
            "informationViewTextColor": "999999",
            "informationViewLinkColor": "E5F20D",

            "informationViewButtonColor": "1E90C1",
            "informationViewButtonTextColor": "000000"

        } }"""
)

# InstallableFontsResponse
installableFonts = InstallableFontsResponse()
installableFonts.designers.append(designer)
installableFonts.designers.append(designer2)
installableFonts.designers.remove(designer2)
installableFonts.designers.extend([designer2])
installableFonts.name.en = "Commercial Fonts"
installableFonts.name.de = "Kommerzielle Schriften"
installableFonts.prefersRevealedUserIdentity = True
installableFonts.response = "success"
installableFonts.userEmail = "post@yanone.de"
installableFonts.userName.en = "Yanone"
installableFonts.version = "0.1.7-alpha"
installableFonts.foundries.append(foundry)
# print(installableFonts.designers)


class User(object):
    def __init__(self, login=None, online=True):
        self.login = login
        self.prefFile = os.path.join(tempFolder, str(id(self)) + ".json")
        self.online = online
        self.credentials = ()

        self.loadClient()

        if self.login:
            success, message = self.client.deleteUserAccount(*self.login)
            if not success and message != [
                "#(response.userUnknown)",
                "#(response.userUnknown.headline)",
            ]:
                raise ValueError(message)
            # print('Creating user account for %s' % self.login[0])
            success, message = self.client.createUserAccount(
                "Test User", self.login[0], self.login[1], self.login[1]
            )
            if not success:
                raise ValueError(message)
            self.credentials = (self.client.user(), self.client.secretKey())

            self.clearInvitations()
            self.clearSubscriptions()

    # def linkUser(self):
    # 	self.unlinkUser()
    # 	if self.login:
    # 		return self.client.linkUser(*self.credentials)

    def expiringTestFont(self):
        return (
            self.client.publishers()[0]
            .subscriptions()[-1]
            .protocol.installableFontsCommand()[1]
            .foundries[-1]
            .families[0]
            .fonts[-1]
        )

    def testFont(self):
        publisher = self.client.publishers()[0]
        subscription = publisher.subscriptions()[-1]
        installableFontsCommand = subscription.protocol.installableFontsCommand()[1]
        foundry = installableFontsCommand.foundries[-1]
        family = foundry.families[-1]
        font = family.fonts[-1]
        return font

    def testFonts(self):
        publisher = self.client.publishers()[0]
        subscription = publisher.subscriptions()[-1]
        installableFontsCommand = subscription.protocol.installableFontsCommand()[1]
        foundry = installableFontsCommand.foundries[-1]
        family = foundry.families[-1]
        return family.fonts

    def clearSubscriptions(self):
        self.client.testScenario = None
        for publisher in self.client.publishers():
            publisher.delete()

    def clearInvitations(self):
        self.client.testScenario = None
        for invitation in self.client.pendingInvitations():
            invitation.decline()

    def takeDown(self):
        self.client.testScenario = None
        self.clearInvitations()
        self.clearSubscriptions()
        if self.login:
            self.client.deleteUserAccount(*self.login)

    # def unlinkUser(self):
    # 	self.client.testScenario = None
    # 	if self.login:
    # 		if self.client.user():
    # 			self.client.unlinkUser()

    def loadClient(self):
        self.client = APIClient(
            preferences=AppKitNSUserDefaults("world.type.test%s" % id(self))
            if MAC
            else JSON(self.prefFile),
            mothership=MOTHERSHIP,
            pubSubSubscriptions=True,
            online=self.online,
            testing=True,
        )


print("setting up objects finished...")


class TestStringMethods(unittest.TestCase):

    currentResult = None
    maxDiff = None

    def test_emptyValues(self):

        print("test_emptyValues() started...")

        self.assertTrue(HexColorDataType().valid())
        self.assertTrue(FontEncodingDataType().valid())
        self.assertTrue(EmailDataType().valid())
        self.assertTrue(BooleanDataType().valid())
        self.assertTrue(WebURLDataType().valid())
        self.assertTrue(IntegerDataType().valid())
        self.assertTrue(FloatDataType().valid())
        self.assertTrue(DateDataType().valid())
        self.assertTrue(VersionDataType().valid())

        self.assertTrue(LanguageSupportDataType().valid())
        self.assertTrue(OpenTypeFeatureDataType().valid())
        self.assertTrue(OpenSourceLicenseIdentifierDataType().valid())
        self.assertTrue(SupportedAPICommandsDataType().valid())
        self.assertTrue(FontPurposeDataType().valid())
        self.assertTrue(FontMimeType().valid())
        self.assertTrue(FontStatusDataType().valid())

        self.assertTrue(InstallableFontsResponseType().valid())
        self.assertTrue(InstallFontAssetResponseType().valid())
        self.assertTrue(InstallFontResponseType().valid())
        self.assertTrue(UninstallFontAssedResponseType().valid())
        self.assertTrue(UninstallFontResponseType().valid())

    def test_EndpointResponse(self):

        print("test_EndpointResponse() started...")

        print(root)
        # Dump and reload
        json = root.dumpJSON()
        root2 = EndpointResponse()
        root2.loadJSON(json)
        self.assertTrue(root.sameContent(root2))

        # name
        r2 = copy.deepcopy(root)
        r2.name.en = ""
        self.assertEqual(
            r2.validate()[2],
            ["<EndpointResponse>.name is a required attribute, but empty"],
        )

        # canonicalURL
        r2 = copy.deepcopy(root)
        try:
            r2.canonicalURL = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        # adminEmail
        r2 = copy.deepcopy(root)
        try:
            r2.adminEmail = "post_at_yanone.de"
        except ValueError as e:
            self.assertEqual(str(e), "Not a valid email format: post_at_yanone.de")

        # supportedCommands
        r2 = copy.deepcopy(root)
        try:
            r2.supportedCommands = ["unsupportedCommand"]
        except ValueError as e:
            self.assertEqual(
                str(e),
                (
                    "Unknown API command: 'unsupportedCommand'. "
                    "Possible: ['endpoint', 'installableFonts', 'installFonts', "
                    "'uninstallFonts']"
                ),
            )

        # backgroundColor
        r2 = copy.deepcopy(root)
        try:
            r2.backgroundColor = "CDEFGH"
        except ValueError as e:
            self.assertEqual(
                str(e),
                "Not a valid hex color of format RRGGBB (like FF0000 for red): CDEFGH",
            )

        # licenseIdentifier
        r2 = copy.deepcopy(root)
        try:
            r2.licenseIdentifier = "unsupportedLicense"
        except ValueError as e:
            self.assertEqual(
                str(e),
                (
                    "Unknown license identifier: 'unsupportedLicense'. "
                    "See https://spdx.org/licenses/"
                ),
            )

        # logo
        r2 = copy.deepcopy(root)
        try:
            r2.logoURL = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        # privacyPolicyURL
        r2 = copy.deepcopy(root)
        try:
            r2.privacyPolicyURL = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        # termsOfServiceURL
        r2 = copy.deepcopy(root)
        try:
            r2.termsOfServiceURL = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        # public
        r2 = copy.deepcopy(root)
        try:
            r2.public = "True"
        except ValueError as e:
            self.assertEqual(
                str(e), "Wrong data type. Is <class 'str'>, should be: <class 'bool'>."
            )

        # website
        r2 = copy.deepcopy(root)
        try:
            r2.websiteURL = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        print("test_EndpointResponse() finished...")

    def test_copy(self):

        print("test_copy() started...")

        i2 = copy.copy(installableFonts)
        self.assertTrue(installableFonts.sameContent(i2))

        i3 = copy.deepcopy(installableFonts)
        self.assertTrue(installableFonts.sameContent(i3))

        print("test_copy() finished...")

    def test_InstallableFontsResponse(self):

        print("test_InstallableFontsResponse()")

        print(installableFonts)
        # Dump and reload
        json = installableFonts.dumpJSON()
        installableFonts2 = InstallableFontsResponse()
        installableFonts2.loadJSON(json)
        self.assertTrue(installableFonts.sameContent(installableFonts2))

        # designers
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.designers = "yanone"
        except ValueError as e:
            self.assertEqual(
                str(e), "Wrong data type. Is <class 'str'>, should be: <class 'list'>."
            )

        # error
        i2 = copy.deepcopy(installableFonts)
        i2.response = "error"
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse> --> .response is 'error', "
                    "but .errorMessage is missing."
                )
            ],
        )

        # error
        i2 = copy.deepcopy(installableFonts)
        i2.response = "error"
        try:
            data = i2.dumpDict()  # noqa: F841
        except ValueError as e:
            self.assertEqual(
                str(e),
                (
                    "<InstallableFontsResponse> --> .response is 'error', "
                    "but .errorMessage is missing."
                ),
            )

        # name
        # allowed to be emtpy
        i2 = copy.deepcopy(installableFonts)
        i2.name.en = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(validate[2], [])

        # prefersRevealedUserIdentity
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.prefersRevealedUserIdentity = "True"
        except ValueError as e:
            self.assertEqual(
                str(e), "Wrong data type. Is <class 'str'>, should be: <class 'bool'>."
            )

        # type
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.response = "abc"
        except ValueError as e:
            self.assertEqual(
                str(e),
                (
                    "Unknown response type: 'abc'. Possible: ['success', 'error', "
                    "'noFontsAvailable', 'insufficientPermission', "
                    "'temporarilyUnavailable', 'validTypeWorldUserAccountRequired']"
                ),
            )

        # userEmail
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.userEmail = "post_at_yanone.de"
        except ValueError as e:
            self.assertEqual(str(e), "Not a valid email format: post_at_yanone.de")

        # userName
        i2 = copy.deepcopy(installableFonts)
        i2.userName.en = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(validate[2], [])

        # foundries
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries = "yanone"
        except ValueError as e:
            self.assertEqual(
                str(e), "Wrong data type. Is <class 'str'>, should be: <class 'list'>."
            )

        i2 = copy.deepcopy(installableFonts)
        i2.name.en = ""
        i2.name.de = ""
        validate = i2.validate()
        print(validate[2])
        # 		print(validate)
        self.assertEqual(
            validate[1],
            [
                (
                    "<InstallableFontsResponse> --> The response has no .name value. "
                    "It is not required, but highly recommended, to describe the "
                    "purpose of this subscription to the user (such as 'Commercial "
                    "Fonts', 'Free Fonts', etc. This is especially useful if you offer "
                    "several different subscriptions to the same user."
                )
            ],
        )

        i2 = copy.deepcopy(installableFonts)
        i2.response = "error"
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse> --> .response is 'error', "
                    "but .errorMessage is missing."
                )
            ],
        )

    def test_Designer(self):

        print("test_Designer()")

        # name
        i2 = copy.deepcopy(installableFonts)
        i2.designers[0].name.en = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.designers --> <Designer 'None'>.name "
                    "is a required attribute, but empty"
                )
            ],
        )

        # description
        # is optional, so this will pass
        i2 = copy.deepcopy(installableFonts)
        i2.designers[0].description.en = ""
        self.assertEqual(i2.validate()[2], [])

        # keyword
        i2 = copy.deepcopy(installableFonts)
        i2.designers[0].keyword = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.designers --> <Designer 'Yanone'>."
                    "keyword is a required attribute, but empty"
                ),
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'>.fonts --> <Font "
                    "'YanoneKaffeesatz-Regular'> --> Has designer 'yanone', but "
                    "<InstallableFontsResponse>.designers has no matching designer."
                ),
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'>.fonts --> <Font "
                    "'YanoneKaffeesatz-Bold'> --> Has designer 'yanone', but "
                    "<InstallableFontsResponse>.designers has no matching designer."
                ),
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'> --> Has designer "
                    "'yanone', but <InstallableFontsResponse>.designers has no "
                    "matching designer."
                ),
            ],
        )

        # name
        i2 = copy.deepcopy(installableFonts)
        i2.designers[0].name.en = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.designers --> <Designer 'None'>.name"
                    " is a required attribute, but empty"
                )
            ],
        )

        # website
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.designers[0].websiteURL = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

    def test_LicenseDefinition(self):

        print("test_LicenseDefinition()")

        # name
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].licenses[0].name.en = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".licenses --> <LicenseDefinition 'None'>.name is a required "
                    "attribute, but empty"
                )
            ],
        )

        # URL
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].licenses[0].URL = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        # keyword
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].licenses[0].keyword = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".licenses --> <LicenseDefinition 'Yanone EULA'>.keyword is a "
                    "required attribute, but empty"
                ),
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'>.fonts --> "
                    "<Font 'YanoneKaffeesatz-Regular'>.usedLicenses --> <LicenseUsage"
                    " 'yanoneEULA'> --> Has license 'yanoneEULA', but <Foundry "
                    "'Awesome Fonts'> has no matching license."
                ),
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'>.fonts --> <Font "
                    "'YanoneKaffeesatz-Bold'>.usedLicenses --> <LicenseUsage "
                    "'yanoneEULA'> --> Has license 'yanoneEULA', but <Foundry "
                    "'Awesome Fonts'> has no matching license."
                ),
            ],
        )

        i2 = copy.deepcopy(installableFonts)
        print(i2.foundries[0].licenses[0])
        assert i2.foundries[0].licenses[0].parent == i2.foundries[0]

    def test_Version(self):

        print("test_Version()")

        # description
        # is optional, so this will pass
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].families[0].versions[0].description.en = ""
        i2.foundries[0].families[0].versions[0].description.de = ""
        self.assertEqual(i2.validate()[2], [])

        # number
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].versions[0].number = "1.1.2.3"
        except ValueError as e:
            self.assertEqual(str(e), "1.1.2.3 is not valid SemVer string")

        # number
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].versions[0].number = "a"
        except ValueError as e:
            self.assertEqual(str(e), "False")

        # releaseDate
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].versions[0].releaseDate = "2010-20-21"
        except ValueError as e:
            self.assertEqual(
                str(e),
                "ValueError: time data '2010-20-21' does not match format '%Y-%m-%d'",
            )

        i2 = copy.deepcopy(installableFonts)
        print(i2.foundries[0].families[0].versions[0])
        assert i2.foundries[0].families[0].versions[0].isFontSpecific() is False
        assert (
            i2.foundries[0].families[0].versions[0].parent
            == i2.foundries[0].families[0]
        )
        assert i2.foundries[0].families[0].fonts[0].versions[0].isFontSpecific() is True
        assert (
            i2.foundries[0].families[0].fonts[0].versions[0].parent
            == i2.foundries[0].families[0].fonts[0]
        )

        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].filename(
                i2.foundries[0].families[0].fonts[0].getVersions()[-1]
            )
        except ValueError as e:
            self.assertEqual(str(e), "Supplied version must be str or int or float")

    def test_LicenseUsage(self):

        print("test_LicenseUsage()")

        # allowanceDescription
        # is optional, so this will pass
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].families[0].fonts[0].usedLicenses[
            0
        ].allowanceDescription.en = None
        self.assertEqual(i2.validate()[2], [])

        # dateAddedForUser
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].usedLicenses[
                0
            ].dateAddedForUser = "2010-20-21"
        except ValueError as e:
            self.assertEqual(
                str(e),
                "ValueError: time data '2010-20-21' does not match format '%Y-%m-%d'",
            )

        # keyword
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].families[0].fonts[0].usedLicenses[0].keyword = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'>.fonts --> <Font "
                    "'YanoneKaffeesatz-Regular'>.usedLicenses --> <LicenseUsage ''>."
                    "keyword is a required attribute, but empty"
                )
            ],
        )

        # seatsAllowed
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].usedLicenses[0].seatsAllowed = "5,0"
        except ValueError as e:
            self.assertEqual(str(e), "invalid literal for int() with base 10: '5,0'")
        # try the same, but modify the json string, the re-import
        json = installableFonts.dumpJSON()
        json = json.replace('"seatsAllowed": 5', '"seatsAllowed": "5,0"')
        try:
            i2.loadJSON(json)
        except ValueError as e:
            self.assertEqual(str(e), "invalid literal for int() with base 10: '5,0'")

        # seatsInstalled
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].usedLicenses[0].seatsInstalled = "1,0"
        except ValueError as e:
            self.assertEqual(str(e), "invalid literal for int() with base 10: '1,0'")

        # URL
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].usedLicenses[0].upgradeURL = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        i2 = copy.deepcopy(installableFonts)
        print(i2.foundries[0].families[0].fonts[0].usedLicenses[0])

    def test_FontPackage(self):

        print("test_FontPackage()")

        i2 = copy.deepcopy(installableFonts)
        print(i2.foundries[0].families[0].packages[0])

    def test_Font(self):

        print("test_Font()")

        # dateAddedForUser
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].dateFirstPublished = "2010-20-21"
        except ValueError as e:
            self.assertEqual(
                str(e),
                "ValueError: time data '2010-20-21' does not match format '%Y-%m-%d'",
            )

        # designers
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].families[0].fonts[0].designerKeywords = ["gfknlergerg"]
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'>.fonts --> <Font "
                    "'YanoneKaffeesatz-Regular'> --> Has designer 'gfknlergerg', but "
                    "<InstallableFontsResponse>.designers has no matching designer."
                )
            ],
        )

        # format
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].format = "abc"
        except ValueError as e:
            self.assertTrue("Unknown font extension: 'abc'." in str(e))

        # free
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].free = "True"
        except ValueError as e:
            self.assertEqual(
                str(e), "Wrong data type. Is <class 'str'>, should be: <class 'bool'>."
            )

        # name
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].families[0].fonts[0].name.en = ""
        i2.foundries[0].families[0].fonts[0].name.de = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'>.fonts --> <Font "
                    "'YanoneKaffeesatz-Regular'>.name is a required attribute, "
                    "but empty"
                )
            ],
        )

        # pdf
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].pdfURL = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        # postScriptName
        # TODO: write check for postScriptName
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].families[0].fonts[0].postScriptName = "YanoneKaffeesatzRegular"
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(validate[2], [])

        # protected
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].protected = "True"
        except ValueError as e:
            self.assertEqual(
                str(e), "Wrong data type. Is <class 'str'>, should be: <class 'bool'>."
            )

        # purpose
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].purpose = "anything"
        except ValueError as e:
            self.assertEqual(
                str(e),
                "Unknown font type: 'anything'. Possible: ['desktop', 'web', 'app']",
            )

        # status
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].status = "instable"
        except ValueError as e:
            self.assertEqual(
                str(e),
                (
                    "Unknown Font Status: 'instable'. Possible: ['prerelease', "
                    "'trial', 'stable']"
                ),
            )

        # uniqueID
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].families[0].fonts[0].uniqueID = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'>.fonts --> <Font "
                    "'YanoneKaffeesatz-Regular'>.uniqueID is a required attribute, "
                    "but empty"
                )
            ],
        )
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].families[0].fonts[0].uniqueID = "a" * 255
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'>.fonts --> <Font "
                    "'YanoneKaffeesatz-Regular'> --> The suggested file name is longer "
                    "than 220 characters: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                    "aaaaaaaaaaaa_1.0.otf"
                )
            ],
        )
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].families[0].fonts[0].uniqueID = "abc:def"
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'>.fonts --> <Font "
                    "'YanoneKaffeesatz-Regular'> --> .uniqueID must not contain the "
                    "character ':' because it will be used for the font’s file name "
                    "on disk."
                )
            ],
        )

        # usedLicenses
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].families[0].fonts[0].usedLicenses = []
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'>.fonts --> <Font "
                    "'YanoneKaffeesatz-Regular'>.usedLicenses is a required "
                    "attribute, but empty"
                )
            ],
        )
        try:
            i2.foundries[0].families[0].fonts[0].usedLicenses = ["hergerg"]
        except ValueError as e:
            self.assertEqual(
                str(e),
                (
                    "Wrong data type. Is <class 'str'>, should be: "
                    "<class 'typeworld.api.LicenseUsage'>."
                ),
            )

        # variableFont
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].variableFont = "True"
        except ValueError as e:
            self.assertEqual(
                str(e), "Wrong data type. Is <class 'str'>, should be: <class 'bool'>."
            )

        # versions
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].families[0].versions = []
        i2.foundries[0].families[0].fonts[0].versions = []
        try:
            validate = i2.validate()
        except ValueError as e:
            self.assertEqual(
                str(e),
                (
                    "<Font 'YanoneKaffeesatz-Regular'> has no version information, and "
                    "neither has its family <Family 'Yanone Kaffeesatz'>. Either one "
                    "needs to carry version information."
                ),
            )

        # other
        i2 = copy.deepcopy(installableFonts)
        print(i2.foundries[0].families[0].fonts[0])
        assert (
            i2.foundries[0].families[0].fonts[0].parent == i2.foundries[0].families[0]
        )
        assert type(i2.foundries[0].families[0].fonts[0].getDesigners()) == list

        # filename and purpose
        i2 = copy.deepcopy(installableFonts)
        self.assertEqual(
            i2.foundries[0]
            .families[0]
            .fonts[0]
            .filename(i2.foundries[0].families[0].fonts[0].getVersions()[-1].number),
            "yanone-kaffeesatz-regular_1.0.otf",
        )
        i2.foundries[0].families[0].fonts[0].format = ""
        self.assertEqual(
            i2.foundries[0]
            .families[0]
            .fonts[0]
            .filename(i2.foundries[0].families[0].fonts[0].getVersions()[-1].number),
            "yanone-kaffeesatz-regular_1.0",
        )
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'>.fonts --> <Font "
                    "'YanoneKaffeesatz-Regular'> --> Is a desktop font (see .purpose), "
                    "but has no .format value."
                )
            ],
        )

        # language support
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].languageSupport = {"LATN": ["DEU"]}
        except ValueError as e:
            self.assertEqual(
                str(e), "Script tag 'LATN' needs to be a four-letter lowercase tag."
            )
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].languageSupport = {"latn": ["de"]}
        except ValueError as e:
            self.assertEqual(
                str(e), "Language tag 'de' needs to be a three-letter uppercase tag."
            )

        # features
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].fonts[0].features = ["aal", "liga"]
        except ValueError as e:
            self.assertEqual(
                str(e),
                "OpenType feature tag 'aal' needs to be a four-letter lowercase tag.",
            )

    def test_Family(self):

        print("test_Family()")

        # billboardURLs
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].billboardURLs[0] = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        # dateFirstPublished
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].dateFirstPublished = "2010-20-21"
        except ValueError as e:
            self.assertEqual(
                str(e),
                "ValueError: time data '2010-20-21' does not match format '%Y-%m-%d'",
            )

        # description
        # allowed to be empty
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].families[0].description.en = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(validate[2], [])

        # designers
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].designerKeywords = "yanone"
        except ValueError as e:
            self.assertEqual(
                str(e), "Wrong data type. Is <class 'str'>, should be: <class 'list'>."
            )
        i2.foundries[0].families[0].designerKeywords = ["awieberg"]
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'Yanone Kaffeesatz'> --> Has designer "
                    "'awieberg', but <InstallableFontsResponse>.designers has no "
                    "matching designer."
                )
            ],
        )

        # galleryURL
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].galleryURL = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        # issueTrackerURL
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].issueTrackerURL = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        # name
        i2.foundries[0].families[0].name.en = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    ".families --> <Family 'None'>.name is a required attribute, "
                    "but empty"
                )
            ],
        )

        # pdf
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].pdfURL = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        # sourceURL
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].families[0].sourceURL = (
                "typeworldserver.com/?page=outputDataBaseFile&"
                "className=TWFS_FamilyBillboards&ID=2&field=image"
            )
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        # uniqueID
        # TODO

        # versions
        # already check at font level

        i2 = copy.deepcopy(installableFonts)
        print(i2.foundries[0].families[0])
        assert i2.foundries[0].families[0].parent == i2.foundries[0]
        assert type(i2.foundries[0].families[0].getDesigners()) == list
        assert type(i2.foundries[0].families[0].getAllDesigners()) == list

        # Package Names
        i2 = copy.deepcopy(installableFonts)

        self.assertEqual(
            i2.foundries[0].families[0].getPackages()[-1].name.de, "Desktop-Schriften"
        )
        self.assertEqual(
            i2.foundries[0].families[0].getPackages()[-1].name.en, "Desktop Fonts"
        )
        self.assertEqual(
            i2.foundries[0].families[0].getPackages()[-1].getFormats(), ["otf"]
        )

        self.assertEqual(
            i2.foundries[0].families[0].fonts[0].getPackageKeywords(), ["desktop"]
        )
        self.assertEqual(
            i2.foundries[0].families[0].fonts[1].getPackageKeywords(),
            [typeworld.api.DEFAULT],
        )

    def test_Foundry(self):

        print("test_Foundry()")

        # description
        # allowed to be empty
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].description.en = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(validate[2], [])

        # styling
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].styling = json.loads(
            """{"whatevs": {
            "headerColor": "F20D5E",
            "headerTextColor": "000000",
            "headerLinkColor": "E5F20D",

            "backgroundColor": "E5F20D",
            "textColor": "000000",
            "linkColor": "F7AD22",

            "selectionColor": "0D79F2",
            "selectionTextColor": "E5F20D",

            "buttonColor": "197AA3",
            "buttonTextColor": "FFFFFF",

            "informationViewBackgroundColor": "469BF5",
            "informationViewTextColor": "000000",
            "informationViewLinkColor": "E5F20D",

            "informationViewButtonColor": "E5F20D",
            "informationViewButtonTextColor": "000000"

        }, "dark": {
            "headerColor": "B10947",
            "headerTextColor": "000000",
            "headerLinkColor": "E5F20D",

            "backgroundColor": "1A1A1A",
            "textColor": "E5F20D",
            "linkColor": "C07F07",

            "selectionColor": "B10947",
            "selectionTextColor": "E5F20D",

            "buttonColor": "22A4DC",
            "buttonTextColor": "000000",

            "informationViewBackgroundColor": "000000",
            "informationViewTextColor": "999999",
            "informationViewLinkColor": "E5F20D",

            "informationViewButtonColor": "1E90C1",
            "informationViewButtonTextColor": "000000"

        } }"""
        )
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    " --> Styling keyword 'whatevs' is unknown. Known are "
                    "['light', 'dark']."
                )
            ],
        )

        # styling
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].styling = json.loads(
            """{"light": {
            "headerColor": "F20D5E",
            "headerTextColor": "000000",
            "headerLinkColor": "E5F20D",

            "backgroundColor": "E5F20D",
            "textColor": "000000",
            "linkColor": "F7AD22",

            "selectionColor": "0D79F2",
            "selectionTextColor": "E5F20D",

            "buttonColor": "197AA3",
            "buttonTextColor": "FFFFFF",

            "informationViewBackgroundColor": "469BF5",
            "informationViewTextColor": "000000",
            "informationViewLinkColor": "E5F20D",

            "informationViewButtonColor": "E5F20D",
            "informationViewButtonTextColor": "000000",

            "logoURL": "awesomefonts.com/logo.svg"

        }, "dark": {
            "headerColor": "B10947",
            "headerTextColor": "000000",
            "headerLinkColor": "E5F20D",

            "backgroundColor": "1A1A1A",
            "textColor": "E5F20D",
            "linkColor": "C07F07",

            "selectionColor": "B10947",
            "selectionTextColor": "E5F20D",

            "buttonColor": "22A4DC",
            "buttonTextColor": "000000",

            "informationViewBackgroundColor": "000000",
            "informationViewTextColor": "999999",
            "informationViewLinkColor": "E5F20D",

            "informationViewButtonColor": "1E90C1",
            "informationViewButtonTextColor": "000000"

        } }"""
        )
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    " --> .styling 'logoURL' attribute: Needs to start with http:// or "
                    "https://"
                )
            ],
        )

        # styling
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].styling = json.loads(
            """{"light": {
            "headerColor": "F20D5I",
            "headerTextColor": "000000",
            "headerLinkColor": "E5F20D",

            "backgroundColor": "E5F20D",
            "textColor": "000000",
            "linkColor": "F7AD22",

            "selectionColor": "0D79F2",
            "selectionTextColor": "E5F20D",

            "buttonColor": "197AA3",
            "buttonTextColor": "FFFFFF",

            "informationViewBackgroundColor": "469BF5",
            "informationViewTextColor": "000000",
            "informationViewLinkColor": "E5F20D",

            "informationViewButtonColor": "E5F20D",
            "informationViewButtonTextColor": "000000"

        }, "dark": {
            "headerColor": "B10947",
            "headerTextColor": "000000",
            "headerLinkColor": "E5F20D",

            "backgroundColor": "1A1A1A",
            "textColor": "E5F20D",
            "linkColor": "C07F07",

            "selectionColor": "B10947",
            "selectionTextColor": "E5F20D",

            "buttonColor": "22A4DC",
            "buttonTextColor": "000000",

            "informationViewBackgroundColor": "000000",
            "informationViewTextColor": "999999",
            "informationViewLinkColor": "E5F20D",

            "informationViewButtonColor": "1E90C1",
            "informationViewButtonTextColor": "000000"

        } }"""
        )
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'Awesome Fonts'>"
                    " --> .styling color attribute 'headerColor': Not a valid hex color"
                    " of format RRGGBB (like FF0000 for red): F20D5I"
                )
            ],
        )

        # email
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].email = "post_at_yanone.de"
        except ValueError as e:
            self.assertEqual(str(e), "Not a valid email format: post_at_yanone.de")

        # licenses
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].licenses = "yanoneEULA"
        except ValueError as e:
            self.assertEqual(
                str(e), "Wrong data type. Is <class 'str'>, should be: <class 'list'>."
            )

        # name
        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].name.en = ""
        i2.foundries[0].name.de = ""
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'None'>.name"
                    " is a required attribute, but empty"
                )
            ],
        )

        # supportEmail
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].supportEmail = "post_at_yanone.de"
        except ValueError as e:
            self.assertEqual(str(e), "Not a valid email format: post_at_yanone.de")

        # telephone
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].telephone = "+49176123456a456"
        except ValueError as e:
            self.assertEqual(
                str(e), "Needs to start with + and contain only numbers 0-9"
            )
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].telephone = "0049176123456456"
        except ValueError as e:
            self.assertEqual(
                str(e), "Needs to start with + and contain only numbers 0-9"
            )
        try:
            i2.foundries[0].telephone = "a"
        except ValueError as e:
            self.assertEqual(
                str(e), "Needs to start with + and contain only numbers 0-9"
            )

        # socialURLs
        self.assertEqual(
            str(foundry.socialURLs),
            "['https://facebook.com/pages/YanoneYanone', 'https://twitter.com/yanone']",
        )

        # website
        i2 = copy.deepcopy(installableFonts)
        try:
            i2.foundries[0].websiteURL = 1
        except ValueError as e:
            self.assertEqual(str(e), "Needs to start with http:// or https://")

        i2 = copy.deepcopy(installableFonts)
        print(i2.foundries[0])
        assert i2.foundries[0].name.getTextAndLocale("en") == ("Awesome Fonts", "en")
        assert i2.foundries[0].name.getTextAndLocale(["en"]) == ("Awesome Fonts", "en")
        assert i2.foundries[0].name.getTextAndLocale("de") == ("Tolle Schriften", "de")
        assert i2.foundries[0].name.getTextAndLocale(["de"]) == (
            "Tolle Schriften",
            "de",
        )
        assert i2.foundries[0].name.getTextAndLocale(["ar"]) == ("Awesome Fonts", "en")

        i2 = copy.deepcopy(installableFonts)
        i2.foundries[0].name.en = "abc" * 1000
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse>.foundries --> <Foundry 'abcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc"
                    "abcabcabcabcabc'>.name --> <MultiLanguageText> --> Language entry "
                    "'en' is too long. Allowed are 100 characters."
                )
            ],
        )

        i2 = copy.deepcopy(installableFonts)
        foundry2 = copy.deepcopy(i2.foundries[0])
        i2.foundries.append(foundry2)
        validate = i2.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallableFontsResponse> --> "
                    "Duplicate unique foundry IDs: ['yanone']"
                ),
                (
                    "<InstallableFontsResponse> --> "
                    "Duplicate unique family IDs: ['yanone-yanonekaffeesatz']"
                ),
                (
                    "<InstallableFontsResponse> --> Duplicate unique family IDs: "
                    "['yanone-kaffeesatz-regular', 'yanone-kaffeesatz-bold']"
                ),
            ],
        )

    def test_otherStuff(self):

        print("test_otherStuff()")

        # __repr__
        s = typeworld.api.StringDataType()
        s.value = "a"
        self.assertEqual(str(s), "<StringDataType 'a'>")

        assert type(root.supportedCommands.index("installableFonts")) == int
        assert installableFonts.designers[0].parent == installableFonts

        success, message = user1.client.rootCommand(protectedSubscription)
        self.assertTrue(success)

        success, message = user1.client.rootCommand(protectedSubscription[1:])
        self.assertFalse(success)
        self.assertEqual(message, "Unknown custom protocol, known are: ['typeworld']")

        user1.client.testScenario = "simulateInvalidAPIJSONResponse"
        success, message = user1.client.rootCommand(protectedSubscription)
        self.assertFalse(success)
        self.assertEqual(
            message,
            "Unknown license identifier: 'mefowefbhrf'. See https://spdx.org/licenses/",
        )

        user1.client.testScenario = "simulateFaultyAPIJSONResponse"
        success, message = user1.client.rootCommand(protectedSubscription)
        self.assertFalse(success)
        print(message)  # nocoverage
        self.assertTrue(
            "Invalid control character at: line 6 column 47 (char 225)" in message
        )

        # TODO: Invite user to subscription with API endpoint as source

        self.assertEqual(
            typeworld.client.helpers.addAttributeToURL(
                "https://type.world?hello=world#xyz", "hello=type&world=type"
            ),
            "https://type.world?hello=type&world=type#xyz",
        )

        # load json/dict
        d = {"en": "Hello World", "de": "Hallo Welt"}
        j = json.dumps(d)
        d1 = typeworld.api.MultiLanguageText(json=j).dumpDict()
        d2 = typeworld.api.MultiLanguageText(dict=d).dumpDict()
        from deepdiff import DeepDiff

        self.assertEqual(DeepDiff(d1, d2, ignore_order=True), {})

        # URL parsing and constructing
        success, protocol = typeworld.client.getProtocol(freeNamedSubscription)
        self.assertEqual(protocol.secretURL(), freeNamedSubscription)
        self.assertEqual(protocol.unsecretURL(), freeNamedSubscription)
        self.assertEqual(
            typeworld.client.URL(freeNamedSubscription).HTTPURL(),
            "https://typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/",
        )

        typeworld.client.helpers.Garbage(
            20, uppercase=True, lowercase=True, numbers=True, punctuation=True
        )

    def test_InstallFontsResponse(self):

        print("test_InstallFontsResponse()")

        installFonts = InstallFontsResponse()
        asset = InstallFontAsset()
        installFonts.assets.append(asset)
        asset.uniqueID = "abc"
        asset.response = "success"
        asset.mimeType = "font/otf"
        # 		asset.encoding = 'base64' # missing
        asset.data = b"ABC"
        validate = asset.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            ["<InstallFontAsset> --> .data is set, but .encoding is missing"],
        )

        installFonts = InstallFontsResponse()
        asset = InstallFontAsset()
        installFonts.assets.append(asset)
        asset.uniqueID = "abc"
        asset.response = "success"
        asset.encoding = "base64"
        # 		asset.mimeType = 'font/otf' # missing
        asset.data = b"ABC"
        validate = asset.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            ["<InstallFontAsset> --> .data is set, but .mimeType is missing"],
        )

        installFonts = InstallFontsResponse()
        asset = InstallFontAsset()
        installFonts.assets.append(asset)
        asset.uniqueID = "abc"
        asset.response = "success"
        asset.encoding = "base64"
        # 		asset.mimeType = 'font/otf' # missing
        asset.dataURL = "https://awesomefonts.com/font.otf"
        validate = asset.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            ["<InstallFontAsset> --> .dataURL is set, but .mimeType is missing"],
        )

        installFonts = InstallFontsResponse()
        asset = InstallFontAsset()
        installFonts.assets.append(asset)
        asset.uniqueID = "abc"
        asset.response = "success"
        asset.encoding = "base64"
        asset.mimeType = "font/otf"  # missing
        asset.dataURL = "https://awesomefonts.com/font.otf"
        asset.data = b"ABC"
        validate = asset.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallFontAsset> --> "
                    "Either .dataURL or .data can be defined, not both"
                )
            ],
        )

        installFonts = InstallFontsResponse()
        asset = InstallFontAsset()
        installFonts.assets.append(asset)
        asset.uniqueID = "abc"
        asset.response = "success"
        asset.mimeType = "font/otf"
        asset.encoding = "base64"
        # 		asset.data = b'ABC' # missing
        validate = asset.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallFontAsset> --> .response is set to success, but neither "
                    ".data nor .dataURL are set."
                )
            ],
        )

        installFonts = InstallFontsResponse()
        asset = InstallFontAsset()
        installFonts.assets.append(asset)
        asset.uniqueID = "abc"
        asset.mimeType = "font/otf"
        asset.response = "error"
        validate = asset.validate()
        print(validate[2])
        self.assertEqual(
            validate[2],
            [
                (
                    "<InstallFontAsset> --> .response is 'error', "
                    "but .errorMessage is missing."
                )
            ],
        )

        installFonts = InstallFontsResponse()
        asset = InstallFontAsset()
        try:
            asset.mimeType = "font/whatevs"
        except ValueError as e:
            self.assertEqual(
                str(e),
                (
                    "Unknown font MIME Type: 'font/whatevs'. Possible: "
                    "['font/collection', 'font/otf', 'font/sfnt', 'font/ttf']"
                ),
            )

        asset = InstallFontAsset()
        try:
            asset.response = "a"
        except ValueError as e:
            self.assertEqual(
                str(e),
                (
                    "Unknown response type: 'a'. Possible: ['success', 'error', "
                    "'unknownFont', 'insufficientPermission', "
                    "'temporarilyUnavailable', 'validTypeWorldUserAccountRequired', "
                    "'loginRequired', 'revealedUserIdentityRequired', "
                    "'seatAllowanceReached']"
                ),
            )

    def test_UninstallFontsResponse(self):

        print("test_UninstallFontsResponse()")

        asset = UninstallFontAsset()
        try:
            asset.response = "a"
        except ValueError as e:
            self.assertEqual(
                str(e),
                (
                    "Unknown response type: 'a'. Possible: ['success', 'error', "
                    "'unknownFont', 'insufficientPermission', "
                    "'temporarilyUnavailable', 'validTypeWorldUserAccountRequired', "
                    "'loginRequired', 'unknownInstallation']"
                ),
            )

    def test_InstallableFontsResponse_Old(self):

        # DOCU
        RootResponse().docu()
        EndpointResponse().docu()
        InstallableFontsResponse().docu()
        InstallFontsResponse().docu()
        UninstallFontsResponse().docu()

        # Data types
        try:
            BooleanDataType().put("abc")
        except ValueError:
            pass

        try:
            IntegerDataType().put("abc")
        except ValueError:
            pass

        try:
            FloatDataType().put("abc")
        except ValueError:
            pass

        FontEncodingDataType().valid()
        try:
            FontEncodingDataType().put("abc")
        except ValueError:
            pass

        try:
            VersionDataType().put("0.1.2.3")
        except ValueError:
            pass

        try:
            WebURLDataType().put("yanone.de")
        except ValueError:
            pass

        try:
            EmailDataType().put("post@yanone")
        except ValueError:
            pass

        try:
            HexColorDataType().put("ABCDEF")  # pass
            HexColorDataType().put("ABCDEX")  # error
        except ValueError:
            pass

        try:
            HexColorDataType().put("012345678")
        except ValueError:
            pass

        try:
            DateDataType().put("2018-02-28")  # pass
            DateDataType().put("2018-02-30")  # error
        except ValueError:
            pass

        text = MultiLanguageText()
        self.assertEqual(
            text.customValidation()[2], ["Needs to contain at least one language field"]
        )
        self.assertEqual(bool(text), False)
        text.en = "Hello"
        self.assertEqual(bool(text), True)

        text.en = "Hello"
        self.assertEqual(text.customValidation()[2], [])

        # HTML in Text
        text.en = "Hello, <b>world</b>"
        self.assertNotEqual(text.customValidation()[2], [])

        # Markdown in Text
        text.en = "Hello, _world_"
        self.assertNotEqual(text.customValidation()[2], [])

        description = MultiLanguageLongText()
        self.assertEqual(bool(description), False)
        description.en = "Hello"
        self.assertEqual(bool(description), True)

        description.en = "Hello"
        self.assertEqual(description.customValidation()[2], [])

        # HTML in Text
        description.en = "Hello, <b>world</b>"
        self.assertNotEqual(description.customValidation()[2], [])

        # Markdown in Text
        description.en = "Hello, _world_"
        self.assertEqual(description.customValidation()[2], [])

        i2 = copy.deepcopy(installableFonts)
        font = i2.foundries[0].families[0].fonts[0]

        # __repr__
        print(font.uniqueID)

        _list = FontListProxy()
        print(_list)
        _list.append(Font())
        _list[0] = Font()

        _list = font.nonListProxyBasedKeys()

        font.doesntHaveThisAttribute = "a"
        print(font.doesntHaveThisAttribute)
        try:
            print(font.doesntHaveThatAttribute)
        except AttributeError:
            pass

        font.postScriptName = ""

        font.name = MultiLanguageText()
        font.name.en = None
        print(font.name.parent)
        # try:
        print(installableFonts.validate())
        # except:
        # 	pass

        usedLicense = LicenseUsage()
        usedLicense.keyword = "awesomeFontsEULAAAAA"
        font.usedLicenses.append(usedLicense)
        # try:
        print(installableFonts.validate())
        # except:
        # 	pass

        font.versions = []
        font.parent.versions = []
        # try:
        print(installableFonts.validate())
        # except:
        # 	pass

        font.designerKeywords.append("maxx")
        # try:
        print(installableFonts.validate())
        # except:
        # 	pass

    def test_helpers(self):

        print("test_helpers()")

        # makeSemVer(a.number)
        self.assertEqual(makeSemVer(2.1), "2.1.0")

        # urlIsValid()
        self.assertEqual(
            typeworld.client.urlIsValid(
                (
                    "typeworld://json+https//s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm"
                    "@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
                )
            )[0],
            True,
        )
        self.assertEqual(
            typeworld.client.urlIsValid(
                (
                    "https//s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm"
                    "@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
                )
            )[0],
            False,
        )
        self.assertEqual(
            typeworld.client.urlIsValid(
                (
                    "typeworldjson://json+https//s9lWvayTEOaB9eIIMA67:"
                    "bN0QnnNsaE4LfHlOMGkm@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
                )
            )[0],
            False,
        )

        # splitJSONURL()
        self.assertEqual(
            typeworld.client.splitJSONURL(
                (
                    "typeworld://json+https//s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm"
                    ":accessToken@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
                )
            ),
            (
                "typeworld://",
                "json",
                "https://",
                "s9lWvayTEOaB9eIIMA67",
                "bN0QnnNsaE4LfHlOMGkm",
                "accessToken",
                "typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/",
            ),
        )
        self.assertEqual(
            typeworld.client.splitJSONURL(
                (
                    "typeworld://json+https//s9lWvayTEOaB9eIIMA67@"
                    "typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
                )
            ),
            (
                "typeworld://",
                "json",
                "https://",
                "s9lWvayTEOaB9eIIMA67",
                "",
                "",
                "typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/",
            ),
        )
        self.assertEqual(
            typeworld.client.splitJSONURL(
                "typeworld://json+https//typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
            ),
            (
                "typeworld://",
                "json",
                "https://",
                "",
                "",
                "",
                "typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/",
            ),
        )
        self.assertEqual(
            typeworld.client.splitJSONURL(
                "typeworld://json+http//typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
            ),
            (
                "typeworld://",
                "json",
                "http://",
                "",
                "",
                "",
                "typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/",
            ),
        )

        if ONLINE:
            # Locale
            self.assertTrue("en" in user0.client.locale())
            user0.client.set("localizationType", "systemLocale")
            self.assertTrue("en" in user0.client.locale())
            user0.client.set("localizationType", "customLocale")
            self.assertTrue("en" in user0.client.locale())
            user0.client.set("customLocaleChoice", "de")
            self.assertEqual(user0.client.locale(), ["de", "en"])

        from typeworld.client.helpers import addAttributeToURL

        self.assertEqual(
            addAttributeToURL("https://type.world/", "hello=world"),
            "https://type.world/?hello=world",
        )
        self.assertEqual(
            addAttributeToURL("https://type.world/?foo=bar", "hello=world"),
            "https://type.world/?foo=bar&hello=world",
        )

    def test_simulateExternalScenarios(self):

        print("test_simulateExternalScenarios()")

        user0.takeDown()

        user0.client.testScenario = "simulateEndpointDoesntSupportInstallFontCommand"
        success, message, publisher, subscription = user0.client.addSubscription(
            freeSubscription
        )
        self.assertEqual(success, False)

        user0.client.testScenario = (
            "simulateEndpointDoesntSupportInstallableFontsCommand"
        )
        success, message, publisher, subscription = user0.client.addSubscription(
            freeSubscription
        )
        self.assertEqual(success, False)

        user0.client.testScenario = "simulateCustomError"
        success, message, publisher, subscription = user0.client.addSubscription(
            freeSubscription
        )
        self.assertEqual(success, False)
        self.assertEqual(message.getText(), "simulateCustomError")

        user0.client.testScenario = "simulateNotOnline"
        success, message, publisher, subscription = user0.client.addSubscription(
            freeSubscription
        )
        self.assertEqual(success, False)

        user0.client.testScenario = "simulateProgrammingError"
        success, message, publisher, subscription = user0.client.addSubscription(
            freeSubscription
        )
        self.assertEqual(success, False)
        self.assertEqual(
            message,
            (
                "Connection refused: "
                "https://typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
            ),
        )

        success, message, publisher, subscription = user0.client.addSubscription(
            (
                "typeworld://unknownprotocol+"
                "https//typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
            )
        )
        self.assertEqual(success, False)
        self.assertEqual(
            message, "Protocol unknownprotocol doesn’t exist in this app (yet)."
        )

        success, message, publisher, subscription = user0.client.addSubscription(
            (
                "typeworld://json+https://s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@"
                "typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/@"
            )
        )
        self.assertEqual(success, False)
        self.assertEqual(
            message, "URL contains more than one @ sign, so don’t know how to parse it."
        )

        success, message, publisher, subscription = user0.client.addSubscription(
            (
                "typeworldjson://json+https://s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm"
                "@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
            )
        )
        self.assertEqual(success, False)
        self.assertEqual(message, "Unknown custom protocol, known are: ['typeworld']")

        success, message, publisher, subscription = user0.client.addSubscription(
            (
                "typeworldjson//json+https://s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm"
                "@typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
            )
        )
        self.assertEqual(success, False)
        self.assertEqual(message, "Unknown custom protocol, known are: ['typeworld']")

        success, message, publisher, subscription = user0.client.addSubscription(
            (
                "typeworld://json+https://s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@"
                "typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/:"
            )
        )
        self.assertEqual(success, False)
        self.assertEqual(
            message,
            (
                "URL contains more than one :// combination, "
                "so don’t know how to parse it."
            ),
        )

        success, message, publisher, subscription = user0.client.addSubscription(
            (
                "typeworld://json+s9lWvayTEOaB9eIIMA67:bN0QnnNsaE4LfHlOMGkm@"
                "typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
            )
        )
        self.assertEqual(success, False)
        self.assertEqual(message, "URL is malformed.")

    def test_normalSubscription(self):

        print("test_normalSubscription() started...")

        # Reset Test Conditions
        request = urllib.request.Request(
            "https://typeworldserver.com/resetTestConditions"
        )
        response = urllib.request.urlopen(request, context=sslcontext).read()
        print(response)

        self.assertTrue(
            user0.client.online(MOTHERSHIP.split("//")[1].split("/")[0].split(":")[0])
        )

        self.assertTrue(user2.client.user())

        # verifyCredentials without subscriptionURL
        parameters = {
            "anonymousAppID": user2.client.anonymousAppID(),
            "anonymousTypeWorldUserID": user2.client.user(),
            "APIKey": "I3ZYbDwYgG3S7lpOGI6LjEylQWt6tPS7MJtN1d3T",
            "testing": "true",
        }
        success, response = performRequest(
            MOTHERSHIP + "/verifyCredentials", parameters, sslcontext
        )
        self.assertEqual(success, True)
        response = json.loads(response.read().decode())
        self.assertEqual(response["response"], "success")

        # # Load subscription with offline client
        # userOffline = User(online = False)
        # result = userOffline.client.addSubscription(freeSubscription)
        # print(result)
        # success, message, publisher, subscription = result
        # self.assertEqual(success, True)

        # General stuff
        self.assertEqual(type(user0.client.locale()), list)
        self.assertTrue(typeworld.client.urlIsValid(freeSubscription)[0])

        # Scenario 1:
        # Test a simple subscription of free fonts without Type.World user account

        result = user0.client.addSubscription(freeSubscription)
        print("Scenario 1:", result)
        success, message, publisher, subscription = result
        self.assertEqual(success, True)
        self.assertEqual(
            user0.client.publishers()[0].canonicalURL,
            "https://typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/",
        )
        self.assertEqual(len(user0.client.publishers()[0].subscriptions()), 1)
        self.assertEqual(
            len(
                user0.client.publishers()[0]
                .subscriptions()[-1]
                .protocol.installableFontsCommand()[1]
                .foundries
            ),
            1,
        )
        self.assertEqual(
            user0.client.publishers()[0]
            .subscriptions()[-1]
            .protocol.installableFontsCommand()[1]
            .foundries[0]
            .name.getTextAndLocale(),
            ("Test Foundry", "en"),
        )

        self.assertFalse(subscription.hasProtectedFonts())

        self.assertEqual(
            user0.client.publishers()[0].subscriptions()[-1].protocol.protocolName(),
            "Type.World JSON Protocol",
        )

        # Name
        self.assertEqual(
            user0.client.publishers()[0].name()[0], "Test Publisher (Don’t Touch)"
        )
        self.assertEqual(
            user0.client.publishers()[0].subscriptions()[0].name(), "Free Fonts"
        )

        # Reload client
        # Equal to closing the app and re-opening,
        # so code gets loaded from disk/defaults
        user0.loadClient()

        user0.clearSubscriptions()

        # Flat subscription
        result = user0.client.addSubscription(flatFreeSubscription)
        success, message, publisher, subscription = result
        if not success:
            print(message)  # nocoverage
        self.assertEqual(success, True)

        data = user0.client.get(f"subscription({flatFreeSubscription})")["data"]
        self.assertTrue("installFonts" in data and data["installFonts"])
        i = typeworld.api.InstallFontsResponse()
        i.loadJSON(data["installFonts"])
        self.assertEqual(i.validate()[2], [])

        # Update Flat subscription
        result = user0.client.publishers()[0].subscriptions()[0].update()
        success, message, changed = result
        self.assertEqual(success, True)

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        # Install All 4 Fonts
        user0.client.publishers()[0].subscriptions()[0].set(
            "acceptedTermsOfService", True
        )
        fonts = [[x.uniqueID, x.getVersions()[-1].number] for x in user0.testFonts()]
        success, message = (
            user0.client.publishers()[0].subscriptions()[0].installFonts(fonts)
        )
        if not success:
            print(message)  # nocoverage
        self.assertEqual(success, True)
        self.assertEqual(
            user0.client.publishers()[0].subscriptions()[0].amountInstalledFonts(), 4
        )

        # Remove Font
        user0.client.testScenario = "simulateNoPath"
        success, message = (
            user0.client.publishers()[0]
            .subscriptions()[0]
            .removeFonts([user0.testFont().uniqueID])
        )
        if not success:
            print(message)  # nocoverage
        self.assertEqual(success, False)

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        # Remove all 4 fonts
        user0.client.testScenario = None
        fonts = [x.uniqueID for x in user0.testFonts()]
        success, message = (
            user0.client.publishers()[0].subscriptions()[0].removeFonts(fonts)
        )
        if not success:
            print(message)  # nocoverage
        self.assertEqual(success, True)
        self.assertEqual(
            user0.client.publishers()[0].subscriptions()[0].amountInstalledFonts(), 0
        )

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        user0.loadClient()

        user0.clearSubscriptions()

        # #

        # Scenario 2:
        # Protected subscription, installation on machine without user account
        # This is supposed to fail because accessing protected subscriptions requires
        # a valid Type.World user account, but user0 is not linked with a user account
        result = user0.client.addSubscription(protectedSubscription)
        print("Scenario 2:", result)
        success, message, publisher, subscription = result
        self.assertEqual(success, False)
        self.assertEqual(
            message,
            [
                "#(response.validTypeWorldUserAccountRequired)",
                "#(response.validTypeWorldUserAccountRequired.headline)",
            ],
        )

        # #

        # verifyCredentials with subscriptionURL
        parameters = {
            "anonymousAppID": user1.client.anonymousAppID(),
            "anonymousTypeWorldUserID": user1.client.user(),
            "APIKey": "I3ZYbDwYgG3S7lpOGI6LjEylQWt6tPS7MJtN1d3T",
            "subscriptionURL": protectedSubscriptionWithoutAccessToken,
            "testing": "true",
        }
        success, response = performRequest(
            MOTHERSHIP + "/verifyCredentials", parameters, sslcontext
        )
        print(success, response)
        self.assertEqual(success, True)
        response = json.loads(response.read().decode())
        print(response)
        self.assertEqual(response["response"], "invalid")

        # Scenario 3:
        # Protected subscription,
        # installation on first machine with Type.World user account
        result = user1.client.addSubscription(protectedSubscription)
        print("Scenario 3:", result)
        success, message, publisher, subscription = result
        print("Message:", message)

        self.assertEqual(success, True)
        self.assertEqual(len(user1.client.publishers()[0].subscriptions()), 1)
        self.assertEqual(
            len(
                user1.client.publishers()[0]
                .subscriptions()[-1]
                .protocol.installableFontsCommand()[1]
                .foundries
            ),
            1,
        )
        self.assertTrue(subscription.hasProtectedFonts())

        # verifyCredentials with subscriptionURL
        parameters = {
            "anonymousAppID": user1.client.anonymousAppID(),
            "anonymousTypeWorldUserID": user1.client.user(),
            "APIKey": "I3ZYbDwYgG3S7lpOGI6LjEylQWt6tPS7MJtN1d3T",
            "subscriptionURL": protectedSubscriptionWithoutAccessToken,
            "testing": "true",
        }
        success, response = performRequest(
            MOTHERSHIP + "/verifyCredentials", parameters, sslcontext
        )
        self.assertEqual(success, True)
        response = json.loads(response.read().decode())
        print(response)
        self.assertEqual(response["response"], "success")

        # verifyCredentials with subscriptionURL
        parameters = {
            "anonymousAppID": user1.client.anonymousAppID(),
            "anonymousTypeWorldUserID": user1.client.user(),
            "APIKey": "I3ZYbDwYgG3S7lpOGI6LjEylQWt6tPS7MJtN1d3T",
            "subscriptionURL": protectedSubscriptionWithoutAccessToken.replace(
                "@", "a@"
            ),  # change URL slightly
            "testing": "true",
        }
        success, response = performRequest(
            MOTHERSHIP + "/verifyCredentials", parameters, sslcontext
        )
        self.assertEqual(success, True)
        response = json.loads(response.read().decode())
        print(response)
        self.assertEqual(response["response"], "invalid")

        # Clear
        user1.clearSubscriptions()

        # verifyCredentials with subscriptionURL
        parameters = {
            "anonymousAppID": user1.client.anonymousAppID(),
            "anonymousTypeWorldUserID": user1.client.user(),
            "APIKey": "I3ZYbDwYgG3S7lpOGI6LjEylQWt6tPS7MJtN1d3T",
            "subscriptionURL": protectedSubscriptionWithoutAccessToken,
            "testing": "true",
        }
        success, response = performRequest(
            MOTHERSHIP + "/verifyCredentials", parameters, sslcontext
        )
        self.assertEqual(success, True)
        response = json.loads(response.read().decode())
        print(response)
        self.assertEqual(response["response"], "invalid")

        # Re-add subscription
        result = user1.client.addSubscription(protectedSubscription)
        success, message, publisher, subscription = result
        self.assertEqual(success, True)

        # verifyCredentials with subscriptionURL
        parameters = {
            "anonymousAppID": user1.client.anonymousAppID(),
            "anonymousTypeWorldUserID": user1.client.user(),
            "APIKey": "I3ZYbDwYgG3S7lpOGI6LjEylQWt6tPS7MJtN1d3T",
            "subscriptionURL": protectedSubscriptionWithoutAccessToken,
            "testing": "true",
        }
        success, response = performRequest(
            MOTHERSHIP + "/verifyCredentials", parameters, sslcontext
        )
        self.assertEqual(success, True)
        response = json.loads(response.read().decode())
        print(response)
        self.assertEqual(response["response"], "success")

        # verifyCredentials without subscriptionURL
        parameters = {
            "subscriptionURL": protectedSubscriptionWithoutAccessToken,
            "APIKey": "I3ZYbDwYgG3S7lpOGI6LjEylQWt6tPS7MJtN1d3T",
            "testing": "true",
        }
        success, response = performRequest(
            MOTHERSHIP + "/updateSubscription", parameters, sslcontext
        )
        self.assertEqual(success, True)
        response = json.loads(response.read().decode())
        self.assertEqual(response["response"], "success")

        time.sleep(5)

        # Protocol
        success, protocol = typeworld.client.getProtocol(protectedSubscription)
        self.assertEqual(protocol.secretURL(), protectedSubscriptionWithoutAccessToken)
        self.assertEqual(
            protocol.unsecretURL(),
            protectedSubscriptionWithoutAccessToken.replace(
                ":OxObIWDJjW95SkeL3BNr@", ":secretKey@"
            ),
        )

        # saveURL
        self.assertEqual(
            user1.client.publishers()[0].subscriptions()[-1].protocol.unsecretURL(),
            (
                "typeworld://json+https//s9lWvayTEOaB9eIIMA67:secretKey@"
                "typeworldserver.com/api/q8JZfYn9olyUvcCOiqHq/"
            ),
        )
        # completeURL
        self.assertEqual(
            user1.client.publishers()[0].subscriptions()[-1].protocol.secretURL(),
            protectedSubscriptionWithoutAccessToken,
        )

        # Reload client
        # Equal to closing the app and re-opening, so code gets
        # loaded from disk/defaults
        user1.loadClient()
        self.assertEqual(
            user1.client.publishers()[0].subscriptions()[-1].protocol.secretURL(),
            protectedSubscriptionWithoutAccessToken,
        )

        user1.client.testScenario = "simulateCentralServerNotReachable"
        user1.client.publishers()[0].subscriptions()[0].stillAlive()
        user1.client.testScenario = "simulateCentralServerProgrammingError"
        user1.client.publishers()[0].subscriptions()[0].stillAlive()
        user1.client.testScenario = "simulateCentralServerErrorInResponse"
        user1.client.publishers()[0].subscriptions()[0].stillAlive()
        user1.client.testScenario = "simulateNotOnline"
        user1.client.publishers()[0].subscriptions()[0].stillAlive()
        user1.client.testScenario = None
        user1.client.publishers()[0].subscriptions()[0].stillAlive()

        user1.client.testScenario = "simulateFaultyClientVersion"
        success, message = user1.client.downloadSubscriptions()
        self.assertEqual(success, False)
        self.assertEqual(
            message,
            [
                "#(response.clientVersionInvalid)",
                "#(response.clientVersionInvalid.headline)",
            ],
        )

        user1.client.testScenario = "simulateNoClientVersion"
        success, message = user1.client.downloadSubscriptions()
        self.assertEqual(success, False)
        self.assertEqual(
            message,
            [
                "#(response.Required parameter clientVersion is missing.)",
                "#(response.Required parameter clientVersion is missing..headline)",
            ],
        )

        user1.client.testScenario = "simulateCentralServerNotReachable"
        self.assertEqual(user1.client.downloadSubscriptions()[0], False)
        user1.client.testScenario = "simulateCentralServerProgrammingError"
        self.assertEqual(user1.client.downloadSubscriptions()[0], False)
        user1.client.testScenario = "simulateCentralServerErrorInResponse"
        self.assertEqual(user1.client.downloadSubscriptions()[0], False)
        user1.client.testScenario = "simulateNotOnline"
        self.assertEqual(user1.client.downloadSubscriptions()[0], False)
        user1.client.testScenario = None
        self.assertEqual(user1.client.downloadSubscriptions()[0], True)
        success, message, changes = user1.client.publishers()[0].update()
        print("Updating publisher:", success, message, changes)
        self.assertEqual(success, True)
        self.assertEqual(changes, False)
        success, message, changes = (
            user1.client.publishers()[0].subscriptions()[0].update()
        )
        print("Updating subscription 1:", success, message, changes)
        self.assertEqual(success, True)
        self.assertEqual(changes, False)
        self.assertEqual(user1.client.publishers()[0].stillUpdating(), False)
        self.assertEqual(
            user1.client.publishers()[0].subscriptions()[0].stillUpdating(), False
        )
        print(user1.client.publishers()[0].updatingProblem())
        self.assertEqual(user1.client.allSubscriptionsUpdated(), True)

        # Install Font
        # First it's meant to fail because the user hasn't
        # accepted the Terms & Conditions
        self.assertEqual(
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number]]
            ),
            (
                False,
                [
                    "#(response.termsOfServiceNotAccepted)",
                    "#(response.termsOfServiceNotAccepted.headline)",
                ],
            ),
        )
        user1.client.publishers()[0].subscriptions()[-1].set(
            "acceptedTermsOfService", True
        )
        # Then it's supposed to fail because the server requires the revealted user
        # identity for this subscription
        self.assertEqual(
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .protocol.installableFontsCommand()[1]
            .prefersRevealedUserIdentity,
            True,
        )
        self.assertEqual(
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number]]
            ),
            (
                False,
                [
                    "#(response.revealedUserIdentityRequired)",
                    "#(response.revealedUserIdentityRequired.headline)",
                ],
            ),
        )
        user1.client.publishers()[0].subscriptions()[-1].set("revealIdentity", True)

        # Finally supposed to pass
        self.assertEqual(
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number]]
            ),
            (True, None),
        )
        self.assertEqual(user1.client.publishers()[0].amountInstalledFonts(), 1)
        self.assertEqual(
            user1.client.publishers()[0].subscriptions()[0].amountInstalledFonts(), 1
        )

        # Test for version
        self.assertEqual(
            user1.client.publishers()[0]
            .subscriptions()[0]
            .installedFontVersion(fontID=user1.testFont().uniqueID),
            user1.testFont().getVersions()[-1].number,
        )
        self.assertEqual(
            user1.client.publishers()[0]
            .subscriptions()[0]
            .installedFontVersion(font=user1.testFont()),
            user1.testFont().getVersions()[-1].number,
        )

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        # Simulations
        user1.client.testScenario = "simulateNotOnline"
        success, message, changes = user1.client.publishers()[0].update()
        self.assertEqual(success, False)
        success, message, changes = (
            user1.client.publishers()[0].subscriptions()[0].update()
        )
        self.assertEqual(success, False)
        user1.client.testScenario = "simulateProgrammingError"
        success, message, changes = user1.client.publishers()[0].update()
        self.assertEqual(success, False)
        success, message, changes = (
            user1.client.publishers()[0].subscriptions()[0].update()
        )
        self.assertEqual(success, False)
        user1.client.testScenario = "simulateInsufficientPermissions"
        success, message, changes = user1.client.publishers()[0].update()
        self.assertEqual(success, False)
        success, message, changes = (
            user1.client.publishers()[0].subscriptions()[0].update()
        )
        self.assertEqual(success, False)
        user1.client.testScenario = "simulateCustomError"
        success, message, changes = user1.client.publishers()[0].update()
        self.assertEqual(success, False)
        self.assertEqual(message.getText(), "simulateCustomError")
        success, message, changes = (
            user1.client.publishers()[0].subscriptions()[0].update()
        )
        self.assertEqual(success, False)
        self.assertEqual(message.getText(), "simulateCustomError")

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        # Uninstall font here
        user1.client.testScenario = None
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .removeFonts([user1.testFont().uniqueID])
        )
        if success is False:
            print("Uninstall font:", message)  # nocoverage
        self.assertEqual(success, True)

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        # Repeat font installation
        user1.client.testScenario = "simulateLoginRequired"
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number]]
            )
        )
        if success is False:
            print(message)  # nocoverage
        self.assertEqual(success, False)
        self.assertEqual(
            message, ["#(response.loginRequired)", "#(response.loginRequired.headline)"]
        )

        # Repeat font installation
        user1.client.testScenario = "simulateProgrammingError"
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number]]
            )
        )
        if not success:
            print(message)  # nocoverage
        self.assertEqual(success, False)

        user1.client.testScenario = "simulatePermissionError"
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number]]
            )
        )
        if not success:
            print(message)  # nocoverage
        self.assertEqual(success, False)

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        user1.client.testScenario = "simulateCustomError"
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number]]
            )
        )
        if not success:
            print(message)  # nocoverage
        self.assertEqual(success, False)
        self.assertEqual(message.getText(), "simulateCustomError")

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        user1.client.testScenario = "simulateInsufficientPermissions"
        publisher = user1.client.publishers()[0]
        subscription = publisher.subscriptions()[-1]
        print(user1.testFont().getVersions())
        success, message = subscription.installFonts(
            [[user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number]]
        )
        if not success:
            print(message)  # nocoverage
        self.assertEqual(success, False)

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        # Supposed to pass
        user1.client.testScenario = None
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number]]
            )
        )
        if not success:
            print(message)  # nocoverage
        self.assertEqual(success, True)
        self.assertEqual(user1.client.publishers()[0].amountInstalledFonts(), 1)
        self.assertEqual(
            user1.client.publishers()[0].subscriptions()[0].amountInstalledFonts(), 1
        )

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        # Simulate unexpected empty subscription
        user1.client.testScenario = "simulateNoFontsAvailable"
        success, message, changes = (
            user1.client.publishers()[0].subscriptions()[0].update()
        )
        print("Updating subscription 2:", success, message, changes)
        self.assertEqual(success, True)
        self.assertEqual(changes, True)
        self.assertEqual(
            user1.client.publishers()[0].subscriptions()[0].amountInstalledFonts(), 0
        )
        user1.client.testScenario = None
        success, message, changes = (
            user1.client.publishers()[0].subscriptions()[0].update()
        )

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        # Install font again
        user1.client.testScenario = None
        self.assertEqual(
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number]]
            ),
            (True, None),
        )

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        self.assertEqual(user1.client.publishers()[0].amountInstalledFonts(), 1)
        self.assertEqual(
            user1.client.publishers()[0].subscriptions()[0].amountInstalledFonts(), 1
        )
        self.assertEqual(len(user1.client.publishers()), 1)
        self.assertEqual(len(user1.client.publishers()[0].subscriptions()), 1)

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        # Remove font again
        user1.client.testScenario = None
        self.assertEqual(
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .removeFonts([user1.testFont().uniqueID]),
            (True, None),
        )

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        # linkedAppInstances
        success, instances = user1.client.linkedAppInstances()
        self.assertEqual(success, True)
        self.assertTrue(len(instances) >= 1)

        # Revoke app instance
        success, response = user1.client.revokeAppInstance(
            user1.client.anonymousAppID()
        )
        if not success:
            print(response)
        self.assertEqual(success, True)

        # Save test font's uniqueID and version for later
        testFontID = user1.testFont().uniqueID
        testFontVersion = user1.testFont().getVersions()[-1].number

        print("\nLine %s" % getframeinfo(currentframe()).lineno)

        # Can't access app instances information while revoked
        success, response = user1.client.linkedAppInstances()
        self.assertEqual(
            response,
            [
                "#(response.appInstanceRevoked)",
                "#(response.appInstanceRevoked.headline)",
            ],
        )

        # Update subscriptions
        success, message, changed = (
            user1.client.publishers()[0].subscriptions()[-1].update()
        )
        self.assertEqual(success, True)

        # Reinstall font, fails because no permissions
        user1.client.testScenario = None
        response = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts([[testFontID, testFontVersion]])
        )
        success, message = response
        print(response)
        self.assertEqual(success, False)
        self.assertEqual(
            message,
            [
                "#(response.insufficientPermission)",
                "#(response.insufficientPermission.headline)",
            ],
        )

        # Reactivate app instance
        success, response = user1.client.reactivateAppInstance(
            user1.client.anonymousAppID()
        )
        if not success:
            print(response)
        self.assertEqual(success, True)

        self.assertEqual(user1.client.downloadSubscriptions(), (True, None))

        # Reinstall font
        user1.client.testScenario = None
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number]]
            )
        )
        if not success:
            print(message)  # nocoverage
        self.assertEqual(success, True)
        self.assertEqual(user1.client.publishers()[0].amountInstalledFonts(), 1)
        self.assertEqual(
            user1.client.publishers()[0].subscriptions()[0].amountInstalledFonts(), 1
        )

        # This is also supposed to delete the installed protected font
        user1.client.testScenario = "simulateCentralServerNotReachable"
        self.assertEqual(user1.client.unlinkUser()[0], False)
        user1.client.testScenario = "simulateCentralServerProgrammingError"
        self.assertEqual(user1.client.unlinkUser()[0], False)
        user1.client.testScenario = "simulateCentralServerErrorInResponse"
        self.assertEqual(user1.client.unlinkUser()[0], False)
        user1.client.testScenario = "simulateNotOnline"
        self.assertEqual(user1.client.unlinkUser()[0], False)
        self.assertTrue(user1.client.syncProblems())
        user1.client.testScenario = None
        success, message = user1.client.unlinkUser()
        self.assertEqual(success, True)
        self.assertFalse(user1.client.syncProblems())
        self.assertEqual(user1.client.userEmail(), None)
        self.assertEqual(user1.client.user(), "")

        self.assertEqual(user1.client.publishers()[0].amountInstalledFonts(), 0)
        self.assertEqual(len(user1.client.publishers()[0].subscriptions()), 1)

        # Delete subscription from user-less app, so that it can be re-added
        # during upcoming user linking
        user1.client.publishers()[0].subscriptions()[0].delete()
        self.assertEqual(len(user1.client.publishers()), 0)

        user1.client.testScenario = "simulateCentralServerNotReachable"
        self.assertEqual(user1.client.linkUser(*user1.credentials)[0], False)
        user1.client.testScenario = "simulateCentralServerProgrammingError"
        self.assertEqual(user1.client.linkUser(*user1.credentials)[0], False)
        user1.client.testScenario = "simulateCentralServerErrorInResponse"
        self.assertEqual(user1.client.linkUser(*user1.credentials)[0], False)
        user1.client.testScenario = "simulateNotOnline"
        self.assertEqual(user1.client.linkUser(*user1.credentials)[0], False)
        user1.client.testScenario = None
        success, message = user1.client.linkUser(*user1.credentials)
        print("linkUser:", success, message)
        self.assertEqual(success, True)

        # Unlink
        self.assertEqual(user1.client.unlinkUser()[0], True)
        # Log in
        self.assertEqual(user1.client.logInUserAccount(*testUser1)[0], True)

        self.assertEqual(len(user1.client.publishers()[0].subscriptions()), 1)
        self.assertEqual(user1.client.userEmail(), "test1@type.world")

        # Install again
        user1.client.publishers()[0].subscriptions()[-1].set(
            "acceptedTermsOfService", True
        )
        user1.client.publishers()[0].subscriptions()[-1].set("revealIdentity", True)
        self.assertEqual(
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user1.testFont().uniqueID, user1.testFont().getVersions()[-1].number]]
            ),
            (True, None),
        )
        self.assertEqual(user1.client.publishers()[0].amountInstalledFonts(), 1)

        # Sync subscription
        user1.client.testScenario = "simulateCentralServerNotReachable"
        self.assertEqual(user1.client.syncSubscriptions()[0], False)
        user1.client.testScenario = "simulateCentralServerProgrammingError"
        self.assertEqual(user1.client.syncSubscriptions()[0], False)
        user1.client.testScenario = "simulateCentralServerErrorInResponse"
        self.assertEqual(user1.client.syncSubscriptions()[0], False)
        user1.client.testScenario = "simulateNotOnline"
        self.assertEqual(user1.client.syncSubscriptions()[0], False)
        user1.client.testScenario = None
        self.assertEqual(user1.client.syncSubscriptions()[0], True)

        # #

        # Scenario 4:
        # Protected subscription, installation on second machine

        user2.client.testScenario = "simulateWrongMimeType"
        success, message, publisher, subscription = user2.client.addSubscription(
            protectedSubscription
        )
        self.assertEqual(success, False)
        self.assertEqual(
            message,
            (
                "Resource headers returned wrong MIME type: 'text/html'. "
                "Expected is '['application/json']'."
            ),
        )
        user2.client.testScenario = "simulateNotHTTP200"
        success, message, publisher, subscription = user2.client.addSubscription(
            protectedSubscription
        )
        self.assertEqual(success, False)
        user2.client.testScenario = "simulateProgrammingError"
        success, message, publisher, subscription = user2.client.addSubscription(
            protectedSubscription
        )
        self.assertEqual(success, False)
        user2.client.testScenario = "simulateInvalidAPIJSONResponse"
        success, message, publisher, subscription = user2.client.addSubscription(
            protectedSubscription
        )
        self.assertEqual(success, False)
        user2.client.testScenario = "simulateFaultyAPIJSONResponse"
        success, message, publisher, subscription = user2.client.addSubscription(
            protectedSubscription
        )
        self.assertEqual(success, False)
        user2.client.testScenario = "simulateCentralServerNotReachable"
        success, message, publisher, subscription = user2.client.addSubscription(
            protectedSubscription
        )
        self.assertEqual(success, False)
        user2.client.testScenario = "simulateCentralServerProgrammingError"
        success, message, publisher, subscription = user2.client.addSubscription(
            protectedSubscription
        )
        self.assertEqual(success, False)
        user2.client.testScenario = "simulateCentralServerErrorInResponse"
        success, message, publisher, subscription = user2.client.addSubscription(
            protectedSubscription
        )
        self.assertEqual(success, False)
        user2.client.testScenario = "simulateNotOnline"
        success, message, publisher, subscription = user2.client.addSubscription(
            protectedSubscription
        )
        self.assertEqual(success, False)
        user2.client.testScenario = None
        success, message, publisher, subscription = user2.client.addSubscription(
            protectedSubscription
        )
        self.assertEqual(success, True)
        print(success, message)

        # Two versions available
        self.assertEqual(
            len(
                user2.client.publishers()[0]
                .subscriptions()[-1]
                .installFonts(
                    [[user2.testFont().uniqueID, user2.testFont().getVersions()]]
                )
            ),
            2,
        )

        # Supposed to reject because seats are limited to 1
        user2.client.publishers()[0].subscriptions()[-1].set(
            "acceptedTermsOfService", True
        )
        user2.client.publishers()[0].subscriptions()[-1].set("revealIdentity", True)
        self.assertEqual(
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user2.testFont().uniqueID, user2.testFont().getVersions()[-1].number]]
            ),
            (
                False,
                [
                    "#(response.seatAllowanceReached)",
                    "#(response.seatAllowanceReached.headline)",
                ],
            ),
        )

        # Uninstall font for user1
        user1.client.testScenario = "simulatePermissionError"
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .removeFonts([user1.testFont().uniqueID])
        )
        self.assertEqual(success, False)

        user1.client.testScenario = "simulateTemporarilyUnavailable"
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .removeFonts([user1.testFont().uniqueID])
        )
        self.assertEqual(success, False)

        user1.client.testScenario = "simulateCustomError"
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .removeFonts([user1.testFont().uniqueID])
        )
        print(message)  # nocoverage
        self.assertEqual(success, False)
        self.assertEqual(message.getText(), "simulateCustomError")

        user1.client.testScenario = "simulateNoPath"
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .removeFonts([user1.testFont().uniqueID])
        )
        print(message)  # nocoverage
        self.assertEqual(success, False)

        user1.client.testScenario = "simulateProgrammingError"
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .removeFonts([user1.testFont().uniqueID])
        )
        self.assertEqual(success, False)

        user1.client.testScenario = "simulateInsufficientPermissions"
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .removeFonts([user1.testFont().uniqueID])
        )
        self.assertEqual(success, False)

        # Supposed to succeed
        user1.client.testScenario = None
        success, message = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .removeFonts([user1.testFont().uniqueID])
        )
        self.assertEqual(success, True)

        # Uninstall font for user2, must fail because deleting same font file
        # (doesn't make sense in normal setup)
        result = (
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .removeFonts([user2.testFont().uniqueID])
        )
        print(result)
        self.assertEqual(
            result, (False, "Font path couldn’t be determined (preflight)")
        )

        # Try again for user2
        self.assertEqual(
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user2.testFont().uniqueID, user2.testFont().getVersions()[-1].number]]
            ),
            (True, None),
        )

        # Uninstall font on for user2
        result = (
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .removeFonts([user2.testFont().uniqueID])
        )
        print(result)
        self.assertEqual(result, (True, None))

        # Install older version on second client
        self.assertEqual(
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [[user2.testFont().uniqueID, user2.testFont().getVersions()[0].number]]
            ),
            (True, None),
        )

        # Check amount
        self.assertEqual(user2.client.publishers()[0].amountInstalledFonts(), 1)

        # One font must be outdated
        self.assertEqual(user2.client.amountOutdatedFonts(), 1)
        self.assertEqual(user2.client.publishers()[0].amountOutdatedFonts(), 1)
        self.assertEqual(
            user2.client.publishers()[0].subscriptions()[0].amountOutdatedFonts(), 1
        )

        # Uninstall font for user2
        result = (
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .removeFonts([user2.testFont().uniqueID])
        )
        print(result)
        self.assertEqual(result, (True, None))

        # Family By ID
        family = (
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .protocol.installableFontsCommand()[1]
            .foundries[0]
            .families[0]
        )
        self.assertEqual(
            family,
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .familyByID(family.uniqueID),
        )

        # Font By ID
        font = family.fonts[0]
        self.assertEqual(
            font,
            user2.client.publishers()[0].subscriptions()[-1].fontByID(font.uniqueID),
        )

        # Clear
        user2.clearSubscriptions()
        self.assertEqual(len(user2.client.publishers()), 0)

        # Uninstallation of fonts when they aren't present in the subscription anymore
        user0.client.addSubscription(freeSubscription)
        user0.client.publishers()[0].subscriptions()[-1].set(
            "acceptedTermsOfService", True
        )
        font = (
            user0.client.publishers()[0]
            .subscriptions()[-1]
            .protocol.installableFontsCommand()[1]
            .foundries[0]
            .families[0]
            .fonts[-1]
        )
        self.assertEqual(
            user0.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts([[font.uniqueID, font.getVersions()[-1].number]]),
            (True, None),
        )
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    user0.client.publishers()[0].folder(),
                    user0.client.publishers()[0].subscriptions()[-1].uniqueID()
                    + "-"
                    + font.filename(font.getVersions()[-1].number),
                )
            )
        )
        user0.client.testScenario = "simulateFontNoLongerIncluded"
        self.assertEqual(
            user0.client.publishers()[0].subscriptions()[-1].update(),
            (True, None, True),
        )
        self.assertFalse(
            os.path.exists(
                os.path.join(
                    user0.client.publishers()[0].folder(),
                    font.filename(font.getVersions()[-1].number),
                )
            )
        )

        # #

        print("STATUS: -14")

        # Invitations
        # Invite to client without linked user account
        success, message, publisher, subscription = user0.client.addSubscription(
            freeSubscription
        )
        self.assertEqual(success, True)
        result = (
            user0.client.publishers()[0]
            .subscriptions()[-1]
            .inviteUser("test12345@type.world")
        )
        self.assertEqual(result, (False, "No source user linked."))

        # Invite unknown user
        result = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .inviteUser("test12345@type.world")
        )
        self.assertEqual(
            result,
            (
                False,
                [
                    "#(response.unknownTargetEmail)",
                    "#(response.unknownTargetEmail.headline)",
                ],
            ),
        )

        # Invite same user
        self.assertEqual(user1.client.userEmail(), "test1@type.world")
        # self.assertEqual(user1.client.user(), '736b524a-cf24-11e9-9f62-901b0ecbcc7a')
        result = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .inviteUser("test1@type.world")
        )
        self.assertEqual(
            result,
            (
                False,
                [
                    "#(response.sourceAndTargetIdentical)",
                    "#(response.sourceAndTargetIdentical.headline)",
                ],
            ),
        )

        print("STATUS: -13")

        # Invite real user
        user1.client.testScenario = "simulateCentralServerNotReachable"
        result = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .inviteUser("test2@type.world")
        )
        self.assertEqual(result[0], False)
        user1.client.testScenario = "simulateCentralServerProgrammingError"
        result = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .inviteUser("test2@type.world")
        )
        self.assertEqual(result[0], False)
        user1.client.testScenario = "simulateCentralServerErrorInResponse"
        result = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .inviteUser("test2@type.world")
        )
        self.assertEqual(result[0], False)
        user1.client.testScenario = "simulateNotOnline"
        result = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .inviteUser("test2@type.world")
        )
        self.assertEqual(result[0], False)
        user1.client.testScenario = None
        result = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .inviteUser("test2@type.world")
        )
        print(result)
        self.assertEqual(result[0], True)

        print("STATUS: -12")

        # Update user2
        self.assertEqual(len(user2.client.pendingInvitations()), 0)

        print("STATUS: -11.8")

        self.assertEqual(len(user2.client.publishers()), 0)

        print("STATUS: -11.7")

        self.assertEqual(user2.client.downloadSubscriptions(), (True, None))

        print("STATUS: -11.6")

        self.assertEqual(len(user2.client.pendingInvitations()), 1)

        print("STATUS: -11.5")

        # Decline (exists only here in test script)
        user2.clearInvitations()
        # Invite again
        result = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .inviteUser("test2@type.world")
        )
        self.assertEqual(result, (True, None))

        print("STATUS: -11")

        # Accept invitation
        self.assertEqual(user2.client.downloadSubscriptions(), (True, None))

        user2.client.testScenario = "simulateCentralServerNotReachable"
        success, message = user2.client.pendingInvitations()[0].accept()
        self.assertEqual(success, False)
        user2.client.testScenario = "simulateCentralServerProgrammingError"
        success, message = user2.client.pendingInvitations()[0].accept()
        self.assertEqual(success, False)
        user2.client.testScenario = "simulateCentralServerErrorInResponse"
        success, message = user2.client.pendingInvitations()[0].accept()
        self.assertEqual(success, False)
        user2.client.testScenario = "simulateNotOnline"
        success, message = user2.client.pendingInvitations()[0].accept()
        self.assertEqual(success, False)
        user2.client.testScenario = None
        success, message = user2.client.pendingInvitations()[0].accept()
        print(message)  # nocoverage
        self.assertEqual(success, True)

        print("STATUS: -10")

        user2.client.downloadSubscriptions()
        self.assertEqual(len(user2.client.pendingInvitations()), 0)
        self.assertEqual(len(user2.client.publishers()), 1)

        # Invite yet another user
        self.assertEqual(len(user3.client.pendingInvitations()), 0)
        self.assertEqual(len(user3.client.publishers()), 0)
        result = (
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .inviteUser("test3@type.world")
        )
        self.assertEqual(result, (True, None))
        success, message = user2.client.downloadSubscriptions()
        self.assertEqual(success, True)
        self.assertEqual(len(user2.client.sentInvitations()), 1)

        print("STATUS: -9")

        # Decline invitation
        user3.client.downloadSubscriptions()
        self.assertEqual(len(user3.client.pendingInvitations()), 1)

        user3.client.testScenario = "simulateCentralServerNotReachable"
        success, message = user3.client.pendingInvitations()[0].decline()
        self.assertEqual(success, False)
        user3.client.testScenario = "simulateCentralServerProgrammingError"
        success, message = user3.client.pendingInvitations()[0].decline()
        self.assertEqual(success, False)
        user3.client.testScenario = "simulateCentralServerErrorInResponse"
        success, message = user3.client.pendingInvitations()[0].decline()
        self.assertEqual(success, False)
        user3.client.testScenario = "simulateNotOnline"
        success, message = user3.client.pendingInvitations()[0].decline()
        self.assertEqual(success, False)
        user3.client.testScenario = None
        success, message = user3.client.pendingInvitations()[0].decline()
        self.assertEqual(success, True)

        self.assertEqual(len(user3.client.pendingInvitations()), 0)
        user2.client.downloadSubscriptions()
        self.assertEqual(len(user2.client.sentInvitations()), 0)

        # Invite again
        self.assertEqual(len(user3.client.pendingInvitations()), 0)
        self.assertEqual(len(user3.client.publishers()), 0)
        result = (
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .inviteUser("test3@type.world")
        )
        self.assertEqual(result, (True, None))
        user2.client.downloadSubscriptions()
        self.assertEqual(len(user2.client.sentInvitations()), 1)

        print("STATUS: -8")

        # Accept invitation
        user3.client.downloadSubscriptions()
        self.assertEqual(len(user3.client.pendingInvitations()), 1)
        user3.client.pendingInvitations()[0].accept()
        self.assertEqual(len(user3.client.publishers()), 1)

        print("STATUS: -7")

        # Revoke user
        user2.client.testScenario = "simulateCentralServerNotReachable"
        success, message = (
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .revokeUser("test3@type.world")
        )
        self.assertEqual(success, False)
        user2.client.testScenario = "simulateCentralServerProgrammingError"
        success, message = (
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .revokeUser("test3@type.world")
        )
        self.assertEqual(success, False)
        user2.client.testScenario = "simulateCentralServerErrorInResponse"
        success, message = (
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .revokeUser("test3@type.world")
        )
        self.assertEqual(success, False)
        user2.client.testScenario = "simulateNotOnline"
        success, message = (
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .revokeUser("test3@type.world")
        )
        self.assertEqual(success, False)
        user2.client.testScenario = None
        success, message = (
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .revokeUser("test3@type.world")
        )
        if not success:
            print(message)  # nocoverage
        self.assertEqual(success, True)

        print("STATUS: -6")

        self.assertEqual(result, (True, None))
        user3.client.downloadSubscriptions()
        self.assertEqual(len(user3.client.publishers()), 0)

        print("STATUS: -5")

        # Invite again
        self.assertEqual(len(user3.client.pendingInvitations()), 0)
        self.assertEqual(len(user3.client.publishers()), 0)
        result = (
            user2.client.publishers()[0]
            .subscriptions()[-1]
            .inviteUser("test3@type.world")
        )
        self.assertEqual(result, (True, None))
        user2.client.downloadSubscriptions()
        self.assertEqual(len(user2.client.sentInvitations()), 1)

        print("STATUS: -4")

        # Accept invitation
        user3.client.downloadSubscriptions()
        self.assertEqual(len(user3.client.pendingInvitations()), 1)
        self.assertEqual(len(user3.client.publishers()), 0)
        user3.client.pendingInvitations()[0].accept()
        self.assertEqual(len(user3.client.publishers()), 1)

        print("STATUS: -3")

        # Invitation accepted
        success = user3.client.publishers()[-1].subscriptions()[-1].invitationAccepted()
        self.assertEqual(success, True)

        print("STATUS: -2")

        # Get publisher's logo, first time
        self.assertTrue(
            user0.client.publishers()[0]
            .subscriptions()[0]
            .protocol.rootCommand()[1]
            .logoURL
        )
        success, logo, mimeType = user0.client.publishers()[0].resourceByURL(
            user0.client.publishers()[0]
            .subscriptions()[0]
            .protocol.rootCommand()[1]
            .logoURL
        )
        self.assertEqual(success, True)
        self.assertTrue(logo.startswith('<?xml version="1.0" encoding="utf-8"?>'))

        # Get publisher's logo, second time (from cache in preferences)
        self.assertTrue(
            user0.client.publishers()[0]
            .subscriptions()[0]
            .protocol.rootCommand()[1]
            .logoURL
        )
        success, logo, mimeType = user0.client.publishers()[0].resourceByURL(
            user0.client.publishers()[0]
            .subscriptions()[0]
            .protocol.rootCommand()[1]
            .logoURL
        )
        self.assertEqual(success, True)
        self.assertTrue(logo.startswith('<?xml version="1.0" encoding="utf-8"?>'))

        logoURL = (
            user0.client.publishers()[0]
            .subscriptions()[0]
            .protocol.installableFontsCommand()[1]
            .foundries[0]
            .styling["light"]["logoURL"]
        )

        # Get foundry's logo, first time
        self.assertTrue(logoURL)
        success, logo, mimeType = (
            user0.client.publishers()[0].subscriptions()[0].resourceByURL(logoURL)
        )
        self.assertEqual(success, True)
        self.assertTrue(logo.startswith('<?xml version="1.0" encoding="utf-8"?>'))

        # Get foundry's logo, second time (from cache in preferences)
        self.assertTrue(logoURL)
        success, logo, mimeType = (
            user0.client.publishers()[0].subscriptions()[0].resourceByURL(logoURL)
        )
        self.assertEqual(success, True)
        self.assertTrue(logo.startswith('<?xml version="1.0" encoding="utf-8"?>'))

        # Get foundry's logo, first time
        self.assertTrue(logoURL)
        success, logo, mimeType = (
            user0.client.publishers()[0]
            .subscriptions()[0]
            .resourceByURL(logoURL, binary=True)
        )
        self.assertEqual(success, True)
        self.assertTrue(logo.startswith("PD94b"))

        # Get foundry's logo, second time (from cache in preferences)
        self.assertTrue(logoURL)
        success, logo, mimeType = (
            user0.client.publishers()[0]
            .subscriptions()[0]
            .resourceByURL(logoURL, binary=True)
        )
        self.assertEqual(success, True)
        self.assertTrue(logo.startswith("PD94b"))

        print("STATUS: -1")

        #####

        # Expiring font

        # Install font
        user1.client.testScenario = None
        success, response = (
            user1.client.publishers()[0]
            .subscriptions()[-1]
            .installFonts(
                [
                    [
                        user1.expiringTestFont().uniqueID,
                        user1.expiringTestFont().getVersions()[-1].number,
                    ]
                ]
            )
        )
        if not success:
            print(response)
        self.assertEqual(success, True)

        self.assertEqual(len(user1.client.expiringInstalledFonts()), 1)

        # Traceback Test
        user1.client.tracebackTest()
        user1.client.tracebackTest2()

        # Delete subscription from first user. Subsequent invitation must
        # then be taken down as well.
        user1.client.publishers()[0].delete()
        user2.client.downloadSubscriptions()
        user3.client.downloadSubscriptions()
        self.assertEqual(len(user2.client.pendingInvitations()), 0)
        self.assertEqual(len(user3.client.pendingInvitations()), 0)

        print("test_normalSubscription() finished...")

    # def _test_APIValidator(self):

    # 	print('test_APIValidator() started...')

    # 	# Announce subscription update
    # 	parameters = {"command": "validateAPIEndpoint",
    # 				"subscriptionURL": protectedSubscription,
    # 				}

    # 	success, response = performRequest(MOTHERSHIP, parameters, sslcontext)
    # 	self.assertEqual(success, True)

    # 	response = json.loads(response.read().decode())
    # 	print(response)

    # 	self.assertEqual(response['response'], 'success')

    # 	print('test_APIValidator() finished...')

    def test_UserAccounts(self):

        print("test_UserAccounts() started...")

        # Create user account

        success, message = user0.client.createUserAccount(
            "Test", "test0@type.world", "", ""
        )
        self.assertEqual(message, "#(RequiredFieldEmpty)")

        success, message = user0.client.createUserAccount(
            "Test", "test0@type.world", "abc", "def"
        )
        self.assertEqual(message, "#(PasswordsDontMatch)")

        user0.client.testScenario = "simulateCentralServerNotReachable"
        success, message = user0.client.createUserAccount(
            "Test", "test0@type.world", "abc", "abc"
        )
        self.assertEqual(success, False)
        self.assertTrue("urlopen error" in message)

        user0.client.testScenario = "simulateCentralServerProgrammingError"
        success, message = user0.client.createUserAccount(
            "Test", "test0@type.world", "abc", "abc"
        )
        self.assertEqual(success, False)
        self.assertTrue("HTTP Error 500" in message)

        user0.client.testScenario = "simulateCentralServerErrorInResponse"
        success, message = user0.client.createUserAccount(
            "Test", "test0@type.world", "abc", "abc"
        )
        self.assertEqual(success, False)
        self.assertEqual(
            message,
            [
                "#(response.simulateCentralServerErrorInResponse)",
                "#(response.simulateCentralServerErrorInResponse.headline)",
            ],
        )

        user0.client.testScenario = "simulateNotOnline"
        success, message = user0.client.createUserAccount(
            "Test", "test0@type.world", "abc", "abc"
        )
        self.assertEqual(success, False)
        self.assertEqual(
            message, ["#(response.notOnline)", "#(response.notOnline.headline)"]
        )

        # Delete User Account

        user0.client.testScenario = None
        success, message = user0.client.deleteUserAccount("test0@type.world", "")
        self.assertEqual(message, "#(RequiredFieldEmpty)")

        user0.client.testScenario = "simulateCentralServerNotReachable"
        success, message = user0.client.deleteUserAccount("test0@type.world", "abc")
        self.assertEqual(success, False)
        user0.client.testScenario = "simulateCentralServerProgrammingError"
        success, message = user0.client.deleteUserAccount("test0@type.world", "abc")
        self.assertEqual(success, False)
        user0.client.testScenario = "simulateCentralServerErrorInResponse"
        success, message = user0.client.deleteUserAccount("test0@type.world", "abc")
        self.assertEqual(success, False)
        user0.client.testScenario = "simulateNotOnline"
        success, message = user0.client.deleteUserAccount("test0@type.world", "abc")
        self.assertEqual(success, False)
        self.assertEqual(
            message, ["#(response.notOnline)", "#(response.notOnline.headline)"]
        )

        # Log In User Account

        success, message = user0.client.logInUserAccount("test0@type.world", "")
        self.assertEqual(message, "#(RequiredFieldEmpty)")

        user0.client.testScenario = "simulateCentralServerNotReachable"
        success, message = user0.client.logInUserAccount(*testUser1)
        self.assertEqual(success, False)
        user0.client.testScenario = "simulateCentralServerProgrammingError"
        success, message = user0.client.logInUserAccount(*testUser1)
        self.assertEqual(success, False)
        user0.client.testScenario = "simulateCentralServerErrorInResponse"
        success, message = user0.client.logInUserAccount(*testUser1)
        self.assertEqual(success, False)
        user0.client.testScenario = "simulateNotOnline"
        success, message = user0.client.logInUserAccount(*testUser1)
        self.assertEqual(success, False)

        user0.client.testScenario = None
        success, message = user0.client.logInUserAccount(*testUser1)
        self.assertEqual(success, True)
        success, message = user0.client.unlinkUser()
        self.assertEqual(success, True)

        print("test_UserAccounts() finished...")

    def run(self, result=None):
        self.currentResult = result  # remember result for use in tearDown
        unittest.TestCase.run(self, result)  # call superclass run method

    # from https://stackoverflow.com/questions/4414234/getting-pythons-
    # unittest-results-in-a-teardown-method
    def tearDown(self):
        result = self.defaultTestResult()  # these 2 methods have no side effects
        self._feedErrorsToResult(result, self._outcome.errors)
        errors.extend(result.errors)
        failures.extend(result.failures)


def setUp():

    print("setUp() started...")

    global user0, user1, user2, user3, tempFolder
    tempFolder = tempfile.mkdtemp()
    user0 = User()
    user1 = User(testUser1)
    user2 = User(testUser2)
    user3 = User(testUser3)

    print("setUp() finished...")


def tearDown():

    print("tearDown() started...")

    global user0, user1, user2, user3, tempFolder
    user0.takeDown()
    user1.takeDown()
    user2.takeDown()
    user3.takeDown()

    # Local
    if "TRAVIS" not in os.environ:
        os.rmdir(tempFolder)  # nocoverage

    print("tearDown() finished...")


if __name__ == "__main__":

    if ONLINE:
        setUp()

    result = unittest.main(exit=False, failfast=True)

    if ONLINE:
        tearDown()

    if errors:
        raise ValueError()  # nocoverage
    if failures:
        raise ValueError()  # nocoverage
