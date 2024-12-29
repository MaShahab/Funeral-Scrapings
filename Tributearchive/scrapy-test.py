import scrapy, json

class quoteSpider(scrapy.Spider):
    name = 'Practice'

    start_urls = ['https://www.tributearchive.com/funeral-homes/area/usa/alabama']

    def parse(self,response):
        print('////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////')
        headers = {
    'authority': 'scrapingclub.com',
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.tributearchive.com/funeral-homes/area/usa/alabama',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': '__cfduid=d69d9664405f96c6477078a5c1fa78bb41613195439; _ga=GA1.2.523835360.1613195440; _gid=GA1.2.1763722170.1613195440',
}

        yield scrapy.Request('https://www.tributearchive.com/funeral-homes/area/usa/alabama',
                             callback = self.parse_detail, headers=headers)

    def parse_detail(self, response):

        product = {}

        data = response
        print(json.loads(response.body))

        # data = json.loads(response.body)
        # yield data

        # product['product_name'] = data['title']
        # product['detail'] = data['description']
        # product['price'] = data['price']
        # yield product