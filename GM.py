import omdb
import dicttoxml
import re
from xml.dom.minidom import parseString
import ConfigParser

def querymovie(*args, **kwargs):
	title = kwargs.get('title', '')
	year = kwargs.get('year', '')
	imdbid = kwargs.get('imdbid', '')

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
        
        print 'I can not find the movie ['+title+'] in year '+year+',or something likewise.'	
	return ''

def main():

	config = ConfigParser.RawConfigParser()
	config.read('GM.cfg')
	movies_repo = config.get('Path','movies_repo')
	genres_path = config.get('Path','genre_path')	
	genres = dict(config.items('Genre'))
	#print genres

	m = str(raw_input('Movie Name: '))
	y = str(raw_input('Movie Year: '))

	res = querymovie(title=m, year=y)

	if len(res)>0:
		print 'Movie:\t'+res['title']+', '+res['year']+', '+res['imdb_id']+', '+res['genre']
		xml = re.sub('root','movie',dicttoxml.dicttoxml(res).encode('utf-8'))
		print parseString(xml).toprettyxml()

if __name__ == '__main__':
	main()
