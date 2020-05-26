[![Build Status](https://travis-ci.org/typeWorld/typeWorld.svg?branch=master)](https://travis-ci.org/typeWorld/typeWorld)
[![codecov](https://codecov.io/gh/typeWorld/typeWorld/branch/master/graph/badge.svg)](https://codecov.io/gh/typeWorld/typeWorld)


# Installation

Install via PyPi: `pip install typeworld`

# Tests

To successfully run the tests in `test.py`, you need an authorization key to be obtained from Yanone, and put it into your OS’s keychain like so:

```python
import keyring

key = '**replace**'
keyring.set_password('https://typeworld.appspot.com/api', 'revokeAppInstance', key)
keyring.set_password('http://127.0.0.1:8080/api', 'revokeAppInstance', key)
```

# API

For the documentation of the official API in detail, jump [→ here](Lib/typeworld/api).


# Package

To create a new package, install twine via `pip install twine`, then `cd` to `Lib/` and then:

* `python setup.py sdist`
* `twine upload dist/*`
