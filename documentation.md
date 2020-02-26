# Server Interaction

## The subscription URI (Unique Resource Identifier)

By clicking the *Install in Type.World App* button on your SSL-encrypted website, a URI of the following scheme gets handed off to the locally installed app through the custom protocol handler `typeworld://` that the app has registered with the operating system.

`typeworld://json+http[s]//[subscriptionID[:secretKey[:accessToken]]@]awesomefonts.com/api/`

The URI parts in detail:

* `typeworld://` This is the protocol handler used by the Type.World app. The app advertises the handler to the operating system, and upon clicking such a link, the operating system calls the app and hands over the link.
* `json` The protocol to be used within the Type.World app. Currently, only the Type.World JSON Protocol is available to use.
* `https//` The transport protocol to be used, in this case SSL-encrypted HTTPS. *Note:* because valid URLs are only allowed to contain one `://` sequence which is already in use to denote the custom protocol handler `typeworld://`, the colon `:` will be stripped off of the URL in a browser, even if you define it. The Type.World app will internally convert `https//` back to `https://`.
* `subscriptionID` uniquely identifies a subscription. In case of per-user subscriptions, you would probably use it to identify a user and then decide which fonts to serve him/her. The `subscriptionID` should be an anonymous string and must not contain either `:` or `@` and is optional for publicly accessible subscriptions (such as free fonts).
* `secretKey` matches with the `subscriptionID` and is used to authenticate the request. This secret key is saved in the OS’s keychain. The `secretKey ` must not contain either `:` or `@` and is optional for publicly accessible subscriptions (such as free fonts). The secret key is actually not necessary to authenticate the request against the server. Instead it’s necessary to store a secret key in the user’s OS keychain so that complete URLs are not openly visible.
* `accessToken` 
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




# Security Design


For protected subscriptions, the publisher provides a subscription link that contains a secret key to authenticate a subscription (*Format C*). An additional single-use access token may be added to the URL (*Format CE*) for initial access.

`typeworld://json+https//subscriptionID:secretKey:accessToken@awesomefonts.com/api/`

The security design outlined below consists of a an unprotected base level and two optional security levels. The optional security level’s intention isn’t securing the leaking of fonts alone, but also dominantly a user experience issue (See *"Remote De-Authorization of App Instances by the User"*).

## Subscription Access

Subscription URIs must not be passed to users by email or other unencrypted means. Because they may contain the secret key for protected subscriptions, the links could be intercepted and the fonts leaked.

Instead, two ways are designated to grant a user access to a subscription:

