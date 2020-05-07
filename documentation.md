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
These fonts could be hosted either on API endpoints implemented by the type foundry themselves, or on third party services that support the protocol. The custom font scenario is the only one where it makes sense to hire an external service as a turn-key solution because establishing which users get to install which fonts is a fast and straightforward process to set up manually on a web interface for custom jobs, whereas serving commercial fonts to anonymous customers requires the data knowledge of an online shop.

## Benefits

In summary, the technology provides the following benefits over established font download conduct:

### Benefits For Users

* One-click font installation triggered directly from inside the browser, given that the end user has installed the Type.World App once
* Organizing font subscriptions from different publishers in a central Type.World user account. This user account can be automatically synchronized to another computer’s Type.World App that’s connected to the same user account (like a work station computer and a laptop for traveling). For the time being, only the subscriptions are synchronized, and not the installation status of each font. Because seat allowances for commercial font subscriptions are expected to be limited, automatically activating fonts on a second synchronized computer is problematic and not currently planned. Instead, users can organize fonts into collections and activate/deactivate them on separate computers as needed.
* Restoring font subscriptions after a computer has crashed or got lost is as easy as logging back into the Type.World user account in the app. The whole process of archiving and backing up purchased fonts disappears and the time needed to restore a complete work environment after an operating reinstallation is reduced dramatically in regards to the fonts. In that sense, in terms of user experience, the Type.World technology mimicks the behaviours of modern day app stores where all previously purchased apps are readily available for installation on a new machine with one click, except that the Type.World technology doesn’t get itself involved in the selling part like an app store does.
* Users may invite other users to share font subscriptions from within the app
* Installation of font updates is as easy as following the notification via the operating system to trigger the font update. However, fonts will never be installed fully automatically, although this might be an option for the future, because in a professional workflow the designers need to be fully aware of the possibility that the fonts’ metrics may have changed which might mess with their documents. Therefore, font updates will come only as notifications and need to be explicitly triggered by the user.

### Benefits For Publishers

* Anonymous tracking of how many fonts are installed per subscription, giving commercial foundries the ability to observe the adherence of their customers to their font licenses. As desktop fonts are normally licensed limited to a certain number of seats (computers), API endpoints can record font installations anonymously and reject future installation requests once seat allowance is reached. Furthermore, foundries can include a license upgrade link with each font which will be displayed to the end users, making it simple as never before for customers to purchase license upgrades when the limits are reached. As end users grow accustomed to the technology and its benefits, their readiness to purchase upgrades will also grow, as a similarly easy user experience isn’t available with the old way of downloading and organizing fonts from zip archives. This easy license upgrade constitutes real added financial value to foundries on top of binding customers through the general user experience upgrade already.
* For custom font projects, the technology allows the type shop to push font updates onto the workgroup graphic designers fast and reliably and monitor the font version adoption level, unlike previously, where font updates were sent by email and their adoption level was in the hands of god.
Optionally, publishers may request the transmission of end users identities (name and email address) for closed workgroups upon font installation, establishing a direct communication link between publisher and end user for critical communication, for example to remind them of the old font versions they’re using.
* Happier returning customers through user the experience upgrade
* Participation in a new foundry ecosystem that happy Type.World users may want to stay in once they have gotten used to the user experience upgrade. The Type.World app and website will contain a discovery section of all those foundries that are participating in the technology.

# Terminology

* Subscription
* Publisher


# Server Interaction

## The subscription URL

By clicking the *Install in Type.World App* button on your SSL-encrypted website, a URL of the following scheme gets handed off to the locally installed app through the custom protocol handler `typeworld://` that the app has registered with the operating system.

`typeworld://json+http[s]//[subscriptionID[:secretKey[:accessToken]]@]awesomefonts.com/api/`

The URL parts in detail:

