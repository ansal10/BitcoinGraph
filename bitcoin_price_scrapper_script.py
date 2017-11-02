import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import os

FILENAME = '/Users/ansal/PycharmProjects/PyScripts/data.txt'
GRAPH_SIZE_LIMIT = 1000
DATA_FORMAT = {
	"data": {
		"coinsecure": {
			"buys": [], "sells": []
		},
		"zebpay": {
			"buys": [], "sells": []
		},
		"bci": {
			"buys": [], "sells": []
		},
		"coinbase": {
			"buys": [], "sells": []
		}
	}
}


def alert(price=0):
	os.system('say "Alert"')
	pass


def coinbase_price():
	url = "https://api.coinbase.com/v2/prices/INR/spot?"
	res = json.loads(requests.get(url).text)
	price = float(res['data'][0]['amount'])
	return price, price


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
	buy, sell = None, None
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


def coinsecure_price():

	buy, sell = None, None
	# url = 'https://coinsecure.in/exchange'
	# chrome_options = Options()
	# chrome_options.add_argument("--headless")
	# chrome_options.add_argument("--window-size=1920x1080")
	# chrome_driver = '/Users/ansal/codebase/chromedriver'
	# driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
	# try:
	# 	driver.get(url)
	# 	time.sleep(10)
	# 	buy = driver.find_elements_by_xpath("//h2[@class='r-h ng-binding']")[0].text.encode('utf-8', 'ignore')
	# 	sell = driver.find_elements_by_xpath("//h2[@class='r-h ng-binding']")[1].text.encode('utf-8', 'ignore')
	# 	buy = int(''.join([i if i.isdigit() else '' for i in buy])) / 100
	# 	buy = int((1.0 / .996) * buy)
	# 	sell = int(''.join([i if i.isdigit() else '' for i in sell])) / 100
	#
	# except Exception as e:
	# 	print e
	# finally:
	# 	driver.quit()
	# if buy == 0 or sell == 0:
	# 	return None, None

	return buy, sell


zb = zebpay_price()
bci = bitcoin_india_price()
csc = coinsecure_price()
cb = coinbase_price()

max_buy = max([zb[0], bci[0], csc[0]])
min_sell = min(zb[1], bci[1], csc[1])


file_data = open(FILENAME).read()
data = json.loads(file_data) if file_data.__len__() > 0 else DATA_FORMAT

data['data']['zebpay']['buys'].append(zb[0])
data['data']['zebpay']['sells'].append(zb[1])

data['data']['bci']['buys'].append(bci[0])
data['data']['bci']['sells'].append(bci[1])

data['data']['coinbase']['buys'].append(cb[0])
data['data']['coinbase']['sells'].append(cb[0])

# if csc[0] is not None:
data['data']['coinsecure']['buys'].append(csc[0])
data['data']['coinsecure']['sells'].append(csc[1])

alert_flag = False
for wallet in DATA_FORMAT['data'].keys():
	if data['data'][wallet]['buys'].__len__() > GRAPH_SIZE_LIMIT:
		data['data'][wallet]['buys'] = data['data'][wallet]['buys'][1:]
		data['data'][wallet]['sells'] = data['data'][wallet]['sells'][1:]

	# price down notification
	for x in ['buys', 'sells']:
		slopes = data['data'][wallet][x]
		last_1_slope = abs(slopes[-2:][0] - slopes[-2:][-1])
		last_3_slope = abs(slopes[-4:][0] - slopes[-4:][-1])
		last_5_slope = abs(slopes[-6:][0] - slopes[-6:][-1])
		last_8_slope = abs(slopes[-9:][0] - slopes[-9:][-1])

		if last_1_slope >= 2500 or last_3_slope >= 3500 or last_5_slope >= 5000 or last_8_slope >= 7000:
			alert_flag = True

		print wallet, x, last_1_slope, last_3_slope, last_5_slope, last_8_slope

if alert_flag:
	alert()

raw_data = json.dumps(data, indent=4)
f = open(FILENAME, 'w')
f.write(raw_data)
f.close()
# alert(bci[1] - csc[0])
