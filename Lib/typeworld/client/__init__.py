# -*- coding: utf-8 -*-

import os
import sys
import json
import copy
import platform
import urllib.request
import urllib.error
import urllib.parse
import traceback
import time
import base64
import threading
import ssl
import certifi
import semver
import logging
import inspect
import re
from time import gmtime, strftime
import http.client as httplib
import requests

import typeworld.api

from typeworld.client.helpers import (
    ReadFromFile,
    WriteToFile,
    MachineName,
    OSName,
    Garbage,
    install_font,
    uninstall_font,
)


WIN = platform.system() == "Windows"
MAC = platform.system() == "Darwin"
LINUX = platform.system() == "Linux"
CI = os.getenv("CI", "false").lower() == "true"
GAE = os.getenv("GAE_ENV", "").startswith("standard")

MOTHERSHIP = "https://api.type.world/v1"

if MAC:
    from AppKit import NSUserDefaults
    from typeworld.client.helpers import nslog


class DummyKeyring(object):
    def __init__(self):
        self.passwords = {}

    def set_password(self, key, username, password):
        self.passwords[(key, username)] = password

    def get_password(self, key, username):
        if (key, username) in self.passwords:
            return self.passwords[(key, username)]

    def delete_password(self, key, username):
        if (key, username) in self.passwords:
            del self.passwords[(key, username)]


dummyKeyRing = DummyKeyring()
if "TRAVIS" in os.environ:
    import tempfile

    tempFolder = tempfile.mkdtemp()


def urlIsValid(url):

    if not url.find("typeworld://") < url.find("+") < url.find("http") < url.find("//", url.find("http")):
        return False, "URL is malformed."

    if url.count("@") > 1:
        return (
            False,
            "URL contains more than one @ sign, so don’t know how to parse it.",
        )

    found = False
    for protocol in typeworld.api.PROTOCOLS:
        if url.startswith(protocol + "://"):
            found = True
            break
    if not found:
        return (
            False,
            "Unknown custom protocol, known are: %s" % (typeworld.api.PROTOCOLS),
        )

    if url.count("://") > 1:
        return (
            False,
            "URL contains more than one :// combination, so don’t know how to parse it.",
        )

    return True, None


class URL(object):
    def __init__(self, url):
        (
            self.customProtocol,
            self.protocol,
            self.transportProtocol,
            self.subscriptionID,
            self.secretKey,
            self.accessToken,
            self.restDomain,
        ) = splitJSONURL(url)

    def unsecretURL(self):

        if self.subscriptionID and self.secretKey:
            return (
                str(self.customProtocol)
                + str(self.protocol)
                + "+"
                + str(self.transportProtocol.replace("://", "//"))
                + str(self.subscriptionID)
                + ":"
                + "secretKey"
                + "@"
                + str(self.restDomain)
            )

        elif self.subscriptionID:
            return (
                str(self.customProtocol)
                + str(self.protocol)
                + "+"
                + str(self.transportProtocol.replace("://", "//"))
                + str(self.subscriptionID)
                + "@"
                + str(self.restDomain)
            )

        else:
            return (
                str(self.customProtocol)
                + str(self.protocol)
                + "+"
                + str(self.transportProtocol.replace("://", "//"))
                + str(self.restDomain)
            )

    def shortUnsecretURL(self):

        if self.subscriptionID:
            return (
                str(self.customProtocol)
                + str(self.protocol)
                + "+"
                + str(self.transportProtocol.replace("://", "//"))
                + str(self.subscriptionID)
                + "@"
                + str(self.restDomain)
            )

        else:
            return (
                str(self.customProtocol)
                + str(self.protocol)
                + "+"
                + str(self.transportProtocol.replace("://", "//"))
                + str(self.restDomain)
            )

    def secretURL(self):

        if self.subscriptionID and self.secretKey:
            return (
                str(self.customProtocol)
                + str(self.protocol)
                + "+"
                + str(self.transportProtocol.replace("://", "//"))
                + str(self.subscriptionID)
                + ":"
                + str(self.secretKey)
                + "@"
                + str(self.restDomain)
            )

        elif self.subscriptionID:
            return (
                str(self.customProtocol)
                + str(self.protocol)
                + "+"
                + str(self.transportProtocol.replace("://", "//"))
                + str(self.subscriptionID)
                + "@"
                + str(self.restDomain)
            )

        else:
            return (
                str(self.customProtocol)
                + str(self.protocol)
                + "+"
                + str(self.transportProtocol.replace("://", "//"))
                + str(self.restDomain)
            )

    def HTTPURL(self):
        return str(self.transportProtocol) + str(self.restDomain)


def getProtocol(url):
    """\
    Loads a protocol plugin from the file system and returns an
    instantiated protocol object
    """

    protocolName = URL(url).protocol

    for ext in (".py", ".pyc"):
        if os.path.exists(os.path.join(os.path.dirname(__file__), "protocols", protocolName + ext)):

            import importlib

            spec = importlib.util.spec_from_file_location(
                "json",
                os.path.join(os.path.dirname(__file__), "protocols", protocolName + ext),
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            protocolObject = module.TypeWorldProtocol(url)

            return True, protocolObject

    return False, "Protocol %s doesn’t exist in this app (yet)." % protocolName


def request(url, parameters={}, method="POST", timeout=30):
    """Perform request in a loop 10 times, because the central server’s instance might
    shut down unexpectedly during a request, especially longer running ones."""

    message = None
    tries = 10

    # status_code = None
    # content = None
    # headers = None

    for i in range(tries):

        try:
            if method == "POST":
                request = requests.post(url, parameters, timeout=timeout)
            elif method == "GET":
                request = requests.get(url, timeout=timeout)
            content = request.content
            status_code = request.status_code
            headers = request.headers
        except Exception:

            # Continue the loop directly unless this is last round
            if i < tries - 1:
                continue

            # Output error message
            if parameters:
                parameters = copy.copy(parameters)
                for key in parameters:
                    if key.lower().endswith("key"):
                        parameters[key] = "*****"
                    if key.lower().endswith("secret"):
                        parameters[key] = "*****"
                message = (
                    f"Response from {url} with parameters {parameters} after {i+1} tries: "
                    + traceback.format_exc().splitlines()[-1]
                )
            else:
                message = traceback.format_exc().splitlines()[-1]

            return False, message, {"status_code": None, "headers": None}

        if status_code == 200:
            return True, content, {"status_code": status_code, "headers": headers}
        else:
            return False, f"HTTP Error {status_code}", {"status_code": status_code, "headers": headers}


def splitJSONURL(url):

    customProtocol = "typeworld://"
    url = url.replace(customProtocol, "")

    protocol = url.split("+")[0]
    url = url.replace(protocol + "+", "")

    url = url.replace("http//", "http://")
    url = url.replace("https//", "https://")
    url = url.replace("HTTP//", "http://")
    url = url.replace("HTTPS//", "https://")

    transportProtocol = None
    if url.startswith("https://"):
        transportProtocol = "https://"
    elif url.startswith("http://"):
        transportProtocol = "http://"

    urlRest = url[len(transportProtocol) :]

    subscriptionID = ""
    secretKey = ""
    accessToken = ""

    # With credentials
    if "@" in urlRest:

        credentials, domain = urlRest.split("@")
        credentialParts = credentials.split(":")

        if len(credentialParts) == 3:
            subscriptionID, secretKey, accessToken = credentialParts

        elif len(credentialParts) == 2:
            subscriptionID, secretKey = credentialParts

        elif len(credentialParts) == 1:
            subscriptionID = credentialParts[0]

    # No credentials given
    else:
        domain = urlRest

    return (
        customProtocol,
        protocol,
        transportProtocol,
        subscriptionID,
        secretKey,
        accessToken,
        domain,
    )


class Preferences(object):
    def __init__(self):
        self._dict = {}  # nocoverage
        # (In tests, preferences are loaded either as JSON or as AppKitNSUserDefaults,
        # not the plain class here)

    def get(self, key):
        if key in self._dict:
            return self._dict[key]

    def set(self, key, value):
        self._dict[key] = value
        self.save()

    def remove(self, key):
        if key in self._dict:
            del self._dict[key]
        self.save()

    def save(self):
        pass

    def dictionary(self):
        return self._dict  # nocoverage
        # (In tests, preferences are loaded either as JSON or as AppKitNSUserDefaults,
        # not the plain class here)


class JSON(Preferences):
    def __init__(self, path):
        self.path = path
        self._dict = {}

        if self.path and os.path.exists(self.path):
            self._dict = json.loads(ReadFromFile(self.path))

    def save(self):

        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        WriteToFile(self.path, json.dumps(self._dict))

    def dictionary(self):
        return self._dict


class AppKitNSUserDefaults(Preferences):
    def __init__(self, name):
        # 		NSUserDefaults = objc.lookUpClass('NSUserDefaults')
        self.defaults = NSUserDefaults.alloc().initWithSuiteName_(name)
        self.values = {}

    def get(self, key):

        if key in self.values:
            return self.values[key]

        else:

            o = self.defaults.objectForKey_(key)

            if o:

                if "Array" in o.__class__.__name__:
                    o = list(o)

                elif "Dictionary" in o.__class__.__name__:
                    o = dict(o)

                elif "unicode" in o.__class__.__name__:
                    o = str(o)

                self.values[key] = o
                return self.values[key]

    def set(self, key, value):

        # 		self.defaults.setObject_forKey_(json.dumps(value), key)

        # if MAC:
        # 	if type(value) == dict:
        # 		value = NSDictionary.alloc().initWithDictionary_(value)

        self.values[key] = value
        self.defaults.setObject_forKey_(value, key)

    def remove(self, key):
        if key in self.values:
            del self.values[key]

        if self.defaults.objectForKey_(key):
            self.defaults.removeObjectForKey_(key)

    def convertItem(self, item):

        if "Array" in item.__class__.__name__ or type(item) in (list, tuple):
            _list = list(item)
            for i, _item in enumerate(_list):
                _list[i] = self.convertItem(_item)
            return _list

        elif "Dictionary" in item.__class__.__name__ or type(item) == dict:
            d = dict(item)
            for k, v in d.items():
                d[k] = self.convertItem(v)

            return d

        elif "unicode" in item.__class__.__name__:
            return str(item)

    def dictionary(self):

        d = self.defaults.dictionaryRepresentation()
        return self.convertItem(d)


class TypeWorldClientDelegate(object):
    def __init__(self):
        self.client = None
        self.initialize()

    def initialize(self):
        pass

    def _fontWillInstall(self, font):
        try:
            self.fontWillInstall(font)
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def fontWillInstall(self, font):
        assert type(font) == typeworld.api.Font

    def _fontHasInstalled(self, success, message, font):
        try:
            self.fontHasInstalled(success, message, font)
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def fontHasInstalled(self, success, message, font):
        if success:
            assert type(font) == typeworld.api.Font

    def _fontWillUninstall(self, font):
        try:
            self.fontWillUninstall(font)
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def fontWillUninstall(self, font):
        assert type(font) == typeworld.api.Font

    def _fontHasUninstalled(self, success, message, font):
        try:
            self.fontHasUninstalled(success, message, font)
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def fontHasUninstalled(self, success, message, font):
        if success:
            assert type(font) == typeworld.api.Font

    def _subscriptionUpdateNotificationHasBeenReceived(self, subscription):
        try:
            self.subscriptionUpdateNotificationHasBeenReceived(subscription)
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def subscriptionUpdateNotificationHasBeenReceived(self, subscription):
        assert type(subscription) == typeworld.client.APISubscription
        pass

    # def _subscriptionInvitationHasBeenReceived(self, invitation):
    #     try:
    #         self.subscriptionInvitationHasBeenReceived(invitation)
    #     except Exception:  # nocoverage
    #         self.client.handleTraceback(  # nocoverage
    #             sourceMethod=getattr(self, sys._getframe().f_code.co_name)
    #         )

    # def subscriptionInvitationHasBeenReceived(self, invitation):
    #     pass

    def _userAccountUpdateNotificationHasBeenReceived(self):
        try:
            self.userAccountUpdateNotificationHasBeenReceived()
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def userAccountUpdateNotificationHasBeenReceived(self):
        pass

    def _userAccountHasBeenUpdated(self):
        try:
            self.userAccountHasBeenUpdated()
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def userAccountHasBeenUpdated(self):
        pass

    def _userAccountIsReloading(self):
        try:
            self.userAccountIsReloading()
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def userAccountIsReloading(self):
        pass

    def _userAccountHasReloaded(self):
        try:
            self.userAccountHasReloaded()
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def userAccountHasReloaded(self):
        pass

    def _subscriptionWillDelete(self, subscription):
        try:
            self.subscriptionWillDelete(subscription)
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def subscriptionWillDelete(self, subscription):
        pass

    def _subscriptionHasBeenDeleted(self, subscription, withinPublisherDeletion=False, remotely=False):
        try:
            self.subscriptionHasBeenDeleted(subscription, withinPublisherDeletion, remotely)
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def subscriptionHasBeenDeleted(self, subscription, withinPublisherDeletion, remotely):
        pass

    def _publisherWillDelete(self, publisher):
        try:
            self.publisherWillDelete(publisher)
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def publisherWillDelete(self, publisher):
        pass

    def _publisherHasBeenDeleted(self, publisher):
        try:
            self.publisherHasBeenDeleted(publisher)
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def publisherHasBeenDeleted(self, publisher):
        pass

    def _subscriptionHasBeenAdded(self, subscription, remotely=False):
        try:
            self.subscriptionHasBeenAdded(subscription, remotely)
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def subscriptionHasBeenAdded(self, subscription, remotely):
        pass

    def _subscriptionWillUpdate(self, subscription):
        try:
            self.subscriptionWillUpdate(subscription)
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def subscriptionWillUpdate(self, subscription):
        pass

    def _subscriptionHasBeenUpdated(self, subscription, success, message, changes):
        try:
            self.subscriptionHasBeenUpdated(subscription, success, message, changes)
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def subscriptionHasBeenUpdated(self, subscription, success, message, changes):
        pass

    def _clientPreferenceChanged(self, key, value):
        try:
            self.clientPreferenceChanged(key, value)
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def clientPreferenceChanged(self, key, value):
        pass

    def _messageQueueConnected(self):
        try:
            self.messageQueueConnected()
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def messageQueueConnected(self):
        pass

    def _messageQueueError(self, status=None):
        try:
            self.messageQueueError(status=status)

        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def messageQueueError(self, status=None):
        pass

    def _messageQueueLostConnection(self):
        try:
            self.messageQueueLostConnection()
            self.client.zmqRestart()

        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def messageQueueLostConnection(self):
        pass

    def _messageQueueDisconnected(self):
        try:
            self.messageQueueDisconnected()
        except Exception:  # nocoverage
            self.client.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))  # nocoverage

    def messageQueueDisconnected(self):
        pass


