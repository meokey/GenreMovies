from os import listdir, symlink, link
from os.path import isfile, isdir, islink, join, split, getsize
from glob import glob
import errno, sys, getpass, codecs
import re, pprint, json, ast

from xml.dom.minidom import parseString, Document
from optparse import OptionParser,OptionGroup
import ConfigParser

import omdb
import dicttoxml

class ppprint(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)

def unic(s):
	if type(s) == str:
		v = unicode(s, "utf-8", errors="ignore")
	else:
		v = unicode(s)
	return v

def querymovie(*args, **kwargs):
	title = kwargs.get('title', '')
	year = kwargs.get('year', '')
	imdbid = kwargs.get('imdbid', None)

	#print '###querymovie###',title, year, imdbid    #comments
	if title:
		title = title.replace('.',' ')

	omdb.set_default('tomatoes','true')
	omdb.set_default('plot','full')
	if imdbid <> None:
		res = omdb.get(imdbid=imdbid)
	else:
		res = omdb.get(title=title,year=year)
	#print res	# comment
	if len(res)>0:
		return res
	elif title:
		return searchmovie(title, year)
	else:
		return ''

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
	
	aaa = '720p|1080p|dvdrip|dbd-rip|bdrip|brrip|bluray|blu-ray|h264|x264|xvid|ntsc|pal|hq|dts|hdtv|aac|duology|trilogy|quadrilogy|pentalogy|hexology|heptalogy|octology|anthology|extended|pdvd'
	
	#print '###moviename###	'+d		#comment	
	tt = re.search(r'(tt\d{7})',d)
        if tt:
                imdbid = tt.group(1)
        else:
                if str.isalnum(d[0]):
			my = re.search(r'^(.*?)\.\(((19|20)\d\d)[0-9,-]*\).*',d)
                	if my:
                        	title = my.group(1)
				year = my.group(2)
                	else:
				m = re.search(r'^(.*?)\.[A-Z]+\.*',d)
                        	if m:
                                	title = m.group(1)
                        	else:
                                	m = re.search(r'^(.*?)\.?('+aaa+')',d,re.I)
                                	if m:
                                        	title = m.group(1)
		else:
			my = re.search(ur'^.*\.\(((19|20)\d\d)[0-9,-]*\)\.(.*?)\.?('+aaa+')',d,re.I)
			if my:
				title = my.group(3)
				year = my.group(1)
			else:
				my = re.search(ur'^.*\.\(((19|20)\d\d)[0-9,-]*\)\.(.*)$',d,re.I)
				if my:
					title = my.group(3)
					year = my.group(1)

	return (title, year, imdbid)

def searchdir(movies_repo,opt_display,ignore):
	y = {}
	n = {}

	for d in listdir(movies_repo):
		if d in ignore:
			print'\tIgnoring movie ['+d+']...'
			continue

		md = join(movies_repo,d)
		if isdir(md):
			#print '\t####searchdir: '+md	#comment
			if isfile(md+'/imdb.xml'):	# existance of imdb.xml indicates that links have been created, skip
				print '\tSkipping movie ['+d+']...'
				continue
			#print "\tI'm processing movie ["+d+'].'  # comment

			# check omdbapi.com to gather imdb info for the movie
			title, year, imdbid = moviename(d)					
			res = querymovie(title=title, year=year, imdbid=imdbid)

			if len(res)>2:
				#print u'\tMovie:\t'+res['title'].decode("utf-8")+u', '+res['year'].decode("utf-8")+u', '+res['imdb_id'].decode("utf-8")+u', '+res['genre'].decode("utf-8")	# comment
				
				xmlfile = md+'/'+res['title'].replace('/',' ').replace('*',' ').replace('?',' ').encode("utf-8")+'.('+res['year'].encode("utf-8")+').'+res['imdb_id'].encode("utf-8")+'.imdb.xml'
				#print 'xmlfile = ['+xmlfile+']'		# comment
				if not opt_display:		# (not isfile(xmlfile)) and
					w = True	#False
					try:
						s = getsize(xmlfile)
						if s==0:
							w = True
					except (OSError, IOError):
						w = True
					if w==True:
						f = codecs.open(xmlfile,'w', encoding="utf-8")
						f.write(parseString(re.sub(ur'root',ur'movie',dicttoxml.dicttoxml(unic(res)))).toprettyxml().encode("utf-8"))
						f.close()
						link(xmlfile,md+'/imdb.xml')
				if isfile(md+'/.genres.dat'):	# pre-defined genres
                                        with open(md+'/.genres.dat','r') as f:
                                                genres = ast.literal_eval(f.read())
                                        f.close()
                                        y[d] = genres
                                else:				# read genres from res
					genres = res['genre']
					if not genres:
						genres = res['Genre']
					genres = genres.replace(" ","").split(",")
					if not opt_display:
                    	                    json.dump(genres,open(md+'/.genres.dat','w'))
				y[d] = genres
	
				#xml = re.sub('root','movie',dicttoxml.dicttoxml(res).encode('utf-8'))
				#print parseString(xml).toprettyxml()
			else:
				# check .genres.dat file for pre-defined genres to the movie
	                        if isfile(md+'/.genres.dat'):
        	                        with open(md+'/.genres.dat','r') as f:
                	                        genres = ast.literal_eval(f.read())
					f.close()
					y[d] = genres
					n[d.decode('utf-8')] = ''
				else:
					#print 'I can not find the movie ['+d+'], or something likewise.'
					n[d.decode('utf-8')] = ''

	return (y,n)

