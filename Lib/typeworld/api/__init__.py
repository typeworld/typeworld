# -*- coding: utf-8 -*-

import json
import copy
import types
import inspect
import re
import traceback
import datetime
import markdown2
import semver
import functools
import platform


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

#  Constants

VERSION = "0.2.3-beta"

WIN = platform.system() == "Windows"
MAC = platform.system() == "Darwin"
LINUX = platform.system() == "Linux"

# Response types (success, error, ...)
SUCCESS = "success"
ERROR = "error"

UNKNOWNFONT = "unknownFont"
INSUFFICIENTPERMISSION = "insufficientPermission"
SEATALLOWANCEREACHED = "seatAllowanceReached"
UNKNOWNINSTALLATION = "unknownInstallation"
NOFONTSAVAILABLE = "noFontsAvailable"
TEMPORARILYUNAVAILABLE = "temporarilyUnavailable"
VALIDTYPEWORLDUSERACCOUNTREQUIRED = "validTypeWorldUserAccountRequired"
REVEALEDUSERIDENTITYREQUIRED = "revealedUserIdentityRequired"
LOGINREQUIRED = "loginRequired"

PROTOCOLS = ["typeworld"]


RESPONSES = {
    SUCCESS: "The request has been processed successfully.",
    ERROR: (
        "There request produced an error. You may add a custom error "
        "message in the `errorMessage` field."
    ),
    UNKNOWNFONT: "No font could be identified for the given `fontID`.",
    INSUFFICIENTPERMISSION: (
        "The Type.World user account credentials "
        "couldn’t be confirmed by the publisher (which are checked with the "
        "central server) and therefore access to the subscription is denied."
    ),
    SEATALLOWANCEREACHED: (
        "The user has exhausted their seat allowances for "
        "this font. The app may take them to the publisher’s website as "
        "defined in ::LicenseUsage.upgradeURL:: to upgrade their font license."
    ),
    UNKNOWNINSTALLATION: (
        "This font installation (combination of app instance and user "
        "credentials) is unknown. The response with this error message is "
        "crucial to remote de-authorization of app instances. When a user "
        "de-authorizes an entire app instance’s worth of font installations, "
        "such as when a computer got bricked and re-installed or is lost, the "
        "success of the remote de-authorization process is judged by either "
        "`success` responses (app actually had this font installed and its "
        "deletion has been recorded) or `unknownInstallation` responses "
        "(app didn’t have this font installed). All other reponses count as "
        "errors in the remote de-authorization process."
    ),
    NOFONTSAVAILABLE: (
        "This subscription exists but carries " "no fonts at the moment."
    ),
    TEMPORARILYUNAVAILABLE: (
        "The service is temporarily unavailable " "but should work again later on."
    ),
    VALIDTYPEWORLDUSERACCOUNTREQUIRED: (
        "The access to this subscription requires a valid Type.World user "
        "account connected to an app."
    ),
    REVEALEDUSERIDENTITYREQUIRED: (
        "The access to this subscription requires a valid Type.World user "
        "account and that the user agrees to having their identity "
        "(name and email address) submitted to the publisher upon font "
        "installation (closed workgroups only)."
    ),
    LOGINREQUIRED: (
        "The access to this subscription requires that the user logs into "
        "the publisher’s website again to authenticate themselves. "
        "Normally, this happens after a subscription’s secret key has been "
        "invalidated. The user will be taken to the publisher’s website "
        "defined at ::EndpointResponse.loginURL::. After successful login, "
        "a button should be presented to the user to reconnect to the same "
        "subscription that they are trying to access. To identify the "
        "subscription, the link that the user will be taken to will carry a "
        "`subscriptionID` parameter with the subscriptionID as defined in "
        "the subscription’s URL."
    ),
}

# Commands
ENDPOINTCOMMAND = {
    "keyword": "endpoint",
    "currentVersion": VERSION,
    "responseTypes": [SUCCESS, ERROR],
    "acceptableMimeTypes": ["application/json"],
}
INSTALLABLEFONTSCOMMAND = {
    "keyword": "installableFonts",
    "currentVersion": VERSION,
    "responseTypes": [
        SUCCESS,
        ERROR,
        NOFONTSAVAILABLE,
        INSUFFICIENTPERMISSION,
        TEMPORARILYUNAVAILABLE,
        VALIDTYPEWORLDUSERACCOUNTREQUIRED,
    ],
    "acceptableMimeTypes": ["application/json"],
}
INSTALLFONTSCOMMAND = {
    "keyword": "installFonts",
    "currentVersion": VERSION,
    "responseTypes": [
        SUCCESS,
        ERROR,
        INSUFFICIENTPERMISSION,
        TEMPORARILYUNAVAILABLE,
        VALIDTYPEWORLDUSERACCOUNTREQUIRED,
        LOGINREQUIRED,
        REVEALEDUSERIDENTITYREQUIRED,
    ],
    "acceptableMimeTypes": ["application/json"],
}
UNINSTALLFONTSCOMMAND = {
    "keyword": "uninstallFonts",
    "currentVersion": VERSION,
    "responseTypes": [
        SUCCESS,
        ERROR,
        INSUFFICIENTPERMISSION,
        TEMPORARILYUNAVAILABLE,
        VALIDTYPEWORLDUSERACCOUNTREQUIRED,
        LOGINREQUIRED,
    ],
    "acceptableMimeTypes": ["application/json"],
}

INSTALLFONTASSETCOMMAND = {
    "responseTypes": [
        SUCCESS,
        ERROR,
        UNKNOWNFONT,
        INSUFFICIENTPERMISSION,
        TEMPORARILYUNAVAILABLE,
        VALIDTYPEWORLDUSERACCOUNTREQUIRED,
        LOGINREQUIRED,
        REVEALEDUSERIDENTITYREQUIRED,
        SEATALLOWANCEREACHED,
    ],
}
UNINSTALLFONTASSETCOMMAND = {
    "responseTypes": [
        SUCCESS,
        ERROR,
        UNKNOWNFONT,
        INSUFFICIENTPERMISSION,
        TEMPORARILYUNAVAILABLE,
        VALIDTYPEWORLDUSERACCOUNTREQUIRED,
        LOGINREQUIRED,
        UNKNOWNINSTALLATION,
    ],
}

COMMANDS = [
    ENDPOINTCOMMAND,
    INSTALLABLEFONTSCOMMAND,
    INSTALLFONTSCOMMAND,
    UNINSTALLFONTSCOMMAND,
]


FONTPURPOSES = {
    "desktop": {
        "acceptableMimeTypes": [
            "font/collection",
            "font/otf",
            "font/sfnt",
            "font/ttf",
        ],
    },
    "web": {"acceptableMimeTypes": ["application/zip"]},
    "app": {"acceptableMimeTypes": ["application/zip"]},
}

# https://tools.ietf.org/html/rfc8081

MIMETYPES = {
    "font/sfnt": {"fileExtensions": ["otf", "ttf"]},
    "font/ttf": {"fileExtensions": ["ttf"]},
    "font/otf": {"fileExtensions": ["otf"]},
    "font/collection": {"fileExtensions": ["ttc"]},
    "font/woff": {"fileExtensions": ["woff"]},
    "font/woff2": {"fileExtensions": ["woff2"]},
}

# Compile list of file extensions
FILEEXTENSIONS = []
for mimeType in list(MIMETYPES.keys()):
    FILEEXTENSIONS = list(
        set(FILEEXTENSIONS) | set(MIMETYPES[mimeType]["fileExtensions"])
    )

FILEEXTENSIONNAMES = {
    "otf": "OpenType",
    "ttf": "TrueType",
    "ttc": "TrueType collection",
    "woff": "WOFF",
    "woff2": "WOFF2",
}

MIMETYPEFORFONTTYPE = {
    "otf": "font/otf",
    "ttf": "font/ttf",
    "ttc": "font/collection",
    "woff": "font/woff",
    "woff2": "font/woff2",
}

FONTENCODINGS = ["base64"]

OPENSOURCELICENSES = [
    "0BSD",
    "AAL",
    "Abstyles",
    "Adobe-2006",
    "Adobe-Glyph",
    "ADSL",
    "AFL-1.1",
    "AFL-1.2",
    "AFL-2.0",
    "AFL-2.1",
    "AFL-3.0",
    "Afmparse",
    "AGPL-1.0",
    "AGPL-3.0-only",
    "AGPL-3.0-or-later",
    "Aladdin",
    "AMDPLPA",
    "AML",
    "AMPAS",
    "ANTLR-PD",
    "Apache-1.0",
    "Apache-1.1",
    "Apache-2.0",
    "APAFML",
    "APL-1.0",
    "APSL-1.0",
    "APSL-1.1",
    "APSL-1.2",
    "APSL-2.0",
    "Artistic-1.0-cl8",
    "Artistic-1.0-Perl",
    "Artistic-1.0",
    "Artistic-2.0",
    "Bahyph",
    "Barr",
    "Beerware",
    "BitTorrent-1.0",
    "BitTorrent-1.1",
    "Borceux",
    "BSD-1-Clause",
    "BSD-2-Clause-FreeBSD",
    "BSD-2-Clause-NetBSD",
    "BSD-2-Clause-Patent",
    "BSD-2-Clause",
    "BSD-3-Clause-Attribution",
    "BSD-3-Clause-Clear",
    "BSD-3-Clause-LBNL",
    "BSD-3-Clause-No-Nuclear-License-2014",
    "BSD-3-Clause-No-Nuclear-License",
    "BSD-3-Clause-No-Nuclear-Warranty",
    "BSD-3-Clause",
    "BSD-4-Clause-UC",
    "BSD-4-Clause",
    "BSD-Protection",
    "BSD-Source-Code",
    "BSL-1.0",
    "bzip2-1.0.5",
    "bzip2-1.0.6",
    "Caldera",
    "CATOSL-1.1",
    "CC-BY-1.0",
    "CC-BY-2.0",
    "CC-BY-2.5",
    "CC-BY-3.0",
    "CC-BY-4.0",
    "CC-BY-NC-1.0",
    "CC-BY-NC-2.0",
    "CC-BY-NC-2.5",
    "CC-BY-NC-3.0",
    "CC-BY-NC-4.0",
    "CC-BY-NC-ND-1.0",
    "CC-BY-NC-ND-2.0",
    "CC-BY-NC-ND-2.5",
    "CC-BY-NC-ND-3.0",
    "CC-BY-NC-ND-4.0",
    "CC-BY-NC-SA-1.0",
    "CC-BY-NC-SA-2.0",
    "CC-BY-NC-SA-2.5",
    "CC-BY-NC-SA-3.0",
    "CC-BY-NC-SA-4.0",
    "CC-BY-ND-1.0",
    "CC-BY-ND-2.0",
    "CC-BY-ND-2.5",
    "CC-BY-ND-3.0",
    "CC-BY-ND-4.0",
    "CC-BY-SA-1.0",
    "CC-BY-SA-2.0",
    "CC-BY-SA-2.5",
    "CC-BY-SA-3.0",
    "CC-BY-SA-4.0",
    "CC0-1.0",
    "CDDL-1.0",
    "CDDL-1.1",
    "CDLA-Permissive-1.0",
    "CDLA-Sharing-1.0",
    "CECILL-1.0",
    "CECILL-1.1",
    "CECILL-2.0",
    "CECILL-2.1",
    "CECILL-B",
    "CECILL-C",
    "ClArtistic",
    "CNRI-Jython",
    "CNRI-Python-GPL-Compatible",
    "CNRI-Python",
    "Condor-1.1",
    "CPAL-1.0",
    "CPL-1.0",
    "CPOL-1.02",
    "Crossword",
    "CrystalStacker",
    "CUA-OPL-1.0",
    "Cube",
    "curl",
    "D-FSL-1.0",
    "diffmark",
    "DOC",
    "Dotseqn",
    "DSDP",
    "dvipdfm",
    "ECL-1.0",
    "ECL-2.0",
    "EFL-1.0",
    "EFL-2.0",
    "eGenix",
    "Entessa",
    "EPL-1.0",
    "EPL-2.0",
    "ErlPL-1.1",
    "EUDatagrid",
    "EUPL-1.0",
    "EUPL-1.1",
    "EUPL-1.2",
    "Eurosym",
    "Fair",
    "Frameworx-1.0",
    "FreeImage",
    "FSFAP",
    "FSFUL",
    "FSFULLR",
    "FTL",
    "GFDL-1.1-only",
    "GFDL-1.1-or-later",
    "GFDL-1.2-only",
    "GFDL-1.2-or-later",
    "GFDL-1.3-only",
    "GFDL-1.3-or-later",
    "Giftware",
    "GL2PS",
    "Glide",
    "Glulxe",
    "gnuplot",
    "GPL-1.0-only",
    "GPL-1.0-or-later",
    "GPL-2.0-only",
    "GPL-2.0-or-later",
    "GPL-3.0-only",
    "GPL-3.0-or-later",
    "gSOAP-1.3b",
    "HaskellReport",
    "HPND",
    "IBM-pibs",
    "ICU",
    "IJG",
    "ImageMagick",
    "iMatix",
    "Imlib2",
    "Info-ZIP",
    "Intel-ACPI",
    "Intel",
    "Interbase-1.0",
    "IPA",
    "IPL-1.0",
    "ISC",
    "JasPer-2.0",
    "JSON",
    "LAL-1.2",
    "LAL-1.3",
    "Latex2e",
    "Leptonica",
    "LGPL-2.0-only",
    "LGPL-2.0-or-later",
    "LGPL-2.1-only",
    "LGPL-2.1-or-later",
    "LGPL-3.0-only",
    "LGPL-3.0-or-later",
    "LGPLLR",
    "Libpng",
    "libtiff",
    "LiLiQ-P-1.1",
    "LiLiQ-R-1.1",
    "LiLiQ-Rplus-1.1",
    "LPL-1.0",
    "LPL-1.02",
    "LPPL-1.0",
    "LPPL-1.1",
    "LPPL-1.2",
    "LPPL-1.3a",
    "LPPL-1.3c",
    "MakeIndex",
    "MirOS",
    "MIT-advertising",
    "MIT-CMU",
    "MIT-enna",
    "MIT-feh",
    "MIT",
    "MITNFA",
    "Motosoto",
    "mpich2",
    "MPL-1.0",
    "MPL-1.1",
    "MPL-2.0-no-copyleft-exception",
    "MPL-2.0",
    "MS-PL",
    "MS-RL",
    "MTLL",
    "Multics",
    "Mup",
    "NASA-1.3",
    "Naumen",
    "NBPL-1.0",
    "NCSA",
    "Net-SNMP",
    "NetCDF",
    "Newsletr",
    "NGPL",
    "NLOD-1.0",
    "NLPL",
    "Nokia",
    "NOSL",
    "Noweb",
    "NPL-1.0",
    "NPL-1.1",
    "NPOSL-3.0",
    "NRL",
    "NTP",
    "OCCT-PL",
    "OCLC-2.0",
    "ODbL-1.0",
    "OFL-1.0",
    "OFL-1.1",
    "OGTSL",
    "OLDAP-1.1",
    "OLDAP-1.2",
    "OLDAP-1.3",
    "OLDAP-1.4",
    "OLDAP-2.0.1",
    "OLDAP-2.0",
    "OLDAP-2.1",
    "OLDAP-2.2.1",
    "OLDAP-2.2.2",
    "OLDAP-2.2",
    "OLDAP-2.3",
    "OLDAP-2.4",
    "OLDAP-2.5",
    "OLDAP-2.6",
    "OLDAP-2.7",
    "OLDAP-2.8",
    "OML",
    "OpenSSL",
    "OPL-1.0",
    "OSET-PL-2.1",
    "OSL-1.0",
    "OSL-1.1",
    "OSL-2.0",
    "OSL-2.1",
    "OSL-3.0",
    "PDDL-1.0",
    "PHP-3.0",
    "PHP-3.01",
    "Plexus",
    "PostgreSQL",
    "psfrag",
    "psutils",
    "Python-2.0",
    "Qhull",
    "QPL-1.0",
    "Rdisc",
    "RHeCos-1.1",
    "RPL-1.1",
    "RPL-1.5",
    "RPSL-1.0",
    "RSA-MD",
    "RSCPL",
    "Ruby",
    "SAX-PD",
    "Saxpath",
    "SCEA",
    "Sendmail",
    "SGI-B-1.0",
    "SGI-B-1.1",
    "SGI-B-2.0",
    "SimPL-2.0",
    "SISSL-1.2",
    "SISSL",
    "Sleepycat",
    "SMLNJ",
    "SMPPL",
    "SNIA",
    "Spencer-86",
    "Spencer-94",
    "Spencer-99",
    "SPL-1.0",
    "SugarCRM-1.1.3",
    "SWL",
    "TCL",
    "TCP-wrappers",
    "TMate",
    "TORQUE-1.1",
    "TOSL",
    "Unicode-DFS-2015",
    "Unicode-DFS-2016",
    "Unicode-TOU",
    "Unlicense",
    "UPL-1.0",
    "Vim",
    "VOSTROM",
    "VSL-1.0",
    "W3C-19980720",
    "W3C-20150513",
    "W3C",
    "Watcom-1.0",
    "Wsuipa",
    "WTFPL",
    "X11",
    "Xerox",
    "XFree86-1.1",
    "xinetd",
    "Xnet",
    "xpp",
    "XSkat",
    "YPL-1.0",
    "YPL-1.1",
    "Zed",
    "Zend-2.0",
    "Zimbra-1.3",
    "Zimbra-1.4",
    "zlib-acknowledgement",
    "Zlib",
    "ZPL-1.1",
    "ZPL-2.0",
    "ZPL-2.1",
]

