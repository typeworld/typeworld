# -*- coding: utf-8 -*-

import json, copy, types, inspect, re, traceback, datetime
from optparse import OptionParser
import semver

import typeWorld.api
import typeWorld.api.base

# Response types (success, error, ...)
SUCCESS = 'success'
ERROR = 'error'
SEATALLOWANCEREACHED = 'seatAllowanceReached'

PROTOCOLS = ['typeworldjson', 'typeworldgithub']

# Commands
INSTALLABLEFONTSCOMMAND = {
    'keyword': 'installableFonts',
    'currentVersion': 0.1,
    'versionHistory': [0.1],
    'responseTypes': [SUCCESS, ERROR],
    'acceptableMimeTypes': ['application/json'],
    }
INSTALLFONTCOMMAND ={
    'keyword': 'installFont',
    'currentVersion': 0.1,
    'versionHistory': [0.1],
    'responseTypes': [SUCCESS, ERROR, SEATALLOWANCEREACHED],
    'acceptableMimeTypes': ['application/json'],
    }
UNINSTALLFONTCOMMAND =  {
    'keyword': 'uninstallFont',
    'currentVersion': 0.1,
    'versionHistory': [0.1],
    'responseTypes': [SUCCESS, ERROR],
    'acceptableMimeTypes': ['application/json'],
    }
COMMANDS = [INSTALLABLEFONTSCOMMAND, INSTALLFONTCOMMAND, UNINSTALLFONTCOMMAND]

FONTTYPES = {
    'desktop': {
        'acceptableMimeTypes': ['font/collection', 'font/otf', 'font/sfnt', 'font/ttf', 'application/zip'],
    },
    'web': {
        'acceptableMimeTypes': ['application/zip'],
    },
    'app': {
        'acceptableMimeTypes': ['application/zip'],
    },
}

# https://tools.ietf.org/html/rfc8081

MIMETYPES = {
    'font/sfnt': {
        'fileExtensions': ['otf', 'ttf'],
    },
    'font/ttf': {
        'fileExtensions': ['ttf'],
    },
    'font/otf': {
        'fileExtensions': ['otf'],
    },
    'font/collection': {
        'fileExtensions': ['ttc'],
    },
    'font/woff': {
        'fileExtensions': ['woff'],
    },
    'font/woff2': {
        'fileExtensions': ['woff2'],
    },
}

# Compile list of file extensions
FILEEXTENSIONS = []
for mimeType in list(MIMETYPES.keys()):
    FILEEXTENSIONS = list(set(FILEEXTENSIONS) | set(MIMETYPES[mimeType]['fileExtensions']))

FILEEXTENSIONNAMES = {
    'otf': 'OpenType',
    'ttf': 'TrueType',
    'ttc': 'TrueType collection',
    'woff': 'WOFF',
    'woff2': 'WOFF2',
}

MIMETYPEFORFONTTYPE = {
    'otf': 'font/otf',
    'ttf': 'font/ttf',
    'ttc': 'font/collection',
    'woff': 'font/woff',
    'woff2': 'font/woff2',
}

FONTENCODINGS = ['base64']

