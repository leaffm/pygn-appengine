#!/usr/bin/env python
#
# Copyright 2013 Leaf Media Group.
# @author: samiq
#
import os
import logging
import webapp2
from webapp2_extras import jinja2
import datetime

logging.getLogger().setLevel(logging.DEBUG)

class Home(webapp2.RequestHandler):
	# Default handler for the app

	def get(self):
		# Default handler for get requests unhandled
		self.redirect('/')

class BasicHandler(webapp2.RequestHandler):
	def get(self):
		# Default handler for get requests
		self.not_found()
	
	def post(self):
		# Default handler for post requests
		self.not_found()

	def not_found(self):
		# Sends an 404 error back to the browser.
		self.response.set_status(404)
		self.render_response("404.html")
	
class NotFoundHandler(BasicHandler):
	def get(self):
		self.not_found()