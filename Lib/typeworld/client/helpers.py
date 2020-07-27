import platform
import os


def ReadFromFile(path):
    """\
    Return content of file
    """
    import os
    import codecs

    if os.path.exists(path):
        f = codecs.open(path, encoding="utf-8", mode="r")
        text = f.read()  # .decode('utf8')
        f.close()
        return text


def WriteToFile(path, string):
    """\
    Write content to file
    """
    f = open(path, "wb")
    f.write(string.encode())
    f.close()
    return True


def Execute(command):
    """\
    Execute system command, return output.
    """

    import os
    import subprocess

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, shell=True, close_fds=True
    )
    os.waitpid(process.pid, 0)
    response = process.stdout.read().strip()
    process.stdout.close()
    process.wait()
    return response


def Garbage(length, uppercase=True, lowercase=True, numbers=True, punctuation=False):
    """\
    Return string containing garbage.
    """

    import random

    uppercaseparts = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lowercaseparts = "abcdefghijklmnopqrstuvwxyz"
    numberparts = "0123456789"
    punctuationparts = ".-_"

    pool = ""
    if uppercase:
        pool += uppercaseparts
    if lowercase:
        pool += lowercaseparts
    if numbers:
        pool += numberparts
    if punctuation:
        pool += punctuationparts

    garbage = ""

    while len(garbage) < length:
        garbage += random.choice(pool)

    return garbage


def get_registry_value(key, subkey, value):
    import winreg

    key = getattr(winreg, key)
    handle = winreg.OpenKey(key, subkey)
    (value, type) = winreg.QueryValueEx(handle, value)
    return value


def MachineName():

    machineModelIdentifier = None
    humanReadableName = None
    specsDescription = None

    if platform.system() == "Windows":

        specsDescription = get_registry_value(
            "HKEY_LOCAL_MACHINE",
            "HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0",
            "ProcessorNameString",
        )
        humanReadableName = get_registry_value(
            "HKEY_LOCAL_MACHINE",
            "HARDWARE\\DESCRIPTION\\System\\BIOS",
            "SystemProductName",
        )

    if platform.system() == "Linux":

        cpu = ""
        itemsUsed = []
        procinfo = Execute("cat /proc/cpuinfo").decode()

        for line in procinfo.split("\n"):
            if ":" in line:
                k, v = line.split(":")[:2]
                if k.strip() == "model name" and k not in itemsUsed:
                    cpu += v.strip()
                    itemsUsed.append(k)

        if os.path.exists("/sys/devices/virtual/dmi/id/sys_vendor") and os.path.exists(
            "/sys/devices/virtual/dmi/id/product_name"
        ):
            humanReadableName = "%s %s" % (
                Execute("cat /sys/devices/virtual/dmi/id/sys_vendor").decode(),
                Execute("cat /sys/devices/virtual/dmi/id/product_name").decode(),
            )
        else:
            humanReadableName = "Google App Engine"  # nocoverage
        specsDescription = cpu

    elif platform.system() == "Darwin":

        name = None

        # Approach 1
        import plistlib

        data = plistlib.loads(Execute("system_profiler -xml SPHardwareDataType"))

        # Approach 2
        if not name:
            name = data[0]["_items"][0]["machine_name"]

        machineModelIdentifier = data[0]["_items"][0]["machine_model"]
        humanReadableName = "%s" % name
        # if not name.startswith('Apple'):
        # 	name = 'Apple ' + name
        specsDescription = []
        # if 'cpu_type' in data[0]['_items'][0]:
        # 	specsDescription.append(data[0]['_items'][0]['cpu_type'])
        if "current_processor_speed" in data[0]["_items"][0]:
            specsDescription.append(data[0]["_items"][0]["current_processor_speed"])
        specsDescription.append("with")
        if "physical_memory" in data[0]["_items"][0]:
            specsDescription.append(data[0]["_items"][0]["physical_memory"])

        specsDescription = " ".join(specsDescription)

    return machineModelIdentifier, humanReadableName, specsDescription


