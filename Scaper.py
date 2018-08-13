from bs4 import BeautifulSoup
import requests
import sqlite3
import random
conn = sqlite3.connect('example.db')

# library to generate user agent
from user_agent import generate_user_agent

proxies = []
headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}
proxies_doc = requests.get('https://www.sslproxies.org/', timeout=5, headers=headers)
soup = BeautifulSoup(proxies_doc.content, "html.parser")
proxies_table = soup.find(id='proxylisttable')

# Save proxies in the array
for row in proxies_table.tbody.find_all('tr'):
	proxies.append({'ip':   row.find_all('td')[0].string, 'port': row.find_all('td')[1].string})

def random_proxy():
	return random.randint(0, len(proxies) - 1)


page_link ='https://www.some-website.com'
page_link_http ='http://www.some-website.com'
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

c.execute("SELECT EXISTS(SELECT 1 FROM pages WHERE url=?)", (page_link,))
if (not c.fetchone()[0]):
	c.execute("INSERT INTO pages VALUES (?)", (page_link,))


nextRow = True
counter = 1
newProxies = True
repeatRequest = 0
oldCounter = counter

def loop_through():
	global nextRow
	global proxies
	global counter
	global newProxies
	global repeatRequest
	global oldCounter
	if nextRow:
		nextRow = False
		i = 0
		for row in c.execute('SELECT url FROM pages ORDER BY ROWID ASC'):
			i = i + 1
			if counter == i:
				nextRow = True
				newProxies = True
				proxy_index = random_proxy()
				proxy = proxies[proxy_index]
				url = row[0]
				if url[0]=='/':
					url = page_link + url

				if (not url.startswith('http')):
					url = page_link + '/' + url

				print("Num link ", counter, " ********************************************************")
				if counter != oldCounter:
					repeatRequest = repeatRequest + 1

				try:
					page_response = requests.get(url, proxy['ip'] + ':' + proxy['port'], timeout=300, headers=headers)
					page_content = BeautifulSoup(page_response.content, "html.parser")
					a = page_content.find_all('a', href=True)
					img = page_content.find_all('img', src=True)
					video = page_content.find_all('video', src=True)
					for x in a:
						c.execute("SELECT EXISTS(SELECT 1 FROM pages WHERE url=?)", (x['href'],))
						#print("Check_href:", x['href'], sep="")
						if ((page_link in x['href']) or (page_link_http in x['href']) or x['href'][0]=='/' or (not x['href'].startswith('http'))) and (not c.fetchone()[0]):
							c.execute("INSERT INTO pages VALUES (?)", (x['href'],))
							#print("href: ", x['href'], sep="")


					for x in img:
						c.execute("SELECT EXISTS(SELECT 1 FROM img WHERE url=?)", (x['src'],))
						if ((page_link in x['src']) or (page_link_http in x['src']) or x['src'][0]=='/' or (not x['src'].startswith('http'))) and (not c.fetchone()[0]):
							c.execute("INSERT INTO img VALUES (?)", (x['src'],))
							#print("img:", x['src'], sep="")


					for x in video:
						c.execute("SELECT EXISTS(SELECT 1 FROM video WHERE url=?)", (x['src'],))
						if ((page_link in x['src']) or (page_link_http in x['src']) or x['src'][0]=='/' or (not x['src'].startswith('http'))) and (not c.fetchone()[0]):
							c.execute("INSERT INTO video VALUES (?)", (x['src'],))
							#print("video:", x['src'], sep="")


				except Exception as e:
					del proxies[proxy_index]
					if repeatRequest <= 5:
						counter = counter - 1
					else:
						repeatRequest = 0
						oldCounter = counter

					if len(proxies) < 3:
						while newProxies:
							try:
								proxy_index = random_proxy()
								proxy = proxies[proxy_index]
								newProxies = False
								proxies_doc = requests.get('https://www.sslproxies.org/', proxy['ip'] + ':' + proxy['port'], timeout=5, headers=headers)
								soup = BeautifulSoup(proxies_doc.content, "html.parser")
								proxies_table = soup.find(id='proxylisttable')
								for row in proxies_table.tbody.find_all('tr'):
									proxies.append({'ip':   row.find_all('td')[0].string, 'port': row.find_all('td')[1].string})
							except Exception as e:
								newProxies = True
								







				







while nextRow:
	loop_through()
	counter = counter + 1
	oldCounter = oldCounter + 1
	if(counter % 100 == 0):
		conn.commit()
		


conn.commit()
conn.close()


