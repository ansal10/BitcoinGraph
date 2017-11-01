import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import os
import datetime

FILENAME = '/Users/ansal/PycharmProjects/PyScripts/data2.txt'
GRAPH_SIZE_LIMIT = 10000


def alert(price=0):
	if price > 4000:
		os.system('say "Time to Trade, Hurry"')


def zebpay_price():
	url = "https://api.zebpay.com/api/v1/ticker?currencyCode=INR"
	res = requests.get(url).text
	res = json.loads(res)
	buy = res['buy']
	sell = res['sell']
	return buy, sell


def bitcoin_india_price():
	url = 'https://bitcoin-india.org'
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("--window-size=1920x1080")
	chrome_driver = '/Users/ansal/codebase/chromedriver'
	driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
	try:
		driver.get(url)
		time.sleep(5)
		buy = float(driver.find_elements_by_id('buyvalue')[0].text)
		sell = float(driver.find_elements_by_id('sellvalue')[0].text)
	except Exception as e:
		print e
	finally:
		driver.quit()
	return buy, sell


zb = zebpay_price()
bci = bitcoin_india_price()

file_data = open(FILENAME).read()
data = json.loads(file_data)

now = datetime.datetime.now().isoformat()

data['data']['zebpay']['buys'].append({'price':zb[0], 'time':now})
data['data']['zebpay']['sells'].append({'price':zb[1], 'time':now})

data['data']['bci']['buys'].append({'price':bci[0], 'time':now})
data['data']['bci']['sells'].append({'price':bci[1], 'time':now})

for wallet in ['zebpay', 'bci']:
	if data['data'][wallet]['buys'].__len__() > GRAPH_SIZE_LIMIT:
		data['data'][wallet]['buys'] = data['data'][wallet]['buys'][1:]
		data['data'][wallet]['sells'] = data['data'][wallet]['sells'][1:]

raw_data = json.dumps(data, indent=4)
f = open(FILENAME, 'w')
f.write(raw_data)
f.close()
alert(bci[1] - zb[0])
