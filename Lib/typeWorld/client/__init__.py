# -*- coding: utf-8 -*-


import os, sys, json

from typeWorld.base import *
import typeWorld.api




class Repository(object):
	u"""\
	Represents a font repository under a specific API endpoint.
	"""

class APIEndPoint(object):
	u"""\
	Represents an API endpoint, identified and grouped by the canonical URL attribute of the API responses. This API endpoint class can then hold several repositories.
	"""


class APIClient(object):
	u"""\
	Main Type.World client app object. Use it to load repositories and install/uninstall fonts.
	"""

	def __init__(self):

		self.endpoints = []
		