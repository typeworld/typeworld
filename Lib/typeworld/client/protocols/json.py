import urllib
import urllib.error
import typeworld.client.protocols
import typeworld.api
from typeworld.api import VERSION


def readJSONResponse(url, responses, acceptableMimeTypes, data={}):
    d = {}
    d["errors"] = []
    d["warnings"] = []
    d["information"] = []

    root = typeworld.api.RootResponse()

    request = urllib.request.Request(url)

    if "source" not in data:
        data["source"] = "typeworldApp"

    # gather commands
    commands = [response._command["keyword"] for response in responses]
    data["commands"] = ",".join(commands)

    data = urllib.parse.urlencode(data)
    data = data.encode("ascii")

    try:
        import ssl
        import certifi

        sslcontext = ssl.create_default_context(cafile=certifi.where())

        try:
            response = urllib.request.urlopen(request, data, context=sslcontext)
        except ConnectionRefusedError:
            d["errors"].append(f"Connection refused: {url}")
            return root, d
        except urllib.error.URLError:
            d["errors"].append(f"Connection refused: {url}")
            return root, d

        incomingMIMEType = response.headers["content-type"].split(";")[0]
        if incomingMIMEType not in acceptableMimeTypes:
            d["errors"].append(
                "Resource headers returned wrong MIME type: '%s'. Expected is '%s'."
                % (response.headers["content-type"], acceptableMimeTypes)
            )

        if response.getcode() != 200:
            d["errors"].append(str(response.info()))

        if response.getcode() == 200:
            # Catching ValueErrors
            try:
                root.loadJSON(response.read().decode())
                information, warnings, errors = root.validate()

                if information:
                    d["information"].extend(information)
                if warnings:
                    d["warnings"].extend(warnings)
                if errors:
                    d["errors"].extend(errors)
            except ValueError as e:
                d["errors"].append(str(e))

    except urllib.request.HTTPError as e:
        d["errors"].append("Error retrieving %s: %s" % (url, e))

    return root, d


