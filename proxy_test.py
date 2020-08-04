import requests
import random
import settings



def get_random_proxy():
    proxies = settings.PROXY_LIST
    secure_random = random.SystemRandom()
    return secure_random.choice(proxies)


#url = 'https://www.priceguide.cards/en'
#proxies = {
#    "http": 'http://81.171.24.199:3128',
#    "https": 'http://81.171.24.199:3128'
#}
#response = requests.get(url,proxies=proxies)
#print(response)

print(get_random_proxy())