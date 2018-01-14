

# typeWorld.api Reference

1. [List of Classes](#classTOC)
2. [Introduction](#introduction)
3. [Versioning](#versioning)
4. [Object model](#objectmodel)
5. [Class Reference](#classreference)



## List of Classes

<div id="classTOC"></div>

- [APIRoot](#class_APIRoot)<br />
- [MultiLanguageText](#class_MultiLanguageText)<br />
- [Response](#class_Response)<br />
- [InstallableFontsResponse](#class_InstallableFontsResponse)<br />
- [Foundry](#class_Foundry)<br />
- [Family](#class_Family)<br />
- [Version](#class_Version)<br />
- [Font](#class_Font)<br />
- [License](#class_License)<br />
- [Designer](#class_Designer)<br />
- [UninstallFontsResponse](#class_UninstallFontsResponse)<br />
- [InstallFontsResponse](#class_InstallFontsResponse)<br />





<div id="introduction"></div>

## Introduction

The Type.World API is designed to be installed on web servers and allow a font installer app, such as the upcoming GUI app under the same name, to load and install fonts on people’s computers through a one-click process involving a custom URI such as typeworld://

Requires `deepdiff` for recursive dictionary comparison, but only if you wish to compare two instances of `APIRoot()` objects. You can install it through `pip`:

```sh
pip install deepdiff
```

First, we import the Type.World module:

```python
from typeWorld.api import *
```

Below you see the minimum possible object tree for a sucessful response.

```python
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
```

Will output the following JSON code:

```json
{
  "canonicalURL": "https://fontpublisher.com/api/", 
  "adminEmail": "admin@fontpublisher.com", 
  "public": false, 
  "supportedCommands": [
    "installableFonts", 
    "installFonts", 
    "uninstallFonts"
  ], 
  "licenseIdentifier": "CC-BY-NC-ND-4.0", 
  "response": {
    "command": "installableFonts", 
    "installableFonts": {
      "designers": [
        {
          "name": {
            "en": "Max Mustermann"
          }, 
          "keyword": "max"
        }
      ], 
      "version": 0.1, 
      "type": "success", 
      "foundries": [
        {
          "website": "https://awesomefonts.com", 
          "licenses": [
            {
              "URL": "https://awesomefonts.com/eula/", 
              "name": {
                "en": "Awesome Fonts Desktop EULA"
              }, 
              "keyword": "awesomeFontsEULA"
            }
          ], 
          "families": [
            {
              "designers": [
                "max"
              ], 
              "fonts": [
                {
                  "postScriptName": "AwesomeSans-Regular", 
                  "licenseKeyword": "awesomeFontsEULA", 
                  "name": {
                    "en": "Regular"
                  }, 
                  "type": "desktop"
                }
              ], 
              "name": {
                "en": "Awesome Sans"
              }, 
              "versions": [
                {
                  "number": 0.1
                }
              ]
            }
          ], 
          "name": {
            "en": "Awesome Fonts"
          }
        }
      ]
    }
  }, 
  "name": {
    "en": "Font Publisher"
  }
}
```

Next we load that same JSON code back into an object tree, such as the GUI app would do when it loads the JSON from font publisher’s API endpoints.

```python
# Load a second API instance from that JSON
api2 = APIRoot()
api2.loadJSON(json)

# Let’s see if they are identical (requires deepdiff)
print api == api2
```


Will, or should print:

```python
True
```


<div id="objectmodel"></div>

## Object model

![](../../../object-model.png)



<div id="versioning"></div>

## Versioning

Every type producer has different habits when it comes to versioning of fonts. Most people would update all fonts of the family to the new version, others would only tweak a few fonts.

To accommodate all of these habits, the Type.World API supports version information in two places. However, the entire system relies on version numbers being specified as float numbers, making them mathematically comparable for sorting. Higher numbers mean newer versions.

#### Versions at the [Family](#class_Family) level

The [Family.versions](#class_Family_attribute_versions) attribute can carry a list of [Version](#class_Version) objects. Versions that you specify here are expected to be present throughout the entire family; meaning that the complete amount of all fonts in all versions is the result of a multiplication of the number of fonts with the number of versions.

#### Versions at the [Font](#class_Font) level

In addition to that, you may also specify a list of [Version](#class_Version) objects at the [Font.versions](#class_Font_attribute_versions) attribute. Versions that you specify here are expected to be available only for this font. 

When versions defined here carry the same version number as versions defined at the family level, the font-specific versions take precedence over the family-specific versions.

You may define a smaller amount of versions here than at the family level. In this case it is still assumed that all those versions which are defined at the family level but not at the font level are available for this font, with the versions defined at the font being available additionally.

You may also define a larger amount of versions here than at the family level. In this case it is assumed that the font carries versions that are not available for the entire family.

This leaves us with four different scenarios for defining versions:

#### 1. Versions only defined at family level

Each font is expected to be available in all the versions defined at the family level.

#### 2. Versions only defined at font level

Each font is expected to be available in just the versions defined at each individual font. Therefore, a single font can contain completely individual version numbers and descriptions.

#### 3. Versions are defined at family and font level

Each font is expected to be available in all the versions defined at the family level.

Additionally, font-level definitions can overwrite versions defined at family level when they use the same version number. This makes sense when only the description of a font-level version needs to differ from the same version number’s family-level description.

Additionally, individual font-level definitions may add versions not defined at the family level.

#### Use [Font.getSortedVersions()](#class_Font_method_getSortedVersions)

Because in the end the versions matter only at the font level, the [Font.getSortedVersions()](#class_Font_method_getSortedVersions) method will output the final list of versions in the above combinations, with font-level definitions taking precedence over family-level definitions.


<div id="classreference"></div>

## Class Reference




<div id="class_APIRoot"></div>

# _class_ APIRoot()

This is the main class that sits at the root of all API responses. It contains some mandatory information about the API endpoint such as its name and admin email, the copyright license under which the API endpoint issues its data, and whether or not this endpoint can be publicized about.

Any API response is expected to carry this minimum information, even when invoked without a particular command.

In case the API endpoint has been invoked with a particular command, the response data is attached to the [APIRoot.response](#class_APIRoot_attribute_response) attribute.


```python
api = APIRoot()
api.name.en = u'Font Publisher'
api.canonicalURL = 'https://fontpublisher.com/api/'
api.adminEmail = 'admin@fontpublisher.com'
api.supportedCommands = ['installableFonts', 'installFonts', 'uninstallFonts']
```

        

### Attributes

[adminEmail](#class_APIRoot_attribute_adminEmail)<br />[canonicalURL](#class_APIRoot_attribute_canonicalURL)<br />[licenseIdentifier](#class_APIRoot_attribute_licenseIdentifier)<br />[logo](#class_APIRoot_attribute_logo)<br />[name](#class_APIRoot_attribute_name)<br />[public](#class_APIRoot_attribute_public)<br />[response](#class_APIRoot_attribute_response)<br />[supportedCommands](#class_APIRoot_attribute_supportedCommands)<br />[website](#class_APIRoot_attribute_website)<br />

### Methods

[sameContent()](#class_APIRoot_method_sameContent)<br />[validate()](#class_APIRoot_method_validate)<br />

## Attributes

<div id="class_APIRoot_attribute_adminEmail"></div>

#### adminEmail

API endpoint Administrator, to contact for technical problems and such

Type: Unicode<br />
Required: True<br />
<div id="class_APIRoot_attribute_canonicalURL"></div>

#### canonicalURL

Official API endpoint URL, bare of ID keys and other parameters. Used for grouping of subscriptions. It is expected that this URL will not change.

Type: Unicode<br />
Required: True<br />
<div id="class_APIRoot_attribute_licenseIdentifier"></div>

#### licenseIdentifier

Identifier of license under which the API endpoint publishes its data, as per [https://spdx.org/licenses/](). This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. Licenses of the individual responses can be fine-tuned in the respective responses.

Type: Unicode<br />
Required: True<br />
Default value: CC-BY-NC-ND-4.0

<div id="class_APIRoot_attribute_logo"></div>

#### logo

URL of logo of API endpoint, for publication. Specifications to follow.

Type: Unicode<br />
Required: False<br />
<div id="class_APIRoot_attribute_name"></div>

#### name

Human-readable name of API endpoint

Type: [MultiLanguageText](#class_MultiLanguageText)<br />
Required: True<br />
<div id="class_APIRoot_attribute_public"></div>

#### public

API endpoint is meant to be publicly visible and its existence may be publicized within the project

Type: Bool<br />
Required: True<br />
Default value: False

<div id="class_APIRoot_attribute_response"></div>

#### response

Response of the API call

Type: [Response](#class_Response)<br />
Required: False<br />
<div id="class_APIRoot_attribute_supportedCommands"></div>

#### supportedCommands

List of commands this API endpoint supports: ['installableFonts', 'installFonts', 'uninstallFonts']

Type: List of Unicode objects<br />
Required: True<br />
<div id="class_APIRoot_attribute_website"></div>

#### website

URL of human-visitable website of API endpoint, for publication

Type: Unicode<br />
Required: False<br />


## Methods

<div id="class_APIRoot_method_sameContent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.

<div id="class_APIRoot_method_validate"></div>

#### validate()

Return three lists with informations, warnings, and errors.

An empty errors list is regarded as a successful validation, otherwise the validation is regarded as a failure.





<div id="class_MultiLanguageText"></div>

# _class_ MultiLanguageText()

Multi-language text. Attributes are language keys as per [https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes]

The GUI app will then calculate the language data to be displayed using [MultiLanguageText.getText()](#class_MultiLanguageText_method_getText) with a prioritized list of languages that the user can understand. They may be pulled from the operating system’s language preferences.

These classes are already initiated wherever they are used, and can be addresses instantly with the language attributes:

```python
api.name.en = u'Font Publisher XYZ'
api.name.de = u'Schriftenhaus XYZ'
```

If you are loading language information from an external source, you may use the `.set()` method to enter data:

```python
# Simulating external data source
for languageCode, text in (
                ('en': u'Font Publisher XYZ'),
                ('de': u'Schriftenhaus XYZ'),
        )
        api.name.set(languageCode, text)
```

### Methods

[getText()](#class_MultiLanguageText_method_getText)<br />

## Methods

<div id="class_MultiLanguageText_method_getText"></div>

#### getText(locale = ['en'])

Returns the text in the first language found from the specified list of languages. If that language can’t be found, we’ll try English as a standard. If that can’t be found either, return the first language you can find.





<div id="class_Response"></div>

# _class_ Response()



### Attributes

[command](#class_Response_attribute_command)<br />[installFonts](#class_Response_attribute_installFonts)<br />[installableFonts](#class_Response_attribute_installableFonts)<br />[uninstallFonts](#class_Response_attribute_uninstallFonts)<br />

### Methods

[getCommand()](#class_Response_method_getCommand)<br />

## Attributes

<div id="class_Response_attribute_command"></div>

#### command

Command code of the response. The specific response must then be present under an attribute of same name.

Type: Unicode<br />
Required: True<br />
<div id="class_Response_attribute_installFonts"></div>

#### installFonts

Type: [InstallFontsResponse](#class_InstallFontsResponse)<br />
Required: False<br />
<div id="class_Response_attribute_installableFonts"></div>

#### installableFonts

Type: [InstallableFontsResponse](#class_InstallableFontsResponse)<br />
Required: False<br />
<div id="class_Response_attribute_uninstallFonts"></div>

#### uninstallFonts

Type: [UninstallFontsResponse](#class_UninstallFontsResponse)<br />
Required: False<br />


## Methods

<div id="class_Response_method_getCommand"></div>

#### getCommand()

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





<div id="class_InstallableFontsResponse"></div>

# _class_ InstallableFontsResponse()

This is the response expected to be returned when the API is invoked using the command parameter, such as `http://fontpublisher.com/api/?command=installableFonts`.

The response needs to be specified at the [Response.command](#class_Response_attribute_command) attribute, and then the [Response](#class_Response) object needs to carry the specific response command at the attribute of same name, in this case [Reponse.installableFonts](#class_Reponse_attribute_installableFonts).

```python
api.response = Response()
api.response.command = 'installableFonts'
api.response.installableFonts = InstallableFontsResponse()
```

### Attributes

[customMessage](#class_InstallableFontsResponse_attribute_customMessage)<br />[designers](#class_InstallableFontsResponse_attribute_designers)<br />[foundries](#class_InstallableFontsResponse_attribute_foundries)<br />[licenseIdentifier](#class_InstallableFontsResponse_attribute_licenseIdentifier)<br />[type](#class_InstallableFontsResponse_attribute_type)<br />[version](#class_InstallableFontsResponse_attribute_version)<br />

## Attributes

<div id="class_InstallableFontsResponse_attribute_customMessage"></div>

#### customMessage

Description of error in case of [InstallableFontsResponse.type](#class_InstallableFontsResponse_attribute_type) being "custom".

Type: [MultiLanguageText](#class_MultiLanguageText)<br />
Required: False<br />
<div id="class_InstallableFontsResponse_attribute_designers"></div>

#### designers

List of [Designer](#class_Designer) objects, referenced in the fonts or font families by the keyword. These are defined at the root of the response for space efficiency, as one designer can be involved in the design of several typefaces across several foundries.

Type: List of [Designer](#class_Designer) objects<br />
Required: False<br />
<div id="class_InstallableFontsResponse_attribute_foundries"></div>

#### foundries

List of [Foundry](#class_Foundry) objects; foundries that this distributor supports. In most cases this will be only one, as many foundries are their own distributors.

Type: List of [Foundry](#class_Foundry) objects<br />
Required: True<br />
<div id="class_InstallableFontsResponse_attribute_licenseIdentifier"></div>

#### licenseIdentifier

Identifier of license under which the API endpoint publishes this particular response, as per [https://spdx.org/licenses/](). This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. This license can be different from the license at the root of the response. The idea is that different responses can be issued under different licenses, depending on their use scenario. If not specified, the root license is assumed.

Type: Unicode<br />
Required: False<br />
Default value: CC-BY-NC-ND-4.0

<div id="class_InstallableFontsResponse_attribute_type"></div>

#### type

Type of response. This can be "success", "error", or "custom". In case of "custom", you may specify an additional message to be presented to the user under [InstallableFontsResponse.customMessage](#class_InstallableFontsResponse_attribute_customMessage).

Type: Unicode<br />
Required: True<br />
<div id="class_InstallableFontsResponse_attribute_version"></div>

#### version

Version of "installableFonts" response

Type: Float<br />
Required: True<br />
Default value: 0.1





<div id="class_Foundry"></div>

# _class_ Foundry()



### Attributes

[backgroundColor](#class_Foundry_attribute_backgroundColor)<br />[description](#class_Foundry_attribute_description)<br />[email](#class_Foundry_attribute_email)<br />[facebook](#class_Foundry_attribute_facebook)<br />[families](#class_Foundry_attribute_families)<br />[instagram](#class_Foundry_attribute_instagram)<br />[licenses](#class_Foundry_attribute_licenses)<br />[logo](#class_Foundry_attribute_logo)<br />[name](#class_Foundry_attribute_name)<br />[skype](#class_Foundry_attribute_skype)<br />[supportEmail](#class_Foundry_attribute_supportEmail)<br />[telephone](#class_Foundry_attribute_telephone)<br />[twitter](#class_Foundry_attribute_twitter)<br />[website](#class_Foundry_attribute_website)<br />

## Attributes

<div id="class_Foundry_attribute_backgroundColor"></div>

#### backgroundColor

Six-digit RRGGBB hex color value (without leading "#") for foundry’s preferred background color

Type: Str<br />
Required: False<br />
<div id="class_Foundry_attribute_description"></div>

#### description

Description of foundry

Type: [MultiLanguageText](#class_MultiLanguageText)<br />
Required: False<br />
<div id="class_Foundry_attribute_email"></div>

#### email

General email address for this foundry

Type: Unicode<br />
Required: False<br />
<div id="class_Foundry_attribute_facebook"></div>

#### facebook

Facebook page URL handle for this foundry. The URL 

Type: Unicode<br />
Required: False<br />
<div id="class_Foundry_attribute_families"></div>

#### families

List of [Family](#class_Family) objects.

Type: List of [Family](#class_Family) objects<br />
Required: True<br />
<div id="class_Foundry_attribute_instagram"></div>

#### instagram

Instagram handle for this foundry, without the @

Type: Unicode<br />
Required: False<br />
<div id="class_Foundry_attribute_licenses"></div>

#### licenses

List of [License](#class_License) objects under which the fonts in this response are issued. For space efficiency, these licenses are defined at the foundry object and will be referenced in each font by their keyword. Keywords need to be unique for this foundry and may repeat across foundries.

Type: List of [License](#class_License) objects<br />
Required: True<br />
<div id="class_Foundry_attribute_logo"></div>

#### logo

URL of foundry’s logo. Specifications to follow.

Type: Unicode<br />
Required: False<br />
<div id="class_Foundry_attribute_name"></div>

#### name

Name of foundry

Type: [MultiLanguageText](#class_MultiLanguageText)<br />
Required: True<br />
<div id="class_Foundry_attribute_skype"></div>

#### skype

Skype handle for this foundry

Type: Unicode<br />
Required: False<br />
<div id="class_Foundry_attribute_supportEmail"></div>

#### supportEmail

Support email address for this foundry

Type: Unicode<br />
Required: False<br />
<div id="class_Foundry_attribute_telephone"></div>

#### telephone

Telephone number for this foundry

Type: Unicode<br />
Required: False<br />
<div id="class_Foundry_attribute_twitter"></div>

#### twitter

Twitter handle for this foundry, without the @

Type: Unicode<br />
Required: False<br />
<div id="class_Foundry_attribute_website"></div>

#### website

Website for this foundry

Type: Unicode<br />
Required: False<br />




<div id="class_Family"></div>

# _class_ Family()



### Attributes

[billboards](#class_Family_attribute_billboards)<br />[description](#class_Family_attribute_description)<br />[designers](#class_Family_attribute_designers)<br />[fonts](#class_Family_attribute_fonts)<br />[issueTrackerURL](#class_Family_attribute_issueTrackerURL)<br />[name](#class_Family_attribute_name)<br />[sourceURL](#class_Family_attribute_sourceURL)<br />[versions](#class_Family_attribute_versions)<br />

### Methods

[getAllDesigners()](#class_Family_method_getAllDesigners)<br />

## Attributes

<div id="class_Family_attribute_billboards"></div>

#### billboards

List of URLs pointing at images to show for this typeface, specifications to follow

Type: List of Unicode objects<br />
Required: False<br />
<div id="class_Family_attribute_description"></div>

#### description

Description of font family

Type: [MultiLanguageText](#class_MultiLanguageText)<br />
Required: False<br />
<div id="class_Family_attribute_designers"></div>

#### designers

List of keywords referencing designers. These are defined at [InstallableFontsResponse.designers](#class_InstallableFontsResponse_attribute_designers). In case designers differ between fonts within the same family, they can also be defined at the font level at [Font.designers](#class_Font_attribute_designers). The font-level references take precedence over the family-level references.

Type: List of Unicode objects<br />
Required: False<br />
<div id="class_Family_attribute_fonts"></div>

#### fonts

List of [Font](#class_Font) objects.

Type: List of [Font](#class_Font) objects<br />
Required: True<br />
<div id="class_Family_attribute_issueTrackerURL"></div>

#### issueTrackerURL

URL pointing to an issue tracker system, where users can debate about a typeface’s design or technicalities

Type: Unicode<br />
Required: False<br />
<div id="class_Family_attribute_name"></div>

#### name

Human-readable name of font family. This may include any additions that you find useful to communicate to your users.

Type: [MultiLanguageText](#class_MultiLanguageText)<br />
Required: True<br />
<div id="class_Family_attribute_sourceURL"></div>

#### sourceURL

URL pointing to the source of a font project, such as a GitHub repository

Type: Unicode<br />
Required: False<br />
<div id="class_Family_attribute_versions"></div>

#### versions

List of [Version](#class_Version) objects. Versions specified here are expected to be available for all fonts in the family, which is probably most common and efficient. You may define additional font-specific versions at the [Font](#class_Font) object. You may also rely entirely on font-specific versions and leave this field here empty. However, either the fonts or the font family *must* carry version information and the validator will complain when they don’t.

Please also read the section on [versioning](#versioning) above.

Type: List of [Version](#class_Version) objects<br />
Required: False<br />


## Methods

<div id="class_Family_method_getAllDesigners"></div>

#### getAllDesigners()

Returns a list of [Designer](#class_Designer) objects that represent all of the designers referenced both at the family level as well as with all the family’s fonts, in case the fonts carry specific designers. This could be used to give a one-glance overview of all designers involved.
                





<div id="class_Version"></div>

# _class_ Version()



### Attributes

[description](#class_Version_attribute_description)<br />[number](#class_Version_attribute_number)<br />

### Methods

[isFontSpecific()](#class_Version_method_isFontSpecific)<br />

## Attributes

<div id="class_Version_attribute_description"></div>

#### description

Description of font version

Type: [MultiLanguageText](#class_MultiLanguageText)<br />
Required: False<br />
<div id="class_Version_attribute_number"></div>

#### number

Font version number

Type: Float<br />
Required: True<br />


## Methods

<div id="class_Version_method_isFontSpecific"></div>

#### isFontSpecific()

Returns True if this version is defined at the font level. Returns False if this version is defined at the family level.
                





<div id="class_Font"></div>

# _class_ Font()



### Attributes

[beta](#class_Font_attribute_beta)<br />[designers](#class_Font_attribute_designers)<br />[free](#class_Font_attribute_free)<br />[licenseAllowanceDescription](#class_Font_attribute_licenseAllowanceDescription)<br />[licenseKeyword](#class_Font_attribute_licenseKeyword)<br />[name](#class_Font_attribute_name)<br />[postScriptName](#class_Font_attribute_postScriptName)<br />[previewImage](#class_Font_attribute_previewImage)<br />[seatsAllowed](#class_Font_attribute_seatsAllowed)<br />[seatsInstalled](#class_Font_attribute_seatsInstalled)<br />[timeAdded](#class_Font_attribute_timeAdded)<br />[type](#class_Font_attribute_type)<br />[upgradeLicenseURL](#class_Font_attribute_upgradeLicenseURL)<br />[variableFont](#class_Font_attribute_variableFont)<br />[variantName](#class_Font_attribute_variantName)<br />[versions](#class_Font_attribute_versions)<br />

### Methods

[getDesigners()](#class_Font_method_getDesigners)<br />[getLicense()](#class_Font_method_getLicense)<br />[getSortedVersions()](#class_Font_method_getSortedVersions)<br />

## Attributes

<div id="class_Font_attribute_beta"></div>

#### beta

Font is in beta stage. For UI signaling

Type: Bool<br />
Required: False<br />
<div id="class_Font_attribute_designers"></div>

#### designers

List of keywords referencing designers. These are defined at [InstallableFontsResponse.designers](#class_InstallableFontsResponse_attribute_designers). This attribute overrides the designer definitions at the family level at [Family.designers](#class_Family_attribute_designers).

Type: List of Unicode objects<br />
Required: False<br />
<div id="class_Font_attribute_free"></div>

#### free

Font is freeware. For UI signaling

Type: Bool<br />
Required: False<br />
<div id="class_Font_attribute_licenseAllowanceDescription"></div>

#### licenseAllowanceDescription

In case of non-desktop font (see [Font.type](#class_Font_attribute_type)), custom string for web fonts or app fonts reminding the user of the license’s limits, e.g. "100.000 page views/month"

Type: [MultiLanguageText](#class_MultiLanguageText)<br />
Required: False<br />
<div id="class_Font_attribute_licenseKeyword"></div>

#### licenseKeyword

Keyword reference of font’s license. This license must be specified in the Foundry.Licenses

Type: Unicode<br />
Required: True<br />
<div id="class_Font_attribute_name"></div>

#### name

Human-readable name of font. This may include any additions that you find useful to communicate to your users.

Type: [MultiLanguageText](#class_MultiLanguageText)<br />
Required: True<br />
<div id="class_Font_attribute_postScriptName"></div>

#### postScriptName

Complete PostScript name of font

Type: Unicode<br />
Required: True<br />
<div id="class_Font_attribute_previewImage"></div>

#### previewImage

URL of preview image of font, specifications to follow

Type: Unicode<br />
Required: False<br />
<div id="class_Font_attribute_seatsAllowed"></div>

#### seatsAllowed

In case of desktop font (see [Font.type](#class_Font_attribute_type)), number of installations permitted by the user’s license.

Type: Int<br />
Required: False<br />
<div id="class_Font_attribute_seatsInstalled"></div>

#### seatsInstalled

In case of desktop font (see [Font.type](#class_Font_attribute_type)), number of installations recorded by the API endpoint. This value will need to be supplied by the API endpoint through tracking all font installations through the "anonymousAppID" parameter of the "installFonts" and "uninstallFonts" command. Please note that the app is currently not designed to reject installations of the fonts when the limits are exceeded. Instead it is in the responsibility of the API endpoint to reject font installations though the "installFonts" command when the limits are exceeded.

Type: Int<br />
Required: False<br />
<div id="class_Font_attribute_timeAdded"></div>

#### timeAdded

Timestamp of the time the user has purchased this font or the font has become available to the user otherwise, like a new font within a foundry’s beta font repository. Will be used in the UI to signal which fonts have become newly available in addition to previously available fonts.

Type: Int<br />
Required: False<br />
<div id="class_Font_attribute_type"></div>

#### type

Technical type of font. This influences how the app handles the font. For instance, it will only install desktop fonts on the system, and make other font types available though folders. Possible: ['desktop', 'web', 'app']

Type: Unicode<br />
Required: True<br />
<div id="class_Font_attribute_upgradeLicenseURL"></div>

#### upgradeLicenseURL

URL the user can be sent to to upgrade the license of the font, for instance at the foundry’s online shop

Type: Unicode<br />
Required: False<br />
<div id="class_Font_attribute_variableFont"></div>

#### variableFont

Font is an OpenType Variable Font. For UI signaling

Type: Bool<br />
Required: False<br />
<div id="class_Font_attribute_variantName"></div>

#### variantName

Optional variant name of font. This is used to visually group fonts in the UI. Thinking "Office Fonts" and such.

Type: [MultiLanguageText](#class_MultiLanguageText)<br />
Required: False<br />
<div id="class_Font_attribute_versions"></div>

#### versions

List of [Version](#class_Version) objects. These are font-specific versions; they may exist only for this font. You may define additional versions at the family object under [Family.versions](#class_Family_attribute_versions), which are then expected to be available for the entire family. However, either the fonts or the font family *must* carry version information and the validator will complain when they don’t.

Please also read the section on [versioning](#versioning) above.

Type: List of [Version](#class_Version) objects<br />
Required: False<br />


## Methods

<div id="class_Font_method_getDesigners"></div>

#### getDesigners()

Returns a list of [Designer](#class_Designer) objects that this font references. These are the combination of family-level designers and font-level designers. The same logic as for versioning applies. Please read the section about [versioning](#versioning) above.
                

<div id="class_Font_method_getLicense"></div>

#### getLicense()

Returns the [License](#class_License) object that this font references.
                

<div id="class_Font_method_getSortedVersions"></div>

#### getSortedVersions()

Returns list of [Version](#class_Version) objects.

This is the final list based on the version information in this font object as well as in its parent [Family](#class_Family) object. Please read the section about [versioning](#versioning) above.





<div id="class_License"></div>

# _class_ License()



### Attributes

[URL](#class_License_attribute_URL)<br />[keyword](#class_License_attribute_keyword)<br />[name](#class_License_attribute_name)<br />

## Attributes

<div id="class_License_attribute_URL"></div>

#### URL

URL where the font license can be viewed online

Type: Unicode<br />
Required: True<br />
<div id="class_License_attribute_keyword"></div>

#### keyword

Keyword under which the license will be referenced from the individual fonts.

Type: Unicode<br />
Required: True<br />
<div id="class_License_attribute_name"></div>

#### name

Human-readable name of font license

Type: [MultiLanguageText](#class_MultiLanguageText)<br />
Required: True<br />




<div id="class_Designer"></div>

# _class_ Designer()



### Attributes

[description](#class_Designer_attribute_description)<br />[keyword](#class_Designer_attribute_keyword)<br />[name](#class_Designer_attribute_name)<br />[website](#class_Designer_attribute_website)<br />

## Attributes

<div id="class_Designer_attribute_description"></div>

#### description

Description of designer

Type: [MultiLanguageText](#class_MultiLanguageText)<br />
Required: False<br />
<div id="class_Designer_attribute_keyword"></div>

#### keyword

Keyword under which the designer will be referenced from the individual fonts or font families

Type: Unicode<br />
Required: True<br />
<div id="class_Designer_attribute_name"></div>

#### name

Human-readable name of designer

Type: [MultiLanguageText](#class_MultiLanguageText)<br />
Required: True<br />
<div id="class_Designer_attribute_website"></div>

#### website

Designer’s web site

Type: Unicode<br />
Required: False<br />




<div id="class_UninstallFontsResponse"></div>

# _class_ UninstallFontsResponse()



### Attributes

[customMessage](#class_UninstallFontsResponse_attribute_customMessage)<br />[licenseIdentifier](#class_UninstallFontsResponse_attribute_licenseIdentifier)<br />[type](#class_UninstallFontsResponse_attribute_type)<br />[version](#class_UninstallFontsResponse_attribute_version)<br />

## Attributes

<div id="class_UninstallFontsResponse_attribute_customMessage"></div>

#### customMessage

Description of error in case of custom response type

Type: Unicode<br />
Required: False<br />
<div id="class_UninstallFontsResponse_attribute_licenseIdentifier"></div>

#### licenseIdentifier

Identifier of license under which the API endpoint publishes this particular response, as per https://spdx.org/licenses/. This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. This license can be different from the license at the root of the response. The idea is that different responses can be issued under different licenses, depending on their use scenario. If not specified, the root license is assumed.

Type: Unicode<br />
Required: False<br />
Default value: CC-BY-NC-ND-4.0

<div id="class_UninstallFontsResponse_attribute_type"></div>

#### type

Success or error or else.

Type: Unicode<br />
Required: True<br />
<div id="class_UninstallFontsResponse_attribute_version"></div>

#### version

Version of "uninstallFonts" response

Type: Float<br />
Required: True<br />
Default value: 0.1





<div id="class_InstallFontsResponse"></div>

# _class_ InstallFontsResponse()



### Attributes

[customMessage](#class_InstallFontsResponse_attribute_customMessage)<br />[licenseIdentifier](#class_InstallFontsResponse_attribute_licenseIdentifier)<br />[type](#class_InstallFontsResponse_attribute_type)<br />[version](#class_InstallFontsResponse_attribute_version)<br />

## Attributes

<div id="class_InstallFontsResponse_attribute_customMessage"></div>

#### customMessage

Description of error in case of custom response type

Type: Unicode<br />
Required: False<br />
<div id="class_InstallFontsResponse_attribute_licenseIdentifier"></div>

#### licenseIdentifier

Identifier of license under which the API endpoint publishes this particular response, as per https://spdx.org/licenses/. This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. This license can be different from the license at the root of the response. The idea is that different responses can be issued under different licenses, depending on their use scenario. If not specified, the root license is assumed.

Type: Unicode<br />
Required: False<br />
Default value: CC-BY-NC-ND-4.0

<div id="class_InstallFontsResponse_attribute_type"></div>

#### type

Success or error or else.

Type: Unicode<br />
Required: True<br />
<div id="class_InstallFontsResponse_attribute_version"></div>

#### version

Version of "installFonts" response

Type: Float<br />
Required: True<br />
Default value: 0.1