FONTSTATUSES = ["prerelease", "trial", "stable"]

PUBLISHERSIDEAPPANDUSERCREDENTIALSTATUSES = ["active", "deleted", "revoked"]

DEFAULT = "__default__"


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

#  Helper methods


def makeSemVer(version):
    """Turn simple float number (0.1) into semver-compatible number
    for comparison by adding .0(s): (0.1.0)"""

    # Make string
    version = str(version)

    if version.count(".") < 2:

        # Strip leading zeros
        version = ".".join(map(str, list(map(int, version.split(".")))))

        # Add .0(s)
        version = version + (2 - version.count(".")) * ".0"

    return version


def ResponsesDocu(responses):

    text = "\n\n"

    for response in responses:

        text += "`%s`: %s\n\n" % (response, RESPONSES[response])

    return text


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

#  Basic Data Types


class DataType(object):
    initialData = None
    dataType = None

    def __init__(self):
        self.value = copy.copy(self.initialData)

        if issubclass(self.__class__, (MultiLanguageText, MultiLanguageTextProxy)):
            self.value = self.dataType()

    def __repr__(self):
        if issubclass(self.__class__, Proxy):
            return "<%s>" % (self.dataType.__name__)
        else:
            return "<%s '%s'>" % (self.__class__.__name__, self.get())

    def valid(self):
        if not self.value:
            return True

        if type(self.value) == self.dataType:
            return True
        else:
            return "Wrong data type. Is %s, should be: %s." % (
                type(self.value),
                self.dataType,
            )

    def get(self):
        return self.value

    def put(self, value):

        self.value = self.shapeValue(value)

        if issubclass(
            self.value.__class__, (DictBasedObject, ListProxy, Proxy, DataType)
        ):
            object.__setattr__(self.value, "_parent", self)

        valid = self.valid()
        if valid is not True and valid is not None:
            raise ValueError(valid)

    def shapeValue(self, value):
        return value

    def isEmpty(self):
        return self.value is None or self.value == [] or self.value == ""

    def isSet(self):
        return not self.isEmpty()

    def formatHint(self):
        return None

    def exampleData(self):
        return None


class BooleanDataType(DataType):
    dataType = bool


class IntegerDataType(DataType):
    dataType = int

    def shapeValue(self, value):
        return int(value)


class FloatDataType(DataType):
    dataType = float

    def shapeValue(self, value):
        return float(value)


class StringDataType(DataType):
    dataType = str

    def shapeValue(self, value):
        return str(value)


class DictionaryDataType(DataType):
    dataType = dict

    def shapeValue(self, value):
        return dict(value)


class FontDataType(StringDataType):
    pass


class FontEncodingDataType(StringDataType):
    def valid(self):
        if not self.value:
            return True

        if self.value not in FONTENCODINGS:
            return "Encoding '%s' is unknown. Known are: %s" % (
                self.value,
                FONTENCODINGS,
            )

        return True


class VersionDataType(StringDataType):
    dataType = str

    def valid(self):
        if not self.value:
            return True

        # Append .0 for semver comparison
        try:
            value = makeSemVer(self.value)
        except ValueError:
            return False

        try:
            semver.parse(value)
        except ValueError as e:
            return str(e)
        return True

    def formatHint(self):
        return (
            "Simple float number (1 or 1.01) or semantic versioning "
            "(2.0.0-rc.1) as per [semver.org](https://semver.org)"
        )


class TimestampDataType(IntegerDataType):
    pass


class DateDataType(StringDataType):
    def valid(self):
        if not self.value:
            return True

        try:
            datetime.datetime.strptime(self.value, "%Y-%m-%d")
            return True

        except ValueError:
            return traceback.format_exc().splitlines()[-1]

    def formatHint(self):
        return "YYYY-MM-DD"


class WebURLDataType(StringDataType):
    def valid(self):
        if not self.value:
            return True

        if not self.value.startswith("http://") and not self.value.startswith(
            "https://"
        ):
            return "Needs to start with http:// or https://"
        else:
            return True


class TelephoneDataType(StringDataType):
    def valid(self):
        if not self.value:
            return True

        text = "Needs to start with + and contain only numbers 0-9"

        match = re.match(r"(\+[0-9]+)", self.value)
        if match:
            match = self.value.replace(match.group(), "")
            if match:
                return text
        else:
            return text

        return True

    def formatHint(self):
        return "+1234567890"


class WebResourceURLDataType(WebURLDataType):
    def formatHint(self):
        return (
            "This resource may get downloaded and cached on the client "
            "computer. To ensure up-to-date resources, append a unique ID "
            "to the URL such as a timestamp of the resources’s upload on your "
            "server, e.g. "
            "https://awesomefonts.com/xyz/regular/specimen.pdf?t=1548239062"
        )


class EmailDataType(StringDataType):
    def valid(self):
        if not self.value:
            return True
        if (
            "@" in self.value
            and "." in self.value
            and self.value.find(".", self.value.find("@")) > 0
            and self.value.count("@") == 1
            and self.value.find("..") == -1
        ):

            return True
        else:
            return "Not a valid email format: %s" % self.value


class HexColorDataType(StringDataType):
    def valid(self):
        if not self.value:
            return True
        if (len(self.value) == 3 or len(self.value) == 6) and re.match(
            "^[A-Fa-f0-9]*$", self.value
        ):

            return True
        else:
            return (
                "Not a valid hex color of format RRGGBB "
                "(like FF0000 for red): %s" % self.value
            )

    def formatHint(self):
        return "Hex RRGGBB (without leading #)"


class ListProxy(DataType):
    initialData = []

    # Data type of each list member
    # Here commented out to enforce explicit setting of data type
    # for each Proxy
    # dataType = str

    def __repr__(self):
        if self.value:
            return "%s" % ([x.get() for x in self.value])
        else:
            return "[]"

    def __getitem__(self, i):
        return self.value[i].get()

    def __setitem__(self, i, value):

        if issubclass(value.__class__, (DictBasedObject, Proxy, ListProxy, DataType)):
            object.__setattr__(value, "_parent", self)

        self.value[i].put(value)
        object.__setattr__(self.value[i], "_parent", self)

    def __delitem__(self, i):
        del self.value[i]

    def __iter__(self):
        for element in self.value:
            yield element.get()

    def __len__(self):
        return len(self.value)

    def index(self, item):
        return [x.get() for x in self.value].index(item)

    def get(self):
        return self

    def put(self, values):

        if not type(values) in (list, tuple):
            raise ValueError(
                "Wrong data type. Is %s, should be: %s." % (type(values), list)
            )

        self.value = []
        for value in values:
            self.append(value)

    def append(self, value):

        newData = self.dataType()
        newData.put(value)

        self.value.append(newData)

        if issubclass(newData.__class__, (DictBasedObject, Proxy, ListProxy, DataType)):
            object.__setattr__(newData, "_parent", self)

    def extend(self, values):
        for value in values:
            self.append(value)

    def remove(self, removeValue):
        for i, value in enumerate(self.value):
            if self[i] == removeValue:
                del self[i]

    # def valid(self):

    #     if self.value:
    #         for data in self.value:
    #             valid = data.valid()
    #             return valid
    #     return True


