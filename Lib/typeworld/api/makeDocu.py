# -*- coding: utf-8 -*-

import os
import sys

# Use local code for local testing, and rely on system-installed module for CI-testing
CI = os.getenv("CI", "false").lower() != "false"
if not CI:
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if path not in sys.path:
        sys.path.insert(0, path)

import typeworld.api  # noqa: E402


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
docstring = docstring.replace("__version__", typeworld.api.VERSION)

# Test code
testCode1Path = os.path.join(os.path.dirname(__file__), "testcode1.py")
docstring = docstring.replace("__testcode1__", open(testCode1Path).read())
docstring = docstring.replace(
    "__testcode1result__", Execute("python3 " + testCode1Path).decode()
)

testCode2Path = os.path.join(os.path.dirname(__file__), "testcode2.py")
docstring = docstring.replace("__testcode2__", open(testCode2Path).read())
docstring = docstring.replace(
    "__testcode2result__", Execute("python3 " + testCode2Path).decode()
)

# Breaking changes
changesList = [f"* `{x}`" for x in typeworld.api.BREAKINGVERSIONS]
docstring = docstring.replace("__breakingAppVersions__", "\n".join(changesList))


for handle in handles:
    for className, string in docstrings:
        if handle == className:
            docstring += string
            docstring += "\n\n"
            break
docstring = docstring.strip() + "\n"

if "TRAVIS" not in os.environ:
    f = open(os.path.join(os.path.dirname(__file__), "README.md"), "w")
    f.write(docstring)
    f.close()