def OSName():

    import platform

    if platform.system() == "Darwin":
        return "macOS %s" % platform.mac_ver()[0]

    elif platform.system() == "Windows":

        return (
            get_registry_value(
                "HKEY_LOCAL_MACHINE",
                "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
                "ProductName",
            )
            + ", "
            + str(platform.version())
        )

    elif platform.system() == "Linux":
        return " ".join(platform.platform())


def addAttributeToURL(url, attributes):

    from urllib.parse import urlparse

    o = urlparse(url)

    for attribute in attributes.split("&"):

        key, value = attribute.split("=")

        replaced = False
        queryParts = o.query.split("&")
        if queryParts:
            for i, query in enumerate(queryParts):
                if "=" in query and query.startswith(key + "="):
                    queryParts[i] = attribute
                    replaced = True
                    break
        if not replaced:
            if queryParts[0]:
                queryParts.append(attribute)
            else:
                queryParts[0] = attribute
        o = o._replace(query="&".join(queryParts))

    return o.geturl()


WIN = platform.system() == "Windows"
MAC = platform.system() == "Darwin"
LINUX = platform.system() == "Linux"


# from https://gist.github.com/dgelessus/018681c297dfae22a06a3bc315d9e6e3:

"""Allows logging Python :class:`str`s to the system log using Foundation's ``NSLog``
function. This module is meant to help with debugging the loading process of Rubicon on
systems like iOS, where sometimes only NSLog output (but not stdout/stderr) is available
to the developer."""

if MAC:
    import ctypes
    import sys

    __all__ = [
        "nslog",
    ]

    # Name of the UTF-16 encoding with the system byte order.
    if sys.byteorder == "little":
        UTF16_NATIVE = "utf-16-le"
    elif sys.byteorder == "big":  # nocoverage
        UTF16_NATIVE = "utf-16-be"  # nocoverage
    else:
        raise AssertionError("Unknown byte order: " + sys.byteorder)  # nocoverage

    # Note: Many of the following definitions are duplicated in other rubicon.objc
    # submodules.
    # However because this module is used to debug the early startup process of Rubicon,
    # we can't use any of the other
    # definitions.

    class CFTypeRef(ctypes.c_void_p):
        pass

    CFIndex = ctypes.c_long
    UniChar = ctypes.c_uint16

    CoreFoundation = ctypes.CDLL(
        "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
    )
    Foundation = ctypes.CDLL(
        "/System/Library/Frameworks/Foundation.framework/Foundation"
    )

    # void CFRelease(CFTypeRef arg)
    CoreFoundation.CFRelease.restype = None
    CoreFoundation.CFRelease.argtypes = [CFTypeRef]

    # CFStringRef CFStringCreateWithCharacters(CFAllocatorRef alloc, const UniChar
    # *chars, CFIndex numChars)
    CoreFoundation.CFStringCreateWithCharacters.restype = CFTypeRef
    CoreFoundation.CFStringCreateWithCharacters.argtypes = [
        CFTypeRef,
        ctypes.POINTER(UniChar),
        CFIndex,
    ]

    # void NSLog(NSString *format, ...)
    Foundation.NSLog.restype = None
    Foundation.NSLog.argtypes = [CFTypeRef]

    def _cfstr(s):
        """Create a ``CFString`` from the given Python :class:`str`."""

        encoded = s.encode(UTF16_NATIVE)
        assert len(encoded) % 2 == 0
        arr = (UniChar * (len(encoded) // 2)).from_buffer_copy(encoded)
        cfstring = CoreFoundation.CFStringCreateWithCharacters(None, arr, len(arr))
        assert cfstring is not None
        return cfstring

    # Format string for a single object.
    FORMAT = _cfstr("%@")

    def nslog(s):
        """Log the given Python :class:`str` to the system log."""

        cfstring = _cfstr(s)
        Foundation.NSLog(FORMAT, cfstring)
        CoreFoundation.CFRelease(cfstring)

    # class NSLogWriter(io.TextIOBase):
    # 	"""An output-only text stream that writes to the system log."""

    # 	def write(self, s):
    # 		nslog(s[:-1] if s.endswith('\n') else s)
    # 		return len(s)

    # 	@property
    # 	def encoding(self):
    # 		return UTF16_NATIVE