class DictBasedObject(object):
    _structure = {}
    _deprecatedKeys = []
    _possible_keys = []
    _dataType_for_possible_keys = None

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        obj = cls()
        obj.loadJSON(self.dumpJSON())
        return obj

    def sameContent(self, other):
        return self.difference(other) == {}

    def difference(self, other):
        from deepdiff import DeepDiff

        return DeepDiff(self.dumpDict(), other.dumpDict(), ignore_order=True)

    def nonListProxyBasedKeys(self):

        _list = []

        for keyword in self._structure.keys():
            if ListProxy not in inspect.getmro(self._structure[keyword][0]):
                _list.append(keyword)

        _list.extend(self._deprecatedKeys)

        return _list

    def linkDocuText(self, text):
        def my_replace(match):
            match = match.group()
            match = match[2:-2]

            if "." in match:
                className, attributeName = match.split(".")

                if "()" in attributeName:
                    attributeName = attributeName[:-2]
                    match = "[%s.%s()](#user-content-class-%s-method-%s)" % (
                        className,
                        attributeName,
                        className.lower(),
                        attributeName.lower(),
                    )
                else:
                    match = "[%s.%s](#user-content-class-%s-attribute-%s)" % (
                        className,
                        attributeName,
                        className.lower(),
                        attributeName.lower(),
                    )
            else:
                className = match
                match = "[%s](#user-content-class-%s)" % (className, className.lower(),)

            return match

        try:
            text = re.sub(r"::.+?::", my_replace, text)
        except Exception:
            pass

        return text or ""

    def typeDescription(self, class_):

        if issubclass(class_, ListProxy):
            return "List of %s objects" % self.typeDescription(class_.dataType)

        elif class_.dataType in (
            dict,
            list,
            tuple,
            str,
            bytes,
            set,
            frozenset,
            bool,
            int,
            float,
        ):
            return class_.dataType.__name__.capitalize()

        elif "" in ("%s" % class_.dataType):
            return self.linkDocuText("::%s::" % class_.dataType.__name__)

        # Seems unused

        # elif 'typeworld.api.' in ("%s" % class_.dataType):
        #     return self.linkDocuText('::%s::' % class_.dataType.__name__)

        # else:
        #     return class_.dataType.__name__.title()

    def additionalDocu(self):

        doc = ""

        if hasattr(self, "sample"):

            doc += f"""*Example JSON data:*
```json
{self.sample().dumpJSON(strict = False)}
```

"""

        return doc

    def docu(self):

        classes = []

        # Define string
        docstring = ""
        head = ""
        attributes = ""
        methods = ""
        attributesList = []
        methodsList = []

        head += '<div id="class-%s"></div>\n\n' % self.__class__.__name__.lower()

        head += "# _class_ %s()\n\n" % self.__class__.__name__

        head += self.linkDocuText(inspect.getdoc(self))

        head += "\n\n"

        additionalDocu = self.additionalDocu()
        if additionalDocu:

            head += additionalDocu + "\n\n"

        # attributes

        attributes += "## Attributes\n\n"

        for key in sorted(self._structure.keys()):

            attributesList.append(key)
            attributes += '<div id="class-%s-attribute-%s"></div>\n\n' % (
                self.__class__.__name__.lower(),
                key,
            )
            attributes += "### %s\n\n" % key

            # Description
            if self._structure[key][3]:
                attributes += self.linkDocuText(self._structure[key][3]) + "\n\n"

            attributes += "__Required:__ %s" % self._structure[key][1] + "<br />\n"

            attributes += (
                "__Type:__ %s" % self.typeDescription(self._structure[key][0])
                + "<br />\n"
            )

            # Format Hint
            hint = self._structure[key][0]().formatHint()
            if hint:
                attributes += "__Format:__ %s" % hint + "<br />\n"

            if self._structure[key][2] is not None:
                attributes += "__Default value:__ %s" % self._structure[key][2] + "\n\n"

            # Example Data
            example = self._structure[key][0]().exampleData()
            if example:
                attributes += "Example:\n"
                attributes += "```json\n"
                attributes += json.dumps(example, indent=4)
                attributes += "\n```\n"

        method_list = [
            func
            for func in dir(self)
            if callable(getattr(self, func))
            and not func.startswith("__")
            and inspect.getdoc(getattr(self, func))
        ]

        if method_list:
            methods += "## Methods\n\n"

            for methodName in method_list:

                methodsList.append(methodName)
                methods += '<div id="class-%s-method-%s"></div>\n\n' % (
                    self.__class__.__name__.lower(),
                    methodName.lower(),
                )

                args = inspect.getfullargspec(getattr(self, methodName))
                if args.args != ["self"]:

                    argList = []
                    if args.args and args.defaults:

                        startPoint = len(args.args) - len(args.defaults)
                        for i, defaultValue in enumerate(args.defaults):
                            argList.append(
                                "%s = %s" % (args.args[i + startPoint], defaultValue)
                            )

                    methods += "#### %s(%s)\n\n" % (methodName, ", ".join(argList),)
                else:
                    methods += "#### %s()\n\n" % methodName
                methods += (
                    self.linkDocuText(inspect.getdoc(getattr(self, methodName)))
                    + "\n\n"
                )

        # Compile
        docstring += head

        # TOC
        if attributesList:
            docstring += "### Attributes\n\n"
            for attribute in attributesList:
                docstring += "[%s](#class-%s-attribute-%s)<br />" % (
                    attribute,
                    self.__class__.__name__.lower(),
                    attribute.lower(),
                )
            docstring += "\n\n"

        if methodsList:
            docstring += "### Methods\n\n"
            for methodName in methodsList:
                docstring += "[%s()](#class-%s-method-%s)<br />" % (
                    methodName,
                    self.__class__.__name__.lower(),
                    methodName.lower(),
                )
            docstring += "\n\n"

        if attributesList:
            docstring += attributes
            docstring += "\n\n"

        if methodsList:
            docstring += methods
            docstring += "\n\n"

        # Add data
        classes.append([self.__class__.__name__, docstring])

        # Recurse
        for key in list(self._structure.keys()):
            if issubclass(self._structure[key][0], Proxy):

                o = self._structure[key][0].dataType()
                classes.extend(o.docu())

            if issubclass(self._structure[key][0], ListProxy):

                o = self._structure[key][0].dataType.dataType()
                if hasattr(o, "docu"):
                    classes.extend(o.docu())

        return classes

    def __init__(self, json=None, dict=None):

        super(DictBasedObject, self).__init__()

        object.__setattr__(self, "_content", {})
        object.__setattr__(
            self,
            "_allowedKeys",
            set(self._structure.keys()) | set(self._possible_keys),
        )

        # Fill default values
        for key in self._structure:

            # Set default values
            if self._structure[key][2] is not None:
                setattr(self, key, self._structure[key][2])

        if json:
            self.loadJSON(json)
        elif dict:
            self.loadDict(dict)

    def initAttr(self, key):

        if key not in self._content:

            if key in list(object.__getattribute__(self, "_structure").keys()):
                self._content[key] = object.__getattribute__(self, "_structure")[key][
                    0
                ]()

            elif key in self._possible_keys:
                self._content[key] = self._dataType_for_possible_keys()

            self._content[key]._parent = self

    def __getattr__(self, key):

        if key in self._allowedKeys:
            self.initAttr(key)
            return self._content[key].get()

        else:
            return object.__getattribute__(self, key)

    def __setattr__(self, key, value):

        if key in self._allowedKeys:
            self.initAttr(key)

            if issubclass(
                value.__class__, (DictBasedObject, ListProxy, Proxy, DataType)
            ):
                object.__setattr__(value, "_parent", self)

            self.__dict__["_content"][key].put(value)

        else:
            object.__setattr__(self, key, value)

    def set(self, key, value):
        self.__setattr__(key, value)

    def get(self, key):
        return self.__getattr__(key)

    def validate(self, strict=True):

        information = []
        warnings = []
        critical = []

        def extendWithKey(values, key=None, sourceObject=None):

            # Remove duplicates
            seen = set()
            seen_add = seen.add
            values = [x for x in values if not (x in seen or seen_add(x))]
            #                values = list(set(values))

            _list = []
            for value in values:
                if sourceObject and key:
                    _list.append(
                        "%s.%s --> %s --> %s" % (self, key, sourceObject, value)
                    )
                elif key:
                    _list.append("%s.%s --> %s" % (self, key, value))
                else:
                    _list.append("%s --> %s" % (self, value))
            return _list

        # Check if required fields are filled
        for key in list(self._structure.keys()):

            self.initAttr(key)

            if self.discardThisKey(key) is False:

                if strict and self._structure[key][1] and self._content[key].isEmpty():
                    critical.append(
                        "%s.%s is a required attribute, but empty" % (self, key)
                    )

                else:

                    # recurse
                    if issubclass(self._content[key].__class__, (Proxy)):

                        if self._content[key].isEmpty() is False:
                            (newInformation, newWarnings, newCritical,) = self._content[
                                key
                            ].value.validate(strict=strict)
                            information.extend(extendWithKey(newInformation, key))
                            warnings.extend(extendWithKey(newWarnings, key))
                            critical.extend(extendWithKey(newCritical, key))

                            # Check custom messages:
                            if hasattr(
                                self._content[key].value, "customValidation"
                            ) and isinstance(
                                self._content[key].value.customValidation,
                                types.MethodType,
                            ):
                                (
                                    newInformation,
                                    newWarnings,
                                    newCritical,
                                ) = self._content[key].value.customValidation()
                                information.extend(
                                    extendWithKey(
                                        newInformation, key, self._content[key]
                                    )
                                )
                                warnings.extend(
                                    extendWithKey(newWarnings, key, self._content[key])
                                )
                                critical.extend(
                                    extendWithKey(newCritical, key, self._content[key])
                                )

                    # recurse
                    if issubclass(self._content[key].__class__, (ListProxy)):

                        if self._content[key].isEmpty() is False:
                            for item in self._content[key]:
                                if hasattr(item, "validate") and isinstance(
                                    item.validate, types.MethodType
                                ):
                                    (
                                        newInformation,
                                        newWarnings,
                                        newCritical,
                                    ) = item.validate(strict=strict)
                                    information.extend(
                                        extendWithKey(newInformation, key)
                                    )
                                    warnings.extend(extendWithKey(newWarnings, key))
                                    critical.extend(extendWithKey(newCritical, key))

                                # Check custom messages:
                                if hasattr(item, "customValidation") and isinstance(
                                    item.customValidation, types.MethodType
                                ):
                                    (
                                        newInformation,
                                        newWarnings,
                                        newCritical,
                                    ) = item.customValidation()
                                    information.extend(
                                        extendWithKey(newInformation, key, item)
                                    )
                                    warnings.extend(
                                        extendWithKey(newWarnings, key, item)
                                    )
                                    critical.extend(
                                        extendWithKey(newCritical, key, item)
                                    )

        # Check custom messages:
        if (
            issubclass(self.__class__, BaseResponse)
            and hasattr(self, "customValidation")
            and isinstance(self.customValidation, types.MethodType)
        ):
            newInformation, newWarnings, newCritical = self.customValidation()
            information.extend(extendWithKey(newInformation))
            warnings.extend(extendWithKey(newWarnings))
            critical.extend(extendWithKey(newCritical))

        return information, warnings, critical

    def discardThisKey(self, key):
        return False

    def dumpDict(self, strict=True):

        d = {}

        # Auto-validate
        information, warnings, critical = self.validate(strict=strict)
        if critical:
            raise ValueError(critical[0])

        for key in list(self._content.keys()):

            if self.discardThisKey(key) is False:

                # if required or not empty
                if (
                    (key in self._structure and self._structure[key][1])
                    or getattr(self, key)
                    or (
                        hasattr(getattr(self, key), "isSet")
                        and getattr(self, key).isSet()
                    )
                ):

                    if hasattr(getattr(self, key), "dumpDict"):
                        d[key] = getattr(self, key).dumpDict(strict=strict)

                    elif issubclass(getattr(self, key).__class__, (ListProxy)):
                        d[key] = list(getattr(self, key))

                        if len(d[key]) > 0 and hasattr(d[key][0], "dumpDict"):
                            d[key] = [x.dumpDict(strict=strict) for x in d[key]]

                    else:
                        d[key] = getattr(self, key)

        return d

    def loadDict(self, d):

        for key in list(d.keys()):
            if key in self._allowedKeys:

                if key in list(self._structure.keys()):

                    if issubclass(self._structure[key][0], (Proxy)):

                        try:
                            exec(
                                "self.%s = typeworld.api.%s()"
                                % (key, self._structure[key][0].dataType.__name__,)
                            )
                        except Exception:
                            exec(
                                "self.%s = %s()"
                                % (key, self._structure[key][0].dataType.__name__,)
                            )
                        exec("self.%s.loadDict(d[key])" % (key))
                    elif issubclass(self._structure[key][0], (ListProxy)):
                        _list = self.__getattr__(key)
                        for item in d[key]:
                            o = self._structure[key][0].dataType.dataType()

                            if hasattr(o, "loadDict"):
                                o.loadDict(item)
                                _list.append(o)
                            else:
                                _list.append(item)
                        exec("self._content[key] = _list")

                    else:
                        self.set(key, d[key])

    def dumpJSON(self, strict=True):
        return json.dumps(self.dumpDict(strict=strict), indent=4, sort_keys=True)

    def loadJSON(self, j):
        self.loadDict(json.loads(j))


class Proxy(DataType):
    pass


class ResponseCommandDataType(StringDataType):
    def formatHint(self):
        return (
            "To ensure the proper function of the entire Type.World protocol, "
            "your API endpoint *must* return the proper responses as per "
            "[this flow chart](https://type.world/documentation/Type.World%20"
            "Request%20Flow%20Chart.pdf). "
            "In addition to ensure functionality, this enables the response "
            "messages displayed to the user to be translated into all the "
            "possible languages on our side."
        )


