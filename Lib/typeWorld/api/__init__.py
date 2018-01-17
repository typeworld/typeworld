# -*- coding: utf-8 -*-

from typeWorld.base import *


####################################################################################################################################

#  Object model

class SupportedAPICommandsDataType(UnicodeDataType):
	
	commands = [x['keyword'] for x in COMMANDS]


	def valid(self):
		if self.value in self.commands:
			return True
		else:
			return 'Unknown API command: "%s". Possible: %s' % (self.value, self.commands)

class SupportedAPICommandsListProxy(ListProxy):
	dataType = SupportedAPICommandsDataType


class FontTypeDataType(UnicodeDataType):
	def valid(self):
		if self.value in FONTTYPES:
			return True
		else:
			return 'Unknown font type: "%s". Possible: %s' % (self.value, FONTTYPES)

####################################################################################################################################

#  License

class License(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'keyword':	 				[UnicodeDataType,		True, 	None, 	'Keyword under which the license will be referenced from the individual fonts.'],
		'name':	 					[MultiLanguageTextProxy,		True, 	None, 	'Human-readable name of font license'],
		'URL':	 					[WebURLDataType,		True, 	None, 	'URL where the font license can be viewed online'],
	}

	def __repr__(self):
		return '<License "%s">' % self.name or self.keyword or 'undefined'

def License_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
License.parent = property(lambda self: License_Parent(self))

class LicenseProxy(Proxy):
	dataType = License

class LicensesListProxy(ListProxy):
	dataType = LicenseProxy


####################################################################################################################################

#  Designer

class Designer(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'keyword':	 				[UnicodeDataType,		True, 	None, 	'Keyword under which the designer will be referenced from the individual fonts or font families'],
		'name':	 					[MultiLanguageTextProxy,		True, 	None, 	'Human-readable name of designer'],
		'website':	 				[WebURLDataType,		False, 	None, 	u'Designer’s web site'],
		'description':	 			[MultiLanguageTextProxy,		False, 	None, 	'Description of designer'],
	}

	def __repr__(self):
		return '<Designer "%s">' % self.name.getText() or self.keyword or 'undefined'

def Designer_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
Designer.parent = property(lambda self: Designer_Parent(self))

class DesignerProxy(Proxy):
	dataType = Designer

class DesignersListProxy(ListProxy):
	dataType = DesignerProxy

class DesignersReferencesListProxy(ListProxy):
	dataType = UnicodeDataType

####################################################################################################################################

#  Font Family Version


class Version(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'number':	 				[FloatDataType,				True, 	None, 	'Font version number'],
		'description':	 			[MultiLanguageTextProxy,	False, 	None, 	'Description of font version'],
		'releaseDate':	 			[FloatDataType,				False, 	None, 	u'Timestamp of version’s release date.'],
	}

	def __repr__(self):
		return '<Version %s (%s)>' % (self.number if self.number else 'None', 'font-specific' if self.isFontSpecific() else 'family-specific')

	def isFontSpecific(self):
		u'''\
		Returns True if this version is defined at the font level. Returns False if this version is defined at the family level.
		'''
		return issubclass(self.parent.__class__, Font)

def Version_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
Version.parent = property(lambda self: Version_Parent(self))

class VersionProxy(Proxy):
	dataType = Version

class VersionListProxy(ListProxy):
	dataType = VersionProxy


####################################################################################################################################

#  Fonts