OPENSOURCELICENSES = ['0BSD', 'AAL', 'Abstyles', 'Adobe-2006', 'Adobe-Glyph', 'ADSL', 'AFL-1.1', 'AFL-1.2', 'AFL-2.0', 'AFL-2.1', 'AFL-3.0', 'Afmparse', 'AGPL-1.0', 'AGPL-3.0-only', 'AGPL-3.0-or-later', 'Aladdin', 'AMDPLPA', 'AML', 'AMPAS', 'ANTLR-PD', 'Apache-1.0', 'Apache-1.1', 'Apache-2.0', 'APAFML', 'APL-1.0', 'APSL-1.0', 'APSL-1.1', 'APSL-1.2', 'APSL-2.0', 'Artistic-1.0-cl8', 'Artistic-1.0-Perl', 'Artistic-1.0', 'Artistic-2.0', 'Bahyph', 'Barr', 'Beerware', 'BitTorrent-1.0', 'BitTorrent-1.1', 'Borceux', 'BSD-1-Clause', 'BSD-2-Clause-FreeBSD', 'BSD-2-Clause-NetBSD', 'BSD-2-Clause-Patent', 'BSD-2-Clause', 'BSD-3-Clause-Attribution', 'BSD-3-Clause-Clear', 'BSD-3-Clause-LBNL', 'BSD-3-Clause-No-Nuclear-License-2014', 'BSD-3-Clause-No-Nuclear-License', 'BSD-3-Clause-No-Nuclear-Warranty', 'BSD-3-Clause', 'BSD-4-Clause-UC', 'BSD-4-Clause', 'BSD-Protection', 'BSD-Source-Code', 'BSL-1.0', 'bzip2-1.0.5', 'bzip2-1.0.6', 'Caldera', 'CATOSL-1.1', 'CC-BY-1.0', 'CC-BY-2.0', 'CC-BY-2.5', 'CC-BY-3.0', 'CC-BY-4.0', 'CC-BY-NC-1.0', 'CC-BY-NC-2.0', 'CC-BY-NC-2.5', 'CC-BY-NC-3.0', 'CC-BY-NC-4.0', 'CC-BY-NC-ND-1.0', 'CC-BY-NC-ND-2.0', 'CC-BY-NC-ND-2.5', 'CC-BY-NC-ND-3.0', 'CC-BY-NC-ND-4.0', 'CC-BY-NC-SA-1.0', 'CC-BY-NC-SA-2.0', 'CC-BY-NC-SA-2.5', 'CC-BY-NC-SA-3.0', 'CC-BY-NC-SA-4.0', 'CC-BY-ND-1.0', 'CC-BY-ND-2.0', 'CC-BY-ND-2.5', 'CC-BY-ND-3.0', 'CC-BY-ND-4.0', 'CC-BY-SA-1.0', 'CC-BY-SA-2.0', 'CC-BY-SA-2.5', 'CC-BY-SA-3.0', 'CC-BY-SA-4.0', 'CC0-1.0', 'CDDL-1.0', 'CDDL-1.1', 'CDLA-Permissive-1.0', 'CDLA-Sharing-1.0', 'CECILL-1.0', 'CECILL-1.1', 'CECILL-2.0', 'CECILL-2.1', 'CECILL-B', 'CECILL-C', 'ClArtistic', 'CNRI-Jython', 'CNRI-Python-GPL-Compatible', 'CNRI-Python', 'Condor-1.1', 'CPAL-1.0', 'CPL-1.0', 'CPOL-1.02', 'Crossword', 'CrystalStacker', 'CUA-OPL-1.0', 'Cube', 'curl', 'D-FSL-1.0', 'diffmark', 'DOC', 'Dotseqn', 'DSDP', 'dvipdfm', 'ECL-1.0', 'ECL-2.0', 'EFL-1.0', 'EFL-2.0', 'eGenix', 'Entessa', 'EPL-1.0', 'EPL-2.0', 'ErlPL-1.1', 'EUDatagrid', 'EUPL-1.0', 'EUPL-1.1', 'EUPL-1.2', 'Eurosym', 'Fair', 'Frameworx-1.0', 'FreeImage', 'FSFAP', 'FSFUL', 'FSFULLR', 'FTL', 'GFDL-1.1-only', 'GFDL-1.1-or-later', 'GFDL-1.2-only', 'GFDL-1.2-or-later', 'GFDL-1.3-only', 'GFDL-1.3-or-later', 'Giftware', 'GL2PS', 'Glide', 'Glulxe', 'gnuplot', 'GPL-1.0-only', 'GPL-1.0-or-later', 'GPL-2.0-only', 'GPL-2.0-or-later', 'GPL-3.0-only', 'GPL-3.0-or-later', 'gSOAP-1.3b', 'HaskellReport', 'HPND', 'IBM-pibs', 'ICU', 'IJG', 'ImageMagick', 'iMatix', 'Imlib2', 'Info-ZIP', 'Intel-ACPI', 'Intel', 'Interbase-1.0', 'IPA', 'IPL-1.0', 'ISC', 'JasPer-2.0', 'JSON', 'LAL-1.2', 'LAL-1.3', 'Latex2e', 'Leptonica', 'LGPL-2.0-only', 'LGPL-2.0-or-later', 'LGPL-2.1-only', 'LGPL-2.1-or-later', 'LGPL-3.0-only', 'LGPL-3.0-or-later', 'LGPLLR', 'Libpng', 'libtiff', 'LiLiQ-P-1.1', 'LiLiQ-R-1.1', 'LiLiQ-Rplus-1.1', 'LPL-1.0', 'LPL-1.02', 'LPPL-1.0', 'LPPL-1.1', 'LPPL-1.2', 'LPPL-1.3a', 'LPPL-1.3c', 'MakeIndex', 'MirOS', 'MIT-advertising', 'MIT-CMU', 'MIT-enna', 'MIT-feh', 'MIT', 'MITNFA', 'Motosoto', 'mpich2', 'MPL-1.0', 'MPL-1.1', 'MPL-2.0-no-copyleft-exception', 'MPL-2.0', 'MS-PL', 'MS-RL', 'MTLL', 'Multics', 'Mup', 'NASA-1.3', 'Naumen', 'NBPL-1.0', 'NCSA', 'Net-SNMP', 'NetCDF', 'Newsletr', 'NGPL', 'NLOD-1.0', 'NLPL', 'Nokia', 'NOSL', 'Noweb', 'NPL-1.0', 'NPL-1.1', 'NPOSL-3.0', 'NRL', 'NTP', 'OCCT-PL', 'OCLC-2.0', 'ODbL-1.0', 'OFL-1.0', 'OFL-1.1', 'OGTSL', 'OLDAP-1.1', 'OLDAP-1.2', 'OLDAP-1.3', 'OLDAP-1.4', 'OLDAP-2.0.1', 'OLDAP-2.0', 'OLDAP-2.1', 'OLDAP-2.2.1', 'OLDAP-2.2.2', 'OLDAP-2.2', 'OLDAP-2.3', 'OLDAP-2.4', 'OLDAP-2.5', 'OLDAP-2.6', 'OLDAP-2.7', 'OLDAP-2.8', 'OML', 'OpenSSL', 'OPL-1.0', 'OSET-PL-2.1', 'OSL-1.0', 'OSL-1.1', 'OSL-2.0', 'OSL-2.1', 'OSL-3.0', 'PDDL-1.0', 'PHP-3.0', 'PHP-3.01', 'Plexus', 'PostgreSQL', 'psfrag', 'psutils', 'Python-2.0', 'Qhull', 'QPL-1.0', 'Rdisc', 'RHeCos-1.1', 'RPL-1.1', 'RPL-1.5', 'RPSL-1.0', 'RSA-MD', 'RSCPL', 'Ruby', 'SAX-PD', 'Saxpath', 'SCEA', 'Sendmail', 'SGI-B-1.0', 'SGI-B-1.1', 'SGI-B-2.0', 'SimPL-2.0', 'SISSL-1.2', 'SISSL', 'Sleepycat', 'SMLNJ', 'SMPPL', 'SNIA', 'Spencer-86', 'Spencer-94', 'Spencer-99', 'SPL-1.0', 'SugarCRM-1.1.3', 'SWL', 'TCL', 'TCP-wrappers', 'TMate', 'TORQUE-1.1', 'TOSL', 'Unicode-DFS-2015', 'Unicode-DFS-2016', 'Unicode-TOU', 'Unlicense', 'UPL-1.0', 'Vim', 'VOSTROM', 'VSL-1.0', 'W3C-19980720', 'W3C-20150513', 'W3C', 'Watcom-1.0', 'Wsuipa', 'WTFPL', 'X11', 'Xerox', 'XFree86-1.1', 'xinetd', 'Xnet', 'xpp', 'XSkat', 'YPL-1.0', 'YPL-1.1', 'Zed', 'Zend-2.0', 'Zimbra-1.3', 'Zimbra-1.4', 'zlib-acknowledgement', 'Zlib', 'ZPL-1.1', 'ZPL-2.0', 'ZPL-2.1']