class MultiLanguageText(DictBasedObject):
    """\
Multi-language text. Attributes are language keys as per
[https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes]

The GUI app will then calculate the language data to be displayed using
::MultiLanguageText.getText():: with a prioritized list of languages that
the user can understand. They may be pulled from the operating system’s
language preferences.

These classes are already initiated wherever they are used, and can be
addresses instantly with the language attributes:

```python
api.name.en = u'Font Publisher XYZ'
api.name.de = u'Schriftenhaus XYZ'
```

If you are loading language information from an external source, you may use
the `.set()` method to enter data:

```python
# Simulating external data source
for languageCode, text in (
        ('en': u'Font Publisher XYZ'),
        ('de': u'Schriftenhaus XYZ'),
    )
    api.name.set(languageCode, text)
```

Neither HTML nor Markdown code is permitted in `MultiLanguageText`.
"""

    _possible_keys = [
        "ab",
        "aa",
        "af",
        "ak",
        "sq",
        "am",
        "ar",
        "an",
        "hy",
        "as",
        "av",
        "ae",
        "ay",
        "az",
        "bm",
        "ba",
        "eu",
        "be",
        "bn",
        "bh",
        "bi",
        "bs",
        "br",
        "bg",
        "my",
        "ca",
        "ch",
        "ce",
        "ny",
        "zh",
        "cv",
        "kw",
        "co",
        "cr",
        "hr",
        "cs",
        "da",
        "dv",
        "nl",
        "dz",
        "en",
        "eo",
        "et",
        "ee",
        "fo",
        "fj",
        "fi",
        "fr",
        "ff",
        "gl",
        "ka",
        "de",
        "el",
        "gn",
        "gu",
        "ht",
        "ha",
        "he",
        "hz",
        "hi",
        "ho",
        "hu",
        "ia",
        "id",
        "ie",
        "ga",
        "ig",
        "ik",
        "io",
        "is",
        "it",
        "iu",
        "ja",
        "jv",
        "kl",
        "kn",
        "kr",
        "ks",
        "kk",
        "km",
        "ki",
        "rw",
        "ky",
        "kv",
        "kg",
        "ko",
        "ku",
        "kj",
        "la",
        "lb",
        "lg",
        "li",
        "ln",
        "lo",
        "lt",
        "lu",
        "lv",
        "gv",
        "mk",
        "mg",
        "ms",
        "ml",
        "mt",
        "mi",
        "mr",
        "mh",
        "mn",
        "na",
        "nv",
        "nd",
        "ne",
        "ng",
        "nb",
        "nn",
        "no",
        "ii",
        "nr",
        "oc",
        "oj",
        "cu",
        "om",
        "or",
        "os",
        "pa",
        "pi",
        "fa",
        "pl",
        "ps",
        "pt",
        "qu",
        "rm",
        "rn",
        "ro",
        "ru",
        "sa",
        "sc",
        "sd",
        "se",
        "sm",
        "sg",
        "sr",
        "gd",
        "sn",
        "si",
        "sk",
        "sl",
        "so",
        "st",
        "es",
        "su",
        "sw",
        "ss",
        "sv",
        "ta",
        "te",
        "tg",
        "th",
        "ti",
        "bo",
        "tk",
        "tl",
        "tn",
        "to",
        "tr",
        "ts",
        "tt",
        "tw",
        "ty",
        "ug",
        "uk",
        "ur",
        "uz",
        "ve",
        "vi",
        "vo",
        "wa",
        "cy",
        "wo",
        "fy",
        "xh",
        "yi",
        "yo",
        "za",
        "zu",
    ]
    _dataType_for_possible_keys = StringDataType
    _length = 100
    _markdownAllowed = False

    # def __repr__(self):
    #     return '<MultiLanguageText>'

    def __str__(self):
        return str(self.getText())

    def __bool__(self):
        return bool(self.getText())

    def sample(self):
        o = self.__class__()
        o.en = "Text in English"
        o.de = "Text auf Deutsch"
        return o

    def getTextAndLocale(self, locale=["en"]):
        """Like getText(), but additionally returns the language of whatever
        text was found first."""

        if type(locale) in (str, str):
            if self.get(locale):
                return self.get(locale), locale

        elif type(locale) in (list, tuple):
            for key in locale:
                if self.get(key):
                    return self.get(key), key

        # try english
        if self.get("en"):
            return self.get("en"), "en"

        # try anything
        for key in self._possible_keys:
            if self.get(key):
                return self.get(key), key

        return None, None

    def getText(self, locale=["en"]):
        """Returns the text in the first language found from the specified
        list of languages. If that language can’t be found, we’ll try English
        as a standard. If that can’t be found either, return the first language
        you can find."""

        text, locale = self.getTextAndLocale(locale)

        return text

    def customValidation(self):

        information, warnings, critical = [], [], []

        if self.isEmpty():
            critical.append("Needs to contain at least one language field")

        # Check for text length
        for langId in self._possible_keys:
            if self.get(langId):
                string = self.get(langId)
                if len(string) > self._length:
                    critical.append(
                        (
                            "Language entry '%s' is too long. "
                            "Allowed are %s characters."
                        )
                        % (langId, self._length)
                    )

                if re.findall(r"(<.+?>)", string):
                    if self._markdownAllowed:
                        critical.append(
                            (
                                "String contains HTML code, which is not "
                                "allowed. You may use Markdown for text "
                                "formatting."
                            )
                        )
                    else:
                        critical.append(
                            "String contains HTML code, which is not allowed."
                        )

                if (
                    not self._markdownAllowed
                    and string
                    and "<p>" + string + "</p>\n" != markdown2.markdown(string)
                ):
                    critical.append(
                        "String contains Markdown code, which is not allowed."
                    )

        return information, warnings, critical

    def isSet(self):
        return not self.isEmpty()

    def isEmpty(self):

        # Check for existence of languages
        hasAtLeastOneLanguage = False
        for langId in self._possible_keys:
            if langId in self._content and self.getText([langId]) is not None:
                hasAtLeastOneLanguage = True
                break

        return not hasAtLeastOneLanguage

    def loadDict(self, d):
        for key in d:
            self.set(key, d[key])


def MultiLanguageText_Parent(self):
    if hasattr(self, "_parent") and hasattr(self._parent, "_parent"):
        return self._parent._parent


MultiLanguageText.parent = property(lambda self: MultiLanguageText_Parent(self))


class MultiLanguageTextProxy(Proxy):
    dataType = MultiLanguageText

    def isEmpty(self):
        return self.value.isEmpty()

    def formatHint(self):
        text = "Maximum allowed characters: %s." % self.dataType._length
        if self.dataType._markdownAllowed:
            text += " Mardown code is permitted for text formatting."
        return text


class MultiLanguageTextListProxy(ListProxy):
    dataType = MultiLanguageTextProxy


###############################################################################


class MultiLanguageLongText(MultiLanguageText):
    """\
Multi-language text. Attributes are language keys as per
[https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes]

The GUI app will then calculate the language data to be displayed using
::MultiLanguageText.getText():: with a prioritized list of languages that
the user can understand. They may be pulled from the operating system’s
language preferences.

These classes are already initiated wherever they are used, and can be
addresses instantly with the language attributes:

```python
api.name.en = u'Font Publisher XYZ'
api.name.de = u'Schriftenhaus XYZ'
```

If you are loading language information from an external source, you may use
the `.set()` method to enter data:

```python
# Simulating external data source
for languageCode, text in (
        ('en': u'Font Publisher XYZ'),
        ('de': u'Schriftenhaus XYZ'),
    )
    api.name.set(languageCode, text)
```

Neither HTML nor Markdown code is permitted in `MultiLanguageText`.
"""

    _length = 3000
    _markdownAllowed = True


class MultiLanguageLongTextProxy(MultiLanguageTextProxy):
    dataType = MultiLanguageLongText


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

#  Top-Level Data Types


class LanguageSupportDataType(DictionaryDataType):
    def valid(self):
        if not self.value:
            return True
        for script in self.value:
            if not len(script) == 4 or not script.islower():
                return "Script tag '%s' needs to be a four-letter lowercase tag." % (
                    script
                )

            for language in self.value[script]:
                if not len(language) == 3 or not language.isupper():
                    return (
                        "Language tag '%s' needs to be a " "three-letter uppercase tag."
                    ) % (language)

        return True


class OpenTypeFeatureDataType(StringDataType):
    def valid(self):
        if not self.value:
            return True

        if not len(self.value) == 4 or not self.value.islower():
            return (
                "OpenType feature tag '%s' needs to be a " "four-letter lowercase tag."
            ) % (self.value)

        return True


class OpenTypeFeatureListProxy(ListProxy):
    dataType = OpenTypeFeatureDataType


class OpenSourceLicenseIdentifierDataType(StringDataType):
    def valid(self):
        if not self.value:
            return True

        if self.value in OPENSOURCELICENSES:
            return True
        else:
            return (
                "Unknown license identifier: '%s'. " "See https://spdx.org/licenses/"
            ) % (self.value)


class SupportedAPICommandsDataType(StringDataType):

    commands = [x["keyword"] for x in COMMANDS]

    def valid(self):
        if not self.value:
            return True

        if self.value in self.commands:
            return True
        else:
            return "Unknown API command: '%s'. Possible: %s" % (
                self.value,
                self.commands,
            )


class SupportedAPICommandsListProxy(ListProxy):
    dataType = SupportedAPICommandsDataType


class FontPurposeDataType(StringDataType):
    def valid(self):
        if not self.value:
            return True

        if self.value in list(FONTPURPOSES.keys()):
            return True
        else:
            return "Unknown font type: '%s'. Possible: %s" % (
                self.value,
                list(FONTPURPOSES.keys()),
            )


class FontMimeType(StringDataType):
    def valid(self):
        if not self.value:
            return True

        if self.value in list(FONTPURPOSES["desktop"]["acceptableMimeTypes"]):
            return True
        else:
            return "Unknown font MIME Type: '%s'. Possible: %s" % (
                self.value,
                list(FONTPURPOSES["desktop"]["acceptableMimeTypes"]),
            )


class FontStatusDataType(StringDataType):

    statuses = FONTSTATUSES

    def valid(self):
        if not self.value:
            return True

        if self.value in self.statuses:
            return True
        else:
            return "Unknown Font Status: '%s'. Possible: %s" % (
                self.value,
                self.statuses,
            )


class FontExtensionDataType(StringDataType):
    def valid(self):
        if not self.value:
            return True

        found = False

        for mimeType in list(MIMETYPES.keys()):
            if self.value in MIMETYPES[mimeType]["fileExtensions"]:
                found = True
                break

        if found:
            return True
        else:

            return "Unknown font extension: '%s'. Possible: %s" % (
                self.value,
                FILEEXTENSIONS,
            )


###############################################################################

#  LicenseDefinition


class LicenseDefinition(DictBasedObject):
    #   key:  [data type, required, default value, description]
    _structure = {
        "keyword": [
            StringDataType,
            True,
            None,
            (
                "Machine-readable keyword under which the license will be "
                "referenced from the individual fonts."
            ),
        ],
        "name": [
            MultiLanguageTextProxy,
            True,
            None,
            "Human-readable name of font license",
        ],
        "URL": [
            WebURLDataType,
            True,
            None,
            "URL where the font license text can be viewed online",
        ],
    }

    def __repr__(self):
        return "<LicenseDefinition '%s'>" % self.name or self.keyword or "undefined"

    def sample(self):
        o = self.__class__()
        o.keyword = "awesomefontsEULA"
        o.name.en = "Awesome Fonts End User License Agreement"
        o.name.de = "Awesome Fonts Endnutzerlizenzvereinbarung"
        o.URL = "https://awesomefonts.com/eula.html"
        return o


def LicenseDefinition_Parent(self):
    if (
        hasattr(self, "_parent")
        and hasattr(self._parent, "_parent")
        and hasattr(self._parent._parent, "_parent")
    ):
        return self._parent._parent._parent


LicenseDefinition.parent = property(lambda self: LicenseDefinition_Parent(self))


class LicenseDefinitionProxy(Proxy):
    dataType = LicenseDefinition


class LicenseDefinitionListProxy(ListProxy):
    dataType = LicenseDefinitionProxy


###############################################################################

#  FontPackage


class FontPackage(DictBasedObject):
    """\
    `FontPackages` are groups of fonts that serve a certain purpose
    to the user.
    They can be defined at ::InstallableFontsReponse.packages::,
    ::Foundry.packages::, ::Family.packages::
    and are referenced by their keywords in ::Font.packageKeywords::.

    On a font family level, defined at ::Family.packages::, a typical example
    for defining a `FontPackage` would be the so called **Office Fonts**.
    While they are technically identical to other OpenType fonts, they normally
    have a sightly different set of glyphs and OpenType features.
    Linking them to a `FontPackage` allows the UI to display them clearly as a
    separate set of fonts that serve a different purpuse than the
    regular fonts.

    On a subscription-wide level, defined at
    ::InstallableFontsReponse.packages::, a `FontPackage` could represent a
    curated collection of fonts of various foundries and families, for example
    **Script Fonts** or **Brush Fonts** or **Corporate Fonts**.

    Each font may be part of several `FontPackages`.

    For the time being, only family-level FontPackages are supported in the UI.
    """

    #   key:  [data type, required, default value, description]
    _structure = {
        "keyword": [
            StringDataType,
            True,
            None,
            (
                "Keyword of font packages. This keyword must be referenced in "
                "::Font.packageKeywords:: and must be unique to this subscription."
            ),
        ],
        "name": [MultiLanguageTextProxy, True, None, "Name of package"],
        "description": [MultiLanguageTextProxy, False, None, "Description"],
    }

    def __repr__(self):
        return "<FontPackage '%s'>" % self.keyword or "undefined"

    def sample(self):
        o = self.__class__()
        o.keyword = "officefonts"
        o.name.en = "Office Fonts"
        o.name.de = "Office-Schriften"
        o.description.en = (
            "These fonts are produced specifically to be used in "
            "Office applications."
        )
        o.description.de = (
            "Diese Schriftdateien sind für die Benutzung in "
            "Office-Applikationen vorgesehen."
        )
        return o

    def getFormats(self):
        formats = []
        if hasattr(self, "fonts"):
            for font in self.fonts:
                if font.format not in formats:
                    formats.append(font.format)

        return formats


