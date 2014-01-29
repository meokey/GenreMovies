import omdb
import dicttoxml
import re
from xml.dom.minidom import parseString

def main():
	movie = str(raw_input('Movie Name: '))
	year = str(raw_input('Movie Year: '))

	omdb.set_default('tomatoes','true')
	res = omdb.get(title=movie,year=year)
	if len(res)>0:	
		print 'Genre: '+res['genre']

		xml = re.sub('root','movie',dicttoxml.dicttoxml(res).encode('utf-8'))
		print parseString(xml).toprettyxml()
	else:
		aa = omdb.Client()
		movies = parseString(aa.request(s=movie+'*', r='XML').content).getElementsByTagName('Movie')
		if movies.length>0:
			print 'I can not find the movie ['+movie+'] in year ['+year+']. But do find the following(s):'
			for node in movies:
				print node.attributes['Title'].value+'\t in '+node.attributes['Year'].value+',\tIMDB:'+node.attributes['imdbID'].value
		else:
			print 'I can not find the movie['+movie+'] in year '+year+',or something likewise.'

if __name__ == '__main__':
	main()
