from bs4 import BeautifulSoup
import re, urllib
from urllib import urlopen
import MySQLdb



def scrape_page(number,cursor,db):
	url = 'http://basketball.realgm.com/international/stats/2017/Averages/All/All/points/All/desc/' + str(number)
	f = urlopen(url)
	soup = BeautifulSoup(f.read(),'lxml')
	tbody = soup.findAll('tbody')[0]
	links = tbody.findAll('a')
	for link in links:
		id_ = re.findall('Summary/(.+?)">',str(link))[0]
		name = link.contents[0]
		query = "INSERT IGNORE INTO players (player_id, player_name) VALUES (" + id_ + ',"' +  name + '"' + ");"
		cursor.execute(query)
		db.commit()
	
#add ncaa, nba, d league
#also add teams


if __name__ == "__main__":
	db = MySQLdb.connect("localhost","root","","ballusers")
	cursor = db.cursor()
	total_pages = 132
	for i in range(1,total_pages + 1):
		print i
		scrape_page(i,cursor,db)
	db.close()
