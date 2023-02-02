import re
from datetime import datetime, timedelta

import requests


class Fubotv:

    default_headers = {
        "accept":"*/*",
        "accept-encoding":"gzip, deflate, br",
        "accept-language":"ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "origin":"https://www.fubo.tv",
        "referer":"https://www.fubo.tv/",
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    }

    login_headers = {
        "accept":"*/*",
        "accept-encoding":"gzip, deflate, br",
        "accept-language":"ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "origin":"https://www.fubo.tv",
        "referer":"https://www.fubo.tv/",
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "x-client-version":"R20230127.2",
        "x-device-app":"web",
        "x-device-group":"desktop",
        "x-device-id":"zVcOFOTj00Yrd-AgZ3",
        "x-device-model":"Windows NT 10.0 Chrome 109.0.0.0",
        "x-device-platform":"desktop",
        "x-device-type":"desktop",
        "x-player-version":"1.57.4",
        "x-preferred-language":"en-US",
        "x-supported-codecs-list":"avc",
    }


    @classmethod
    def login(cls, email, passwd):
        url = "https://api.fubo.tv/signin"
        return requests.put(url, data={"email":email, "password":passwd}, headers=cls.login_headers).json()


    @classmethod
    def ch_list(cls):
        now = datetime.utcnow()
        now2 = now + timedelta(hours=1)
        url = f"https://api.fubo.tv/epg?startTime={now.year}-{str(now.month).zfill(2)}-{str(now.day).zfill(2)}T{str(now.hour).zfill(2)}%3A00%3A00.000Z&endTime={now2.year}-{str(now2.month).zfill(2)}-{str(now2.day).zfill(2)}T{str(now2.hour).zfill(2)}%3A00%3A00.000Z&enrichments=follow"
        data = requests.get(url, headers=cls.default_headers).json()
        ret = []
        for item in data['response']:
            ret.append({
                'name': item['data']['channel']['name'],
                'id': item['data']['channel']['id'],
                'current': '' if len(item['data']['programsWithAssets']) == 0 else item['data']['programsWithAssets'][0]['program']['title'],
                'logo': item['data']['channel']['logoOnWhiteUrl'],
            })
        return ret
    

    @classmethod
    def get_url(cls, token, ch_id):
        cls.default_headers["authorization"] = f"Bearer {token}"

        # 스트리밍 url 얻기
        url = f"https://api.fubo.tv/v3/kgraph/v3/networks/{ch_id}/stream"
        data = requests.get(url, headers=cls.default_headers).json()

        # master url
        url = data['streamUrls'][0]['url']
        res = requests.get(url, headers=cls.default_headers)

        # 고해상도 url 선택
        max_width = current_width = 0
        max_url = None
        for line in res.text.splitlines():
            if line.startswith('#'):
                match = re.search('RESOLUTION=(?P<width>\d+)x\d', line)
                if match:
                    current_width = int(match.group('width'))
            elif line.startswith('http'):
                if current_width > max_width:
                    max_width = current_width 
                    max_url = line

        # url에 쿠키포함
        max_url = max_url.replace('cookie_supported_platform=1', "cookie_supported_platform=0")
        return max_url
