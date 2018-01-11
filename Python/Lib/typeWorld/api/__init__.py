# -*- coding: utf-8 -*-

import json, copy, types, inspect, re
from optparse import OptionParser

import logging
logging.basicConfig()

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
				return 'Wrong data type. Is %s, should be: %s' % (type(self.value), self.dataType)
		else:
			return True

	def get(self):
		return self.value

	def put(self, value):


		self.value = self.shapeValue(value)

		if issubclass(self.value.__class__, (DictBasedObject, ListProxy, Proxy, DataType)):
#			print 'Setting _parent of %s to %s' % (self.value, self)
			object.__setattr__(self.value, '_parent', self)

		valid = self.valid()
		if valid != True and valid != None:
			raise ValueError(valid)

	def shapeValue(self, value):
		return value

	def isEmpty(self):
		return self.value == None or self.value == [] or self.value == ''

class BooleanDataType(DataType):
	dataType = bool

class IntegerDataType(DataType):
	dataType = int

class FloatDataType(DataType):
	dataType = float

class StringDataType(DataType):
	dataType = str

class UnicodeDataType(DataType):
	dataType = unicode

class WebURLDataType(UnicodeDataType):

	def shapeValue(self, value):
		return value.lower()

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
			len(self.value) == 3 or \
			len(self.value) == 6 or \
			re.match("^[A-Fa-f0-9]*$", self.value):

			return True
		else:
			return 'Not a valid hex color of format RRGGBB (like FF0000 for red): %s' % self.value



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
#			print 'Setting _parent of %s to %s' % (value, self)

		self.value[i].put(value)
		object.__setattr__(self.value[i], '_parent', self)
#		print 'Setting _parent of %s to %s' % (self.value[i], self)

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
#			print 'Setting _parent of %s to %s (in .append())' % (value, self)

		if issubclass(newData.__class__, (DictBasedObject, Proxy, ListProxy, DataType)):
			object.__setattr__(newData, '_parent', self)
#			print 'Setting _parent of %s to %s (in .append())' % (value, self)


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
	_possible_keys = []
	_dataType_for_possible_keys = None


	def linkDocuText(self, text):

#		print text

		def my_replace(match):
			match = match.group()
			match = match[2:-2]

			if '.' in match:
				className, attributeName = match.split('.')

				if '()' in attributeName:
					attributeName = attributeName[:-2]
					match = u'[%s.%s()](#class_%s_method_%s)' % (className, attributeName, className, attributeName)
				else:
					match = u'[%s.%s](#class_%s_attribute_%s)' % (className, attributeName, className, attributeName)
			else:
				className = match
				match = u'[%s](#class_%s)' % (className, className)


			return match
		
		try:
			text = re.sub(r'::.+?::', my_replace, text)
		except:
			pass

		return text or u''

	def typeDescription(self, class_):

		if issubclass(class_, ListProxy):
			try:
				return 'List of %s objects' % self.typeDescription(class_.dataType)
			except:
				return 'List of %s objects' % class_.dataType.dataType.__name__

		elif 'typeWorld.api.' in ('%s' % class_.dataType):
			return self.linkDocuText('::%s::' % class_.dataType.__name__)


		return class_.dataType.__name__.title()

	def docu(self):

		classes = []

		# Define string
		docstring = u''
		head = u''
		attributes = u''
		methods = u''
		attributesList = []
		methodsList = []


		head += u'<div id="class_%s"></div>\n\n' % self.__class__.__name__

		head += u'# _class_ %s()\n\n' % self.__class__.__name__

		head += self.linkDocuText(inspect.getdoc(self))

		head += u'\n\n'

		# attributes

		attributes += u'## Attributes\n\n'

		for key in sorted(self._structure.keys()):


			attributesList.append(key)
			attributes += u'<div id="class_%s_attribute_%s"></div>\n\n' % (self.__class__.__name__, key)
			attributes += u'#### %s\n\n' % key

			if self._structure[key][3]:
				attributes += self.linkDocuText(self._structure[key][3]) + u'\n\n'

			attributes += u'Type: %s' % self.typeDescription(self._structure[key][0]) + u'<br />\n'
			attributes += u'Required: %s' % self._structure[key][1] + u'<br />\n'

			if self._structure[key][2] != None:
				attributes += u'Default value: %s' % self._structure[key][2] + u'\n\n'


		method_list = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__") and inspect.getdoc(getattr(self, func))]

		if method_list:
			methods += u'## Methods\n\n'

			for methodName in method_list:

				methodsList.append(methodName)
				methods += u'<div id="class_%s_method_%s"></div>\n\n' % (self.__class__.__name__, methodName)

				args = inspect.getargspec(getattr(self, methodName))
				if args.args != ['self']:
					
					argList = []
					startPoint = len(args.args) - len(args.defaults)
					for i, defaultValue in enumerate(args.defaults):
						argList.append('%s = %s' % (args.args[i + startPoint], defaultValue))



					methods += u'#### %s(%s)\n\n' % (methodName, ', '.join(argList))
				else:
					methods += u'#### %s()\n\n' % methodName
				methods += self.linkDocuText(inspect.getdoc(getattr(self, methodName))) + u'\n\n'

		# Compile
		docstring += head

		# TOC
		if attributesList:
			docstring += u'### Attributes\n\n'
			for attribute in attributesList:
				docstring += u'[%s](#class_%s_attribute_%s)<br />' % (attribute, self.__class__.__name__, attribute)
			docstring += u'\n\n'

		if methodsList:
			docstring += u'### Methods\n\n'
			for methodName in methodsList:
				docstring += '[%s()](#class_%s_method_%s)<br />' % (methodName, self.__class__.__name__, methodName)
			docstring += u'\n\n'

		if attributesList:
			docstring += attributes
			docstring += u'\n\n'
	
		if methodsList:
			docstring += methods
			docstring += u'\n\n'


		# Add data
		classes.append([self.__class__.__name__, docstring])

		# Recurse
		for key in self._structure.keys():
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

		# Add base structure to main structure:
