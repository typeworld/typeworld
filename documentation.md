# Preamble

### Document Date

Document last revised: %timestamp%

### Development Time Line

Currently, we’re looking into the following timeline:

* Spring/Early Summer 2020: Reaching **Beta** status, afterwards only casual development until September 2020, very limited support (because summer, only God can judge me)
* September 2020: Return to full time development, full support
* March 2021: Release of final **Version 1.0**

### Development Status

As of this writing, the Type.World Project is still in *Alpha* phase, but rapidly approaching *Beta* status.

[![Build Status](https://travis-ci.org/typeWorld/typeWorld.svg?branch=master)](https://travis-ci.org/typeWorld/typeWorld)
[![codecov](https://codecov.io/gh/typeWorld/typeWorld/branch/master/graph/badge.svg)](https://codecov.io/gh/typeWorld/typeWorld)
[![PyPI version](https://badge.fury.io/py/typeworld.svg)](https://badge.fury.io/py/typeworld)

The **Beta** status applies mostly to the Type.World JSON Protocol and the [headless client module](https://github.com/typeworld/typeworld) which is used by the GUI App, as well as central server, including documentation. This is what developers of API endpoints need in order to implement the system on their servers.

The GUI App has a rather limited feature set at the moment, just enough to demo the system properly. It is expected to develop significantly between September 2020 and March 2021.

### Problems with the Documentation

If you have any problems in understanding the system that probably means that it hasn’t been explained well enough yet. In this case, please drop me a line at [hello@type.world](mailto:hello@type.world) and explain your limitations. I will try to improve the documentation.


# Quick Start

To start developing your own API Endpoint for the Type.World App, you need to:

* Understand the project’s development timeline (see *Development Time Line* hereabove under *Preamble*
* Download the app at [type.world/app](https://type.world/app)
* After you’ve installed the app, access a demo subscription by clicking on this link: [`typeworld://json+https//typeworldserver.com/flatapi/bZA2JbWHEAkFjako0Mtz/`](typeworld://json+https//typeworldserver.com/flatapi/bZA2JbWHEAkFjako0Mtz/)
* Read the *Type.World JSON Protocol* documentation over on [github.com/typeworld/typeworld](https://github.com/typeworld/typeworld/tree/master/Lib/typeworld/api)
* Read the sample Flask server implementation over on [github.com/typeworld/sampleFlaskServer](https://github.com/typeworld/sampleFlaskServer)
* Read and understand this very document here

## Check List

In order to go online with your API Endpoint, consider the following check list:

* I’ve obtained an `APIKey` for my API Endpoint through the user account section at [type.world/account](https://type.world/account)
* I’ve made sure that calls to the central type.world server are looping for a certain number of times in case a server instance disappears mid-request (see [Type.World API](#typeworld-api))
* I’ve checked my API Endpoint with the API Endpoint Validator (see [API Endpoint Validator](#api-endpoint-validator))
* I made sure the fonts in my subscription all have unique and unchanging `uniqueID` attributes




# Introduction

The Type.World technology aims to improve the user experience around font installations for end users, in turn improving the participating publishers’ market position. It defines a protocol that font publishers may implement on their web servers, serving data about which of their users are entitled to download and install certain fonts.

The Type.World App needs to be installed by a user once, and is then pointed at these publisher API endpoints (Application Programming Interface) through a link on the publisher’s website as an alternative download means next to the established way of providing the available fonts to download in zip archives.
Over time, end users will accumulate font subscriptions from different publishers all in one app. The visual appearance of each publisher and foundry is customizable (color scheme and logos), so that a certain level of foundry corporate design adherence is ensured.

Initially, only metadata about which fonts are available to a user is received by the app, and not the fonts themselves, which means that they cannot be readily displayed in the app, only the meta data about their existence. Instead, publishers can define preview poster images that the users can check out next to PDF links describing and previewing the fonts in detail.

Upon the user’s request, the app will download and install the fonts which will be immediately accessible in all apps in the operating system. The installed fonts will remain installed when the app isn’t open or the computer is offline, although a select few features will require the app to keep running. Only new font installations or deletions of so called *protected fonts* require an internet connection.

Users will be notified of available font updates. And they can synchronize their subscriptions to other computers or invite other users to share a subscription.

Because the Type.World technology is also meant as an excercize in self empowerment for type publishers, the creation of all data that a subscription holds, both metadata about the fonts as well as font data itself, lies in the responsibility and hosting of the publisher. For example, it lies in the publisher’s responsibility to record and properly display how many seats a user has installed for a certain font license, and update the number after a font has been installed or deleted. The app will in this case only display that number to the user and not make any own calculations. Similarly, it is in the server’s responsibility to reject font installation requests once the license’s seats have been used up. Which also means that publishers may choose to allow a certain number of excess seats over the license’s limit without explicitly informing their users about it. The app will not observe any of that, only display the publisher server’s response to the user.

It needs to be understood that Type.World doesn’t offer a 100% ready turn-key solution. It defines the protocol and provides the end user app.

The fonts and subscriptions are decentrally hosted by each publisher for their users. The central Type.World server will handle the knowledge of subscriptions per Type.World user account for the purpose of backup, synchronization, and invitations.

The technology is aimed at the following three font publishing schemes:

* Free Fonts
* Commercial Fonts
* Custom Fonts

**Free Font** providers can offer all of their fonts to be installable in the Type.World App.

**Commercial font foundries**, probably the most important scenario for this technology, will find three ways to serve fonts: 

* All knowledge about which user is entitled to download which fonts is already present in the foundry’s databases. Instead of displaying that data in HTML form and serving it to a browser, the same data is refactored into the Type.World JSON protocol and served to the Type.World App for display. And instead of the fonts being available in zip files to download, the foundry’s API endpoint will serve them under the JSON Protocol upon the app’s request.
* Foundries may serve their entire library on a time based subscription and the Type.World technology will serve as an easy to use distribution channel.
* Foundries may serve trial versions of their fonts to potential customers. The Type.World Protocol includes the option to set expiration times for installed fonts, and the app will ensure the font’s deletion upon expiry. Whether foundries decide to offer trial fonts in a separate subscription open to the public, or offer trial fonts only on request inside customer’s existing font subscriptions with them, is each foundry’s own decision.

**Custom font projects** will be able to serve fonts to small workgroups, normally graphic designers within a branding firm. Font updates can be made available to the graphic designers fast and reliably, and the adoption level of font updates can be monitored on the server side.
These fonts could be hosted either on API endpoints implemented by the type foundry themselves, or on third party services that support the protocol. The custom font scenario is the only one where it makes sense to hire an external service as a turn-key solution for hosting and serving the fonts because establishing which users get to install which fonts is a fast and straightforward process to set up manually on a web interface for custom jobs, whereas serving commercial fonts to anonymous customers requires the data knowledge of an online shop.

## Benefits

In summary, the technology provides the following benefits over established font download conduct:

### Benefits For Users

* One-click font installation triggered directly from inside the browser, given that the end user has installed the Type.World App once
* Organizing font subscriptions from different publishers in a central Type.World user account. This user account can be automatically synchronized to another computer’s Type.World App that’s connected to the same user account (like a work station computer and a laptop for traveling). For the time being, only the subscriptions are synchronized, and not the installation status of each font. Because seat allowances for commercial font subscriptions are expected to be limited, automatically activating fonts on a second synchronized computer is problematic and not currently planned. Instead, users can organize fonts into collections and activate/deactivate them on separate computers as needed.
* Restoring font subscriptions after a computer has crashed or got lost is as easy as logging back into the Type.World user account in the app. The whole process of archiving and backing up purchased fonts disappears and the time needed to restore a complete work environment after an operating system reinstallation is reduced dramatically in regards to the fonts. In that sense, in terms of user experience, the Type.World technology mimicks the behaviours of modern day app stores where all previously purchased apps are readily available for installation on a new machine with one click, except that the Type.World technology doesn’t get itself involved in the selling part like an app store does.
* Users may invite other users to share font subscriptions from within the app
* Installation of font updates is as easy as following the notification via the operating system to trigger the font update. However, fonts will never be installed fully automatically, although this might be an option for the future, because in a professional workflow the designers need to be fully aware of the possibility that the fonts’ metrics may have changed which might mess with their documents. Therefore, font updates will come only as notifications and need to be explicitly triggered by the user.

### Benefits For Publishers

* Anonymous tracking of how many fonts are installed per subscription, giving commercial foundries the ability to observe the adherence of their customers to their font licenses. As desktop fonts are normally licensed limited to a certain number of seats (computers), API endpoints can record font installations anonymously and reject future installation requests once seat allowance is reached. Furthermore, foundries can include a license upgrade link with each font which will be displayed to the end users, making it simple as never before for customers to purchase license upgrades when the limits are reached. As end users grow accustomed to the technology and its benefits, their readiness to purchase upgrades will also grow, as a similarly easy user experience isn’t available with the old way of downloading and organizing fonts from zip archives. This easy license upgrade constitutes real added financial value to foundries on top of binding customers through the general user experience upgrade already.
* For custom font projects, the technology allows the type shop to push font updates onto the workgroup graphic designers fast and reliably and monitor the font version adoption level, unlike previously, where font updates were sent by email and their adoption level was in the hands of god.
Optionally, publishers may request the transmission of end users identities (name and email address) for closed workgroups upon font installation, establishing a direct communication link between publisher and end user for critical communication, for example to remind them of the old font versions they’re using.
* Happier returning customers through user the experience upgrade
* Participation in a new foundry ecosystem that happy Type.World users may want to stay in once they have gotten used to the user experience upgrade. The Type.World app and website will contain a discovery section of all those foundries that are participating in the technology.

## Terminology

* **Publisher** describes a publisher of fonts under a Type.World JSON API Endpoint. This can be a free font publisher serving free fonts, an independent type publisher serving their own designs, a custom type shop, or a font retailer selling and serving fonts of several different foundries to a customer. Regardless the font’s origins, as long as they serve them to the Type.World App, we call them *Publisher*.
* **Subscription** describes a collection of fonts served by a *Publisher* designated for use by a Type.World user. Like a newspaper subscription which is served by one publisher and designated for one customer, so are our font subscriptions. A Type.World user may accumulate and access one or several subscriptions by one or several publishers in their app.
* **API Endpoint** describes an endpoint on a publisher’s web server that exists particularly to serve fonts to the Type.World App. This endpoint can coexist with a publisher’s normal web site on the same server, but under a different URL, like `https://awesomefonts.com` for the public web site and `https://awesomefonts.com/typeworldapi/` for the API Endpoint.
* **Third party service** describes a turn-key solution for hosting fonts to be served under the Type.World JSON Protocol, the *first party* being Type.World itself, *second party* being you implementing your own *API Endpoint*, and *third party* being an external service implemented by someone other than Type.World or yourself that you can use to serve fonts. I’m referring mostly to services here that implement serving *custom fonts* because serving *retail fonts* requires the knowledge of which customer bought which fonts, and only online shops have that knowledge. Unless, of course, such a third party also operates an online shop, like [Fontdue](https://www.fontdue.com/) does.


# Serving Fonts

In order to serve fonts to a user of the Type.World App, the publisher needs to serve these fonts under a certain machine readable data protocol. While the app can theoretically read several different such protocols, currently only the *Type.World JSON Protocol* is implemented.

A subscription URL is served to a user, normally by clicking on a button on the publisher’s web site, and the Type.World App reads the necessary data from the API Endpoint.

Alternatively, a user can be invited to a subscription by another user via the app.

## Type.World JSON Protocol

The *Type.World JSON Protocol* is hosted and documented on [its Github page](https://github.com/typeworld/typeworld/tree/master/Lib/typeworld/api).



## Dynamic vs. Static Serving

Like normal web sites, fonts can be served to a user either *dynamically* or *statically*. 

**Dynamic** serving usually means to custom-tailor the generated data for a certain user. In case of commercial type foundries, the API Endpoint would only serve the fonts that a customer has actually purchased from the foundry, and not the entire rest of their catalogue. In many ways, the dynamically served data would mimic the user account or download section of that foundry’s web site where a customer has access to the fonts they have purchased.

In a first step, only the *metadata* about a user’s fonts would be requested by the app and served by the API endpoint, and later, upon the user’s request, the API Endpoint would serve the *actual* binary font files. Because commercial fonts need to be protected, they are not openly accessible on the publisher’s web server and instead only served upon request and after authentication.

Serving dynamic content requires a software to run on the publisher’s server and create the dynamic data on request. The programming language of that software is up to the publisher to decide. Any language can be used. Relevant to the exchange of data is the data protocol described here, the *Type.World JSON Protocol*.

**Static** serving could be an option for hosting free fonts without custom-tailoring the data to users. In this case, a dynamic server-side API Endpoint is not necessary to exist. A subscription can be served all in a single JSON file, with links to openly acessible binary font files present in the JSON data.

Here’s an example for a *flat* or *static* subscription:

This is the link that would be served to the app: [`typeworld://json+https//typeworldserver.com/flatapi/bZA2JbWHEAkFjako0Mtz/`](typeworld://json+https//typeworldserver.com/flatapi/bZA2JbWHEAkFjako0Mtz/) (You can click on this link if you have the app installed)

To directly view the same subscription as raw JSON code in the browser, click here: [`https://typeworldserver.com/flatapi/bZA2JbWHEAkFjako0Mtz/`](https://typeworldserver.com/flatapi/bZA2JbWHEAkFjako0Mtz/)




## The Subscription URL

By clicking the *Install in Type.World App* button on your SSL-encrypted website, a URL of the following scheme gets handed off to the locally installed app through the custom protocol handler `typeworld://` that the app has registered with the operating system.

`typeworld://json+http[s]//[subscriptionID[:secretKey[:accessToken]]@]awesomefonts.com/api/`

The URL parts in detail:

* `typeworld://` This is the protocol handler used by the Type.World app. The app advertises the handler to the operating system, and upon clicking such a link, the operating system calls the app and hands over the link.
* `json` The protocol to be used within the Type.World app. Currently, only the Type.World JSON Protocol is available to use.
* `https//` The transport protocol to be used, in this case SSL-encrypted HTTPS. *Note:* because valid URLs are only allowed to contain one `://` sequence which is already in use to denote the custom protocol handler `typeworld://`, the colon `:` will be stripped off of the URL in a browser, even if you define it. The Type.World app will internally convert `https//` back to `https://`.
* `subscriptionID` uniquely identifies a subscription. In case of per-user subscriptions, you would probably use it to identify a user and then decide which fonts to serve them. The `subscriptionID` should be an anonymous string and is optional for publicly accessible subscriptions (such as free fonts). Allowed characters: **[a-z][A-Z][0-9]_-**
* `secretKey` matches with the `subscriptionID` and is used to authenticate the request. This secret key is saved in the OS’s keychain. The `secretKey ` is optional for publicly accessible subscriptions (such as free fonts). The secret key is actually not necessary to authenticate the request against the server (because the `subscriptionID` is supposed to be anonymous). Instead it’s necessary to store a secret key in the user’s OS keychain so that complete URLs are not openly visible. Allowed characters: **[a-z][A-Z][0-9]_-**
* `accessToken` Single use access token. Allowed characters: **[a-z][A-Z][0-9]_-**
* `awesomefonts.com/api/` is where your API endpoint sits and waits to serve fonts to your customers.

There are several possible ways to combine access credentials, as follows:

### Format A

A publicly accessible subscription without any access restrictions. This API endpoint has exactly one subscription to serve: `typeworld://json+https//awesomefonts.com/api/`

### Format B

A publicly accessible subscription without `secretKey`, but `subscriptionID` still used to identify a particular subscription in this API endpoint: `typeworld://json+https//subscriptionID@awesomefonts.com/api/`

### Format C

Example for a protected subscription:
`typeworld://json+https//subscriptionID:secretKey@awesomefonts.com/api/`

### Format CE

Example for a protected subscription with access token:
`typeworld://json+https//subscriptionID:secretKey:accessToken@awesomefonts.com/api/`


## Serving JSON Responses

### `POST` Requests

To avoid the subscription URL complete with the `subscriptionID` and `secretKey` showing up in server logs, your server should serve your protected JSON data only when replying to `POST` requests, as request parameters will be transmitted in the HTTP headers and will be invisible to server logs.

The app will ask for the JSON responses at your API endpoint (`https://awesomefonts.com/api/` in the above URL examples) and will hand over some or all of the following parameters through the HTTP headers’ POST fields:

* **`commands`** The commands to reply to, such as `installableFonts`. It could also be a comma-separated list of commands requested to be served in one go to speed up HTTP traffic. The combination `endpoint,installableFonts` will be requested by the app on initial access of a subscription, asking for metadata about the API Endpoint as well as the fonts offered by this subscription. This combination `installFonts,installableFonts` and `uninstallFonts,installableFonts` will be requested by the app when installing or uninstalling protected fonts. As the seat allowance is expected to change for installing/uninstalling protected fonts, the subscription needs to be updated directly after installing/uninstalling a font for updated display to the user. All requested commands will be nested inside a root command. It is mandatory to execute the commands on the server side in the order they were requested in: First the fonts are served or marked as deleted (`installFonts` or `uninstallFonts`), then the updated subscription is generated (`installableFonts`).
* **`subscriptionID`** The aforementioned ID to uniquely identify the fonts you serve.
* **`secretKey`** The secret key to authenticate the requester.
* **`accessToken`** The single use access token that you may use to identify whether a user was logged in to your website when first accessing a subscription. The access token is only ever served there in your website’s user account, and thrown away and replaced upon first access using this token. Afterwards users need to be verified with the central Type.World server. See *"Security Design, Level 2"* for details.
* **`anonymousAppID`** is a key that uniquely and anonymously identifies a Type.World app installation. You should use this to track how often a font has been installed by a user through different app instances and reject requests once the limit has been reached.
* **`fonts`** identifying the unique font ID and version number to install or uninstall as a comma separated list of slash-separated `fontID/version` tuples, such as `font1ID/font1version,font2ID/font2version,font3ID/font3version`.
* **`userEmail`** and **`userName`** in case the user has a Type.World user account and has explicitly agreed to reveal his/her identity on a per-subscription basis. This only makes sense in a trusted custom type development environment where the type designers may want to get in touch personally with the font’s users in a small work group, for instance in a branding agency. This tremendously streamlines everyone’s workflow. If necessary, a publisher in a trusted custom type development environment could reject the serving of subscriptions to requesters who are unidentified, e.g. requests with empty `userEmail` and `userName` parameters. There is currently no way to verify the correctness of the incoming two values for data privacy reasons. They need to be taken as is.

### `GET` Requests

For simplicity’s sake, you should reject incoming `GET` requests altogether to force the requester into using `POST` requests. This is for your own protection, as `GET` requests complete with the `subscriptionID` and `secretKey` might show up in server logs and therefore pose an attack vector to your protected fonts and meta data.

I suggest to return a `405 Method Not Allowed` HTTP response for all `GET` requests for serving subscription dynamically. It’s okay to serve subscriptions for `GET` requests for static subscriptions of free fonts.

### Warning of SQL Injection

Whatever you do with your server, bear in mind that the parameters attached to the requests could be malformed to contain [SQL injection attacks](https://www.w3schools.com/sql/sql_injection.asp) and the likes and need to be quarantined.




# Security Design


For protected subscriptions, the publisher provides a subscription link that contains a secret key to authenticate a subscription (*Format C*). An additional single-use access token may be added to the URL (*Format CE*) for initial access.

`typeworld://json+https//subscriptionID:secretKey:accessToken@awesomefonts.com/api/`

The security design outlined below consists of an unprotected base level and two optional security levels. The optional security level’s intention isn’t securing the leaking of fonts alone, but also very dominantly a user experience issue in the long run (See *"Remote De-Authorization of App Instances by the User"*).

## Subscription Access

Subscription URLs for protected fonts must not be passed to users by email or other unencrypted means. Because they may contain the secret key for protected subscriptions, the links could be intercepted and the fonts leaked.

Instead, two ways are designated to grant a user access to a subscription:

* **Button on publisher’s website**: The user can access the subscription on the publisher’s website in their personal account section, available only after login. This way, the subscription URL is passed from the browser directly to the app with no transmission other than (ideally) encrypted HTTPS traffic. The subscription URL with its secret key is as secure as the publisher’s website login.
* **Invitation API**: The central Type.World server provides an API ([`inviteUserToSubscription ` command](https://type.world/developer/api#inviteUserToSubscription)) to invite users to a subscription, identified by their Type.World user account email address, which must be known to the publisher. The user will receive an email notifying them of the subscription invitation, and in the app they may accept or decline the invitation.
Again, no subscription link is transmitted except between the Type.World server and app over HTTPS. The primary use of this API command is for users to pass the subscription on to other users in the app. But a publisher could theoretically use it to invite their users to a subscription directly without providing a button on their website. However, that’s not very convenient, as the publisher needs to collect their users’ Type.World user account email addresses, which could be different from the user account email addresses registered with the publisher. A publisher inviting users directly could be interesting for custom type projects, but for normal access, the button on the publisher’s website is recommended.

The secret keys are then stored in the operating system’s keychain app and subscription URLs stored in the user preferences are stripped of that secret key so that they cannot be easily read by third party code. Since keychain access is normally restricted to the app that created a key in the keychain, a user is normally prompted when a third party wants to read it out.

With it, the subscription URLs with their secret key are stored as securely on the user’s computer as any other password used and stored in the operating system.

## Security Levels

Securing your subscription could involve three different levels of security, of which only two are intended for protected fonts. Of those two, different security levels can be achieved through different implementation effort by the publisher.

### Level 0: No Access Restriction

At the very bottom of security levels there is no access restriction to a subscription and its fonts.

URL *Format A* or *Format B* are used here. Anyone can access these fonts and its primary use would be free fonts.

### Level 1: Secret Key

As soon as a subscription contains a single protected font, the app will require to be linked to a Type.World user account so that the subscription can be recorded in that user account.

When the API Endpoint receives a request for either `installableFonts` or `installFonts` or `uninstallFonts` commands, it should check with the central Type.World server API ([`verifyCredentials` command](https://type.world/developer/api#verifyCredentials)) whether that user account is linked to at least one app instance, or rather, whether the request origin’s app instance is linked to a user account. For the verification API call, the publisher hands the `anonymousTypeWorldUserID` and `anonymousAppID` parameters that it received by the app over to the central server.

**Downsides:**

The security of this approach is limited by the operating system’s keychain security and by links being transmitted by non-encypted means, such as in emails. A user could unintentionally grant access to a secret key request by third party code in the operating system. It is the operating system’s responsibility to prevent this from happening and/or notifying the user sufficiently. But a user also needs to pay sufficient attention. The same is true for all other passwords stored in the keychains and is the normal scenario for storing passwords.

**Benefits:**

While the security level of this approach is limited, a rather important benefit lies in User Experience: See *"Remote De-Authorization of App Instances by the User"*


### Level 2: Tight Access Restriction with Single Use Access Token

The highest level of security can be achieved with some additional effort by the publisher. It involves the single use access token of the subscription URL *Format CE* for initial subscription access, and the inclusion of the subscription URL in the [`verifyCredentials` command](https://type.world/developer/api#verifyCredentials) with the Type.World server.

The access button in the publisher’s user account section contains the single use access token under the URL *Format CE*. This access token is stored in the user account with the publisher and only ever included in this download button. Once the user clicks the button and the app requests the subscription with the `installableFonts` command for the first time, the access token is submitted along with the request in a `accessToken` parameter. The publisher verifies that the request carries the correct access token for this user. If authentication was successful, the publisher invalidates this access token and assigns a fresh one, allowing future access only with the fresh token. (Make sure that the access button isn’t visible on your website when that happens, or that it will be reloaded with the fresh access token instantly upon clicking, because if something goes wrong in the communication after the access token has been invalidated, the user will want to click again and needs to be able to access the fresh access token).

Otherwise, the publisher’s server returns the `insufficientPermission` response and the subscription isn’t added the user account.

The app throws away the single use access token and continues to only ever use the subscription URL in *Format C*.

All subsequent requests with the publisher’s API Endpoint are then authenticated using the already mentioned [`verifyCredentials` command](https://type.world/developer/api#verifyCredentials), but with the additional subscription URL transmitted along with the request in the `subscriptionURL` parameter. Then, the server verifies not only that a Type.World user account is linked to an app instance, but also that the user already holds that subscription.

In summary, a request is authenticated either by a valid access token or by a successful [`verifyCredentials` request](https://type.world/developer/api#verifyCredentials) using the optional `subscriptionURL` parameter.

With this approach, secret subscription URLs (in *Format C*) could theoretically disseminate into the wild with no consequences, because they don’t contain the access token, and without it, users can’t add a subscription by its URL alone. The only way to share such a subscription is the invitation API.

**Downsides:**

This approach cannot prevent a user to invite other users to share a subscription, but the limiting of invitations was never intended. However:

**Benefits:**

This approach is the only way to make 100% sure that users are authentic. If a user violates any of the publisher’s terms, the publisher may revoke the access to a subscription using the invitation API. Along with revoking access to one or all of its initial users, all subsequent invitations by those users to even other users will be revoked as well.

## Remote De-Authorization of App Instances by the User

Subscriptions are synchronized with the central server in a Type.World user account and users can choose to de-authorize all subscriptions for an entire app instance through the app preferences. 

The main incentive for the user to de-authorize his/her older app instances that are not accessible any more on a stolen or bricked computer is to free up font installations, because the font installations of that lost computer are still counted in the publisher’s tracking of installed seats with regards to each font license. 

Should the de-authorized app instance regain access to the internet (in case the computer is actually stolen rather than lost/broken), all protected fonts will be deleted from it instantly. And because all referenced publishers already know of the de-authorization (through the [`verifyCredentials` command](https://type.world/developer/api#verifyCredentials)), new font installations thereafter will also be impossible. While the fonts could theoretically continue to live on an offline computer indefinitely, this approach allows the user to at least free those seats themselves without personally interacting with the publisher to free those seats, or upgrading font licenses.

Therefore, the primary benefit of this is a user experience gain, because users don’t need to interact with the publisher when all this happens.

## Central Subscription Invitation Infrastructure

Because spreading subscription URLs by email (or other means) is potentially unsafe from eavesropping, the central Type.World server provides an invitation API using its JSON API under the [`inviteUserToSubscription`](https://type.world/developer/api#inviteUserToSubscription) command (or directly in the app). Therefore, only users with a registered Type.World user account can be invited. Here, users will be identified by the email address of their Type.World user account (like Dropbox or Google Documents). There is no way to search the Type.World user database for users. Only valid and previously registered email addresses will be accepted.

It is not possible to provide this invitation infrastructure to users without a Type.World user account, because otherwise a notification about the invitation needs to be sent out by email which can be intercepted and accessed before the legitimate user gets access. 

Without a Type.World user account, this notification, however formed, would be the key to the subscription. With a Type.World user account, the account itself is the key, and any form of notification of the invitation, such as by email, is meaningless without the previously existing user account.

## Central Server Authorization

Access to the [`verifyCredentials`](https://type.world/developer/api#verifyCredentials) command (amongst others) on the central Type.World server will be restricted to holders of a publisher-specific secret API key. The API Key can be obtained through the user account section on the Type.World website.


# User Experience Recommendations

## Commercial Fonts

A customer purchases a font from a publisher. It is expected that the customer needs to be logged into the publisher’s web site and that the purchase is recorded in the publisher’s user account.

After the purchase is complete, the customer is offered two download options: The traditional ZIP file and a new *Download in Type.World App* button. Upon clicking on that new button, the Type.World App comes open and sets up the subscription in the app, or updates it if it was previously present. The newly purchased fonts are then available to install for the user.

The user needs to have downloaded and installed the app before this hand-off can take place. And in case of commercial fonts, the user also needs to have created a separate Type.World user account, so that the subscription’s existence for this user can be recorded by the Type.World system. The reason why this is mandatory for commercial fonts is explained under [Remote De-Authorization of App Instances by the User](#remote-de-authorization-of-app-instances-by-the-user).

However, a user only ever needs to install the app and set up a Type.World user account once. After that initial setup, the user experience is flawless.

## Custom Fonts

Graphic designers are working in a branding firm to create a visual appearance for their client’s new brand. A type designer is commissioned by the branding firm to create a custom typeface for this new brand. The type designer uploads the font files to their Type.World font server. This could be their own server implementation or a turn-key service. The type designer then invites the branding firm’s project lead to a subscription in the Type.World App, who in turn invites all graphic designers in the firm to use the subscription in the Type.World App.

The type designer can regularly publish updates of the typeface which will be offered to download for the graphic designers in the app. As opposed to pushing new font files to designers by email, the type designer and the project lead can now observe which of their designers are working with which version of the commissioned typeface, and remind the designer to update the fonts if necessary. The knowledge of which users are using which version of the fonts is anonymous by default, but the font server may also request that the user’s identity is revealed to the server when installing fonts. This knowledge can be made available to the project lead by the font server in a secure way.

## Free Fonts

Free fonts can be offered to download for users, either in one subscription per family, or all fonts in one subscription.


# Developer Tools

## Type.World API
The central *type.world* server operates its own API that offers various interactions with the system, such as the user validation:

[Central Type.World Server API Documentation](/developer/api)

### WARNING: HTTP 500 or 503 response by central server

The central Type.World server is hosted in Google’s cloud in a *Google App Engine*. Instances of this server are initiated and destroyed whenever the load balancer pleases. As a result, a server instance may disappear in the middle of your request, and the request therefore returned with either HTTP Code `500 Internal Server Error` or `503 Service Unavailable`. You need to be prepared for that, and repeat the request if necessary.

Internally, the `typeworld.client` module uses a method called `performRequest()` that loops over the request up to 10 times, making sure that the central server can be reached even if a request is returned with either `500` or `503` once. If you implement your server in Python, you are invited to make use of that method as well, or otherwise create your implementation, as long as you are aware of sudden server disappearances.

## API Endpoint Validator

If you’re building your own API endpoint under the Type.World JSON protocol, we offer a remote API Endpoint Validator that will check your endpoint for proper functionality.

* If you obtain the `typeworld` Python module via [PyPi](https://pypi.org/project/typeworld/) with `pip install typeworld`, you may invoke the validator from the command line: `validateTypeWorldEndpoint typeworld://json+https//typeworldserver.com/api/bZA2JbWHEAkFjako0Mtz/ all`. This is the preferred method because it allows you to check your local development server that isn’t live on the internet. Also if you run it locally, it reduces strain on the central server. (That’s because of latency. These validations will take long, and the load balancer will think it needs to start another instance, which will affect our billing)
* You may invoke the validator on directly this website: [Online API Endpoint Validator](/developer/validate)
* You may also use this validator remotely with its own API: [Type.World API](/developer/api/#validateAPIEndpoint).

# Finances

The Type.World project aims to be a non-profit service to the type industry.
However, there are costs, and those costs are expected to be shouldered by those factions in the industry that use the Type.World system in commercial work for themselves, be it custom fonts or selling commercial fonts. Even free font offerings don’t exist in a vacuum. They’re making money from ads, for instance, and therefore need to support the project.

## Costs

* *Server Costs:* The central server that handles the Type.World user accounts is running on Google App Engine and billed per use. As of this writing we’re still in the free introductory phase that Google offers to all new projects. For later, server costs can’t be foreseen because they highly depend on the server usage, which depends on how widely the type industry adopts this projects. All we can assume for now is that Google’s cloud computing prices are very competitive and are expected to be bearable.
* *Sending emails* from the server via [Mailgun](https://www.mailgun.com) costs money
* *Code Signing Certificates* are necessary separately for both Windows and macOS to sign the GUI App in order to make it installable and usable safely in the operating systems. Costs are currently $129/year for the Windows Certificate and €99/year for membership in the Apple Developer Program; the certificate itself is free for macOS.
* *Legal Costs:* Some parts of this project requires legal aid (Terms & Conditions etc.). I was planning for this work to be done between September 2020 and March 2021, so I haven’t looked into costs yet.
* *Development Costs:* Developing this system costs a lot of time. That development time needs to be paid for, because the developer needs to pay rent, social security, organic food, and wants to be able to put aside money for the future. In other words, the developer wants to be paid a decent salary. Currently, this project is developed by one person (Yanone), but that could and should change in the future. Please not that salaries are distinctively different from *profit* as senselessly accumulating money. As of this writing, Google Fonts is sponsoring the development costs for the system to be published in its first stable version 1.0, until March 2021, with Windows and macOS versions of the GUI app.

## Sources of Income

* *Donations:* Type.World operates a Patreon page for monthly recurring donations. You should donate: [patreon.com/typeWorld](https://www.patreon.com/typeWorld)
* *Sponsoring:* For sponsoring outside of the Patreon donations, please get in touch at [hello@type.world](mailto:hello@type.world)
* *Affiliate Commissions:* The project will try to enter into affiliate commission agreements with commercial type foundries that offer the system to their users. All web traffic to type foundry websites that originates from the Type.World system will be identified by the foundry by a special key that is appended to the website links, such as: `https://awesomefonts.com/familyxyz/?affiliateID=hb6di3kes`. In this example, the string `hb6di3kes` identifies Type.World as the origin. The foundry sets a cookie in the user’s browser for Type.World being the origin, and pays out a commission to Type.World for each sale that is generated thereafter that originated from Type.World. Type.World will be asking for a minimum commission of 5% for sales that originated from itself.

## Future Outlook

Should the income be higher than all costs in the long term, it needs to be decided what to do with that money. Either the income is reduced (for example by lowering the commission percentage), or the excess money is spent on improving the system. Many ideas exist that could be supported by such excess money:

* iOS and Android versions of the Type.World App.
* Creating a carefully curated set of font licenses, the *Type.World Licenses*, that are offered to type foundries to use to sell their fonts under, at least optionally. Like the well known *Creative Commons* set of licenses, font customers would learn and understand the implications of each *Type.World* license over time, greatly enhancing the font buying experience.
* While it is Type.World’s aim to steer clear of selling fonts, and rather driving traffic directly into the foundries’ arms, it could still try to further improve the buying experience for customers of independent type foundries. One such improvement could be a universal login. Users would log into a foundry’s website with their Type.World user account, eliminating the need to create a separate user account for each foundry in a decentralized type world.
* Creating FairFonts.org, a searchable database of all fonts directly available from their producers, connecting customers directly with producers in the fair trade principle. Fair Fonts would exist as a website, but more prominently as a mobile app for people to explore fonts on their phones, let’s say in the subway on their way to work. They can like and share fonts they find there, and receive notifications of newly published fonts by certain or all designers or foundries.



# To Do

The following items aren’t yet implemented in the app, but planned:

* Implement *Collections*. Like playlists in a music app, users can arrange arbitrary fonts into collections. The collections can also be shared with other Type.World users
* When trial fonts expire while the computer is offline, the uninstallation calls won't reach the server and need to be recorded for later sending.
* Unpixelated appearance on hi-resolution Windows screens. The awkward app appearance on hi-resolution Windows screens stems from a limitation in `wx`, a cross-platform Python GUI framework that the Type.World App uses. The limitation is expected to be lifted in `wx`’s upcoming 4.1 release and thus Type.World is expected to look crisp on hi-resolution screens. Sadly, the timeline for that `wx` update is not known. But it’s sure to happen, as `wx` is a very popular and actively developed framework.
* Email verification after account creation
* Look over client’s Pub/Sub implementation. For instance, topics for subscriptions may not yet exist, so when they exist later, the client needs to try to subscribe again
* Decide on whether incoming font asset lists may contain mixed successfull/erroneous results for only successful. In latter case, first check all incoming assets for errors before proceeding with the installation. Further, when an incoming asset list contains both successful as well as erroneous data, abort installation, and then send uninstallation requests back to server, so that recorded installation from just now can be removed again.
* After linking a user account to the app, the existing subscriptions aren’t uploaded/synched