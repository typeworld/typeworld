import typeworld.client.protocols
import typeworld.api
import requests
import requests.exceptions
from typeworld.api import VERSION


def readJSONResponse(url, responses, acceptableMimeTypes, data={}):
    d = {}
    d["errors"] = []
    d["warnings"] = []
    d["information"] = []

    root = typeworld.api.RootResponse()

    if "source" not in data:
        data["source"] = "typeworldApp"

    # gather commands
    commands = [response._command["keyword"] for response in responses]
    data["commands"] = ",".join(commands)

    try:
        response = requests.post(url, data, timeout=30)
    except requests.exceptions.ConnectionError:
        d["errors"].append(f"Connection refused: {url}")
        return root, d
    except requests.exceptions.HTTPError:
        d["errors"].append(f"HTTP Error: {url}")
        return root, d
    except requests.exceptions.Timeout:
        d["errors"].append(f"Connection timed out: {url}")
        return root, d
    except requests.exceptions.TooManyRedirects:
        d["errors"].append(f"Too many redirects: {url}")
        return root, d

    if response.status_code != 200:
        d["errors"].append(f"HTTP Error {response.status_code}")

    if response.status_code == 200:

        incomingMIMEType = response.headers["content-type"].split(";")[0]
        if incomingMIMEType not in acceptableMimeTypes:
            d["errors"].append(
                "Resource headers returned wrong MIME type: '%s'. Expected is '%s'."
                % (response.headers["content-type"], acceptableMimeTypes)
            )

        # Catching ValueErrors
        try:
            root.loadJSON(response.text)
            information, warnings, errors = root.validate()

            if information:
                d["information"].extend(information)
            if warnings:
                d["warnings"].extend(warnings)
            if errors:
                d["errors"].extend(errors)
        except ValueError as e:
            d["errors"].append(str(e))

    return root, d


class TypeWorldProtocol(typeworld.client.protocols.TypeWorldProtocolBase):
    def initialize(self):
        self.versions = []
        self._endpointCommand = None
        self._installableFontsCommand = None
        self._installFontsCommand = None

    def loadFromDB(self):
        """Overwrite this"""

        if self.get("endpoint"):
            api = typeworld.api.EndpointResponse()
            api.parent = self
            api.loadJSON(self.get("endpoint"))
            self._endpointCommand = api

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

            self._endpointCommand = root.endpoint
            self._rootCommand = root

        # Success
        return True, self._rootCommand

    def returnEndpointCommand(self, testScenario):

        if not self._endpointCommand:

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

            self._endpointCommand = root.endpoint
            self._rootCommand = root

        # Success
        return True, self._endpointCommand

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

        if responses["errors"]:

            if self.url.unsecretURL() in self.subscription.parent._updatingSubscriptions:
                self.subscription.parent._updatingSubscriptions.remove(self.url.unsecretURL())
            self.subscription._updatingProblem = "\n".join(responses["errors"])
            return False, self.subscription._updatingProblem, False

        if root.installableFonts.response == "error":
            if self.url.unsecretURL() in self.subscription.parent._updatingSubscriptions:
                self.subscription.parent._updatingSubscriptions.remove(self.url.unsecretURL())
            self.subscription._updatingProblem = root.installableFonts.errorMessage
            return False, self.subscription._updatingProblem, False

        if root.installableFonts.response in (
            "temporarilyUnavailable",
            "insufficientPermission",
            "loginRequired",
        ):
            if self.url.unsecretURL() in self.subscription.parent._updatingSubscriptions:
                self.subscription.parent._updatingSubscriptions.remove(self.url.unsecretURL())
            self.subscription._updatingProblem = [
                f"#(response.{root.installableFonts.response})",
                f"#(response.{root.installableFonts.response}.headline)",
            ]
            return (
                False,
                [
                    f"#(response.{root.installableFonts.response})",
                    f"#(response.{root.installableFonts.response}.headline)",
                ],
                False,
            )

        # Security check: Does url begin with canonicalURL?
        if not self.url.HTTPURL().startswith(root.endpoint.canonicalURL):
            return False, "'url' must begin with 'canonicalURL'", None

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
        for foundry in root.installableFonts.foundries:
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
                                if self.subscription.installedFontVersion(font.uniqueID):
                                    deleteTheseFonts.append(fontID)

            success, message = self.subscription.removeFonts(deleteTheseFonts, updateSubscription=False)
            if not success:
                return (
                    False,
                    "Couldn’t uninstall previously installed fonts: %s" % message,
                    True,
                )

        # Compare
        changes = self._installableFontsCommand.getContentChanges(root.installableFonts)

        # Success
        self._installableFontsCommand = root.installableFonts

        # EndpointResponse
        if root.endpoint:
            self._endpointCommand = root.endpoint

        # InstallFontsResponse
        if root.installFonts:
            self._installFontsCommand = root.installFonts
        else:
            self._installFontsCommand = None

        self.save()

        return True, None, changes

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
            "APIKey": self.client.secretTypeWorldAPIKey,
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

        if updateSubscription and root.installableFonts and root.installableFonts.response == "success":
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
                "APIKey": self.client.secretTypeWorldAPIKey,
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

            if updateSubscription and root.installableFonts and root.installableFonts.response == "success":
                self.setInstallableFontsCommand(root.installableFonts)

            return True, api

    def aboutToAddSubscription(
        self,
        anonymousAppID,
        anonymousTypeWorldUserID,
        accessToken,
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
            "APIKey": self.client.secretTypeWorldAPIKey,
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

        # Errors
        if responses["errors"]:
            return False, responses["errors"][0]

        if (
            "installableFonts" not in root.endpoint.supportedCommands
            or "installFonts" not in root.endpoint.supportedCommands
        ):
            return (
                False,
                "API endpoint %s does not support the 'installableFonts' and 'installFonts' commands."
                % root.endpoint.canonicalURL,
            )

        if root.installableFonts.response == "error":
            if root.installableFonts.errorMessage:
                return False, root.installableFonts.errorMessage
            else:
                return False, "api.response is error, but no error message was given"

        # Predefined response messages
        if root.installableFonts.response != "error" and root.installableFonts.response != "success":
            return (
                False,
                [
                    "#(response.%s)" % root.installableFonts.response,
                    "#(response.%s.headline)" % root.installableFonts.response,
                ],
            )

        # Security check: Does url begin with canonicalURL?
        if not self.url.HTTPURL().startswith(root.endpoint.canonicalURL):
            return False, "'url' must begin with 'canonicalURL'"

        # Success
        self._rootCommand = root
        self._endpointCommand = root.endpoint
        self._installableFontsCommand = root.installableFonts

        # InstallFontsResponse
        if root.installFonts:
            self._installFontsCommand = root.installFonts
        else:
            self._installFontsCommand = None

        if self.url.secretKey:
            self.setSecretKey(self.url.secretKey)

        return True, None

    def save(self):

        assert self._endpointCommand
        self.set("endpoint", self._endpointCommand.dumpJSON(validate=False))

        assert self._installableFontsCommand
        self.set("installableFonts", self._installableFontsCommand.dumpJSON(validate=False))

        if self._installFontsCommand:
            self.set("installFonts", self._installFontsCommand.dumpJSON(validate=False))
        else:
            self.set("installFonts", "")
