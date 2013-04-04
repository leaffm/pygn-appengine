#!/usr/bin/env python
#
# Copyright 2013 Leaf Media Group.
# @author: samiq
#
import os
import json
import logging
import base_handlers
from google.appengine.ext import db
import models

logging.getLogger().setLevel(logging.DEBUG)

class ApiBasic(base_handlers.BasicHandler):
	# Base Class for API Handlers

	# Sends a response back with a bad parameter code and message.
	def bad_params(self):		
		self.response.set_status(406)
		self.response.headers['Content-Type'] = 'text/json'
		self.response.out.write('{"error":"Please check all provided data and try again."}')
		
	# Sends a success result back with a json object representing the response data.
	def success(self,obj=None):		
		rs = {}
		rs['result'] = 'ok'
		
		if obj:
			rs['data'] = obj
	
		self.response.set_status(200)
		self.response.headers['Content-Type'] = 'text/json'
		self.response.out.write(json.dumps(rs))
