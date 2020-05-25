# -*- coding: utf-8 -*-

import os
import typeworld.protocol
from ynlib.files import WriteToFile, ReadFromFile
from ynlib.system import Execute

docstrings = []

docstrings.extend(typeworld.protocol.RootResponse().docu())
docstrings.extend(typeworld.protocol.EndpointResponse().docu())
docstrings.extend(typeworld.protocol.InstallableFontsResponse().docu())
docstrings.extend(typeworld.protocol.InstallFontsResponse().docu())
docstrings.extend(typeworld.protocol.UninstallFontsResponse().docu())

docstring = ReadFromFile(os.path.join(os.path.dirname(__file__), 'docu.md'))


handles = []
for key in [x[0] for x in docstrings]:
	if not key in handles:
		handles.append(key)

classTOC = ''
for handle in handles:
	classTOC += '- [%s](#user-content-class-%s)<br />\n' % (handle, handle.lower())
classTOC += '\n\n'

docstring = docstring.replace('__classTOC__', classTOC)

# Test code
testCode1Path = os.path.join(os.path.dirname(__file__), 'testcode1.py')
docstring = docstring.replace('__testcode1__', open(testCode1Path).read())
docstring = docstring.replace('__testcode1result__', Execute('python ' + testCode1Path).decode())

testCode2Path = os.path.join(os.path.dirname(__file__), 'testcode2.py')
docstring = docstring.replace('__testcode2__', open(testCode2Path).read())
docstring = docstring.replace('__testcode2result__', Execute('python ' + testCode2Path).decode())


for handle in handles:
	for className, string in docstrings:
		if handle == className:
			docstring += string
			docstring += '\n\n'
			break

if not 'TRAVIS' in os.environ:
	WriteToFile(os.path.join(os.path.dirname(__file__), 'README.md'), docstring)
