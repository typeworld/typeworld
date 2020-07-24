# -*- coding: utf-8 -*-

import os
import typeworld.api


def Execute(command):
    """\
    Execute system command, return output.
    """

    import sys
    import os
    import platform

    if sys.version.startswith("2.3") or platform.system() == "Windows":

        p = os.popen(command, "r")
        response = p.read()
        p.close()
        return response

    else:

        import subprocess

        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, shell=True, close_fds=True
        )
        os.waitpid(process.pid, 0)
        response = process.stdout.read().strip()
        process.stdout.close()
        return response


docstrings = []

docstrings.extend(typeworld.api.RootResponse().docu())
docstrings.extend(typeworld.api.EndpointResponse().docu())
docstrings.extend(typeworld.api.InstallableFontsResponse().docu())
docstrings.extend(typeworld.api.InstallFontsResponse().docu())
docstrings.extend(typeworld.api.UninstallFontsResponse().docu())

docstring = open(os.path.join(os.path.dirname(__file__), "docu.md"), "r").read()


handles = []
for key in [x[0] for x in docstrings]:
    if key not in handles:
        handles.append(key)

classTOC = ""
for handle in handles:
    classTOC += "- [%s](#user-content-class-%s)<br />\n" % (handle, handle.lower())
classTOC += "\n\n"

docstring = docstring.replace("__classTOC__", classTOC)

# Test code
testCode1Path = os.path.join(os.path.dirname(__file__), "testcode1.py")
docstring = docstring.replace("__testcode1__", open(testCode1Path).read())
docstring = docstring.replace(
    "__testcode1result__", Execute("python " + testCode1Path).decode()
)

testCode2Path = os.path.join(os.path.dirname(__file__), "testcode2.py")
docstring = docstring.replace("__testcode2__", open(testCode2Path).read())
docstring = docstring.replace(
    "__testcode2result__", Execute("python " + testCode2Path).decode()
)


for handle in handles:
    for className, string in docstrings:
        if handle == className:
            docstring += string
            docstring += "\n\n"
            break

if "TRAVIS" not in os.environ:
    f = open(os.path.join(os.path.dirname(__file__), "README.md"), "w")
    f.write(docstring)
    f.close()
