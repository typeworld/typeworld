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

This code is very anal about the format of the data you put in. If it detects a wrong data type (like an float number you are putting into a fields that is supposed to hold integers), it will immediately throw a tantrum. Later, when you want to generate the JSON code for your response, it will perform additional logic checks, like checking if the designers are actually defined that you are referencing in the fonts. 

Any such mistakes will not pass. That’s because I don’t want to be dealing with badly formatted data in the GUI app and have to push out an update every time I discover that someone supplies badly formatted data. Obviously, you don’t need to use this library to create your JSON responses and can still format your data badly using your own routines. In this case the data will be checked in the app using the very same code and then rejected. Therefore, please use the API Validator at https://type.world/validator/ to check your own data for your web-facing API endpoint.


<div id="serverinteraction"></div>

## Server Interaction

### The subscription URL

By clicking the *Install in Type.World App* button on your SSL-encrypted website, a URL of the following scheme gets handed off to the app through a custom protocol handler:

`typeworld://json+https//[subscriptionID[:secretKey]@]awesomefonts.com/api/`

*Note: Even though this notation suggests the use of HTTP authentication, we will not make use of it. See [Serving JSON responses](#user-content-servingjsonresponses) below for more information.*

Example for a protected subscription:
`typeworld://json+https//subscriptionID:secretKey@awesomefonts.com/api/`

Example for a publicly accessible subscription without `secretKey`, but `subscriptionID` still used to identify a particular subscription: `typeworld://json+https//subscriptionID@awesomefonts.com/api/`

Example for a publicly accessible subscription without `secretKey` or `subscriptionID`. This API endpoint has exactly one subscription to serve: `typeworld://json+https//awesomefonts.com/api/`

The URL parts in detail:

* `typeworld://` This is the protocol handler used by the Type.World app. The app advertises the handler to the operating system, and upon clicking such a link, the operating system calls the app and hands over the link.
* `json` The protocol to be used within the Type.World app. Currently, only the Type.World JSON Protocol is available to use.
* `https//` The transport protocol to be used, in this case SSL-encrypted HTTPS. *Note:* because valid URLs are only allowed to contain one `://` sequence which is already in use to denote the custom protocol handler `typeworld://`, the colon `:` will be stripped off of the URL in the browser, even if you define it there a second time. The Type.World app will internally convert `https//` back to `https://`.
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

`typeworld://json+https//subscriptionID:secretKey@awesomefonts.com/api/[?token=singleusetoken]`

The security design outlined below consists of two optional layers.

The first layer restricts initial access to a subscription to users who are legitimately logged in to a website. Through the website, the subscription link will contain a single-use access token that gets invalidated on first access of the subscription. This way it is preventable that subscription links spread and get accessed by users other than the legitimate user.

The second layer restricts access to a subscription to verified users. The publisher’s server keeps a ledger of which users and app instances are legitimate. The central server and the publisher’s server are in communication with each other over who is legitimate. This second layer serves the purpose of being able to invalidate certain app instances once a computer gets stolen (and continued to be used). This is only possible if app instances get recorded in a Type.World user profile.

In detail:

### Layer 1: Single-use access tokens to authorize access by the publisher

As a voluntary security measure to prevent unauthorized access, the publisher may append a single-use access token to the URL. This access token will only be available to customers that are logged in to the publisher’s web site. 
Upon first access of the JSON API endpoint, the `anonymousAppID` parameter appended to the API call will be saved as a valid app ID on the publisher’s server, and the single-use access token will be invalidated. A new single-use access token will be generated and provided for future access of the subscription link on the publisher’s website. Only requests carrying a valid known `anonymousAppID` will be granted access.

This first access of the publisher’s API endpoint is expected to happen instantly, as the app will be triggered by clicking on the activation link on the publisher’s web site and the subscription’s content will be loaded.

This prevents the subscription URL from being passed on in unauthorized ways, as its use in other unauthorized app instances will then carry either an invalid access token or an unknown `anonymousAppID`.

(Passing on subscriptions to other users will be possible through the central Type.World server using its JSON API under the `inviteTypeWorldUserToSubscription` command), see below.)

### Layer 2: Access restriction to users with Type.World user account

As yet another additional voluntary security measure, the publisher could decide to grant access to their API endpoint only to users with a registered Type.World user account. Because API calls will also carry an `anonymousTypeWorldUserID` parameter (in case the user’s app instance is linked to a Type.World user account), this user ID can be verified with the central Type.World server using its JSON API under the `verifyCredentials` command. If no `anonymousTypeWorldUserID` parameter is attached to the request or the `anonymousAppID` was found to be invalid, the `validTypeWorldUserAccountRequired` response will be returned, so that the user can be informed to get him/herself a valid user account first, then try again.

After verification, the `anonymousTypeWorldUserID` should be saved together with the valid `anonymousAppID` on the publisher’s server and not be verified upon every access to the API endpoint to speed up the responses and reduce strain on the central server.

### De-authorization of app instances by the user

Subscriptions are synchronized with the central server for registered users and users can de-authorize the subscriptions for an entire app instance through the Type.World web site (when a computer got stolen for example). 

The main incentive for the user to de-authorize his/her older app instances that are not accessible any more is to free up font installations, because the font installations of the lost computer are still counted in the publisher's tracking of installed seats with regards to each font license. 

The central server will inform the publisher’s API endpoint of a de-authorization under the `setAnonymousAppIDStatus` command. Additionally, an app’s status can be verified with the central Type.World server using its JSON API under the `verifyCredentials` command. Again, to speed up the responses and reduce strain on the central server, the publisher’s server should save the invalidated `anonymousAppID`, regardless of whether it had prior knowledge of this particular `anonymousAppID`.

A publisher should then choose to reject access to its API endpoint for invalidated `anonymousAppID`s.

