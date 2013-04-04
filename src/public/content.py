#!/usr/bin/env python
#
# Copyright 2013 Leaf Media Group.
# @author: samiq
#
import os
import webapp2
import base_handlers

class Home(base_handlers.BasicHandler):

	def get(self):
		self.response.write("Have you tried <a href='http://playleaf.co'>Leaf</a>? ... Leaf is music made social!")