class Font(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'name':	 			[MultiLanguageTextProxy,		True, 	None, 	u'Human-readable name of font. This may include any additions that you find useful to communicate to your users.'],
		'ID':				[UnicodeDataType,		True, 	None, 	u'An string that uniquely identifies this font within its publisher. It will be used to ask for un/installation of the font from the server in the `installFont` and `uninstallFont` commands.'],
		'postScriptName':	[UnicodeDataType,		True, 	None, 	u'Complete PostScript name of font'],
		'previewImage':		[WebURLDataType,		False, 	None, 	u'URL of preview image of font, specifications to follow'],
		'variantName':		[MultiLanguageTextProxy,		False, 	None, 	'Optional variant name of font. This is used to visually group fonts in the UI. Thinking "Office Fonts" and such.'],
		'licenseKeyword':	[UnicodeDataType,		True, 	None, 	u'Keyword reference of font’s license. This license must be specified in the Foundry.Licenses'],
		'versions':	 		[VersionListProxy,		False, 	None, 	u'List of ::Version:: objects. These are font-specific versions; they may exist only for this font. You may define additional versions at the family object under ::Family.versions::, which are then expected to be available for the entire family. However, either the fonts or the font family *must* carry version information and the validator will complain when they don’t.\n\nPlease also read the section on [versioning](#versioning) above.'],
		'designers':	 	[DesignersReferencesListProxy,	False, 	None, 	u'List of keywords referencing designers. These are defined at ::InstallableFontsResponse.designers::. This attribute overrides the designer definitions at the family level at ::Family.designers::.'],
		'free':				[BooleanDataType,		False, 	None, 	u'Font is freeware. For UI signaling'],
		'beta':				[BooleanDataType,		False, 	None, 	u'Font is in beta stage. For UI signaling'],
		'variableFont':		[BooleanDataType,		False, 	None, 	u'Font is an OpenType Variable Font. For UI signaling'],
#		'public':			[BooleanDataType,		False, 	False, 	u'If false, signals restricted access to a commercial font only available to certain users. Download and installation may be restricted by the API point depending on the API point URL that needs to include the private key to identify the user.'],
		'type':				[FontTypeDataType,		True, 	None, 	u'Technical type of font. This influences how the app handles the font. For instance, it will only install desktop fonts on the system, and make other font types available though folders. Possible: %s' % (FONTTYPES)],
		'seatsAllowedForUser':[IntegerDataType,		False, 	None, 	u'In case of desktop font (see ::Font.type::), number of installations permitted by the user’s license.'],
		'seatsInstalledByUser':	[IntegerDataType,		False, 	None, 	u'In case of desktop font (see ::Font.type::), number of installations recorded by the API endpoint. This value will need to be supplied by the API endpoint through tracking all font installations through the "anonymousAppID" parameter of the "%s" and "%s" command. Please note that the app is currently not designed to reject installations of the fonts when the limits are exceeded. Instead it is in the responsibility of the API endpoint to reject font installations though the "%s" command when the limits are exceeded.' % (INSTALLFONTCOMMAND['keyword'], UNINSTALLFONTCOMMAND['keyword'], INSTALLFONTCOMMAND['keyword'])],
		'licenseAllowanceDescription':	[MultiLanguageTextProxy,		False, 	None, 	u'In case of non-desktop font (see ::Font.type::), custom string for web fonts or app fonts reminding the user of the license’s limits, e.g. "100.000 page views/month"'],
		'upgradeLicenseURL':[WebURLDataType,		False, 	None, 	u'URL the user can be sent to to upgrade the license of the font, for instance at the foundry’s online shop'],
		'upgradeLicenseURL':[WebURLDataType,		False, 	None, 	u'URL the user can be sent to to upgrade the license of the font, for instance at the foundry’s online shop'],
		'timeAddedForUser':	[IntegerDataType,		False, 	None, 	u'Timestamp of the time the user has purchased this font or the font has become available to the user otherwise, like a new font within a foundry’s beta font repository. Will be used in the UI to signal which fonts have become newly available in addition to previously available fonts. This is not to be confused with the ::Version.releaseDate::, although they could be identical.'],
	}

	def __repr__(self):
		return '<Font "%s">' % (self.postScriptName or self.name.getText() or 'undefined')

	def hasVersionInformation(self):
		return self.versions or self.parent.versions

	def getLicense(self):
		u'''\
		Returns the ::License:: object that this font references.
		'''
		return self.parent.parent.getLicenseByKeyword(self.licenseKeyword)

	def customValidation(self):
		information, warnings, critical = [], [], []

		# Checking version information
		if not self.hasVersionInformation():
			critical.append('The font %s has no version information, and neither has its family %s. Either one needs to carry version information.' % (self, self.parent))

		# Checking for existing license
		if not self.getLicense():
			critical.append('%s has license "%s", but %s has no matching license.' % (self, self.licenseKeyword, self.parent.parent))

		# Checking for designers
		for designerKeyword in self.designers:
			if not self.parent.parent.parent.getDesignerByKeyword(designerKeyword):
				critical.append('%s has designer "%s", but %s.designers has no matching designer.' % (self, designerKeyword, self.parent.parent.parent))

		return information, warnings, critical

	def getSortedVersions(self):
		u'''\
		Returns list of ::Version:: objects.

		This is the final list based on the version information in this font object as well as in its parent ::Family:: object. Please read the section about [versioning](#versioning) above.
		'''

		if not self.hasVersionInformation():
			raise ValueError('Font %s has no version information, and neither has its family %s. Either one needs to carry version information.' % (self, self.parent))

		versions = []
		haveVersionNumbers = []
		for version in self.versions:
			versions.append(version)
			haveVersionNumbers.append(version.number)
		for version in self.parent.versions:
			if not version.number in haveVersionNumbers:
				versions.append(version)
				haveVersionNumbers.append(version.number)

		versions.sort(key=lambda x: x.number, reverse=False)
		return versions

	def getDesigners(self):
		u'''\
		Returns a list of ::Designer:: objects that this font references. These are the combination of family-level designers and font-level designers. The same logic as for versioning applies. Please read the section about [versioning](#versioning) above.
		'''
		if not hasattr(self, '_designers'):
			self._designers = []

			# Family level designers
			if self.parent.designers:
				for designerKeyword in self.parent.designers:
					self._designers.append(self.parent.parent.parent.getDesignerByKeyword(designerKeyword))

			# Font level designers
			if self.designers:
				for designerKeyword in self.designers:
					self._designers.append(self.parent.parent.parent.getDesignerByKeyword(designerKeyword))

		return self._designers