class FontPackageProxy(Proxy):
    dataType = FontPackage


class FontPackageListProxy(ListProxy):
    dataType = FontPackageProxy


class FontPackageReferencesListProxy(ListProxy):
    dataType = StringDataType


###############################################################################

#  LicenseUsage


class LicenseUsage(DictBasedObject):
    #   key:  [data type, required, default value, description]
    _structure = {
        "keyword": [
            StringDataType,
            True,
            None,
            (
                "Keyword reference of font’s license. This license must be "
                "specified in ::Foundry.licenses::"
            ),
        ],
        "seatsAllowed": [
            IntegerDataType,
            False,
            0,
            (
                "In case of desktop font (see ::Font.purpose::), number of "
                "installations permitted by the user’s license."
            ),
        ],
        "seatsInstalled": [
            IntegerDataType,
            False,
            0,
            (
                "In case of desktop font (see ::Font.purpose::), number of "
                "installations recorded by the API endpoint. This value will "
                "need to be supplied dynamically by the API endpoint through "
                "tracking all font installations through the `anonymousAppID` "
                "parameter of the '%s' and '%s' command. Please note that the "
                "Type.World client app is currently not designed to reject "
                "installations of the fonts when the limits are exceeded. "
                "Instead it is in the responsibility of the API endpoint to "
                "reject font installations though the '%s' command when the "
                "limits are exceeded. In that case the user will be presented "
                "with one or more license upgrade links."
            )
            % (
                INSTALLFONTSCOMMAND["keyword"],
                UNINSTALLFONTSCOMMAND["keyword"],
                INSTALLFONTSCOMMAND["keyword"],
            ),
        ],
        "allowanceDescription": [
            MultiLanguageTextProxy,
            False,
            None,
            (
                "In case of non-desktop font (see ::Font.purpose::), custom "
                "string for web fonts or app fonts reminding the user of the "
                "license’s limits, e.g. '100.000 page views/month'"
            ),
        ],
        "upgradeURL": [
            WebURLDataType,
            False,
            None,
            (
                "URL the user can be sent to to upgrade the license of the "
                "font, for instance at the foundry’s online shop. If "
                "possible, this link should be user-specific and guide "
                "him/her as far into the upgrade process as possible."
            ),
        ],
        "dateAddedForUser": [
            DateDataType,
            False,
            None,
            (
                "Date that the user has purchased this font or the font has "
                "become available to the user otherwise (like a new font "
                "within a foundry’s beta font repository). Will be used in "
                "the UI to signal which fonts have become newly available "
                "in addition to previously available fonts. This is not to "
                "be confused with the ::Version.releaseDate::, although they "
                "could be identical."
            ),
        ],
    }

    def sample(self):
        o = self.__class__()
        o.keyword = "awesomefontsEULA"
        o.seatsAllowed = 5
        o.seatsInstalled = 2
        o.upgradeURL = "https://awesomefonts.com/shop/upgradelicense/083487263904356"
        return o

    def __repr__(self):
        return "<LicenseUsage '%s'>" % self.keyword or "undefined"

    def customValidation(self):
        information, warnings, critical = [], [], []

        # Checking for existing license
        if self.keyword and not self.getLicense():
            critical.append(
                "Has license '%s', but %s has no matching license."
                % (self.keyword, self.parent.parent.parent)
            )

        return information, warnings, critical

    def getLicense(self):
        """\
        Returns the ::License:: object that this font references.
        """
        return self.parent.parent.parent.getLicenseByKeyword(self.keyword)


def LicenseUsage_Parent(self):
    if (
        hasattr(self, "_parent")
        and hasattr(self._parent, "_parent")
        and hasattr(self._parent._parent, "_parent")
    ):
        return self._parent._parent._parent


LicenseUsage.parent = property(lambda self: LicenseUsage_Parent(self))


class LicenseUsageProxy(Proxy):
    dataType = LicenseUsage


class LicenseUsageListProxy(ListProxy):
    dataType = LicenseUsageProxy


#######################################################################################

#  Designer


class Designer(DictBasedObject):
    #   key:                    [data type, required, default value, description]
    _structure = {
        "keyword": [
            StringDataType,
            True,
            None,
            (
                "Machine-readable keyword under which the designer will be referenced "
                "from the individual fonts or font families"
            ),
        ],
        "name": [
            MultiLanguageTextProxy,
            True,
            None,
            "Human-readable name of designer",
        ],
        "websiteURL": [WebURLDataType, False, None, "Designer’s web site"],
        "description": [
            MultiLanguageLongTextProxy,
            False,
            None,
            "Description of designer",
        ],
    }

    def sample(self):
        o = self.__class__()
        o.keyword = "johndoe"
        o.name.en = "John Doe"
        o.websiteURL = "https://johndoe.com"
        return o

    def __repr__(self):
        return "<Designer '%s'>" % self.name.getText() or self.keyword or "undefined"


def Designer_Parent(self):
    if (
        hasattr(self, "_parent")
        and hasattr(self._parent, "_parent")
        and hasattr(self._parent._parent, "_parent")
    ):
        return self._parent._parent._parent


Designer.parent = property(lambda self: Designer_Parent(self))


class DesignerProxy(Proxy):
    dataType = Designer


class DesignersListProxy(ListProxy):
    dataType = DesignerProxy


class DesignersReferencesListProxy(ListProxy):
    dataType = StringDataType


########################################################################################

#  Font Family Version


class Version(DictBasedObject):
    #   key:                    [data type, required, default value, description]
    _structure = {
        "number": [
            VersionDataType,
            True,
            None,
            (
                "Font version number. This can be a simple float number (1.002) or a "
                "semver version string (see https://semver.org). For comparison, "
                "single-dot version numbers (or even integers) are appended with "
                "another .0 (1.0 to 1.0.0), then compared using the Python `semver` "
                "module."
            ),
        ],
        "description": [
            MultiLanguageLongTextProxy,
            False,
            None,
            "Description of font version",
        ],
        "releaseDate": [DateDataType, False, None, "Font version’s release date."],
    }

    def sample(self):
        o = self.__class__()
        o.number = "1.2"
        o.description.en = "Added capital SZ and Turkish Lira sign"
        o.description.de = "Versal-SZ und türkisches Lira-Zeichen hinzugefügt"
        o.releaseDate = "2020-05-21"
        return o

    def __repr__(self):
        return "<Version %s (%s)>" % (
            self.number if self.number else "None",
            "font-specific" if self.isFontSpecific() else "family-specific",
        )

    def isFontSpecific(self):
        """\
        Returns True if this version is defined at the font level.
        Returns False if this version is defined at the family level.
        """
        return issubclass(self.parent.__class__, Font)


def Version_Parent(self):
    if (
        hasattr(self, "_parent")
        and hasattr(self._parent, "_parent")
        and hasattr(self._parent._parent, "_parent")
    ):
        return self._parent._parent._parent


Version.parent = property(lambda self: Version_Parent(self))


class VersionProxy(Proxy):
    dataType = Version


class VersionListProxy(ListProxy):
    dataType = VersionProxy


########################################################################################

#  Fonts


