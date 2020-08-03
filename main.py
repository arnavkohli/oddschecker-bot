from bs4 import BeautifulSoup as bs
import requests, pprint
from telegram_bot import TelegramBot
from datetime import datetime
import time as Time

#API_TOKEN = <API_TOKEN_HERE>
#CHAT_ID = <CHAT_ID_HERE>


bot = TelegramBot(token=API_TOKEN, chat_id=CHAT_ID)

def clean_name(val):
	return val.lower().replace(' ','-')

horses_done = []

def getting_race_tracks_and_timings():
	url = "https://www.oddschecker.com/horse-racing"
	page = requests.get(url)
	soup = bs(page.text, 'html.parser')

	todays_divs = soup.find_all('div', attrs = {'data-day' : 'today'})

	objs = []
	for div in todays_divs:
		objs += div.find_all(['div', 'span'], attrs = {'class' : ['race-details', 'flag-wrap']})

	race_tracks = {}

	total = len(objs)
	for index, obj in enumerate(objs):
		if index == total - 1:
			continue
		if index % 2 == 0:
			country = objs[index + 1].text.strip()
			if country in ('UK', 'USA'):
				try:
					key = clean_name(obj.find('a', attrs = {'class' : 'venue'} ).text.strip())
					val = [i.text for i in obj.find_all('a', attrs = {'class' : 'race-time'} )]
					race_tracks[key] = val
				except:
					continue

	return race_tracks

def should_send_notification(bet365_odds, other):
	# Compare first part
	try:
		bet_fh = int(bet365_odds.split('/')[0])
		if bet_fh <= 10:
			diff = 3
		else:
			diff = 6
		other_fh = int(other.split('/')[0])
		if bet_fh - other_fh >= diff:
			return True
	except:
		return False

	# Compare second part
	try:
		bet_fh = int(bet365_odds.split('/')[1])
		if bet_fh <= 10:
			diff = 3
		else:
			diff = 6
		other_fh = int(other.split('/')[1])
		if bet_fh - other_fh >= diff:
			return True
	except:
		return False

	return False


def getting_race_info(race_tracks):
	for track in race_tracks:
		base = f"https://www.oddschecker.com/horse-racing/{track}/"
		print (f"[TRACK] {track}")
		for time in race_tracks[track]:
			try:
				url = base + f"{time}/winner"
				page = requests.get(url)
				soup = bs(page.text, 'html.parser')

				table = soup.find('tbody')
				objs = table.find_all('tr')
			except:
				continue
				
			print (f"-[+] {time}")
			changes = 0
			horses = []

			for obj in objs:
				try:
					name = obj.find('span', attrs = {'class' : 'name-wrap'}).text
					tds = obj.find_all('td')
					bet365_odds = None
					for td in tds:
						p = td.find('p')
						if p:
							if not bet365_odds:
								bet365_odds = p.text
								continue
							if should_send_notification(bet365_odds, p.text) and (name not in horses_done):
								changes += 1
								horses.append(name)
								horses_done.append(name)
								if changes > 2:
									break
				except:
					continue

			if 0 < changes <= 2:
				msg = f"[+] Lookout for {' || '.join(horses)} @ {track.upper()} {time}!"
				print (msg)
				bot.sendMessage(msg)

			Time.sleep(2)



def run():
	race_tracks = getting_race_tracks_and_timings()
	getting_race_info(race_tracks)



if __name__ == '__main__':
	while True:
		start = datetime.now()
		run()
		end = datetime.now()

		print (f'[RUN FINISHED] Time Taken: {(end - start).seconds}')

	