#		if hasattr(self, '_base_structure') and self._base_structure:
#			for key in self._base_structure.keys():
#				self._structure[key] = self._base_structure[key]


		# Fill default values
		for key in self._structure.keys():

			# if required and default value is not empty
			if self._structure[key][1] and self._structure[key][2] is not None:
				setattr(self, key, self._structure[key][2])


	def initAttr(self, key):

		if not self._content.has_key(key):

			if key in object.__getattribute__(self, '_structure').keys():
				self._content[key] = object.__getattribute__(self, '_structure')[key][0]()

			elif key in self._possible_keys:
				self._content[key] = self._dataType_for_possible_keys()

			self._content[key]._parent = self
#				print key, self._content[key]

#		print 'initAttr', self, key, self._content[key]

#		print self, key, self._content[key]
#			print self._content[key]


	def __getattr__(self, key):


		if key in self.allowedKeys():
			self.initAttr(key)
#			print '__getattr__', self, key, self._content[key]
			return self._content[key].get()

		elif object.__getattribute__(self, key):
			return object.__getattribute__(self, key)

		else:
			raise AttributeError('%s does not have an attribute "%s".' % (self.__class__.__name__, key))

	def __setattr__(self, key, value):
		if key in self.allowedKeys():
			self.initAttr(key)

			if issubclass(value.__class__, (DictBasedObject, ListProxy, Proxy, DataType)):
				object.__setattr__(value, '_parent', self)
#				print 'Setting _parent of %s to %s' % (value, self)

			self.__dict__['_content'][key].put(value)

		else:
			object.__setattr__(self, key, value)

#		else:
#			raise AttributeError('%s.%s is not a valid attribute.' % (self, key))

	def set(self, key, value):
		self.__setattr__(key, value)

	def get(self, key):
		return self.__getattr__(key)

	def allowedKeys(self):
		allowed = set(self._structure.keys()) | set(self._possible_keys)
		return allowed

	def validateData(self, key, data):
		information = []
		warnings = []
		critical = []

		if data != None and isinstance(data.valid, types.MethodType) and isinstance(data.get, types.MethodType):
			if data.get() != None:
				
				valid = data.valid()

				if valid == True:
					pass

				elif type(valid) == str or type(valid) == unicode:
					critical.append('%s.%s is invalid: %s' % (self, key, valid))

				else:
					critical.append('%s.%s is invalid for an unknown reason' % (self, key))


		return information, warnings, critical

	def _validate(self):

#		print '____validate()', self

		information = []
		warnings = []
		critical = []

		def extendWithKey(values):
			_list = []
			for value in values:
				_list.append('%s.%s --> %s' % (self, key, value))
			return _list


		# Check if required fields are filled
		for key in self._structure.keys():

#			if self._structure[key][1]:
			self.initAttr(key)

			# if self._structure[key][1]:
			# 	if 'fonts' in key:
			# 		print key, self._content[key].isEmpty()


#			print key, self._content[key], self._content[key].isEmpty()

			if self._structure[key][1] and self._content[key].isEmpty():
				critical.append('%s.%s is a required attribute, but empty' % (self, key))

			else:
				# recurse
				if issubclass(self._content[key].__class__, (Proxy)):
					if self._content[key]:
		
#						print 'isProxy', key, self._content[key], self._content[key].isEmpty()

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

#			if self._structure[key][1] == False and self._content[key].isEmpty():

