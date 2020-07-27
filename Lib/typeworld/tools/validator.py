import typeworld.client
import typeworld.api
import traceback
import json
from typeworld.client.helpers import Garbage


profiles = (
    (
        "setup",
        "Setup",
        (
            "Check API endpoint response (`EndpointResponse` class) and download "
            "subscription (`InstallableFontsResponse` class).\nIf necessary, create "
            "a Type.World user account and try again."
        ),
    ),
    (
        "freefont",
        "Free Fonts",
        (
            "Download and install a free font. This subscription needs to hold at "
            "least one free font.\nThe first free font will be downloaded"
        ),
    ),
    (
        "nonexpiringprotectedfont",
        "Non-expiring Protected Fonts",
        (
            "To check the proper response of your API Endpoint in handling protected "
            "fonts (the norm for commercial setups),\nthis test requires the "
            "subscription to hold at least one protected font with at least one "
            "`LicenseUsage` object\nwith a `seatsAllowed` attribute of `1` and a "
            "`seatsInstalled` attribute of `0`.\nThe routine will install the font, "
            "and then attempt to install the same font a second time on\nanother "
            "(assumed) computer. This is supposed to fail because only 1 seat is "
            "allowed.\nOnly after removing the font installation, the second computer "
            "can succeed in installing the font."
        ),
    ),
    # 	('expiringprotectedfont',
    # 'Expiring Protected Fonts',
    # 'To check the proper response of your API Endpoint in handling
    # protected fonts (the norm for commercial setups), this test requires
    # the subscription to hold at least one protected font with at least one
    # LicenseUsage object with a seatsAllowed attribute of 1 and a seatsInstalled
    # attribute of 0. The routine will install the font, and then attempt to
    # install the same font a second time on another (assumed) computer.
    # This is supposed to fail because only 1 seat is allowed. Only after
    # removing the font installation, the second computer can succeed in
    # installing the font.'),
)