def makeSemVer(version):
    'Turn simple float number (0.1) into semver-compatible number for comparison by adding .0(s): (0.1.0)'

    # Make string
    version = str(version)

    if version.count('.') < 2:

        # Strip leading zeros
        version = '.'.join(map(str, list(map(int, version.split('.')))))

        # Add .0(s)
        version = version + (2 - version.count('.')) * '.0'

    return version



class DataType(object):
    initialData = None
    dataType = None

    def __init__(self, value = None):
        if value:
            self.value = value
        else:
            self.value = copy.copy(self.initialData)

        if issubclass(self.__class__, (MultiLanguageText, MultiLanguageTextProxy)):
            self.value = self.dataType()


    def __repr__(self):
        return '<%s "%s">' % (self.__class__.__name__, self.get())

    def valid(self):
        if self.dataType != None:
            if type(self.value) == self.dataType:
                return True
            else:
                return 'Wrong data type. Is %s, should be: %s.' % (type(self.value), self.dataType)
        else:
            return True

    def get(self):
        return self.value

    def put(self, value):


        self.value = self.shapeValue(value)

        if issubclass(self.value.__class__, (DictBasedObject, ListProxy, Proxy, DataType)):
#           print 'Setting _parent of %s to %s' % (self.value, self)
            object.__setattr__(self.value, '_parent', self)

        valid = self.valid()
        if valid != True and valid != None:
            raise ValueError(valid)

    def shapeValue(self, value):
        return value

    def isEmpty(self):
        return self.value == None or self.value == [] or self.value == ''

    def formatHint(self):
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


class UnicodeDataType(DataType):
    dataType = str

    def shapeValue(self, value):
        return str(value)


class FontDataType(StringDataType):
    pass


class FontEncodingDataType(StringDataType):

    def valid(self):
        
        if self.value not in FONTENCODINGS:
            return 'Encoding %s is unknown. Known are: %s' % (self.value, FONTENCODINGS)

        return True

