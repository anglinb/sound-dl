import os
import requests
import json
import string
import eyed3
import eyed3.id3

#Constants
TEMP_DIR = "tmp"
COMPLETE_DIR = "complete"
VALID_CHARS = "-_.() %s%s" % (string.ascii_letters, string.digits)
CUR_DIR = os.path.abspath(os.curdir)
REL_DIR = os.curdir

#Models
class urlSong():
	def __init__(self, url, title):
		self.url = url
		self.title = title

	def add_file_path(self, path):
		self.path = path

	def add_relative_path(self, relpath):
		self.relpath = relpath


class metaData():
	def __init__(self, artist, songtitle):
		self.artist = artist
		self.songtitle = songtitle

	# def __init__(self, songtitle):
	# 	self.songtitle = songtitle

class Tagger():
	def add_tags(self, metaData, urlSong):
		# print urlSong.path
		song = eyed3.load(urlSong.path)
		song.tag = eyed3.id3.Tag()
		song.tag.file_info = eyed3.id3.FileInfo(urlSong.path)
		if metaData.artist != '':
			# print song.tag.file_info
			song.tag.artist = unicode(metaData.artist)
		song.tag.title = unicode(metaData.songtitle)
		song.tag.save()
		return True

#Container
class Download():
	count = 0

	def __init__(self):
		self.setup()
		self.tagger = Tagger()

	def setup(self):
		if not os.path.isdir(os.path.join(CUR_DIR, TEMP_DIR)):
			os.makedirs(os.path.join(CUR_DIR, TEMP_DIR))
		if not os.path.isdir(os.path.join(CUR_DIR, COMPLETE_DIR)):
			os.makedirs(os.path.join(CUR_DIR, COMPLETE_DIR))

	def get_url(self, url):
		#url = 'https://soundcloud.com/candylanddjs/cash-cash-overtime-candyland'
		r = requests.post('http://sounddrain.com/api.php',{'url':url})
		j = json.loads(r.content)
		if 'url' in j:
			return urlSong(url=j['url'],title=j['title'])
		else:
			return False

	def clean_file_name(self, title):
		return ''.join(c for c in title if c in VALID_CHARS)

	def guess_pieces(self, title):
		dash = title.count('-')
		if dash == 1:
			pieces = title.split('-')
			artist = pieces[0]
			songtitle = pieces[1]
			meta = metaData(artist=artist,songtitle=songtitle)
			return meta
		else:
			print "Can't guess ["+title+"]; using entire title."
			meta = metaData(songtitle=title)
			return meta

	def move_to_complete(self, urlSong):
		newfilename = os.path.join(CUR_DIR, COMPLETE_DIR, self.clean_file_name(urlSong.title))
		if not os.path.isfile(newfilename+'.mp3'):
			os.rename(urlSong.path, newfilename+'.mp3')
			urlSong.add_file_path(newfilename+'.mp3')
			return urlSong
		else:
			complete = False
			for x in xrange(1,10):
				if not os.path.isfile(newfilename+str(x)+'.mp3'):
					complete = urlSong
					os.rename(urlSong.path, newfilename+str(x)+'.mp3')
					urlSong.add_file_path(newfilename+str(x)+'.mp3')
					break
			if complete:
				return urlSong
			else:
				print "Could not rename image"
				return False


	def download_song(self, urlSong):
		self.count = self.count + 1
		request = requests.get(urlSong.url, stream=True)
		filepath = os.path.join(CUR_DIR, TEMP_DIR,'tmp'+str(self.count)+'.mp3')
		with open(filepath, "wb") as code:
			for chunk in request.iter_content(1024):
				if not chunk:
					break
				code.write(chunk)
		urlSong.add_file_path(filepath)
		return urlSong

	def dl(self, url):
		song = self.get_url(url)
		if song:
			print "Downloading: "+song.title
			song = self.download_song(song)
			meta = self.guess_pieces(song.title)
			self.tagger.add_tags(metaData=meta,urlSong=song)
			song = self.move_to_complete(song)
		else:
			print "Song could not be found"

d = Download()
d.dl('https://soundcloud.com/candylanddjs/cash-cash-overtime-candyland')