class TypeWorldProtocol(typeworld.client.protocols.TypeWorldProtocolBase):
    def initialize(self):
        self.versions = []
        self._rootCommand = None
        self._installableFontsCommand = None
        self._installFontsCommand = None

    def loadFromDB(self):
        """Overwrite this"""

        if self.get("endpoint"):
            api = typeworld.api.EndpointResponse()
            api.parent = self
            api.loadJSON(self.get("endpoint"))
            self._rootCommand = api

        if self.get("installableFonts"):
            api = typeworld.api.InstallableFontsResponse()
            api.parent = self
            api.loadJSON(self.get("installableFonts"))
            self._installableFontsCommand = api

        if self.get("installFonts"):
            api = typeworld.api.InstallFontsResponse()
            api.parent = self
            api.loadJSON(self.get("installFonts"))
            self._installFontsCommand = api

    def latestVersion(self):
        return self._installableFontsCommand

    def returnRootCommand(self, testScenario):

        if not self._rootCommand:

            # Read response
            data = {
                "subscriptionID": self.url.subscriptionID,
                "appVersion": VERSION,
            }
            if testScenario:
                data["testScenario"] = testScenario
            root, responses = readJSONResponse(
                self.connectURL(),
                [typeworld.api.EndpointResponse()],
                typeworld.api.INSTALLABLEFONTSCOMMAND["acceptableMimeTypes"],
                data=data,
            )

            # Errors
            if responses["errors"]:
                return False, responses["errors"][0]

            self._rootCommand = root.endpoint

        # Success
        return True, self._rootCommand

    def returnInstallableFontsCommand(self):
        return True, self.latestVersion()

    def protocolName(self):
        return "Type.World JSON Protocol"

    def update(self):

        data = {
            "subscriptionID": self.url.subscriptionID,
            "anonymousAppID": self.client.anonymousAppID(),
            "anonymousTypeWorldUserID": self.client.user(),
            "appVersion": VERSION,
            "mothership": self.client.mothership,
        }
        if self.client.testScenario:
            data["testScenario"] = self.client.testScenario
        secretKey = self.getSecretKey()
        if secretKey:
            data["secretKey"] = secretKey
        if self.client.testing:
            data["testing"] = "true"

        root, responses = readJSONResponse(
            self.connectURL(),
            [
                typeworld.api.EndpointResponse(),
                typeworld.api.InstallableFontsResponse(),
            ],
            typeworld.api.INSTALLABLEFONTSCOMMAND["acceptableMimeTypes"],
            data=data,
        )
        api = root.installableFonts

        if responses["errors"]:

            if (
                self.url.unsecretURL()
                in self.subscription.parent._updatingSubscriptions
            ):
                self.subscription.parent._updatingSubscriptions.remove(
                    self.url.unsecretURL()
                )
            self.subscription._updatingProblem = "\n".join(responses["errors"])
            return False, self.subscription._updatingProblem, False

        if api.response == "error":
            if (
                self.url.unsecretURL()
                in self.subscription.parent._updatingSubscriptions
            ):
                self.subscription.parent._updatingSubscriptions.remove(
                    self.url.unsecretURL()
                )
            self.subscription._updatingProblem = api.errorMessage
            return False, self.subscription._updatingProblem, False

        if api.response in (
            "temporarilyUnavailable",
            "insufficientPermission",
            "loginRequired",
        ):
            if (
                self.url.unsecretURL()
                in self.subscription.parent._updatingSubscriptions
            ):
                self.subscription.parent._updatingSubscriptions.remove(
                    self.url.unsecretURL()
                )
            self.subscription._updatingProblem = [
                f"#(response.{api.response})",
                f"#(response.{api.response}.headline)",
            ]
            return (
                False,
                [f"#(response.{api.response})", f"#(response.{api.response}.headline)"],
                False,
            )

        # # Detect installed fonts now not available in subscription anymore and delete
        # them
        # hasFonts = False
        # removeFonts = []
        # if api.response == NOFONTSAVAILABLE:
        # 	for foundry in self._installableFontsCommand.foundries:
        # 		for family in foundry.families:
        # 			for font in family.fonts:
        # 				hasFonts = True
        # 				removeFonts.append(font.uniqueID)
        # 	if removeFonts:
        # 		success, message = self.subscription.removeFonts(removeFonts)
        # 		if not success:
        # 			return False, 'Couldn’t uninstall previously installed fonts: %s' %
        # message, True

        # Previously available fonts
        oldIDs = []
        for foundry in self._installableFontsCommand.foundries:
            for family in foundry.families:
                for font in family.fonts:
                    oldIDs.append(font.uniqueID)

        # Newly available fonts
        newIDs = []
        for foundry in api.foundries:
            for family in foundry.families:
                for font in family.fonts:
                    newIDs.append(font.uniqueID)

        # These fonts are no longer available, so delete them.
        # Shrink the list of deletable fonts to the ones actually installed.
        deletedFonts = list(set(oldIDs) - set(newIDs))
        deleteTheseFonts = []
        if deletedFonts:
            for fontID in deletedFonts:
                for foundry in self._installableFontsCommand.foundries:
                    for family in foundry.families:
                        for font in family.fonts:
                            if font.uniqueID == fontID:
                                if self.subscription.installedFontVersion(
                                    font.uniqueID
                                ):
                                    deleteTheseFonts.append(fontID)

            success, message = self.subscription.removeFonts(
                deleteTheseFonts, updateSubscription=False
            )
            if not success:
                return (
                    False,
                    "Couldn’t uninstall previously installed fonts: %s" % message,
                    True,
                )

        # Compare
        identical = self._installableFontsCommand.sameContent(api)
        self._installableFontsCommand = api

        # EndpointResponse
        if root.endpoint:
            self._rootCommand = root.endpoint

        # InstallFontsResponse
        if root.installFonts:
            self._installFontsCommand = root.installFonts
        else:
            self._installFontsCommand = None

        self.save()

        return True, None, not identical

    def setInstallableFontsCommand(self, command):
        self._installableFontsCommand = command

    # 		self.client.delegate.subscriptionWasUpdated(self.subscription.parent,
    # self.subscription)

    def removeFonts(self, fonts, updateSubscription=False):

        data = {
            "fonts": ",".join(fonts),
            "anonymousAppID": self.client.anonymousAppID(),
            "anonymousTypeWorldUserID": self.client.user(),
            "subscriptionID": self.url.subscriptionID,
            "secretKey": self.getSecretKey(),
            "secretTypeWorldAPIKey": self.client.secretTypeWorldAPIKey,
            "appVersion": VERSION,
            "mothership": self.client.mothership,
        }
        if self.client.testScenario:
            data["testScenario"] = self.client.testScenario
        if self.client.testing:
            data["testing"] = "true"

        commands = [typeworld.api.UninstallFontsResponse()]
        if updateSubscription:
            commands.append(typeworld.api.InstallableFontsResponse())

        root, messages = readJSONResponse(
            self.connectURL(),
            commands,
            typeworld.api.UNINSTALLFONTSCOMMAND["acceptableMimeTypes"],
            data=data,
        )
        api = root.uninstallFonts

        if messages["errors"]:
            return False, "\n\n".join(messages["errors"])

        if api.response == "error":
            return False, api.errorMessage

        if api.response != "success":
            return (
                False,
                [f"#(response.{api.response})", f"#(response.{api.response}.headline)"],
            )

        if (
            updateSubscription
            and root.installableFonts
            and root.installableFonts.response == "success"
        ):
            self.setInstallableFontsCommand(root.installableFonts)

        return True, api

    def installFonts(self, fonts, updateSubscription=False):

        # Build URL

        if self._installFontsCommand:
            return True, self._installFontsCommand

        else:

            data = {
                "fonts": ",".join([f"{x[0]}/{x[1]}" for x in fonts]),
                "anonymousAppID": self.client.anonymousAppID(),
                "anonymousTypeWorldUserID": self.client.user(),
                "subscriptionID": self.url.subscriptionID,
                "secretKey": self.getSecretKey(),
                "secretTypeWorldAPIKey": self.client.secretTypeWorldAPIKey,
                "appVersion": VERSION,
                "mothership": self.client.mothership,
            }
            if self.client.testScenario:
                data["testScenario"] = self.client.testScenario
            if self.client.testing:
                data["testing"] = "true"

            if self.subscription.get("revealIdentity") and self.client.userName():
                data["userName"] = self.client.userName()
            if self.subscription.get("revealIdentity") and self.client.userEmail():
                data["userEmail"] = self.client.userEmail()

            commands = [typeworld.api.InstallFontsResponse()]
            if updateSubscription:
                commands.append(typeworld.api.InstallableFontsResponse())

            root, messages = readJSONResponse(
                self.connectURL(),
                commands,
                typeworld.api.INSTALLFONTSCOMMAND["acceptableMimeTypes"],
                data=data,
            )
            api = root.installFonts

            if messages["errors"]:
                return False, "\n\n".join(messages["errors"])

            if api.response == "error":
                return False, api.errorMessage

            if api.response != "success":
                return (
                    False,
                    [
                        f"#(response.{api.response})",
                        f"#(response.{api.response}.headline)",
                    ],
                )

            if (
                updateSubscription
                and root.installableFonts
                and root.installableFonts.response == "success"
            ):
                self.setInstallableFontsCommand(root.installableFonts)

            return True, api

    def aboutToAddSubscription(
        self,
        anonymousAppID,
        anonymousTypeWorldUserID,
        accessToken,
        secretTypeWorldAPIKey,
        testScenario,
    ):
        """Overwrite this.
        Put here an initial health check of the subscription. Check if URLs point to the
        right place etc.
        Return False, 'message' in case of errors."""

        # Read response
        data = {
            "subscriptionID": self.url.subscriptionID,
            "secretKey": self.url.secretKey,
            "anonymousAppID": anonymousAppID,
            "anonymousTypeWorldUserID": anonymousTypeWorldUserID,
            "accessToken": accessToken,
            "appVersion": VERSION,
            "mothership": self.client.mothership,
        }
        if testScenario:
            data["testScenario"] = testScenario
        if self.client.testing:
            data["testing"] = "true"

        root, responses = readJSONResponse(
            self.connectURL(),
            [
                typeworld.api.EndpointResponse(),
                typeworld.api.InstallableFontsResponse(),
            ],
            typeworld.api.INSTALLABLEFONTSCOMMAND["acceptableMimeTypes"],
            data=data,
        )

        # InstallableFontsResponse
        api = root.installableFonts

        # EndpointResponse
        self._rootCommand = root.endpoint

        # Errors
        if responses["errors"]:
            return False, responses["errors"][0]

        if (
            "installableFonts" not in self._rootCommand.supportedCommands
            or "installFonts" not in self._rootCommand.supportedCommands
        ):
            return (
                False,
                (
                    "API endpoint %s does not support the 'installableFonts' or "
                    "'installFonts' commands."
                )
                % self._rootCommand.canonicalURL,
            )

        if api.response == "error":
            return False, api.errorMessage

        # Predefined response messages
        if api.response != "error" and api.response != "success":
            return (
                False,
                [
                    "#(response.%s)" % api.response,
                    "#(response.%s.headline)" % api.response,
                ],
            )

        # Success
        self._installableFontsCommand = api

        # InstallFontsResponse
        if root.installFonts:
            self._installFontsCommand = root.installFonts
        else:
            self._installFontsCommand = None

        if self.url.secretKey:
            self.setSecretKey(self.url.secretKey)

        return True, None

    def save(self):

        assert self._rootCommand
        self.set("endpoint", self._rootCommand.dumpJSON())

        assert self._installableFontsCommand
        self.set("installableFonts", self._installableFontsCommand.dumpJSON())

        if self._installFontsCommand:
            self.set("installFonts", self._installFontsCommand.dumpJSON())
        else:
            self.set("installFonts", "")
