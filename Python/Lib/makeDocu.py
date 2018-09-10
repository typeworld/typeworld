# -*- coding: utf-8 -*-

import os
from typeWorld.api import *
from typeWorld.api.base import *

api = APIRoot()

docstrings = api.docu()


docstring = '''

# typeWorld.api Reference


## Preamble

The Type.World protocol and software is in **alpha** stage. Changes to the protocol may still occur at any time.

The protocol and app are expected to stabilize by the end of 2018.


## Contents

1. [Introduction](#introduction)
2. [List of Classes](#classTOC)
3. [Object model](#objectmodel)
4. [Versioning](#versioning)
5. [Use of Languages/Scripts](#languages)
6. [Example Code](#example)
7. [Class Reference](#classreference)





<div id="introduction"></div>

## Introduction

The Type.World API is designed to be installed on web servers and allow a font installer app, such as the upcoming GUI app under the same name, to load and install fonts on people’s computers through a one-click process involving a custom URI such as typeworld://

Requires `deepdiff` for recursive dictionary comparison, but only if you wish to compare two instances of `APIRoot()` objects, and `semver` for version number comparison. You can install them through `pip`:

```sh
pip install deepdiff
pip install semver
```

This code is very anal about the format of the data you put in. If it detects a wrong data type (like an float number you are putting into a fields that is supposed to hold integers), it will immediately throw a tantrum. Later, when you want to generate the JSON code for your response, it will perform additional logic checks, like checking if the designers are actually defined that you are referencing in the fonts. 

Any such mistakes will not pass. That’s because I don’t want to be dealing with badly formatted data in the GUI app and have to push out an update every time I discover that someone supplies badly formatted data. Obviously, you don’t need to use this library to create your JSON responses and can still format your data badly using your own routines. In this case the data will be checked in the app using the very same code and then rejected. Therefore, please use the API Validator at https://type.world/validator/ to check your own data for your web-facing API endpoint.


<div id="classTOC"></div>

## List of Classes

__classTOC__


<div id="objectmodel"></div>

## Object model

![](../../object-model.png)



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




<div id="languages"></div>

## Use of Languages/Scripts

All text definitions in the Type.World JSON Protocol are multi-lingual by default using the [MultiLanguageText](#class_MultiLanguageText) class. The application will then decide which language to pick to display to the user in case several languages are defined for one attribute, based on the user’s OS language and app preferences.

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
print api.sameContent(api2)
```


Will, or should print:

```python
True
```



<div id="classreference"></div>

## Class Reference




'''






handles = []
for key in [x[0] for x in docstrings]:
	if not key in handles:
		handles.append(key)

classTOC = ''
for handle in handles:
	classTOC += '- [%s](#class_%s)<br />\n' % (handle, handle)
classTOC += '\n\n'

docstring = docstring.replace('__classTOC__', classTOC)

for handle in handles:
	for className, string in docstrings:
		if handle == className:
			docstring += string
			docstring += '\n\n'
			break



if not 'TRAVIS' in os.environ:
	from ynlib.files import WriteToFile
	WriteToFile(os.path.join(os.path.dirname(__file__), 'typeWorld', 'README.md'), docstring)