* **Button on publisher’s website**: The user can access the subscription on the publisher’s website in their personal account section, available only after login. This way, the subscription URI is passed from the browser directly to the app with no transmission other than (ideally) encrypted HTTPS traffic. The subscription URI with its secret key is as secure as the publisher’s website login.
* **Invitation API**: The central Type.World server provides an API ([`inviteUserToSubscription ` command](https://type.world/developer/api#inviteUserToSubscription)) to invite users to a subscription, identified by their Type.World user account email address, which must be known to the publisher. The user will receive an email notifying them of the subscription invitation, and in the app they may accept or decline the invitation.
Again, no subscription link is transmitted except between the Type.World server and app over HTTPS. The primary use of this API command is for users to pass the subscription on to other users in the app. But a publisher could theoretically use it to invite their users to a subscription directly without providing a button on their website. However, that’s not very convenient, as the publisher needs to collect their users’ Type.World user account email addresses, which could be different from the user account email addresses registered with the publisher. For initial access, the button on the publisher’s website is recommended.

The secret keys are then stored in the operating system’s keychain app and subscription URIs stored in the user preferences are stripped of that secret key so that they cannot be easily read by third party code. Since keychain access is normally restricted to the app that created a key in the keychain, a user is normally prompted when a third party wants to read it out.

With it, the subscription URIs with their secret key are stored as securely on the user’s computer as any other password used and stored in the operating system.

## Security Levels

Securing your subscription could involve three different levels of security, of which only two are intended for protected fonts. Of those two, different security levels can be achieved through different implementation effort be the publisher.

### Level 0: No access restriction

At the very bottom of security levels there is no access restriction to a subscription and its fonts.

URI *Format A* or *Format B* are used here. Anyone can access these fonts and its primary use would be free font subscriptions.

### Level 1: Secret Key

As soon as a subscription contains a single protected font, the app will require to be linked to a Type.World user account so that the subscription can be recorded in that user account.

When the API Endpoint receives a request for either `installableFonts` or `installFont` or `uninstallFont` commands, it should check with the central Type.World server API ([`verifyCredentials` command](https://type.world/developer/api#verifyCredentials)) whether that user account is linked to at least one app instance, or in other words, whether this app instance is linked to a user account. For the verification API call, the publisher hands the `anonymousTypeWorldUserID` and `anonymousAppID` parameters that it received by the app over to the central server.

**Downsides:**

The security of this approach is limited by the operating system’s keychain security and by links being transmitted by non-encypted means, such as in emails. A user could unintentionally grant access to a secret key request by third party code. It is the operating system’s responsibility to prevent this from happening and/or notifying the user sufficiently. But a user also needs to pay sufficient attention. The same is true for all other passwords stored in the keychains and is the normal scenario for storing passwords.

**Benefits:**

While the security level of this approach is limited, a rather important benefit lies in User Experience: See *"Remote De-Authorization of App Instances by the User"*


### Level 2: Tight Access Restriction with Single Use Access Token

The highest level of security can be achieved with some additional effort by the publisher. It involves the single use access token of the subscription URI *Format CE* for initial subscription access, and the inclusion of the subscription URI in the [`verifyCredentials` command](https://type.world/developer/api#verifyCredentials) with the Type.World server.

The access button in the publisher’s user account section contains the addition single use access token under the URI *Format CE*. This access token is stored in the user account with the publisher and only ever included in this download button. Once the user clicks the button and the app requests the subscription with the `installableFonts` command for the first time, the access token is submitted along with the request in a `accessToken` parameter. The publisher verifies that the request carries the correct access token for this user. If authentication was successful, the publisher invalidates this access token and assigns a fresh one, allowing future access only with the fresh token. (Make sure that the access button isn’t visible on your website when that happens, or that it will be reloaded with the fresh access token instantly upon clicking, because if something goes wrong in the communication after the access token has been invalidated, the user will want to click again and needs to be able to access the fresh access token).

Otherwise, the publisher’s server returns the `insufficientPermission` response and the subscription isn’t added the user account.

The app throws away the single use access token and continues to only ever use the subscription URI in *Format C*.

All subsequent requests with the publisher’s API Endpoint are then authenticated using the already mentioned [`verifyCredentials` command](https://type.world/developer/api#verifyCredentials), but with the additional subscription URI transmitted along with the request in the `subscriptionURI` parameter. Then, the server verifies not only that a Type.World user account is linked to an app instance, but also that the user already holds that subscription.

In summary, a request is authenticated either by a valid access token or by a successful [`verifyCredentials` request](https://type.world/developer/api#verifyCredentials) using the optional `subscriptionURI` parameter.

With this approach, secret subscription URIs (in *Format C*) could theoretically disseminate into the wild with no consequences, because they don’t contain the access token, and without it, users can’t add a subscription by its URI alone. The only way to share such a subscription is the invitation API.

**Downsides:**

This approach cannot prevent a user to invite other users to share a subscription, but the limiting of invitations was never intended. However:

**Benefits:**

This approach is the only way to make sure that users are authentic. If a user violates any of the publisher’s terms, the publisher may revoke the access to a subscription using the invitation API, and along with revoking access to one or all of its initial users, all subsequent invitations by those users to even other users will be revoked as well.

***Note:*** This command isn’t yet implemented with the central Type.World server as of this writing, Feb 26nd 2020.

## Remote De-Authorization of App Instances by the User

Subscriptions are synchronized with the central server for registered users and users can de-authorize all subscriptions for an entire app instance through the app preferences. 

The main incentive for the user to de-authorize his/her older app instances that are not accessible any more by a stolen or bricked computer is to free up font installations, because the font installations of that lost computer are still counted in the publisher’s tracking of installed seats with regards to each font license. 

Should the de-authorized app instance regain access to the internet (in case the computer is actually stolen rather than lost/broken), all fonts and subscriptions will be deleted from it instantly, and because all referenced publishers already know of the de-authorization (through the [`verifyCredentials` command](https://type.world/developer/api#verifyCredentials)), new font installations thereafter will also be impossible. While the fonts could theoretically continue to live on an offline computer indefinitely, this approach allows the user to at least free those seats themselves without personally interacting with the publisher to free those seats, or upgrading font licenses.
