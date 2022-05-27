import json

import aiohttp


def chunkify(items, chunk_size):
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]


async def get_fox():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://some-random-api.ml/img/fox') as response:
            jsn = await response.text()
            url = json.loads(jsn)['link']
        async with session.get(url) as response:
            img = await response.read()
            return img
            # print("Status:", response.status)
            # print("Content-type:", response.headers['content-type'])
            # print("Body:", html[:15], "...")

            # html = await response.text()



# def cat(vk, user_id):
#     img = urllib.request.urlopen('https://thiscatdoesnotexist.com/').read()
#     save_photo(vk, user_id, img)
#
#
# def fox(vk, user_id):
#     response = requests.get('https://some-random-api.ml/img/fox')  # Get-запрос
#     img = urllib.request.urlopen(json.loads(response.text)['link']).read()
#     save_photo(vk, user_id, img)
