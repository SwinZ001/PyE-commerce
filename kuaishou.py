import json

import requests

url = 'https://www.kuaishou.com/graphql'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'Cookie':'kpf=PC_WEB; kpn=KUAISHOU_VISION; clientid=3; did=web_821df3db85bd3a901667d87961f2094b; ktrace-context=1|MS43NjQ1ODM2OTgyODY2OTgyLjE2NjE1NTQyLjE2NjQ0NzM0MDc3ODQuMTkzMDg=|MS43NjQ1ODM2OTgyODY2OTgyLjIxMzM5OTkyLjE2NjQ0NzM0MDc3ODQuMTkzMDk=|0|graphql-server|webservice|false|NA; client_key=65890b29; userId=1632901381; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABaTTKJQdzDqYWmidGw4KVBhCaIeTr8Q1Q66ljzQlCMx3bV415_kvzAxXIEUXlMMge2cW4yOf6HeG-JU9p4vIT-CUJdfrmzgZEk_AYCsgihxpxIYMzp0cRMP9TjLmpJpJ77N31We3wqs-XR9T5jvRMQaKff7_rF3Se3tG0RQL1FmzhPLajetOgvZ37zwSrsqYKQgOTtYoVonaSfUF0MwG9pBoS5dGNQ2tN9j6L3QVO7fJXKiWdIiBAaPInmRNr1Q0K0mLa7AV9ZzO7bs6dlqGsc6-6OU9orygFMAE; kuaishou.server.web_ph=3788d68c0d7e8976cadee146860475eef527',
    'content-type':'application/json'
}

def get_params(keyword,i):
    params = {"operationName": "visionSearchPhoto",
              "query": "fragment photoContent on PhotoEntity {\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  __typename\n}\n\nfragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  tags {\n    type\n    name\n    __typename\n  }\n  __typename\n}\n\nquery visionSearchPhoto($keyword: String, $pcursor: String, $searchSessionId: String, $page: String, $webPageArea: String) {\n  visionSearchPhoto(keyword: $keyword, pcursor: $pcursor, searchSessionId: $searchSessionId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      ...feedContent\n      __typename\n    }\n    searchSessionId\n    pcursor\n    aladdinBanner {\n      imgUrl\n      link\n      __typename\n    }\n    __typename\n  }\n}\n",
              "variables": {"keyword":keyword, "pcursor":i, "page": "search", "searchSessionId": "MTRfMTYzMjkwMTM4MV8xNjY0NDc4OTg5NTU5X-WBh-mdoumqkeWjq180OTE5"},
              }

    return json.dumps(params)


word="假面骑士"
i = -1

while 1:
    try:
        i += 1
        print(i)
        response = requests.post(url=url, headers=headers, data=get_params(word, str(i)))

        data_obj = response.json()

        for i2 in range(0, 20):
            print(data_obj['data']['visionSearchPhoto']['feeds'][i2]['photo']['caption'])
    except:
        break