def Font_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
Font.parent = property(lambda self: Font_Parent(self))


class FontProxy(Proxy):
	dataType = Font

class FontListProxy(ListProxy):
	dataType = FontProxy


# Font Family

class BillboardListProxy(ListProxy):
	dataType = WebURLDataType

class Family(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'name':	 					[MultiLanguageTextProxy,		True, 	None, 	u'Human-readable name of font family. This may include any additions that you find useful to communicate to your users.'],
		'description':	 			[MultiLanguageTextProxy,False, 	None, 	u'Description of font family'],
		'billboards':	 			[BillboardListProxy,	False, 	None, 	u'List of URLs pointing at images to show for this typeface, specifications to follow'],
		'designers':	 			[DesignersReferencesListProxy,	False, 	None, 	u'List of keywords referencing designers. These are defined at ::InstallableFontsResponse.designers::. In case designers differ between fonts within the same family, they can also be defined at the font level at ::Font.designers::. The font-level references take precedence over the family-level references.'],

		'sourceURL':	 			[WebURLDataType,		False, 	None, 	u'URL pointing to the source of a font project, such as a GitHub repository'],
		'issueTrackerURL':	 		[WebURLDataType,		False, 	None, 	u'URL pointing to an issue tracker system, where users can debate about a typeface’s design or technicalities'],
		'versions':	 				[VersionListProxy,		False, 	None, 	u'List of ::Version:: objects. Versions specified here are expected to be available for all fonts in the family, which is probably most common and efficient. You may define additional font-specific versions at the ::Font:: object. You may also rely entirely on font-specific versions and leave this field here empty. However, either the fonts or the font family *must* carry version information and the validator will complain when they don’t.\n\nPlease also read the section on [versioning](#versioning) above.'],
		'fonts':	 				[FontListProxy,			True, 	None, 	u'List of ::Font:: objects.'],
	}

	def __repr__(self):
		return '<Family "%s">' % self.name.getText() or 'undefined'

	def customValidation(self):
		information, warnings, critical = [], [], []

		# Checking for designers
		for designerKeyword in self.designers:
			if not self.parent.parent.getDesignerByKeyword(designerKeyword):
				critical.append('%s has designer "%s", but %s.designers has no matching designer.' % (self, designerKeyword, self.parent.parent))

		return information, warnings, critical

	def getDesigners(self):
		if not hasattr(self, '_designers'):
			self._designers = []
			for designerKeyword in self.designers:
				self._designers.append(self.parent.parent.getDesignerByKeyword(designerKeyword))
		return self._designers

	def getAllDesigners(self):
		u'''\
		Returns a list of ::Designer:: objects that represent all of the designers referenced both at the family level as well as with all the family’s fonts, in case the fonts carry specific designers. This could be used to give a one-glance overview of all designers involved.
		'''
		if not hasattr(self, '_allDesigners'):
			self._allDesigners = []
			self._allDesignersKeywords = []
			for designerKeyword in self.designers:
				self._allDesigners.append(self.parent.parent.getDesignerByKeyword(designerKeyword))
				self._allDesignersKeywords.append(designerKeyword)
			for font in self.fonts:
				for designerKeyword in font.designers:
					if not designerKeyword in self._allDesignersKeywords:
						self._allDesigners.append(self.parent.parent.getDesignerByKeyword(designerKeyword))
						self._allDesignersKeywords.append(designerKeyword)
		return self._allDesigners

