import json
import re
import os
import traceback
from datetime import datetime
import requests
import subprocess


class BitcoinPriceAlert(object):
    DATA_FILE = os.path.dirname(os.path.abspath(__file__)) + "/data.json"
    DATA = {
        "zebpay": {
            "item": ['buy', "sells"],
            "url": "http://www.bitcoinrates.in/getdata.php"
        },
        "bci": {
            "item": ['buy', "sells"],
            "url": "https://bitcoin-india.org/"
        },
        "coinsecure": {
            "item": ['buy', "sells"],
            "url": "http://www.bitcoinrates.in/getdata.php"
        },
        "coinbase": {
            "item": ['buy'],
            "url": "https://api.coinbase.com/v2/prices/INR/spot?"
        }
    }
    
    URL_DATA = {
        "http://www.bitcoinrates.in/getdata.php": None,
        "https://bitcoin-india.org/": None,
        "https://api.coinbase.com/v2/prices/INR/spot?": None
    }
    
    DATA_TEMPLATE = {
    
    }
    
    def __init__(self):
        try:
            self.timestamp = datetime.now().isoformat()
            price_data = self.prices_data()
            data = self.dump_data(price_data)
            self.check_alert(data)
        except Exception as e:
            print "Serious Exception ===================>"
            traceback.print_exc()
            print "Serious Exception <==================="
            self.alert()

    def zebpay_prices(self):
        try:
            url = self.DATA['zebpay']['url']
            if self.URL_DATA[url] is None:
                res = json.loads(requests.get(url).text)
                self.URL_DATA[url] = res
            
            res = self.URL_DATA[url]
            rates = res['rates']['4']
            buy = float(rates['buyratefees'])
            sell = float(rates['sellratefees'])
            return buy, sell
        except Exception as e:
            traceback.print_exc()
            return None, None
    
    def coinsecure_prices(self):
        try:
            url = self.DATA['coinsecure']['url']
            if self.URL_DATA[url] is None:
                res = json.loads(requests.get(url).text)
                self.URL_DATA[url] = res
            
            res = self.URL_DATA[url]
            rates = res['rates']['1']
            buy = float(rates['buyratefees'])
            sell = float(rates['sellratefees'])
            return buy, sell
        except Exception as e:
            traceback.print_exc()
            return None, None
    
    def bci_prices(self):
        try:
            url = self.DATA['bci']['url']
            if self.URL_DATA[url] is None:
                body = subprocess.check_output(['curl', url]).split("\n")
                self.URL_DATA[url] = body
            
            body = self.URL_DATA[url]
            buy = [x for x in body if 'buyvalue' in x][0]
            sell = [x for x in body if 'sellvalue' in x][0]
            buy = float(re.findall(r"[\d]+", buy)[1])
            sell = float(re.findall(r"[\d]+", sell)[1])
            return buy, sell
        except Exception as e:
            traceback.print_exc()
            return None, None
    
    def coinbase_prices(self):
        try:
            url = self.DATA['coinbase']['url']
            if self.URL_DATA[url] is None:
                res = json.loads(requests.get(url).text)
                self.URL_DATA[url] = res
            
            res = self.URL_DATA[url]
            price = float(res['data'][0]['amount'])
            return price, price
        except Exception as e:
            traceback.print_exc()
            return None, None
    
    def prices_data(self):
        data = {}
        
        for wallet in self.DATA.keys():
            for type in self.DATA[wallet]['item']:
                data[wallet] = data.get(wallet) or {}
                data[wallet][type] = self.get_price(wallet, type)
        return data
    
    def get_price(self, wallet, type):
        prices = [None, None]
        if wallet == 'zebpay':
            prices = self.zebpay_prices()
        elif wallet == 'bci':
            prices = self.bci_prices()
        elif wallet == 'coinsecure':
            prices = self.coinsecure_prices()
        elif wallet == 'coinbase':
            prices = self.coinbase_prices()
        
        if type == 'buy':
            return prices[0]
        elif type == 'sells':
            return prices[1]
    
    def get_formatted_price(self, price):
        return {
            "price": price,
            "timestamp": self.timestamp
        }
    
    def dump_data(self, price_data):
        data = open(self.DATA_FILE).read()
        data = json.loads(data) if data.__len__() > 0 else {}
        
        for wallet in self.DATA.keys():
            for type in self.DATA[wallet]['item']:
                data[wallet] = data.get(wallet) or {}
                data[wallet][type] = data[wallet].get(type) or []
                self.add_price_to_data(data[wallet][type], price_data[wallet][type])
        
        open(self.DATA_FILE, 'w').write(json.dumps(data, indent=4))
        return data
    
    def add_price_to_data(self, data, price):
        if price is None:
            price = data[-1]['price']
        
        d = self.get_formatted_price(price)
        data.append(d)
    
    def check_alert(self, data):
        alert_me = False
        for wallet in data.keys():
            for type in data[wallet].keys():
                last_1_slope = abs(data[wallet][type][-2:][0]['price'] - data[wallet][type][-1]['price'])
                last_3_slope = abs(data[wallet][type][-4:][0]['price'] - data[wallet][type][-1]['price'])
                last_6_slope = abs(data[wallet][type][-7:][0]['price'] - data[wallet][type][-1]['price'])
                last_10_slope = abs(data[wallet][type][-11:][0]['price'] - data[wallet][type][-1]['price'])
                last_15_slope = abs(data[wallet][type][-16:][0]['price'] - data[wallet][type][-1]['price'])
                
                if last_1_slope >= 1500 or last_3_slope >= 2500 or last_6_slope >= 3500 or last_10_slope >= 4500 or last_15_slope >= 5500:
                    alert_me = "%s %s %s %s %s %s %s"%(wallet, type, last_1_slope, last_3_slope, last_6_slope, last_10_slope, last_15_slope)
                    print alert_me
                    
        if alert_me:
            self.alert("Alert")
            
    def alert(self, str):
        os.system(""" say "%s" """ % str)


BitcoinPriceAlert()
