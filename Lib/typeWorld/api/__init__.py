# -*- coding: utf-8 -*-

from typeWorld.api.base import *
import functools, os

import platform
WIN = platform.system() == 'Windows'
MAC = platform.system() == 'Darwin'


####################################################################################################################################

#  LicenseDefinition

class LicenseDefinition(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'keyword':	 				[UnicodeDataType,		True, 	None, 	'Machine-readable keyword under which the license will be referenced from the individual fonts.'],
		'name':	 					[MultiLanguageTextProxy,		True, 	None, 	'Human-readable name of font license'],
		'URL':	 					[WebURLDataType,		True, 	None, 	'URL where the font license text can be viewed online'],
	}

	def __repr__(self):
		return '<LicenseDefinition "%s">' % self.name or self.keyword or 'undefined'

def LicenseDefinition_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
LicenseDefinition.parent = property(lambda self: LicenseDefinition_Parent(self))

class LicenseDefinitionProxy(Proxy):
	dataType = LicenseDefinition

class LicenseDefinitionListProxy(ListProxy):
	dataType = LicenseDefinitionProxy



####################################################################################################################################

#  LicenseUsage

class LicenseUsage(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {

		'keyword':						[UnicodeDataType,		True, 	None, 	'Keyword reference of font’s license. This license must be specified in ::Foundry.licenses::'],
		'seatsAllowedForUser':			[IntegerDataType,		False, 	None, 	'In case of desktop font (see ::Font.purpose::), number of installations permitted by the user’s license.'],
		'seatsInstalledByUser':			[IntegerDataType,		False, 	None, 	'In case of desktop font (see ::Font.purpose::), number of installations recorded by the API endpoint. This value will need to be supplied dynamically by the API endpoint through tracking all font installations through the "anonymousAppID" parameter of the "%s" and "%s" command. Please note that the Type.World client app is currently not designed to reject installations of the fonts when the limits are exceeded. Instead it is in the responsibility of the API endpoint to reject font installations though the "%s" command when the limits are exceeded. In that case the user will be presented with one or more license upgrade links.' % (INSTALLFONTCOMMAND['keyword'], UNINSTALLFONTCOMMAND['keyword'], INSTALLFONTCOMMAND['keyword'])],
		'allowanceDescription':			[MultiLanguageTextProxy,False, 	None, 	'In case of non-desktop font (see ::Font.purpose::), custom string for web fonts or app fonts reminding the user of the license’s limits, e.g. "100.000 page views/month"'],
		'upgradeURL':					[WebURLDataType,		False, 	None, 	'URL the user can be sent to to upgrade the license of the font, for instance at the foundry’s online shop. If possible, this link should be user-specific and guide him/her as far into the upgrade process as possible.'],
		'dateAddedForUser':				[DateDataType,			False, 	None, 	'Date that the user has purchased this font or the font has become available to the user otherwise (like a new font within a foundry’s beta font repository). Will be used in the UI to signal which fonts have become newly available in addition to previously available fonts. This is not to be confused with the ::Version.releaseDate::, although they could be identical.'],
	}

	def __repr__(self):
		return '<LicenseUsage "%s">' % self.keyword or 'undefined'

	def customValidation(self):
		information, warnings, critical = [], [], []

		# Checking for existing license
		if not self.getLicense():
			critical.append('%s has license "%s", but %s has no matching license.' % (self, self.keyword, self.parent.parent.parent))

		return information, warnings, critical

	def getLicense(self):
		'''\
		Returns the ::License:: object that this font references.
		'''
		return self.parent.parent.parent.getLicenseByKeyword(self.keyword)

def LicenseUsage_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
LicenseUsage.parent = property(lambda self: LicenseUsage_Parent(self))

class LicenseUsageProxy(Proxy):
	dataType = LicenseUsage

class LicenseUsageListProxy(ListProxy):
	dataType = LicenseUsageProxy



####################################################################################################################################

#  Designer

class Designer(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'keyword':	 				[UnicodeDataType,		True, 	None, 	'Machine-readable keyword under which the designer will be referenced from the individual fonts or font families'],
		'name':	 					[MultiLanguageTextProxy,		True, 	None, 	'Human-readable name of designer'],
		'website':	 				[WebURLDataType,		False, 	None, 	'Designer’s web site'],
		'description':	 			[MultiLanguageLongTextProxy,		False, 	None, 	'Description of designer'],
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
		'number':	 				[VersionDataType,			True, 	None, 	'Font version number. This can be a simple float number (1.002) or a semver version string (see https://semver.org). For comparison, single-dot version numbers (or even integers) are appended with another .0 (1.0 to 1.0.0), then compared using the Python `semver` module.'],
		'description':	 			[MultiLanguageLongTextProxy,	False, 	None, 	'Description of font version'],
		'releaseDate':	 			[DateDataType,				False, 	None, 	'Font version’s release date.'],
	}

	def __repr__(self):
		return '<Version %s (%s)>' % (self.number if self.number else 'None', 'font-specific' if self.isFontSpecific() else 'family-specific')

	def isFontSpecific(self):
		'''\
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
		'name':	 			[MultiLanguageTextProxy,		True, 	None, 	'Human-readable name of font. This may include any additions that you find useful to communicate to your users.'],
		'uniqueID':			[StringDataType,		True, 	None, 	'A machine-readable string that uniquely identifies this font within the publisher. It will be used to ask for un/installation of the font from the server in the `installFont` and `uninstallFont` commands. Also, it will be used for the file name of the font on disk, together with the version string and the file extension. Together, they must not be longer than 255 characters and must not contain the following characters: / ? < > \\ : * | ^'],
		'postScriptName':	[UnicodeDataType,		True, 	None, 	'Complete PostScript name of font'],
#		'previewImage':		[WebResourceURLDataType,False, 	None, 	'URL of preview image of font, specifications to follow.'],
		'setName':			[MultiLanguageTextProxy,False, 	None, 	'Optional set name of font. This is used to group fonts in the UI. Think of fonts here that are of identical technical formats but serve different purposes, such as "Office Fonts" vs. "Desktop Fonts".'],
		'versions':	 		[VersionListProxy,		False, 	None, 	'List of ::Version:: objects. These are font-specific versions; they may exist only for this font. You may define additional versions at the family object under ::Family.versions::, which are then expected to be available for the entire family. However, either the fonts or the font family *must* carry version information and the validator will complain when they don’t.\n\nPlease also read the section on [versioning](#versioning) above.'],
		'designers':	 	[DesignersReferencesListProxy,	False, 	None, 	'List of keywords referencing designers. These are defined at ::InstallableFontsResponse.designers::. This attribute overrides the designer definitions at the family level at ::Family.designers::.'],
		'free':				[BooleanDataType,		False, 	None, 	'Font is freeware. For UI signaling'],
		'status':			[FontStatusDataType,	True, 	'stable','Font status. For UI signaling. Possible values are: %s' % FONTSTATUSES],
		'variableFont':		[BooleanDataType,		False, 	None, 	'Font is an OpenType Variable Font. For UI signaling'],
		'purpose':			[FontPurposeDataType,	True, 	None, 	'Technical purpose of font. This influences how the app handles the font. For instance, it will only install desktop fonts on the system, and make other font types available though folders. Possible: %s' % (list(FONTPURPOSES.keys()))],
		'format':			[FontExtensionDataType,	False, 	None, 	'Font file format. Required value in case of `desktop` font (see ::Font.purpose::. Possible: %s' % FILEEXTENSIONS],
		'protected':		[BooleanDataType,		False, 	False, 	'Indication that the server requires a valid subscriptionID to be used for authentication. The server *may* limit the downloads of fonts. This may also be used for fonts that are free to download, but their installations want to be tracked/limited anyway. Most importantly, this indicates that the uninstall command needs to be called on the API endpoint when the font gets uninstalled.'],
		'dateFirstPublished':[DateDataType,			False, 	None, 	'Date of the initial release of the font. May also be defined family-wide at ::Family.dateFirstPublished::.'],
		'usedLicenses':	 	[LicenseUsageListProxy,	True, 	None, 	'List of ::LicenseUsage:: objects. These licenses represent the different ways in which a user has access to this font. At least one used license must be defined here, because a user needs to know under which legal circumstances he/she is using the font. Several used licenses may be defined for a single font in case a customer owns several licenses that cover the same font. For instance, a customer could have purchased a font license standalone, but also as part of the foundry’s entire catalogue. It’s important to keep these separate in order to provide the user with separate upgrade links where he/she needs to choose which of several owned licenses needs to be upgraded. Therefore, in case of a commercial retail foundry, used licenses correlate to a user’s purchase history.'],
		'pdf':				[WebResourceURLDataType,False, 	None, 	'URL of PDF file with type specimen and/or instructions for this particular font. (See also: ::Family.pdf::'],
	}

	def __repr__(self):
		return '<Font "%s">' % (self.postScriptName or self.name.getText() or 'undefined')

	def filename(self, version):
		'''\
		Returns the recommended font file name to be used to store the font on disk.

		It is composed of the font’s uniqueID, its version string and the file extension. Together, they must not exceed 255 characters.
		'''
		if self.format:
			return '%s_%s.%s' % (self.uniqueID, version, self.format)
		else:
			return '%s_%s' % (self.uniqueID, version)

	def hasVersionInformation(self):
		return self.versions or self.parent.versions

	def customValidation(self):
		information, warnings, critical = [], [], []

		# Checking font type/extension
		if self.purpose == 'desktop' and not self.format:
			critical.append('The font %s is a desktop font (see .purpose), but has no .format value.' % (self))

		# Checking version information
		if not self.hasVersionInformation():
			critical.append('The font %s has no version information, and neither has its family %s. Either one needs to carry version information.' % (self, self.parent))

		# Checking for designers
		for designerKeyword in self.designers:
			if not self.parent.parent.parent.getDesignerByKeyword(designerKeyword):
				critical.append('%s has designer "%s", but %s.designers has no matching designer.' % (self, designerKeyword, self.parent.parent.parent))

		# Checking uniqueID for file name contradictions:
		forbidden = '/?<>\\:*|^'
		for char in forbidden:
			if self.uniqueID.count(char) > 0:
				critical.append("uniqueID must not contain the character %s because it will be used for the font's file name on disk." % char)

		for version in self.getVersions():
			filename = self.filename(version.number)
			if len(filename) > 255:
				critical.append("The suggested file name is longer than 255 characters: %s" % filename)

		return information, warnings, critical

	def getVersions(self):
		'''\
		Returns list of ::Version:: objects.

		This is the final list based on the version information in this font object as well as in its parent ::Family:: object. Please read the section about [versioning](#versioning) above.
		'''

		if not self.hasVersionInformation():
			raise ValueError('Font %s has no version information, and neither has its family %s. Either one needs to carry version information.' % (self, self.parent))


		def compare(a, b):
			return semver.compare(makeSemVer(a.number), makeSemVer(b.number))

		versions = []
		haveVersionNumbers = []
		for version in self.versions:
			versions.append(version)
			haveVersionNumbers.append(makeSemVer(version.number))
		for version in self.parent.versions:
			if not version.number in haveVersionNumbers:
				versions.append(version)
				haveVersionNumbers.append(makeSemVer(version.number))

		versions = sorted(versions, key=functools.cmp_to_key(compare))

		return versions

	def getDesigners(self):
		'''\
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
	dataType = WebResourceURLDataType

class Family(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'uniqueID':					[StringDataType,		True, 	None, 	'An string that uniquely identifies this family within the publisher.'],
		'name':	 					[MultiLanguageTextProxy,True, 	None, 	'Human-readable name of font family. This may include any additions that you find useful to communicate to your users.'],
		'description':	 			[MultiLanguageLongTextProxy,False, 	None, 	'Description of font family'],
		'billboards':	 			[BillboardListProxy,	False, 	None, 	'List of URLs pointing at images to show for this typeface, specifications to follow'],
		'designers':	 			[DesignersReferencesListProxy,	False, 	None, 	'List of keywords referencing designers. These are defined at ::InstallableFontsResponse.designers::. In case designers differ between fonts within the same family, they can also be defined at the font level at ::Font.designers::. The font-level references take precedence over the family-level references.'],

		'sourceURL':	 			[WebURLDataType,		False, 	None, 	'URL pointing to the source of a font project, such as a GitHub repository'],
		'issueTrackerURL':	 		[WebURLDataType,		False, 	None, 	'URL pointing to an issue tracker system, where users can debate about a typeface’s design or technicalities'],
		'inUseURL':	 				[WebURLDataType,		False, 	None, 	'URL pointing to a web site that shows real world examples of the fonts in use.'],
		'versions':	 				[VersionListProxy,		False, 	None, 	'List of ::Version:: objects. Versions specified here are expected to be available for all fonts in the family, which is probably most common and efficient. You may define additional font-specific versions at the ::Font:: object. You may also rely entirely on font-specific versions and leave this field here empty. However, either the fonts or the font family *must* carry version information and the validator will complain when they don’t.\n\nPlease also read the section on [versioning](#versioning) above.'],
		'fonts':	 				[FontListProxy,			True, 	None, 	'List of ::Font:: objects. The order will be displayed unchanged in the UI, so it’s in your responsibility to order them correctly.'],
		'dateFirstPublished':		[DateDataType,			False, 	None, 	'Date of the initial release of the family. May be overriden on font level at ::Font.dateFirstPublished::.'],
		'pdf':						[WebResourceURLDataType,False, 	None, 	'URL of PDF file with type specimen and/or instructions for entire family. May be overriden on font level at ::Font.pdf::.'],
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
		'''\
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

	def setNames(self, locale):
		setNames = []
		for font in self.fonts:
			if not font.setName.getText(locale) in setNames:
				setNames.append(font.setName.getText(locale))
		return setNames

	def formatsForSetName(self, setName, locale):
		formats = []
		for font in self.fonts:
			if font.setName.getText(locale) == setName:
				if not font.format in formats:
					formats.append(font.format)
		return formats


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
		'uniqueID':					[StringDataType,		True, 	None, 	'An string that uniquely identifies this foundry within the publisher.'],
		'name':	 					[MultiLanguageTextProxy,True, 	None, 	'Name of foundry'],
		'logo':	 					[WebResourceURLDataType,False, 	None, 	'URL of foundry’s logo. Specifications to follow.'],
		'description':	 			[MultiLanguageLongTextProxy,False, 	None, 	'Description of foundry'],
		'email':	 				[EmailDataType,			False, 	None, 	'General email address for this foundry.'],
		'website':	 				[WebURLDataType,		False, 	None, 	'Website for this foundry'],
		'twitter':	 				[UnicodeDataType,		False, 	None, 	'Twitter handle for this foundry, without the @'],
		'facebook':	 				[WebURLDataType,		False, 	None, 	'Facebook page URL handle for this foundry. The URL '],
		'instagram':	 			[UnicodeDataType,		False, 	None, 	'Instagram handle for this foundry, without the @'],
		'skype':	 				[UnicodeDataType,		False, 	None, 	'Skype handle for this foundry'],
		'telephone':	 			[UnicodeDataType,		False, 	None, 	'Telephone number for this foundry'],
		'supportEmail':	 			[EmailDataType,			False, 	None, 	'Support email address for this foundry.'],
		'supportWebsite':	 		[WebURLDataType,		False, 	None, 	'Support website for this foundry, such as a chat room, forum, online service desk.'],
		'supportTelephone':	 		[UnicodeDataType,		False, 	None, 	'Support telephone number for this foundry.'],

		#styling
		'backgroundColor': 			[HexColorDataType,		False, 	None, 	'Foundry’s preferred background color. This is meant to go as a background color to the logo at ::Foundry.logo::'],

		# data
		'licenses':					[LicenseDefinitionListProxy,True, 	None, 	'List of ::LicenseDefinition:: objects under which the fonts in this response are issued. For space efficiency, these licenses are defined at the foundry object and will be referenced in each font by their keyword. Keywords need to be unique for this foundry and may repeat across foundries.'],
		'families':					[FamiliesListProxy,		True, 	None, 	'List of ::Family:: objects.'],
	}

	def __repr__(self):
		return '<Foundry "%s">' % self.name.getText() or 'undefined'

	def getLicenseByKeyword(self, keyword):
		if not hasattr(self, '_licensesDict'):
			self._licensesDict = {}
			for license in self.licenses:
				self._licensesDict[license.keyword] = license

		if keyword in self._licensesDict:
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

#  Base Response

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


####################################################################################################################################

#  Available Fonts

class InstallableFontsResponseType(ResponseCommandDataType):
	def valid(self):
		if self.value in INSTALLABLEFONTSCOMMAND['responseTypes']:
			return True
		else:
			return 'Unknown response type: "%s". Possible: %s' % (self.value, INSTALLABLEFONTSCOMMAND['responseTypes'])

class InstallableFontsResponse(BaseResponse):
	'''\
	This is the response expected to be returned when the API is invoked using the `?command=installableFonts` parameter.

	```python
	# Create root object
	installableFonts = InstallableFontsResponse()

	# Add data to the command here
	# ...

	# Return the call’s JSON content to the HTTP request
	return installableFonts.dumpJSON()
	```

	'''
	# 	key: 					[data type, required, default value, description]
	_structure = {

		# Root
		'type': 			[InstallableFontsResponseType,	True, 	None, 	'Type of response. This can be any of %s. In case of "error", you may specify an additional message to be presented to the user under ::InstallableFontsResponse.errorMessage::.' % INSTALLABLEFONTSCOMMAND['responseTypes']],
		'errorMessage': 	[MultiLanguageTextProxy,		False, 	None, 	'Description of error in case of ::InstallableFontsResponse.type:: being "custom".'],
		'version': 			[VersionDataType,				True, 	INSTALLABLEFONTSCOMMAND['currentVersion'], 	'Version of "%s" response' % INSTALLABLEFONTSCOMMAND['keyword']],

		# Response-specific
		'designers':		[DesignersListProxy,			False, 	None, 	'List of ::Designer:: objects, referenced in the fonts or font families by the keyword. These are defined at the root of the response for space efficiency, as one designer can be involved in the design of several typefaces across several foundries.'],
		'foundries':		[FoundryListProxy,				True, 	None, 	'List of ::Foundry:: objects; foundries that this distributor supports. In most cases this will be only one, as many foundries are their own distributors.'],

		'name':				[MultiLanguageTextProxy,		False, 	None, 	'A name of this response and its contents. This is needed to manage subscriptions in the UI. For instance "Free Fonts" for all free and non-restricted fonts, or "Commercial Fonts" for all those fonts that the use has commercially licensed, so their access is restricted. In case of a free font website that offers individual subscriptions for each typeface, this decription could be the name of the typeface.'],
		'userName':			[MultiLanguageTextProxy,		False, 	None, 	'The name of the user who these fonts are licensed to.'],
		'userEmail':		[EmailDataType,					False, 	None, 	'The email address of the user who these fonts are licensed to.'],
		'prefersRevealedUserIdentity':	[BooleanDataType,	True, 	False, 	'Indicates that the publisher prefers to have the user reveal his/her identity to the publisher when installing fonts. In the app, the user will be asked via a dialog to turn the setting on, but is not required to do so.'],
	}


	def getDesignerByKeyword(self, keyword):
		if not hasattr(self, '_designersDict'):
			self._designersDict = {}
			for designer in self.designers:
				self._designersDict[designer.keyword] = designer

		if keyword in self._designersDict:
			return self._designersDict[keyword]

	def discardThisKey(self, key):
		
		if key in ['foundries', 'designers', 'licenseIdentifier'] and self.type != 'success':
			return True

		return False

	def customValidation(self):
		information, warnings, critical = [], [], []

		if self.type == 'success' and not self.name.getText():
			warnings.append('The response has no .name value. It is not required, but highly recommended, to describe the purpose of this subscription to the user (such as "Commercial Fonts", "Free Fonts", etc. This is especially useful if you offer several different subscriptions to the same user.')


		# Check all uniqueIDs for duplicity
		foundryIDs = []
		familyIDs = []
		fontIDs = []
		for foundry in self.foundries:
			foundryIDs.append(foundry.uniqueID)
			for family in foundry.families:
				familyIDs.append(family.uniqueID)
				for font in family.fonts:
					fontIDs.append(font.uniqueID)

		import collections

		duplicateFoundryIDs = [item for item, count in list(collections.Counter(foundryIDs).items()) if count > 1]
		if duplicateFoundryIDs:
			critical.append('Duplicate unique foundry IDs: %s' % duplicateFoundryIDs)

		duplicateFamilyIDs = [item for item, count in list(collections.Counter(familyIDs).items()) if count > 1]
		if duplicateFamilyIDs:
			critical.append('Duplicate unique family IDs: %s' % duplicateFamilyIDs)

		duplicateFontIDs = [item for item, count in list(collections.Counter(fontIDs).items()) if count > 1]
		if duplicateFontIDs:
			critical.append('Duplicate unique family IDs: %s' % duplicateFontIDs)


		return information, warnings, critical


####################################################################################################################################

#  InstallFont

class InstallFontResponseType(ResponseCommandDataType):
	def valid(self):
		if self.value in INSTALLFONTCOMMAND['responseTypes']:
			return True
		else:
			return 'Unknown response type: "%s". Possible: %s' % (self.value, INSTALLFONTCOMMAND['responseTypes'])

class InstallFontResponse(BaseResponse):
	'''\
	This is the response expected to be returned when the API is invoked using the `?command=installFonts` parameter.

	```python
	# Create root object
	installFonts = InstallFontResponse()

	# Add data to the command here
	# ...

	# Return the call’s JSON content to the HTTP request
	return installFonts.dumpJSON()
	```

	'''

	# 	key: 					[data type, required, default value, description]
	_structure = {

		# Root
		'type': 			[InstallFontResponseType,	True, 	None, 	'Type of response. This can be any of %s. In case of "error", you may specify an additional message to be presented to the user under ::InstallFontResponse.errorMessage::.' % INSTALLFONTCOMMAND['responseTypes']],
		'errorMessage': 	[MultiLanguageTextProxy,	False, 	None, 	'Description of error in case of custom response type'],
		'version': 			[VersionDataType,			True, 	INSTALLFONTCOMMAND['currentVersion'], 	'Version of "%s" response' % INSTALLFONTCOMMAND['keyword']],

		'font': 			[FontDataType,				False, 	None, 	'Binary font data encoded to a string using ::InstallFontResponse.encoding::'],
		'encoding': 		[FontEncodingDataType,		False, 	None, 	'Encoding type for binary font data. Currently supported: %s' % (FONTENCODINGS)],
		'fileName':			[UnicodeDataType, 			False, 	None, 	'Suggested file name of font. This may be ignored by the app in favour of a unique file name.'],

		}

	def customValidation(self):

		information, warnings, critical = [], [], []

		if self.type == 'success' and not self.font:
			critical.append('%s.type is set to success, but %s.font is missing' % (self, self))

		if self.font and not self.encoding:
			critical.append('%s.font is set, but %s.encoding is missing' % (self, self))

		return information, warnings, critical


####################################################################################################################################

#  Uninstall Fonts

class UninstallFontResponseType(ResponseCommandDataType):
	def valid(self):
		if self.value in UNINSTALLFONTCOMMAND['responseTypes']:
			return True
		else:
			return 'Unknown response type: "%s". Possible: %s' % (self.value, UNINSTALLFONTCOMMAND['responseTypes'])

class UninstallFontResponse(BaseResponse):
	'''\
	This is the response expected to be returned when the API is invoked using the `?command=uninstallFonts` parameter.

	```python
	# Create root object
	uninstallFonts = UninstallFontResponse()

	# Add data to the command here
	# ...

	# Return the call’s JSON content to the HTTP request
	return uninstallFonts.dumpJSON()
	```

	'''
	# 	key: 					[data type, required, default value, description]

	_structure = {

		# Root
		'type': 			[UninstallFontResponseType,	True, 	None, 	'Type of response. This can be any of %s. In case of "error", you may specify an additional message to be presented to the user under ::UninstallFontResponse.errorMessage::.' % UNINSTALLFONTCOMMAND['responseTypes']],
		'errorMessage': 	[MultiLanguageTextProxy,	False, 	None, 	'Description of error in case of custom response type'],
		'version': 			[VersionDataType,			True, 	UNINSTALLFONTCOMMAND['currentVersion'], 	'Version of "%s" response' % UNINSTALLFONTCOMMAND['keyword']],

		# Response-specific
		}


####################################################################################################################################

#  SetAnonymousAppIDStatus

class SetAnonymousAppIDStatusResponseType(ResponseCommandDataType):
	def valid(self):
		if self.value in SETANONYMOUSAPPIDSTATUSCOMMAND['responseTypes']:
			return True
		else:
			return 'Unknown response type: "%s". Possible: %s' % (self.value, SETANONYMOUSAPPIDSTATUSCOMMAND['responseTypes'])

class SetAnonymousAppIDStatusResponse(BaseResponse):
	# 	key: 					[data type, required, default value, description]
	_structure = {

		# Root
		'type': 			[InstallFontResponseType,	True, 	None, 	'Type of response. This can be any of %s. In case of "error", you may specify an additional message to be presented to the user under ::InstallFontResponse.errorMessage::.' % SETANONYMOUSAPPIDSTATUSCOMMAND['responseTypes']],
		'errorMessage': 	[MultiLanguageTextProxy,	False, 	None, 	'Description of error in case of custom response type'],
		'version': 			[VersionDataType,			True, 	SETANONYMOUSAPPIDSTATUSCOMMAND['currentVersion'], 	'Version of "%s" response' % SETANONYMOUSAPPIDSTATUSCOMMAND['keyword']],
		}


####################################################################################################################################


class RootResponse(BaseResponse):
	'''\
This is the main class that sits at the root of all API responses. It contains some mandatory information about the API endpoint such as its name and admin email, the copyright license under which the API endpoint issues its data, and whether or not this endpoint can be publicized about.

Any API response is expected to carry this minimum information, even when invoked without a particular command.

In case the API endpoint has been invoked with a particular command, the response data is attached to the ::APIRoot.response:: attribute.


```python
response = RootResponse()
response.name.en = u'Font Publisher'
response.canonicalURL = 'https://fontpublisher.com/api/'
response.adminEmail = 'admin@fontpublisher.com'
response.supportedCommands = ['installableFonts', 'installFonts', 'uninstallFonts']
```

	'''


	# 	key: 					[data type, required, default value, description]
	_structure = {
		'canonicalURL': 		[WebURLDataType, 			True, 	None, 	'Official API endpoint URL, bare of ID keys and other parameters. Used for grouping of subscriptions. It is expected that this URL will not change. When it does, it will be treated as a different publisher.'],
		'adminEmail': 			[EmailDataType, 			True, 	None, 	'API endpoint Administrator. This email needs to be reachable for various information around the Type.World protocol as well as technical problems.'],
		'licenseIdentifier':	[OpenSourceLicenseIdentifierDataType,True, 	'CC-BY-NC-ND-4.0', 	'Identifier of license under which the API endpoint publishes its data, as per [https://spdx.org/licenses/](). This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. Licenses of the individual responses can be fine-tuned in the respective responses.'],
		'supportedCommands': 	[SupportedAPICommandsListProxy, True, 	None, 	'List of commands this API endpoint supports: %s' % [x['keyword'] for x in COMMANDS]],
		'name': 				[MultiLanguageTextProxy, 	True, 	None, 	'Human-readable name of API endpoint'],
		'public': 				[BooleanDataType, 			True, 	False, 	'API endpoint is meant to be publicly visible and its existence may be publicized within the project'],
		'logo': 				[WebResourceURLDataType, 	False, 	None, 	'URL of logo of API endpoint, for publication. Specifications to follow.'],
		'backgroundColor': 		[HexColorDataType,			False, 	None, 	'Publisher’s preferred background color. This is meant to go as a background color to the logo at ::APIRoot.logo::'],
		'website': 				[WebURLDataType, 			False, 	None, 	'URL of human-visitable website of API endpoint, for publication'],
		'privacyPolicy': 		[WebURLDataType, 			True, 	'https://type.world/legal/default/PrivacyPolicy.html', 	'URL of human-readable Privacy Policy of API endpoint. This will be displayed to the user for consent when adding a subscription. The default URL points to a document edited by Type.World that you can use (at your own risk) instead of having to write your own.\n\nThe link will open with a `locales` parameter containing a comma-separated list of the user’s preferred UI languages and a `canonicalURL` parameter containing the subscription’s canonical URL and a `subscriptionID` parameter containing the anonymous subscription ID.'],
		'termsOfServiceAgreement': [WebURLDataType, 		True, 	'https://type.world/legal/default/TermsOfService.html', 	'URL of human-readable Terms of Service Agreement of API endpoint. This will be displayed to the user for consent when adding a subscription. The default URL points to a document edited by Type.World that you can use (at your own risk) instead of having to write your own.\n\nThe link will open with a `locales` parameter containing a comma-separated list of the user’s preferred UI languages and a `canonicalURL` parameter containing the subscription’s canonical URL and a `subscriptionID` parameter containing the anonymous subscription ID.'],
		'version': 			[VersionDataType,			True, 	INSTALLFONTCOMMAND['currentVersion'], 	'Version of "%s" response' % INSTALLFONTCOMMAND['keyword']],
	}


	def customValidation(self):
		'''\
		Return three lists with informations, warnings, and errors.

		An empty errors list is regarded as a successful validation, otherwise the validation is regarded as a failure.
		'''
		information, warnings, critical = [], [], []

		if self.canonicalURL and not self.canonicalURL.startswith('https://'):
			warnings.append('%s.canonicalURL is not using SSL (https://). Consider using SSL to protect your data.' % (self))

		return information, warnings, critical


