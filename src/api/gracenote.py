#!/usr/bin/env python
#
# Copyright 2013 Leaf Media Group.
# @author: samiq
#
import os
import json
import logging
from api import handlers
from pygn import pygn

logging.getLogger().setLevel(logging.DEBUG)

# replace client id with yours, if you don't have one
# you can get yours at https://developer.gracenote.com
CLIENT_ID = '*******-************************'

# every app has to register and get the user id.
# to get yours uncomment the code in the Registration class
# below and run once, then save the ID in this variable.
USER_ID = ''

class Home(handlers.ApiBasic):
	# Handles the basic get and post of gracenote objects
	
	def get(self):
		self.success()

class Registration(handlers.ApiBasic):
	
	def get(self):
		# un comment to get the USER_ID, only run once and save 
		# the response back to the var on the top
		# ============================================
		# user_id = pygn.register(CLIENT_ID)
		# self.response.write(user_id)
		# ============================================
		self.response("Already registered!")

class Track(handlers.ApiBasic):

	def get(self):
		
		artist = self.request.get('artist') or ''
		album = self.request.get('album') or ''
		track = self.request.get('track') or ''
		meta = pygn.searchTrack(CLIENT_ID, USER_ID, artist, album, track)
		self.success(meta)

class Album(handlers.ApiBasic):

	def get(self):
		
		artist = self.request.get('artist') or ''
		album = self.request.get('album') or ''
		meta = pygn.searchAlbum(CLIENT_ID, USER_ID, artist, album)
		self.success(meta)

class Artist(handlers.ApiBasic):

	def get(self):
		
		artist = self.request.get('artist') or ''		
		meta = pygn.searchArtist(CLIENT_ID, USER_ID, artist)
		self.success(meta)
