# Type.World


Type.World is in the process of becoming a one-click font installer. 

This repository consists of these main parts:

## 1. API

This is a completely water-proof Python implementation of the API protocol. It will output JSON responses and you should use it because it performs all sorts of data type and logic checks.

See [typeWorld.api](Lib/typeWorld/api)

## 2. Reference Server

This is a Python implementation of the simplest-possible server for fonts under the Type.World protocol. After installing Flask (as a Pyton web server), you can run it off the shelf on your computer to play with the protocol.

See [typeWorld.referenceServer](Lib/typeWorld/referenceServer)

## 3. Client

This is a pure Python client implementation for installing fonts on your computer. It will be used as a basis for the Type.World GUI App, but you may also use it in your own app.

See [typeWorld.client](Lib/typeWorld/client)