#			print inspect.getmro(self._content[key].value)


				# Check data types for validity recursively
				for key in self._content.keys():

					if self._content[key].isEmpty() == False:
						# field is required or empty
						if (self._structure.has_key(key) and self._structure[key][1]) or (self._content.has_key(key) and self._content[key].isEmpty()):
							self.initAttr(key)
							data = self._content[key]
			#				print data

							newInformation, newWarnings, newCritical = self.validateData(key, data)
							information.extend(extendWithKey(newInformation))
							warnings.extend(extendWithKey(newWarnings))
							critical.extend(extendWithKey(newCritical))

		#Check custom messages:
		# if hasattr(self, 'customValidation') and isinstance(self.customValidation, types.MethodType):
		# 	newWarnings, newCritical = self.customValidation()
		# 	warnings.extend(newWarnings)
		# 	critical.extend(newCritical)



		return information, warnings, critical

	def validate(self):
		return self._validate()


	def dumpDict(self):

		d = {}

		# Auto-validate
		information, warnings, critical = self.validate()
		if critical:
			raise ValueError(critical[0])


		for key in self._content.keys():
			

			# if required or not empty
			if (self._structure.has_key(key) and self._structure[key][1]) or getattr(self, key) is not None:

				
				if hasattr(getattr(self, key), 'dumpDict'):
					d[key] = getattr(self, key).dumpDict()

				# elif issubclass(getattr(self, key).__class__, (DictBasedObject)):
				# 	d[key] = getattr(self, key).dumpDict()

				elif issubclass(getattr(self, key).__class__, (ListProxy)):
					d[key] = list(getattr(self, key))

					if len(d[key]) > 0 and hasattr(d[key][0], 'dumpDict'):
						d[key] = [x.dumpDict() for x in d[key]]

				else:
					d[key] = getattr(self, key)

				# delete empty sets that are not required
				if (self._structure.has_key(key) and self._structure[key][1] == False) and not d[key]:
					del d[key]


		return d

	def loadDict(self, d):

		allowedKeys = self.allowedKeys()

		for key in d.keys():
			if key in allowedKeys:

#				print 'Load key %s' % key

 				if key in self._structure.keys():

 					if issubclass(self._structure[key][0], (Proxy)):
 #						print 'Proxy', self._structure[key][0].dataType

# 						exec('self.%s = d[key]' % (key))
 						exec('self.%s = %s()' % (key, self._structure[key][0].dataType.__name__))
 						exec('self.%s.loadDict(d[key])' % (key))

 					elif issubclass(self._structure[key][0], (ListProxy)):
# 						print 'ListProxy', self._structure[key][0].dataType

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
	
	def _valid(self):
		if hasattr(self, 'value') and hasattr(object.__getattribute__(self, 'value'), 'valid') and isinstance(object.__getattribute__(self, 'value').valid, types.MethodType):
			return object.__getattribute__(self, 'value').valid()
		else:
			return True