Should the de-authorized app instance regain access to the internet (in case the computer is actually stolen rather than lost/broken), all fonts and subscriptions will be deleted from it instantly, and because all referenced publishers have already been informed of the de-authorization, new font installations thereafter will also be rejected (by the publishers directly). And in case the stolen computer does not regain access to the internet again, the already installed fonts will inevitably continue to live on it, but new installations will be rejected, and seats will be freed for the user anyway.



### Central subscription invitation infrastructure

Because spreading subscription URLs by email (or other means) is potentially unsafe from eavesropping, the central Type.World server provides an invitation API using its JSON API under the `inviteTypeWorldUserToSubscription` command (or directly in the app’s GUI). Therefore, only users with a registered Type.World user account can be invited. Here, users will be identified by the email address of their Type.World user account (like Dropbox or Google Documents). There is no way to search the Type.World user database for users. Only valid registered email addresses will be accepted.

When a subscription gets activated after an invitation, the central server will inform the publisher’s API endpoint of the successful invitation under the `setAnonymousAppIDStatus` command. The publisher’s server will then save the newly introduced `anonymousAppID` to be valid in combination with the `anonymousTypeWorldUserID` parameter.

It is not possible to provide this invitation infrastructure to users without a Type.World user account, because otherwise a notification about the invitation needs to be sent out which can be intercepted and accessed before the legitimate user gets access. 

Without a Type.World user account, this notification, however formed, would be the key to the subscription. With a Type.World user account, the account itself is the key, and any form of notification of the invitation, such as by email, is meaningless without the previously existing user account.

### Central server authorization

API calls from the central Type.World server to the publisher’s API endpoint for the `setAnonymousAppIDStatus` command will be authorized through a secret API key to be obtained via the user account on the Type.World web site. 

Likewise, the access to the `verifyCredentials` command on the central Type.World server will be restricted to holders of that same secret API key.

### Splitting of responsibility and server unavailability

Because the central Type.World server cannot always be available for querying (although it should, of course), and because the the whole Type.World project is an exercise in self-empowerment for independent type publishers, publishers are requested to keep track of the `anonymousAppID`/`anonymousTypeWorldUserID` pairs for a subscription. Since the central server will proactively inform the publisher’s server of newly added (invitation) or invalidated (de-authorization) `anonymousAppID`s, the only truly necessary verification with the central server is upon first subscription access by an app (through the `installableFonts` command), to check for a user ID’s validity.