def validateAPIEndpoint(
    subscriptionURL, runProfiles, endpointURL="https://api.type.world/v1", responses={}
):

    if "freefont" in runProfiles and "setup" not in runProfiles:
        runProfiles.append("setup")

    if "nonexpiringprotectedfont" in runProfiles and "setup" not in runProfiles:
        runProfiles.append("setup")

    if "all" in runProfiles:
        for keyword in [x[0] for x in profiles]:
            if keyword not in runProfiles:
                runProfiles.append(keyword)

    # Initiate
    if not responses:
        responses = {
            "response": "success",
        }
        responses["version"] = typeworld.api.VERSION

    responses["stages"] = []
    responses["information"] = []
    responses["warnings"] = []
    responses["errors"] = []

    typeworldClient = typeworld.client.APIClient(mothership=endpointURL)
    typeworldClient2 = typeworld.client.APIClient(mothership=endpointURL)
    testUser = (f"{Garbage(20)}@type.world", Garbage(20))
    testUser2 = (f"{Garbage(20)}@type.world", Garbage(20))
    check = None
    stage = None
    stages = [x[1] for x in profiles]
    stages.append("Teardown")

    serverRequiresValidUser = False

    class Check(object):
        def __init__(self, description):
            self.description = description

        def success(self, message=None):

            d = {}
            d["description"] = self.description
            d["result"] = "passed"
            d["comments"] = message or ""
            responses["stages"][-1]["log"].append(d)

            # print('Success:', self.description)

        def fail(self, message):

            d = {}
            d["description"] = self.description
            d["result"] = "failed"
            d["comments"] = message or ""
            responses["stages"][-1]["log"].append(d)

            # print('Failure:', self.description)

            responses["stages"][-1]["result"] = "failed"
            responses["response"] = "failed"
            responses["errors"].append(message)
            typeworldClient.deleteUserAccount(*testUser)
            typeworldClient2.deleteUserAccount(*testUser2)

    class Stage(object):
        def __init__(self, description):

            self.description = description
            assert self.description in stages

            # print(f'Stage {self.description}')

            # Add previous stage to finished list
            d = {}
            d["name"] = self.description
            d["log"] = []
            d["result"] = "incomplete"
            responses["stages"].append(d)

        def complete(self):
            responses["stages"][-1]["result"] = "passed"
            stages.remove(self.description)

        def incomplete(self):
            responses["stages"][-1]["result"] = "notTested"

    try:

        if "setup" in runProfiles:

            #############################
            #############################
            stage = Stage("Setup")

            # Check EndpointResponse
            check = Check("Loading `EndpointResponse`")
            success, message = typeworldClient.rootCommand(subscriptionURL)

            if type(message) == list:
                message = message[0]

            passOnResponses = []

            if success:
                check.success()
            else:
                if message in passOnResponses:
                    check.success()
                else:
                    check.fail(message)
                    return responses

            # Check normal subscription
            check = Check("Loading subscription with `installableFonts` command")
            success, message, publisher, subscription = typeworldClient.addSubscription(
                subscriptionURL
            )

            if type(message) == list:
                message = message[0]

            passOnResponses = ["#(response.validTypeWorldUserAccountRequired)"]

            if success:
                check.success()
            else:
                if message in passOnResponses:
                    pass
                else:
                    check.fail(message)
                    return responses

            # (response.validTypeWorldUserAccountRequired)
            if message == "#(response.validTypeWorldUserAccountRequired)":

                check.success(
                    (
                        "Publisher server responded with "
                        "`validTypeWorldUserAccountRequired`. "
                        "Need to create valid user account first."
                    )
                )
                serverRequiresValidUser = True

                # Create User Account
                check = Check("Create first Type.World user account")
                success, message = typeworldClient.createUserAccount(
                    "API Validator Test User", testUser[0], testUser[1], testUser[1]
                )

                if type(message) == list:
                    message = message[0]

                passOnResponses = []

                if success:
                    check.success()
                else:
                    if message in passOnResponses:
                        check.success()
                    else:
                        check.fail(message)
                        return responses

                # Retry normal subscription
                check = Check(
                    (
                        "Loading subscription another time, this time with valid "
                        "Type.World user account"
                    )
                )
                (
                    success,
                    message,
                    publisher,
                    subscription,
                ) = typeworldClient.addSubscription(subscriptionURL)

                if type(message) == list:
                    message = message[0]

                passOnResponses = []

                if success:
                    check.success()
                else:
                    if message in passOnResponses:
                        check.success()
                    else:
                        check.fail(message)
                        return responses

            # Test for fonts
            freeFonts = []
            protectedFonts = []
            protectedNonExpiringFonts = []
            protectedExpiringFonts = []
            protectedNonExpiringYetTrialFonts = []

            for publisher in typeworldClient.publishers():
                for subscription in publisher.subscriptions():
                    for foundry in subscription.protocol.installableFontsCommand()[
                        1
                    ].foundries:
                        for family in foundry.families:
                            for font in family.fonts:
                                if font.free:
                                    freeFonts.append(font)
                                if font.protected:
                                    protectedFonts.append(font)
                                    if font.expiryDuration:
                                        protectedNonExpiringYetTrialFonts.append(font)
                                    elif font.expiry:
                                        protectedExpiringFonts.append(font)
                                    else:
                                        protectedNonExpiringFonts.append(font)

            check = Check("Looking for fonts")

            protectedNonExpiringFontsVerb = (
                "is" if len(protectedNonExpiringFonts) == 1 else "are"
            )
            protectedExpiringFontsVerb = (
                "is" if len(protectedExpiringFonts) == 1 else "are"
            )
            protectedNonExpiringYetTrialFontsVerb = (
                "carries" if len(protectedNonExpiringYetTrialFonts) == 1 else "carry"
            )

            check.success(
                (
                    f"Found {len(freeFonts)} free fonts, {len(protectedFonts)} "
                    f"protected fonts, of which {len(protectedNonExpiringFonts)} "
                    f"{protectedNonExpiringFontsVerb} not expiring at all, "
                    f"{len(protectedExpiringFonts)} {protectedExpiringFontsVerb} "
                    f"currently expiring, and {len(protectedNonExpiringYetTrialFonts)} "
                    f"{protectedNonExpiringYetTrialFontsVerb} a `expiryDuration` "
                    f"attribute but is/are currently not yet expiring."
                )
            )

            if protectedFonts and not serverRequiresValidUser:
                check = Check(
                    (
                        "Check if server responded with "
                        "`validTypeWorldUserAccountRequired` when no Type.World "
                        "user credentials were given"
                    )
                )
                check.fail(
                    (
                        "The subscription holds protected fonts, but the server didn’t "
                        "reject requests with the `validTypeWorldUserAccountRequired` "
                        "response when queried without Type.World user credentials "
                        "(`anonymousUserID` and `secretKey`). In that case it must "
                        "serve the `validTypeWorldUserAccountRequired` response for "
                        "both the `installableFonts` as well as the `installFonts` "
                        "response."
                    )
                )
                return responses

            stage.complete()

        if "freefont" in runProfiles:

            # Install Free Font
            if freeFonts:

                #############################
                #############################
                stage = Stage("Free Fonts")

                font = freeFonts[0]
                subscription = font.parent.parent.parent.parent.subscription
                check = Check(
                    f"Installing first found free font `{font.postScriptName}`"
                )
                success, message = subscription.installFonts(
                    [[font.uniqueID, font.getVersions()[-1].number]]
                )

                if type(message) == list:
                    message = message[0]

                passOnResponses = ["#(response.termsOfServiceNotAccepted)"]

                if success:
                    check.success()
                else:
                    if message in passOnResponses:
                        check.success()
                    else:
                        check.fail(message)
                        return responses

                # Agree to terms, repeat
                if message == "#(response.termsOfServiceNotAccepted)":

                    subscription.set("acceptedTermsOfService", True)
                    check.success(
                        (
                            "The internal client responded with "
                            "`termsOfServiceNotAccepted`. So we simulate the click on "
                            "the acceptance button here and try again."
                        )
                    )
                    check = Check(
                        f"Installing first valid free font `{font.postScriptName}`"
                    )

                    # Repeat
                    success, message = subscription.installFonts(
                        [[font.uniqueID, font.getVersions()[-1].number]]
                    )

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = []

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(message)
                            return responses

                stage.complete()

        if "nonexpiringprotectedfont" in runProfiles:

            # Install protected fonts
            if protectedFonts:

                # Non-expiring
                if protectedNonExpiringFonts:

                    #############################
                    #############################
                    stage = Stage("Non-expiring Protected Fonts")

                    check = Check(
                        (
                            "Checking for the existence of a non-expiring protected "
                            "font with installed seats of 0 and a seat limit of 1, so "
                            "we can test for reaching seat allowances"
                        )
                    )
                    validFont = None
                    for font in protectedNonExpiringFonts:
                        if len(font.usedLicenses) == 1:
                            for usedLicense in font.usedLicenses:
                                if (
                                    usedLicense.seatsAllowed == 1
                                    and usedLicense.seatsInstalled == 0
                                ):
                                    validFont = font
                                    break

                    if not validFont:
                        check.fail(
                            (
                                "For testing purposes, this subscription needs one "
                                "non-expiring protected font that carries one "
                                "LicenseUsage with a `seatsInstalled` attribute of "
                                "`0` and a `seatsAllowed` attribute of `1`."
                            )
                        )
                        return responses

                    # Install font. Expected to fail because
                    # of un-agreed Terms & Conditions
                    font = validFont
                    fontID = font.uniqueID
                    subscription = font.parent.parent.parent.parent.subscription
                    check = Check(
                        (
                            f"Installing first valid non-expiring "
                            f"protected font `{font.postScriptName}`"
                        )
                    )
                    success, message = subscription.installFonts(
                        [[font.uniqueID, font.getVersions()[-1].number]]
                    )

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = ["#(response.termsOfServiceNotAccepted)"]

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            pass
                        else:
                            check.fail(message)
                            return responses

                    # Agree to terms, repeat
                    if message == "#(response.termsOfServiceNotAccepted)":
                        subscription.set("acceptedTermsOfService", True)
                        check.success(
                            (
                                "The internal client responded with "
                                "`termsOfServiceNotAccepted`. So we simulate the click "
                                "on the acceptance button here and try again."
                            )
                        )
                        check = Check(
                            (
                                f"Installing first valid non-expiring "
                                f"protected font `{font.postScriptName}`"
                            )
                        )

                        # Repeat
                        success, message = subscription.installFonts(
                            [[font.uniqueID, font.getVersions()[-1].number]]
                        )

                        if type(message) == list:
                            message = message[0]

                        passOnResponses = ["#(response.revealedUserIdentityRequired)"]

                        if success:
                            check.success()
                        else:
                            if message in passOnResponses:
                                pass
                            else:
                                check.fail(message)
                                return responses

                    # Agree to terms, repeat
                    if message == "#(response.revealedUserIdentityRequired)":
                        subscription.set("revealIdentity", True)
                        check.success(
                            (
                                "The server requested to have the user’s identity "
                                "revealed as per the `revealedUserIdentityRequired` "
                                "response. Let’s agree and try again."
                            )
                        )
                        check = Check(
                            (
                                f"Installing first valid non-expiring "
                                f"protected font `{font.postScriptName}`"
                            )
                        )

                        # Repeat
                        success, message = subscription.installFonts(
                            [[font.uniqueID, font.getVersions()[-1].number]]
                        )

                        if type(message) == list:
                            message = message[0]

                        passOnResponses = []

                        if success:
                            check.success()
                        else:
                            if message in passOnResponses:
                                check.success()
                            else:
                                check.fail(message)
                                return responses

                    # See if installed Seats changed
                    check = Check(
                        (
                            f"Check if installed seats of `{font.postScriptName}` "
                            "license changed from `0` to `1` after font installation"
                        )
                    )
                    # Reload font object
                    font = subscription.fontByID(fontID)
                    if font.usedLicenses[0].seatsInstalled == 1:
                        check.success()
                    else:
                        check.fail(
                            (
                                f"Font’s `seatsInstalled` attribute is "
                                f"`{font.usedLicenses[0].seatsInstalled}`, "
                                f"should be `1`."
                            )
                        )
                        return responses

                    # Install font on second computer
                    # Create User Account
                    check = Check("Create second Type.World user account")
                    success, message = typeworldClient2.createUserAccount(
                        "API Validator Test User 2",
                        testUser2[0],
                        testUser2[1],
                        testUser2[1],
                    )

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = []

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(message)
                            return responses

                    # Load normal subscription
                    check = Check("Loading subscription for second user")
                    (
                        success,
                        message,
                        publisher2,
                        subscription2,
                    ) = typeworldClient2.addSubscription(subscriptionURL)

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = []

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(message)
                            return responses

                    subscription2.set("acceptedTermsOfService", True)
                    subscription2.set("revealIdentity", True)
                    font2 = subscription2.fontByID(fontID)

                    # See if installed Seats changed
                    check = Check(
                        (
                            f"Check if installed seats of `{font2.postScriptName}` "
                            "for second user is also `1`"
                        )
                    )
                    if font2.usedLicenses[0].seatsInstalled == 1:
                        check.success()
                    else:
                        check.fail(
                            (
                                f"Font’s `seatsInstalled` attribute is "
                                f"`{font2.usedLicenses[0].seatsInstalled}`, "
                                f"should be `1`."
                            )
                        )
                        return responses

                    # Install Font
                    check = Check(
                        (
                            f"Install same `{font2.postScriptName}` for second user, "
                            f"expecting to fail with `seatAllowanceReached` response"
                        )
                    )
                    success, message = subscription2.installFonts(
                        [[font2.uniqueID, font2.getVersions()[-1].number]]
                    )

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = ["#(response.seatAllowanceReached)"]

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(message)
                            return responses

                    # # Seat allowance reached
                    # if message == '#(response.seatAllowanceReached)':
                    # 	check.success()

                    # Uninstall font for first user
                    check = Check(f"Uninstall `{font2.postScriptName}` for first user")
                    success, message = subscription.removeFonts([font.uniqueID])

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = []

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(message)
                            return responses

                    # See if installed Seats changed
                    check = Check(
                        (
                            f"Check if installed seats of `{font.postScriptName}` "
                            f"license changed from `1` to `0` after font removal"
                        )
                    )
                    # Reload font object
                    font = subscription.fontByID(fontID)
                    if font.usedLicenses[0].seatsInstalled == 0:
                        check.success()
                    else:
                        check.fail(
                            (
                                f"Font’s `seatsInstalled` attribute is "
                                f"`{font.usedLicenses[0].seatsInstalled}`, "
                                f"should be `0`."
                            )
                        )
                        return responses

                    # See if installed Seats changed
                    check = Check(
                        (
                            f"Check if installed seats of `{font2.postScriptName}` "
                            f"license changed from `1` back to `0` after subscription "
                            f"update for second user"
                        )
                    )
                    subscription2.update()
                    # Reload font object
                    font2 = subscription2.fontByID(fontID)
                    if font2.usedLicenses[0].seatsInstalled == 0:
                        check.success()
                    else:
                        check.fail(
                            (
                                f"Font’s `seatsInstalled` attribute is "
                                f"`{font2.usedLicenses[0].seatsInstalled}`, "
                                f"should be `0`."
                            )
                        )
                        return responses

                    # Install Font
                    check = Check(
                        f"Install `{font2.postScriptName}` again for second user"
                    )
                    success, message = subscription2.installFonts(
                        [[font2.uniqueID, font2.getVersions()[-1].number]]
                    )

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = []

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(message)
                            return responses

                    # Uninstall font for second user
                    check = Check(f"Uninstall `{font2.postScriptName}` for second user")
                    success, message = subscription2.removeFonts([font2.uniqueID])

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = []

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(message)
                            return responses

                    # Uninstall font for second user, a second time
                    check = Check(
                        (
                            f"Uninstall `{font2.postScriptName}` for second user yet "
                            f"again, this time expecting `unknownInstallation` "
                            f"response because font shouldn’t be recorded as installed "
                            f"anymore"
                        )
                    )
                    success, message = subscription2.removeFonts(
                        [font2.uniqueID], dryRun=True
                    )

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = ["#(response.unknownInstallation)"]

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(message)
                            return responses

                    # APP REVOCATION

                    # Revoke App Instance
                    check = Check("Revoke app instance")
                    success, message = typeworldClient.revokeAppInstance()

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = []

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(message)
                            return responses

                    # Access subscription
                    check = Check(
                        (
                            "Update subscription in revoked app instance, expected "
                            "to pass despite revoked app instance"
                        )
                    )
                    success, message, changed = subscription.update()

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = []

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(
                                (
                                    "It seems intuitive to return a "
                                    "`insufficientPermission` response when the user "
                                    "isn’t valid. But we need a successful response "
                                    "here in case anything in the revokation process "
                                    "needs to be repeated while the app instance is "
                                    "already marked as revoked. In this case we still "
                                    "need to be able to access the meta data about the "
                                    "fonts (= the subscription), to be able to send "
                                    "`uninstall` requests. Only the font installation "
                                    "must fail (this would have been the next step)"
                                )
                            )
                    # 							return responses

                    # Install font
                    check = Check(
                        (
                            f"Install `{font.postScriptName}` in revoked app instance, "
                            "expected to fail with `insufficientPermission` response"
                        )
                    )
                    success, message = subscription.installFonts(
                        [[font.uniqueID, font.getVersions()[-1].number]]
                    )

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = ["#(response.insufficientPermission)"]

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(
                                (
                                    "When an app instance is revoked, the font "
                                    "installation request needs to return with a "
                                    "`insufficientPermission` response here."
                                )
                            )
                    # 							return responses

                    # Reactivate App Instance
                    check = Check("Reactivate app instance")
                    success, message = typeworldClient.reactivateAppInstance()

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = []

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(message)
                            return responses

                    # Install font
                    check = Check(
                        f"Install `{font.postScriptName}` in reactivated app instance"
                    )
                    success, message = subscription.installFonts(
                        [[font.uniqueID, font.getVersions()[-1].number]]
                    )

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = []

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(message)
                            return responses

                    # Remove font
                    check = Check(
                        f"Remove `{font.postScriptName}` in reactivated app instance"
                    )
                    success, message = subscription.removeFonts([font.uniqueID])

                    if type(message) == list:
                        message = message[0]

                    passOnResponses = []

                    if success:
                        check.success()
                    else:
                        if message in passOnResponses:
                            check.success()
                        else:
                            check.fail(message)
                            return responses

                    stage.complete()

    except Exception:
        if stage and check:
            check.fail(traceback.format_exc())
        if stage:
            stage.complete()

        responses["response"] = "failure"
        responses["errors"] = [traceback.format_exc()]

        # return responses

    if "setup" in runProfiles:

        #############################
        #############################
        stage = Stage("Teardown")
        check = Check(
            (
                "Uninstall all remaining fonts and delete temporary "
                "user accounts (if created)"
            )
        )

        success, message = typeworldClient.deleteUserAccount(*testUser)
        if type(message) == list:
            message = message[0]

        passOnResponses = ["#(response.userUnknown)"]

        if success:
            pass
        else:
            if message in passOnResponses:
                check.success()
            else:
                check.fail(message)
        # 				return responses

        success, message = typeworldClient2.deleteUserAccount(*testUser2)
        if type(message) == list:
            message = message[0]

        passOnResponses = ["#(response.userUnknown)"]

        if success:
            pass
        else:
            if message in passOnResponses:
                check.success()
            else:
                check.fail(message)
        # 				return responses

        check.success()
        stage.complete()

    for stage in stages:
        stage = Stage(stage)
        stage.incomplete()

    return responses


def main():
    import argparse

    choices = ["all", *[x[0] for x in profiles]]
    helpString = f"a profile name: {'|'.join(choices)}\n\nIn details:"
    for keyword, title, description in profiles:
        headline = f"{title} ({keyword}):"
        helpString += f'\n\n{headline}\n{"#" * len(headline)}\n{description}'
    parser = argparse.ArgumentParser(
        description="Validate a Type.World API JSON Endpoint",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "subscriptionURL",
        metavar="subscriptionURL",
        type=str,
        help=(
            "Type.World Subscription URL (see: "
            "https://type.world/developer#the-subscription-url)"
        ),
    )
    parser.add_argument(
        "profiles",
        metavar="profile",
        type=str,
        nargs="+",
        help=helpString,
        choices=choices,
    )

    args = parser.parse_args()
    responses = validateAPIEndpoint(args.subscriptionURL, args.profiles)
    print(json.dumps(responses, indent=4))


if __name__ == "__main__":
    main()