class APIInvitation(object):
    keywords = ()

    def __init__(self, d):
        for key in self.keywords:
            # if key in d:
            setattr(self, key, d[key])
            # else:
            # 	setattr(self, key, None)


class APIPendingInvitation(APIInvitation):
    keywords = (
        "url",
        "ID",
        "invitedByUserName",
        "invitedByUserEmail",
        "time",
        "canonicalURL",
        "publisherName",
        "subscriptionName",
        "logoURL",
        "backgroundColor",
        "fonts",
        "families",
        "foundries",
        "websiteURL",
    )

    def accept(self):
        return self.parent.acceptInvitation(self.url)

    def decline(self):
        return self.parent.declineInvitation(self.url)


class APIAcceptedInvitation(APIInvitation):
    keywords = (
        "url",
        "ID",
        "invitedByUserName",
        "invitedByUserEmail",
        "time",
        "canonicalURL",
        "publisherName",
        "subscriptionName",
        "logoURL",
        "backgroundColor",
        "fonts",
        "families",
        "foundries",
        "websiteURL",
    )


class APISentInvitation(APIInvitation):
    keywords = (
        "url",
        "invitedUserName",
        "invitedUserEmail",
        "invitedTime",
        "acceptedTime",
        "confirmed",
    )


class APIClient(object):
    """\
    Main Type.World client app object.
    Use it to load repositories and install/uninstall fonts.
    """

    def __init__(
        self,
        preferences=None,
        secretTypeWorldAPIKey=None,
        delegate=None,
        mothership=None,
        mode="headless",
        zmqSubscriptions=False,
        online=False,
        testing=False,
        externallyControlled=False,
        secretServerAuthKey=None,
        inCompiledApp=False,
        commercial=False,
        appID="world.type.headless",
    ):

        try:
            self._preferences = preferences or Preferences()
            # if self:
            # 	self.clearPendingOnlineCommands()
            self._publishers = {}
            self._subscriptionsUpdated = []
            self.onlineCommandsQueue = []
            self._syncProblems = []
            self.secretTypeWorldAPIKey = secretTypeWorldAPIKey
            self.delegate = delegate or TypeWorldClientDelegate()
            self.delegate.client = self
            self.mothership = mothership or MOTHERSHIP
            self.mode = mode  # gui or headless
            self.zmqSubscriptions = zmqSubscriptions
            self._isSetOnline = online
            self.lastOnlineCheck = {}
            self.testing = testing
            self.externallyControlled = externallyControlled
            self.secretServerAuthKey = secretServerAuthKey
            self.inCompiledApp = inCompiledApp
            self.commercial = commercial
            self.appID = appID

            self._zmqRunning = False
            self._zmqCallbacks = {}
            self._zmqStatus = None

            self.sslcontext = ssl.create_default_context(cafile=certifi.where())

            # For Unit Testing
            self.testScenario = None

            self._systemLocale = None
            self._online = {}

            # wentOnline()
            if self._isSetOnline and not self.externallyControlled:
                self.wentOnline()

            # ZMQ
            if self._isSetOnline and self.zmqSubscriptions:
                if self.user():
                    topicID = "user-%s" % self.user()
                    self.registerZMQCallback(topicID, self.zmqCallback)
                self.manageMessageQueueConnection()

            #
            # Version-dependent startup procedures
            #

            # 0.2.10 or newer
            if semver.VersionInfo.parse(typeworld.api.VERSION).compare("0.2.10-beta") >= 0:
                # Delete all resources
                for publisher in self.publishers():
                    for subscription in publisher.subscriptions():
                        subscription.remove("resources")
                self.remove("resources")

        except Exception as e:  # nocoverage
            self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def __repr__(self):
        return f'<APIClient user="{self.user()}">'

    def tracebackTest(self):
        try:
            assert abc  # noqa: F821

        except Exception as e:
            self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)

    def tracebackTest2(self):
        try:
            assert abc  # noqa: F821

        except Exception:
            self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name))

    def wentOnline(self):
        success, message = self.downloadSettings(performCommands=True)
        assert success
        assert self.get("downloadedSettings")["messagingQueue"].startswith("tcp://")
        assert self.get("downloadedSettings")["breakingAPIVersions"]
        print(self.get("downloadedSettings"))

    def wentOffline(self):
        pass

    def zmqRestart(self):
        self.zmqQuit()
        self.wentOnline()
        self.zmqSetup()
        self.reRegisterZMQCallbacks()

    def zmqSetup(self):
        import zmq
        import zmq.error

        if not self._zmqRunning:
            self._zmqctx = zmq.Context.instance()
            self.zmqSocket = self._zmqctx.socket(zmq.SUB)

            # https://github.com/zeromq/libzmq/issues/2882
            self.zmqSocket.setsockopt(zmq.TCP_KEEPALIVE, 1)
            self.zmqSocket.setsockopt(zmq.TCP_KEEPALIVE_CNT, 10)
            self.zmqSocket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 30)
            self.zmqSocket.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 30)

            target = self.get("downloadedSettings")["messagingQueue"]
            self.zmqSocket.connect(target)

            self._zmqRunning = True
            self.zmqListenerThread = threading.Thread(target=self.zmqListener, daemon=True)
            self.zmqListenerThread.start()

            # MONITOR
            self._zmqMonitor = self.zmqSocket.get_monitor_socket()
            self.zmqMonitorThread = threading.Thread(
                target=self.event_monitor,
                args=(self._zmqMonitor,),
                daemon=True,
            )
            self.zmqMonitorThread.start()

    def event_monitor(self, monitor):
        import zmq
        from zmq.utils.monitor import recv_monitor_message
        import zmq.error

        EVENT_MAP = {}
        for name in dir(zmq):
            if name.startswith("EVENT_"):
                value = getattr(zmq, name)
                # print("%21s : %4i" % (name, value))
                EVENT_MAP[value] = name

        # Store these events:
        error = [
            "EVENT_CLOSED",
            "EVENT_CONNECT_RETRIED",
            "EVENT_CONNECT_DELAYED",
        ]
        lostConnection = [
            "EVENT_DISCONNECTED",
            "EVENT_CLOSED",
        ]
        connected = ["EVENT_HANDSHAKE_SUCCEEDED"]

        try:
            while monitor.poll():
                evt = recv_monitor_message(monitor)
                status = EVENT_MAP[evt["event"]]
                if status in error:
                    self.delegate._messageQueueError(status=status)
                if status in lostConnection:
                    zmqRestartThread = threading.Thread(target=self.delegate._messageQueueLostConnection, daemon=True)
                    zmqRestartThread.start()
                    # self.delegate._messageQueueLostConnection()
                if status in connected:
                    self.delegate._messageQueueConnected()

                evt.update({"description": status})
                # print("Event: {}".format(evt))

                if evt["event"] == zmq.EVENT_MONITOR_STOPPED:
                    break

        except zmq.error.ZMQError:
            pass
        monitor.close()
        # print("event monitor thread done!")

    def zmqListener(self):
        import zmq
        import zmq.error

        while self._zmqRunning:
            time.sleep(0.1)
            try:
                topic, msg = self.zmqSocket.recv_multipart(flags=zmq.NOBLOCK)
                topic = topic.decode()
                msg = msg.decode()

                if topic in self._zmqCallbacks:
                    self._zmqCallbacks[topic](msg)
            except zmq.Again:
                pass
            except zmq.error.ZMQError:
                pass

    def quit(self):
        self.zmqQuit()

    def zmqQuit(self):
        if self._zmqRunning:
            # for topic in self._zmqCallbacks:
            #     self.zmqSocket.setsockopt(zmq.UNSUBSCRIBE, topic.encode("ascii"))
            self._zmqRunning = False
            self._zmqMonitor.close()
            self.zmqSocket.close()
            self._zmqctx.destroy()
            self.zmqListenerThread.join()
            self.zmqMonitorThread.join()
            # self._zmqctx.term()
            self.delegate._messageQueueDisconnected()

    def reRegisterZMQCallbacks(self):
        import zmq
        import zmq.error

        if self.zmqSubscriptions:
            for topic in self._zmqCallbacks:
                self.zmqSocket.setsockopt(zmq.SUBSCRIBE, topic.encode("ascii"))

    def registerZMQCallback(self, topic, method):
        import zmq
        import zmq.error

        if self.zmqSubscriptions:
            if self._zmqRunning and not self.zmqSocket.closed:
                self.zmqSocket.setsockopt(zmq.SUBSCRIBE, topic.encode("ascii"))
            self._zmqCallbacks[topic] = method

    def unregisterZMQCallback(self, topic):
        import zmq
        import zmq.error

        if self.zmqSubscriptions:
            if topic in self._zmqCallbacks:
                if self._zmqRunning and not self.zmqSocket.closed:
                    self.zmqSocket.setsockopt(zmq.UNSUBSCRIBE, topic.encode("ascii"))
                del self._zmqCallbacks[topic]

    def zmqCallback(self, message):
        try:

            if message:
                data = json.loads(message)
                if data["command"] == "pullUpdates" and (
                    "sourceAnonymousAppID" not in data
                    or (
                        "sourceAnonymousAppID" in data
                        and data["sourceAnonymousAppID"]
                        and data["sourceAnonymousAppID"] != self.anonymousAppID()
                    )
                ):
                    self.delegate._userAccountUpdateNotificationHasBeenReceived()

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    # def clearPendingOnlineCommands(self):
    # 	commands = self.get('pendingOnlineCommands') or {}
    # 	commands['acceptInvitation'] = []
    # 	commands['declineInvitation'] = []
    # 	commands['downloadSubscriptions'] = []
    # 	commands['linkUser'] = []
    # 	commands['syncSubscriptions'] = []
    # 	commands['unlinkUser'] = []
    # 	commands['uploadSubscriptions'] = []
    # 	self.set('pendingOnlineCommands', commands)

    def holdsSubscriptionWithLiveNotifcations(self):
        for publisher in self.publishers():
            for subscription in publisher.subscriptions():
                success, command = subscription.protocol.endpointCommand()
                if success:
                    if command.sendsLiveNotifications:
                        return True
        return False

    def requiresMessageQueueConnection(self):
        return (
            (self.user() and self.get("userAccountStatus") == "pro")
            or self.holdsSubscriptionWithLiveNotifcations()
            or self.testing
            # or self.testScenario == "simulateProAccount"
        )

    def manageMessageQueueConnection(self):
        import zmq
        import zmq.error

        if self._isSetOnline and self.zmqSubscriptions:
            requiresMessageQueueConnection = self.requiresMessageQueueConnection()

            if requiresMessageQueueConnection and not self._zmqRunning:
                self.zmqSetup()
                for topic in self._zmqCallbacks:
                    self.zmqSocket.setsockopt(zmq.SUBSCRIBE, topic.encode("ascii"))

            elif not requiresMessageQueueConnection and self._zmqRunning:
                self.zmqQuit()

    def get(self, key):
        try:
            return self._preferences.get("world.type.guiapp." + key) or self._preferences.get(key)
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def set(self, key, value):
        try:
            self._preferences.set("world.type.guiapp." + key, value)
            self.delegate._clientPreferenceChanged(key, value)
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def remove(self, key):
        try:
            self._preferences.remove("world.type.guiapp." + key)
            self._preferences.remove(key)
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def performRequest(self, url, parameters={}, method="POST"):

        try:
            parameters["sourceAnonymousAppID"] = self.anonymousAppID()
            parameters["clientVersion"] = typeworld.api.VERSION
            if self.testScenario == "simulateFaultyClientVersion":
                parameters["clientVersion"] = "abc"
            elif self.testScenario == "simulateNoClientVersion":
                del parameters["clientVersion"]

            if self.testing:
                parameters["testing"] = "true"

            # if self._isSetOnline:
            if self.testScenario:
                parameters["testScenario"] = self.testScenario
            if self.testScenario == "simulateCentralServerNotReachable":
                url = "https://api.type.worlddd/api"
            return request(url, parameters, method)
            # else:
            # 	return False, 'APIClient is set to work offline as set by:
            # APIClient(online=False)'

        except Exception as e:  # nocoverage
            success, message = self.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )
            return success, message, None

    def pendingInvitations(self):
        try:
            _list = []
            if self.get("pendingInvitations"):
                for invitation in self.get("pendingInvitations"):
                    invitation = APIPendingInvitation(invitation)
                    invitation.parent = self
                    _list.append(invitation)
            return _list
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def acceptedInvitations(self):
        try:
            _list = []
            if self.get("acceptedInvitations"):
                for invitation in self.get("acceptedInvitations"):
                    invitation = APIAcceptedInvitation(invitation)
                    invitation.parent = self
                    _list.append(invitation)
            return _list
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def sentInvitations(self):
        try:
            _list = []
            if self.get("sentInvitations"):
                for invitation in self.get("sentInvitations"):
                    invitation = APISentInvitation(invitation)
                    invitation.parent = self
                    _list.append(invitation)
            return _list
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def secretSubscriptionURLs(self):
        try:

            _list = []

            for publisher in self.publishers():
                for subscription in publisher.subscriptions():
                    _list.append(subscription.protocol.secretURL())

            return _list

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def unsecretSubscriptionURLs(self):
        try:
            _list = []

            for publisher in self.publishers():
                for subscription in publisher.subscriptions():
                    _list.append(subscription.protocol.unsecretURL())

            return _list
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def timezone(self):
        try:
            return strftime("%z", gmtime())
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def syncProblems(self):
        return self._syncProblems

    def addMachineIDToParameters(self, parameters):
        try:
            (
                machineModelIdentifier,
                machineHumanReadableName,
                machineSpecsDescription,
            ) = MachineName()

            if machineModelIdentifier:
                parameters["machineModelIdentifier"] = machineModelIdentifier

            if machineHumanReadableName:
                parameters["machineHumanReadableName"] = machineHumanReadableName

            if machineSpecsDescription:
                parameters["machineSpecsDescription"] = machineSpecsDescription

            import platform

            parameters["machineNodeName"] = platform.node()

            osName = OSName()
            if osName:
                parameters["machineOSVersion"] = osName

            return parameters

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def online(self, server=None):
        try:

            if self.testScenario == "simulateNotOnline":
                return False

            if "GAE_DEPLOYMENT_ID" in os.environ:
                return True  # nocoverage

            if not server:
                server = "type.world"

            if not server.startswith("http"):
                server = "http://" + server

            if server in self.lastOnlineCheck and type(self.lastOnlineCheck[server]) is float:
                if time.time() - self.lastOnlineCheck[server] < 10:
                    return True

            if server.startswith("http://"):
                server = server[7:]
            elif server.startswith("https://"):
                server = server[8:]

            # try:
            #     urllib.request.urlopen(server, context=self.sslcontext)  # Python 3.x
            # except urllib.error.URLError:
            #     return False

            conn = httplib.HTTPConnection(server, timeout=5)
            try:
                conn.request("HEAD", "/")
                conn.close()
                # return True
            except:  # noqa
                conn.close()
                return False

            # try:
            #     urllib2.urlopen(server, timeout=1)
            # except urllib2.URLError as err:
            #     return False

            # Do nothing if HTTP errors are returned, and let the subsequent methods
            # handle the details
            # except urllib.error.HTTPError:
            #     pass

            self.lastOnlineCheck[server] = time.time()
            return True

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def appendCommands(self, commandName, commandsList=["pending"]):
        try:

            # Set up data structure
            commands = self.get("pendingOnlineCommands")
            if not self.get("pendingOnlineCommands"):
                commands = {}
            # Init empty
            if commandName not in commands:
                commands[commandName] = []
            if (
                commandName in commands and len(commands[commandName]) == 0
            ):  # set anyway if empty because NSObject immutability
                commands[commandName] = []
            self.set("pendingOnlineCommands", commands)

            # Add commands to list
            commands = self.get("pendingOnlineCommands")
            if type(commandsList) in (str, int):
                commandsList = [commandsList]
            for commandListItem in commandsList:
                if commandListItem not in commands[commandName]:
                    commands[commandName] = list(commands[commandName])
                    commands[commandName].append(commandListItem)
            self.set("pendingOnlineCommands", commands)

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def performCommands(self):
        log = False

        if log:
            print()
            print("performCommands()")
            # for line in traceback.format_stack():
            #     print(line.strip())
        try:

            success, message = True, None
            self._syncProblems = []

            if self.online():

                self.delegate._userAccountIsReloading()

                commands = self.get("pendingOnlineCommands") or {}

                # unlinkUser
                if "unlinkUser" in commands and commands["unlinkUser"]:
                    success, message = self.performUnlinkUser()
                    if log:
                        print("unlinkUser")

                    if success:
                        commands["unlinkUser"] = []
                        self.set("pendingOnlineCommands", commands)

                    else:
                        self._syncProblems.append(message)

                # linkUser
                if "linkUser" in commands and commands["linkUser"]:
                    success, message = self.performLinkUser(commands["linkUser"][0])
                    if log:
                        print("linkUser")

                    if success:
                        commands["linkUser"] = []
                        self.set("pendingOnlineCommands", commands)

                    else:
                        self._syncProblems.append(message)

                # syncSubscriptions
                if "syncSubscriptions" in commands and commands["syncSubscriptions"]:
                    success, message = self.performSyncSubscriptions(commands["syncSubscriptions"])
                    if log:
                        print("syncSubscriptions")

                    if success:
                        commands["syncSubscriptions"] = []
                        self.set("pendingOnlineCommands", commands)

                    else:
                        self._syncProblems.append(message)

                # uploadSubscriptions
                if "uploadSubscriptions" in commands and commands["uploadSubscriptions"]:
                    success, message = self.perfomUploadSubscriptions(commands["uploadSubscriptions"])
                    if log:
                        print("uploadSubscriptions")

                    if success:
                        commands["uploadSubscriptions"] = []
                        self.set("pendingOnlineCommands", commands)

                    else:
                        self._syncProblems.append(message)

                # acceptInvitation
                if "acceptInvitation" in commands and commands["acceptInvitation"]:
                    success, message = self.performAcceptInvitation(commands["acceptInvitation"])
                    if log:
                        print("acceptInvitation")

                    if success:
                        commands["acceptInvitation"] = []
                        self.set("pendingOnlineCommands", commands)

                    else:
                        self._syncProblems.append(message)

                # declineInvitation
                if "declineInvitation" in commands and commands["declineInvitation"]:
                    success, message = self.performDeclineInvitation(commands["declineInvitation"])
                    if log:
                        print("declineInvitation")

                    if success:
                        commands["declineInvitation"] = []
                        self.set("pendingOnlineCommands", commands)

                    else:
                        self._syncProblems.append(message)

                # downloadSubscriptions
                if "downloadSubscriptions" in commands and commands["downloadSubscriptions"]:
                    success, message = self.performDownloadSubscriptions()
                    if log:
                        print("downloadSubscriptions")

                    if success:
                        commands["downloadSubscriptions"] = []
                        self.set("pendingOnlineCommands", commands)

                    else:
                        self._syncProblems.append(message)

                # downloadSettings
                if "downloadSettings" in commands and commands["downloadSettings"]:
                    success, message = self.performDownloadSettings()
                    if log:
                        print("downloadSettings")

                    if success:
                        commands["downloadSettings"] = []
                        self.set("pendingOnlineCommands", commands)

                    else:
                        self._syncProblems.append(message)

                self.delegate._userAccountHasReloaded()

                if self._syncProblems:
                    return False, self._syncProblems[0]
                else:
                    return True, None

            else:

                self.delegate._userAccountHasReloaded()
                self._syncProblems.append("#(response.notOnline)")
                return (
                    False,
                    ["#(response.notOnline)", "#(response.notOnline.headline)"],
                )

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def uploadSubscriptions(self, performCommands=True):
        try:

            self.appendCommands("uploadSubscriptions", self.secretSubscriptionURLs() or ["empty"])
            # self.appendCommands("downloadSubscriptions")

            success, message = True, None
            if performCommands:
                success, message = self.performCommands()
            return success, message

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def perfomUploadSubscriptions(self, oldURLs):

        try:

            userID = self.user()

            if userID:

                if oldURLs == ["pending"]:
                    oldURLs = ["empty"]

                self.set("lastServerSync", int(time.time()))

                # 				self.log('Uploading subscriptions: %s' % oldURLs)

                parameters = {
                    "anonymousAppID": self.anonymousAppID(),
                    "anonymousUserID": userID,
                    "subscriptionURLs": ",".join(oldURLs),
                    "secretKey": self.secretKey(),
                }

                success, response, headers = self.performRequest(
                    self.mothership + "/uploadUserSubscriptions", parameters
                )
                if not success:
                    return False, response

                response = json.loads(response)

                if response["response"] != "success":
                    return (
                        False,
                        [
                            "#(response.%s)" % response["response"],
                            "#(response.%s.headline)" % response["response"],
                        ],
                    )

            # Success
            return True, None
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def downloadSubscriptions(self, performCommands=True):

        try:
            if self.user():
                self.appendCommands("downloadSubscriptions")

                if performCommands:
                    return self.performCommands()
            else:
                return True, None

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def performDownloadSubscriptions(self):
        try:
            userID = self.user()

            if userID:

                parameters = {
                    "anonymousAppID": self.anonymousAppID(),
                    "anonymousUserID": userID,
                    "userTimezone": self.timezone(),
                    "secretKey": self.secretKey(),
                }

                success, response, responseObject = self.performRequest(
                    self.mothership + "/downloadUserSubscriptions", parameters
                )
                if not success:
                    return False, response

                response = json.loads(response)

                if response["response"] != "success":
                    return (
                        False,
                        [
                            "#(response.%s)" % response["response"],
                            "#(response.%s.headline)" % response["response"],
                        ],
                    )

                self.set("lastServerSync", int(time.time()))

                return self.executeDownloadSubscriptions(response)

            return True, None
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def executeDownloadSubscriptions(self, response):
        try:
            oldURLs = self.secretSubscriptionURLs()

            # Uninstall all protected fonts when app instance is reported as revoked
            if response["appInstanceIsRevoked"]:
                success, message = self.uninstallAllProtectedFonts()
                if not success:
                    return False, message

            # Verified Email Address
            if "userAccountEmailIsVerified" in response:
                self.set("userAccountEmailIsVerified", response["userAccountEmailIsVerified"])

            # USer Account Status
            if "userAccountStatus" in response:
                self.set("userAccountStatus", response["userAccountStatus"])

            # Website Token
            if "typeWorldWebsiteToken" in response:
                keyring = self.keyring()
                keyring.set_password(
                    self.userKeychainKey(self.user()),
                    "typeWorldWebsiteToken",
                    response["typeWorldWebsiteToken"],
                )

            # Add new subscriptions
            for incomingSubscription in response["heldSubscriptions"]:

                # Incoming server timestamp
                incomingServerTimestamp = None
                if "serverTimestamp" in incomingSubscription and incomingSubscription["serverTimestamp"]:
                    incomingServerTimestamp = incomingSubscription["serverTimestamp"]

                # Add new subscription
                if incomingSubscription["url"] not in oldURLs:
                    success, message, publisher, subscription = self.addSubscription(
                        incomingSubscription["url"], remotely=True
                    )

                    if success:

                        if incomingServerTimestamp:
                            subscription.set("serverTimestamp", incomingServerTimestamp)

                        self.delegate._subscriptionHasBeenAdded(subscription, remotely=True)

                    else:
                        return (
                            False,
                            "Received from self.addSubscription() for %s: %s" % (incomingSubscription["url"], message),
                        )

                # Update subscription
                else:
                    subscription = None
                    for publisher in self.publishers():
                        for subscription in publisher.subscriptions():
                            if subscription.url == URL(incomingSubscription["url"]).unsecretURL():
                                break

                    if (
                        incomingServerTimestamp
                        and subscription.get("serverTimestamp")
                        and int(incomingServerTimestamp) > int(subscription.get("serverTimestamp"))
                    ) or (incomingServerTimestamp and not subscription.get("serverTimestamp")):
                        success, message, changes = subscription.update()

                        if success:
                            subscription.set("serverTimestamp", int(incomingServerTimestamp))

            def replace_item(obj, key, replace_value):
                for k, v in obj.items():
                    if v == key:
                        obj[k] = replace_value
                return obj

            # oldPendingInvitations = self.pendingInvitations()

            # Invitations
            self.set(
                "acceptedInvitations",
                [replace_item(x, None, "") for x in response["acceptedInvitations"]],
            )
            self.set(
                "pendingInvitations",
                [replace_item(x, None, "") for x in response["pendingInvitations"]],
            )
            self.set(
                "sentInvitations",
                [replace_item(x, None, "") for x in response["sentInvitations"]],
            )

            # newPendingInvitations = self.pendingInvitations()
            # TODO: trigger notification

            # import threading
            # preloadThread = threading.Thread(target=self.preloadLogos)
            # preloadThread.start()

            # Delete subscriptions
            for publisher in self.publishers():
                for subscription in publisher.subscriptions():
                    if not subscription.protocol.secretURL() in [
                        x["url"] for x in response["heldSubscriptions"]
                    ] and not subscription.protocol.unsecretURL() in [
                        x["url"] for x in response["acceptedInvitations"]
                    ]:
                        subscription.delete(remotely=True)

            self.delegate._userAccountHasBeenUpdated()

            return True, None
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def acceptInvitation(self, url):
        try:
            userID = self.user()
            if userID:
                self.appendCommands("acceptInvitation", [url])

            return self.performCommands()
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def performAcceptInvitation(self, urls):
        try:
            userID = self.user()

            # Get Invitation IDs from urls
            IDs = []
            for invitation in self.pendingInvitations():
                for url in urls:
                    if invitation.url == url:
                        if invitation.ID not in IDs:
                            IDs.append(invitation.ID)
            assert len(IDs) == len(urls)

            if userID:

                self.set("lastServerSync", int(time.time()))

                parameters = {
                    "anonymousAppID": self.anonymousAppID(),
                    "anonymousUserID": userID,
                    "subscriptionIDs": ",".join(IDs),
                    "secretKey": self.secretKey(),
                }

                success, response, responseObject = self.performRequest(
                    self.mothership + "/acceptInvitations", parameters
                )
                if not success:
                    return False, response

                response = json.loads(response)

                if response["response"] != "success":
                    return (
                        False,
                        [
                            "#(response.%s)" % response["response"],
                            "#(response.%s.headline)" % response["response"],
                        ],
                    )

                # Success
                return self.executeDownloadSubscriptions(response)
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def declineInvitation(self, url):
        try:

            userID = self.user()
            if userID:
                self.appendCommands("declineInvitation", [url])

            return self.performCommands()

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def performDeclineInvitation(self, urls):
        try:
            userID = self.user()

            # Get Invitation IDs from urls
            IDs = []
            for invitation in self.pendingInvitations():
                for url in urls:
                    if invitation.url == url:
                        if invitation.ID not in IDs:
                            IDs.append(invitation.ID)
            assert len(IDs) == len(urls)

            if userID:

                self.set("lastServerSync", int(time.time()))

                parameters = {
                    "anonymousAppID": self.anonymousAppID(),
                    "anonymousUserID": userID,
                    "subscriptionIDs": ",".join(IDs),
                    "secretKey": self.secretKey(),
                }

                success, response, responseObject = self.performRequest(
                    self.mothership + "/declineInvitations", parameters
                )
                if not success:
                    return False, response

                response = json.loads(response)

                if response["response"] != "success":
                    return (
                        False,
                        [
                            "#(response.%s)" % response["response"],
                            "#(response.%s.headline)" % response["response"],
                        ],
                    )

                # Success
                return self.executeDownloadSubscriptions(response)
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def syncSubscriptions(self, performCommands=True):
        try:
            self.appendCommands("syncSubscriptions", self.secretSubscriptionURLs() or ["empty"])

            if performCommands:
                return self.performCommands()
            else:
                return True, None

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def performSyncSubscriptions(self, oldURLs):
        try:
            userID = self.user()

            if userID:

                if oldURLs == ["pending"]:
                    oldURLs = ["empty"]

                self.set("lastServerSync", int(time.time()))

                parameters = {
                    "anonymousAppID": self.anonymousAppID(),
                    "anonymousUserID": userID,
                    "subscriptionURLs": ",".join(oldURLs),
                    "secretKey": self.secretKey(),
                }

                success, response, responseObject = self.performRequest(
                    self.mothership + "/syncUserSubscriptions", parameters
                )
                if not success:
                    return False, response

                response = json.loads(response)

                if response["response"] != "success":
                    return (
                        False,
                        [
                            "#(response.%s)" % response["response"],
                            "#(response.%s.headline)" % response["response"],
                        ],
                    )

                # Add new subscriptions
                for url in response["subscriptions"]:
                    if url not in oldURLs:
                        (
                            success,
                            message,
                            publisher,
                            subscription,
                        ) = self.addSubscription(url, remotely=True)

                        if not success:
                            return False, message

                # Success
                return True, len(response["subscriptions"]) - len(oldURLs)

            return True, None

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def downloadSettings(self, performCommands=True):
        try:

            if performCommands:
                return self.performDownloadSettings()
            else:
                self.appendCommands("downloadSettings")

            return True, None

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def performDownloadSettings(self):
        try:

            parameters = {}

            if self.user():
                parameters["anonymousUserID"] = self.user()
                parameters["secretKey"] = self.secretKey()

            success, response, responseObject = self.performRequest(self.mothership + "/downloadSettings", parameters)
            if not success:
                return False, response

            response = json.loads(response)

            if response["response"] != "success":
                return (
                    False,
                    [
                        "#(response.%s)" % response["response"],
                        "#(response.%s.headline)" % response["response"],
                    ],
                )

            self.set("downloadedSettings", response["settings"])
            self.set("lastSettingsDownloaded", int(time.time()))

            return True, None

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def user(self):
        try:
            return self.get("typeworldUserAccount") or ""
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def userKeychainKey(self, ID):
        try:
            return "https://%s@%s.type.world" % (ID, self.anonymousAppID())
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def secretKey(self, userID=None):
        try:
            keyring = self.keyring()
            return keyring.get_password(self.userKeychainKey(userID or self.user()), "secretKey")
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def userName(self):
        try:
            keyring = self.keyring()
            return keyring.get_password(self.userKeychainKey(self.user()), "userName")
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def userEmail(self):
        try:
            keyring = self.keyring()
            return keyring.get_password(self.userKeychainKey(self.user()), "userEmail")

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def createUserAccount(self, name, email, password1, password2):
        try:
            if self.online():

                if not name or not email or not password1 or not password2:
                    return False, "#(RequiredFieldEmpty)"

                if password1 != password2:
                    return False, "#(PasswordsDontMatch)"

                parameters = {
                    "name": name,
                    "email": email,
                    "password": password1,
                }
                if self.secretServerAuthKey:
                    parameters["SECRETKEY"] = self.secretServerAuthKey

                success, response, responseObject = self.performRequest(
                    self.mothership + "/createUserAccount", parameters
                )
                if not success:
                    return False, response

                response = json.loads(response)

                if response["response"] != "success":
                    return (
                        False,
                        [
                            "#(response.%s)" % response["response"],
                            "#(response.%s.headline)" % response["response"],
                        ],
                    )

                # success
                return self.linkUser(response["anonymousUserID"], response["secretKey"])

            else:
                return (
                    False,
                    ["#(response.notOnline)", "#(response.notOnline.headline)"],
                )

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def deleteUserAccount(self, email, password):
        try:

            if self.online():

                # Required parameters
                if not email or not password:
                    return False, "#(RequiredFieldEmpty)"

                # Unlink user first
                if self.userEmail() == email:
                    success, message = self.performUnlinkUser()
                    if not success:
                        return False, message

                parameters = {
                    "email": email,
                    "password": password,
                }

                success, response, responseObject = self.performRequest(
                    self.mothership + "/deleteUserAccount", parameters
                )
                if not success:
                    return False, response

                response = json.loads(response)

                if response["response"] != "success":
                    return (
                        False,
                        [
                            "#(response.%s)" % response["response"],
                            "#(response.%s.headline)" % response["response"],
                        ],
                    )

                # success

                return True, None

            else:
                return (
                    False,
                    ["#(response.notOnline)", "#(response.notOnline.headline)"],
                )
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def resendEmailVerification(self):
        try:
            parameters = {
                "email": self.userEmail(),
            }

            success, response, responseObject = self.performRequest(
                self.mothership + "/resendEmailVerification", parameters
            )

            if not success:
                return False, response

            response = json.loads(response)

            if response["response"] != "success":
                return (
                    False,
                    [
                        "#(response.%s)" % response["response"],
                        "#(response.%s.headline)" % response["response"],
                    ],
                )

            # success
            return True, None

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def logInUserAccount(self, email, password):
        try:
            if not email or not password:
                return False, "#(RequiredFieldEmpty)"

            if self.online():

                parameters = {
                    "email": email,
                    "password": password,
                }

                success, response, responseObject = self.performRequest(
                    self.mothership + "/logInUserAccount", parameters
                )
                if not success:
                    return False, response

                response = json.loads(response)

                if response["response"] != "success":
                    return (
                        False,
                        [
                            "#(response.%s)" % response["response"],
                            "#(response.%s.headline)" % response["response"],
                        ],
                    )

                # success
                return self.linkUser(response["anonymousUserID"], response["secretKey"])
            else:
                return (
                    False,
                    ["#(response.notOnline)", "#(response.notOnline.headline)"],
                )

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def linkUser(self, userID, secretKey):
        try:
            # Set secret key now, so it doesn't show up in preferences when offline
            keyring = self.keyring()
            keyring.set_password(self.userKeychainKey(userID), "secretKey", secretKey)
            assert self.secretKey(userID) == secretKey

            self.appendCommands("linkUser", userID)
            self.appendCommands("syncSubscriptions")
            self.appendCommands("downloadSubscriptions")

            return self.performCommands()
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def performLinkUser(self, userID):
        try:

            parameters = {
                "anonymousAppID": self.anonymousAppID(),
                "anonymousUserID": userID,
                "secretKey": self.secretKey(userID),
            }

            parameters = self.addMachineIDToParameters(parameters)

            success, response, responseObject = self.performRequest(
                self.mothership + "/linkTypeWorldUserAccount", parameters
            )
            if not success:
                return False, response

            response = json.loads(response)

            if response["response"] != "success":
                return (
                    False,
                    [
                        "#(response.%s)" % response["response"],
                        "#(response.%s.headline)" % response["response"],
                    ],
                )

            # Success
            self.set("typeworldUserAccount", userID)
            assert userID == self.user()

            # ZMQ
            topicID = "user-%s" % self.user()
            self.registerZMQCallback(topicID, self.zmqCallback)

            keyring = self.keyring()
            if "userEmail" in response:
                keyring.set_password(self.userKeychainKey(userID), "userEmail", response["userEmail"])
            if "userName" in response:
                keyring.set_password(self.userKeychainKey(userID), "userName", response["userName"])

            return True, None

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def linkedAppInstances(self):
        try:
            if not self.user():
                return False, "No user"

            parameters = {
                "anonymousAppID": self.anonymousAppID(),
                "anonymousUserID": self.user(),
                "secretKey": self.secretKey(),
            }

            success, response, responseObject = self.performRequest(self.mothership + "/userAppInstances", parameters)
            if not success:
                return False, response

            response = json.loads(response)

            if response["response"] != "success":
                return (
                    False,
                    [
                        "#(response.%s)" % response["response"],
                        "#(response.%s.headline)" % response["response"],
                    ],
                )

            class AppInstance(object):
                pass

            # Success
            instances = []

            for serverInstance in response["appInstances"]:

                instance = AppInstance()

                for key in serverInstance:
                    setattr(instance, key, serverInstance[key])

                instances.append(instance)

            return True, instances
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def revokeAppInstance(self, anonymousAppID=None):
        try:
            if not self.user():
                return False, "No user"

            parameters = {
                "anonymousAppID": anonymousAppID or self.anonymousAppID(),
                "anonymousUserID": self.user(),
                "secretKey": self.secretKey(),
            }

            success, response, responseObject = self.performRequest(self.mothership + "/revokeAppInstance", parameters)
            if not success:
                return False, response

            response = json.loads(response)

            if response["response"] != "success":
                return (
                    False,
                    [
                        "#(response.%s)" % response["response"],
                        "#(response.%s.headline)" % response["response"],
                    ],
                )

            return True, None
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def reactivateAppInstance(self, anonymousAppID=None):
        try:

            if not self.user():
                return False, "No user"

            parameters = {
                "anonymousAppID": anonymousAppID or self.anonymousAppID(),
                "anonymousUserID": self.user(),
                "secretKey": self.secretKey(),
            }

            success, response, responseObject = self.performRequest(
                self.mothership + "/reactivateAppInstance", parameters
            )
            if not success:
                return False, response

            response = json.loads(response)

            if response["response"] != "success":
                return (
                    False,
                    [
                        "#(response.%s)" % response["response"],
                        "#(response.%s.headline)" % response["response"],
                    ],
                )

            return True, None
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def unlinkUser(self):
        try:
            self.appendCommands("unlinkUser")
            return self.performCommands()
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def uninstallAllProtectedFonts(self, dryRun=False):
        try:
            # Uninstall all protected fonts
            for publisher in self.publishers():
                for subscription in publisher.subscriptions():

                    (
                        success,
                        installabeFontsCommand,
                    ) = subscription.protocol.installableFontsCommand()
                    assert success

                    fontIDs = []

                    for foundry in installabeFontsCommand.foundries:
                        for family in foundry.families:
                            for font in family.fonts:

                                # Dry run from central server: add all fonts to list
                                if dryRun and font.protected:
                                    fontIDs.append(font.uniqueID)  # nocoverage (This is executed only when the
                                    # central server uninstalls *all* fonts)

                                # Run from local client, add only actually installed
                                # fonts
                                elif not dryRun and font.protected and subscription.installedFontVersion(font=font):
                                    fontIDs.append(font.uniqueID)

                    if fontIDs:
                        success, message = subscription.removeFonts(fontIDs, dryRun=dryRun, updateSubscription=False)
                        if not success:
                            return False, message

            return True, None
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def performUnlinkUser(self):
        try:
            userID = self.user()

            success, response = self.uninstallAllProtectedFonts()
            if not success:
                return False, response

            parameters = {
                "anonymousAppID": self.anonymousAppID(),
                "anonymousUserID": userID,
                "secretKey": self.secretKey(),
            }

            success, response, responseObject = self.performRequest(
                self.mothership + "/unlinkTypeWorldUserAccount", parameters
            )
            if not success:
                return False, response

            response = json.loads(response)

            continueFor = ["userUnknown"]
            if response["response"] != "success" and not response["response"] in continueFor:
                return (
                    False,
                    [
                        "#(response.%s)" % response["response"],
                        "#(response.%s.headline)" % response["response"],
                    ],
                )

            self.set("typeworldUserAccount", "")
            self.set("userAccountEmailIsVerified", "")
            self.remove("acceptedInvitations")
            self.remove("pendingInvitations")
            self.remove("sentInvitations")

            # ZMQ
            topicID = "user-%s" % userID
            self.unregisterZMQCallback(topicID)

            keyring = self.keyring()
            keyring.delete_password(self.userKeychainKey(userID), "secretKey")
            keyring.delete_password(self.userKeychainKey(userID), "userEmail")
            keyring.delete_password(self.userKeychainKey(userID), "userName")

            # Success
            return True, None

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def systemLocale(self):
        try:

            if not self._systemLocale:
                if MAC:
                    from AppKit import NSLocale

                    self._systemLocale = str(NSLocale.preferredLanguages()[0].split("_")[0].split("-")[0])
                else:
                    import locale

                    self._systemLocale = locale.getdefaultlocale()[0].split("_")[0]

            return self._systemLocale
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def locale(self):
        try:

            """\
            Reads user locale from OS
            """

            if self.get("localizationType") == "systemLocale":
                _locale = [self.systemLocale()]
            elif self.get("localizationType") == "customLocale":
                _locale = [self.get("customLocaleChoice") or "en"]
            else:
                _locale = [self.systemLocale()]

            if "en" not in _locale:
                _locale.append("en")

            return _locale
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def expiringInstalledFonts(self):
        try:
            fonts = []
            for publisher in self.publishers():
                for subscription in publisher.subscriptions():
                    fonts.extend(subscription.expiringInstalledFonts())
            return fonts
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def amountOutdatedFonts(self):
        try:
            amount = 0
            for publisher in self.publishers():
                amount += publisher.amountOutdatedFonts()
            return amount
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def keyring(self):
        try:

            # Using keyring causes problems on all three MAC/WIN/LINUX
            # when used headlessly in a CI environment,
            # so we’re using the dummy for CI, which sucks because
            # then you can’t self-test thoroughly it during app build
            if (CI and not self.inCompiledApp) or GAE:
                keyring = dummyKeyRing
                return keyring

            import keyring  # nocoverage

            if MAC:  # nocoverage
                if self.inCompiledApp:
                    keyring.core.set_keyring(keyring.core.load_keyring("keyring.backends.macOS.Keyring"))  # nocoverage

            elif WIN:  # nocoverage
                keyring.core.set_keyring(
                    keyring.core.load_keyring("keyring.backends.Windows.WinVaultKeyring")
                )  # nocoverage

            elif LINUX:  # nocoverage
                keyring.core.set_keyring(
                    keyring.core.load_keyring("keyring.backends.kwallet.DBusKeyring")
                )  # nocoverage

            return keyring  # nocoverage

        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def handleTraceback(self, file=None, sourceMethod=None, e=None):

        # Needs explicit permission, to be handled by UI
        if self.get("sendCrashReports") or self.testing:

            payload = f"""\
Version: {typeworld.api.VERSION}
{traceback.format_exc()}
"""

            print(payload)
            # Remove path parts to make tracebacks identical (so they don't re-surface)

            def removePathPrefix(_payload, _snippet, _file):
                m = re.search(r'File "(.+?)"', _payload, re.MULTILINE)
                if m:
                    _file = m.group(1)
                    index = _file.find(_snippet)
                    if index != -1:
                        clientPathPrefix = _file[:index]
                        return _payload.replace(clientPathPrefix, "")
                    else:
                        return _payload
                else:
                    return _payload  # nocoverage (this seems to never get executed,
                    # because code always contains `File "..."` like it should.
                    # Leaving this here just in case) TODO

            # Normalize file paths
            if WIN:
                payload = (
                    removePathPrefix(payload, "TypeWorld.exe", __file__)
                    .replace("\\", "/")
                    .replace("TypeWorld.exe", "app.py")
                )
            payload = removePathPrefix(payload, "typeworld/client/", __file__).replace("\\", "/")
            payload = removePathPrefix(payload, "app.py", file).replace("\\", "/")

            # Create supplementary information
            supplementary = {
                "os": OSName(),
                "file": file or __file__,
                "preferences": self._preferences.dictionary(),
            }

            if sourceMethod:
                if hasattr(sourceMethod, "__self__") and sourceMethod.__self__:
                    supplementary["sourceMethodSignature"] = (
                        str(sourceMethod.__self__.__class__.__name__)
                        + "."
                        + str(sourceMethod.__name__)
                        + str(inspect.signature(sourceMethod))
                    )
                else:
                    supplementary["sourceMethodSignature"] = str(  # nocoverage
                        sourceMethod.__name__  # nocoverage
                    ) + str(  # nocoverage
                        inspect.signature(sourceMethod)  # nocoverage
                    )  # nocoverage
                # (currently not testing for calling this method without
                # a sourceMethod parameter)

            supplementary["traceback"] = payload
            supplementary["stack"] = []
            supplementary["trace"] = []
            for s in inspect.stack():
                supplementary["stack"].append(
                    {
                        "filename": str(s.filename),
                        "lineno": str(s.lineno),
                        "function": str(s.function),
                        "code_context": str(s.code_context[0].replace("\t", " ").rstrip()) if s.code_context else None,
                    }
                )
            for s in inspect.trace():
                supplementary["trace"].append(
                    {
                        "filename": str(s.filename),
                        "lineno": str(s.lineno),
                        "function": str(s.function),
                        "code_context": str(s.code_context[0].replace("\t", " ").rstrip()) if s.code_context else None,
                    }
                )

            # replace faulty line of code (some Python versions include the faulty code
            # line in the traceback output, some not)
            if supplementary["trace"] and supplementary["trace"][0]["code_context"]:
                payload = payload.replace(supplementary["trace"][0]["code_context"], "")
                payload = payload.replace("\n \n", "\n")

            parameters = {
                "payload": payload,
                "supplementary": json.dumps(supplementary),
            }

            # Submit to central server
            # if self.online(self.mothership):

            def handleTracebackWorker(self):

                success, response, responseObject = self.performRequest(
                    self.mothership + "/handleTraceback", parameters
                )
                if success:
                    response = json.loads(response)
                    if response["response"] != "success":
                        self.log("handleTraceback() error on server, step 2: %s" % response)
                if not success:
                    self.log("handleTraceback() error on server, step 1: %s" % response)

            handleTracebackThread = threading.Thread(target=handleTracebackWorker, args=(self,))
            handleTracebackThread.start()

            # Log
            if sourceMethod:
                self.log(payload + "\nMethod signature:\n" + supplementary["sourceMethodSignature"])
            else:
                self.log(payload)  # nocoverage  # nocoverage  # nocoverage
                # (currently not testing for calling this method without a sourceMethod
                # parameter)

            return False, payload

    def log(self, *arg):
        string = "Type.World: %s" % " ".join(map(str, arg))
        if MAC:
            nslog(string)
        else:
            logging.debug(string)

    def prepareUpdate(self):
        self._subscriptionsUpdated = []

    def allSubscriptionsUpdated(self):
        try:

            for publisher in self.publishers():
                for subscription in publisher.subscriptions():
                    if subscription.stillUpdating():
                        return False

            return True
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    # # DEPRECATED, since resources are now handled by GUI since 0.2.10-beta
    # def deleteResources(self, urls):

    #     try:
    #         resources = self.get("resources") or {}

    #         for url in urls:
    #             for key in resources.keys():
    #                 if key.startswith(url):
    #                     del resources[key]
    #                     break

    #         self.set("resources", resources)

    #     except Exception as e:  # nocoverage
    #         return self.handleTraceback(  # nocoverage
    #             sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
    #         )

    # # DEPRECATED, since resources are now handled by GUI since 0.2.10-beta
    # def resourceByURL(self, url, binary=False, update=False):
    #     """Caches and returns content of a HTTP resource. If binary is set to True,
    #     content will be stored and return as a bas64-encoded string"""
    #     try:
    #         resources = self.get("resources") or {}

    #         key = f"{url},binary={binary}"

    #         # Load fresh
    #         if key not in resources or update:

    #             if self.testScenario:
    #               url = addAttributeToURL(url, "testScenario=%s" % self.testScenario)

    #             success, response, responseObject = request(url, method="GET")
    #             if not success:
    #                 return False, response, responseObject.headers["content-type"]

    #             content = responseObject.content

    #             if binary:
    #                 content = base64.b64encode(content).decode()
    #             else:
    #                 content = content.decode()

    #           resources[key] = responseObject.headers["content-type"] + "," + content
    #             self.set("resources", resources)

    #             return True, content, responseObject.headers["content-type"]

    #         # Serve from cache
    #         else:

    #             response = resources[key]
    #             mimeType = response.split(",")[0]
    #             content = response[len(mimeType) + 1 :]

    #             return True, content, mimeType
    #     except Exception as e:  # nocoverage
    #         return self.handleTraceback(  # nocoverage
    #             sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
    #         )

    def anonymousAppID(self):
        try:
            anonymousAppID = self.get("anonymousAppID")

            if anonymousAppID is None or anonymousAppID == {}:
                import uuid

                anonymousAppID = str(uuid.uuid1())
                self.set("anonymousAppID", anonymousAppID)

            return anonymousAppID
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def endpointCommand(self, url):
        try:
            # Check for URL validity
            success, response = urlIsValid(url)
            if not success:
                return False, response

            # Get subscription
            success, protocol = getProtocol(url)
            protocol.client = self
            # Get Root Command
            return protocol.endpointCommand(testScenario=self.testScenario)
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def reportAPIEndpointError(self, url):
        reportThread = threading.Thread(target=self.reportAPIEndpointErrorWorker, args=(url,))
        reportThread.start()

    def reportAPIEndpointErrorWorker(self, url):
        success, content, response = self.performRequest(
            self.mothership + "/reportAPIEndpointError", {"subscriptionURL": url}
        )

    def addSubscription(
        self,
        url,
        username=None,
        password=None,
        remotely=False,
        JSON=None,
        reportErrors=True,
    ):
        try:
            self._updatingProblem = None

            # Check for URL validity
            success, response = urlIsValid(url)
            if not success:
                return False, response, None, None

            # Get subscription
            success, message = getProtocol(url)
            if success:
                protocol = message
                protocol.client = self
            else:
                return False, message, None, None

            # Change secret key
            if protocol.unsecretURL() in self.unsecretSubscriptionURLs():

                # Initial endpointCommand
                success, message = self.endpointCommand(url)
                if success:
                    endpointCommand = message
                else:
                    if reportErrors:
                        self.reportAPIEndpointError(url)
                    return False, message, None, None

                protocol.setSecretKey(protocol.url.secretKey)
                publisher = self.publisher(endpointCommand.canonicalURL)
                subscription = publisher.subscription(protocol.unsecretURL(), protocol)

            else:

                # Initial Health Check
                success, response = protocol.aboutToAddSubscription(
                    anonymousAppID=self.anonymousAppID(),
                    anonymousTypeWorldUserID=self.user(),
                    accessToken=protocol.url.accessToken,
                    testScenario=self.testScenario,
                )
                if not success:
                    message = response
                    # self._updatingProblem = [
                    #     "#(response.loginRequired)",
                    #     "#(response.loginRequired.headline)",
                    # ]
                    if reportErrors:
                        self.reportAPIEndpointError(url)
                    return False, message, None, None

                # endpointCommand
                success, endpointCommand = protocol.endpointCommand(testScenario=self.testScenario)
                assert success
                assert endpointCommand

                # Breaking API Version Check
                if "breakingAPIVersions" in self.get("downloadedSettings"):
                    breakingVersions = copy.copy(self.get("downloadedSettings")["breakingAPIVersions"])
                    if self.testScenario == "simulateBreakingAPIVersion":
                        versionParts = breakingVersions[-1].split(".")
                        versionParts[0] = str(int(versionParts[0]) + 1)
                        breakingVersions.append(".".join(versionParts))

                    success, rootCommand = protocol.rootCommand(testScenario=self.testScenario)
                    assert success
                    assert rootCommand
                    incomingVersion = rootCommand.version

                    for breakingVersion in breakingVersions:
                        # Breaking version is higher than local API version
                        if (
                            semver.VersionInfo.parse(breakingVersion).compare(typeworld.api.VERSION)
                            == 1
                            # Incoming version is higher than breaking
                        ) and (semver.VersionInfo.parse(incomingVersion).compare(breakingVersion) == 1):
                            if reportErrors:
                                self.reportAPIEndpointError(url)
                            return (
                                False,
                                [
                                    "#(response.appUpdateRequired)",
                                    "#(response.appUpdateRequired.headline)",
                                ],
                                None,
                                None,
                            )

                # Commercial app check
                if self.commercial and self.appID not in endpointCommand.allowedCommercialApps:
                    if reportErrors:
                        self.reportAPIEndpointError(url)
                    return (
                        False,
                        [
                            "#(response.commercialAppNotAllowed)",
                            "#(response.commercialAppNotAllowed.headline)",
                        ],
                        None,
                        None,
                    )

                publisher = self.publisher(endpointCommand.canonicalURL)
                subscription = publisher.subscription(protocol.unsecretURL(), protocol)

                # Success
                subscription.save()
                publisher.save()
                subscription.stillAlive()
                self.manageMessageQueueConnection()
                self.delegate._subscriptionHasBeenAdded(subscription, remotely)

            if not remotely and not self.externallyControlled:
                success, message = self.uploadSubscriptions()
                if not success:
                    return (
                        False,
                        message,
                        None,
                        None,
                    )  # 'Response from client.uploadSubscriptions(): %s' %

            return True, None, publisher, subscription

        except Exception as e:  # nocoverage
            self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

            return False, traceback.format_exc(), None, None

    def publisher(self, canonicalURL):
        try:
            if canonicalURL not in self._publishers:
                e = APIPublisher(self, canonicalURL)
                self._publishers[canonicalURL] = e

            if self.get("publishers") and canonicalURL in self.get("publishers"):
                self._publishers[canonicalURL].exists = True

            return self._publishers[canonicalURL]
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def publishers(self):
        try:
            if self.get("publishers"):
                publishers = []
                if self.get("publishers"):
                    for canonicalURL in self.get("publishers"):
                        publisher = self.publisher(canonicalURL)
                        if publisher.subscriptions():
                            publishers.append(publisher)
                return publishers
            else:
                return []
        except Exception as e:  # nocoverage
            return self.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def files(self):
        "Returns list of all resource URLs"
        files = []
        for publisher in self.publishers():
            files = set(files) | set(publisher.files())
        return list(set(files))


