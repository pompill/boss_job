import requests
from lxml import etree
import pymongo

client = pymongo.MongoClient(host='120.79.162.44', port=10086)
client.admin.authenticate("Leo", "fwwb123456")
boss_job = client["fwwb"]
boss_city_code = boss_job["boss_city_code"]


def gethtml(url, ip):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 ('
                            'KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
              'referer': 'https://www.zhipin.com/c101010100/h_101010100/?query=%E5%A4%A7%E6%95%B0%E6%8D%AE'}
    html = requests.get(url=url, headers=header, proxies=ip).content.decode('utf-8')
    return html


def getcode_num(html):
    selector = etree.HTML(html)
    href = selector.xpath('//ul[@class="cur"]/li/a/@href')
    print(href)
    # for h in href:
    #     city = h[2:-1]
    #     data = {'city': city}
    #     boss_city_code.insert(data)

if __name__ == "__main__":
    start_url = "https://www.zhipin.com/"
    ip = {'http': 'http://114.100.188.66:13656'}
    html1 = gethtml(start_url, ip=ip)
    getcode_num(html1)
