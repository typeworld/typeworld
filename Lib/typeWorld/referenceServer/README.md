

# Type.World Reference Server

This is a Python implementation of the simplest-possible server for fonts under the Type.World protocol.
Its data is stored in a simple folder structure under the `data` folder (can change in `preferences.plist`), with `.plist` files holding most of the meta data.

This server implementation provides a thorough example of the logic of how to output data, most importantly for the `installableFonts` command. 
The same logic may not apply for your own cause. For instance, this reference server announces access to free/non-restricted fonts (YanoneKaffeesatz-Thin) when no userID is supplied in the access URL. Otherwise, when a userID is given (which indicates access to commercial or otherwise restricted fonts), it will look up in the `preferences.plist` whether the non-restricted fonts shall be included, too. But this may not work for you. Instead, you could annouce non-restricted fonts under a modified URL that includes a parameter describing access to free fonts (e.g. &freefonts=true) and only then including the non-restricted fonts.

Therefore, this server *may* be used as is, but you may also want to adjust it to your needs. Then, it’ll just serve as a *reference*, as the title suggests.

Its web server is based on Flask, which you can install with pip:

`pip install flask`

Then you can run the server from the command line:

`python referenceServer.py`

It will print a couple of links like so:

```
####################################################################

  Type.World Reference Server
  General API information:                                   http://127.0.0.1:5000/
  Official Type.World App link for user1:                    http://127.0.0.1:5000/?userID=5hXmdNNvywkHe2asYLXqJR2T
  installableFonts for user1:                                http://127.0.0.1:5000/?command=installableFonts&userID=5hXmdNNvywkHe2asYLXqJR2T&&anonymousAppID=H625npqamfsy2cnZgNSJWpZm
  installableFonts, just free & non-restricted, no userID:   http://127.0.0.1:5000/?command=installableFonts&anonymousAppID=H625npqamfsy2cnZgNSJWpZm
  Install free font:                                         http://127.0.0.1:5000/?command=installFont&fontID=awesomefonts-YanoneKaffeesatz-Thin&fontVersion=1.0
  Install access-limited font:                               http://127.0.0.1:5000/?command=installFont&userID=5hXmdNNvywkHe2asYLXqJR2T&fontID=awesomefonts-YanoneKaffeesatz-Regular&fontVersion=1.0&anonymousAppID=H625npqamfsy2cnZgNSJWpZm
  Uninstall access-limited font:                             http://127.0.0.1:5000/?command=uninstallFont&userID=5hXmdNNvywkHe2asYLXqJR2T&fontID=awesomefonts-YanoneKaffeesatz-Regular&anonymousAppID=H625npqamfsy2cnZgNSJWpZm

####################################################################
```

Copy/paste these into your browser to see the JSON responses.
