import requests
import pymongo
import schedule


def get_status(url, proxies, timeout):
    header = {
        'user-agent': 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
    }
    c = requests.get(url=url, headers=header, proxies=proxies, timeout=timeout)
    code = c.status_code
    return code

def get_proxies():
    client = pymongo.MongoClient(host='120.79.162.44', port=10086)
    client.admin.authenticate("Leo", "fwwb123456")
    db = client.fwwb
    find_ip = db.boss_ip
    data = find_ip.find()
    return data, find_ip

def main():
    url = "https://www.zhipin.com/job_detail/1415544969.html"
    data = get_proxies()[0]
    find_ip = get_proxies()[1]
    for d in data:
        if d['ip'][0:5] == 'https':
            proxies = {'https': d['ip']}
        else:
            proxies = {'http': d['ip']}
        try:
            if get_status(url=url, proxies=proxies, timeout=20) == 200:
                print('有效ip:%s' % str(d['ip']))
            else:
                find_ip.remove({'ip': d['ip']})
                print('失效ip:%s' % str(d['ip']))
        except Exception as err:
            find_ip.remove({'ip': d['ip']})
            print('失效ip:%s' % str(d['ip']))
            print(err)


if __name__ == "__main__":
    main()
    schedule.every(6).minutes.do(main)
    while True:
        schedule.run_pending()