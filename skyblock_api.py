import requests

from data import api_key

def update():
    url = 'https://api.hypixel.net/skyblock/'

    bz = requests.get(url + 'bazaar', params = {'key': api_key})
    bazaar = bz.json()

    auctions_list = []
    ah0 = requests.get(url + 'auctions', params = {'key': api_key})
    page0 = ah0.json()
    num_of_pages = page0["totalPages"] + 1
    #auctions_list += page0["auctions"]

    #for page_num in range(1, num_of_pages):
    for page_num in range(0, num_of_pages):
        print('Downloading page', page_num)
        page_n = requests.get(url + 'auctions', params = {'key': api_key, 'page': page_num})
        page_json = page_n.json()
        if page_json["success"]:
            for auction in page_json["auctions"]:
                auction_compact = {
                    "item_name": auction["item_name"],
                    "extra": auction["extra"]
                }
                if 'bin' in auction.keys():
                    auction_compact['bin'] = True
                    auction_compact['starting_bid'] = auction['starting_bid']
                auctions_list.append(auction_compact)
        else:
            print('error')
    print('Finished updating')
    
    return bazaar, auctions_list

if __name__ == '__main__':
    update()