from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from time import time
import json

from data import refresh_time, server_adress
from skyblock_api import update
from items import auction_items, enchanted_books

class Server(HTTPServer):
    def __init__(self, *params):
        super(HTTPServer, self).__init__(*params)
        self.bazaar = None
        self.auctions_list = None
        self.last_updated = None
        self.result = ""
        api_puller = threading.Thread(target = self.pull_from_api)
        api_puller.start()

    def pull_from_api(self):
        self.bazaar, self.auctions_list = update()
        self.last_updated = time()
        self.parse_data()
        threading.Timer(refresh_time, self.pull_from_api).start()

    def parse_data(self):
        profits = {
                'AH': [],
                'BZ': [],
                'LAST_UPDATED': self.last_updated
        }
        # Simple auction items
        for item in auction_items:
            item_prizes = []
            for auction in self.auctions_list:
                if auction['item_name'] == item['name']:
                    if 'bin' in auction.keys():
                        item_prizes.append(auction['starting_bid'])
            item_prizes.sort()
            item_object = {
                    'name': item['name'],
                    'bin_1': None,
                    'bin_5': None,
                    'bin_10': None,
                    'count': len(item_prizes)
            }
            if len(item_prizes) > 0:
                item_object['bin_1'] =  round(item_prizes[0]/item['price'], 2)
            if len(item_prizes) > 4:
                item_object['bin_5'] =  round(item_prizes[4]/item['price'], 2)
            if len(item_prizes) > 9:
                item_object['bin_10'] =  round(item_prizes[9]/item['price'], 2)
            profits['AH'].append(item_object)

        # Enchanted books
        for book in enchanted_books:
            item_prizes = []
            for auction in self.auctions_list:
                if auction['item_name'] == 'Enchanted Book':
                    if book['name'] in auction['extra']:
                        if 'bin' in auction.keys():
                            item_prizes.append(auction['starting_bid'])
            item_prizes.sort()
            item_object = {
                'name': book['name'],
                'bin_1': None,
                'bin_5': None,
                'bin_10': None,
                'count': len(item_prizes)
            }
            if len(item_prizes) > 0:
                item_object['bin_1'] = round(item_prizes[0]/book['price'], 2)
            if len(item_prizes) > 4:
                item_object['bin_5'] = round(item_prizes[4]/book['price'], 2)
            if len(item_prizes) > 9:
                item_object['bin_10'] = round(item_prizes[9]/book['price'], 2)
            profits['AH'].append(item_object)

        # Bazaar
        catalyst = self.bazaar["products"]["CATALYST"]["quick_status"]
        hyper_catalyst = self.bazaar["products"]["HYPER_CATALYST"]["quick_status"]
        profits['BZ'].append(
            {
                'name': 'Upgrading catalysts (buy order->sell offer)',          
                'profits': round((hyper_catalyst['buyPrice'] - catalyst['sellPrice']) * 8 / 300, 2)
            }
        )
        profits['BZ'].append(
            {
                'name': 'Upgrading catalysts (buy instantly->sell instantly)',
                'profits': round((hyper_catalyst['sellPrice'] - catalyst['buyPrice']) * 8 / 300, 2)
            }
        )
        self.result = json.dumps(profits, indent=2)
        

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not self.server.bazaar:
            self.send_response(400)
            self.send_header('content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write('The api is starting, please wait.'.encode())
        if self.path == '/get_cookie_data':
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.server.result.encode())
        else:
            self.send_response(400)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('content-type', 'text/html')
            self.end_headers()

def run(server_class=Server, handler_class=Handler):
    httpd = server_class(server_adress, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run()