class MultiLanguageText(DictBasedObject):
	u"""\
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

	def getText(self, locale = ['en']):
		u'''Returns the text in the first language found from the specified list of languages. If that language can’t be found, we’ll try English as a standard. If that can’t be found either, return the first language you can find.'''

		if type(locale) in (str, unicode):
			if self.get(locale):
				return self.get(locale)

		elif type(locale) in (str, unicode):
			for key in locale:
				if self.get(key):
					return self.get(key)

		# try english
		if self.get('en'):
			return self.get('en')

		# try anything
		for key in self._possible_keys:
			if self.get(key):
				return self.get(key)


	def customValidation(self):

		information, warnings, critical = [], [], []

		if self.isEmpty():
			critical.append('%s needs to contain at least one language field' % (self))

		# Check for text length
		for langId in self._possible_keys:
			if self._content.has_key(langId):
				if len(getattr(self, langId)) > self._length:
					critical.append('%s.%s is too long. Allowed are %s characters.' % (self, langId, self._length))
#		return True
		return information, warnings, critical

	def isEmpty(self):
		# Check for existence of languages
		hasAtLeastOneLanguage = False
		for langId in self._possible_keys:
			if self._content.has_key(langId):
				hasAtLeastOneLanguage = True
				break

#		print self, self._parent._parent, 'hasAtLeastOneLanguage', hasAtLeastOneLanguage
		if hasAtLeastOneLanguage:
			return False
		else:
			return True

	def valid(self):
		# Check for text length
		for langId in self._possible_keys:
			if self._content.has_key(langId):
				if len(getattr(self, langId)) > self._length:
					return '%s.%s is too long. Allowed are %s characters.' % (self, langId, self._length)

		return True



	def loadDict(self, d):
		for key in d.keys():
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



##############################################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################


# Response types (success, error, ...)
SUCCESS = 'success'
ERROR = 'error'
CUSTOM = 'custom'


# Commands
INSTALLABLEFONTSCOMMAND = {
	'keyword': 'installableFonts',
	'currentVersion': 0.1,
	'versionHistory': [0.1],
	'responseTypes': [SUCCESS, ERROR, CUSTOM],
	'acceptableMimeTypes': ['application/json'],
	}
INSTALLFONTSCOMMAND ={
	'keyword': 'installFonts',
	'currentVersion': 0.1,
	'versionHistory': [0.1],
	'responseTypes': [SUCCESS, ERROR, CUSTOM],
	'acceptableMimeTypes': ['application/json', 'application/x-font-ttf', 'application/x-font-truetype', 'application/x-font-opentype'],
	}
UNINSTALLFONTSCOMMAND =	{
	'keyword': 'uninstallFonts',
	'currentVersion': 0.1,
	'versionHistory': [0.1],
	'responseTypes': [SUCCESS, ERROR, CUSTOM],
	'acceptableMimeTypes': ['application/json'],
	}
COMMANDS = [INSTALLABLEFONTSCOMMAND, INSTALLFONTSCOMMAND, UNINSTALLFONTSCOMMAND]

FONTTYPES = ['desktop', 'web', 'app']


####################################################################################################################################

#  Object model

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
		if self.value in FONTTYPES:
			return True
		else:
			return 'Unknown font type: "%s". Possible: %s' % (self.value, FONTTYPES)

####################################################################################################################################

#  License

class License(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'keyword':	 				[UnicodeDataType,		True, 	None, 	'Keyword under which the license will be referenced from the individual fonts.'],
		'name':	 					[MultiLanguageTextProxy,		True, 	None, 	'Human-readable name of font license'],
		'URL':	 					[WebURLDataType,		True, 	None, 	'URL where the font license can be viewed online'],
	}

	def __repr__(self):
		return '<License "%s">' % self.name or self.keyword or 'undefined'

def License_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
License.parent = property(lambda self: License_Parent(self))

class LicenseProxy(Proxy):
	dataType = License

class LicensesListProxy(ListProxy):
	dataType = LicenseProxy


####################################################################################################################################

#  Designer

class Designer(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'keyword':	 				[UnicodeDataType,		True, 	None, 	'Keyword under which the designer will be referenced from the individual fonts or font families'],
		'name':	 					[MultiLanguageTextProxy,		True, 	None, 	'Human-readable name of designer'],
		'website':	 				[WebURLDataType,		False, 	None, 	u'Designer’s web site'],
		'description':	 			[MultiLanguageTextProxy,		False, 	None, 	'Description of designer'],
	}

	def __repr__(self):
		return '<Designer "%s">' % self.name.getText() or self.keyword or 'undefined'

def Designer_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
Designer.parent = property(lambda self: Designer_Parent(self))

class DesignerProxy(Proxy):
	dataType = Designer

class DesignersListProxy(ListProxy):
	dataType = DesignerProxy

class DesignersReferencesListProxy(ListProxy):
	dataType = UnicodeDataType

####################################################################################################################################

#  Font Family Version


class Version(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'number':	 				[FloatDataType,				True, 	None, 	'Font version number'],
		'description':	 			[MultiLanguageTextProxy,	False, 	None, 	'Description of font version'],
	}

	def __repr__(self):
		return '<Version %s (%s)>' % (self.number if self.number else 'None', 'font-specific' if self.isFontSpecific() else 'family-specific')

	def isFontSpecific(self):
		u'''\
		Returns True if this version is defined at the font level. Returns False if this version is defined at the family level.
		'''
		return issubclass(self.parent.__class__, Font)

def Version_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
Version.parent = property(lambda self: Version_Parent(self))

class VersionProxy(Proxy):
	dataType = Version

class VersionListProxy(ListProxy):
	dataType = VersionProxy


####################################################################################################################################

#  Fonts

class Font(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'name':	 			[MultiLanguageTextProxy,		True, 	None, 	u'Human-readable name of font. This may include any additions that you find useful to communicate to your users.'],
		'postScriptName':	[UnicodeDataType,		True, 	None, 	u'Complete PostScript name of font'],
		'previewImage':		[WebURLDataType,		False, 	None, 	u'URL of preview image of font, specifications to follow'],
		'variantName':		[MultiLanguageTextProxy,		False, 	None, 	'Optional variant name of font. This is used to visually group fonts in the UI. Thinking "Office Fonts" and such.'],
		'licenseKeyword':	[UnicodeDataType,		True, 	None, 	u'Keyword reference of font’s license. This license must be specified in the Foundry.Licenses'],
		'versions':	 		[VersionListProxy,		False, 	None, 	u'List of ::Version:: objects. These are font-specific versions; they may exist only for this font. You may define additional versions at the family object under ::Family.versions::, which are then expected to be available for the entire family. However, either the fonts or the font family *must* carry version information and the validator will complain when they don’t.\n\nPlease also read the section on [versioning](#versioning) above.'],
		'designers':	 	[DesignersReferencesListProxy,	False, 	None, 	u'List of keywords referencing designers. These are defined at ::InstallableFontsResponse.designers::. This attribute overrides the designer definitions at the family level at ::Family.designers::.'],
		'free':				[BooleanDataType,		False, 	None, 	u'Font is freeware. For UI signaling'],
		'beta':				[BooleanDataType,		False, 	None, 	u'Font is in beta stage. For UI signaling'],
		'variableFont':		[BooleanDataType,		False, 	None, 	u'Font is an OpenType Variable Font. For UI signaling'],
#		'public':			[BooleanDataType,		False, 	False, 	u'If false, signals restricted access to a commercial font only available to certain users. Download and installation may be restricted by the API point depending on the API point URL that needs to include the private key to identify the user.'],
		'type':				[FontTypeDataType,		True, 	None, 	u'Technical type of font. This influences how the app handles the font. For instance, it will only install desktop fonts on the system, and make other font types available though folders. Possible: %s' % (FONTTYPES)],
		'seatsAllowed':		[IntegerDataType,		False, 	None, 	u'In case of desktop font (see ::Font.type::), number of installations permitted by the user’s license.'],
		'seatsInstalled':	[IntegerDataType,		False, 	None, 	u'In case of desktop font (see ::Font.type::), number of installations recorded by the API endpoint. This value will need to be supplied by the API endpoint through tracking all font installations through the "anonymousAppID" parameter of the "%s" and "%s" command. Please note that the app is currently not designed to reject installations of the fonts when the limits are exceeded. Instead it is in the responsibility of the API endpoint to reject font installations though the "%s" command when the limits are exceeded.' % (INSTALLFONTSCOMMAND['keyword'], UNINSTALLFONTSCOMMAND['keyword'], INSTALLFONTSCOMMAND['keyword'])],
		'licenseAllowanceDescription':	[MultiLanguageTextProxy,		False, 	None, 	u'In case of non-desktop font (see ::Font.type::), custom string for web fonts or app fonts reminding the user of the license’s limits, e.g. "100.000 page views/month"'],
		'upgradeLicenseURL':[WebURLDataType,		False, 	None, 	u'URL the user can be sent to to upgrade the license of the font, for instance at the foundry’s online shop'],
		'upgradeLicenseURL':[WebURLDataType,		False, 	None, 	u'URL the user can be sent to to upgrade the license of the font, for instance at the foundry’s online shop'],
		'timeAdded':		[IntegerDataType,		False, 	None, 	u'Timestamp of the time the user has purchased this font or the font has become available to the user otherwise, like a new font within a foundry’s beta font repository. Will be used in the UI to signal which fonts have become newly available in addition to previously available fonts.'],
	}

	def __repr__(self):
		return '<Font "%s">' % (self.postScriptName or self.name.getText() or 'undefined')

	def hasVersionInformation(self):
		return self.versions or self.parent.versions

	def getLicense(self):
		u'''\
		Returns the ::License:: object that this font references.
		'''
		return self.parent.parent.getLicenseByKeyword(self.licenseKeyword)

	def customValidation(self):
		information, warnings, critical = [], [], []

		# Checking version information
		if not self.hasVersionInformation():
			critical.append('The font %s has no version information, and neither has its family %s. Either one needs to carry version information.' % (self, self.parent))

		# Checking for existing license
		if not self.getLicense():
			critical.append('%s has license "%s", but %s has no matching license.' % (self, self.licenseKeyword, self.parent.parent))

		return information, warnings, critical

	def getSortedVersions(self):
		u'''\
		Returns list of ::Version:: objects.

		This is the final list based on the version information in this font object as well as in its parent ::Family:: object. Please read the section about [versioning](#versioning) above.
		'''

		if not self.hasVersionInformation():
			raise ValueError('Font %s has no version information, and neither has its family %s. Either one needs to carry version information.' % (self, self.parent))

		versions = []
		haveVersionNumbers = []
		for version in self.versions:
			versions.append(version)
			haveVersionNumbers.append(version.number)
		for version in self.parent.versions:
			if not version.number in haveVersionNumbers:
				versions.append(version)
				haveVersionNumbers.append(version.number)

		versions.sort(key=lambda x: x.number, reverse=False)
		return versions

	def getDesigners(self):
		u'''\
		Returns a list of ::Designer:: objects that this font references. These are the combination of family-level designers and font-level designers. The same logic as for versioning applies. Please read the section about [versioning](#versioning) above.
		'''
		if not hasattr(self, '_designers'):
			self._designers = []

			# Family level designers
			if self.parent.designers:
				for designerKeyword in self.parent.designers:
					self._designers.append(self.parent.parent.parent.getDesignerByKeyword(designerKeyword))

			# Font level designers
			if self.designers:
				for designerKeyword in self.designers:
					self._designers.append(self.parent.parent.parent.getDesignerByKeyword(designerKeyword))

		return self._designers


def Font_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
Font.parent = property(lambda self: Font_Parent(self))


class FontProxy(Proxy):
	dataType = Font

class FontListProxy(ListProxy):
	dataType = FontProxy


# Font Family

class BillboardListProxy(ListProxy):
	dataType = WebURLDataType

class Family(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'name':	 					[MultiLanguageTextProxy,		True, 	None, 	u'Human-readable name of font family. This may include any additions that you find useful to communicate to your users.'],
		'description':	 			[MultiLanguageTextProxy,False, 	None, 	u'Description of font family'],
		'billboards':	 			[BillboardListProxy,	False, 	None, 	u'List of URLs pointing at images to show for this typeface, specifications to follow'],
		'designers':	 			[DesignersReferencesListProxy,	False, 	None, 	u'List of keywords referencing designers. These are defined at ::InstallableFontsResponse.designers::. In case designers differ between fonts within the same family, they can also be defined at the font level at ::Font.designers::. The font-level references take precedence over the family-level references.'],

		'sourceURL':	 			[WebURLDataType,		False, 	None, 	u'URL pointing to the source of a font project, such as a GitHub repository'],
		'issueTrackerURL':	 		[WebURLDataType,		False, 	None, 	u'URL pointing to an issue tracker system, where users can debate about a typeface’s design or technicalities'],
		'versions':	 				[VersionListProxy,		False, 	None, 	u'List of ::Version:: objects. Versions specified here are expected to be available for all fonts in the family, which is probably most common and efficient. You may define additional font-specific versions at the ::Font:: object. You may also rely entirely on font-specific versions and leave this field here empty. However, either the fonts or the font family *must* carry version information and the validator will complain when they don’t.\n\nPlease also read the section on [versioning](#versioning) above.'],
		'fonts':	 				[FontListProxy,			True, 	None, 	u'List of ::Font:: objects.'],
	}

	def __repr__(self):
		return '<Family "%s">' % self.name.getText() or 'undefined'

	def getDesigners(self):
		if not hasattr(self, '_designers'):
			self._designers = []
			for designerKeyword in self.designers:
				self._designers.append(self.parent.parent.getDesignerByKeyword(designerKeyword))
		return self._designers

	def getAllDesigners(self):
		u'''\
		Returns a list of ::Designer:: objects that represent all of the designers referenced both at the family level as well as with all the family’s fonts, in case the fonts carry specific designers. This could be used to give a one-glance overview of all designers involved.
		'''
		if not hasattr(self, '_allDesigners'):
			self._allDesigners = []
			self._allDesignersKeywords = []
			for designerKeyword in self.designers:
				self._allDesigners.append(self.parent.parent.getDesignerByKeyword(designerKeyword))
				self._allDesignersKeywords.append(designerKeyword)
			for font in self.fonts:
				for designerKeyword in font.designers:
					if not designerKeyword in self._allDesignersKeywords:
						self._allDesigners.append(self.parent.parent.getDesignerByKeyword(designerKeyword))
						self._allDesignersKeywords.append(designerKeyword)
		return self._allDesigners

def Family_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
Family.parent = property(lambda self: Family_Parent(self))

class FamilyProxy(Proxy):
	dataType = Family

class FamiliesListProxy(ListProxy):
	dataType = FamilyProxy


####################################################################################################################################

#  Font Foundry

class Foundry(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'name':	 					[MultiLanguageTextProxy,		True, 	None, 	'Name of foundry'],
		'logo':	 					[WebURLDataType,		False, 	None, 	u'URL of foundry’s logo. Specifications to follow.'],
		'description':	 			[MultiLanguageTextProxy,False, 	None, 	'Description of foundry'],
		'email':	 				[EmailDataType,			False, 	None, 	'General email address for this foundry'],
		'supportEmail':	 			[EmailDataType,			False, 	None, 	'Support email address for this foundry'],
		'website':	 				[WebURLDataType,		False, 	None, 	'Website for this foundry'],
		'twitter':	 				[UnicodeDataType,		False, 	None, 	'Twitter handle for this foundry, without the @'],
		'facebook':	 				[WebURLDataType,		False, 	None, 	'Facebook page URL handle for this foundry. The URL '],
		'instagram':	 			[UnicodeDataType,		False, 	None, 	'Instagram handle for this foundry, without the @'],
		'skype':	 				[UnicodeDataType,		False, 	None, 	'Skype handle for this foundry'],
		'telephone':	 			[UnicodeDataType,		False, 	None, 	'Telephone number for this foundry'],

		#styling
		'backgroundColor': 			[HexColorDataType,		False, 	None, 	u'Six-digit RRGGBB hex color value (without leading "#") for foundry’s preferred background color'],

		# data
		'licenses':					[LicensesListProxy,		True, 	None, 	'List of ::License:: objects under which the fonts in this response are issued. For space efficiency, these licenses are defined at the foundry object and will be referenced in each font by their keyword. Keywords need to be unique for this foundry and may repeat across foundries.'],
		'families':					[FamiliesListProxy,		True, 	None, 	'List of ::Family:: objects.'],
	}

	def __repr__(self):
		return '<Foundry "%s">' % self.name.getText() or 'undefined'

	def getLicenseByKeyword(self, keyword):
		if not hasattr(self, '_licensesDict'):
			self._licensesDict = {}
			for license in self.licenses:
				self._licensesDict[license.keyword] = license

		if self._licensesDict.has_key(keyword):
			return self._licensesDict[keyword]


def Foundry_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent') and hasattr(self._parent._parent, '_parent'):
		return self._parent._parent._parent
Foundry.parent = property(lambda self: Foundry_Parent(self))

class FoundryProxy(Proxy):
	dataType = Foundry

class FoundryListProxy(ListProxy):
	dataType = FoundryProxy

####################################################################################################################################

#  Available Fonts

class BaseResponse(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_base_structure = {
	}

	def __repr__(self):
		return '<%s>' % self.__class__.__name__

	def customValidation(self):
		information, warnings, critical = [], [], []

		if self.type == CUSTOM and self.customMessage is None:
			critical.append('%s.type is "%s", but .customMessage is missing.' % (self, CUSTOM))

		return information, warnings, critical

def BaseResponse_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent'):
		return self._parent._parent
BaseResponse.parent = property(lambda self: BaseResponse_Parent(self))


class InstallableFontsResponseType(UnicodeDataType):
	def valid(self):
		if self.value in INSTALLABLEFONTSCOMMAND['responseTypes']:
			return True
		else:
			return 'Unknown response type: "%s". Possible: %s' % (self.value, INSTALLABLEFONTSCOMMAND['responseTypes'])

class InstallableFontsResponse(BaseResponse):
	u'''\
	This is the response expected to be returned when the API is invoked using the command parameter, such as `http://fontpublisher.com/api/?command=installableFonts`.

	The response needs to be specified at the ::Response.command:: attribute, and then the ::Response:: object needs to carry the specific response command at the attribute of same name, in this case ::Reponse.installableFonts::.

	```python
	api.response = Response()
	api.response.command = 'installableFonts'
	api.response.installableFonts = InstallableFontsResponse()
	```

	'''
	# 	key: 					[data type, required, default value, description]
	_structure = {

		# Root
		'type': 			[InstallableFontsResponseType,	True, 	None, 	'Type of response. This can be "success", "error", or "custom". In case of "custom", you may specify an additional message to be presented to the user under ::InstallableFontsResponse.customMessage::.'],
		'customMessage': 	[MultiLanguageTextProxy,				False, 	None, 	'Description of error in case of ::InstallableFontsResponse.type:: being "custom".'],
		'version': 			[FloatDataType,					True, 	INSTALLABLEFONTSCOMMAND['currentVersion'], 	'Version of "%s" response' % INSTALLABLEFONTSCOMMAND['keyword']],
		'licenseIdentifier':[UnicodeDataType, 				False, 	u'CC-BY-NC-ND-4.0', 	'Identifier of license under which the API endpoint publishes this particular response, as per [https://spdx.org/licenses/](). This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. This license can be different from the license at the root of the response. The idea is that different responses can be issued under different licenses, depending on their use scenario. If not specified, the root license is assumed.'],

		# Response-specific
		'designers':		[DesignersListProxy,			False, 	None, 	'List of ::Designer:: objects, referenced in the fonts or font families by the keyword. These are defined at the root of the response for space efficiency, as one designer can be involved in the design of several typefaces across several foundries.'],
		'foundries':		[FoundryListProxy,				True, 	None, 	'List of ::Foundry:: objects; foundries that this distributor supports. In most cases this will be only one, as many foundries are their own distributors.'],
	}

	def getDesignerByKeyword(self, keyword):
		if not hasattr(self, '_designersDict'):
			self._designersDict = {}
			for designer in self.designers:
				self._designersDict[designer.keyword] = designer

		if self._designersDict.has_key(keyword):
			return self._designersDict[keyword]

class InstallableFontsResponseProxy(Proxy):
	dataType = InstallableFontsResponse

####################################################################################################################################

#  InstallFonts

class InstallFontsResponseType(UnicodeDataType):
	def valid(self):
		if self.value in INSTALLFONTSCOMMAND['responseTypes']:
			return True
		else:
			return 'Unknown response type: "%s". Possible: %s' % (self.value, INSTALLFONTSCOMMAND['responseTypes'])

class InstallFontsResponse(BaseResponse):
	# 	key: 					[data type, required, default value, description]
	_structure = {

		# Root
		'type': 			[InstallableFontsResponseType,	True, 	None, 	'Success or error or else.'],
		'customMessage': 	[UnicodeDataType,				False, 	None, 	'Description of error in case of custom response type'],
		'version': 			[FloatDataType,					True, 	INSTALLFONTSCOMMAND['currentVersion'], 	'Version of "%s" response' % INSTALLFONTSCOMMAND['keyword']],
		'licenseIdentifier':[UnicodeDataType, 				False, 	u'CC-BY-NC-ND-4.0', 	'Identifier of license under which the API endpoint publishes this particular response, as per https://spdx.org/licenses/. This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. This license can be different from the license at the root of the response. The idea is that different responses can be issued under different licenses, depending on their use scenario. If not specified, the root license is assumed.'],

		# Response-specific
		}

class InstallFontsResponseProxy(Proxy):
	dataType = InstallFontsResponse

####################################################################################################################################

#  Uninstall Fonts

class UninstallFontsResponseType(UnicodeDataType):
	def valid(self):
		if self.value in UNINSTALLFONTSCOMMAND['responseTypes']:
			return True
		else:
			return 'Unknown response type: "%s". Possible: %s' % (self.value, UNINSTALLFONTSCOMMAND['responseTypes'])

class UninstallFontsResponse(BaseResponse):
	# 	key: 					[data type, required, default value, description]
	_structure = {

		# Root
		'type': 			[InstallableFontsResponseType,	True, 	None, 	'Success or error or else.'],
		'customMessage': 	[UnicodeDataType,				False, 	None, 	'Description of error in case of custom response type'],
		'version': 			[FloatDataType,					True, 	UNINSTALLFONTSCOMMAND['currentVersion'], 	'Version of "%s" response' % UNINSTALLFONTSCOMMAND['keyword']],
		'licenseIdentifier':[UnicodeDataType, 				False, 	u'CC-BY-NC-ND-4.0', 	'Identifier of license under which the API endpoint publishes this particular response, as per https://spdx.org/licenses/. This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. This license can be different from the license at the root of the response. The idea is that different responses can be issued under different licenses, depending on their use scenario. If not specified, the root license is assumed.'],

		# Response-specific
		}

class UninstallFontsResponseProxy(Proxy):
	dataType = UninstallFontsResponse


class Response(DictBasedObject):
	# 	key: 					[data type, required, default value, description]
	_structure = {
		'command': 							[SupportedAPICommandsDataType,	True, 	None, 	'Command code of the response. The specific response must then be present under an attribute of same name.'],
		INSTALLABLEFONTSCOMMAND['keyword']:	[InstallableFontsResponseProxy, 	False, 	None, 	''],
		INSTALLFONTSCOMMAND['keyword']:		[InstallFontsResponseProxy, 	False, 	None, 	''],
		UNINSTALLFONTSCOMMAND['keyword']:	[UninstallFontsResponseProxy, 	False, 	None, 	''],
	}

	def __repr__(self):
		return '<Response>'

	def getCommand(self):
		u'''\
Returns the specific response referenced in the .command attribute. This is a shortcut.

```python
print api.response.getCommand()

# will print:
<InstallableFontsResponse>

# which is the same as:
print api.response.get(api.response.command)

# will print:
<InstallableFontsResponse>
```
'''
#		exec("command = self.%s" % self.command)
		return self.get(self.command)

	def customValidation(self):

		information, warnings, critical = [], [], []

		if not self.getCommand():
			critical.append('%s.command is set, but we are missing that command at %s.%s' % (self, self, self.command))

		return information, warnings, critical


def Response_Parent(self):
	if hasattr(self, '_parent') and hasattr(self._parent, '_parent'):
		return self._parent._parent
Response.parent = property(lambda self: Response_Parent(self))


class ResponseProxy(Proxy):
	dataType = Response

class APIRoot(DictBasedObject):
	u'''\
This is the main class that sits at the root of all API responses. It contains some mandatory information about the API endpoint such as its name and admin email, the copyright license under which the API endpoint issues its data, and whether or not this endpoint can be publicized about.

Any API response is expected to carry this minimum information, even when invoked without a particular command.

In case the API endpoint has been invoked with a particular command, the response data is attached to the ::APIRoot.response:: attribute.


```python
api = APIRoot()
api.name.en = u'Font Publisher'
api.canonicalURL = 'https://fontpublisher.com/api/'
api.adminEmail = 'admin@fontpublisher.com'
api.supportedCommands = ['installableFonts', 'installFonts', 'uninstallFonts']
```

	'''


	# 	key: 					[data type, required, default value, description]
	_structure = {
		'canonicalURL': 		[WebURLDataType, 			True, 	None, 	'Official API endpoint URL, bare of ID keys and other parameters. Used for grouping of subscriptions. It is expected that this URL will not change.'],
		'adminEmail': 			[EmailDataType, 			True, 	None, 	'API endpoint Administrator, to contact for technical problems and such'],
		'licenseIdentifier':	[UnicodeDataType, 			True, 	u'CC-BY-NC-ND-4.0', 	'Identifier of license under which the API endpoint publishes its data, as per [https://spdx.org/licenses/](). This license will not be presented to the user. The software client needs to be aware of the license and proceed only if allowed, otherwise decline the usage of this API endpoint. Licenses of the individual responses can be fine-tuned in the respective responses.'],
		'supportedCommands': 	[SupportedAPICommandsListProxy, True, 	None, 	'List of commands this API endpoint supports: %s' % [x['keyword'] for x in COMMANDS]],
		'name': 				[MultiLanguageTextProxy, 			True, 	None, 	'Human-readable name of API endpoint'],
		'public': 				[BooleanDataType, 			True, 	False, 	'API endpoint is meant to be publicly visible and its existence may be publicized within the project'],
		'logo': 				[WebURLDataType, 			False, 	None, 	'URL of logo of API endpoint, for publication. Specifications to follow.'],
		'website': 				[WebURLDataType, 			False, 	None, 	'URL of human-visitable website of API endpoint, for publication'],
		'response': 			[ResponseProxy, 			False, 	None, 	'Response of the API call'],
	}

	def __cmp__(self, other):
		from deepdiff import DeepDiff
		return 	DeepDiff(self.dumpDict(), other.dumpDict(), ignore_order=True) == {}

	def __repr__(self):
		return '<API>'

	def validate(self):
		u'''\
		Return three lists with informations, warnings, and errors.

		An empty errors list is regarded as a successful validation, otherwise the validation is regarded as a failure.
		'''
		information, warnings, errors = self._validate()
		if self.canonicalURL and not self.canonicalURL.startswith('https://'):
			warnings.append('%s.canonicalURL is not using SSL (https://). Consider using SSL to protect your data.' % (self))
		return information, warnings, errors



