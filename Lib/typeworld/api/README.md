# Type.World JSON Protocol (Version 0.2.9-beta)

## Preamble

This document covers the syntax of the JSON Protocol only. The general Type.World developer documentation is located at [type.world/developer](https://type.world/developer).

## The typeworld.client Python module

This page is simultaneously the documentation of the `typeworld.api` Python module that the Type.World App uses to read and validate the incoming data, as well as the definition of the Type.World JSON Protocol. In fact, this documentation is generated directly from the module code.

While you can assemble your JSON responses in the server side programming language of your choice, the `typeworld.api` Python module documented here will read your data and validate it and therefore acts as the official API documentation.

This module is very strict about the format of the data you put in. If it detects a wrong data type (like an float number you are putting into a field that is supposed to hold integers), it will immediately throw a tantrum. Later, when you want to generate the JSON code for your response, it will perform additional logic checks, like checking if the designers are actually defined that you are referencing in the fonts. 

Any such mistakes will not pass. If you use your own routines to assemble your JSON reponses, please make sure to check your web facing API endpoint using the online validator at [type.world/developer/validate](https://type.world/developer/validate).

## Contents

1. [Protocol Changes](#user-content-protocolchanges)
1. [List of Classes](#user-content-classtoc)
1. [Object model](#user-content-objectmodel)
1. [Versioning](#user-content-versioning)
1. [Use of Languages/Scripts](#user-content-languages)
1. [Example Code](#user-content-example)
1. [Class Reference](#user-content-classreference)


<div id="protocolchanges"></div>

## Protocol Changes

This section lists changes to the protocol since it reached Beta status with version `0.2.2-beta`.



### Changes in `0.2.9-beta`

* Introduced [EndpointResponse.sendsLiveNotifications](#user-content-class-endpointresponse-attribute-sendslivenotifications).
  The app won’t start listening to live notifications unless a subscription holds this setting.
* Introduced [EndpointResponse.allowedCommercialApps](#user-content-class-endpointresponse-attribute-allowedcommercialapps).
  In case a non-commercial copyright license is given in [EndpointResponse.licenseIdentifier](#user-content-class-endpointresponse-attribute-licenseIdentifier)
  (which defaults to `CC-BY-NC-ND-4.0`, a non-commercial license indeed), this list specifies which commercial apps are allowed to access an API Endpoint.

### Changes in `0.2.6-beta`

* Introduced font-level [Font.billboardURLs](#user-content-class-font-attribute-billboardurls) similar to family-level URLs.
  The method [Font.getBillboardURLs()](#user-content-class-font-method-getbillboardurls) will compile them, 
  currently simply choosing one or the other, font-level over family-level.

### Changes in `0.2.4-beta`

* After a rewrite to use Python’s `requests` library for calls to the internet, the method 
  `type.client.performRequest()` has been renamed to `type.client.request()` and is also
  missing the `sslContext` parameter. This interface is now `type.client.performRequest(url, parameters={})` and
  the return values are `success, response.content, response`
* Added mandatory [InstallFontAsset.version](#user-content-class-installfontasset-attribute-version) attribute.
  Dynamically created responses to the `installFonts` command didn’t need it as its content was expected
  to match the requested font IDs and versions, but static subscription need it as all available fonts need to be defined
  in all available versions here.


<div id="classtoc"></div>

## List of Classes

- [RootResponse](#user-content-class-rootresponse)<br />
- [EndpointResponse](#user-content-class-endpointresponse)<br />
- [MultiLanguageText](#user-content-class-multilanguagetext)<br />
- [InstallableFontsResponse](#user-content-class-installablefontsresponse)<br />
- [Designer](#user-content-class-designer)<br />
- [MultiLanguageLongText](#user-content-class-multilanguagelongtext)<br />
- [Foundry](#user-content-class-foundry)<br />
- [LicenseDefinition](#user-content-class-licensedefinition)<br />
- [Family](#user-content-class-family)<br />
- [FontPackage](#user-content-class-fontpackage)<br />
- [Version](#user-content-class-version)<br />
- [Font](#user-content-class-font)<br />
- [LicenseUsage](#user-content-class-licenseusage)<br />
- [InstallFontsResponse](#user-content-class-installfontsresponse)<br />
- [InstallFontAsset](#user-content-class-installfontasset)<br />
- [UninstallFontsResponse](#user-content-class-uninstallfontsresponse)<br />
- [UninstallFontAsset](#user-content-class-uninstallfontasset)<br />





<div id="objectmodel"></div>

## Object model

![](../../../images/object-model.png)



<div id="versioning"></div>

## Versioning

Every type producer has different habits when it comes to versioning of fonts. Most people would update all fonts of the family to the new version, others would only tweak a few fonts.

To accommodate all of these habits, the Type.World API supports version information in two places. However, the entire system relies on version numbers being specified as float numbers, making them mathematically comparable for sorting. Higher numbers mean newer versions.

#### Versions at the [Family](#user-content-class-family) level

The [Family.versions](#user-content-class-family-attribute-versions) attribute can carry a list of [Version](#user-content-class-version) objects. Versions that you specify here are expected to be present throughout the entire family; meaning that the complete amount of all fonts in all versions is the result of a multiplication of the number of fonts with the number of versions.

#### Versions at the [Font](#user-content-class-font) level

In addition to that, you may also specify a list of [Version](#user-content-class-version) objects at the [Font.versions](#user-content-class-font-attribute-versions) attribute. Versions that you specify here are expected to be available only for this font. 

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

#### Use [Font.getSortedVersions()](#user-content-class-font-method-getsortedversions)

Because in the end the versions matter only at the font level, the [Font.getSortedVersions()](#user-content-class-font-method-getsortedversions) method will output the final list of versions in the above combinations, with font-level definitions taking precedence over family-level definitions.




<div id="languages"></div>

## Use of Languages/Scripts

All text definitions in the Type.World JSON Protocol are multi-lingual by default using the [MultiLanguageText](#user-content-class-multilanguagetext) class. The application will then decide which language to pick to display to the user in case several languages are defined for one attribute, based on the user’s OS language and app preferences.

It is important to note that the languages used here are bound to their commonly used *scripts*. German and English are expected to be written in the Latin script, while Arabic and Hebrew, for instance, are expected to be written in the Arabic and Hebrew script, respectively. 

Therefore, the user interface will make styling decisions based on the used language. Most prominently, Arabic and Hebrew content (where useful) will be rendered right-to-left (being right-justified), while most other scripts will be rendered left-to-right.
The text rendering choice is *implicit* in the language choice. 

Other than in HTML, where one normally defines the language and the writing direction separately and explicitly, the Type.World App inferres the writing direction from the displayed language. The common and most widely read script should be used for each language.

Therefore, if a publisher wants their Arabic name to be displayed in the Latin script, the language *English* (or any other Latin-based language) should be used in the data.

In the following example, the Arabic string written in the Arabic script will be displayed to Arabic users:

```python
api.name.en = 'Levantine Fonts'
api.name.ar = 'خط الشامي'
```

Here, the publisher decides to display a Latin name only, and therefore needs to use a Latin-based language definition:

```python
api.name.en = 'Khatt Al-Shami'
```

This is wrong and will lead to improper text rendering, even though the text is actually showing the Arabic *language*, but not the Arabic *script*:

```python
api.name.ar = 'Khatt Al-Shami'
```







<div id="example"></div>

## Example Code


### Example 1: Root Response

Below you see the minimum possible object tree for a request for the `endpoint` command.

```python
# Import module
import typeworld.api

# Root of Response
root = typeworld.api.RootResponse()

# EndpointResponse
endpoint = typeworld.api.EndpointResponse()
endpoint.name.en = "Font Publisher"
endpoint.canonicalURL = "http://fontpublisher.com/api/"
endpoint.adminEmail = "admin@fontpublisher.com"
endpoint.supportedCommands = [
    x["keyword"] for x in typeworld.api.COMMANDS
]  # this API supports all commands

# Attach EndpointResponse to RootResponse
root.endpoint = endpoint

# Print API response as JSON
print(root.dumpJSON())

```

Will output the following JSON code:

```json
{
    "endpoint": {
        "adminEmail": "admin@fontpublisher.com",
        "allowedCommercialApps": [
            "world.type.app"
        ],
        "canonicalURL": "http://fontpublisher.com/api/",
        "licenseIdentifier": "CC-BY-NC-ND-4.0",
        "name": {
            "en": "Font Publisher"
        },
        "privacyPolicyURL": "https://type.world/legal/default/PrivacyPolicy.html",
        "public": false,
        "sendsLiveNotifications": false,
        "supportedCommands": [
            "endpoint",
            "installableFonts",
            "installFonts",
            "uninstallFonts"
        ],
        "termsOfServiceURL": "https://type.world/legal/default/TermsOfService.html"
    },
    "version": "0.2.9-beta"
}
```

### Example 2: InstallableFonts Response

Below you see the minimum possible object tree for a sucessful `installabefonts` response.

```python
# Import module
import typeworld.api

# Root of Response
root = typeworld.api.RootResponse()

# Response for 'availableFonts' command
installableFonts = typeworld.api.InstallableFontsResponse()
installableFonts.response = "success"

###

# Add designer to root of response
designer = typeworld.api.Designer()
designer.keyword = "max"
designer.name.en = "Max Mustermann"
installableFonts.designers.append(designer)

# Add foundry to root of response
foundry = typeworld.api.Foundry()
foundry.name.en = "Awesome Fonts"
foundry.website = "https://awesomefonts.com"
foundry.uniqueID = "awesomefontsfoundry"
installableFonts.foundries.append(foundry)

# Add license to foundry
license = typeworld.api.LicenseDefinition()
license.keyword = "awesomeFontsEULA"
license.name.en = "Awesome Fonts Desktop EULA"
license.URL = "https://awesomefonts.com/EULA/"
foundry.licenses.append(license)

# Add font family to foundry
family = typeworld.api.Family()
family.name.en = "Awesome Sans"
family.designerKeywords.append("max")
family.uniqueID = "awesomefontsfoundry-awesomesans"
foundry.families.append(family)

# Add version to font family
version = typeworld.api.Version()
version.number = 0.1
family.versions.append(version)

# Add font to family
font = typeworld.api.Font()
font.name.en = "Regular"
font.postScriptName = "AwesomeSans-Regular"
font.licenseKeyword = "awesomeFontsEULA"
font.purpose = "desktop"
font.format = "otf"
font.uniqueID = "awesomefontsfoundry-awesomesans-regular"
family.fonts.append(font)

# Font's license usage
licenseUsage = typeworld.api.LicenseUsage()
licenseUsage.keyword = "awesomeFontsEULA"
font.usedLicenses.append(licenseUsage)

###

# Attach EndpointResponse to RootResponse
root.installableFonts = installableFonts

# Print API response as JSON
print(root.dumpJSON())

```

Will output the following JSON code:

```json
{
    "installableFonts": {
        "designers": [
            {
                "keyword": "max",
                "name": {
                    "en": "Max Mustermann"
                }
            }
        ],
        "foundries": [
            {
                "families": [
                    {
                        "designerKeywords": [
                            "max"
                        ],
                        "fonts": [
                            {
                                "format": "otf",
                                "name": {
                                    "en": "Regular"
                                },
                                "postScriptName": "AwesomeSans-Regular",
                                "purpose": "desktop",
                                "status": "stable",
                                "uniqueID": "awesomefontsfoundry-awesomesans-regular",
                                "usedLicenses": [
                                    {
                                        "keyword": "awesomeFontsEULA"
                                    }
                                ]
                            }
                        ],
                        "name": {
                            "en": "Awesome Sans"
                        },
                        "uniqueID": "awesomefontsfoundry-awesomesans",
                        "versions": [
                            {
                                "number": "0.1"
                            }
                        ]
                    }
                ],
                "licenses": [
                    {
                        "URL": "https://awesomefonts.com/EULA/",
                        "keyword": "awesomeFontsEULA",
                        "name": {
                            "en": "Awesome Fonts Desktop EULA"
                        }
                    }
                ],
                "name": {
                    "en": "Awesome Fonts"
                },
                "styling": {
                    "dark": {},
                    "light": {}
                },
                "uniqueID": "awesomefontsfoundry"
            }
        ],
        "prefersRevealedUserIdentity": false,
        "response": "success"
    },
    "version": "0.2.9-beta"
}
```

Next we load that same JSON code back into an object tree, such as the GUI app would do when it loads the JSON from font publisher’s API endpoints.

```python
# Load a second API instance from that JSON
root2 = RootResponse()
root2.loadJSON(jsonResponse)

# Let’s see if they are identical (requires deepdiff)
print(root.sameContent(root2))
```


Will, or should print:

```python
True
```



<div id="classreference"></div>

## Class Reference
<div id="class-rootresponse"></div>

# _class_ RootResponse()

This is the root object for each response, and contains one or more individual
response objects as requested in the `commands` parameter of API endpoint calls.

This exists to speed up processes by reducing server calls. For instance,
installing a protected fonts and afterwards asking for a refreshed
`installableFonts` command requires two separate calls to the publisher’s API
endpoint, which in turns needs to verify the requester’s identy with the central
type.world server. By requesting `installFonts,installableFonts` commands in one go,
a lot of time is saved.

*Example JSON data:*
```json
{
    "endpoint": {
        "adminEmail": "admin@awesomefonts.com",
        "allowedCommercialApps": [
            "world.type.app"
        ],
        "canonicalURL": "https://awesomefonts.com/api/",
        "licenseIdentifier": "CC-BY-NC-ND-4.0",
        "name": {
            "de": "Geile Schriften",
            "en": "Awesome Fonts"
        },
        "privacyPolicyURL": "https://awesomefonts.com/privacypolicy.html",
        "public": true,
        "sendsLiveNotifications": false,
        "supportedCommands": [
            "endpoint",
            "installableFonts",
            "installFonts",
            "uninstallFonts"
        ],
        "termsOfServiceURL": "https://awesomefonts.com/termsofservice.html"
    },
    "installableFonts": {
        "foundries": [],
        "prefersRevealedUserIdentity": false,
        "response": "success"
    },
    "version": "0.2.9-beta"
}
```



### Attributes

[endpoint](#class-rootresponse-attribute-endpoint)<br />[installFonts](#class-rootresponse-attribute-installfonts)<br />[installableFonts](#class-rootresponse-attribute-installablefonts)<br />[uninstallFonts](#class-rootresponse-attribute-uninstallfonts)<br />[version](#class-rootresponse-attribute-version)<br />

## Attributes

<div id="class-rootresponse-attribute-endpoint"></div>

### endpoint

[EndpointResponse](#user-content-class-endpointresponse) object.

__Required:__ False<br />
__Type:__ [EndpointResponse](#user-content-class-endpointresponse)<br />
<div id="class-rootresponse-attribute-installFonts"></div>

### installFonts

[InstallFontsResponse](#user-content-class-installfontsresponse) object.

__Required:__ False<br />
__Type:__ [InstallFontsResponse](#user-content-class-installfontsresponse)<br />
<div id="class-rootresponse-attribute-installableFonts"></div>

### installableFonts

[InstallableFontsResponse](#user-content-class-installablefontsresponse) object.

__Required:__ False<br />
__Type:__ [InstallableFontsResponse](#user-content-class-installablefontsresponse)<br />
<div id="class-rootresponse-attribute-uninstallFonts"></div>

### uninstallFonts

[UninstallFontsResponse](#user-content-class-uninstallfontsresponse) object.

__Required:__ False<br />
__Type:__ [UninstallFontsResponse](#user-content-class-uninstallfontsresponse)<br />
<div id="class-rootresponse-attribute-version"></div>

### version

Version of 'installFonts' response

__Required:__ True<br />
__Type:__ Str<br />
__Format:__ Simple float number (1 or 1.01) or semantic versioning (2.0.0-rc.1) as per [semver.org](https://semver.org)<br />
__Default value:__ 0.2.9-beta





<div id="class-endpointresponse"></div>

# _class_ EndpointResponse()

This is the response expected to be returned when the API is invoked using the
`?commands=endpoint` parameter.

This response contains some mandatory information about the API endpoint such as its
name and admin email, the copyright license under which the API endpoint issues its
data, and whether or not this endpoint can be publicized about.
    

*Example JSON data:*
```json
{
    "adminEmail": "admin@awesomefonts.com",
    "allowedCommercialApps": [
        "world.type.app"
    ],
    "canonicalURL": "https://awesomefonts.com/api/",
    "licenseIdentifier": "CC-BY-NC-ND-4.0",
    "name": {
        "de": "Geile Schriften",
        "en": "Awesome Fonts"
    },
    "privacyPolicyURL": "https://awesomefonts.com/privacypolicy.html",
    "public": true,
    "sendsLiveNotifications": false,
    "supportedCommands": [
        "endpoint",
        "installableFonts",
        "installFonts",
        "uninstallFonts"
    ],
    "termsOfServiceURL": "https://awesomefonts.com/termsofservice.html"
}
```



### Attributes

[adminEmail](#class-endpointresponse-attribute-adminemail)<br />[allowedCommercialApps](#class-endpointresponse-attribute-allowedcommercialapps)<br />[backgroundColor](#class-endpointresponse-attribute-backgroundcolor)<br />[canonicalURL](#class-endpointresponse-attribute-canonicalurl)<br />[licenseIdentifier](#class-endpointresponse-attribute-licenseidentifier)<br />[loginURL](#class-endpointresponse-attribute-loginurl)<br />[logoURL](#class-endpointresponse-attribute-logourl)<br />[name](#class-endpointresponse-attribute-name)<br />[privacyPolicyURL](#class-endpointresponse-attribute-privacypolicyurl)<br />[public](#class-endpointresponse-attribute-public)<br />[sendsLiveNotifications](#class-endpointresponse-attribute-sendslivenotifications)<br />[supportedCommands](#class-endpointresponse-attribute-supportedcommands)<br />[termsOfServiceURL](#class-endpointresponse-attribute-termsofserviceurl)<br />[websiteURL](#class-endpointresponse-attribute-websiteurl)<br />

## Attributes

<div id="class-endpointresponse-attribute-adminEmail"></div>

### adminEmail

API endpoint Administrator. This email needs to be reachable for various information around the Type.World protocol as well as technical problems.

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-endpointresponse-attribute-allowedCommercialApps"></div>

### allowedCommercialApps

Machine-readable list of commercial apps that are allowed to access this API Endpoint in case [EndpointResponse.licenseIdentifier](#user-content-class-endpointresponse-attribute-licenseidentifier) carries a non-commercial copyright license such as the default `CC-BY-NC-ND-4.0`. A reverse-domain notation for the app ID is recommended but not required. Note: As the originator of the entire technology, the Type.World App is on this list by default, even though it is a commercial app. This is for backwards-compatibility for endpoints that don’t carry this attribute yet but are expected to allow access by Type.World. If you don’t want the Type.World to access your API Endpoint, you may explicitly unset this attribute to an empty list: `endpoint.allowedCommercialApps = []`

__Required:__ True<br />
__Type:__ List of Str objects<br />
__Default value:__ ['world.type.app']

<div id="class-endpointresponse-attribute-backgroundColor"></div>

### backgroundColor

Publisher’s preferred background color. This is meant to go as a background color to the logo at [APIRoot.logoURL](#user-content-class-apiroot-attribute-logourl)

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ Hex RRGGBB (without leading #)<br />
<div id="class-endpointresponse-attribute-canonicalURL"></div>

### canonicalURL

Same as the API Endpoint URL, bare of IDs and other parameters. Used for grouping of subscriptions. It is expected that this URL will not change. When it does, it will be treated as a different publisher.<br />The *API Endpoint URL* must begin with the *Canonical URL* (if you indeed choose the two to be different) or otherwise subscriptions could impersonate another publisher by displaying their name and using their Canonical URL. In other words, both must be located on the same server.

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-endpointresponse-attribute-licenseIdentifier"></div>

### licenseIdentifier

Machine-readable identifier of license under which the API Endpoint publishes its (metda)data, as per [https://spdx.org/licenses/](). This license will not be presented to the user. Instead, the software client that accesses your API Endpoint needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. In other words, the non-commercial `CC-BY-NC-ND-4.0` license that is the default here forbids commercial software from accessing your API Endpoint unless they have a separate legal agreememt with you.

__Required:__ True<br />
__Type:__ Str<br />
__Default value:__ CC-BY-NC-ND-4.0

<div id="class-endpointresponse-attribute-loginURL"></div>

### loginURL

URL for user to log in to publisher’s account in case a validation is required. This normally work in combination with the `loginRequired` response.

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-endpointresponse-attribute-logoURL"></div>

### logoURL

URL of logo of API endpoint, for publication. Specifications to follow.

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ This resource may get downloaded and cached on the client computer. To ensure up-to-date resources, append a unique ID to the URL such as a timestamp of when the resources changed on your server, e.g. https://awesomefonts.com/xyz/regular/specimen.pdf?t=1548239062. Don’t use the current time for a timestamp, as this will mean constant reloading the resource when it actually hasn’t changed. Instead use the resource’s server-side change timestamp.<br />
<div id="class-endpointresponse-attribute-name"></div>

### name

Human-readable name of API endpoint

__Required:__ True<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-endpointresponse-attribute-privacyPolicyURL"></div>

### privacyPolicyURL

URL of human-readable Privacy Policy of API endpoint. This will be displayed to the user for consent when adding a subscription. The default URL points to a document edited by Type.World that you can use (at your own risk) instead of having to write your own.

The link will open with a `locales` parameter containing a comma-separated list of the user’s preferred UI languages and a `canonicalURL` parameter containing the subscription’s canonical URL and a `subscriptionID` parameter containing the anonymous subscription ID.

__Required:__ True<br />
__Type:__ Str<br />
__Default value:__ https://type.world/legal/default/PrivacyPolicy.html

<div id="class-endpointresponse-attribute-public"></div>

### public

API endpoint is meant to be publicly visible and its existence may be publicized within the project

__Required:__ True<br />
__Type:__ Bool<br />
__Default value:__ False

<div id="class-endpointresponse-attribute-sendsLiveNotifications"></div>

### sendsLiveNotifications

API endpoint is sending live notifications through the central server, namely through the `updateSubscription` command. The app won’t start listening to live notifications unless a subscription holds this setting. 

__Required:__ True<br />
__Type:__ Bool<br />
__Default value:__ False

<div id="class-endpointresponse-attribute-supportedCommands"></div>

### supportedCommands

List of commands this API endpoint supports: ['endpoint', 'installableFonts', 'installFonts', 'uninstallFonts']

__Required:__ True<br />
__Type:__ List of Str objects<br />
<div id="class-endpointresponse-attribute-termsOfServiceURL"></div>

### termsOfServiceURL

URL of human-readable Terms of Service Agreement of API endpoint. This will be displayed to the user for consent when adding a subscription. The default URL points to a document edited by Type.World that you can use (at your own risk) instead of having to write your own.

The link will open with a `locales` parameter containing a comma-separated list of the user’s preferred UI languages and a `canonicalURL` parameter containing the subscription’s canonical URL and a `subscriptionID` parameter containing the anonymous subscription ID.

__Required:__ True<br />
__Type:__ Str<br />
__Default value:__ https://type.world/legal/default/TermsOfService.html

<div id="class-endpointresponse-attribute-websiteURL"></div>

### websiteURL

URL of human-visitable website of API endpoint, for publication

__Required:__ False<br />
__Type:__ Str<br />




<div id="class-multilanguagetext"></div>

# _class_ MultiLanguageText()

Multi-language text. Attributes are language keys as per
[https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes]

The GUI app will then calculate the language data to be displayed using
[MultiLanguageText.getText()](#user-content-class-multilanguagetext-method-gettext) with a prioritized list of languages that
the user can understand. They may be pulled from the operating system’s
language preferences.

These classes are already initiated wherever they are used, and can be
addresses instantly with the language attributes:

```python
api.name.en = u'Font Publisher XYZ'
api.name.de = u'Schriftenhaus XYZ'
```

If you are loading language information from an external source, you may use
the `.set()` method to enter data:

```python
# Simulating external data source
for languageCode, text in (
        ('en': u'Font Publisher XYZ'),
        ('de': u'Schriftenhaus XYZ'),
    )
    api.name.set(languageCode, text)
```

Neither HTML nor Markdown code is permitted in `MultiLanguageText`.

*Example JSON data:*
```json
{
    "de": "Text auf Deutsch",
    "en": "Text in English"
}
```



### Methods

[getText()](#class-multilanguagetext-method-gettext)<br />[getTextAndLocale()](#class-multilanguagetext-method-gettextandlocale)<br />

## Methods

<div id="class-multilanguagetext-method-gettext"></div>

#### getText(locale = ['en'])

Returns the text in the first language found from the specified
list of languages. If that language can’t be found, we’ll try English
as a standard. If that can’t be found either, return the first language
you can find.

<div id="class-multilanguagetext-method-gettextandlocale"></div>

#### getTextAndLocale(locale = ['en'])

Like getText(), but additionally returns the language of whatever
text was found first.





<div id="class-installablefontsresponse"></div>

# _class_ InstallableFontsResponse()

This is the response expected to be returned when the API is invoked using the
`?commands=installableFonts` parameter, and contains metadata about which fonts
are available to install for a user.

*Example JSON data:*
```json
{
    "foundries": [],
    "prefersRevealedUserIdentity": false,
    "response": "success"
}
```



### Attributes

[designers](#class-installablefontsresponse-attribute-designers)<br />[errorMessage](#class-installablefontsresponse-attribute-errormessage)<br />[foundries](#class-installablefontsresponse-attribute-foundries)<br />[name](#class-installablefontsresponse-attribute-name)<br />[packages](#class-installablefontsresponse-attribute-packages)<br />[prefersRevealedUserIdentity](#class-installablefontsresponse-attribute-prefersrevealeduseridentity)<br />[response](#class-installablefontsresponse-attribute-response)<br />[userEmail](#class-installablefontsresponse-attribute-useremail)<br />[userName](#class-installablefontsresponse-attribute-username)<br />

## Attributes

<div id="class-installablefontsresponse-attribute-designers"></div>

### designers

List of [Designer](#user-content-class-designer) objects, referenced in the fonts or font families by the keyword. These are defined at the root of the response for space efficiency, as one designer can be involved in the design of several typefaces across several foundries.

__Required:__ False<br />
__Type:__ List of [Designer](#user-content-class-designer) objects<br />
<div id="class-installablefontsresponse-attribute-errorMessage"></div>

### errorMessage

Description of error in case of [InstallableFontsResponse.response](#user-content-class-installablefontsresponse-attribute-response) being 'custom'.

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-installablefontsresponse-attribute-foundries"></div>

### foundries

List of [Foundry](#user-content-class-foundry) objects; foundries that this distributor supports. In most cases this will be only one, as many foundries are their own distributors.

__Required:__ True<br />
__Type:__ List of [Foundry](#user-content-class-foundry) objects<br />
<div id="class-installablefontsresponse-attribute-name"></div>

### name

A name of this response and its contents. This is needed to manage subscriptions in the UI. For instance 'Free Fonts' for all free and non-restricted fonts, or 'Commercial Fonts' for all those fonts that the use has commercially licensed, so their access is restricted. In case of a free font website that offers individual subscriptions for each typeface, this decription could be the name of the typeface.

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-installablefontsresponse-attribute-packages"></div>

### packages

Publisher-wide list of [FontPackage](#user-content-class-fontpackage) objects. These will be referenced by their keyword in [Font.packageKeywords](#user-content-class-font-attribute-packagekeywords)

__Required:__ False<br />
__Type:__ List of [FontPackage](#user-content-class-fontpackage) objects<br />
<div id="class-installablefontsresponse-attribute-prefersRevealedUserIdentity"></div>

### prefersRevealedUserIdentity

Indicates that the publisher prefers to have the user reveal his/her identity to the publisher when installing fonts. In the app, the user will be asked via a dialog to turn the setting on, but is not required to do so.

__Required:__ True<br />
__Type:__ Bool<br />
__Default value:__ False

<div id="class-installablefontsresponse-attribute-response"></div>

### response

Type of response: 

`success`: The request has been processed successfully.

`error`: There request produced an error. You may add a custom error message in the `errorMessage` field.

`noFontsAvailable`: This subscription exists but carries no fonts at the moment.

`insufficientPermission`: The Type.World user account credentials couldn’t be confirmed by the publisher (which are checked with the central server) and therefore access to the subscription is denied.

`temporarilyUnavailable`: The service is temporarily unavailable but should work again later on.

`validTypeWorldUserAccountRequired`: The access to this subscription requires a valid Type.World user account connected to an app.



__Required:__ True<br />
__Type:__ Str<br />
__Format:__ To ensure the proper function of the entire Type.World protocol, your API endpoint *must* return the proper responses as per [this flow chart](https://type.world/documentation/Type.World%20Request%20Flow%20Chart.pdf). In addition to ensure functionality, this enables the response messages displayed to the user to be translated into all the possible languages on our side.<br />
<div id="class-installablefontsresponse-attribute-userEmail"></div>

### userEmail

The email address of the user who these fonts are licensed to.

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-installablefontsresponse-attribute-userName"></div>

### userName

The name of the user who these fonts are licensed to.

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />




<div id="class-designer"></div>

# _class_ Designer()



*Example JSON data:*
```json
{
    "keyword": "johndoe",
    "name": {
        "en": "John Doe"
    },
    "websiteURL": "https://johndoe.com"
}
```



### Attributes

[description](#class-designer-attribute-description)<br />[keyword](#class-designer-attribute-keyword)<br />[name](#class-designer-attribute-name)<br />[websiteURL](#class-designer-attribute-websiteurl)<br />

## Attributes

<div id="class-designer-attribute-description"></div>

### description

Description of designer

__Required:__ False<br />
__Type:__ [MultiLanguageLongText](#user-content-class-multilanguagelongtext)<br />
__Format:__ Maximum allowed characters: 3000. Mardown code is permitted for text formatting.<br />
<div id="class-designer-attribute-keyword"></div>

### keyword

Machine-readable keyword under which the designer will be referenced from the individual fonts or font families

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-designer-attribute-name"></div>

### name

Human-readable name of designer

__Required:__ True<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-designer-attribute-websiteURL"></div>

### websiteURL

Designer’s web site

__Required:__ False<br />
__Type:__ Str<br />




<div id="class-multilanguagelongtext"></div>

# _class_ MultiLanguageLongText()

Multi-language text. Attributes are language keys as per
[https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes]

The GUI app will then calculate the language data to be displayed using
[MultiLanguageText.getText()](#user-content-class-multilanguagetext-method-gettext) with a prioritized list of languages that
the user can understand. They may be pulled from the operating system’s
language preferences.

These classes are already initiated wherever they are used, and can be
addresses instantly with the language attributes:

```python
api.name.en = u'Font Publisher XYZ'
api.name.de = u'Schriftenhaus XYZ'
```

If you are loading language information from an external source, you may use
the `.set()` method to enter data:

```python
# Simulating external data source
for languageCode, text in (
        ('en': u'Font Publisher XYZ'),
        ('de': u'Schriftenhaus XYZ'),
    )
    api.name.set(languageCode, text)
```

Neither HTML nor Markdown code is permitted in `MultiLanguageText`.

*Example JSON data:*
```json
{
    "de": "Text auf Deutsch",
    "en": "Text in English"
}
```



### Methods

[getText()](#class-multilanguagelongtext-method-gettext)<br />[getTextAndLocale()](#class-multilanguagelongtext-method-gettextandlocale)<br />

## Methods

<div id="class-multilanguagelongtext-method-gettext"></div>

#### getText(locale = ['en'])

Returns the text in the first language found from the specified
list of languages. If that language can’t be found, we’ll try English
as a standard. If that can’t be found either, return the first language
you can find.

<div id="class-multilanguagelongtext-method-gettextandlocale"></div>

#### getTextAndLocale(locale = ['en'])

Like getText(), but additionally returns the language of whatever
text was found first.





<div id="class-foundry"></div>

# _class_ Foundry()



*Example JSON data:*
```json
{
    "families": [],
    "licenses": [],
    "name": {
        "de": "Geile Schriften",
        "en": "Awesome Fonts"
    },
    "styling": {
        "dark": {},
        "light": {}
    },
    "uniqueID": "AwesomeFonts",
    "websiteURL": "https://awesomefonts.com"
}
```



### Attributes

[description](#class-foundry-attribute-description)<br />[email](#class-foundry-attribute-email)<br />[families](#class-foundry-attribute-families)<br />[licenses](#class-foundry-attribute-licenses)<br />[name](#class-foundry-attribute-name)<br />[packages](#class-foundry-attribute-packages)<br />[socialURLs](#class-foundry-attribute-socialurls)<br />[styling](#class-foundry-attribute-styling)<br />[supportEmail](#class-foundry-attribute-supportemail)<br />[supportTelephone](#class-foundry-attribute-supporttelephone)<br />[supportURL](#class-foundry-attribute-supporturl)<br />[telephone](#class-foundry-attribute-telephone)<br />[uniqueID](#class-foundry-attribute-uniqueid)<br />[websiteURL](#class-foundry-attribute-websiteurl)<br />

## Attributes

<div id="class-foundry-attribute-description"></div>

### description

Description of foundry

__Required:__ False<br />
__Type:__ [MultiLanguageLongText](#user-content-class-multilanguagelongtext)<br />
__Format:__ Maximum allowed characters: 3000. Mardown code is permitted for text formatting.<br />
<div id="class-foundry-attribute-email"></div>

### email

General email address for this foundry.

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-foundry-attribute-families"></div>

### families

List of [Family](#user-content-class-family) objects.

__Required:__ True<br />
__Type:__ List of [Family](#user-content-class-family) objects<br />
<div id="class-foundry-attribute-licenses"></div>

### licenses

List of [LicenseDefinition](#user-content-class-licensedefinition) objects under which the fonts in this response are issued. For space efficiency, these licenses are defined at the foundry object and will be referenced in each font by their keyword. Keywords need to be unique for this foundry and may repeat across foundries.

__Required:__ True<br />
__Type:__ List of [LicenseDefinition](#user-content-class-licensedefinition) objects<br />
<div id="class-foundry-attribute-name"></div>

### name

Name of foundry

__Required:__ True<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-foundry-attribute-packages"></div>

### packages

Foundry-wide list of [FontPackage](#user-content-class-fontpackage) objects. These will be referenced by their keyword in [Font.packageKeywords](#user-content-class-font-attribute-packagekeywords)

__Required:__ False<br />
__Type:__ List of [FontPackage](#user-content-class-fontpackage) objects<br />
<div id="class-foundry-attribute-socialURLs"></div>

### socialURLs

List of web URLs pointing to social media channels

__Required:__ False<br />
__Type:__ List of Str objects<br />
<div id="class-foundry-attribute-styling"></div>

### styling

Dictionary of styling values, for light and dark theme. See example below. If you want to style your foundry here, please start with the light theme. You may omit the dark theme.

__Required:__ False<br />
__Type:__ Dict<br />
__Default value:__ {'light': {}, 'dark': {}}

Example:
```json
{
    "light": {
        "headerColor": "219BD3",
        "headerTextColor": "000000",
        "headerLinkColor": "145F7F",
        "backgroundColor": "FFFFFF",
        "textColor": "000000",
        "linkColor": "F7AD22",
        "selectionColor": "F7AD22",
        "selectionTextColor": "000000",
        "buttonColor": "197AA3",
        "buttonTextColor": "FFFFFF",
        "informationViewBackgroundColor": "F2F2F2",
        "informationViewTextColor": "000000",
        "informationViewLinkColor": "1D89B8",
        "informationViewButtonColor": "197AA3",
        "informationViewButtonTextColor": "FFFFFF",
        "logoURL": "https://awesomefoundry.com/logo-lighttheme.svg"
    },
    "dark": {
        "headerColor": "156486",
        "headerTextColor": "000000",
        "headerLinkColor": "53B9E4",
        "backgroundColor": "262626",
        "textColor": "999999",
        "linkColor": "C07F07",
        "selectionColor": "9A6606",
        "selectionTextColor": "000000",
        "buttonColor": "22A4DC",
        "buttonTextColor": "000000",
        "informationViewBackgroundColor": "1A1A1A",
        "informationViewTextColor": "999999",
        "informationViewLinkColor": "53B9E4",
        "informationViewButtonColor": "22A4DC",
        "informationViewButtonTextColor": "000000",
        "logoURL": "https://awesomefoundry.com/logo-darktheme.svg"
    }
}
```
<div id="class-foundry-attribute-supportEmail"></div>

### supportEmail

Support email address for this foundry.

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-foundry-attribute-supportTelephone"></div>

### supportTelephone

Support telephone number for this foundry.

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ +1234567890<br />
<div id="class-foundry-attribute-supportURL"></div>

### supportURL

Support website for this foundry, such as a chat room, forum, online service desk.

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-foundry-attribute-telephone"></div>

### telephone

Telephone number for this foundry

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ +1234567890<br />
<div id="class-foundry-attribute-uniqueID"></div>

### uniqueID

An string that uniquely identifies this foundry within the publisher.

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-foundry-attribute-websiteURL"></div>

### websiteURL

Website for this foundry

__Required:__ False<br />
__Type:__ Str<br />




<div id="class-licensedefinition"></div>

# _class_ LicenseDefinition()



*Example JSON data:*
```json
{
    "URL": "https://awesomefonts.com/eula.html",
    "keyword": "awesomefontsEULA",
    "name": {
        "de": "Awesome Fonts Endnutzerlizenzvereinbarung",
        "en": "Awesome Fonts End User License Agreement"
    }
}
```



### Attributes

[URL](#class-licensedefinition-attribute-url)<br />[keyword](#class-licensedefinition-attribute-keyword)<br />[name](#class-licensedefinition-attribute-name)<br />

## Attributes

<div id="class-licensedefinition-attribute-URL"></div>

### URL

URL where the font license text can be viewed online

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-licensedefinition-attribute-keyword"></div>

### keyword

Machine-readable keyword under which the license will be referenced from the individual fonts.

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-licensedefinition-attribute-name"></div>

### name

Human-readable name of font license

__Required:__ True<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />




<div id="class-family"></div>

# _class_ Family()



*Example JSON data:*
```json
{
    "description": {
        "de": "Fette Groteske mit runden Ecken",
        "en": "Nice big fat face with smooth corners"
    },
    "fonts": [],
    "name": {
        "en": "Awesome Family"
    },
    "uniqueID": "AwesomeFonts-AwesomeFamily"
}
```



### Attributes

[billboardURLs](#class-family-attribute-billboardurls)<br />[dateFirstPublished](#class-family-attribute-datefirstpublished)<br />[description](#class-family-attribute-description)<br />[designerKeywords](#class-family-attribute-designerkeywords)<br />[fonts](#class-family-attribute-fonts)<br />[galleryURL](#class-family-attribute-galleryurl)<br />[issueTrackerURL](#class-family-attribute-issuetrackerurl)<br />[name](#class-family-attribute-name)<br />[packages](#class-family-attribute-packages)<br />[pdfURL](#class-family-attribute-pdfurl)<br />[sourceURL](#class-family-attribute-sourceurl)<br />[uniqueID](#class-family-attribute-uniqueid)<br />[versions](#class-family-attribute-versions)<br />

### Methods

[getAllDesigners()](#class-family-method-getalldesigners)<br />

## Attributes

<div id="class-family-attribute-billboardURLs"></div>

### billboardURLs

List of URLs pointing at images to show for this typeface. We suggest to use square dimensions and uncompressed SVG images because they scale to all sizes smoothly, but ultimately any size or HTML-compatible image type is possible.

__Required:__ False<br />
__Type:__ List of Str objects<br />
<div id="class-family-attribute-dateFirstPublished"></div>

### dateFirstPublished

Human readable date of the initial release of the family. May be overriden on font level at [Font.dateFirstPublished](#user-content-class-font-attribute-datefirstpublished).

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ YYYY-MM-DD<br />
<div id="class-family-attribute-description"></div>

### description

Description of font family

__Required:__ False<br />
__Type:__ [MultiLanguageLongText](#user-content-class-multilanguagelongtext)<br />
__Format:__ Maximum allowed characters: 3000. Mardown code is permitted for text formatting.<br />
<div id="class-family-attribute-designerKeywords"></div>

### designerKeywords

List of keywords referencing designers. These are defined at [InstallableFontsResponse.designers](#user-content-class-installablefontsresponse-attribute-designers). In case designers differ between fonts within the same family, they can also be defined at the font level at [Font.designers](#user-content-class-font-attribute-designers). The font-level references take precedence over the family-level references.

__Required:__ False<br />
__Type:__ List of Str objects<br />
<div id="class-family-attribute-fonts"></div>

### fonts

List of [Font](#user-content-class-font) objects. The order will be displayed unchanged in the UI, so it’s in your responsibility to order them correctly.

__Required:__ True<br />
__Type:__ List of [Font](#user-content-class-font) objects<br />
<div id="class-family-attribute-galleryURL"></div>

### galleryURL

URL pointing to a web site that shows real world examples of the fonts in use or other types of galleries.

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-family-attribute-issueTrackerURL"></div>

### issueTrackerURL

URL pointing to an issue tracker system, where users can debate about a typeface’s design or technicalities

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-family-attribute-name"></div>

### name

Human-readable name of font family. This may include any additions that you find useful to communicate to your users.

__Required:__ True<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-family-attribute-packages"></div>

### packages

Family-wide list of [FontPackage](#user-content-class-fontpackage) objects. These will be referenced by their keyword in [Font.packageKeywords](#user-content-class-font-attribute-packagekeywords)

__Required:__ False<br />
__Type:__ List of [FontPackage](#user-content-class-fontpackage) objects<br />
<div id="class-family-attribute-pdfURL"></div>

### pdfURL

URL of PDF file with type specimen and/or instructions for entire family. May be overriden on font level at [Font.pdf](#user-content-class-font-attribute-pdf).

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ This resource may get downloaded and cached on the client computer. To ensure up-to-date resources, append a unique ID to the URL such as a timestamp of when the resources changed on your server, e.g. https://awesomefonts.com/xyz/regular/specimen.pdf?t=1548239062. Don’t use the current time for a timestamp, as this will mean constant reloading the resource when it actually hasn’t changed. Instead use the resource’s server-side change timestamp.<br />
<div id="class-family-attribute-sourceURL"></div>

### sourceURL

URL pointing to the source of a font project, such as a GitHub repository

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-family-attribute-uniqueID"></div>

### uniqueID

An string that uniquely identifies this family within the publisher.

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-family-attribute-versions"></div>

### versions

List of [Version](#user-content-class-version) objects. Versions specified here are expected to be available for all fonts in the family, which is probably most common and efficient. You may define additional font-specific versions at the [Font](#user-content-class-font) object. You may also rely entirely on font-specific versions and leave this field here empty. However, either the fonts or the font family *must* carry version information and the validator will complain when they don’t.

Please also read the section on [versioning](#versioning) above.

__Required:__ False<br />
__Type:__ List of [Version](#user-content-class-version) objects<br />


## Methods

<div id="class-family-method-getalldesigners"></div>

#### getAllDesigners()

Returns a list of [Designer](#user-content-class-designer) objects that represent all of the designers
referenced both at the family level as well as with all the family’s fonts,
in case the fonts carry specific designers. This could be used to give a
one-glance overview of all designers involved.





<div id="class-fontpackage"></div>

# _class_ FontPackage()

`FontPackages` are groups of fonts that serve a certain purpose
to the user.
They can be defined at [InstallableFontsReponse.packages](#user-content-class-installablefontsreponse-attribute-packages),
[Foundry.packages](#user-content-class-foundry-attribute-packages), [Family.packages](#user-content-class-family-attribute-packages)
and are referenced by their keywords in [Font.packageKeywords](#user-content-class-font-attribute-packagekeywords).

On a font family level, defined at [Family.packages](#user-content-class-family-attribute-packages), a typical example
for defining a `FontPackage` would be the so called **Office Fonts**.
While they are technically identical to other OpenType fonts, they normally
have a sightly different set of glyphs and OpenType features.
Linking them to a `FontPackage` allows the UI to display them clearly as a
separate set of fonts that serve a different purpuse than the
regular fonts.

On a subscription-wide level, defined at
[InstallableFontsReponse.packages](#user-content-class-installablefontsreponse-attribute-packages), a `FontPackage` could represent a
curated collection of fonts of various foundries and families, for example
**Script Fonts** or **Brush Fonts** or **Corporate Fonts**.

Each font may be part of several `FontPackages`.

For the time being, only family-level FontPackages are supported in the UI.

*Example JSON data:*
```json
{
    "description": {
        "de": "Diese Schriftdateien sind f\u00fcr die Benutzung in Office-Applikationen vorgesehen.",
        "en": "These fonts are produced specifically to be used in Office applications."
    },
    "keyword": "officefonts",
    "name": {
        "de": "Office-Schriften",
        "en": "Office Fonts"
    }
}
```



### Attributes

[description](#class-fontpackage-attribute-description)<br />[keyword](#class-fontpackage-attribute-keyword)<br />[name](#class-fontpackage-attribute-name)<br />

### Methods

[getFonts()](#class-fontpackage-method-getfonts)<br />

## Attributes

<div id="class-fontpackage-attribute-description"></div>

### description

Description

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-fontpackage-attribute-keyword"></div>

### keyword

Keyword of font packages. This keyword must be referenced in [Font.packageKeywords](#user-content-class-font-attribute-packagekeywords) and must be unique to this subscription.

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-fontpackage-attribute-name"></div>

### name

Name of package

__Required:__ True<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />


## Methods

<div id="class-fontpackage-method-getfonts"></div>

#### getFonts(filterByFontFormat = [], variableFont = None)

Calculate list of fonts of this package by applying filters for
font.format and font.variableFont (possibly more in the future)





<div id="class-version"></div>

# _class_ Version()



*Example JSON data:*
```json
{
    "description": {
        "de": "Versal-SZ und t\u00fcrkisches Lira-Zeichen hinzugef\u00fcgt",
        "en": "Added capital SZ and Turkish Lira sign"
    },
    "number": "1.2",
    "releaseDate": "2020-05-21"
}
```



### Attributes

[description](#class-version-attribute-description)<br />[number](#class-version-attribute-number)<br />[releaseDate](#class-version-attribute-releasedate)<br />

### Methods

[isFontSpecific()](#class-version-method-isfontspecific)<br />

## Attributes

<div id="class-version-attribute-description"></div>

### description

Description of font version

__Required:__ False<br />
__Type:__ [MultiLanguageLongText](#user-content-class-multilanguagelongtext)<br />
__Format:__ Maximum allowed characters: 3000. Mardown code is permitted for text formatting.<br />
<div id="class-version-attribute-number"></div>

### number

Font version number. This can be a simple float number (1.002) or a semver version string (see https://semver.org). For comparison, single-dot version numbers (or even integers) are appended with another .0 (1.0 to 1.0.0), then compared using the Python `semver` module.

__Required:__ True<br />
__Type:__ Str<br />
__Format:__ Simple float number (1 or 1.01) or semantic versioning (2.0.0-rc.1) as per [semver.org](https://semver.org)<br />
<div id="class-version-attribute-releaseDate"></div>

### releaseDate

Font version’s release date.

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ YYYY-MM-DD<br />


## Methods

<div id="class-version-method-isfontspecific"></div>

#### isFontSpecific()

Returns True if this version is defined at the font level.
Returns False if this version is defined at the family level.





<div id="class-font"></div>

# _class_ Font()



*Example JSON data:*
```json
{
    "name": {
        "de": "Fette",
        "en": "Bold"
    },
    "postScriptName": "AwesomeFamily-Bold",
    "purpose": "desktop",
    "status": "stable",
    "uniqueID": "AwesomeFonts-AwesomeFamily-Bold",
    "usedLicenses": []
}
```



### Attributes

[billboardURLs](#class-font-attribute-billboardurls)<br />[dateFirstPublished](#class-font-attribute-datefirstpublished)<br />[designerKeywords](#class-font-attribute-designerkeywords)<br />[expiry](#class-font-attribute-expiry)<br />[expiryDuration](#class-font-attribute-expiryduration)<br />[features](#class-font-attribute-features)<br />[format](#class-font-attribute-format)<br />[free](#class-font-attribute-free)<br />[languageSupport](#class-font-attribute-languagesupport)<br />[name](#class-font-attribute-name)<br />[packageKeywords](#class-font-attribute-packagekeywords)<br />[pdfURL](#class-font-attribute-pdfurl)<br />[postScriptName](#class-font-attribute-postscriptname)<br />[protected](#class-font-attribute-protected)<br />[purpose](#class-font-attribute-purpose)<br />[status](#class-font-attribute-status)<br />[uniqueID](#class-font-attribute-uniqueid)<br />[usedLicenses](#class-font-attribute-usedlicenses)<br />[variableFont](#class-font-attribute-variablefont)<br />[versions](#class-font-attribute-versions)<br />

### Methods

[filename()](#class-font-method-filename)<br />[getBillboardURLs()](#class-font-method-getbillboardurls)<br />[getDesigners()](#class-font-method-getdesigners)<br />[getVersions()](#class-font-method-getversions)<br />

## Attributes

<div id="class-font-attribute-billboardURLs"></div>

### billboardURLs

List of URLs pointing at images to show for this typeface. We suggest to use square dimensions and uncompressed SVG images because they scale to all sizes smoothly, but ultimately any size or HTML-compatible image type is possible.

__Required:__ False<br />
__Type:__ List of Str objects<br />
<div id="class-font-attribute-dateFirstPublished"></div>

### dateFirstPublished

Human readable date of the initial release of the font. May also be defined family-wide at [Family.dateFirstPublished](#user-content-class-family-attribute-datefirstpublished).

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ YYYY-MM-DD<br />
<div id="class-font-attribute-designerKeywords"></div>

### designerKeywords

List of keywords referencing designers. These are defined at [InstallableFontsResponse.designers](#user-content-class-installablefontsresponse-attribute-designers). This attribute overrides the designer definitions at the family level at [Family.designers](#user-content-class-family-attribute-designers).

__Required:__ False<br />
__Type:__ List of Str objects<br />
<div id="class-font-attribute-expiry"></div>

### expiry

Unix timestamp of font’s expiry. The font will be deleted on that moment. This could be set either upon initial installation of a trial font, or also before initial installation as a general expiry moment.

__Required:__ False<br />
__Type:__ Int<br />
<div id="class-font-attribute-expiryDuration"></div>

### expiryDuration

Minutes for which the user will be able to use the font after initial installation. This attribute is used only as a visual hint in the UI and should be set for trial fonts that expire a certain period after initial installation, such as 60 minutes. If the font is a trial font limited to a certain usage period after initial installation, it must also be marked as [Font.protected](#user-content-class-font-attribute-protected), with no [Font.expiry](#user-content-class-font-attribute-expiry) timestamp set at first (because the expiry depends on the moment of initial installation). On initial font installation by the user, the publisher’s server needs to record that moment’s time, and from there onwards serve the subscription with [Font.expiry](#user-content-class-font-attribute-expiry) attribute set in the future. Because the font is marked as [Font.protected](#user-content-class-font-attribute-protected), the app will update the subscription directly after font installation, upon when it will learn of the newly added [Font.expiry](#user-content-class-font-attribute-expiry) attribute. Please note that you *have* to set [Font.expiry](#user-content-class-font-attribute-expiry) after initial installation yourself. The Type.World app will not follow up on its own on installed fonts just with the [Font.expiryDuration](#user-content-class-font-attribute-expiryduration) attribute, which is used only for display.

__Required:__ False<br />
__Type:__ Int<br />
<div id="class-font-attribute-features"></div>

### features

List of supported OpenType features as per https://docs.microsoft.com/en-us/typography/opentype/spec/featuretags

__Required:__ False<br />
__Type:__ List of Str objects<br />
<div id="class-font-attribute-format"></div>

### format

Font file format. Required value in case of `desktop` font (see [Font.purpose](#user-content-class-font-attribute-purpose). Possible: ['otf', 'woff2', 'ttc', 'woff', 'ttf']

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-font-attribute-free"></div>

### free

Font is freeware. For UI signaling

__Required:__ False<br />
__Type:__ Bool<br />
<div id="class-font-attribute-languageSupport"></div>

### languageSupport

Dictionary of suppported languages as script/language combinations

__Required:__ False<br />
__Type:__ Dict<br />
<div id="class-font-attribute-name"></div>

### name

Human-readable name of font. This may include any additions that you find useful to communicate to your users.

__Required:__ True<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-font-attribute-packageKeywords"></div>

### packageKeywords

List of references to [FontPackage](#user-content-class-fontpackage) objects by their keyword

__Required:__ False<br />
__Type:__ List of Str objects<br />
<div id="class-font-attribute-pdfURL"></div>

### pdfURL

URL of PDF file with type specimen and/or instructions for this particular font. (See also: [Family.pdf](#user-content-class-family-attribute-pdf)

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ This resource may get downloaded and cached on the client computer. To ensure up-to-date resources, append a unique ID to the URL such as a timestamp of when the resources changed on your server, e.g. https://awesomefonts.com/xyz/regular/specimen.pdf?t=1548239062. Don’t use the current time for a timestamp, as this will mean constant reloading the resource when it actually hasn’t changed. Instead use the resource’s server-side change timestamp.<br />
<div id="class-font-attribute-postScriptName"></div>

### postScriptName

Complete PostScript name of font

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-font-attribute-protected"></div>

### protected

Indication that font is (most likely) commercial and requires a certain amount of special treatment over a free font: 1) The API Endpoint requires a valid subscriptionID to be used for authentication. 2) The API Endpoint may limit the downloads of fonts. 3) Most importantly, the `uninstallFonts` command needs to be called on the API Endpoint when the font gets uninstalled.This may also be used for fonts that are free to download, but their installations want to be monitored or limited anyway. 

__Required:__ False<br />
__Type:__ Bool<br />
__Default value:__ False

<div id="class-font-attribute-purpose"></div>

### purpose

Technical purpose of font. This influences how the app handles the font. For instance, it will only install desktop fonts on the system, and make other font types available though folders. Possible: ['desktop', 'web', 'app']

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-font-attribute-status"></div>

### status

Font status. For UI signaling. Possible values are: ['prerelease', 'trial', 'stable']

__Required:__ True<br />
__Type:__ Str<br />
__Default value:__ stable

<div id="class-font-attribute-uniqueID"></div>

### uniqueID

A machine-readable string that uniquely identifies this font within the publisher. It will be used to ask for un/installation of the font from the server in the `installFonts` and `uninstallFonts` commands. Also, it will be used for the file name of the font on disk, together with the version string and the file extension. Together, they must not be longer than 220 characters and must not contain the following characters: / ? < > \ : * | ^

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-font-attribute-usedLicenses"></div>

### usedLicenses

List of [LicenseUsage](#user-content-class-licenseusage) objects. These licenses represent the different ways in which a user has access to this font. At least one used license must be defined here, because a user needs to know under which legal circumstances he/she is using the font. Several used licenses may be defined for a single font in case a customer owns several licenses that cover the same font. For instance, a customer could have purchased a font license standalone, but also as part of the foundry’s entire catalogue. It’s important to keep these separate in order to provide the user with separate upgrade links where he/she needs to choose which of several owned licenses needs to be upgraded. Therefore, in case of a commercial retail foundry, used licenses correlate to a user’s purchase history.

__Required:__ True<br />
__Type:__ List of [LicenseUsage](#user-content-class-licenseusage) objects<br />
<div id="class-font-attribute-variableFont"></div>

### variableFont

Font is an OpenType Variable Font. For UI signaling

__Required:__ False<br />
__Type:__ Bool<br />
__Default value:__ False

<div id="class-font-attribute-versions"></div>

### versions

List of [Version](#user-content-class-version) objects. These are font-specific versions; they may exist only for this font. You may define additional versions at the family object under [Family.versions](#user-content-class-family-attribute-versions), which are then expected to be available for the entire family. However, either the fonts or the font family *must* carry version information and the validator will complain when they don’t.

Please also read the section on [versioning](#versioning) above.

__Required:__ False<br />
__Type:__ List of [Version](#user-content-class-version) objects<br />


## Methods

<div id="class-font-method-filename"></div>

#### filename()

Returns the recommended font file name to be used to store the font on disk.

It is composed of the font’s uniqueID, its version string and the file
extension. Together, they must not exceed 220 characters.

<div id="class-font-method-getbillboardurls"></div>

#### getBillboardURLs()

Returns list billboardURLs compiled from [Font.billboardURLs](#user-content-class-font-attribute-billboardurls)
and [Family.billboardURLs](#user-content-class-family-attribute-billboardurls), giving the font-level definitions priority
over family-level definitions.

<div id="class-font-method-getdesigners"></div>

#### getDesigners()

Returns a list of [Designer](#user-content-class-designer) objects that this font references.
These are the combination of family-level designers and font-level designers.
The same logic as for versioning applies.
Please read the section about [versioning](#versioning) above.

<div id="class-font-method-getversions"></div>

#### getVersions()

Returns list of [Version](#user-content-class-version) objects.

This is the final list based on the version information in this font object as
well as in its parent [Family](#user-content-class-family) object. Please read the section about
[versioning](#versioning) above.





<div id="class-licenseusage"></div>

# _class_ LicenseUsage()



*Example JSON data:*
```json
{
    "keyword": "awesomefontsEULA",
    "seatsAllowed": 5,
    "seatsInstalled": 2,
    "upgradeURL": "https://awesomefonts.com/shop/upgradelicense/083487263904356"
}
```



### Attributes

[allowanceDescription](#class-licenseusage-attribute-allowancedescription)<br />[dateAddedForUser](#class-licenseusage-attribute-dateaddedforuser)<br />[keyword](#class-licenseusage-attribute-keyword)<br />[seatsAllowed](#class-licenseusage-attribute-seatsallowed)<br />[seatsInstalled](#class-licenseusage-attribute-seatsinstalled)<br />[upgradeURL](#class-licenseusage-attribute-upgradeurl)<br />

### Methods

[getLicense()](#class-licenseusage-method-getlicense)<br />

## Attributes

<div id="class-licenseusage-attribute-allowanceDescription"></div>

### allowanceDescription

In case of non-desktop font (see [Font.purpose](#user-content-class-font-attribute-purpose)), custom string for web fonts or app fonts reminding the user of the license’s limits, e.g. '100.000 page views/month'

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-licenseusage-attribute-dateAddedForUser"></div>

### dateAddedForUser

Date that the user has purchased this font or the font has become available to the user otherwise (like a new font within a foundry’s beta font repository). Will be used in the UI to signal which fonts have become newly available in addition to previously available fonts. This is not to be confused with the [Version.releaseDate](#user-content-class-version-attribute-releasedate), although they could be identical.

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ YYYY-MM-DD<br />
<div id="class-licenseusage-attribute-keyword"></div>

### keyword

Keyword reference of font’s license. This license must be specified in [Foundry.licenses](#user-content-class-foundry-attribute-licenses)

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-licenseusage-attribute-seatsAllowed"></div>

### seatsAllowed

In case of desktop font (see [Font.purpose](#user-content-class-font-attribute-purpose)), number of installations permitted by the user’s license.

__Required:__ False<br />
__Type:__ Int<br />
__Default value:__ 0

<div id="class-licenseusage-attribute-seatsInstalled"></div>

### seatsInstalled

In case of desktop font (see [Font.purpose](#user-content-class-font-attribute-purpose)), number of installations recorded by the API endpoint. This value will need to be supplied dynamically by the API endpoint through tracking all font installations through the `anonymousAppID` parameter of the 'installFonts' and 'uninstallFonts' command. Please note that the Type.World client app is currently not designed to reject installations of the fonts when the limits are exceeded. Instead it is in the responsibility of the API endpoint to reject font installations though the 'installFonts' command when the limits are exceeded. In that case the user will be presented with one or more license upgrade links.

__Required:__ False<br />
__Type:__ Int<br />
__Default value:__ 0

<div id="class-licenseusage-attribute-upgradeURL"></div>

### upgradeURL

URL the user can be sent to to upgrade the license of the font, for instance at the foundry’s online shop. If possible, this link should be user-specific and guide him/her as far into the upgrade process as possible.

__Required:__ False<br />
__Type:__ Str<br />


## Methods

<div id="class-licenseusage-method-getlicense"></div>

#### getLicense()

Returns the [License](#user-content-class-license) object that this font references.
        





<div id="class-installfontsresponse"></div>

# _class_ InstallFontsResponse()

This is the response expected to be returned when the API is invoked using the
`?commands=installFonts` parameter, and contains the requested binary fonts
attached as [InstallFontAsset](#user-content-class-installfontasset) obects.

*Example JSON data:*
```json
{
    "assets": [
        {
            "data": "emplNXpqdGpoNXdqdHp3enRq...",
            "encoding": "base64",
            "mimeType": "font/otf",
            "response": "success",
            "uniqueID": "AwesomeFonts-AwesomeFamily-Bold",
            "version": "1.1"
        }
    ],
    "response": "success"
}
```



### Attributes

[assets](#class-installfontsresponse-attribute-assets)<br />[errorMessage](#class-installfontsresponse-attribute-errormessage)<br />[response](#class-installfontsresponse-attribute-response)<br />

## Attributes

<div id="class-installfontsresponse-attribute-assets"></div>

### assets

List of [InstallFontAsset](#user-content-class-installfontasset) objects.

__Required:__ False<br />
__Type:__ List of [InstallFontAsset](#user-content-class-installfontasset) objects<br />
<div id="class-installfontsresponse-attribute-errorMessage"></div>

### errorMessage

Description of error in case of custom response type

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-installfontsresponse-attribute-response"></div>

### response

Type of response: 

`success`: The request has been processed successfully.

`error`: There request produced an error. You may add a custom error message in the `errorMessage` field.

`insufficientPermission`: The Type.World user account credentials couldn’t be confirmed by the publisher (which are checked with the central server) and therefore access to the subscription is denied.

`temporarilyUnavailable`: The service is temporarily unavailable but should work again later on.

`validTypeWorldUserAccountRequired`: The access to this subscription requires a valid Type.World user account connected to an app.

`loginRequired`: The access to this subscription requires that the user logs into the publisher’s website again to authenticate themselves. Normally, this happens after a subscription’s secret key has been invalidated. The user will be taken to the publisher’s website defined at [EndpointResponse.loginURL](#user-content-class-endpointresponse-attribute-loginurl). After successful login, a button should be presented to the user to reconnect to the same subscription that they are trying to access. To identify the subscription, the link that the user will be taken to will carry a `subscriptionID` parameter with the subscriptionID as defined in the subscription’s URL.



__Required:__ True<br />
__Type:__ Str<br />
__Format:__ To ensure the proper function of the entire Type.World protocol, your API endpoint *must* return the proper responses as per [this flow chart](https://type.world/documentation/Type.World%20Request%20Flow%20Chart.pdf). In addition to ensure functionality, this enables the response messages displayed to the user to be translated into all the possible languages on our side.<br />




<div id="class-installfontasset"></div>

# _class_ InstallFontAsset()

This is the response expected to be returned when the API is invoked using the
`?commands=installFonts` parameter.

*Example JSON data:*
```json
{
    "data": "emplNXpqdGpoNXdqdHp3enRq...",
    "encoding": "base64",
    "mimeType": "font/otf",
    "response": "success",
    "uniqueID": "AwesomeFonts-AwesomeFamily-Bold",
    "version": "1.1"
}
```



### Attributes

[data](#class-installfontasset-attribute-data)<br />[dataURL](#class-installfontasset-attribute-dataurl)<br />[encoding](#class-installfontasset-attribute-encoding)<br />[errorMessage](#class-installfontasset-attribute-errormessage)<br />[mimeType](#class-installfontasset-attribute-mimetype)<br />[response](#class-installfontasset-attribute-response)<br />[uniqueID](#class-installfontasset-attribute-uniqueid)<br />[version](#class-installfontasset-attribute-version)<br />

## Attributes

<div id="class-installfontasset-attribute-data"></div>

### data

Binary data as a string encoded as one of the following supported encodings: [InstallFontResponse.encoding](#user-content-class-installfontresponse-attribute-encoding). [InstallFontAsset.data](#user-content-class-installfontasset-attribute-data) and [InstallFontAsset.dataURL](#user-content-class-installfontasset-attribute-dataurl) are mutually exclusive; only one can be specified.

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-installfontasset-attribute-dataURL"></div>

### dataURL

HTTP link of font file resource. [InstallFontAsset.data](#user-content-class-installfontasset-attribute-data) and [InstallFontAsset.dataURL](#user-content-class-installfontasset-attribute-dataurl) are mutually exclusive; only one can be specified. The HTTP resource must be served under the correct MIME type specified in [InstallFontAsset.mimeType](#user-content-class-installfontasset-attribute-mimetype) and is expected to be in raw binary encoding; [InstallFontAsset.encoding](#user-content-class-installfontasset-attribute-encoding) is not regarded.

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-installfontasset-attribute-encoding"></div>

### encoding

Encoding type for font data in [InstallFontResponse.data](#user-content-class-installfontresponse-attribute-data). Currently supported: ['base64']

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-installfontasset-attribute-errorMessage"></div>

### errorMessage

Description of error in case of custom response type

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-installfontasset-attribute-mimeType"></div>

### mimeType

MIME Type of data. For desktop fonts, these are ['font/collection', 'font/otf', 'font/sfnt', 'font/ttf'].

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-installfontasset-attribute-response"></div>

### response

Type of response: 

`success`: The request has been processed successfully.

`error`: There request produced an error. You may add a custom error message in the `errorMessage` field.

`unknownFont`: No font could be identified for the given `fontID`.

`insufficientPermission`: The Type.World user account credentials couldn’t be confirmed by the publisher (which are checked with the central server) and therefore access to the subscription is denied.

`temporarilyUnavailable`: The service is temporarily unavailable but should work again later on.

`validTypeWorldUserAccountRequired`: The access to this subscription requires a valid Type.World user account connected to an app.

`loginRequired`: The access to this subscription requires that the user logs into the publisher’s website again to authenticate themselves. Normally, this happens after a subscription’s secret key has been invalidated. The user will be taken to the publisher’s website defined at [EndpointResponse.loginURL](#user-content-class-endpointresponse-attribute-loginurl). After successful login, a button should be presented to the user to reconnect to the same subscription that they are trying to access. To identify the subscription, the link that the user will be taken to will carry a `subscriptionID` parameter with the subscriptionID as defined in the subscription’s URL.

`revealedUserIdentityRequired`: The access to this subscription requires a valid Type.World user account and that the user agrees to having their identity (name and email address) submitted to the publisher upon font installation (closed workgroups only).

`seatAllowanceReached`: The user has exhausted their seat allowances for this font. The app may take them to the publisher’s website as defined in [LicenseUsage.upgradeURL](#user-content-class-licenseusage-attribute-upgradeurl) to upgrade their font license.



__Required:__ True<br />
__Type:__ Str<br />
__Format:__ To ensure the proper function of the entire Type.World protocol, your API endpoint *must* return the proper responses as per [this flow chart](https://type.world/documentation/Type.World%20Request%20Flow%20Chart.pdf). In addition to ensure functionality, this enables the response messages displayed to the user to be translated into all the possible languages on our side.<br />
<div id="class-installfontasset-attribute-uniqueID"></div>

### uniqueID

A machine-readable string that uniquely identifies this font within the subscription. Must match the requested fonts.

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-installfontasset-attribute-version"></div>

### version

Font version. Must match the requested fonts.

__Required:__ True<br />
__Type:__ Str<br />
__Format:__ Simple float number (1 or 1.01) or semantic versioning (2.0.0-rc.1) as per [semver.org](https://semver.org)<br />




<div id="class-uninstallfontsresponse"></div>

# _class_ UninstallFontsResponse()

This is the response expected to be returned when the API is invoked using the
`?commands=uninstallFonts` parameter, and contains empty responses as
[UninstallFontAsset](#user-content-class-uninstallfontasset) objects.
While empty of data, these asset objects are still necessary because each font
uninstallation request may return a different response, to which the GUI app needs
to respond to accordingly.

*Example JSON data:*
```json
{
    "assets": [
        {
            "response": "success",
            "uniqueID": "AwesomeFonts-AwesomeFamily-Bold"
        }
    ],
    "response": "success"
}
```



### Attributes

[assets](#class-uninstallfontsresponse-attribute-assets)<br />[errorMessage](#class-uninstallfontsresponse-attribute-errormessage)<br />[response](#class-uninstallfontsresponse-attribute-response)<br />

## Attributes

<div id="class-uninstallfontsresponse-attribute-assets"></div>

### assets

List of [UninstallFontAsset](#user-content-class-uninstallfontasset) objects.

__Required:__ False<br />
__Type:__ List of [UninstallFontAsset](#user-content-class-uninstallfontasset) objects<br />
<div id="class-uninstallfontsresponse-attribute-errorMessage"></div>

### errorMessage

Description of error in case of custom response type

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-uninstallfontsresponse-attribute-response"></div>

### response

Type of response: 

`success`: The request has been processed successfully.

`error`: There request produced an error. You may add a custom error message in the `errorMessage` field.

`insufficientPermission`: The Type.World user account credentials couldn’t be confirmed by the publisher (which are checked with the central server) and therefore access to the subscription is denied.

`temporarilyUnavailable`: The service is temporarily unavailable but should work again later on.

`validTypeWorldUserAccountRequired`: The access to this subscription requires a valid Type.World user account connected to an app.

`loginRequired`: The access to this subscription requires that the user logs into the publisher’s website again to authenticate themselves. Normally, this happens after a subscription’s secret key has been invalidated. The user will be taken to the publisher’s website defined at [EndpointResponse.loginURL](#user-content-class-endpointresponse-attribute-loginurl). After successful login, a button should be presented to the user to reconnect to the same subscription that they are trying to access. To identify the subscription, the link that the user will be taken to will carry a `subscriptionID` parameter with the subscriptionID as defined in the subscription’s URL.



__Required:__ True<br />
__Type:__ Str<br />
__Format:__ To ensure the proper function of the entire Type.World protocol, your API endpoint *must* return the proper responses as per [this flow chart](https://type.world/documentation/Type.World%20Request%20Flow%20Chart.pdf). In addition to ensure functionality, this enables the response messages displayed to the user to be translated into all the possible languages on our side.<br />




<div id="class-uninstallfontasset"></div>

# _class_ UninstallFontAsset()

This is the response expected to be returned when the API is invoked using the
`?commands=uninstallFonts` parameter.

*Example JSON data:*
```json
{
    "response": "success",
    "uniqueID": "AwesomeFonts-AwesomeFamily-Bold"
}
```



### Attributes

[errorMessage](#class-uninstallfontasset-attribute-errormessage)<br />[response](#class-uninstallfontasset-attribute-response)<br />[uniqueID](#class-uninstallfontasset-attribute-uniqueid)<br />

## Attributes

<div id="class-uninstallfontasset-attribute-errorMessage"></div>

### errorMessage

Description of error in case of custom response type

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-uninstallfontasset-attribute-response"></div>

### response

Type of response: 

`success`: The request has been processed successfully.

`error`: There request produced an error. You may add a custom error message in the `errorMessage` field.

`unknownFont`: No font could be identified for the given `fontID`.

`insufficientPermission`: The Type.World user account credentials couldn’t be confirmed by the publisher (which are checked with the central server) and therefore access to the subscription is denied.

`temporarilyUnavailable`: The service is temporarily unavailable but should work again later on.

`validTypeWorldUserAccountRequired`: The access to this subscription requires a valid Type.World user account connected to an app.

`loginRequired`: The access to this subscription requires that the user logs into the publisher’s website again to authenticate themselves. Normally, this happens after a subscription’s secret key has been invalidated. The user will be taken to the publisher’s website defined at [EndpointResponse.loginURL](#user-content-class-endpointresponse-attribute-loginurl). After successful login, a button should be presented to the user to reconnect to the same subscription that they are trying to access. To identify the subscription, the link that the user will be taken to will carry a `subscriptionID` parameter with the subscriptionID as defined in the subscription’s URL.

`unknownInstallation`: This font installation (combination of app instance and user credentials) is unknown. The response with this error message is crucial to remote de-authorization of app instances. When a user de-authorizes an entire app instance’s worth of font installations, such as when a computer got bricked and re-installed or is lost, the success of the remote de-authorization process is judged by either `success` responses (app actually had this font installed and its deletion has been recorded) or `unknownInstallation` responses (app didn’t have this font installed). All other reponses count as errors in the remote de-authorization process.



__Required:__ True<br />
__Type:__ Str<br />
__Format:__ To ensure the proper function of the entire Type.World protocol, your API endpoint *must* return the proper responses as per [this flow chart](https://type.world/documentation/Type.World%20Request%20Flow%20Chart.pdf). In addition to ensure functionality, this enables the response messages displayed to the user to be translated into all the possible languages on our side.<br />
<div id="class-uninstallfontasset-attribute-uniqueID"></div>

### uniqueID

A machine-readable string that uniquely identifies this font within the subscription. Must match the requested fonts.

__Required:__ True<br />
__Type:__ Str<br />
