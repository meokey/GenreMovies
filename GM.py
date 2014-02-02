from os import listdir
from os.path import isfile, isdir, join, split
import errno, sys
import re, pprint

from xml.dom.minidom import parseString, Document
import ConfigParser

import omdb
import dicttoxml

class ppprint(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)


def querymovie(*args, **kwargs):
	title = kwargs.get('title', '')
	year = kwargs.get('year', '')
	imdbid = kwargs.get('imdbid', None)

	print '###querymovie###',title, year, imdbid    #comments
	if title:
		title = title.replace('.',' ')

	omdb.set_default('tomatoes','true')
	omdb.set_default('plot','full')
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
		print '\n0.\tinput a proper movie name:\nelse:\tquit'
		n = raw_input('\nPlease input the number before your favority movie:')
		try:
			n = int(n)
		except:
			n = -1
		if n==0:
			t = raw_input('\nPlease input IMDB ID of the movie if you know:')
			if t:
				return querymovie(imdbid=t)
			else:
				m = raw_input('\nPlease input the movie name:')
				n = raw_input('\nPlease input the year when the movie was released:')
				return searchmovie(m,n)
		elif (n>0) and (n<i):
			return querymovie(imdbid=movies[n-1].attributes['imdbID'].value)
        
        #print 'I can not find the movie ['+title+'] in year '+year+',or something likewise.'	
	return ''



def moviename(d):
	imdbid = None
	title = d
	year = ''
	
	aaa = '720p|1080p|dvdrip|dbd-rip|bdrip|brrip|bluray|h264|x264|xvid|ntsc|pal|hq|dts|hdtv|aac'
	
	print '###moviename###	'+d		#comment	
	tt = re.search(r'(tt\d{7})',d)
        if tt:
                imdbid = tt.group(1)
        else:
                if str.isalnum(d[0]):
			my = re.search(r'^(.*?)\.\((19|20\d{2})[0-9,-]*\).*',d)
                	if my:
                        	title = my.group(1)
				year = my.group(2)
                	else:
				m = re.search(r'^(.*?)\.[A-Z]+\.*',d)
                        	if m:
                                	title = m.group(1)
                        	else:
                                	m = re.search(r'^(.*?)\.'+aaa,d,re.I)
                                	if m:
                                        	title = m.group(1)
		else:
			my = re.search(ur'^.*\.\(((19|20)\d\d)[0-9,-]*\)\.(.*?)'+aaa,d,re.I)
			if my:
				title = my.group(1)
				year = my.group(3)
			else:
				my = re.search(ur'^.*\.\(((19|20)\d\d)[0-9,-]*\)\.(.*)$',d,re.I)
				if my:
					title = my.group(3)
					year = my.group(1)

	return (title, year, imdbid)

def searchdir(movies_repo):
	y = {}
	n = {}

	for d in listdir(movies_repo):
		md = join(movies_repo,d)
		if isdir(md):
			#print d
			title, year, imdbid = moviename(d)					
			res = querymovie(title=title, year=year,imdbid=imdbid)

			if len(res)>0:
				print u'Movie:\t'+res['title'].decode("utf-8")+u', '+res['year'].decode("utf-8")+u', '+res['imdb_id'].decode("utf-8")+u', '+res['genre'].decode("utf-8")
				y[md.decode("utf-8")] = res
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
				n[md.decode("utf-8")] = ''

	return (y,n)

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
        movies_repo = config.get('Path','movies_repo').encode('UTF8')
        genres_path = config.get('Path','genre_path').encode('UTF8')
        genres = dict(config.items('Genre'))
        #print genres

        #m = str(raw_input('Movie Name: '))
        #y = str(raw_input('Movie Year: '))
        #res = querymovie(title=m, year=y)
        y,n = searchdir(movies_repo)
        print 'we have processed the following '+str(len(y))+' movies.'
	ppprint().pprint(y.keys())
	print '\nwe find no IMDB info for the following '+str(len(n))+' movies,'
	ppprint().pprint(n.keys())

if __name__ == '__main__':
	main()
