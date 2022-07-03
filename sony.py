from tkinter import messagebox
from requests.cookies import cookiejar_from_dict
import requests
import re
import json
import time


class Bot:
    def __init__(self, url):
        with open('data\\sony\\cookie.json', 'r') as fd:
            cookie = json.load(fd)
        self.session = requests.session()
        self.session.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alice',
            'Upgrade-Insecure-Requests': '1',
            'Host': 'store.sony.com.tw',
            'Origin': 'https://store.sony.com.tw',
            'Referer': 'https://store.sony.com.tw/shopping/addToCartJs',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36'
        }
        self.session.cookies = cookiejar_from_dict(cookie)
        self.url = url

    def get_request(self, url):
        # while True:
        #     response = self.session.get(url)
        #     if response.ok:
        #         return response
        #     time.sleep(1)

        while True:
            try:
                response = self.session.get(url)
            except requests.exceptions.Timeout:
                print('Timeout')
                time.sleep(1)
                continue
            except requests.exceptions.ConnectionError:
                print('Connection Error')
                time.sleep(1)
                continue
            except requests.exceptions.RequestException:
                print('Catastrophic Error')
                return None
            else:
                return response

        #response = self.session.get(url)
        #return response

    def post_request(self, url, data):
        # while True:
        #     response = self.session.post(url, data)
        #     if response.ok:
        #         return response
        #     time.sleep(1)

        while True:
            try:
                response = self.session.post(url, data)
            except requests.exceptions.Timeout:
                print('Timeout')
                time.sleep(1)
                continue
            except requests.exceptions.ConnectionError:
                print('Connection Error')
                time.sleep(1)
                continue
            except requests.exceptions.RequestException:
                print('Catastrophic Error')
                return None
            else:
                return response

        #response = self.session.post(url, data)
        #return response

    def get_item_information(self):
        item_pattern = re.compile(R"data-pid=\"([0-9a-zA-Z]+)\"")
        response = self.get_request(self.url)
        text = response.text.split('\n')
        for line in text:
            if re.search(item_pattern, line):
                print('[+] Get Item Information Success')
                return re.search(item_pattern, line).group(1)

    def add_item_to_cart(self, cart_id):
        url = 'https://store.sony.com.tw/shopping/addToCartJs'
        payload = {'uuid': cart_id}
        self.post_request(url, payload)
        print('[+] Add Cart Successfully!')

    def choose_pay_method(self, data_id):
        payload = {
            'qty_' + data_id: '1',
            'CouponID': ''
        }
        url = 'https://store.sony.com.tw/shopping/choosePaymentmethod'
        self.post_request(url, payload)
        print('[+] Choose Payment Method Successfully!')

    def show_cart(self):
        item_pattern = re.compile(R"data-item=\"([0-9a-zA-Z]+)\"")
        url = 'https://store.sony.com.tw/shopping/showCart'
        response = self.post_request(url, None)
        text = response.text.split('\n')
        for line in text:
            if re.search(item_pattern, line):
                print('[+] Find Data item ID: ', re.search(item_pattern, line).group(1))
                return re.search(item_pattern, line).group(1)

    def save_bucket(self):
        with open('data\\sony\\user_information.json', 'r', encoding='utf-8') as fd:
            user_information = json.load(fd)
        url = 'https://store.sony.com.tw/shopping/saveBasket'
        response = self.post_request(url, user_information)
        text = response.text.split('\n')

        token_pattern = re.compile(R"value=\"([0-9a-zA-Z-]+)\"")
        sitekey_pattern = re.compile(R"data-sitekey=\"([0-9a-zA-Z-]+)\"")
        for line in text:
            if 'SYNCHRONIZER_TOKEN' in line:
                if token_pattern.search(line):
                    self.token = token_pattern.search(line).group(1)
                    print('[+] Find token: ', self.token)
            if 'g-recaptcha-box' in line:
                if sitekey_pattern.search(line):
                    self.key = sitekey_pattern.search(line).group(1)
                    print('[+] Find Key', self.key)

    def finish_order(self, captcha_response):
        url = 'https://store.sony.com.tw/shopping/finishOrder'
        payload = {
            'SYNCHRONIZER_TOKEN': self.token,
            'SYNCHRONIZER_URI': '/shopping/previewOrder',
            'isPC': 'Y',
            'submitType': 'cart',
            'accept': '1',
            'g-recaptcha-response': captcha_response
        }
        response = self.post_request(url, payload)

        text = response.text.split('\n')
        value_pattern = re.compile(R"value=\"([0-9a-zA-Z-]+)\"")
        for line in text:
            if 'merID' in line:
                if value_pattern.search(line):
                    self.member_id = value_pattern.search(line).group(1)
                    print('[+] merID: ', value_pattern.search(line).group(1))
            elif 'URLENC' in line:
                if value_pattern.search(line):
                    self. url_enc = value_pattern.search(line).group(1)
                    print('[+] URLENC: ', value_pattern.search(line).group(1))

    def auth(self):
        url = 'https://epos.ctbcbank.com/auth/SSLAuthUI.jsp'
        payload = {
            'merID': self.member_id,
            'URLEnc': self. url_enc
        }
        response = self.session.post(url, payload)
        
        image = requests.get('https://epos.ctbcbank.com/auth/images?rand=')
        print(response)

    def pay(self):
        url = 'https://epos.ctbcbank.com/auth/authPayment'
        with open('data\\sony\\credit_card.json', 'r') as fd:
            credit_card_information = json.load(fd)
        response = self.post_request(url, credit_card_information)
        print(response.text)

    def run(self):
        cart_id = self.get_item_information()
        self.add_item_to_cart(cart_id)
        data_id = self.show_cart()
        self.choose_pay_method(data_id)
        self.save_bucket()
        print('Now you should pass reCapture test yourself: https://store.sony.com.tw/shopping/previewOrder')

    def pop_up_info(self):
        cartID = self.get_item_information()
        while not cartID:
            print('retry')
            time.sleep(60)
            cartID = self.get_item_information()

        messagebox.showinfo(title="Greetings", message="Hello World!")


if __name__ == '__main__':
    bot = Bot('https://store.sony.com.tw/product/show/ff8080817e29d7dd017e2ece92b402ac')
    # bot.pop_up_info()
    bot.run()
    captcha_response = ''
    bot.save_bucket()
    bot.finish_order(captcha_response)



