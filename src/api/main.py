#!/usr/bin/env python
#
# Copyright 2013 Leaf Media Group.
# @author: samiq
#
import webapp2
import base_handlers
from api import gracenote

app = webapp2.WSGIApplication([
			('/api/?$',	base_handlers.Home),
			#-----------------------------------------------------
			# gracenote services
			#-----------------------------------------------------
			('/api/gracenote/?$',		gracenote.Home),
			('/api/gracenote/register',	gracenote.Registration),
			('/api/gracenote/track',	gracenote.Track),
			('/api/gracenote/artist',	gracenote.Artist),
			('/api/gracenote/album',	gracenote.Album)
			],
		debug=True)