def Family_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
Family.parent = property(lambda self: Family_Parent(self))

class FamilyProxy(Proxy):
	dataType = Family

class FamiliesListProxy(ListProxy):
	dataType = FamilyProxy


####################################################################################################################################

#  Font Foundry

class Foundry(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'name':	 					[MultiLanguageTextProxy,		True, 	None, 	'Name of foundry'],
		'logo':	 					[WebURLDataType,		False, 	None, 	u'URL of foundry’s logo. Specifications to follow.'],
		'description':	 			[MultiLanguageTextProxy,False, 	None, 	'Description of foundry'],
		'email':	 				[EmailDataType,			False, 	None, 	'General email address for this foundry'],
		'supportEmail':	 			[EmailDataType,			False, 	None, 	'Support email address for this foundry'],
		'website':	 				[WebURLDataType,		False, 	None, 	'Website for this foundry'],
		'twitter':	 				[UnicodeDataType,		False, 	None, 	'Twitter handle for this foundry, without the @'],
		'facebook':	 				[WebURLDataType,		False, 	None, 	'Facebook page URL handle for this foundry. The URL '],
		'instagram':	 			[UnicodeDataType,		False, 	None, 	'Instagram handle for this foundry, without the @'],
		'skype':	 				[UnicodeDataType,		False, 	None, 	'Skype handle for this foundry'],
		'telephone':	 			[UnicodeDataType,		False, 	None, 	'Telephone number for this foundry'],

		#styling
		'backgroundColor': 			[HexColorDataType,		False, 	None, 	u'Six-digit RRGGBB hex color value (without leading "#") for foundry’s preferred background color'],

		# data
		'licenses':					[LicensesListProxy,		True, 	None, 	'List of ::License:: objects under which the fonts in this response are issued. For space efficiency, these licenses are defined at the foundry object and will be referenced in each font by their keyword. Keywords need to be unique for this foundry and may repeat across foundries.'],
		'families':					[FamiliesListProxy,		True, 	None, 	'List of ::Family:: objects.'],
	}

	def __repr__(self):
		return '<Foundry "%s">' % self.name.getText() or 'undefined'

	def getLicenseByKeyword(self, keyword):
		if not hasattr(self, '_licensesDict'):
			self._licensesDict = {}
			for license in self.licenses:
				self._licensesDict[license.keyword] = license

		if self._licensesDict.has_key(keyword):
			return self._licensesDict[keyword]


def Foundry_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
Foundry.parent = property(lambda self: Foundry_Parent(self))

class FoundryProxy(Proxy):
	dataType = Foundry

class FoundryListProxy(ListProxy):
	dataType = FoundryProxy

####################################################################################################################################

#  Available Fonts

