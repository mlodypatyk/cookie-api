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
    auctions_list += page0["auctions"]

    #for page_num in range(1, num_of_pages):
    for page_num in range(1, num_of_pages):
        print('Downloading page', page_num)
        page_n = requests.get(url + 'auctions', params = {'key': api_key, 'page': page_num})
        page_json = page_n.json()
        if page_json["success"]:
            auctions_list += page_json["auctions"]
        else:
            print('error')
    print('Finished updating')
    
    return bazaar, auctions_list

if __name__ == '__main__':
    update()