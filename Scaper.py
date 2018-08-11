from bs4 import BeautifulSoup
import requests
import sqlite3
conn = sqlite3.connect('example.db')

# library to generate user agent
from user_agent import generate_user_agent


page_link ='https://www.some-website.com'
headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}
page_response = requests.get(page_link, timeout=5, headers=headers)
page_content = BeautifulSoup(page_response.content, "html.parser")
# print("href:", x['href'], sep="")
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS pages
             (url text)''')

c.execute('''CREATE TABLE IF NOT EXISTS img
             (url text)''')

c.execute('''CREATE TABLE IF NOT EXISTS video
             (url text)''')

c.execute("INSERT INTO pages VALUES (?)", (page_link,))

nextRow = True
counter = 1

def loop_through(num):
	global nextRow
	if nextRow:
		nextRow = False
		i = 0
		for row in c.execute('SELECT url FROM pages ORDER BY ROWID ASC'):
			i = i + 1
			if num == i:
				nextRow = True
				print("new link ********************************************************")
				headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}
				page_response = requests.get(row[0], timeout=30, headers=headers)
				print("Reponse ", page_response.status_code, sep="")
				page_content = BeautifulSoup(page_response.content, "html.parser")
				a = page_content.find_all('a', href=True)
				img = page_content.find_all('img', src=True)
				video = page_content.find_all('video', src=True)
				for x in a:

					c.execute("SELECT EXISTS(SELECT 1 FROM pages WHERE url=?)", (x['href'],))
					if (page_link in x['href']) and (not c.fetchone()[0]):
						c.execute("INSERT INTO pages VALUES (?)", (x['href'],))
						#print("href:", x['href'], sep="")


				for x in img:
					if page_link in x['src']:
						c.execute("INSERT INTO img VALUES (?)", (x['src'],))
						#print("img:", x['src'], sep="")


				for x in video:
					if page_link in x['src']:
						c.execute("INSERT INTO video VALUES (?)", (x['src'],))
						#print("video:", x['src'], sep="")







while nextRow:
	loop_through(counter)
	counter = counter + 1
	conn.commit()





#conn.commit()
conn.close()
