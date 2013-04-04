"""
pygn.py

pygn (pronounced "pigeon") is a simple Python client for the Gracenote Music 
Web API, which can retrieve Artist, Album and Track metadata with the most 
common options.

You will need a Gracenote Client ID to use this module. Please contact 
developers@gracenote.com to get one.
"""

import xml.etree.ElementTree, urllib2, urllib, json

# Set DEBUG to True if you want this module to print out the query and response XML
DEBUG = False

class gnmetadata(dict):
	"""
	This class is a dictionary containing metadata fields that are available 
	for the queried item.
	"""
	def __init__(self):
		# Basic Metadata
		self['track_artist_name'] = ''
		self['album_artist_name'] = ''
		self['album_title'] = ''
		self['album_year'] = ''
		self['track_title'] = ''
		self['track_number'] = ''

		# Descriptors
		self['genre'] = {}
		self['artist_origin'] = {}
		self['artist_era'] = {}
		self['artist_type'] = {}
		self['mood'] = {}
		self['tempo'] = {}

		# Related Content
		self['album_art_url'] = ''
		self['artist_image_url'] = ''
		self['artist_bio_url'] = ''
		self['review_url'] = ''

		# Gracenote IDs
		self['album_gnid'] = ''
		self['track_gnid'] = ''		

def register(clientID):
	"""
	This function registers an application as a user of the Gracenote service
	
	It takes as a parameter a clientID string in the form of 
	"NNNNNNN-NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN" and returns a userID in a 
	similar	format.
	
	As the quota of number of users (installed applications or devices) is 
	typically much lower than the number of queries, best practices are for a
	given installed application to call this only once, store the UserID in 
	persistent storage (e.g. filesystem), and then use these IDs for all 
	subsequent calls to the service.
	"""
	
	# Create XML request
	query = _gnquery()
	query.addQuery('REGISTER')
	query.addQueryClient(clientID)
	
	queryXML = query.toString()
	
	# POST query
	response = urllib2.urlopen(_gnurl(clientID), queryXML)
	responseXML = response.read()
	
	# Parse response
	responseTree = xml.etree.ElementTree.fromstring(responseXML)
	
	responseElem = responseTree.find('RESPONSE')
	if responseElem.attrib['STATUS'] == 'OK':
		userElem = responseElem.find('USER')
		userID = userElem.text
	
	return userID
		