class APIPublisher(object):
    """\
    Represents an API endpoint, identified and grouped by the canonical URL attribute
    of the API responses. This API endpoint class can then hold several repositories.
    """

    def __init__(self, parent, canonicalURL):
        self.parent = parent
        self.canonicalURL = canonicalURL
        self.exists = False
        self._subscriptions = {}

        self._updatingSubscriptions = []

    def folder(self):
        try:
            if WIN:
                return os.path.join(os.environ["WINDIR"], "Fonts")

            elif MAC:

                from os.path import expanduser

                home = expanduser("~")
                folder = os.path.join(home, "Library", "Fonts", "Type.World App")

                return folder

            else:
                import tempfile

                return tempfile.gettempdir()
        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def stillUpdating(self):
        try:
            return len(self._updatingSubscriptions) > 0
        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def updatingProblem(self):
        try:

            problems = []

            for subscription in self.subscriptions():
                problem = subscription.updatingProblem()
                if problem and problem not in problems:
                    problems.append(problem)

            if problems:
                return problems

        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def name(self, locale=["en"]):

        try:
            endpointCommand = self.subscriptions()[0].protocol.endpointCommand()[1]
            if endpointCommand:
                return endpointCommand.name.getTextAndLocale(locale=locale)
        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def amountInstalledFonts(self):
        try:
            return len(self.installedFonts())
        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def installedFonts(self):
        try:
            _list = []

            for subscription in self.subscriptions():
                for font in subscription.installedFonts():
                    if font not in _list:
                        _list.append(font)

            return _list
        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def amountOutdatedFonts(self):
        try:
            return len(self.outdatedFonts())
        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def outdatedFonts(self):
        try:
            _list = []

            for subscription in self.subscriptions():
                for font in subscription.outdatedFonts():
                    if font not in _list:
                        _list.append(font)

            return _list
        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    # def currentSubscription(self):
    # 	if self.get('currentSubscription'):
    # 		subscription = self.subscription(self.get('currentSubscription'))
    # 		if subscription:
    # 			return subscription

    def get(self, key):
        try:
            preferences = self.parent.get("publisher(%s)" % self.canonicalURL) or {}
            if key in preferences:

                o = preferences[key]

                if "Array" in o.__class__.__name__:
                    o = list(o)
                elif "Dictionary" in o.__class__.__name__:
                    o = dict(o)

                return o
        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def set(self, key, value):
        try:
            preferences = self.parent.get("publisher(%s)" % self.canonicalURL) or {}
            preferences[key] = value
            self.parent.set("publisher(%s)" % self.canonicalURL, preferences)
        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    # def addGitHubSubscription(self, url, commits):

    # 	self.parent._subscriptions = {}

    # 	subscription = self.subscription(url)
    # 	subscription.set('commits', commits)
    # 	self.set('currentSubscription', url)
    # 	subscription.save()

    # 	return True, None

    def subscription(self, url, protocol=None):
        try:

            if url not in self._subscriptions:

                # Load from DB
                loadFromDB = False

                if not protocol:
                    success, message = getProtocol(url)
                    if success:
                        protocol = message
                        loadFromDB = True

                e = APISubscription(self, protocol)
                if loadFromDB:
                    protocol.loadFromDB()

                self._subscriptions[url] = e

            if self.get("subscriptions") and url in self.get("subscriptions"):
                self._subscriptions[url].exists = True

            return self._subscriptions[url]

        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def subscriptions(self):
        try:
            subscriptions = []
            if self.get("subscriptions"):
                for url in self.get("subscriptions"):
                    if urlIsValid(url)[0] is True:
                        subscriptions.append(self.subscription(url))
            return subscriptions
        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def update(self):
        try:

            self.parent.prepareUpdate()

            changes = False

            if self.parent.online():

                for subscription in self.subscriptions():
                    success, message, change = subscription.update()
                    if change:
                        changes = True
                    if not success:
                        return success, message, changes

                return True, None, changes

            else:
                return (
                    False,
                    ["#(response.notOnline)", "#(response.notOnline.headline)"],
                    False,
                )
        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def save(self):
        try:
            publishers = self.parent.get("publishers") or []
            if self.canonicalURL not in publishers:
                publishers.append(self.canonicalURL)
            self.parent.set("publishers", publishers)
        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    # # DEPRECATED, since resources are now handled by GUI since 0.2.10-beta
    # def resourceByURL(self, url, binary=False, update=False):
    #     """Caches and returns content of a HTTP resource. If binary is set to True,
    #     content will be stored and return as a bas64-encoded string"""

    #     try:
    #       success, response, mimeType = self.parent.resourceByURL(url, binary, update)

    #         # Save resource
    #         if success is True:
    #             resourcesList = self.get("resources") or []
    #             if url not in resourcesList:
    #                 resourcesList.append(url)
    #                 self.set("resources", resourcesList)

    #         return success, response, mimeType

    #     except Exception as e:  # nocoverage
    #         self.parent.handleTraceback(  # nocoverage
    #             sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
    #         )

    def delete(self, calledFromSubscription=False):
        try:

            if not calledFromSubscription:
                for subscription in self.subscriptions():
                    success, message = subscription.delete(calledFromParent=True, remotely=False)
                    if not success:
                        return False, message

            # Resources
            self.parent.delegate._publisherWillDelete(self)

            self.parent.remove("publisher(%s)" % self.canonicalURL)
            publishers = self.parent.get("publishers")
            publishers.remove(self.canonicalURL)
            self.parent.set("publishers", publishers)
            # self.parent.set('currentPublisher', '')

            # Sync to server
            if not calledFromSubscription:
                self.parent.uploadSubscriptions()

            self.parent.delegate._publisherHasBeenDeleted(self)
            self.parent.manageMessageQueueConnection()

            self.parent._publishers = {}

            return True, None

        except Exception as e:  # nocoverage
            self.parent.handleTraceback(sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e)  # nocoverage

    def files(self):
        "Returns list of all resource URLs that the publisher may have loaded"
        files = []
        for subscription in self.subscriptions():
            files = set(files) | set(subscription.files())
        return list(set(files))


