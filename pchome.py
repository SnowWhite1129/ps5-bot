import json
import time
import requests
from requests.cookies import cookiejar_from_dict


class Bot:
    def __init__(self):
        self.gift = ['DGBJKI-A900EO5SQ-000', 'DGBJG9-A900B51O4-000']
        self.rs = 'DGBJG9'
        self.pure_id = 'DGBJG9-A900EO5UE'
        self.id = 'DGBJG9-A900EO5UE-000'
        self.session = requests.session()
        self.session.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
            'Host': '24h.pchome.com.tw',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://24h.pchome.com.tw',
            'Referer': 'https://24h.pchome.com.tw/' + self.pure_id,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36'
        }
        with open('data\\pchome\\cookie.json', 'r') as fd:
            cookie = json.load(fd)
        self.session.cookies = cookiejar_from_dict(cookie)

    def get_cart_information(self):
        print(time.time())
        url = 'https://24h.pchome.com.tw/prod/cart/v1/prod/' + self.id + '/snapup?_=' + str(int(time.time()*1000))
        print(url)
        response = self.session.get(url)
        print(response.text)
        response = json.loads(response.text)
        if response["Status"] != "OK":
            print('Fail')
        self.mac_expire = response["MACExpire"]
        self.mac = response["MAC"]

    def add_cart(self):
        # G is gift list
        gift = '"' + self.gift[0] + '","' + self.gift[1] + '"'
        payload = {
            'data': '{"G":[''],"A":[],"B":[],"TB":"24H","TP":2,"T":"ADD","TI":"' + self.id + '","RS":"' + self.rs + '","YTQ":1,"CAX":"' + self.mac + '","CAXE":"' + self.mac_expire + '"}'
        }
        print(payload['data'])
        url = 'https://24h.pchome.com.tw/fscart/index.php/prod/modify?' + str(int(time.time()*1000))
        response = self.session.post(url, data=payload)
        response = json.loads(response.text)
        if response["PRODTOTAL"] == 0:
            print('Add cart failed!')
            return False

    def get_pk(self):
        payload = {'JSON': 'true'}
        url = 'https://ecssl.pchome.com.tw/sys/cflow/fsapi/getPK'
        response = self.session.post(url)
        print(response.text)

    def send_order(self):
        with open('data\\pchome\\pchome.json', 'r') as fd:
            data = json.load(fd)
        payload = {
            'frmData': data,
            'CouponInfo': '{"actData":[],"prodCouponData":[]}'
        }
        url = 'https://ecssl.pchome.com.tw/sys/cflow/fsapi/BigCar/BIGCAR/OrderSubmit'
        self.session.post(url)


if __name__ == '__main__':
    bot = Bot()
    while True:
        bot.get_cart_information()
        if bot.add_cart() is True:
            break
        time.sleep(0.2)