def matchgenre(imdb_genre,genres,genres_path):
# imdb_genre = genre from IMDB, case insensitive
# genres is a dict from Genre section of GM.cfg
# genres_path is the path to a folder where movies are linked to by genres

	imdb_genre = imdb_genre.lower()
	#print 'Genre: ['+imdb_genre+']'		# comment
	
	# match Genre section in config file
	if genres.get(imdb_genre):
		p = genres_path+genres.get(imdb_genre)+"/"
		if isdir(p):
			return p
	else:
	# match folders
		p = genres_path+imdb_genre+'/'
		g = listdir(genres_path)
		r = [m.group(0) for l in g for m in [re.compile("^("+imdb_genre+").*",re.I).search(l)] if m]
		if len(r)==1:
			p = genres_path+r[0]+'/'
			if isdir(p):
				return p
		print '!!!!! Target genre dirrecoty ['+p+'] does not exist.'
	# match None	
	return None


def argus():
	usage = 'Usage: %prog [options]'
        version = 'v0.4'

        parser = OptionParser(usage=usage,version="%prog "+version)
        parser.add_option("-n","--dry-run", action="store_true", dest="display", default=False, help="display only, do no harm")
        group1 = OptionGroup(parser, "Configuration Options")
        group1.add_option("-c","--config", type="string", dest="config",default="GM.cfg", metavar="/path/to/config", help="desired config file, default file is [%default]")
        group1.add_option("-r","--repository",type="string",dest="movies_repo",metavar="/path/to/movie_repo", help="the path to movies repository")
        group1.add_option("-g","--genres_path",type="string",dest="genres_path",metavar="/path/to/genre", help="the path to genres directory")
        parser.add_option_group(group1)
        group2 = OptionGroup(parser,"Todo & Ignore Lists")
        group2.add_option("-t","--todo", type="string", dest="todo", metavar="/path/to/todo.lst", default="GM.todo", help="the path to todo list file, default todo list file is [%default]")
	group2.add_option("-i","--ignore", type="string", dest="ignore", metavar="/path/to/ignore.list", default="GM.ignore", help="the path to ignore list file, default ignore list file is [%default]")
        parser.add_option_group(group2)

	return parser

def main():
	#print '\tRunning as user ['+getpass.getuser()+'].'	# comment
	parser = argus()
	(opts, args) = parser.parse_args()
	#print opts.display,opts.config,opts.movies_repo,opts.genres_path	# comment

	if opts.config:
		confile = opts.config
	else:
		confile = 'GM.cfg'
        if not isfile(confile):
                print '!!!!! I can not find config file '+confile+'. You can adopt example file GM.cfg.example and rename it to default config file GM.cfg. Exiting ...'
                sys.exit(errno.ENOENT)

	config = ConfigParser.RawConfigParser()
        config.read(confile)
        if opts.movies_repo:
		movies_repo = opts.movies_repo
	else:
		movies_repo = config.get('Path','movies_repo').encode('UTF8')
        if opts.genres_path:
		genres_path = opts.genres_path
	else:
		genres_path = config.get('Path','genre_path').encode('UTF8')
	try:
		cd = config.get('Path','Display').lower()
	except:
		cd = opts.display
	else:
		opts.display = cd
	#print 'opts.display = '+str(opts.display)	# comment

	genres = dict(config.items('Genre'))
        #print genres		# comment
	try:
		todofile = config.get('Path','TODO')
	except:
		todofile = 'GM.todo'
	try:
		ignorefile = config.get('Path','IGNORE')
	except:
		ignorefile = 'GM.ignore'
        if opts.todo:
                todofile = opts.todo
        if isfile(todofile):
                with open(todofile) as t:
                        todo = [line.rstrip('\n') for line in t]
        if opts.ignore:
                ignorefile = opts.ignore
        if isfile(ignorefile):
                with open(ignorefile) as t:
                        ignore = [line.rstrip('\n') for line in t]

        #m = str(raw_input('Movie Name: '))
        #y = str(raw_input('Movie Year: '))
        #res = querymovie(title=m, year=y)
        
	y,n = searchdir(movies_repo,opts.display,ignore)

        #print 'we have processed the following '+str(len(y))+' movies.'
	#ppprint().pprint(y.keys())
	for m in y:
		if y[m]:
			#json.dump(y[m],open(movies_repo+m+'/.genres.dat','w'))		# code move to searchdir()
			for g in y[m]:
				#print m.decode("utf-8"),g		# comment
				linkd = matchgenre(g,genres,genres_path)
				if linkd:
					#print linkd+m		# comment
					if not isfile(linkd+m):
						if opts.display:
							print '	Link ['+linkd+m+'] would be created for movie ['+m+'].'	#comment
						else:
							if not islink(linkd+m):
								symlink(movies_repo+m,linkd+m)
								# print 'Link ['+linkd+m+'] is created for movie ['+m+'].'
							#else:
								# print 'Link ['+linkd+m+'] exists.'
				else:
					print '!!!!! Target genre dirrecoty ['+g.decode("utf-8")+'] does not exist for movie ['+m.decode("utf-8")+'].'
	if len(n)>0:
		print '\n!!!!! I find no IMDB info for the following '+str(len(n))+' movies,'
		#ppprint().pprint(n.keys())
		if opts.display:
			td = 'GM.todo.mock'
		f = open(todofile,'w')
		for m in n:
			print m.encode("utf-8")
			f.write(join(movies_repo,m.encode("utf-8"),'\n'))
		f.close()

if __name__ == '__main__':
	main()