def searchTrack(clientID, userID, artistName, albumTitle, trackTitle):
	"""
	Queries the Gracenote service for a track
	"""
	
	# Create XML request
	query = _gnquery()
	
	query.addAuth(clientID, userID)
	query.addQuery('ALBUM_SEARCH')
	query.addQueryMode('SINGLE_BEST_COVER')
	query.addQueryTextField('ARTIST', artistName)
	query.addQueryTextField('ALBUM_TITLE', albumTitle)
	query.addQueryTextField('TRACK_TITLE', trackTitle)
	query.addQueryOption('SELECT_EXTENDED', 'COVER,REVIEW,ARTIST_BIOGRAPHY,ARTIST_IMAGE,ARTIST_OET,MOOD,TEMPO')
	query.addQueryOption('SELECT_DETAIL', 'GENRE:3LEVEL,MOOD:2LEVEL,TEMPO:3LEVEL,ARTIST_ORIGIN:4LEVEL,ARTIST_ERA:2LEVEL,ARTIST_TYPE:2LEVEL')
	
	queryXML = query.toString()
	
	if DEBUG:
		print '------------'
		print 'QUERY XML'
		print '------------'
		print queryXML
	
	# POST query
	response = urllib2.urlopen(_gnurl(clientID), queryXML)
	responseXML = response.read()
	
	if DEBUG:
		print '------------'
		print 'RESPONSE XML'
		print '------------'
		print responseXML

	# Create GNTrackMetadata object
	metadata = gnmetadata()
	
	# Parse response
	responseTree = xml.etree.ElementTree.fromstring(responseXML)
	responseElem = responseTree.find('RESPONSE')
	if responseElem.attrib['STATUS'] == 'OK':
		# Find Album element
		albumElem = responseElem.find('ALBUM')

		# Parse album metadata
		metadata['album_gnid'] = _getElemText(albumElem, 'GN_ID')
		metadata['album_artist_name'] = _getElemText(albumElem, 'ARTIST')
		metadata['album_title'] = _getElemText(albumElem, 'TITLE')
		metadata['album_year'] = _getElemText(albumElem, 'DATE')
		metadata['album_art_url'] = _getElemText(albumElem, 'URL', 'TYPE', 'COVERART')
		metadata['genre'] = _getMultiElemText(albumElem, 'GENRE', 'ORD', 'ID')
		metadata['artist_image_url'] = _getElemText(albumElem, 'URL', 'TYPE', 'ARTIST_IMAGE')
		metadata['artist_bio_url'] = _getElemText(albumElem, 'URL', 'TYPE', 'ARTIST_BIOGRAPHY')
		metadata['review_url'] = _getElemText(albumElem, 'URL', 'TYPE', 'REVIEW')
		
		# Look for OET
		artistOriginElem = albumElem.find('ARTIST_ORIGIN')
		if artistOriginElem is not None:
			metadata['artist_origin'] = _getMultiElemText(albumElem, 'ARTIST_ORIGIN', 'ORD', 'ID')
			metadata['artist_era'] = _getMultiElemText(albumElem, 'ARTIST_ERA', 'ORD', 'ID')
			metadata['artist_type'] = _getMultiElemText(albumElem, 'ARTIST_TYPE', 'ORD', 'ID')
		else:
			# Try to get OET again by fetching album by GNID
			metadata['artist_origin'], metadata['artist_era'], metadata['artist_type'] = _getOET(clientID, userID, metadata['album_gnid'])
			
		# Parse track metadata
		matchedTrackElem = albumElem.find('MATCHED_TRACK_NUM')
		if matchedTrackElem is not None:
			trackElem = albumElem.find('TRACK')
			
			metadata['track_number'] = _getElemText(trackElem, 'TRACK_NUM')
			metadata['track_gnid'] = _getElemText(trackElem, 'GN_ID')
			metadata['track_title'] = _getElemText(trackElem, 'TITLE')
			metadata['track_artist_name'] = _getElemText(trackElem, 'ARTIST')

			metadata['mood'] = _getMultiElemText(trackElem, 'MOOD', 'ORD', 'ID')
			metadata['tempo'] = _getMultiElemText(trackElem, 'TEMPO', 'ORD', 'ID')
			
			# If track-level GOET exists, overwrite metadata from album			
			if trackElem.find('GENRE') is not None:
				metadata['genre']	= _getMultiElemText(trackElem, 'GENRE', 'ORD', 'ID')
			if trackElem.find('ARTIST_ORIGIN') is not None:
				metadata['artist_origin'] = _getMultiElemText(trackElem, 'ARTIST_ORIGIN', 'ORD', 'ID')
			if trackElem.find('ARTIST_ERA') is not None:
				metadata['artist_era'] = _getMultiElemText(trackElem, 'ARTIST_ERA', 'ORD', 'ID')
			if trackElem.find('ARTIST_TYPE') is not None:
				metadata['artist_type'] = _getMultiElemText(trackElem, 'ARTIST_TYPE', 'ORD', 'ID')
				
		
		return metadata

def searchArtist(clientID, userID, artistName):
	"""
	Queries the Gracenote service for an artist. If found, this function will
	return a gnmetadata object containing metadata for the most popular album
	by this artist.
	"""
	return searchTrack(clientID, userID, artistName, '', '')

def searchAlbum(clientID, userID, artistName, albumTitle):
	"""
	Queries the Gracenote service for an album.
	"""
	return searchTrack(clientID, userID, artistName, albumTitle, '')

def _gnurl(clientID):
	"""
	Helper function to form URL to Gracenote service
	"""
	clientIDprefix = clientID.split('-')[0]
	return 'https://c' + clientIDprefix + '.web.cddbp.net/webapi/xml/1.0/'
	
