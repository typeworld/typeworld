# Type.World JSON Protocol (Version __version__)

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

__classTOC__


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
__testcode1__
```

Will output the following JSON code:

```json
__testcode1result__
```

### Example 2: InstallableFonts Response

Below you see the minimum possible object tree for a sucessful `installabefonts` response.

```python
__testcode2__
```

Will output the following JSON code:

```json
__testcode2result__
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