class APISubscription(object):
    """\
    Represents a subscription, identified and grouped by the canonical URL attribute of
    the API responses.
    """

    def __init__(self, parent, protocol):
        try:
            self.parent = parent
            self.exists = False
            self.secretKey = None
            self.protocol = protocol
            self.protocol.subscription = self
            self.protocol.client = self.parent.parent
            self.url = self.protocol.unsecretURL()

            self.stillAliveTouched = None
            self._updatingProblem = None

            # ZMQ
            if self.parent.parent._isSetOnline and self.parent.parent.zmqSubscriptions:
                self.parent.parent.zmqSetup()
                self.parent.parent.registerZMQCallback(self.zmqTopic(), self.zmqCallback)

        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def zmqTopic(self):
        return "subscription-%s" % urllib.parse.quote_plus(self.protocol.shortUnsecretURL())

    def __repr__(self):
        return f'<APISubscription url="{self.url}">'

    def uniqueID(self):
        try:
            uniqueID = self.get("uniqueID")

            if uniqueID is None or uniqueID == {}:
                # import uuid

                uniqueID = Garbage(10)
                self.set("uniqueID", uniqueID)

            return uniqueID
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def zmqCallback(self, message):
        try:
            if message:
                data = json.loads(message)
                if (
                    data["command"] == "pullUpdates"
                    and "sourceAnonymousAppID" not in data
                    or (
                        "sourceAnonymousAppID" in data
                        and data["sourceAnonymousAppID"] != self.parent.parent.anonymousAppID()
                    )
                ):

                    delegate = self.parent.parent.delegate
                    delegate._subscriptionUpdateNotificationHasBeenReceived(self)

                    success, message, changes = self.update()
                    if success:
                        if "serverTimestamp" in data and data["serverTimestamp"]:
                            self.set("serverTimestamp", data["serverTimestamp"])

        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    # TODO: Temporarily suspended because the central API updateSubscription requires
    # an APIKey parameter, so is intended only for publishers atm.
    # Here, this should be called after a protected font has been installed,
    # as it should update the used seats for that font

    # def announceChange(self):
    # 	try:

    # 		if not self.parent.parent.user(): return False, 'No user'

    # 		self.set('lastServerSync', int(time.time()))

    # 		parameters = {
    # 			'command': 'updateSubscription',
    # 			'anonymousAppID': self.parent.parent.anonymousAppID(),
    # 			'anonymousUserID': self.parent.parent.user(),
    # 			'subscriptionURL': self.protocol.url.secretURL(),
    # 			'secretKey': self.parent.parent.secretKey(),
    # 		}

    # 		success, response, responseObject =
    # self.parent.parent.performRequest(self.parent.parent.
    # mothership, parameters)
    # 		if not success:
    # 			return False, response

    # 		response = json.loads(response)

    # 		if response['response'] != 'success':
    # 			return False, ['#(response.%s)' % response['response'], '#(response.%s.
    # headline)' % response['response']]

    # 		# Success
    # 		return True, None

    # 	except Exception as e: self.parent.parent.handleTraceback(sourceMethod =
    # getattr(self, sys._getframe().f_code.co_name), e = e)

    def hasProtectedFonts(self):
        try:
            success, installabeFontsCommand = self.protocol.installableFontsCommand()

            for foundry in installabeFontsCommand.foundries:
                for family in foundry.families:
                    for font in family.fonts:
                        if font.protected:
                            return True

            return False
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def stillAlive(self):

        try:

            def stillAliveWorker(self):

                # Register endpoint

                parameters = {
                    "url": "typeworld://%s+%s"
                    % (
                        self.protocol.url.protocol,
                        self.parent.canonicalURL.replace("://", "//"),
                    ),
                }

                success, response, responseObject = self.parent.parent.performRequest(
                    self.parent.parent.mothership + "/registerAPIEndpoint", parameters
                )
                if not success:
                    return False, response

                response = json.loads(response)

            # Touch only once
            if not self.parent.parent.user():
                if not self.stillAliveTouched:

                    stillAliveThread = threading.Thread(target=stillAliveWorker, args=(self,))
                    stillAliveThread.start()

                    self.stillAliveTouched = time.time()
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def inviteUser(self, targetEmail):
        # print("inviteUser()")
        try:

            if self.parent.parent.online():

                if not self.parent.parent.userEmail():
                    return False, "No source user linked."

                parameters = {
                    "targetUserEmail": targetEmail,
                    "sourceUserEmail": self.parent.parent.userEmail(),
                    "subscriptionURL": self.protocol.secretURL(),
                }

                success, response, responseObject = self.parent.parent.performRequest(
                    self.parent.parent.mothership + "/inviteUserToSubscription",
                    parameters,
                )
                if not success:
                    return False, response

                response = json.loads(response)
                # print(response)

                if response["response"] == "success":
                    return True, None
                else:
                    return (
                        False,
                        [
                            "#(response.%s)" % response["response"],
                            "#(response.%s.headline)" % response["response"],
                        ],
                    )

            else:
                return (
                    False,
                    ["#(response.notOnline)", "#(response.notOnline.headline)"],
                )
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def revokeUser(self, targetEmail):
        try:

            if self.parent.parent.online():

                parameters = {
                    "targetUserEmail": targetEmail,
                    "sourceUserEmail": self.parent.parent.userEmail(),
                    "subscriptionURL": self.protocol.secretURL(),
                }

                success, response, responseObject = self.parent.parent.performRequest(
                    self.parent.parent.mothership + "/revokeSubscriptionInvitation",
                    parameters,
                )
                if not success:
                    return False, response

                response = json.loads(response)

                if response["response"] == "success":
                    return True, None
                else:
                    return False, response["response"]

            else:
                return (
                    False,
                    ["#(response.notOnline)", "#(response.notOnline.headline)"],
                )
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def invitationAccepted(self):
        try:

            if self.parent.parent.user():
                acceptedInvitations = self.parent.parent.acceptedInvitations()
                if acceptedInvitations:
                    for invitation in acceptedInvitations:
                        if self.protocol.unsecretURL() == invitation.url:
                            return True

        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def invitationSent(self):
        try:

            if self.parent.parent.user():
                sentInvitations = self.parent.parent.sentInvitations()
                if sentInvitations:
                    for invitation in sentInvitations:
                        if self.protocol.unsecretURL() == invitation.url:
                            return True

        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def stillUpdating(self):
        try:
            return self.url in self.parent._updatingSubscriptions
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def name(self, locale=["en"]):
        try:

            success, installabeFontsCommand = self.protocol.installableFontsCommand()

            return installabeFontsCommand.name.getText(locale) or "#(Unnamed)"
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    # # DEPRECATED, since resources are now handled by GUI since 0.2.10-beta
    # def resourceByURL(self, url, binary=False, update=False):
    #     """Caches and returns content of a HTTP resource. If binary is set to True,
    #     content will be stored and return as a bas64-encoded string"""
    #     try:
    #         success, response, mimeType = self.parent.parent.resourceByURL(
    #             url, binary, update
    #         )

    #         # Save resource
    #         if success is True:
    #             resourcesList = self.get("resources") or []
    #             if url not in resourcesList:
    #                 resourcesList.append(url)
    #                 self.set("resources", resourcesList)

    #         return success, response, mimeType

    #     except Exception as e:  # nocoverage
    #         self.parent.parent.handleTraceback(  # nocoverage
    #             sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
    #         )

    def familyByID(self, ID):
        try:
            success, installabeFontsCommand = self.protocol.installableFontsCommand()

            for foundry in installabeFontsCommand.foundries:
                for family in foundry.families:
                    if family.uniqueID == ID:
                        return family
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def fontByID(self, ID):
        try:
            success, installabeFontsCommand = self.protocol.installableFontsCommand()

            for foundry in installabeFontsCommand.foundries:
                for family in foundry.families:
                    for font in family.fonts:
                        if font.uniqueID == ID:
                            return font
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def amountInstalledFonts(self):
        try:
            return len(self.installedFonts())
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def installedFonts(self):
        try:
            _list = []
            # Get font

            success, installabeFontsCommand = self.protocol.installableFontsCommand()

            for foundry in installabeFontsCommand.foundries:
                for family in foundry.families:
                    for font in family.fonts:
                        if self.installedFontVersion(font=font):
                            if font not in _list:
                                _list.append(font)
            return _list
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def expiringInstalledFonts(self):
        try:
            fonts = []
            # Get font

            success, installabeFontsCommand = self.protocol.installableFontsCommand()

            for foundry in installabeFontsCommand.foundries:
                for family in foundry.families:
                    for font in family.fonts:
                        if self.installedFontVersion(font=font) and font.expiry:
                            if font not in fonts:
                                fonts.append(font)
            return fonts
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def amountOutdatedFonts(self):
        try:
            return len(self.outdatedFonts())
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def outdatedFonts(self):
        try:
            _list = []

            success, installabeFontsCommand = self.protocol.installableFontsCommand()

            # Get font
            for foundry in installabeFontsCommand.foundries:
                for family in foundry.families:
                    for font in family.fonts:
                        installedFontVersion = self.installedFontVersion(font=font)
                        if installedFontVersion and installedFontVersion != font.getVersions()[-1].number:
                            if font not in _list:
                                _list.append(font.uniqueID)
            return _list
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def installedFontVersion(self, fontID=None, font=None):
        try:

            folder = self.parent.folder()

            if fontID and not font:
                font = self.fontByID(fontID)

            for version in font.getVersions():
                path = os.path.join(folder, self.uniqueID() + "-" + font.filename(version.number))
                if os.path.exists(path):
                    return version.number

        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    # def fontIsOutdated(self, fontID):

    # 	success, installabeFontsCommand = self.protocol.installableFontsCommand()

    # 	for foundry in installabeFontsCommand.foundries:
    # 		for family in foundry.families:
    # 			for font in family.fonts:
    # 				if font.uniqueID == fontID:

    # 					installedVersion = self.installedFontVersion(fontID)
    # 					return installedVersion and installedVersion != font.getVersions()[-1].number

    def removeFonts(self, fontIDs, dryRun=False, updateSubscription=True):
        try:
            success, installableFontsCommand = self.protocol.installableFontsCommand()

            uninstallTheseProtectedFontIDs = []
            uninstallTheseUnprotectedFontIDs = []

            folder = self.parent.folder()

            for fontID in fontIDs:

                path = None
                font = self.fontByID(fontID)
                installedFontVersion = self.installedFontVersion(font=font)
                if installedFontVersion:
                    path = os.path.join(
                        folder,
                        self.uniqueID() + "-" + font.filename(installedFontVersion),
                    )

                if not path and not dryRun:
                    return False, "Font path couldn’t be determined (preflight)"

                if font.protected:

                    self.parent.parent.delegate._fontWillUninstall(font)

                    # Test for permissions here
                    if not dryRun:
                        try:
                            if self.parent.parent.testScenario == "simulatePermissionError":
                                raise PermissionError
                            else:
                                if not os.path.exists(os.path.dirname(path)):
                                    os.makedirs(os.path.dirname(path))
                                f = open(path + ".test", "w")
                                f.write("test")
                                f.close()
                                os.remove(path + ".test")
                        except PermissionError:
                            self.parent.parent.delegate._fontHasInstalled(
                                False,
                                "Insufficient permission to uninstall font.",
                                font,
                            )
                            return False, "Insufficient permission to uninstall font."

                        assert os.path.exists(path + ".test") is False

                    uninstallTheseProtectedFontIDs.append(fontID)

                else:
                    uninstallTheseUnprotectedFontIDs.append(fontID)

            assert self.parent.parent == self.protocol.client
            assert self.parent.parent.testScenario == self.protocol.client.testScenario

            # Server access
            # Protected fonts
            if uninstallTheseProtectedFontIDs:

                success, payload = self.protocol.removeFonts(
                    uninstallTheseProtectedFontIDs,
                    updateSubscription=updateSubscription,
                )

                font = None
                if success:

                    # # Security check
                    # if set([x.uniqueID for x in payload.assets]) - set(fontIDs) or
                    # set(fontIDs) - set([x.uniqueID for x in payload.assets]):
                    # 	return False, 'Incoming fonts’ uniqueIDs mismatch with requested
                    #  font IDs.'

                    if len(payload.assets) == 0:
                        return (
                            False,
                            f"No fonts to uninstall in .assets, expected {len(uninstallTheseProtectedFontIDs)} assets",
                        )

                    # Process fonts
                    for incomingFont in payload.assets:

                        if incomingFont.uniqueID in fontIDs:

                            proceed = ["unknownInstallation", "unknownFont"]  #

                            if incomingFont.response in proceed:
                                pass

                            # Predefined response messages
                            elif incomingFont.response != "error" and incomingFont.response != "success":
                                return (
                                    False,
                                    [
                                        "#(response.%s)" % incomingFont.response,
                                        "#(response.%s.headline)" % incomingFont.response,
                                    ],
                                )

                            elif incomingFont.response == "error":
                                return False, incomingFont.errorMessage

                            if incomingFont.response == "success":

                                path = None
                                font = self.fontByID(incomingFont.uniqueID)
                                installedFontVersion = self.installedFontVersion(font=font)
                                if installedFontVersion:
                                    path = os.path.join(
                                        folder,
                                        self.uniqueID() + "-" + font.filename(installedFontVersion),
                                    )

                                if self.parent.parent.testScenario == "simulateNoPath":
                                    path = None

                                if not path and not dryRun:
                                    return (
                                        False,
                                        "Font path couldn’t be determined (deleting unprotected fonts)",
                                    )

                                if not dryRun:

                                    success, message = uninstall_font(path)
                                    if not success:
                                        return False, message

                                self.parent.parent.delegate._fontHasUninstalled(True, None, font)

                else:
                    self.parent.parent.delegate._fontHasUninstalled(False, payload, font)
                    return False, payload

            # Unprotected fonts
            if uninstallTheseUnprotectedFontIDs:

                for fontID in uninstallTheseUnprotectedFontIDs:

                    path = None
                    font = self.fontByID(fontID)
                    installedFontVersion = self.installedFontVersion(font=font)
                    if installedFontVersion:
                        path = os.path.join(
                            folder,
                            self.uniqueID() + "-" + font.filename(installedFontVersion),
                        )

                    if self.parent.parent.testScenario == "simulateNoPath":
                        path = None

                    if not path and not dryRun:
                        return (
                            False,
                            "Font path couldn’t be determined (deleting unprotected fonts)",
                        )

                    if not dryRun:

                        success, message = uninstall_font(path)
                        if not success:
                            return False, message

                    self.parent.parent.delegate._fontHasUninstalled(True, None, font)

            return True, None

        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def installFonts(self, fonts):
        try:

            success, installabeFontsCommand = self.protocol.installableFontsCommand()

            # Terms of Service
            if installabeFontsCommand.userIsVerified is False and self.get("acceptedTermsOfService") is not True:
                return (
                    False,
                    [
                        "#(response.termsOfServiceNotAccepted)",
                        "#(response.termsOfServiceNotAccepted.headline)",
                    ],
                )

            installTheseFontIDs = []
            protectedFonts = False
            versionByFont = {}

            folder = self.parent.folder()

            fontIDs = []

            for fontID, version in fonts:

                fontIDs.append(fontID)
                versionByFont[fontID] = version

                path = None
                font = self.fontByID(fontID)
                path = os.path.join(folder, self.uniqueID() + "-" + font.filename(version))
                if font.protected or font.expiry or font.expiryDuration:
                    protectedFonts = True

                assert path
                assert font

                self.parent.parent.delegate._fontWillInstall(font)

                # Test for permissions here
                try:
                    if self.parent.parent.testScenario == "simulatePermissionError":
                        raise PermissionError
                    else:
                        if not os.path.exists(os.path.dirname(path)):
                            os.makedirs(os.path.dirname(path))
                        f = open(path + ".test", "w")
                        f.write("test")
                        f.close()
                        os.remove(path + ".test")
                except PermissionError:
                    self.parent.parent.delegate._fontHasInstalled(
                        False, "Insufficient permission to install font.", font
                    )
                    return False, "Insufficient permission to install font."

                assert os.path.exists(path + ".test") is False

                installTheseFontIDs.append(fontID)

            # Server access
            success, payload = self.protocol.installFonts(fonts, updateSubscription=protectedFonts)

            font = None
            if success:

                # Check for empty assets
                if len(payload.assets) == 0:
                    return (
                        False,
                        f"No fonts to install in .assets, expected {len(installTheseFontIDs)} assets",
                    )

                # Check if all requested fonts and fontVersions
                # are present in the assets
                for fontID, version in fonts:
                    if not [fontID, version] in [[x.uniqueID, x.version] for x in payload.assets]:
                        return (
                            False,
                            f"Font {fontID} with version {version} not found in assets",
                        )

                # Process fonts
                for incomingFont in payload.assets:

                    if incomingFont.uniqueID in fontIDs:

                        if incomingFont.response == "error":
                            return False, incomingFont.errorMessage

                        # Predefined response messages
                        elif incomingFont.response != "error" and incomingFont.response != "success":
                            return (
                                False,
                                [
                                    "#(response.%s)" % incomingFont.response,
                                    "#(response.%s.headline)" % incomingFont.response,
                                ],
                            )

                        if incomingFont.response == "success":

                            path = None
                            font = self.fontByID(incomingFont.uniqueID)
                            path = os.path.join(
                                folder,
                                self.uniqueID() + "-" + font.filename(versionByFont[incomingFont.uniqueID]),
                            )
                            assert path

                            if not os.path.exists(os.path.dirname(path)):
                                os.makedirs(os.path.dirname(path))

                            if incomingFont.data and incomingFont.encoding:

                                success, message = install_font(path, base64.b64decode(incomingFont.data))
                                if not success:
                                    return False, message

                            elif incomingFont.dataURL:

                                (
                                    success,
                                    response,
                                    responseObject,
                                ) = self.parent.parent.performRequest(incomingFont.dataURL, method="GET")

                                if not success:
                                    return False, response

                                else:

                                    success, message = install_font(path, response)
                                    if not success:
                                        return False, message

                            self.parent.parent.delegate._fontHasInstalled(True, None, font)

                # Ping
                self.stillAlive()

                return True, None

            else:
                self.parent.parent.delegate._fontHasInstalled(False, payload, font)
                return False, payload

        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def update(self):
        try:
            self.parent._updatingSubscriptions.append(self.url)

            if self.parent.parent.online(self.protocol.url.restDomain.split("/")[0]):

                self.parent.parent.delegate._subscriptionWillUpdate(self)

                self.stillAlive()

                success, message, changes = self.protocol.update()

                if self.url in self.parent._updatingSubscriptions:
                    self.parent._updatingSubscriptions.remove(self.url)
                self._updatingProblem = None
                self.parent.parent._subscriptionsUpdated.append(self.url)

                if not success:
                    self.parent.parent.delegate._subscriptionHasBeenUpdated(self, success, message, changes)
                    return success, message, changes

                if changes:
                    self.save()

                # Success
                self.parent.parent.delegate._subscriptionHasBeenUpdated(self, True, None, changes)
                return True, None, changes

            else:
                self.parent._updatingSubscriptions.remove(self.url)
                self.parent.parent._subscriptionsUpdated.append(self.url)
                self._updatingProblem = [
                    "#(response.serverNotReachable)",
                    "#(response.serverNotReachable.headline)",
                ]

                self.parent.parent.delegate._subscriptionHasBeenUpdated(self, False, self._updatingProblem, False)

                return False, self._updatingProblem, False

        except Exception as e:  # nocoverage
            success, message = self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )
            return False, message, False

    def updatingProblem(self):
        try:
            return self._updatingProblem
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def get(self, key):
        try:
            preferences = dict(self.parent.parent.get("subscription(%s)" % self.protocol.unsecretURL()) or {})
            if key in preferences:

                o = preferences[key]

                if "Array" in o.__class__.__name__:
                    o = list(o)
                elif "Dictionary" in o.__class__.__name__:
                    o = dict(o)

                return o

        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def set(self, key, value):
        try:

            preferences = dict(self.parent.parent.get("subscription(%s)" % self.protocol.unsecretURL()) or {})
            preferences[key] = value
            self.parent.parent.set("subscription(%s)" % self.protocol.unsecretURL(), preferences)
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def remove(self, key):
        try:
            preferences = dict(self.parent.parent.get("subscription(%s)" % self.protocol.unsecretURL()) or {})
            if key in preferences:
                del preferences[key]
                self.parent.parent.set("subscription(%s)" % self.protocol.unsecretURL(), preferences)
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def save(self):
        try:
            subscriptions = self.parent.get("subscriptions") or []
            if not self.protocol.unsecretURL() in subscriptions:
                subscriptions.append(self.protocol.unsecretURL())
            self.parent.set("subscriptions", subscriptions)

            self.protocol.save()
        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def delete(self, calledFromParent=False, remotely=False):
        try:
            success, installabeFontsCommand = self.protocol.installableFontsCommand()

            # Delete all fonts
            for foundry in installabeFontsCommand.foundries:
                for family in foundry.families:
                    for font in family.fonts:
                        self.removeFonts([font.uniqueID])

            # Key
            try:
                self.protocol.deleteSecretKey()
            except Exception:
                pass

            # ZMQ
            self.parent.parent.unregisterZMQCallback(self.zmqTopic())

            # Resources
            self.parent.parent.delegate._subscriptionWillDelete(self)

            self.parent.parent.remove("subscription(%s)" % self.protocol.unsecretURL())

            # Subscriptions
            subscriptions = self.parent.get("subscriptions") or []
            subscriptions.remove(self.protocol.unsecretURL())
            self.parent.set("subscriptions", subscriptions)
            self.parent._subscriptions = {}

            # # currentSubscription
            # if self.parent.get('currentSubscription') == self.protocol.unsecretURL():
            # 	if len(subscriptions) >= 1:
            # 		self.parent.set('currentSubscription', subscriptions[0])

            self.parent._subscriptions = {}

            if len(subscriptions) == 0 and calledFromParent is False:
                self.parent.delete(calledFromSubscription=True)

            self.parent.parent.delegate._subscriptionHasBeenDeleted(
                self, withinPublisherDeletion=calledFromParent, remotely=remotely
            )
            self.parent.parent.manageMessageQueueConnection()

            if not remotely and not calledFromParent:
                self.parent.parent.uploadSubscriptions()

            return True, None

        except Exception as e:  # nocoverage
            self.parent.parent.handleTraceback(  # nocoverage
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def files(self):
        "Returns list of all resource URLs that the subscription may have loaded"
        files = []

        # Endpoint
        success, endpointCommand = self.protocol.endpointCommand()
        if success:
            if endpointCommand.logoURL:
                files.append(endpointCommand.logoURL)

        # Installable Fonts
        success, installableFontsCommand = self.protocol.installableFontsCommand()
        if success:
            for foundry in installableFontsCommand.foundries:

                # styling
                for theme in foundry.styling:
                    if "logoURL" in foundry.styling[theme]:
                        files.append(foundry.styling[theme]["logoURL"])

                for family in foundry.families:
                    for url in family.billboardURLs:
                        files.append(url)
                    for font in family.fonts:
                        for url in font.billboardURLs:
                            files.append(url)

        return list(set(files))