class VersionDataType(StringDataType):
    dataType = str

    def valid(self):
        
        try:

            # Append .0 for semver comparison
            value = makeSemVer(self.value)
            a = semver.parse(value)
            return True
        except:
            return traceback.format_exc()

    def formatHint(self):
        return 'Simple float number (1.01) or semantic versioning (2.0.0-rc.1)'

class DateDataType(StringDataType):

    def valid(self):

        try:
            date_obj = datetime.datetime.strptime(self.value, '%Y-%m-%d')
            return True

        except ValueError:
            return traceback.format_exc().splitlines()[-1]

    def formatHint(self):
        return 'YYYY-MM-DD'


class WebURLDataType(UnicodeDataType):

    def valid(self):
        if not self.value.startswith('http://') and not self.value.startswith('https://'):
            return 'Needs to start with http:// or https://'
        else:
            return True

class EmailDataType(UnicodeDataType):

    def valid(self):
        if \
            '@' in self.value and '.' in self.value and \
            self.value.find('.', self.value.find('@')) > 0 and \
            self.value.count('@') == 1 \
            and self.value.find('..') == -1:

            return True
        else:
            return 'Not a valid email format: %s' % self.value

class HexColorDataType(StringDataType):

    def valid(self):
        if \
            (len(self.value) == 3 or len(self.value) == 6) and \
            re.match("^[A-Fa-f0-9]*$", self.value):

            return True
        else:
            return 'Not a valid hex color of format RRGGBB (like FF0000 for red): %s' % self.value

    def formatHint(self):
        return 'Hex RRGGBB (without leading #)'



class ListProxy(DataType):
    initialData = []


    # Data type of each list member
    # Here commented out to enforce explicit setting of data type for each Proxy
    #dataType = str

    def __repr__(self):
        if self.value:
            return '%s' % ([x.get() for x in self.value])
        else:
            return '[]'

    def __getitem__(self, i):
        return self.value[i].get()

    def __setitem__(self, i, value):

        if issubclass(value.__class__, (DictBasedObject, Proxy, ListProxy, DataType)):
            object.__setattr__(value, '_parent', self)
#           print 'Setting _parent of %s to %s' % (value, self)

        self.value[i].put(value)
        object.__setattr__(self.value[i], '_parent', self)
#       print 'Setting _parent of %s to %s' % (self.value[i], self)

    def __delitem__(self, i):
        del self.value[i]

    def __iter__(self):
        for element in self.value:
            yield element.get()

    def __len__(self):
        return len(self.value)

    def get(self):

        return self

        _list = []
        for data in self.value:
            _list.append(data.get())
        return _list

    def put(self, values):
        self.value = []
        for value in values:
            self.append(value)
            
    def append(self, value):


        newData = self.dataType()
        newData.put(value)

        self.value.append(newData)

        if issubclass(self.value.__class__, (DictBasedObject, Proxy, ListProxy, DataType)):
            object.__setattr__(self.value, '_parent', self)
#           print 'Setting _parent of %s to %s (in .append())' % (value, self)

        if issubclass(newData.__class__, (DictBasedObject, Proxy, ListProxy, DataType)):
            object.__setattr__(newData, '_parent', self)
#           print 'Setting _parent of %s to %s (in .append())' % (value, self)


    def extend(self, values):
        for value in values:
            self.append(value)

    def remove(self, removeValue):
        for i, value in enumerate(self.value):
            if self[i] == removeValue:
                del self[i]

    def valid(self):
        if self.value:
            for data in self.value:
                valid = data.valid()
                if valid != True:
                    return valid
        return True




class DictBasedObject(object):
    _structure = {}
    _deprecatedKeys = []
    _possible_keys = []
    _dataType_for_possible_keys = None


    def nonListProxyBasedKeys(self):

        _list = []

        for keyword in self._structure.keys():
            if not typeWorld.api.base.ListProxy in inspect.getmro(self._structure[keyword][0]):
                _list.append(keyword)

        _list.extend(self._deprecatedKeys)

        return _list



    def linkDocuText(self, text):