* `typeworld://` This is the protocol handler used by the Type.World app. The app advertises the handler to the operating system, and upon clicking such a link, the operating system calls the app and hands over the link.
* `json` The protocol to be used within the Type.World app. Currently, only the Type.World JSON Protocol is available to use.
* `https//` The transport protocol to be used, in this case SSL-encrypted HTTPS. *Note:* because valid URLs are only allowed to contain one `://` sequence which is already in use to denote the custom protocol handler `typeworld://`, the colon `:` will be stripped off of the URL in a browser, even if you define it. The Type.World app will internally convert `https//` back to `https://`.
* `subscriptionID` uniquely identifies a subscription. In case of per-user subscriptions, you would probably use it to identify a user and then decide which fonts to serve him/her. The `subscriptionID` should be an anonymous string and must not contain either `:` or `@` and is optional for publicly accessible subscriptions (such as free fonts). Allowed characters: **[a-z][A-Z][0-9]_-**
* `secretKey` matches with the `subscriptionID` and is used to authenticate the request. This secret key is saved in the OS’s keychain. The `secretKey ` must not contain either `:` or `@` and is optional for publicly accessible subscriptions (such as free fonts). The secret key is actually not necessary to authenticate the request against the server (because the `subscriptionID` is supposed to ba anonymous). Instead it’s necessary to store a secret key in the user’s OS keychain so that complete URLs are not openly visible. Allowed characters: **[a-z][A-Z][0-9]_-**
* `accessToken` Single use access token. Allowed characters: **[a-z][A-Z][0-9]_-**
* `awesomefonts.com/api/` is where your API endpoint sits and waits to serve fonts to your customers.

There are several possible ways to combine access credentials, as follows:

#### Format A

A publicly accessible subscription without any access restrictions. This API endpoint has exactly one subscription to serve: `typeworld://json+https//awesomefonts.com/api/`

#### Format B

A publicly accessible subscription without `secretKey`, but `subscriptionID` still used to identify a particular subscription in this API endpoint: `typeworld://json+https//subscriptionID@awesomefonts.com/api/`

#### Format C

Example for a protected subscription:
`typeworld://json+https//subscriptionID:secretKey@awesomefonts.com/api/`

#### Format CE

Example for a protected subscription with access token:
`typeworld://json+https//subscriptionID:secretKey:accessToken@awesomefonts.com/api/`


## Serving JSON responses

### `POST` requests

To avoid the subscription URL complete with the `subscriptionID` and `secretKey` showing up in server logs, your server should serve your protected JSON data only when replying to `POST` requests. With `POST`, requests parameters will be transmitted in the HTTP headers and will be invisible to server logs.

The app will ask for the JSON responses at your API endpoint (`https://awesomefonts.com/api/` in the above URL examples) and will hand over some or all of the following parameters through HTTP headers:

* `commands` The commands to reply to, such as `installableFonts`.
* `subscriptionID` The aforementioned ID to uniquely identify the fonts you serve.
* `secretKey` The secret key to authenticate the requester.
* `accessToken` The single use access token that you may use to identify whether a user was logged in to your website when first accessing a subscription. The access token is only ever served there in your website’s user account, and thrown away and replaced upon first access using this token. Afterwards users need to be verified with the central Type.World server. See *"Security Design, Level 2"* for details.
* `anonymousAppID` is a key that uniquely and anonymously identifies a Type.World app installation. You should use this to track how often fonts have been installed through the app for a certain user to reject requests once the limit has been reached.
* `fonts` identifying the unique font ID and version number to install or uninstall.
* `userEmail` and `userName` in case the user has a Type.World user account and has explicitly agreed to reveal his/her identity on a per-subscription basis. This only makes sense in a trusted custom type development environment where the type designers may want to get in touch personally with the font’s users in a small work group, for instance in a branding agency. This tremendously streamlines everyone’s workflow. If necessary, a publisher in a trusted custom type development environment could reject the serving of subscriptions to requesters who are unidentified.

### `GET` requests

For simplicity’s sake, you should reject incoming `GET` requests altogether to force the requester into using `POST` requests. This is for your own protection, as `GET` requests complete with the `subscriptionID` and `secretKey` might show up in server logs and therefore pose an attack vector to your protected fonts and meta data.

I suggest to return a `405 Method Not Allowed` HTTP response for all `GET` requests.