class Font(DictBasedObject):
    #   key:                    [data type, required, default value, description]
    _structure = {
        "name": [
            MultiLanguageTextProxy,
            True,
            None,
            (
                "Human-readable name of font. This may include any additions that you "
                "find useful to communicate to your users."
            ),
        ],
        "uniqueID": [
            StringDataType,
            True,
            None,
            (
                "A machine-readable string that uniquely identifies this font within "
                "the publisher. It will be used to ask for un/installation of the "
                "font from the server in the `installFonts` and `uninstallFonts` "
                "commands. Also, it will be used for the file name of the font on "
                "disk, together with the version string and the file extension. "
                "Together, they must not be longer than 220 characters and must "
                "not contain the following characters: / ? < > \\ : * | ^"
            ),
        ],
        "postScriptName": [
            StringDataType,
            True,
            None,
            "Complete PostScript name of font",
        ],
        "packageKeywords": [
            FontPackageReferencesListProxy,
            False,
            None,
            "List of references to ::FontPackage:: objects by their keyword",
        ],
        "versions": [
            VersionListProxy,
            False,
            None,
            (
                "List of ::Version:: objects. These are font-specific versions; they "
                "may exist only for this font. You may define additional versions at "
                "the family object under ::Family.versions::, which are then expected "
                "to be available for the entire family. However, either the fonts or "
                "the font family *must* carry version information and the validator "
                "will complain when they don’t.\n\nPlease also read the section on "
                "[versioning](#versioning) above."
            ),
        ],
        "designerKeywords": [
            DesignersReferencesListProxy,
            False,
            None,
            (
                "List of keywords referencing designers. These are defined at "
                "::InstallableFontsResponse.designers::. This attribute overrides the "
                "designer definitions at the family level at ::Family.designers::."
            ),
        ],
        "free": [BooleanDataType, False, None, "Font is freeware. For UI signaling"],
        "status": [
            FontStatusDataType,
            True,
            "stable",
            "Font status. For UI signaling. Possible values are: %s" % FONTSTATUSES,
        ],
        "variableFont": [
            BooleanDataType,
            False,
            None,
            "Font is an OpenType Variable Font. For UI signaling",
        ],
        "purpose": [
            FontPurposeDataType,
            True,
            None,
            (
                "Technical purpose of font. This influences how the app handles the "
                "font. For instance, it will only install desktop fonts on the system, "
                "and make other font types available though folders. Possible: %s"
                % (list(FONTPURPOSES.keys()))
            ),
        ],
        "format": [
            FontExtensionDataType,
            False,
            None,
            (
                "Font file format. Required value in case of `desktop` font "
                "(see ::Font.purpose::. Possible: %s" % FILEEXTENSIONS
            ),
        ],
        "protected": [
            BooleanDataType,
            False,
            False,
            (
                "Indication that the server requires a valid subscriptionID to be used "
                "for authentication. The server *may* limit the downloads of fonts. "
                "This may also be used for fonts that are free to download, but their "
                "installations want to be tracked/limited anyway. Most importantly, "
                "this indicates that the uninstall command needs to be called on the "
                "API endpoint when the font gets uninstalled."
            ),
        ],
        "dateFirstPublished": [
            DateDataType,
            False,
            None,
            (
                "Human readable date of the initial release of the font. May also be "
                "defined family-wide at ::Family.dateFirstPublished::."
            ),
        ],
        "usedLicenses": [
            LicenseUsageListProxy,
            True,
            None,
            (
                "List of ::LicenseUsage:: objects. These licenses represent the "
                "different ways in which a user has access to this font. At least one "
                "used license must be defined here, because a user needs to know under "
                "which legal circumstances he/she is using the font. Several used "
                "licenses may be defined for a single font in case a customer owns "
                "several licenses that cover the same font. For instance, a customer "
                "could have purchased a font license standalone, but also as part of "
                "the foundry’s entire catalogue. It’s important to keep these separate "
                "in order to provide the user with separate upgrade links where he/she "
                "needs to choose which of several owned licenses needs to be upgraded. "
                "Therefore, in case of a commercial retail foundry, used licenses "
                "correlate to a user’s purchase history."
            ),
        ],
        "pdfURL": [
            WebResourceURLDataType,
            False,
            None,
            (
                "URL of PDF file with type specimen and/or instructions for this "
                "particular font. (See also: ::Family.pdf::"
            ),
        ],
        "expiry": [
            TimestampDataType,
            False,
            None,
            (
                "Unix timestamp of font’s expiry. The font will be deleted on that "
                "moment. This could be set either upon initial installation of a trial "
                "font, or also before initial installation as a general expiry moment."
            ),
        ],
        "expiryDuration": [
            IntegerDataType,
            False,
            None,
            (
                "Minutes for which the user will be able to use the font after initial "
                "installation. This attribute is used only as a visual hint in the UI "
                "and should be set for trial fonts that expire a certain period after "
                "initial installation, such as 60 minutes. If the font is a trial font "
                "limited to a certain usage period after initial installation, it must "
                "also be marked as ::Font.protected::, with no ::Font.expiry:: "
                "timestamp set at first (because the expiry depends on the moment of "
                "initial installation). On initial font installation by the user, the "
                "publisher’s server needs to record that moment’s time, and from there "
                "onwards serve the subscription with ::Font.expiry:: attribute set in "
                "the future. Because the font is marked as ::Font.protected::, the app "
                "will update the subscription directly after font installation, upon "
                "when it will learn of the newly added ::Font.expiry:: attribute. "
                "Please note that you *have* to set ::Font.expiry:: after initial "
                "installation yourself. The Type.World app will not follow up on its "
                "own on installed fonts just with the ::Font.expiryDuration:: "
                "attribute, which is used only for display."
            ),
        ],
        "features": [
            OpenTypeFeatureListProxy,
            False,
            None,
            (
                "List of supported OpenType features as per "
                "https://docs.microsoft.com/en-us/typography/opentype/spec/featuretags"
            ),
        ],
        "languageSupport": [
            LanguageSupportDataType,
            False,
            None,
            "Dictionary of suppported languages as script/language combinations",
        ],
    }

    def __repr__(self):
        return "<Font '%s'>" % (
            self.postScriptName or self.name.getText() or "undefined"
        )

    def sample(self):
        o = self.__class__()
        o.name.en = "Bold"
        o.name.de = "Fette"
        o.uniqueID = "AwesomeFonts-AwesomeFamily-Bold"
        o.postScriptName = "AwesomeFamily-Bold"
        o.purpose = "desktop"
        return o

    def filename(self, version):
        """\
        Returns the recommended font file name to be used to store the font on disk.

        It is composed of the font’s uniqueID, its version string and the file
        extension. Together, they must not exceed 220 characters.
        """

        if not type(version) in (str, int, float):
            raise ValueError("Supplied version must be str or int or float")

        if self.format:
            return "%s_%s.%s" % (self.uniqueID, version, self.format)
        else:
            return "%s_%s" % (self.uniqueID, version)

    def hasVersionInformation(self):
        return self.versions or self.parent.versions

    def customValidation(self):
        information, warnings, critical = [], [], []

        # Checking font type/extension
        if self.purpose == "desktop" and not self.format:
            critical.append(
                "Is a desktop font (see .purpose), but has no .format value."
            )

        # Checking version information
        if not self.hasVersionInformation():
            critical.append(
                (
                    "Has no version information, and neither has its family %s. "
                    "Either one needs to carry version information." % (self.parent)
                )
            )

        # Checking for designers
        for designerKeyword in self.designerKeywords:
            if not self.parent.parent.parent.getDesignerByKeyword(designerKeyword):
                critical.append(
                    "Has designer '%s', but %s.designers has no matching designer."
                    % (designerKeyword, self.parent.parent.parent)
                )

        # Checking uniqueID for file name contradictions:
        forbidden = "/?<>\\:*|^,;"
        for char in forbidden:
            if self.uniqueID.count(char) > 0:
                critical.append(
                    (
                        ".uniqueID must not contain the character '%s' because it will "
                        "be used for the font’s file name on disk." % char
                    )
                )

        for version in self.getVersions():
            filename = self.filename(version.number)
            if len(filename) > 220:
                critical.append(
                    "The suggested file name is longer than 220 characters: %s"
                    % filename
                )

        return information, warnings, critical

    def getVersions(self):
        """\
        Returns list of ::Version:: objects.

        This is the final list based on the version information in this font object as
        well as in its parent ::Family:: object. Please read the section about
        [versioning](#versioning) above.
        """

        if not self.hasVersionInformation():
            raise ValueError(
                (
                    "%s has no version information, and neither has its family %s. "
                    "Either one needs to carry version information."
                    % (self, self.parent)
                )
            )

        def compare(a, b):
            return semver.compare(makeSemVer(a.number), makeSemVer(b.number))

        versions = []
        haveVersionNumbers = []
        for version in self.versions:
            versions.append(version)
            haveVersionNumbers.append(makeSemVer(version.number))
        for version in self.parent.versions:
            if version.number not in haveVersionNumbers:
                versions.append(version)
                haveVersionNumbers.append(makeSemVer(version.number))

        versions = sorted(versions, key=functools.cmp_to_key(compare))

        return versions

    def getDesigners(self):
        """\
        Returns a list of ::Designer:: objects that this font references.
        These are the combination of family-level designers and font-level designers.
        The same logic as for versioning applies.
        Please read the section about [versioning](#versioning) above.
        """
        if not hasattr(self, "_designers"):
            self._designers = []

            # Family level designers
            if self.parent.designerKeywords:
                for designerKeyword in self.parent.designerKeywords:
                    self._designers.append(
                        self.parent.parent.parent.getDesignerByKeyword(designerKeyword)
                    )

            # Font level designers
            if self.designerKeywords:
                for designerKeyword in self.designerKeywords:
                    self._designers.append(
                        self.parent.parent.parent.getDesignerByKeyword(designerKeyword)
                    )

        return self._designers

    def getPackageKeywords(self):
        if self.packageKeywords:
            return list(set(self.packageKeywords))
        else:
            return [DEFAULT]


def Font_Parent(self):
    if (
        hasattr(self, "_parent")
        and hasattr(self._parent, "_parent")
        and hasattr(self._parent._parent, "_parent")
    ):
        return self._parent._parent._parent


Font.parent = property(lambda self: Font_Parent(self))


class FontProxy(Proxy):
    dataType = Font


class FontListProxy(ListProxy):
    dataType = FontProxy


# Font Family


class BillboardListProxy(ListProxy):
    dataType = WebResourceURLDataType


class Family(DictBasedObject):
    #   key:                    [data type, required, default value, description]
    _structure = {
        "uniqueID": [
            StringDataType,
            True,
            None,
            "An string that uniquely identifies this family within the publisher.",
        ],
        "name": [
            MultiLanguageTextProxy,
            True,
            None,
            (
                "Human-readable name of font family. This may include any additions "
                "that you find useful to communicate to your users."
            ),
        ],
        "description": [
            MultiLanguageLongTextProxy,
            False,
            None,
            "Description of font family",
        ],
        "billboardURLs": [
            BillboardListProxy,
            False,
            None,
            (
                "List of URLs pointing at images to show for this typeface. These must "
                "be uncompressed SVG images. It is suggested to use square dimensions, "
                "but it’s not compulsory. It’s unclear at this point how pixel data in "
                "the SVG will be displayed in the app on the two different operating "
                "systems Mac and Windows."
            ),
        ],
        "designerKeywords": [
            DesignersReferencesListProxy,
            False,
            None,
            (
                "List of keywords referencing designers. These are defined at "
                "::InstallableFontsResponse.designers::. In case designers differ "
                "between fonts within the same family, they can also be defined at the "
                "font level at ::Font.designers::. The font-level references take "
                "precedence over the family-level references."
            ),
        ],
        "packages": [
            FontPackageListProxy,
            False,
            None,
            (
                "Family-wide list of ::FontPackage:: objects. These will be "
                "referenced by their keyword in ::Font.packageKeywords::"
            ),
        ],
        "sourceURL": [
            WebURLDataType,
            False,
            None,
            "URL pointing to the source of a font project, such as a GitHub repository",
        ],
        "issueTrackerURL": [
            WebURLDataType,
            False,
            None,
            (
                "URL pointing to an issue tracker system, where users can debate "
                "about a typeface’s design or technicalities"
            ),
        ],
        "galleryURL": [
            WebURLDataType,
            False,
            None,
            (
                "URL pointing to a web site that shows real world examples of the "
                "fonts in use or other types of galleries."
            ),
        ],
        "versions": [
            VersionListProxy,
            False,
            None,
            (
                "List of ::Version:: objects. Versions specified here are expected to "
                "be available for all fonts in the family, which is probably most "
                "common and efficient. You may define additional font-specific "
                "versions at the ::Font:: object. You may also rely entirely on "
                "font-specific versions and leave this field here empty. However, "
                "either the fonts or the font family *must* carry version information "
                "and the validator will complain when they don’t.\n\nPlease also read "
                "the section on [versioning](#versioning) above."
            ),
        ],
        "fonts": [
            FontListProxy,
            True,
            None,
            (
                "List of ::Font:: objects. The order will be displayed unchanged in "
                "the UI, so it’s in your responsibility to order them correctly."
            ),
        ],
        "dateFirstPublished": [
            DateDataType,
            False,
            None,
            (
                "Human readable date of the initial release of the family. May be "
                "overriden on font level at ::Font.dateFirstPublished::."
            ),
        ],
        "pdfURL": [
            WebResourceURLDataType,
            False,
            None,
            (
                "URL of PDF file with type specimen and/or instructions for entire "
                "family. May be overriden on font level at ::Font.pdf::."
            ),
        ],
    }

    def sample(self):
        o = self.__class__()
        o.name.en = "Awesome Family"
        o.description.en = "Nice big fat face with smooth corners"
        o.description.de = "Fette Groteske mit runden Ecken"
        o.uniqueID = "AwesomeFonts-AwesomeFamily"
        return o

    def __repr__(self):
        return "<Family '%s'>" % self.name.getText() or "undefined"

    def customValidation(self):
        information, warnings, critical = [], [], []

        # Checking for designers
        for designerKeyword in self.designerKeywords:
            if not self.parent.parent.getDesignerByKeyword(designerKeyword):
                critical.append(
                    "Has designer '%s', but %s.designers has no matching designer."
                    % (designerKeyword, self.parent.parent)
                )

        return information, warnings, critical

    def getDesigners(self):
        if not hasattr(self, "_designers"):
            self._designers = []
            for designerKeyword in self.designerKeywords:
                self._designers.append(
                    self.parent.parent.getDesignerByKeyword(designerKeyword)
                )
        return self._designers

    def getAllDesigners(self):
        """\
        Returns a list of ::Designer:: objects that represent all of the designers
        referenced both at the family level as well as with all the family’s fonts,
        in case the fonts carry specific designers. This could be used to give a
        one-glance overview of all designers involved.
        """
        if not hasattr(self, "_allDesigners"):
            self._allDesigners = []
            self._allDesignersKeywords = []
            for designerKeyword in self.designerKeywords:
                self._allDesigners.append(
                    self.parent.parent.getDesignerByKeyword(designerKeyword)
                )
                self._allDesignersKeywords.append(designerKeyword)
            for font in self.fonts:
                for designerKeyword in font.designerKeywords:
                    if designerKeyword not in self._allDesignersKeywords:
                        self._allDesigners.append(
                            self.parent.parent.getDesignerByKeyword(designerKeyword)
                        )
                        self._allDesignersKeywords.append(designerKeyword)
        return self._allDesigners

    def getPackages(self):

        packageKeywords = []
        packages = []
        packageByKeyword = {}

        # Collect list of unique package keyword references in family's fonts
        for font in self.fonts:
            for keyword in font.getPackageKeywords():
                if keyword not in packageKeywords:
                    packageKeywords.append(keyword)

        # Prepend a DEFAULT package
        if DEFAULT in packageKeywords:
            defaultPackage = FontPackage()
            defaultPackage.keyword = DEFAULT
            defaultPackage.name.en = DEFAULT
            packages.append(defaultPackage)
            packageByKeyword[DEFAULT] = defaultPackage

        # Build list of FontPackage objects
        for package in self.packages:
            if package.keyword in packageKeywords:
                packages.append(package)
                packageByKeyword[package.keyword] = package

        # Attach fonts attribute to each package
        for package in packages:
            package.fonts = []

        # Attach fonts to packages
        for font in self.fonts:
            for keyword in font.getPackageKeywords():
                packageByKeyword[keyword].fonts.append(font)

        return packages


def Family_Parent(self):
    if (
        hasattr(self, "_parent")
        and hasattr(self._parent, "_parent")
        and hasattr(self._parent._parent, "_parent")
    ):
        return self._parent._parent._parent


Family.parent = property(lambda self: Family_Parent(self))


class FamilyProxy(Proxy):
    dataType = Family


class FamiliesListProxy(ListProxy):
    dataType = FamilyProxy


########################################################################################

#  Web Links


class WebURLListProxy(ListProxy):
    dataType = WebURLDataType


########################################################################################

#  Font Foundry


class StylingDataType(DictionaryDataType):
    def exampleData(self):
        return {
            "light": {
                "headerColor": "219BD3",
                "headerTextColor": "000000",
                "headerLinkColor": "145F7F",
                "backgroundColor": "FFFFFF",
                "textColor": "000000",
                "linkColor": "F7AD22",
                "selectionColor": "F7AD22",
                "selectionTextColor": "000000",
                "buttonColor": "197AA3",
                "buttonTextColor": "FFFFFF",
                "informationViewBackgroundColor": "F2F2F2",
                "informationViewTextColor": "000000",
                "informationViewLinkColor": "1D89B8",
                "informationViewButtonColor": "197AA3",
                "informationViewButtonTextColor": "FFFFFF",
                "logoURL": "https://awesomefoundry.com/logo-lighttheme.svg",
            },
            "dark": {
                "headerColor": "156486",
                "headerTextColor": "000000",
                "headerLinkColor": "53B9E4",
                "backgroundColor": "262626",
                "textColor": "999999",
                "linkColor": "C07F07",
                "selectionColor": "9A6606",
                "selectionTextColor": "000000",
                "buttonColor": "22A4DC",
                "buttonTextColor": "000000",
                "informationViewBackgroundColor": "1A1A1A",
                "informationViewTextColor": "999999",
                "informationViewLinkColor": "53B9E4",
                "informationViewButtonColor": "22A4DC",
                "informationViewButtonTextColor": "000000",
                "logoURL": "https://awesomefoundry.com/logo-darktheme.svg",
            },
        }