class BaseResponse(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_base_structure = {
	}

	def __repr__(self):
		return '<%s>' % self.__class__.__name__


	def customValidation(self):
		information, warnings, critical = [], [], []

		if self.type == ERROR and self.errorMessage is None:
			warnings.append('%s.type is "%s", but .errorMessage is missing.' % (self, ERROR))

		return information, warnings, critical

def BaseResponse_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent'):
		return self._parent._parent
BaseResponse.parent = property(lambda self: BaseResponse_Parent(self))


class InstallableFontsResponseType(UnicodeDataType):
	def valid(self):
		if self.value in INSTALLABLEFONTSCOMMAND['responseTypes']:
			return True
		else:
			return 'Unknown response type: "%s". Possible: %s' % (self.value, INSTALLABLEFONTSCOMMAND['responseTypes'])

class InstallableFontsResponse(BaseResponse):
	u'''\
	This is the response expected to be returned when the API is invoked using the command parameter, such as `http://fontpublisher.com/api/?command=installableFonts`.

	The response needs to be specified at the ::Response.command:: attribute, and then the ::Response:: object needs to carry the specific response command at the attribute of same name, in this case ::Reponse.installableFonts::.

	```python
	api.response = Response()
	api.response.command = 'installableFonts'
	api.response.installableFonts = InstallableFontsResponse()
	```

	'''
	# 	key: 					[data type, required, default value, description]
	_structure = {

		# Root
		'type': 			[InstallableFontsResponseType,	True, 	None, 	'Type of response. This can be "success", "error", or "custom". In case of "custom", you may specify an additional message to be presented to the user under ::InstallableFontsResponse.errorMessage::.'],
		'errorMessage': 	[MultiLanguageTextProxy,				False, 	None, 	'Description of error in case of ::InstallableFontsResponse.type:: being "custom".'],
		'version': 			[FloatDataType,					True, 	INSTALLABLEFONTSCOMMAND['currentVersion'], 	'Version of "%s" response' % INSTALLABLEFONTSCOMMAND['keyword']],
		'licenseIdentifier':[UnicodeDataType, 				False, 	u'CC-BY-NC-ND-4.0', 	'Identifier of license under which the API endpoint publishes this particular response, as per [https://spdx.org/licenses/](). This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. This license can be different from the license at the root of the response. The idea is that different responses can be issued under different licenses, depending on their use scenario. If not specified, the root license is assumed.'],

		# Response-specific
		'designers':		[DesignersListProxy,			False, 	None, 	'List of ::Designer:: objects, referenced in the fonts or font families by the keyword. These are defined at the root of the response for space efficiency, as one designer can be involved in the design of several typefaces across several foundries.'],
		'foundries':		[FoundryListProxy,				True, 	None, 	'List of ::Foundry:: objects; foundries that this distributor supports. In most cases this will be only one, as many foundries are their own distributors.'],
	}

	def getDesignerByKeyword(self, keyword):
		if not hasattr(self, '_designersDict'):
			self._designersDict = {}
			for designer in self.designers:
				self._designersDict[designer.keyword] = designer

		if self._designersDict.has_key(keyword):
			return self._designersDict[keyword]

	def discardThisKey(self, key):
		
		if key in ['foundries', 'designers', 'licenseIdentifier'] and self.type in ['custom', 'error']:
			return True

		return False


class InstallableFontsResponseProxy(Proxy):
	dataType = InstallableFontsResponse

####################################################################################################################################

#  InstallFont

class InstallFontResponseType(UnicodeDataType):
	def valid(self):
		if self.value in INSTALLFONTCOMMAND['responseTypes']:
			return True
		else:
			return 'Unknown response type: "%s". Possible: %s' % (self.value, INSTALLFONTCOMMAND['responseTypes'])

class InstallFontResponse(BaseResponse):
	# 	key: 					[data type, required, default value, description]
	_structure = {

		# Root
		'type': 			[InstallableFontsResponseType,	True, 	None, 	'Success or error.'],
		'errorMessage': 	[MultiLanguageTextProxy,		False, 	None, 	'Description of error in case of custom response type'],
		'version': 			[FloatDataType,					True, 	INSTALLFONTCOMMAND['currentVersion'], 	'Version of "%s" response' % INSTALLFONTCOMMAND['keyword']],
		'licenseIdentifier':[UnicodeDataType, 				False, 	u'CC-BY-NC-ND-4.0', 	'Identifier of license under which the API endpoint publishes this particular response, as per https://spdx.org/licenses/. This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. This license can be different from the license at the root of the response. The idea is that different responses can be issued under different licenses, depending on their use scenario. If not specified, the root license is assumed.'],

		# Response-specific
		}

class InstallFontResponseProxy(Proxy):
	dataType = InstallFontResponse

####################################################################################################################################

#  Uninstall Fonts

class UninstallFontResponseType(UnicodeDataType):
	def valid(self):
		if self.value in UNINSTALLFONTCOMMAND['responseTypes']:
			return True
		else:
			return 'Unknown response type: "%s". Possible: %s' % (self.value, UNINSTALLFONTCOMMAND['responseTypes'])

class UninstallFontResponse(BaseResponse):
	# 	key: 					[data type, required, default value, description]
	_structure = {

		# Root
		'type': 			[InstallableFontsResponseType,	True, 	None, 	'Success or error.'],
		'errorMessage': 	[MultiLanguageTextProxy,		False, 	None, 	'Description of error in case of custom response type'],
		'version': 			[FloatDataType,					True, 	UNINSTALLFONTCOMMAND['currentVersion'], 	'Version of "%s" response' % UNINSTALLFONTCOMMAND['keyword']],
		'licenseIdentifier':[UnicodeDataType, 				False, 	u'CC-BY-NC-ND-4.0', 	'Identifier of license under which the API endpoint publishes this particular response, as per https://spdx.org/licenses/. This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. This license can be different from the license at the root of the response. The idea is that different responses can be issued under different licenses, depending on their use scenario. If not specified, the root license is assumed.'],

		# Response-specific
		}

class UninstallFontResponseProxy(Proxy):
	dataType = UninstallFontResponse


class Response(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'command': 							[SupportedAPICommandsDataType,	True, 	None, 	'Command code of the response. The specific response must then be present under an attribute of same name.'],
		INSTALLABLEFONTSCOMMAND['keyword']:	[InstallableFontsResponseProxy, 	False, 	None, 	''],
		INSTALLFONTCOMMAND['keyword']:		[InstallFontResponseProxy, 	False, 	None, 	''],
		UNINSTALLFONTCOMMAND['keyword']:	[UninstallFontResponseProxy, 	False, 	None, 	''],
	}

	def __repr__(self):
		return '<Response>'

	def getCommand(self):
		u'''\
Returns the specific response referenced in the .command attribute. This is a shortcut.

```python
print api.response.getCommand()

# will print:
<InstallableFontsResponse>

# which is the same as:
print api.response.get(api.response.command)

# will print:
<InstallableFontsResponse>
```
'''
#		exec("command = self.%s" % self.command)
		return self.get(self.command)

	def customValidation(self):

		information, warnings, critical = [], [], []

		if not self.getCommand():
			critical.append('%s.command is set, but we are missing that command at %s.%s' % (self, self, self.command))

		return information, warnings, critical


def Response_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent'):
		return self._parent._parent
Response.parent = property(lambda self: Response_Parent(self))


class ResponseProxy(Proxy):
	dataType = Response

class APIRoot(DictBasedObject):
	u'''\
This is the main class that sits at the root of all API responses. It contains some mandatory information about the API endpoint such as its name and admin email, the copyright license under which the API endpoint issues its data, and whether or not this endpoint can be publicized about.

Any API response is expected to carry this minimum information, even when invoked without a particular command.

In case the API endpoint has been invoked with a particular command, the response data is attached to the ::APIRoot.response:: attribute.


```python
api = APIRoot()
api.name.en = u'Font Publisher'
api.canonicalURL = 'https://fontpublisher.com/api/'
api.adminEmail = 'admin@fontpublisher.com'
api.supportedCommands = ['installableFonts', 'installFonts', 'uninstallFonts']
```

	'''


	# 	key: 					[data type, required, default value, description]
	_structure = {
		'canonicalURL': 		[WebURLDataType, 			True, 	None, 	'Official API endpoint URL, bare of ID keys and other parameters. Used for grouping of subscriptions. It is expected that this URL will not change.'],
		'adminEmail': 			[EmailDataType, 			True, 	None, 	'API endpoint Administrator, to contact for technical problems and such'],
		'licenseIdentifier':	[UnicodeDataType, 			True, 	u'CC-BY-NC-ND-4.0', 	'Identifier of license under which the API endpoint publishes its data, as per [https://spdx.org/licenses/](). This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. Licenses of the individual responses can be fine-tuned in the respective responses.'],
		'supportedCommands': 	[SupportedAPICommandsListProxy, True, 	None, 	'List of commands this API endpoint supports: %s' % [x['keyword'] for x in COMMANDS]],
		'name': 				[MultiLanguageTextProxy, 			True, 	None, 	'Human-readable name of API endpoint'],
		'public': 				[BooleanDataType, 			True, 	False, 	'API endpoint is meant to be publicly visible and its existence may be publicized within the project'],
		'logo': 				[WebURLDataType, 			False, 	None, 	'URL of logo of API endpoint, for publication. Specifications to follow.'],
		'website': 				[WebURLDataType, 			False, 	None, 	'URL of human-visitable website of API endpoint, for publication'],
		'response': 			[ResponseProxy, 			False, 	None, 	'Response of the API call'],
	}


	def difference(self, other):
		from deepdiff import DeepDiff
		return DeepDiff(self.dumpDict(), other.dumpDict(), ignore_order=True)

	def sameContent(self, other):
		u'''\
		Compares the data structure of this object to the other object.

		Requires deepdiff module.
		'''
		return self.difference(other) == {}


	def __repr__(self):
		return '<API>'

	def validate(self):
		u'''\
		Return three lists with informations, warnings, and errors.

		An empty errors list is regarded as a successful validation, otherwise the validation is regarded as a failure.
		'''
		information, warnings, errors = self._validate()
		if self.canonicalURL and not self.canonicalURL.startswith('https://'):
			warnings.append('%s.canonicalURL is not using SSL (https://). Consider using SSL to protect your data.' % (self))
		return information, warnings, errors