Should the central server then not respond, the publisher’s API endpoint should respond with a `temporarilyUnavailable` response type (see [InstallableFontsResponse.type](#user-content-class-installablefontsresponse-attribute-type), of which the user will be notified in the user interface.

User verification with the central server for the `installFont` and `uninstallFont` commands is unnecessary, because these commands will always succeed a prior `installableFonts` command, upon which the publisher’s API endpoint received knowledge of the `anonymousAppID` and `anonymousTypeWorldUserID` pairs.

If the publisher’s own database doesn't contain a valid `anonymousAppID`/`anonymousTypeWorldUserID` for a subscription, the publisher shall be entitled to verify the credentials with the central server once, and add the response to its database, in case the publisher’s server wasn’t available when the central server wanted to inform it of an `anonymousAppID` status change. This way, our responsibilities are equally shared. 🙏

I will monitor and potentially restrict the user verification calls on the central server. In theory, there should only ever be one single verification request for one `anonymousAppID` and one `anonymousTypeWorldUserID` by one publisher’s API endpoint.



<div id="responseflowchart"></div>

## Response Flow Chart

![](../../../images/Request-flow-chart.png)

A high-resolution version of this flow chart can be viewed as a PDF [here](https://type.world/documentation/Type.World%20Request%20Flow%20Chart.pdf).



<div id="protocolchanges"></div>

## Protocol Changes

#### Version 0.1.6-alpha

* `Font.beta` renamed to [`Font.prelease`](#user-content-class-font-attribute-prerelease)

#### Version 0.1.4-alpha

* `Font.requiresUserID` renamed to [`Font.protected`](#user-content-class-font-attribute-protected)

<div id="classtoc"></div>

## List of Classes

- [RootResponse](#user-content-class-rootresponse)<br />
- [MultiLanguageText](#user-content-class-multilanguagetext)<br />
- [InstallableFontsResponse](#user-content-class-installablefontsresponse)<br />
- [Designer](#user-content-class-designer)<br />
- [MultiLanguageLongText](#user-content-class-multilanguagelongtext)<br />
- [Foundry](#user-content-class-foundry)<br />
- [LicenseDefinition](#user-content-class-licensedefinition)<br />
- [Family](#user-content-class-family)<br />
- [Version](#user-content-class-version)<br />
- [Font](#user-content-class-font)<br />
- [LicenseUsage](#user-content-class-licenseusage)<br />
- [InstallFontResponse](#user-content-class-installfontresponse)<br />
- [UninstallFontResponse](#user-content-class-uninstallfontresponse)<br />
- [SetAnonymousAppIDStatusResponse](#user-content-class-setanonymousappidstatusresponse)<br />





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

Below you see the minimum possible object tree for a sucessful `root` response.

```python

# Import module
from typeWorld.api import *

# Root of API
root = RootResponse()
root.name.en = 'Font Publisher'
root.canonicalURL = 'https://fontpublisher.com/api/'
root.adminEmail = 'admin@fontpublisher.com'
root.supportedCommands = [x['keyword'] for x in COMMANDS] # this API supports all commands

# Create API response as JSON
json = root.dumpJSON()

# Let’s see it
print(json)
```

Will output the following JSON code:

```json
{
  "licenseIdentifier": "CC-BY-NC-ND-4.0",
  "public": false,
  "privacyPolicy": "https://type.world/legal/default/PrivacyPolicy.html",
  "termsOfServiceAgreement": "https://type.world/legal/default/TermsOfService.html",
  "version": "0.1.7-alpha",
  "name": {
    "en": "Font Publisher"
  },
  "canonicalURL": "https://fontpublisher.com/api/",
  "adminEmail": "admin@fontpublisher.com",
  "supportedCommands": [
    "installableFonts",
    "installFont",
    "uninstallFont",
    "setAnonymousAppIDStatus"
  ]
}
```

### Example 2: InstallableFonts Response

Below you see the minimum possible object tree for a sucessful `installabefonts` response.

```python

# Import module
from typeWorld.api import *

# Response for 'availableFonts' command
installableFonts = InstallableFontsResponse()
installableFonts.type = 'success'

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
family.designers.append('max')
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

# Output API response as JSON
json = installableFonts.dumpJSON()

# Let’s see it
print(json)
```

Will output the following JSON code:

```json
{
  "version": "0.1.7-alpha",
  "prefersRevealedUserIdentity": false,
  "type": "success",
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
      "name": {
        "en": "Awesome Fonts"
      },
      "website": "https://awesomefonts.com",
      "uniqueID": "awesomefontsfoundry",
      "licenses": [
        {
          "keyword": "awesomeFontsEULA",
          "name": {
            "en": "Awesome Fonts Desktop EULA"
          },
          "URL": "https://awesomefonts.com/EULA/"
        }
      ],
      "families": [
        {
          "name": {
            "en": "Awesome Sans"
          },
          "designers": [
            "max"
          ],
          "uniqueID": "awesomefontsfoundry-awesomesans",
          "versions": [
            {
              "number": "0.1"
            }
          ],
          "fonts": [
            {
              "status": "stable",
              "name": {
                "en": "Regular"
              },
              "postScriptName": "AwesomeSans-Regular",
              "purpose": "desktop",
              "uniqueID": "awesomefontsfoundry-awesomesans-regular",
              "usedLicenses": [
                {
                  "keyword": "awesomeFontsEULA"
                }
              ],
              "format": "otf"
            }
          ]
        }
      ]
    }
  ]
}

```

Next we load that same JSON code back into an object tree, such as the GUI app would do when it loads the JSON from font publisher’s API endpoints.

```python
# Load a second API instance from that JSON
installableFontsInput = InstallableFontsResponse()
installableFontsInput.loadJSON(json)

# Let’s see if they are identical (requires deepdiff)
print(installableFontsInput.sameContent(installableFonts))
```


Will, or should print:

```python
True
```



<div id="classreference"></div>

## Class Reference<div id="class-rootresponse"></div>

# _class_ RootResponse()

This is the main class that sits at the root of all API responses. It contains some mandatory information about the API endpoint such as its name and admin email, the copyright license under which the API endpoint issues its data, and whether or not this endpoint can be publicized about.

Any API response is expected to carry this minimum information, even when invoked without a particular command.

In case the API endpoint has been invoked with a particular command, the response data is attached to the [APIRoot.response](#user-content-class-apiroot-attribute-response) attribute.


```python
response = RootResponse()
response.name.en = u'Font Publisher'
response.canonicalURL = 'https://fontpublisher.com/api/'
response.adminEmail = 'admin@fontpublisher.com'
response.supportedCommands = ['installableFonts', 'installFonts', 'uninstallFonts']
```

        

### Attributes

[adminEmail](#class-rootresponse-attribute-adminemail)<br />[backgroundColor](#class-rootresponse-attribute-backgroundcolor)<br />[canonicalURL](#class-rootresponse-attribute-canonicalurl)<br />[licenseIdentifier](#class-rootresponse-attribute-licenseidentifier)<br />[logo](#class-rootresponse-attribute-logo)<br />[name](#class-rootresponse-attribute-name)<br />[privacyPolicy](#class-rootresponse-attribute-privacypolicy)<br />[public](#class-rootresponse-attribute-public)<br />[supportedCommands](#class-rootresponse-attribute-supportedcommands)<br />[termsOfServiceAgreement](#class-rootresponse-attribute-termsofserviceagreement)<br />[version](#class-rootresponse-attribute-version)<br />[website](#class-rootresponse-attribute-website)<br />

### Methods

[customValidation()](#class-rootresponse-method-customvalidation)<br />[sameContent()](#class-rootresponse-method-samecontent)<br />

## Attributes

<div id="class-rootresponse-attribute-adminEmail"></div>

### adminEmail

API endpoint Administrator. This email needs to be reachable for various information around the Type.World protocol as well as technical problems.

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-rootresponse-attribute-backgroundColor"></div>

### backgroundColor

Publisher’s preferred background color. This is meant to go as a background color to the logo at [APIRoot.logo](#user-content-class-apiroot-attribute-logo)

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ Hex RRGGBB (without leading #)<br />
<div id="class-rootresponse-attribute-canonicalURL"></div>

### canonicalURL

Official API endpoint URL, bare of ID keys and other parameters. Used for grouping of subscriptions. It is expected that this URL will not change. When it does, it will be treated as a different publisher.

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-rootresponse-attribute-licenseIdentifier"></div>

### licenseIdentifier

Identifier of license under which the API endpoint publishes its data, as per [https://spdx.org/licenses/](). This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. Licenses of the individual responses can be fine-tuned in the respective responses.

__Required:__ True<br />
__Type:__ Str<br />
__Default value:__ CC-BY-NC-ND-4.0

<div id="class-rootresponse-attribute-logo"></div>

### logo

URL of logo of API endpoint, for publication. Specifications to follow.

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ This resource may get downloaded and cached on the client computer. To ensure up-to-date resources, append a unique ID to the URL such as a timestamp of the resources’s upload on your server, e.g. https://awesomefonts.com/xyz/regular/specimen.pdf?t=1548239062<br />
<div id="class-rootresponse-attribute-name"></div>

### name

Human-readable name of API endpoint

__Required:__ True<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-rootresponse-attribute-privacyPolicy"></div>

### privacyPolicy

URL of human-readable Privacy Policy of API endpoint. This will be displayed to the user for consent when adding a subscription. The default URL points to a document edited by Type.World that you can use (at your own risk) instead of having to write your own.

The link will open with a `locales` parameter containing a comma-separated list of the user’s preferred UI languages and a `canonicalURL` parameter containing the subscription’s canonical URL and a `subscriptionID` parameter containing the anonymous subscription ID.

__Required:__ True<br />
__Type:__ Str<br />
__Default value:__ https://type.world/legal/default/PrivacyPolicy.html

<div id="class-rootresponse-attribute-public"></div>

### public

API endpoint is meant to be publicly visible and its existence may be publicized within the project

__Required:__ True<br />
__Type:__ Bool<br />
__Default value:__ False

<div id="class-rootresponse-attribute-supportedCommands"></div>

### supportedCommands

List of commands this API endpoint supports: ['installableFonts', 'installFont', 'uninstallFont', 'setAnonymousAppIDStatus']

__Required:__ True<br />
__Type:__ List of Str objects<br />
<div id="class-rootresponse-attribute-termsOfServiceAgreement"></div>

### termsOfServiceAgreement

URL of human-readable Terms of Service Agreement of API endpoint. This will be displayed to the user for consent when adding a subscription. The default URL points to a document edited by Type.World that you can use (at your own risk) instead of having to write your own.

The link will open with a `locales` parameter containing a comma-separated list of the user’s preferred UI languages and a `canonicalURL` parameter containing the subscription’s canonical URL and a `subscriptionID` parameter containing the anonymous subscription ID.

__Required:__ True<br />
__Type:__ Str<br />
__Default value:__ https://type.world/legal/default/TermsOfService.html

<div id="class-rootresponse-attribute-version"></div>

### version

Version of "installFont" response

__Required:__ True<br />
__Type:__ Str<br />
__Format:__ Simple float number (1 or 1.01) or semantic versioning (2.0.0-rc.1) as per [semver.org](https://semver.org)<br />
__Default value:__ 0.1.7-alpha

<div id="class-rootresponse-attribute-website"></div>

### website

URL of human-visitable website of API endpoint, for publication

__Required:__ False<br />
__Type:__ Str<br />


## Methods

<div id="class-rootresponse-method-customvalidation"></div>

#### customValidation()

Return three lists with informations, warnings, and errors.

An empty errors list is regarded as a successful validation, otherwise the validation is regarded as a failure.

<div id="class-rootresponse-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





<div id="class-multilanguagetext"></div>

# _class_ MultiLanguageText()

Multi-language text. Attributes are language keys as per [https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes]

The GUI app will then calculate the language data to be displayed using [MultiLanguageText.getText()](#user-content-class-multilanguagetext-method-gettext) with a prioritized list of languages that the user can understand. They may be pulled from the operating system’s language preferences.

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

Neither HTML nor Markdown code is permitted in `MultiLanguageText`.

### Methods

[getText()](#class-multilanguagetext-method-gettext)<br />[getTextAndLocale()](#class-multilanguagetext-method-gettextandlocale)<br />[sameContent()](#class-multilanguagetext-method-samecontent)<br />

## Methods

<div id="class-multilanguagetext-method-gettext"></div>

#### getText(locale = ['en'], format = plain)

Returns the text in the first language found from the specified list of languages. If that language can’t be found, we’ll try English as a standard. If that can’t be found either, return the first language you can find.

<div id="class-multilanguagetext-method-gettextandlocale"></div>

#### getTextAndLocale(locale = ['en'], format = plain)

Like getText(), but additionally returns the language of whatever text was found first.

<div id="class-multilanguagetext-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





<div id="class-installablefontsresponse"></div>

# _class_ InstallableFontsResponse()

This is the response expected to be returned when the API is invoked using the `?command=installableFonts` parameter.

```python
# Create root object
installableFonts = InstallableFontsResponse()

# Add data to the command here
# ...

# Return the call’s JSON content to the HTTP request
return installableFonts.dumpJSON()
```

### Attributes

[designers](#class-installablefontsresponse-attribute-designers)<br />[errorMessage](#class-installablefontsresponse-attribute-errormessage)<br />[foundries](#class-installablefontsresponse-attribute-foundries)<br />[name](#class-installablefontsresponse-attribute-name)<br />[prefersRevealedUserIdentity](#class-installablefontsresponse-attribute-prefersrevealeduseridentity)<br />[type](#class-installablefontsresponse-attribute-type)<br />[userEmail](#class-installablefontsresponse-attribute-useremail)<br />[userName](#class-installablefontsresponse-attribute-username)<br />[version](#class-installablefontsresponse-attribute-version)<br />

### Methods

[sameContent()](#class-installablefontsresponse-method-samecontent)<br />

## Attributes

<div id="class-installablefontsresponse-attribute-designers"></div>

### designers

List of [Designer](#user-content-class-designer) objects, referenced in the fonts or font families by the keyword. These are defined at the root of the response for space efficiency, as one designer can be involved in the design of several typefaces across several foundries.

__Required:__ False<br />
__Type:__ List of [Designer](#user-content-class-designer) objects<br />
<div id="class-installablefontsresponse-attribute-errorMessage"></div>

### errorMessage

Description of error in case of [InstallableFontsResponse.type](#user-content-class-installablefontsresponse-attribute-type) being "custom".

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

A name of this response and its contents. This is needed to manage subscriptions in the UI. For instance "Free Fonts" for all free and non-restricted fonts, or "Commercial Fonts" for all those fonts that the use has commercially licensed, so their access is restricted. In case of a free font website that offers individual subscriptions for each typeface, this decription could be the name of the typeface.

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-installablefontsresponse-attribute-prefersRevealedUserIdentity"></div>

### prefersRevealedUserIdentity

Indicates that the publisher prefers to have the user reveal his/her identity to the publisher when installing fonts. In the app, the user will be asked via a dialog to turn the setting on, but is not required to do so.

__Required:__ True<br />
__Type:__ Bool<br />
__Default value:__ False

<div id="class-installablefontsresponse-attribute-type"></div>

### type

Type of response. This can be any of ['success', 'error', 'noFontsAvailable', 'insufficientPermission', 'temporarilyUnavailable', 'validTypeWorldUserAccountRequired', 'accessTokenExpired']. In case of "error", you may specify an additional message to be presented to the user under [InstallableFontsResponse.errorMessage](#user-content-class-installablefontsresponse-attribute-errormessage).

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
<div id="class-installablefontsresponse-attribute-version"></div>

### version

Version of "installableFonts" response

__Required:__ True<br />
__Type:__ Str<br />
__Format:__ Simple float number (1 or 1.01) or semantic versioning (2.0.0-rc.1) as per [semver.org](https://semver.org)<br />
__Default value:__ 0.1.7-alpha



## Methods

<div id="class-installablefontsresponse-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





<div id="class-designer"></div>

# _class_ Designer()



### Attributes

[description](#class-designer-attribute-description)<br />[keyword](#class-designer-attribute-keyword)<br />[name](#class-designer-attribute-name)<br />[website](#class-designer-attribute-website)<br />

### Methods

[sameContent()](#class-designer-method-samecontent)<br />

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
<div id="class-designer-attribute-website"></div>

### website

Designer’s web site

__Required:__ False<br />
__Type:__ Str<br />


## Methods

<div id="class-designer-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





<div id="class-multilanguagelongtext"></div>

# _class_ MultiLanguageLongText()

Multi-language text. Attributes are language keys as per [https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes]

The GUI app will then calculate the language data to be displayed using [MultiLanguageText.getText()](#user-content-class-multilanguagetext-method-gettext) with a prioritized list of languages that the user can understand. They may be pulled from the operating system’s language preferences.

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

HTML code is not allowed in `MultiLanguageLongText`, but you may use [Markdown](https://en.wikipedia.org/wiki/Markdown) to add formatting and links.

### Methods

[getText()](#class-multilanguagelongtext-method-gettext)<br />[getTextAndLocale()](#class-multilanguagelongtext-method-gettextandlocale)<br />[sameContent()](#class-multilanguagelongtext-method-samecontent)<br />

## Methods

<div id="class-multilanguagelongtext-method-gettext"></div>

#### getText(locale = ['en'], format = plain)

Returns the text in the first language found from the specified list of languages. If that language can’t be found, we’ll try English as a standard. If that can’t be found either, return the first language you can find.

<div id="class-multilanguagelongtext-method-gettextandlocale"></div>

#### getTextAndLocale(locale = ['en'], format = plain)

Like getText(), but additionally returns the language of whatever text was found first.

<div id="class-multilanguagelongtext-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





<div id="class-foundry"></div>

# _class_ Foundry()



### Attributes

[backgroundColor](#class-foundry-attribute-backgroundcolor)<br />[description](#class-foundry-attribute-description)<br />[email](#class-foundry-attribute-email)<br />[facebook](#class-foundry-attribute-facebook)<br />[families](#class-foundry-attribute-families)<br />[instagram](#class-foundry-attribute-instagram)<br />[licenses](#class-foundry-attribute-licenses)<br />[logo](#class-foundry-attribute-logo)<br />[name](#class-foundry-attribute-name)<br />[skype](#class-foundry-attribute-skype)<br />[supportEmail](#class-foundry-attribute-supportemail)<br />[supportTelephone](#class-foundry-attribute-supporttelephone)<br />[supportWebsite](#class-foundry-attribute-supportwebsite)<br />[telephone](#class-foundry-attribute-telephone)<br />[twitter](#class-foundry-attribute-twitter)<br />[uniqueID](#class-foundry-attribute-uniqueid)<br />[website](#class-foundry-attribute-website)<br />

### Methods

[sameContent()](#class-foundry-method-samecontent)<br />

## Attributes

<div id="class-foundry-attribute-backgroundColor"></div>

### backgroundColor

Foundry’s preferred background color. This is meant to go as a background color to the logo at [Foundry.logo](#user-content-class-foundry-attribute-logo)

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ Hex RRGGBB (without leading #)<br />
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
<div id="class-foundry-attribute-facebook"></div>

### facebook

Facebook page URL handle for this foundry. The URL 

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-foundry-attribute-families"></div>

### families

List of [Family](#user-content-class-family) objects.

__Required:__ True<br />
__Type:__ List of [Family](#user-content-class-family) objects<br />
<div id="class-foundry-attribute-instagram"></div>

### instagram

Instagram handle for this foundry, without the @

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-foundry-attribute-licenses"></div>

### licenses

List of [LicenseDefinition](#user-content-class-licensedefinition) objects under which the fonts in this response are issued. For space efficiency, these licenses are defined at the foundry object and will be referenced in each font by their keyword. Keywords need to be unique for this foundry and may repeat across foundries.

__Required:__ True<br />
__Type:__ List of [LicenseDefinition](#user-content-class-licensedefinition) objects<br />
<div id="class-foundry-attribute-logo"></div>

### logo

URL of foundry’s logo. Specifications to follow.

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ This resource may get downloaded and cached on the client computer. To ensure up-to-date resources, append a unique ID to the URL such as a timestamp of the resources’s upload on your server, e.g. https://awesomefonts.com/xyz/regular/specimen.pdf?t=1548239062<br />
<div id="class-foundry-attribute-name"></div>

### name

Name of foundry

__Required:__ True<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-foundry-attribute-skype"></div>

### skype

Skype handle for this foundry

__Required:__ False<br />
__Type:__ Str<br />
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
<div id="class-foundry-attribute-supportWebsite"></div>

### supportWebsite

Support website for this foundry, such as a chat room, forum, online service desk.

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-foundry-attribute-telephone"></div>

### telephone

Telephone number for this foundry

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-foundry-attribute-twitter"></div>

### twitter

Twitter handle for this foundry, without the @

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-foundry-attribute-uniqueID"></div>

### uniqueID

An string that uniquely identifies this foundry within the publisher.

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-foundry-attribute-website"></div>

### website

Website for this foundry

__Required:__ False<br />
__Type:__ Str<br />


## Methods

<div id="class-foundry-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





<div id="class-licensedefinition"></div>

# _class_ LicenseDefinition()



### Attributes

[URL](#class-licensedefinition-attribute-url)<br />[keyword](#class-licensedefinition-attribute-keyword)<br />[name](#class-licensedefinition-attribute-name)<br />

### Methods

[sameContent()](#class-licensedefinition-method-samecontent)<br />

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


## Methods

<div id="class-licensedefinition-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





<div id="class-family"></div>

# _class_ Family()



### Attributes

[billboards](#class-family-attribute-billboards)<br />[dateFirstPublished](#class-family-attribute-datefirstpublished)<br />[description](#class-family-attribute-description)<br />[designers](#class-family-attribute-designers)<br />[fonts](#class-family-attribute-fonts)<br />[inUseURL](#class-family-attribute-inuseurl)<br />[issueTrackerURL](#class-family-attribute-issuetrackerurl)<br />[name](#class-family-attribute-name)<br />[pdf](#class-family-attribute-pdf)<br />[sourceURL](#class-family-attribute-sourceurl)<br />[uniqueID](#class-family-attribute-uniqueid)<br />[versions](#class-family-attribute-versions)<br />

### Methods

[getAllDesigners()](#class-family-method-getalldesigners)<br />[sameContent()](#class-family-method-samecontent)<br />

## Attributes

<div id="class-family-attribute-billboards"></div>

### billboards

List of URLs pointing at images to show for this typeface, specifications to follow

__Required:__ False<br />
__Type:__ List of Str objects<br />
<div id="class-family-attribute-dateFirstPublished"></div>

### dateFirstPublished

Date of the initial release of the family. May be overriden on font level at [Font.dateFirstPublished](#user-content-class-font-attribute-datefirstpublished).

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ YYYY-MM-DD<br />
<div id="class-family-attribute-description"></div>

### description

Description of font family

__Required:__ False<br />
__Type:__ [MultiLanguageLongText](#user-content-class-multilanguagelongtext)<br />
__Format:__ Maximum allowed characters: 3000. Mardown code is permitted for text formatting.<br />
<div id="class-family-attribute-designers"></div>

### designers

List of keywords referencing designers. These are defined at [InstallableFontsResponse.designers](#user-content-class-installablefontsresponse-attribute-designers). In case designers differ between fonts within the same family, they can also be defined at the font level at [Font.designers](#user-content-class-font-attribute-designers). The font-level references take precedence over the family-level references.

__Required:__ False<br />
__Type:__ List of Str objects<br />
<div id="class-family-attribute-fonts"></div>

### fonts

List of [Font](#user-content-class-font) objects. The order will be displayed unchanged in the UI, so it’s in your responsibility to order them correctly.

__Required:__ True<br />
__Type:__ List of [Font](#user-content-class-font) objects<br />
<div id="class-family-attribute-inUseURL"></div>

### inUseURL

URL pointing to a web site that shows real world examples of the fonts in use.

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
<div id="class-family-attribute-pdf"></div>

### pdf

URL of PDF file with type specimen and/or instructions for entire family. May be overriden on font level at [Font.pdf](#user-content-class-font-attribute-pdf).

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ This resource may get downloaded and cached on the client computer. To ensure up-to-date resources, append a unique ID to the URL such as a timestamp of the resources’s upload on your server, e.g. https://awesomefonts.com/xyz/regular/specimen.pdf?t=1548239062<br />
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

Returns a list of [Designer](#user-content-class-designer) objects that represent all of the designers referenced both at the family level as well as with all the family’s fonts, in case the fonts carry specific designers. This could be used to give a one-glance overview of all designers involved.
                

<div id="class-family-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





<div id="class-version"></div>

# _class_ Version()



### Attributes

[description](#class-version-attribute-description)<br />[number](#class-version-attribute-number)<br />[releaseDate](#class-version-attribute-releasedate)<br />

### Methods

[isFontSpecific()](#class-version-method-isfontspecific)<br />[sameContent()](#class-version-method-samecontent)<br />

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

Returns True if this version is defined at the font level. Returns False if this version is defined at the family level.
                

<div id="class-version-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





<div id="class-font"></div>

# _class_ Font()



### Attributes

[dateFirstPublished](#class-font-attribute-datefirstpublished)<br />[designers](#class-font-attribute-designers)<br />[format](#class-font-attribute-format)<br />[free](#class-font-attribute-free)<br />[name](#class-font-attribute-name)<br />[pdf](#class-font-attribute-pdf)<br />[postScriptName](#class-font-attribute-postscriptname)<br />[protected](#class-font-attribute-protected)<br />[purpose](#class-font-attribute-purpose)<br />[setName](#class-font-attribute-setname)<br />[status](#class-font-attribute-status)<br />[uniqueID](#class-font-attribute-uniqueid)<br />[usedLicenses](#class-font-attribute-usedlicenses)<br />[variableFont](#class-font-attribute-variablefont)<br />[versions](#class-font-attribute-versions)<br />

### Methods

[filename()](#class-font-method-filename)<br />[getDesigners()](#class-font-method-getdesigners)<br />[getVersions()](#class-font-method-getversions)<br />[sameContent()](#class-font-method-samecontent)<br />

## Attributes

<div id="class-font-attribute-dateFirstPublished"></div>

### dateFirstPublished

Date of the initial release of the font. May also be defined family-wide at [Family.dateFirstPublished](#user-content-class-family-attribute-datefirstpublished).

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ YYYY-MM-DD<br />
<div id="class-font-attribute-designers"></div>

### designers

List of keywords referencing designers. These are defined at [InstallableFontsResponse.designers](#user-content-class-installablefontsresponse-attribute-designers). This attribute overrides the designer definitions at the family level at [Family.designers](#user-content-class-family-attribute-designers).

__Required:__ False<br />
__Type:__ List of Str objects<br />
<div id="class-font-attribute-format"></div>

### format

Font file format. Required value in case of `desktop` font (see [Font.purpose](#user-content-class-font-attribute-purpose). Possible: ['woff2', 'ttc', 'woff', 'ttf', 'otf']

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-font-attribute-free"></div>

### free

Font is freeware. For UI signaling

__Required:__ False<br />
__Type:__ Bool<br />
<div id="class-font-attribute-name"></div>

### name

Human-readable name of font. This may include any additions that you find useful to communicate to your users.

__Required:__ True<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-font-attribute-pdf"></div>

### pdf

URL of PDF file with type specimen and/or instructions for this particular font. (See also: [Family.pdf](#user-content-class-family-attribute-pdf)

__Required:__ False<br />
__Type:__ Str<br />
__Format:__ This resource may get downloaded and cached on the client computer. To ensure up-to-date resources, append a unique ID to the URL such as a timestamp of the resources’s upload on your server, e.g. https://awesomefonts.com/xyz/regular/specimen.pdf?t=1548239062<br />
<div id="class-font-attribute-postScriptName"></div>

### postScriptName

Complete PostScript name of font

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-font-attribute-protected"></div>

### protected

Indication that the server requires a valid subscriptionID to be used for authentication. The server *may* limit the downloads of fonts. This may also be used for fonts that are free to download, but their installations want to be tracked/limited anyway. Most importantly, this indicates that the uninstall command needs to be called on the API endpoint when the font gets uninstalled.

__Required:__ False<br />
__Type:__ Bool<br />
__Default value:__ False

<div id="class-font-attribute-purpose"></div>

### purpose

Technical purpose of font. This influences how the app handles the font. For instance, it will only install desktop fonts on the system, and make other font types available though folders. Possible: ['desktop', 'web', 'app']

__Required:__ True<br />
__Type:__ Str<br />
<div id="class-font-attribute-setName"></div>

### setName

Optional set name of font. This is used to group fonts in the UI. Think of fonts here that are of identical technical formats but serve different purposes, such as "Office Fonts" vs. "Desktop Fonts".

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-font-attribute-status"></div>

### status

Font status. For UI signaling. Possible values are: ['prerelease', 'trial', 'stable']

__Required:__ True<br />
__Type:__ Str<br />
__Default value:__ stable

<div id="class-font-attribute-uniqueID"></div>

### uniqueID

A machine-readable string that uniquely identifies this font within the publisher. It will be used to ask for un/installation of the font from the server in the `installFont` and `uninstallFont` commands. Also, it will be used for the file name of the font on disk, together with the version string and the file extension. Together, they must not be longer than 255 characters and must not contain the following characters: / ? < > \ : * | ^

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

It is composed of the font’s uniqueID, its version string and the file extension. Together, they must not exceed 255 characters.

<div id="class-font-method-getdesigners"></div>

#### getDesigners()

Returns a list of [Designer](#user-content-class-designer) objects that this font references. These are the combination of family-level designers and font-level designers. The same logic as for versioning applies. Please read the section about [versioning](#versioning) above.
                

<div id="class-font-method-getversions"></div>

#### getVersions()

Returns list of [Version](#user-content-class-version) objects.

This is the final list based on the version information in this font object as well as in its parent [Family](#user-content-class-family) object. Please read the section about [versioning](#versioning) above.

<div id="class-font-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





<div id="class-licenseusage"></div>

# _class_ LicenseUsage()



### Attributes

[allowanceDescription](#class-licenseusage-attribute-allowancedescription)<br />[dateAddedForUser](#class-licenseusage-attribute-dateaddedforuser)<br />[keyword](#class-licenseusage-attribute-keyword)<br />[seatsAllowed](#class-licenseusage-attribute-seatsallowed)<br />[seatsInstalled](#class-licenseusage-attribute-seatsinstalled)<br />[upgradeURL](#class-licenseusage-attribute-upgradeurl)<br />

### Methods

[getLicense()](#class-licenseusage-method-getlicense)<br />[sameContent()](#class-licenseusage-method-samecontent)<br />

## Attributes

<div id="class-licenseusage-attribute-allowanceDescription"></div>

### allowanceDescription

In case of non-desktop font (see [Font.purpose](#user-content-class-font-attribute-purpose)), custom string for web fonts or app fonts reminding the user of the license’s limits, e.g. "100.000 page views/month"

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
<div id="class-licenseusage-attribute-seatsInstalled"></div>

### seatsInstalled

In case of desktop font (see [Font.purpose](#user-content-class-font-attribute-purpose)), number of installations recorded by the API endpoint. This value will need to be supplied dynamically by the API endpoint through tracking all font installations through the "anonymousAppID" parameter of the "installFont" and "uninstallFont" command. Please note that the Type.World client app is currently not designed to reject installations of the fonts when the limits are exceeded. Instead it is in the responsibility of the API endpoint to reject font installations though the "installFont" command when the limits are exceeded. In that case the user will be presented with one or more license upgrade links.

__Required:__ False<br />
__Type:__ Int<br />
<div id="class-licenseusage-attribute-upgradeURL"></div>

### upgradeURL

URL the user can be sent to to upgrade the license of the font, for instance at the foundry’s online shop. If possible, this link should be user-specific and guide him/her as far into the upgrade process as possible.

__Required:__ False<br />
__Type:__ Str<br />


## Methods

<div id="class-licenseusage-method-getlicense"></div>

#### getLicense()

Returns the [License](#user-content-class-license) object that this font references.
                

<div id="class-licenseusage-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





<div id="class-installfontresponse"></div>

# _class_ InstallFontResponse()

This is the response expected to be returned when the API is invoked using the `?command=installFonts` parameter.

```python
# Create root object
installFonts = InstallFontResponse()

# Add data to the command here
# ...

# Return the call’s JSON content to the HTTP request
return installFonts.dumpJSON()
```

### Attributes

[encoding](#class-installfontresponse-attribute-encoding)<br />[errorMessage](#class-installfontresponse-attribute-errormessage)<br />[fileName](#class-installfontresponse-attribute-filename)<br />[font](#class-installfontresponse-attribute-font)<br />[type](#class-installfontresponse-attribute-type)<br />[version](#class-installfontresponse-attribute-version)<br />

### Methods

[sameContent()](#class-installfontresponse-method-samecontent)<br />

## Attributes

<div id="class-installfontresponse-attribute-encoding"></div>

### encoding

Encoding type for binary font data. Currently supported: ['base64']

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-installfontresponse-attribute-errorMessage"></div>

### errorMessage

Description of error in case of custom response type

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-installfontresponse-attribute-fileName"></div>

### fileName

Suggested file name of font. This may be ignored by the app in favour of a unique file name.

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-installfontresponse-attribute-font"></div>

### font

Binary font data encoded to a string using [InstallFontResponse.encoding](#user-content-class-installfontresponse-attribute-encoding)

__Required:__ False<br />
__Type:__ Str<br />
<div id="class-installfontresponse-attribute-type"></div>

### type

Type of response. This can be any of ['success', 'error', 'unknownFont', 'insufficientPermission', 'temporarilyUnavailable', 'duplicateInstallation', 'seatAllowanceReached', 'validTypeWorldUserAccountRequired', 'revealedUserIdentityRequired']. In case of "error", you may specify an additional message to be presented to the user under [InstallFontResponse.errorMessage](#user-content-class-installfontresponse-attribute-errormessage).

__Required:__ True<br />
__Type:__ Str<br />
__Format:__ To ensure the proper function of the entire Type.World protocol, your API endpoint *must* return the proper responses as per [this flow chart](https://type.world/documentation/Type.World%20Request%20Flow%20Chart.pdf). In addition to ensure functionality, this enables the response messages displayed to the user to be translated into all the possible languages on our side.<br />
<div id="class-installfontresponse-attribute-version"></div>

### version

Version of "installFont" response

__Required:__ True<br />
__Type:__ Str<br />
__Format:__ Simple float number (1 or 1.01) or semantic versioning (2.0.0-rc.1) as per [semver.org](https://semver.org)<br />
__Default value:__ 0.1.7-alpha



## Methods

<div id="class-installfontresponse-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





<div id="class-uninstallfontresponse"></div>

# _class_ UninstallFontResponse()

This is the response expected to be returned when the API is invoked using the `?command=uninstallFonts` parameter.

```python
# Create root object
uninstallFonts = UninstallFontResponse()

# Add data to the command here
# ...

# Return the call’s JSON content to the HTTP request
return uninstallFonts.dumpJSON()
```

### Attributes

[errorMessage](#class-uninstallfontresponse-attribute-errormessage)<br />[type](#class-uninstallfontresponse-attribute-type)<br />[version](#class-uninstallfontresponse-attribute-version)<br />

### Methods

[sameContent()](#class-uninstallfontresponse-method-samecontent)<br />

## Attributes

<div id="class-uninstallfontresponse-attribute-errorMessage"></div>

### errorMessage

Description of error in case of custom response type

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-uninstallfontresponse-attribute-type"></div>

### type

Type of response. This can be any of ['success', 'error', 'unknownFont', 'unknownInstallation', 'insufficientPermission', 'temporarilyUnavailable', 'validTypeWorldUserAccountRequired']. In case of "error", you may specify an additional message to be presented to the user under [UninstallFontResponse.errorMessage](#user-content-class-uninstallfontresponse-attribute-errormessage).

__Required:__ True<br />
__Type:__ Str<br />
__Format:__ To ensure the proper function of the entire Type.World protocol, your API endpoint *must* return the proper responses as per [this flow chart](https://type.world/documentation/Type.World%20Request%20Flow%20Chart.pdf). In addition to ensure functionality, this enables the response messages displayed to the user to be translated into all the possible languages on our side.<br />
<div id="class-uninstallfontresponse-attribute-version"></div>

### version

Version of "uninstallFont" response

__Required:__ True<br />
__Type:__ Str<br />
__Format:__ Simple float number (1 or 1.01) or semantic versioning (2.0.0-rc.1) as per [semver.org](https://semver.org)<br />
__Default value:__ 0.1.7-alpha



## Methods

<div id="class-uninstallfontresponse-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





<div id="class-setanonymousappidstatusresponse"></div>

# _class_ SetAnonymousAppIDStatusResponse()



### Attributes

[errorMessage](#class-setanonymousappidstatusresponse-attribute-errormessage)<br />[type](#class-setanonymousappidstatusresponse-attribute-type)<br />[version](#class-setanonymousappidstatusresponse-attribute-version)<br />

### Methods

[sameContent()](#class-setanonymousappidstatusresponse-method-samecontent)<br />

## Attributes

<div id="class-setanonymousappidstatusresponse-attribute-errorMessage"></div>

### errorMessage

Description of error in case of custom response type

__Required:__ False<br />
__Type:__ [MultiLanguageText](#user-content-class-multilanguagetext)<br />
__Format:__ Maximum allowed characters: 100.<br />
<div id="class-setanonymousappidstatusresponse-attribute-type"></div>

### type

Type of response. This can be any of ['success', 'error', 'insufficientPermission', 'temporarilyUnavailable']. In case of "error", you may specify an additional message to be presented to the user under [InstallFontResponse.errorMessage](#user-content-class-installfontresponse-attribute-errormessage).

__Required:__ True<br />
__Type:__ Str<br />
__Format:__ To ensure the proper function of the entire Type.World protocol, your API endpoint *must* return the proper responses as per [this flow chart](https://type.world/documentation/Type.World%20Request%20Flow%20Chart.pdf). In addition to ensure functionality, this enables the response messages displayed to the user to be translated into all the possible languages on our side.<br />
<div id="class-setanonymousappidstatusresponse-attribute-version"></div>

### version

Version of "setAnonymousAppIDStatus" response

__Required:__ True<br />
__Type:__ Str<br />
__Format:__ Simple float number (1 or 1.01) or semantic versioning (2.0.0-rc.1) as per [semver.org](https://semver.org)<br />
__Default value:__ 0.1.7-alpha



## Methods

<div id="class-setanonymousappidstatusresponse-method-samecontent"></div>

#### sameContent()

Compares the data structure of this object to the other object.

Requires deepdiff module.





