# Type.World


Type.World is in the process of becoming a one-click font installer. 

This repository consists of these main parts:

## 1. API

This is a completely water-proof Python implementation of the API protocol. It will output JSON responses and you should use it because it performs all sorts of data type and logic checks.

See [typeWorld.api](Lib/typeWorld/api).

## 2. Reference Server

This is a Python implementation of the simplest-possible server for fonts under the Type.World protocol. After installing Flask (as a Pyton web server), you can run it off the shelf on your computer to play with the protocol.

See [referenceServer](Lib/typeWorld/referenceServer).