class Foundry(DictBasedObject):
    #   key:                    [data type, required, default value, description]
    _structure = {
        "uniqueID": [
            StringDataType,
            True,
            None,
            "An string that uniquely identifies this foundry within the publisher.",
        ],
        "name": [MultiLanguageTextProxy, True, None, "Name of foundry"],
        "description": [
            MultiLanguageLongTextProxy,
            False,
            None,
            "Description of foundry",
        ],
        "styling": [
            StylingDataType,
            False,
            {"light": {}, "dark": {}},
            (
                "Dictionary of styling values, for light and dark theme. See example "
                "below. If you want to style your foundry here, please start with the "
                "light theme. You may omit the dark theme."
            ),
        ],
        "email": [
            EmailDataType,
            False,
            None,
            "General email address for this foundry.",
        ],
        "websiteURL": [WebURLDataType, False, None, "Website for this foundry"],
        "telephone": [
            TelephoneDataType,
            False,
            None,
            "Telephone number for this foundry",
        ],
        "socialURLs": [
            WebURLListProxy,
            False,
            None,
            "List of web URLs pointing to social media channels",
        ],
        "supportEmail": [
            EmailDataType,
            False,
            None,
            "Support email address for this foundry.",
        ],
        "supportURL": [
            WebURLDataType,
            False,
            None,
            (
                "Support website for this foundry, such as a chat room, forum, "
                "online service desk."
            ),
        ],
        "supportTelephone": [
            TelephoneDataType,
            False,
            None,
            "Support telephone number for this foundry.",
        ],
        # data
        "licenses": [
            LicenseDefinitionListProxy,
            True,
            None,
            (
                "List of ::LicenseDefinition:: objects under which the fonts in this "
                "response are issued. For space efficiency, these licenses are defined "
                "at the foundry object and will be referenced in each font by their "
                "keyword. Keywords need to be unique for this foundry and may repeat "
                "across foundries."
            ),
        ],
        "families": [FamiliesListProxy, True, None, "List of ::Family:: objects."],
        "packages": [
            FontPackageListProxy,
            False,
            None,
            (
                "Foundry-wide list of ::FontPackage:: objects. These will be "
                "referenced by their keyword in ::Font.packageKeywords::"
            ),
        ],
    }

    _stylingColorAttributes = (
        "headerColor",
        "headerTextColor",
        "headerLinkColor",
        "backgroundColor",
        "textColor",
        "linkColor",
        "selectionColor",
        "selectionTextColor",
        "buttonColor",
        "buttonTextColor",
        "informationViewBackgroundColor",
        "informationViewTextColor",
        "informationViewLinkColor",
        "informationViewButtonColor",
        "informationViewButtonTextColor",
    )

    def sample(self):
        o = self.__class__()
        o.name.en = "Awesome Fonts"
        o.name.de = "Geile Schriften"
        o.websiteURL = "https://awesomefonts.com"
        o.uniqueID = "AwesomeFonts"
        return o

    def __repr__(self):
        return "<Foundry '%s'>" % self.name.getText() or "undefined"

    def getLicenseByKeyword(self, keyword):
        if not hasattr(self, "_licensesDict"):
            self._licensesDict = {}
            for license in self.licenses:
                self._licensesDict[license.keyword] = license

        if keyword in self._licensesDict:
            return self._licensesDict[keyword]

    def customValidation(self):
        information, warnings, critical = [], [], []

        themes = ["light", "dark"]

        if self.styling:
            for theme in self.styling:
                if theme not in themes:
                    critical.append(
                        "Styling keyword '%s' is unknown. Known are %s."
                        % (theme, themes)
                    )

                for colorKey in self._stylingColorAttributes:
                    if colorKey in self.styling[theme]:

                        c = HexColorDataType()
                        c.value = self.styling[theme][colorKey]
                        valid = c.valid()
                        if valid is not True:
                            critical.append(
                                ".styling color attribute '%s': %s" % (colorKey, valid)
                            )

                if "logoURL" in self.styling[theme]:
                    logo = WebURLDataType()
                    logo.value = self.styling[theme]["logoURL"]
                    valid = logo.valid()
                    if valid is not True:
                        critical.append(".styling 'logoURL' attribute: %s" % (valid))

        return information, warnings, critical


def Foundry_Parent(self):
    if (
        hasattr(self, "_parent")
        and hasattr(self._parent, "_parent")
        and hasattr(self._parent._parent, "_parent")
    ):
        return self._parent._parent._parent


Foundry.parent = property(lambda self: Foundry_Parent(self))


class FoundryProxy(Proxy):
    dataType = Foundry


class FoundryListProxy(ListProxy):
    dataType = FoundryProxy


########################################################################################

#  Base Response


class BaseResponse(DictBasedObject):
    def __repr__(self):
        return "<%s>" % self.__class__.__name__

    def customValidation(self):
        information, warnings, critical = [], [], []

        if (
            hasattr(self, "response")
            and self.response == ERROR
            and self.errorMessage.isEmpty()
        ):
            critical.append(f".response is '{ERROR}', but .errorMessage is missing.")

        return information, warnings, critical


########################################################################################

#  Available Fonts


class InstallableFontsResponseType(ResponseCommandDataType):
    def valid(self):
        if not self.value:
            return True

        if self.value in INSTALLABLEFONTSCOMMAND["responseTypes"]:
            return True
        else:
            return "Unknown response type: '%s'. Possible: %s" % (
                self.value,
                INSTALLABLEFONTSCOMMAND["responseTypes"],
            )


class InstallableFontsResponse(BaseResponse):
    """\
    This is the response expected to be returned when the API is invoked using the
    `?commands=installableFonts` parameter, and contains metadata about which fonts
    are available to install for a user.
    """

    _command = INSTALLABLEFONTSCOMMAND

    #   key:                    [data type, required, default value, description]
    _structure = {
        # Root
        "response": [
            InstallableFontsResponseType,
            True,
            None,
            "Type of response: %s"
            % (ResponsesDocu(INSTALLABLEFONTSCOMMAND["responseTypes"])),
        ],
        "errorMessage": [
            MultiLanguageTextProxy,
            False,
            None,
            (
                "Description of error in case of ::InstallableFontsResponse.response:: "
                "being 'custom'."
            ),
        ],
        # Response-specific
        "designers": [
            DesignersListProxy,
            False,
            None,
            (
                "List of ::Designer:: objects, referenced in the fonts or font "
                "families by the keyword. These are defined at the root of the "
                "response for space efficiency, as one designer can be involved in "
                "the design of several typefaces across several foundries."
            ),
        ],
        "foundries": [
            FoundryListProxy,
            True,
            None,
            (
                "List of ::Foundry:: objects; foundries that this distributor "
                "supports. In most cases this will be only one, as many foundries "
                "are their own distributors."
            ),
        ],
        "packages": [
            FontPackageListProxy,
            False,
            None,
            (
                "Publisher-wide list of ::FontPackage:: objects. These will be "
                "referenced by their keyword in ::Font.packageKeywords::"
            ),
        ],
        "name": [
            MultiLanguageTextProxy,
            False,
            None,
            (
                "A name of this response and its contents. This is needed to manage "
                "subscriptions in the UI. For instance 'Free Fonts' for all free and "
                "non-restricted fonts, or 'Commercial Fonts' for all those fonts that "
                "the use has commercially licensed, so their access is restricted. "
                "In case of a free font website that offers individual subscriptions "
                "for each typeface, this decription could be the name of the typeface."
            ),
        ],
        "userName": [
            MultiLanguageTextProxy,
            False,
            None,
            "The name of the user who these fonts are licensed to.",
        ],
        "userEmail": [
            EmailDataType,
            False,
            None,
            "The email address of the user who these fonts are licensed to.",
        ],
        "prefersRevealedUserIdentity": [
            BooleanDataType,
            True,
            False,
            (
                "Indicates that the publisher prefers to have the user reveal his/her "
                "identity to the publisher when installing fonts. In the app, the user "
                "will be asked via a dialog to turn the setting on, but is not "
                "required to do so."
            ),
        ],
    }

    def sample(self):
        o = self.__class__()
        o.response = "success"
        return o

    def getDesignerByKeyword(self, keyword):
        if not hasattr(self, "_designersDict"):
            self._designersDict = {}
            for designer in self.designers:
                self._designersDict[designer.keyword] = designer

        if keyword in self._designersDict:
            return self._designersDict[keyword]

    def discardThisKey(self, key):

        if (
            key in ["foundries", "designers", "licenseIdentifier"]
            and self.response != "success"
        ):
            return True

        return False

    def customValidation(self):
        information, warnings, critical = [], [], []

        if (
            hasattr(self, "response")
            and self.response == ERROR
            and self.errorMessage.isEmpty()
        ):
            critical.append(f".response is '{ERROR}', but .errorMessage is missing.")

        if self.response == "success" and not self.name.getText():
            warnings.append(
                (
                    "The response has no .name value. It is not required, but highly "
                    "recommended, to describe the purpose of this subscription to the "
                    "user (such as 'Commercial Fonts', 'Free Fonts', etc. This is "
                    "especially useful if you offer several different subscriptions "
                    "to the same user."
                )
            )

        # Check all uniqueIDs for duplicity
        foundryIDs = []
        familyIDs = []
        fontIDs = []
        for foundry in self.foundries:
            foundryIDs.append(foundry.uniqueID)
            for family in foundry.families:
                familyIDs.append(family.uniqueID)
                for font in family.fonts:
                    fontIDs.append(font.uniqueID)

        import collections

        duplicateFoundryIDs = [
            item
            for item, count in list(collections.Counter(foundryIDs).items())
            if count > 1
        ]
        if duplicateFoundryIDs:
            critical.append("Duplicate unique foundry IDs: %s" % duplicateFoundryIDs)

        duplicateFamilyIDs = [
            item
            for item, count in list(collections.Counter(familyIDs).items())
            if count > 1
        ]
        if duplicateFamilyIDs:
            critical.append("Duplicate unique family IDs: %s" % duplicateFamilyIDs)

        duplicateFontIDs = [
            item
            for item, count in list(collections.Counter(fontIDs).items())
            if count > 1
        ]
        if duplicateFontIDs:
            critical.append("Duplicate unique family IDs: %s" % duplicateFontIDs)

        newInformation, newWarnings, newCritical = super().customValidation()
        if newInformation:
            information.extend(newInformation)
        if newWarnings:
            warnings.extend(newWarnings)
        if newCritical:
            critical.extend(newCritical)

        return information, warnings, critical


########################################################################################

#  InstallFonts


class InstallFontAssetResponseType(ResponseCommandDataType):
    def valid(self):
        if not self.value:
            return True

        if self.value in INSTALLFONTASSETCOMMAND["responseTypes"]:
            return True
        else:
            return "Unknown response type: '%s'. Possible: %s" % (
                self.value,
                INSTALLFONTASSETCOMMAND["responseTypes"],
            )