#       print text

        def my_replace(match):
            match = match.group()
            match = match[2:-2]

            if '.' in match:
                className, attributeName = match.split('.')

                if '()' in attributeName:
                    attributeName = attributeName[:-2]
                    match = '[%s.%s()](#user-content-class-%s-method-%s)' % (className, attributeName, className.lower(), attributeName.lower())
                else:
                    match = '[%s.%s](#user-content-class-%s-attribute-%s)' % (className, attributeName, className.lower(), attributeName.lower())
            else:
                className = match
                match = '[%s](#user-content-class-%s)' % (className, className.lower())


            return match
        
        try:
            text = re.sub(r'::.+?::', my_replace, text)
        except:
            pass

        return text or ''

    def typeDescription(self, class_):

        if issubclass(class_, ListProxy):
            try:
                return 'List of %s objects' % self.typeDescription(class_.dataType)
            except:
                return 'List of %s objects' % class_.dataType.dataType.__name__

        elif 'typeWorld.api.' in ('%s' % class_.dataType):
            return self.linkDocuText('::%s::' % class_.dataType.__name__)

        elif 'typeWorld.api.base.' in ('%s' % class_.dataType):
            return self.linkDocuText('::%s::' % class_.dataType.__name__)

        return class_.dataType.__name__.title()

    def docu(self):

        classes = []

        # Define string
        docstring = ''
        head = ''
        attributes = ''
        methods = ''
        attributesList = []
        methodsList = []


        head += '<div id="class-%s"></div>\n\n' % self.__class__.__name__.lower()

        head += '# _class_ %s()\n\n' % self.__class__.__name__

        head += self.linkDocuText(inspect.getdoc(self))

        head += '\n\n'

        # attributes

        attributes += '## Attributes\n\n'

        for key in sorted(self._structure.keys()):


            attributesList.append(key)
            attributes += '<div id="class-%s-attribute-%s"></div>\n\n' % (self.__class__.__name__.lower(), key)
            attributes += '#### %s\n\n' % key

            # Description
            if self._structure[key][3]:
                attributes += self.linkDocuText(self._structure[key][3]) + '\n\n'

            attributes += 'Type: %s' % self.typeDescription(self._structure[key][0]) + '<br />\n'

            # Format Hint
            hint = self._structure[key][0]().formatHint()
            if hint:
                attributes += 'Format: %s' % hint + '<br />\n'

            attributes += 'Required: %s' % self._structure[key][1] + '<br />\n'

            if self._structure[key][2] != None:
                attributes += 'Default value: %s' % self._structure[key][2] + '\n\n'


        method_list = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__") and inspect.getdoc(getattr(self, func))]

        if method_list:
            methods += '## Methods\n\n'

            for methodName in method_list:

                methodsList.append(methodName)
                methods += '<div id="class-%s-method-%s"></div>\n\n' % (self.__class__.__name__.lower(), methodName.lower())

                args = inspect.getargspec(getattr(self, methodName))
                if args.args != ['self']:
                    
                    argList = []
                    if  args.args and args.defaults:

                        startPoint = len(args.args) - len(args.defaults)
                        for i, defaultValue in enumerate(args.defaults):
                            argList.append('%s = %s' % (args.args[i + startPoint], defaultValue))



                    methods += '#### %s(%s)\n\n' % (methodName, ', '.join(argList))
                else:
                    methods += '#### %s()\n\n' % methodName
                methods += self.linkDocuText(inspect.getdoc(getattr(self, methodName))) + '\n\n'

        # Compile
        docstring += head

        # TOC
        if attributesList:
            docstring += '### Attributes\n\n'
            for attribute in attributesList:
                docstring += '[%s](#class-%s-attribute-%s)<br />' % (attribute, self.__class__.__name__.lower(), attribute.lower())
            docstring += '\n\n'

        if methodsList:
            docstring += '### Methods\n\n'
            for methodName in methodsList:
                docstring += '[%s()](#class-%s-method-%s)<br />' % (methodName, self.__class__.__name__.lower(), methodName.lower())
            docstring += '\n\n'

        if attributesList:
            docstring += attributes
            docstring += '\n\n'
    
        if methodsList:
            docstring += methods
            docstring += '\n\n'


        # Add data
        classes.append([self.__class__.__name__, docstring])

        # Recurse
        for key in list(self._structure.keys()):
            if issubclass(self._structure[key][0], Proxy):

                o = self._structure[key][0].dataType()
                classes.extend(o.docu())

            if issubclass(self._structure[key][0], ListProxy):

                o = self._structure[key][0].dataType.dataType()
                if hasattr(o, 'docu'):
                    classes.extend(o.docu())

        return classes

    def __init__(self):

        super(DictBasedObject, self).__init__()

        object.__setattr__(self, '_content', {})
        object.__setattr__(self, '_allowedKeys', set(self._structure.keys()) | set(self._possible_keys))

        # Add base structure to main structure:
#       if hasattr(self, '_base_structure') and self._base_structure:
#           for key in self._base_structure.keys():
#               self._structure[key] = self._base_structure[key]


        # Fill default values
        for key in list(self._structure.keys()):

            # if required and default value is not empty
            if self._structure[key][1] and self._structure[key][2] is not None:
                setattr(self, key, self._structure[key][2])


    def initAttr(self, key):

        if key not in self._content:

            if key in list(object.__getattribute__(self, '_structure').keys()):
                self._content[key] = object.__getattribute__(self, '_structure')[key][0]()

            elif key in self._possible_keys:
                self._content[key] = self._dataType_for_possible_keys()

            self._content[key]._parent = self