### WARNING:

Whatever you do with your server, bear in mind that the parameters attached to the requests could be malformed to contain [SQL injection attacks](https://www.w3schools.com/sql/sql_injection.asp) and the likes and need to be quarantined.




# Security Design


For protected subscriptions, the publisher provides a subscription link that contains a secret key to authenticate a subscription (*Format C*). An additional single-use access token may be added to the URL (*Format CE*) for initial access.

`typeworld://json+https//subscriptionID:secretKey:accessToken@awesomefonts.com/api/`

The security design outlined below consists of an unprotected base level and two optional security levels. The optional security level’s intention isn’t securing the leaking of fonts alone, but also very dominantly a user experience issue in the long run (See *"Remote De-Authorization of App Instances by the User"*).

## Subscription Access

Subscription URLs must not be passed to users by email or other unencrypted means. Because they may contain the secret key for protected subscriptions, the links could be intercepted and the fonts leaked.

Instead, two ways are designated to grant a user access to a subscription:

* **Button on publisher’s website**: The user can access the subscription on the publisher’s website in their personal account section, available only after login. This way, the subscription URL is passed from the browser directly to the app with no transmission other than (ideally) encrypted HTTPS traffic. The subscription URL with its secret key is as secure as the publisher’s website login.
* **Invitation API**: The central Type.World server provides an API ([`inviteUserToSubscription ` command](https://type.world/developer/api#inviteUserToSubscription)) to invite users to a subscription, identified by their Type.World user account email address, which must be known to the publisher. The user will receive an email notifying them of the subscription invitation, and in the app they may accept or decline the invitation.
Again, no subscription link is transmitted except between the Type.World server and app over HTTPS. The primary use of this API command is for users to pass the subscription on to other users in the app. But a publisher could theoretically use it to invite their users to a subscription directly without providing a button on their website. However, that’s not very convenient, as the publisher needs to collect their users’ Type.World user account email addresses, which could be different from the user account email addresses registered with the publisher. For normal access, the button on the publisher’s website is recommended.

The secret keys are then stored in the operating system’s keychain app and subscription URLs stored in the user preferences are stripped of that secret key so that they cannot be easily read by third party code. Since keychain access is normally restricted to the app that created a key in the keychain, a user is normally prompted when a third party wants to read it out.

With it, the subscription URLs with their secret key are stored as securely on the user’s computer as any other password used and stored in the operating system.

## Security Levels

Securing your subscription could involve three different levels of security, of which only two are intended for protected fonts. Of those two, different security levels can be achieved through different implementation effort by the publisher.

### Level 0: No access restriction

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

This approach is the only way to make sure that users are authentic. If a user violates any of the publisher’s terms, the publisher may revoke the access to a subscription using the invitation API, and along with revoking access to one or all of its initial users, all subsequent invitations by those users to even other users will be revoked as well.

## Remote De-Authorization of App Instances by the User

Subscriptions are synchronized with the central server for registered users and users can de-authorize all subscriptions for an entire app instance through the app preferences. 

The main incentive for the user to de-authorize his/her older app instances that are not accessible any more by a stolen or bricked computer is to free up font installations, because the font installations of that lost computer are still counted in the publisher’s tracking of installed seats with regards to each font license. 

Should the de-authorized app instance regain access to the internet (in case the computer is actually stolen rather than lost/broken), all protected fonts will be deleted from it instantly, and because all referenced publishers already know of the de-authorization (through the [`verifyCredentials` command](https://type.world/developer/api#verifyCredentials)), new font installations thereafter will also be impossible. While the fonts could theoretically continue to live on an offline computer indefinitely, this approach allows the user to at least free those seats themselves without personally interacting with the publisher to free those seats, or upgrading font licenses.

Therefore, the primary benefit of this is a user experience gain, because users don’t need to interact with the publisher when all this happens.

# User Experience Recommendations

## Commercial Fonts

## Custom Fonts

Invite team lead to a subscription.

# TODO

* When trial fonts expire while the computer is offline, the uninstallation calls won't reach the server and need to be recorded for later sending.
