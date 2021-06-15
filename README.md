[![Build Status](https://travis-ci.com/typeworld/typeworld.svg?branch=main)](https://travis-ci.org/typeWorld/typeWorld)
[![PyPI version](https://badge.fury.io/py/typeworld.svg)](https://badge.fury.io/py/typeworld)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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