class InstallFontAsset(BaseResponse):
    """\
    This is the response expected to be returned when the API is invoked using the
    `?commands=installFonts` parameter.
    """

    #   key:                    [data type, required, default value, description]
    _structure = {
        # Root
        "response": [
            InstallFontAssetResponseType,
            True,
            None,
            "Type of response: %s"
            % (ResponsesDocu(INSTALLFONTASSETCOMMAND["responseTypes"])),
        ],
        "errorMessage": [
            MultiLanguageTextProxy,
            False,
            None,
            "Description of error in case of custom response type",
        ],
        "uniqueID": [
            StringDataType,
            True,
            None,
            (
                "A machine-readable string that uniquely identifies this font within "
                "the subscription. Must match the requested fonts."
            ),
        ],
        "mimeType": [
            FontMimeType,
            False,
            None,
            "MIME Type of data. For desktop fonts, these are %s."
            % FONTPURPOSES["desktop"]["acceptableMimeTypes"],
        ],
        "dataURL": [
            WebURLDataType,
            False,
            None,
            (
                "HTTP link of font file resource. ::InstallFontAsset.data:: and "
                "::InstallFontAsset.dataURL:: are mutually exclusive; only one can be "
                "specified. The HTTP resource must be served under the correct "
                "MIME type specified in ::InstallFontAsset.mimeType:: and is expected "
                "to be in raw binary encoding; ::InstallFontAsset.encoding:: "
                "is not regarded."
            ),
        ],
        "data": [
            FontDataType,
            False,
            None,
            (
                "Binary data as a string encoded as one of the following supported "
                "encodings: ::InstallFontResponse.encoding::. "
                "::InstallFontAsset.data:: and ::InstallFontAsset.dataURL:: are "
                "mutually exclusive; only one can be specified."
            ),
        ],
        "encoding": [
            FontEncodingDataType,
            False,
            None,
            (
                "Encoding type for font data in ::InstallFontResponse.data::. "
                "Currently supported: %s" % (FONTENCODINGS)
            ),
        ],
    }

    def sample(self):
        o = self.__class__()
        o.response = "success"
        o.uniqueID = "AwesomeFonts-AwesomeFamily-Bold"
        o.mimeType = "font/otf"
        o.data = "emplNXpqdGpoNXdqdHp3enRq..."
        o.encoding = "base64"
        return o

    def customValidation(self):

        information, warnings, critical = [], [], []

        if self.response == "success" and (not self.data and not self.dataURL):
            critical.append(
                ".response is set to success, but neither .data nor .dataURL are set."
            )

        if self.data and not self.encoding:
            critical.append(".data is set, but .encoding is missing")

        if self.data and not self.mimeType:
            critical.append(".data is set, but .mimeType is missing")

        if self.dataURL and not self.mimeType:
            critical.append(".dataURL is set, but .mimeType is missing")

        if self.dataURL and self.data:
            critical.append("Either .dataURL or .data can be defined, not both")

        if self.response == ERROR and self.errorMessage.isEmpty():
            critical.append(
                ".response is '%s', but .errorMessage is missing." % (ERROR)
            )

        newInformation, newWarnings, newCritical = super().customValidation()
        if newInformation:
            information.extend(newInformation)
        if newWarnings:
            warnings.extend(newWarnings)
        if newCritical:
            critical.extend(newCritical)

        return information, warnings, critical


class InstallFontResponseType(ResponseCommandDataType):
    def valid(self):
        if not self.value:
            return True

        if self.value in INSTALLFONTSCOMMAND["responseTypes"]:
            return True
        else:
            return "Unknown response type: '%s'. Possible: %s" % (
                self.value,
                INSTALLFONTSCOMMAND["responseTypes"],
            )


class InstallFontAssetProxy(Proxy):
    dataType = InstallFontAsset


class InstallFontAssetListProxy(ListProxy):
    dataType = InstallFontAssetProxy


class InstallFontsResponse(BaseResponse):
    """\
    This is the response expected to be returned when the API is invoked using the
    `?commands=installFonts` parameter, and contains the requested binary fonts
    attached as ::InstallFontAsset:: obects.
    """

    _command = INSTALLFONTSCOMMAND

    #   key:                    [data type, required, default value, description]
    _structure = {
        # Root
        "response": [
            InstallFontResponseType,
            True,
            None,
            "Type of response: %s"
            % (ResponsesDocu(UNINSTALLFONTSCOMMAND["responseTypes"])),
        ],
        "errorMessage": [
            MultiLanguageTextProxy,
            False,
            None,
            "Description of error in case of custom response type",
        ],
        "assets": [
            InstallFontAssetListProxy,
            False,
            None,
            "List of ::InstallFontAsset:: objects.",
        ],
    }

    def sample(self):
        o = self.__class__()
        o.response = "success"
        o.assets = [InstallFontAsset().sample()]
        return o


########################################################################################

#  Uninstall Fonts


class UninstallFontAssedResponseType(ResponseCommandDataType):
    def valid(self):
        if not self.value:
            return True

        if self.value in UNINSTALLFONTASSETCOMMAND["responseTypes"]:
            return True
        else:
            return "Unknown response type: '%s'. Possible: %s" % (
                self.value,
                UNINSTALLFONTASSETCOMMAND["responseTypes"],
            )


class UninstallFontAsset(BaseResponse):
    """\
    This is the response expected to be returned when the API is invoked using the
    `?commands=uninstallFonts` parameter.
    """

    #   key:                    [data type, required, default value, description]

    _structure = {
        # Root
        "response": [
            UninstallFontAssedResponseType,
            True,
            None,
            "Type of response: %s"
            % (ResponsesDocu(UNINSTALLFONTASSETCOMMAND["responseTypes"])),
        ],
        "errorMessage": [
            MultiLanguageTextProxy,
            False,
            None,
            "Description of error in case of custom response type",
        ],
        "uniqueID": [
            StringDataType,
            True,
            None,
            (
                "A machine-readable string that uniquely identifies this font within "
                "the subscription. Must match the requested fonts."
            ),
        ],
        # Response-specific
    }

    def sample(self):
        o = self.__class__()
        o.response = "success"
        o.uniqueID = "AwesomeFonts-AwesomeFamily-Bold"
        return o


class UninstallFontResponseType(ResponseCommandDataType):
    def valid(self):
        if not self.value:
            return True

        if self.value in UNINSTALLFONTSCOMMAND["responseTypes"]:
            return True
        else:
            return "Unknown response type: '%s'. Possible: %s" % (
                self.value,
                UNINSTALLFONTSCOMMAND["responseTypes"],
            )


class UninstallFontAssetProxy(Proxy):
    dataType = UninstallFontAsset


class UninstallFontAssetListProxy(ListProxy):
    dataType = UninstallFontAssetProxy


class UninstallFontsResponse(BaseResponse):
    """\
    This is the response expected to be returned when the API is invoked using the
    `?commands=uninstallFonts` parameter, and contains empty responses as
    ::UninstallFontAsset:: objects.
    While empty of data, these asset objects are still necessary because each font
    uninstallation request may return a different response, to which the GUI app needs
    to respond to accordingly.
    """

    _command = UNINSTALLFONTSCOMMAND

    #   key:                    [data type, required, default value, description]
    _structure = {
        # Root
        "response": [
            UninstallFontResponseType,
            True,
            None,
            "Type of response: %s"
            % (ResponsesDocu(UNINSTALLFONTSCOMMAND["responseTypes"])),
        ],
        "errorMessage": [
            MultiLanguageTextProxy,
            False,
            None,
            "Description of error in case of custom response type",
        ],
        "assets": [
            UninstallFontAssetListProxy,
            False,
            None,
            "List of ::UninstallFontAsset:: objects.",
        ],
    }

    def sample(self):
        o = self.__class__()
        o.response = "success"
        o.assets = [UninstallFontAsset().sample()]
        return o


########################################################################################


class EndpointResponse(BaseResponse):
    """\
This is the response expected to be returned when the API is invoked using the
`?commands=endpoint` parameter.

This response contains some mandatory information about the API endpoint such as its
name and admin email, the copyright license under which the API endpoint issues its
data, and whether or not this endpoint can be publicized about.
    """

    _command = ENDPOINTCOMMAND

    #   key:                    [data type, required, default value, description]
    _structure = {
        "canonicalURL": [
            WebURLDataType,
            True,
            None,
            (
                "Official API endpoint URL, bare of ID keys and other parameters. "
                "Used for grouping of subscriptions. It is expected that this URL will "
                "not change. When it does, it will be treated as a different publisher."
            ),
        ],
        "adminEmail": [
            EmailDataType,
            True,
            None,
            (
                "API endpoint Administrator. This email needs to be reachable for "
                "various information around the Type.World protocol as well as "
                "technical problems."
            ),
        ],
        "licenseIdentifier": [
            OpenSourceLicenseIdentifierDataType,
            True,
            "CC-BY-NC-ND-4.0",
            (
                "Identifier of license under which the API endpoint publishes its "
                "data, as per [https://spdx.org/licenses/](). This license will not "
                "be presented to the user. The software client needs to be aware of "
                "the license and proceed only if allowed, otherwise decline the usage "
                "of this API endpoint. Licenses of the individual responses can be "
                "fine-tuned in the respective responses."
            ),
        ],
        "supportedCommands": [
            SupportedAPICommandsListProxy,
            True,
            None,
            "List of commands this API endpoint supports: %s"
            % [x["keyword"] for x in COMMANDS],
        ],
        "name": [
            MultiLanguageTextProxy,
            True,
            None,
            "Human-readable name of API endpoint",
        ],
        "public": [
            BooleanDataType,
            True,
            False,
            (
                "API endpoint is meant to be publicly visible and its existence may "
                "be publicized within the project"
            ),
        ],
        "logoURL": [
            WebResourceURLDataType,
            False,
            None,
            "URL of logo of API endpoint, for publication. Specifications to follow.",
        ],
        "backgroundColor": [
            HexColorDataType,
            False,
            None,
            (
                "Publisher’s preferred background color. This is meant to go as a "
                "background color to the logo at ::APIRoot.logoURL::"
            ),
        ],
        "websiteURL": [
            WebURLDataType,
            False,
            None,
            "URL of human-visitable website of API endpoint, for publication",
        ],
        "privacyPolicyURL": [
            WebURLDataType,
            True,
            "https://type.world/legal/default/PrivacyPolicy.html",
            (
                "URL of human-readable Privacy Policy of API endpoint. This will be "
                "displayed to the user for consent when adding a subscription. "
                "The default URL points to a document edited by Type.World that you "
                "can use (at your own risk) instead of having to write your own.\n\n"
                "The link will open with a `locales` parameter containing a "
                "comma-separated list of the user’s preferred UI languages and a "
                "`canonicalURL` parameter containing the subscription’s canonical URL "
                "and a `subscriptionID` parameter containing the anonymous "
                "subscription ID."
            ),
        ],
        "termsOfServiceURL": [
            WebURLDataType,
            True,
            "https://type.world/legal/default/TermsOfService.html",
            (
                "URL of human-readable Terms of Service Agreement of API endpoint. "
                "This will be displayed to the user for consent when adding a "
                "subscription. The default URL points to a document edited by "
                "Type.World that you can use (at your own risk) instead of having to "
                "write your own.\n\nThe link will open with a `locales` parameter "
                "containing a comma-separated list of the user’s preferred UI "
                "languages and a `canonicalURL` parameter containing the "
                "subscription’s canonical URL and a `subscriptionID` parameter "
                "containing the anonymous subscription ID."
            ),
        ],
        "loginURL": [
            WebURLDataType,
            False,
            None,
            (
                "URL for user to log in to publisher’s account in case a validation "
                "is required. This normally work in combination with the "
                "`loginRequired` response."
            ),
        ],
    }

    def sample(self):
        o = self.__class__()
        o.canonicalURL = "https://awesomefonts.com/api/"
        o.adminEmail = "admin@awesomefonts.com"
        o.supportedCommands = [
            "endpoint",
            "installableFonts",
            "installFonts",
            "uninstallFonts",
        ]
        o.name.en = "Awesome Fonts"
        o.name.de = "Geile Schriften"
        o.privacyPolicyURL = "https://awesomefonts.com/privacypolicy.html"
        o.termsOfServiceURL = "https://awesomefonts.com/termsofservice.html"
        o.public = True
        return o

    def customValidation(self):
        information, warnings, critical = [], [], []

        if self.canonicalURL and not self.canonicalURL.startswith("https://"):
            warnings.append(
                (
                    ".canonicalURL is not using SSL (https://). Consider using SSL "
                    "to protect your data."
                )
            )

        return information, warnings, critical


########################################################################################

#  Root Response


class EndpointResponseProxy(Proxy):
    dataType = EndpointResponse


class InstallableFontsResponseProxy(Proxy):
    dataType = InstallableFontsResponse


class InstallFontsResponseProxy(Proxy):
    dataType = InstallFontsResponse


class UninstallFontsResponseProxy(Proxy):
    dataType = UninstallFontsResponse


class RootResponse(BaseResponse):
    """\
    This is the root object for each response, and contains one or more individual
    response objects as requested in the `commands` parameter of API endpoint calls.

    This exists to speed up processes by reducing server calls. For instance,
    installing a protected fonts and afterwards asking for a refreshed
    `installableFonts` command requires two separate calls to the publisher’s API
    endpoint, which in turns needs to verify the requester’s identy with the central
    type.world server. By requesting `installFonts,installableFonts` commands in one go,
    a lot of time is saved.
    """

    #   key:                    [data type, required, default value, description]
    _structure = {
        # Root
        "endpoint": [
            EndpointResponseProxy,
            False,
            None,
            "::EndpointResponse:: object.",
        ],
        "installableFonts": [
            InstallableFontsResponseProxy,
            False,
            None,
            "::InstallableFontsResponse:: object.",
        ],
        "installFonts": [
            InstallFontsResponseProxy,
            False,
            None,
            "::InstallFontsResponse:: object.",
        ],
        "uninstallFonts": [
            UninstallFontsResponseProxy,
            False,
            None,
            "::UninstallFontsResponse:: object.",
        ],
        "version": [
            VersionDataType,
            True,
            INSTALLFONTSCOMMAND["currentVersion"],
            "Version of '%s' response" % INSTALLFONTSCOMMAND["keyword"],
        ],
    }

    def sample(self):
        o = self.__class__()
        o.endpoint = EndpointResponse().sample()
        o.installableFonts = InstallableFontsResponse().sample()
        return o