def _getOET(clientID, userID, GNID):
	"""
	Helper function to retrieve Origin, Era, and Artist Type by direct album 
	fetch
	"""
	# Create XML request
	query = _gnquery()
	
	query.addAuth(clientID, userID)
	query.addQuery('ALBUM_FETCH')
	query.addQueryGNID(GNID)
	query.addQueryOption('SELECT_EXTENDED', 'ARTIST_OET')
	query.addQueryOption('SELECT_DETAIL', 'ARTIST_ORIGIN:4LEVEL,ARTIST_ERA:2LEVEL,ARTIST_TYPE:2LEVEL')
	
	queryXML = query.toString()
	
	if DEBUG:
		print '------------'
		print 'QUERY XML (from _getOET())'
		print '------------'
		print queryXML
	
	# POST query
	response = urllib2.urlopen(_gnurl(clientID), queryXML)
	albumXML = response.read()
	
	if DEBUG:
		print '------------'
		print 'RESPONSE XML (from _getOET())'
		print '------------'
		print albumXML
	
	# Parse XML
	responseTree = xml.etree.ElementTree.fromstring(albumXML)
	responseElem = responseTree.find('RESPONSE')
	if responseElem.attrib['STATUS'] == 'OK':
		albumElem = responseElem.find('ALBUM')
		artistOrigin = _getMultiElemText(albumElem, 'ARTIST_ORIGIN', 'ORD', 'ID')
		artistEra = _getMultiElemText(albumElem, 'ARTIST_ERA', 'ORD', 'ID')
		artistType = _getMultiElemText(albumElem, 'ARTIST_TYPE', 'ORD', 'ID')
	return artistOrigin, artistEra, artistType
	
class _gnquery:
	"""
	A utility class for creating and configuring an XML query for POST'ing to
	the Gracenote service
	"""

	def __init__(self):
		self.root = xml.etree.ElementTree.Element('QUERIES')
		
	def addAuth(self, clientID, userID):
		auth = xml.etree.ElementTree.SubElement(self.root, 'AUTH')
		client = xml.etree.ElementTree.SubElement(auth, 'CLIENT')
		user = xml.etree.ElementTree.SubElement(auth, 'USER')
	
		client.text = clientID
		user.text = userID
	
	def addQuery(self, cmd):
		query = xml.etree.ElementTree.SubElement(self.root, 'QUERY')
		query.attrib['CMD'] = cmd
	
	def addQueryMode(self, modeStr):
		query = self.root.find('QUERY')
		mode = xml.etree.ElementTree.SubElement(query, 'MODE')
		mode.text = modeStr

	def addQueryTextField(self, fieldName, value):
		query = self.root.find('QUERY')
		text = xml.etree.ElementTree.SubElement(query, 'TEXT')
		text.attrib['TYPE'] = fieldName
		text.text = value
	
	def addQueryOption(self, parameterName, value):
		query = self.root.find('QUERY')
		option = xml.etree.ElementTree.SubElement(query, 'OPTION')
		parameter = xml.etree.ElementTree.SubElement(option, 'PARAMETER')
		parameter.text = parameterName
		valueElem = xml.etree.ElementTree.SubElement(option, 'VALUE')
		valueElem.text = value
	
	def addQueryGNID(self, GNID):
		query = self.root.find('QUERY')
		GNIDElem = xml.etree.ElementTree.SubElement(query, 'GN_ID')
		GNIDElem.text = GNID
		
	def addQueryClient(self, clientID):
		query = self.root.find('QUERY')
		client = xml.etree.ElementTree.SubElement(query, 'CLIENT')
		client.text = clientID
		
	def toString(self):
		return xml.etree.ElementTree.tostring(self.root)

def _getElemText(parentElem, elemName, elemAttribName=None, elemAttribValue=None):
	"""
	XML parsing helper function to find child element with a specific name, 
	and return the text value
	"""
	elems = parentElem.findall(elemName)
	for elem in elems:
		if elemAttribName is not None and elemAttribValue is not None:
			if elem.attrib[elemAttribName] == elemAttribValue:
				return urllib.unquote(elem.text)
			else:
				continue
		else: # Just return the first one
			return urllib.unquote(elem.text)
	return ''

def _getElemAttrib(parentElem, elemName, elemAttribName):
	"""
	XML parsing helper function to find child element with a specific name, 
	and return the value of a specified attribute
	"""
	elem = parentElem.find(elemName)
	if elem is not None:
		return elem.attrib[elemAttribName]

def _getMultiElemText(parentElem, elemName, topKey, bottomKey):
	"""
	XML parsing helper function to return a 2-level dict of multiple elements
	by a specified name, using topKey as the first key, and bottomKey as the second key
	"""
	elems = parentElem.findall(elemName)
	result = {} # 2-level dictionary of items, keyed by topKey and then bottomKey
	if elems is not None:
		for elem in elems:
			if topKey in elem.attrib:
				result[elem.attrib[topKey]] = {bottomKey:elem.attrib[bottomKey], 'TEXT':elem.text}
			else:
				result['0'] = {bottomKey:elem.attrib[bottomKey], 'TEXT':elem.text}
	return result
