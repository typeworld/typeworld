# typeWorld.api Reference


## Preamble

The Type.World protocol and software is in **alpha** stage. Changes to the protocol may still occur at any time.
The protocol and app are expected to stabilize by the end of 2018.


## Contents

1. [Introduction](#user-content-introduction)
1. [Server Interaction](#user-content-serverinteraction)
1. [Security Design](#user-content-securitydesign)
1. [Response Flow Chart](#user-content-responseflowchart)
1. [Protocol Changes](#user-content-protocolchanges)
1. [List of Classes](#user-content-classtoc)
1. [Object model](#user-content-objectmodel)
1. [Versioning](#user-content-versioning)
1. [Use of Languages/Scripts](#user-content-languages)
1. [Example Code](#user-content-example)
1. [Class Reference](#user-content-classreference)





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


<div id="serverinteraction"></div>

## Server Interaction

### The subscription URL

By clicking the *Install in Type.World App* button on your SSL-encrypted website, a URL of the following scheme gets handed off to the app through a custom protocol handler:

`typeworldjson://https//[subscriptionID[:secretKey]@]awesomefonts.com/api/`

*Note: Even though this notation suggests the use of HTTP authentication, we will not make use of it. See [Serving JSON responses](#user-content-servingjsonresponses) below for more information.*

Example for a protected subscription:
`typeworldjson://https//subscriptionID:secretKey@awesomefonts.com/api/`

Example for a publicly accessible subscription without `secretKey`, but `subscriptionID` still used to identify a particular subscription: `typeworldjson://https//subscriptionID@awesomefonts.com/api/`

Example for a publicly accessible subscription without `secretKey` or `subscriptionID`. This API endpoint has exactly one subscription to serve: `typeworldjson://https//awesomefonts.com/api/`

The URL parts in detail:

* `typeworldjson://` This is one of the two custom protocol handlers used by the Type.World app. The app advertises the handler to the operating system, and upon clicking such a link, the operating system calls the app and hands over the link.
* `https//` The transport protocol to be used, in this case SSL-encrypted HTTPS. *Note:* because URLs are only allowed to contain one `://` sequence which is already in use to denote the custom protocol handler `typeworldjson://`, the colon `:` will be stripped off of the URL in the browser, even if you define it a second time. The Type.World app will internally convert `https//` back to `https://`.
* `subscriptionID` uniquely identifies a subscription. In case of per-user subscriptions, you would probably use it to identify a user and then decide which fonts to serve him/her. The `subscriptionID` should be an anonymous string and must not contain either `:` or `@` and is optional for publicly accessible subscriptions (such as free fonts).
* `secretKey` matches with the `subscriptionID` and is used to authenticate the request. This secret key is saved in the OS’s keychain. The `secretKey ` must not contain either `:` or `@` and is optional for publicly accessible subscriptions (such as free fonts). The secret key is actually not necessary to authenticate the request against the server. Instead it’s necessary to store a secret key in the user’s OS keychain so that complete URLs are not openly visible.
* `awesomefonts.com/api/` is where your API endpoint sits and waits to serve fonts to your customers.


<div id="servingjsonresponses"></div>

### Serving JSON responses

#### `POST` requests

To avoid the subscription URL complete with the `subscriptionID` and `secretKey` showing up in server logs, your server should serve protected font (meta) data only when replying to `POST` requests, as request attributes will then be transmitted in the HTTP headers and will be invisible in server logs.

The app will ask for the JSON responses at your API endpoint `https://awesomefonts.com/api/` and will hand over some or all of the following parameters through HTTP headers:

* `command` The command to reply to, such as `installableFonts`.
* `subscriptionID` The aforementioned ID to uniquely identify the fonts you serve.
* `secretKey` The aforementioned secret key to authenticate the requester.
* `anonymousAppID` is a key that uniquely identifies the Type.World app installation. You should use this to track how often fonts have been installed through the app for a certain user and reject requests once the limit has been reached.
* `fontID` identifying the font to install or uninstall. This will be taken from the [Font.uniqueID](#user-content-class-font-attribute-uniqueid) attribute.
* `fontVersion` identifying the font’s version to install
* `userEmail` and `userName` in case the user has a Type.World user account and has explicitly agreed to reveal his/her identity on a per-subscription basis. This only makes sense in a trusted custom type development environment where the type designers may want to get in touch personally with the font’s users in a small work group, for instance in a branding agency. This tremendously streamlines everyone’s workflow. If necessary, a publisher in a trusted custom type development environment could reject the serving of subscriptions to requesters who are unidentified.

#### `GET` requests

For simplicity’s sake, you should reject incoming `GET` requests altogether to force the requester into using `POST` requests. This is for your own protection, as `GET` requests complete with the `subscriptionID` and `secretKey` might show up in server logs and therefore pose an attack vector to your protected fonts and meta data.

I suggest to return a `405 Method Not Allowed` HTTP response for all `GET` requests.

#### WARNING:

Whatever you do with your server, bear in mind that the parameters attached to the requests could be malformed to contain [SQL injection attacks](https://www.w3schools.com/sql/sql_injection.asp) and the likes and need to be quarantined.


<div id="securitydesign"></div>

## Security Design


For protected subscriptions, the publisher provides a subscription link that contains a subscription ID and a secret key to identify a subscription. The secret key is only used on the client computer and stored invisibly in the OS’s keychain, to prevent reading out all subscriptions on a client's computer by third party software. An additional single-use token may be appended to the URL.

`typeworldjson://https//subscriptionID:secretKey@awesomefonts.com/api/[?token=singleusetoken]`

The security design outlined below consists of two optional layers.

The first layer restricts initial access to a subscription to users who are legitimately logged in to a website. Through the website, the subscription link will contain a single-use access token that gets invalidated on first access of the subscription. This way it is preventable that subscription links spread and get accessed by users other than the legitimate user.

The second layer restricts access to a subscription to verified users. The publisher’s server keeps a ledger of which users and app instances are legitimate. The central server and the publisher’s server are in communication with each other over who is legitimate. This second layer serves the purpose of being able to invalidate certain app instances once a computer gets stolen (and continued to be used). This is only possible if app instances get recorded in a Type.World user profile.

### Layer 1: Single-use access tokens to authorize access by the publisher

As a voluntary security measure to prevent unauthorized access, the publisher may append a single-use access token to the URL. This access token will only be available to customers that are logged in to the publisher’s web site. 
Upon first access of the JSON API endpoint, the `anonymousAppID` parameter appended to the API call will be saved as a valid app ID on the publisher’s server, and the single-use access token will be invalidated. From then onwards, only requests carrying a valid known `anonymousAppID` will be granted access.

This first access of the publisher’s API endpoint is expected to happen instantly, as the app will be triggered by clicking on the activation link on the publisher’s web site and the subscription’s content will be loaded.

This prevents the subscription URL from being passed on in unauthorized ways, as its use in other unauthorized app instances will then carry either an invalid access token or an unknown `anonymousAppID`.

(Passing on subscriptions to other users will be possible through the central Type.World server using its JSON API under the `inviteUserToSubscription` command), see below.)

### Layer 2: Access restriction to users with Type.World user account

As yet another additional voluntary security measure, the publisher could decide to grant access to their API endpoint only to users with a registered Type.World user account. Because API calls will also carry an `anonymousTypeWorldUserID` parameter (in case the user’s app instance is linked to a Type.World user account), this user ID can be verified with the central Type.World server using its JSON API under the `verifyCredentials` command.

After verification, the `anonymousTypeWorldUserID` should be saved together with the valid `anonymousAppID` on the publisher’s server and not be verified upon every access to the API endpoint to speed up the responses and reduce strain on the central server.

### De-authorization of app instances by the user

Subscriptions are synchronized with the central server for registered users and users can de-authorize the subscriptions for an entire app instance through the Type.World web site (when a computer got stolen for example). 

The main incentive for the user to de-authorize his/her older app instances that are not accessible any more is to free up font installations, because the font installations of the lost computer are still counted in the publisher's tracking of installed seats with regards to each font license. 

The central server will inform the publisher’s API endpoint of a de-authorization under the `setAnonymousAppIDStatus` command. Additionally, an app’s status can be verified with the central Type.World server using its JSON API under the `verifyCredentials` command. Again, to speed up the responses and reduce strain on the central server, the publisher’s server should save the invalidated `anonymousAppID`, regardless of whether it had prior knowledge of this particular `anonymousAppID`.

A publisher should then choose to reject access to its API endpoint for invalidated `anonymousAppID`s.

Should the de-authorized app instance regain access to the internet (in case the computer is actually stolen rather than lost/broken), all fonts and subscriptions will be deleted from it instantly, and because all referenced publishers have already been informed of the de-authorization, new font installations thereafter will also be rejected (by the publishers directly). And in case the stolen computer does not regain access to the internet again, the already installed fonts will inevitably continue to live on it, but new installations will be rejected, and seats will be freed for the user anyway.



### Central subscription invitation infrastructure

Because spreading subscription URLs by email (or other means) is potentially unsafe from eavesropping, the central Type.World server provides an invitation API using its JSON API under the `inviteUserToSubscription` command (or directly in the app’s GUI). Therefore, only users with a registered Type.World user account can be invited. Here, users will be identified by the email address of their Type.World user account (like Dropbox or Google Documents). There is no way to search the Type.World user database for users. Only valid registered email addresses will be accepted.

When a subscription gets activated after an invitation, the central server will inform the publisher’s API endpoint of the successful invitation under the `setAnonymousAppIDStatus` command. The publisher’s server will then save the newly introduced `anonymousAppID` to be valid in combination with the `anonymousTypeWorldUserID` parameter.

### Central server authorization

API calls from the central Type.World server to the publisher’s API endpoint for the `setAnonymousAppIDStatus` command will be authorized through a secret API key to be obtained via the user account on the Type.World web site. 

Likewise, the access to the `verifyCredentials` command on the central Type.World server will be restricted to holders of that API.

### Splitting of responsibility and server unavailability

Because the central Type.World server cannot always be available for querying (although it should, of course), and because the the whole Type.World project is an exercise in self-empowerment for independent type publishers, publishers are requested to keep track of the `anonymousAppID`/`anonymousTypeWorldUserID` pairs for a subscription. Since the central server will proactively inform the publisher’s server of newly added (invitation) or invalidated (de-authorization) `anonymousAppID`s, the only truly necessary verification with the central server is upon first subscription access by an app (through the `installableFonts` command), to check for a user ID’s validity.

Should the central server then not respond, the publisher’s API endpoint should respond with a `temporarilyUnavailable` response type (see [InstallableFontsResponse.type](#user-content-class-installablefontsresponse-attribute-type), of which the user will be notified in the user interface.

User verification with the central server for the `installFont` and `uninstallFont` commands is unnecessary, because these commands will always succeed a prior `installableFonts` command, upon which the publisher’s API endpoint received knowledge of the `anonymousAppID` and `anonymousTypeWorldUserID` pairs.

I will monitor and potentially restrict the user verification calls on the central server. In theory, there should only ever be one single verification request for one `anonymousAppID` and one `anonymousTypeWorldUserID` by one publisher’s API endpoint.

If the publisher’s own database doesn't contain a valid `anonymousAppID`/`anonymousTypeWorldUserID` for a subscription, the publisher shall be entitled to verify the credentials with the central server once, and add the response to its database, in case the publisher’s server wasn’t available when the central server wanted to inform it of an `anonymousAppID` status change. This way, our responsibilities are equally shared. 🙏



<div id="responseflowchart"></div>

## Response Flow Chart

A high-resolution version of this flow chart can be viewed as a PDF [here](https://type.world/documentation/Type.World%20Request%20Flow%20Chart.pdf).



<div id="protocolchanges"></div>

## Protocol Changes

#### Version 0.1.4-alpha

* `Font.requiresUserID` renamed to [`Font.protected`](#user-content-class-font-attribute-protected)


<div id="classtoc"></div>

## List of Classes

__classTOC__


<div id="objectmodel"></div>

## Object model

![](../../object-model.png)



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