#               print key, self._content[key]

#       print 'initAttr', self, key, self._content[key]

#       print self, key, self._content[key]
#           print self._content[key]


    def __getattr__(self, key):


        if key in self._allowedKeys:
            self.initAttr(key)
#           print '__getattr__', self, key, self._content[key]
            return self._content[key].get()

        elif object.__getattribute__(self, key):
            return object.__getattribute__(self, key)

        else:
            raise AttributeError('%s does not have an attribute "%s".' % (self.__class__.__name__, key))

    def __setattr__(self, key, value):

        if key in self._allowedKeys:
            self.initAttr(key)

            if issubclass(value.__class__, (DictBasedObject, ListProxy, Proxy, DataType)):
                object.__setattr__(value, '_parent', self)
#               print 'Setting _parent of %s to %s' % (value, self)

            self.__dict__['_content'][key].put(value)

        else:
            object.__setattr__(self, key, value)

#       else:
#           raise AttributeError('%s.%s is not a valid attribute.' % (self, key))

    def set(self, key, value):
        self.__setattr__(key, value)

    def get(self, key):
        return self.__getattr__(key)

    def validateData(self, key, data):
        information = []
        warnings = []
        critical = []

        if data != None and isinstance(data.valid, types.MethodType) and isinstance(data.get, types.MethodType):
            if data.get() != None:
                
                valid = data.valid()

                if valid == True:
                    pass

                elif type(valid) == str or type(valid) == str:
                    critical.append('%s.%s is invalid: %s' % (self, key, valid))

                else:
                    critical.append('%s.%s is invalid for an unknown reason' % (self, key))


        return information, warnings, critical

    def _validate(self):

#       print '____validate()', self

        information = []
        warnings = []
        critical = []

        def extendWithKey(values):
            _list = []
            for value in values:
                _list.append('%s.%s --> %s' % (self, key, value))
            return _list


        # Check if required fields are filled
        for key in list(self._structure.keys()):

#           if self._structure[key][1]:
            self.initAttr(key)

            # if self._structure[key][1]:
            #   if 'fonts' in key:
            #       print key, self._content[key].isEmpty()


#           print key, self._content[key], self._content[key].isEmpty()

            if self.discardThisKey(key) == False:

                if self._structure[key][1] and self._content[key].isEmpty():
                    critical.append('%s.%s is a required attribute, but empty' % (self, key))

                else:
                    # recurse
                    if issubclass(self._content[key].__class__, (Proxy)):
                        if self._content[key]:
            
    #                       print 'isProxy', key, self._content[key], self._content[key].isEmpty()

                            if self._content[key].isEmpty() == False:
                                if self._content[key].value:
                                    newInformation, newWarnings, newCritical = self._content[key].value._validate()
                                    information.extend(extendWithKey(newInformation))
                                    warnings.extend(extendWithKey(newWarnings))
                                    critical.extend(extendWithKey(newCritical))

                                # Check custom messages:
                                if hasattr(self._content[key].value, 'customValidation') and isinstance(self._content[key].value.customValidation, types.MethodType):
                                    newInformation, newWarnings, newCritical = self._content[key].value.customValidation()
                                    information.extend(extendWithKey(newInformation))
                                    warnings.extend(extendWithKey(newWarnings))
                                    critical.extend(extendWithKey(newCritical))


                    # recurse
                    if issubclass(self._content[key].__class__, ListProxy):


                        if self._content[key].isEmpty() == False:
                            for item in self._content[key]:
                                if hasattr(item, '_validate') and isinstance(item._validate, types.MethodType):
                                    newInformation, newWarnings, newCritical = item._validate()
                                    information.extend(extendWithKey(newInformation))
                                    warnings.extend(extendWithKey(newWarnings))
                                    critical.extend(extendWithKey(newCritical))

                                # Check custom messages:
                                if hasattr(item, 'customValidation') and isinstance(item.customValidation, types.MethodType):
                                    newInformation, newWarnings, newCritical = item.customValidation()
                                    information.extend(extendWithKey(newInformation))
                                    warnings.extend(extendWithKey(newWarnings))
                                    critical.extend(extendWithKey(newCritical))

    #           if self._structure[key][1] == False and self._content[key].isEmpty():

    #           print inspect.getmro(self._content[key].value)


                    # Check data types for validity recursively
                    for key in list(self._content.keys()):

                        if self._content[key].isEmpty() == False:
                            # field is required or empty
                            if (key in self._structure and self._structure[key][1]) or (key in self._content and self._content[key].isEmpty()):
                                self.initAttr(key)
                                data = self._content[key]
                #               print data

                                newInformation, newWarnings, newCritical = self.validateData(key, data)
                                information.extend(extendWithKey(newInformation))
                                warnings.extend(extendWithKey(newWarnings))
                                critical.extend(extendWithKey(newCritical))

            #Check custom messages:
            # if hasattr(self, 'customValidation') and isinstance(self.customValidation, types.MethodType):
            #   newWarnings, newCritical = self.customValidation()
            #   warnings.extend(newWarnings)
            #   critical.extend(newCritical)



        return information, warnings, critical

    def discardThisKey(self, key):

        return False

    def validate(self):
        return self._validate()


    def dumpDict(self):

        d = {}

        # Auto-validate
        information, warnings, critical = self.validate()
        if critical:
            raise ValueError(critical[0])


        for key in list(self._content.keys()):
            
            if self.discardThisKey(key) == False:

                # if required or not empty
                if (key in self._structure and self._structure[key][1]) or getattr(self, key) is not None:

                    
                    if hasattr(getattr(self, key), 'dumpDict'):
                        d[key] = getattr(self, key).dumpDict()

                    # elif issubclass(getattr(self, key).__class__, (DictBasedObject)):
                    #   d[key] = getattr(self, key).dumpDict()

                    elif issubclass(getattr(self, key).__class__, (ListProxy)):
                        d[key] = list(getattr(self, key))

                        if len(d[key]) > 0 and hasattr(d[key][0], 'dumpDict'):
                            d[key] = [x.dumpDict() for x in d[key]]

                    else:
                        d[key] = getattr(self, key)

                    # delete empty sets that are not required
                    if (key in self._structure and self._structure[key][1] == False) and not d[key]:
                        del d[key]


        return d

    def loadDict(self, d):


        for key in list(d.keys()):
            if key in self._allowedKeys:

#               print 'Load key %s' % key

                if key in list(self._structure.keys()):

                    if issubclass(self._structure[key][0], (Proxy)):
 #                      print 'Proxy', self._structure[key][0].dataType

#                       exec('self.%s = d[key]' % (key))
                        exec('self.%s = typeWorld.api.%s()' % (key, self._structure[key][0].dataType.__name__))
                        exec('self.%s.loadDict(d[key])' % (key))
                    elif issubclass(self._structure[key][0], (ListProxy)):
#                       print 'ListProxy', self._structure[key][0].dataType
                        _list = self.__getattr__(key)
                        for item in d[key]:
                            o = self._structure[key][0].dataType.dataType()

                            if hasattr(o, 'loadDict'):
                                o.loadDict(item)
                                _list.append(o)
                            else:
                                _list.append(item)
                        exec('self._content[key] = _list')

                    else:
                        self.set(key, d[key])

    def dumpJSON(self):
        return json.dumps(self.dumpDict(), indent=2)

    def loadJSON(self, j):
        self.loadDict(json.loads(j))


class Proxy(DataType):
    pass    

    # def _validate(self):
    #     if hasattr(self, 'value') and hasattr(object.__getattribute__(self, 'value'), 'valid') and isinstance(object.__getattribute__(self, 'value').valid, types.MethodType):
    #         return object.__getattribute__(self, 'value').valid()
    #     else:
    #         return True



