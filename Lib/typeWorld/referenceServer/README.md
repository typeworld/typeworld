

# Type.World Reference Server

This is a Python implementation of the simplest-possible server for fonts under the Type.World protocol.
Its data is stored in a simple folder structure under the `data` folder, with `.plist` files holding most of the meta data.

Its web server is based on Flask, which you can install with pip:

`pip install flask`

Then you can run the server from the command line:

`python referenceServer.py`

It will print a couple of links like so:

```
####################################################################

  Type.World Reference Server
  General API information:                    http://127.0.0.1:5000/
  Official Type.World App link for user1:     http://127.0.0.1:5000/?userID=5hXmdNNvywkHe2asYLXqJR2T
  installableFonts command for user1:         http://127.0.0.1:5000/?command=installableFonts&userID=5hXmdNNvywkHe2asYLXqJR2T&anonymousAppID=H625npqamfsy2cnZgNSJWpZm

####################################################################
```

Copy/paste these into your browser to see the JSON responses.

Currently still missing is installation and uninstallation of fonts. Coming up, stay tuned.