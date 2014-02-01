from os import listdir
from os.path import isfile, isdir, join, split
import errno, sys
import re, pprint

from xml.dom.minidom import parseString, Document
import ConfigParser

import omdb
import dicttoxml


def querymovie(*args, **kwargs):
	title = kwargs.get('title', '')
	year = kwargs.get('year', '')
	imdbid = kwargs.get('imdbid', None)

	omdb.set_default('tomatoes','true')
	if imdbid <> None:
		res = omdb.get(imdbid=imdbid)
	else:
		res = omdb.get(title=title,year=year)
	
	if len(res)>0:
		return res
	else:
		return searchmovie(title, year)

def searchmovie(title, year):
	aa = omdb.Client()
        movies = parseString(aa.request(s=title+'*', r='XML').content).getElementsByTagName('Movie')
        if movies.length>0:
                print 'I can not find the movie ['+title+'] in year ['+year+']. But do find the following(s):'
		i = 1
                for node in movies:
                        print str(i)+'.\t'+node.attributes['Title'].value+'\t in '+node.attributes['Year'].value+',\tIMDB:'+node.attributes['imdbID'].value
			i = i+1
		print 'else:\tquit'
		n = raw_input('\nPlease input the number before your favority movie:')
		try:
			n = int(n)
		except:
			n = 0
		if (n>0) and (n<i):
			res=querymovie(imdbid=movies[n-1].attributes['imdbID'].value)
			return res
        
        #print 'I can not find the movie ['+title+'] in year '+year+',or something likewise.'	
	return ''


def searchdir(movies_repo):
	moviedict = {}

	for d in listdir(movies_repo):
		md = join(movies_repo,d)
		if isdir(md):
			tt = re.search(r'(tt\d{7})',d)
			if tt:
				res = querymovie(imdbid=tt.group(1))
			else:
				my = re.search(r'^(.*?)\.\((19|20\d{2})\).*',d)
				if my:
					res = querymovie(title=my.group(1),year=my.group(2))
				else:
					m = re.search(r'^(.*?)\.[A-Z]+\.*',d)
					if m:
						res = querymovie(title=m.group(1))
					else:
						m = re.search(r'^(.*?)\.720p|1080p|dvdrip|bdrip|blueray|h264|xvid|ntsc|pal|hq',d,re.I)
						if m:
							res = querymovie(title=m.group(1))
						else:
							res = querymovie(title=d)

			if len(res)>0:
				#print 'Movie:\t'+res['title']+', '+res['year']+', '+res['imdb_id']+', '+res['genre']
				moviedict[md] = res
				#xmlfile = movies_repo+d+'/'+res['title']+'.('+res['year']+')'+'.'+res['imdb_id']+'.imdb.xml'
				xmlfile = movies_repo+d+'/'+d+'.imdb.xml'
				if not isfile(xmlfile):
					f = open(xmlfile,'w')
					f.write(parseString(re.sub('root','movie',dicttoxml.dicttoxml(res).encode('utf-8'))).toprettyxml())
					f.close()
				#xml = re.sub('root','movie',dicttoxml.dicttoxml(res).encode('utf-8'))
				#print parseString(xml).toprettyxml()
			else:
				#print 'I can not find the movie ['+d+'], or something likewise.'
				moviedict[md] = ''

	return moviedict

def matchgenre(imdb_genre,genres,genres_path):
# imdb_genre = genre from IMDB, case insensitive
# genres is a dict from Genre section of GM.cfg
# genres_path is the path to a folder where movies are linked to by genres

	imdb_genre = imdb_genre.lower()
	
	# match Genre section in config file
	if genres.get(imdb_genre):
		p = genres_path+genres.get(imdb_genre)+"/"
		if isdir(p):
			return genres_path+genres.get(imdb_genre)+"/"
	else:
	# match folders
		g = os.listdir(genres_path)
		r = [m.group(0) for l in g for m in [re.compile("^("+imdb_genre+").*",re.I).search(l)] if m]
		if len(r)==1:
			if os.path.isdir(genres_path+r[0]+'/'):
				return genres_path+r[0]+'/'
	# match None	
	return None

def main():

        config = ConfigParser.RawConfigParser()
        if not isfile('GM.cfg'):
                print 'I can not find config file GM.cfg in current directory. You can adopt example file GM.cfg.example and rename it to GM.cfg. Exiting ...'
                sys.exit(errno.ENOENT)

        config.read('GM.cfg')
        movies_repo = config.get('Path','movies_repo')
        genres_path = config.get('Path','genre_path')
        genres = dict(config.items('Genre'))
        #print genres

        #m = str(raw_input('Movie Name: '))
        #y = str(raw_input('Movie Year: '))
        #res = querymovie(title=m, year=y)
        movie_dict = searchdir(movies_repo)
        print 'we have processed the following '+str(len(movie_dict))+' movies.'
	pprint.pprint(movie_dict.keys())

if __name__ == '__main__':
	main()