class MultiLanguageText(DictBasedObject):
    """\
Multi-language text. Attributes are language keys as per [https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes]

The GUI app will then calculate the language data to be displayed using ::MultiLanguageText.getText():: with a prioritized list of languages that the user can understand. They may be pulled from the operating system’s language preferences.

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

"""

    _possible_keys = ['ab', 'aa', 'af', 'ak', 'sq', 'am', 'ar', 'an', 'hy', 'as', 'av', 'ae', 'ay', 'az', 'bm', 'ba', 'eu', 'be', 'bn', 'bh', 'bi', 'bs', 'br', 'bg', 'my', 'ca', 'ch', 'ce', 'ny', 'zh', 'cv', 'kw', 'co', 'cr', 'hr', 'cs', 'da', 'dv', 'nl', 'dz', 'en', 'eo', 'et', 'ee', 'fo', 'fj', 'fi', 'fr', 'ff', 'gl', 'ka', 'de', 'el', 'gn', 'gu', 'ht', 'ha', 'he', 'hz', 'hi', 'ho', 'hu', 'ia', 'id', 'ie', 'ga', 'ig', 'ik', 'io', 'is', 'it', 'iu', 'ja', 'jv', 'kl', 'kn', 'kr', 'ks', 'kk', 'km', 'ki', 'rw', 'ky', 'kv', 'kg', 'ko', 'ku', 'kj', 'la', 'lb', 'lg', 'li', 'ln', 'lo', 'lt', 'lu', 'lv', 'gv', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mh', 'mn', 'na', 'nv', 'nd', 'ne', 'ng', 'nb', 'nn', 'no', 'ii', 'nr', 'oc', 'oj', 'cu', 'om', 'or', 'os', 'pa', 'pi', 'fa', 'pl', 'ps', 'pt', 'qu', 'rm', 'rn', 'ro', 'ru', 'sa', 'sc', 'sd', 'se', 'sm', 'sg', 'sr', 'gd', 'sn', 'si', 'sk', 'sl', 'so', 'st', 'es', 'su', 'sw', 'ss', 'sv', 'ta', 'te', 'tg', 'th', 'ti', 'bo', 'tk', 'tl', 'tn', 'to', 'tr', 'ts', 'tt', 'tw', 'ty', 'ug', 'uk', 'ur', 'uz', 've', 'vi', 'vo', 'wa', 'cy', 'wo', 'fy', 'xh', 'yi', 'yo', 'za', 'zu']
    _dataType_for_possible_keys = UnicodeDataType
    _length = 1000

    def __repr__(self):
        return '<MultiLanguageText>'

    def getTextAndLocale(self, locale = ['en']):
        '''Like getText(), but additionally returns the language of whatever text was found first.'''

        if type(locale) in (str, str):
            if self.get(locale):
                return self.get(locale), locale

        elif type(locale) in (list, tuple):
            for key in locale:
                if self.get(key):
                    return self.get(key), key

        # try english
        if self.get('en'):
            return self.get('en'), 'en'

        # try anything
        for key in self._possible_keys:
            if self.get(key):
                return self.get(key), key

        return None, None

    def getText(self, locale = ['en']):
        '''Returns the text in the first language found from the specified list of languages. If that language can’t be found, we’ll try English as a standard. If that can’t be found either, return the first language you can find.'''

        text, locale = self.getTextAndLocale(locale)

        return text


    def customValidation(self):

        information, warnings, critical = [], [], []

        if self.isEmpty():
            critical.append('%s needs to contain at least one language field' % (self))

        # Check for text length
        for langId in self._possible_keys:
            if self.get(langId):
#           if self._content.has_key(langId):
                if len(self.get(langId)) > self._length:
                    critical.append('%s.%s is too long. Allowed are %s characters.' % (self, langId, self._length))
#       return True
        return information, warnings, critical

    def isEmpty(self):
        # Check for existence of languages
        hasAtLeastOneLanguage = False
        for langId in self._possible_keys:
            if langId in self._content:
                hasAtLeastOneLanguage = True
                break

#       print self, self._parent._parent, 'hasAtLeastOneLanguage', hasAtLeastOneLanguage
        if hasAtLeastOneLanguage:
            return False
        else:
            return True

    def valid(self):
        # Check for text length
        for langId in self._possible_keys:
            if langId in self._content:
                if len(getattr(self, langId)) > self._length:
                    return '%s.%s is too long. Allowed are %s characters.' % (self, langId, self._length)

        return True



    def loadDict(self, d):
        for key in list(d.keys()):
            self.set(key, d[key])

def MultiLanguageText_Parent(self):
    if hasattr(self, '_parent') and hasattr(self._parent, '_parent'):
        return self._parent._parent
MultiLanguageText.parent = property(lambda self: MultiLanguageText_Parent(self))


class MultiLanguageTextProxy(Proxy):
    dataType = MultiLanguageText

    def isEmpty(self):
        return self.value.isEmpty()

class MultiLanguageTextListProxy(ListProxy):
    dataType = MultiLanguageTextProxy



####################################################################################################################################

#  Object model

class OpenSourceLicenseIdentifierDataType(UnicodeDataType):
    
    def valid(self):
        if self.value in OPENSOURCELICENSES:
            return True
        else:
            return 'Unknown license identifier: "%s". See https://spdx.org/licenses/' % (self.value)


class SupportedAPICommandsDataType(UnicodeDataType):
    
    commands = [x['keyword'] for x in COMMANDS]


    def valid(self):
        if self.value in self.commands:
            return True
        else:
            return 'Unknown API command: "%s". Possible: %s' % (self.value, self.commands)

class SupportedAPICommandsListProxy(ListProxy):
    dataType = SupportedAPICommandsDataType


class FontTypeDataType(UnicodeDataType):
    def valid(self):
        if self.value in list(FONTTYPES.keys()):
            return True
        else:
            return 'Unknown font type: "%s". Possible: %s' % (self.value, list(FONTTYPES.keys()))


class FontExtensionDataType(UnicodeDataType):
    def valid(self):

        found = False

        for mimeType in list(MIMETYPES.keys()):
            if self.value in MIMETYPES[mimeType]['fileExtensions']:
                found = True
                break

        if found:
            return True
        else:

            return 'Unknown font extension: "%s". Possible: %s' % (self.value, FILEEXTENSIONS)

##############################################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################
