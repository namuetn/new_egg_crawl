import scrapy
from newegg_crawler.items import NeweggCrawlerItem
from scrapy.loader import ItemLoader
# from scrapy.loader.processors import TakeFirst
from itemloaders.processors import TakeFirst

class NeweggSpiderSpider(scrapy.Spider):
    name = "newegg_spider"
    allowed_domains = ["newegg.com"]
    # start_urls = ["https://www.newegg.com/GPUs-Video-Graphics-Cards/SubCategory/ID-48/Page-1?Tid=7709"]

    def start_requests(self):
        base_url = 'https://www.newegg.com/GPUs-Video-Graphics-Cards/SubCategory/ID-48/Page-'
        for page_num in range(1, 101):
            url = f'{base_url}{page_num}?Tid=7709'
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        vga_results = response.xpath('//*[@class="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell"]/div/div')

        for vga in vga_results:
            details_loader = ItemLoader(item=NeweggCrawlerItem(), selector=vga)
            details_loader.default_output_processor = TakeFirst()

            details_loader.add_xpath('itemId', '@id')
            details_loader.add_xpath('title', '*[@class="item-info"]/a/text()')
            details_loader.add_xpath('branding', '*[@class="item-info"]/div/a/img/@title')
            details_loader.add_xpath('rating', '*[@class="item-info"]/div/a[2]/@title')
            details_loader.add_xpath('ratingCount', '*[@class="item-info"]/div/a[2]/span/text()')
            
            # Tạo 2 biến và nối 2 biến trên để tạo thành price và add vào details_loader
            strong_value = vga.xpath('*[@class="item-action"]/ul/li[@class="price-current"]/strong/text()').extract_first()
            sup_value = vga.xpath('*[@class="item-action"]/ul/li[@class="price-current"]/sup/text()').extract_first()
            if strong_value and sup_value:
                price = strong_value + sup_value
                details_loader.add_value('price', float(price.replace(',', '')))

            details_loader.add_xpath('shipping', '*[@class="item-action"]/ul/li[@class="price-ship"]/text()')
            details_loader.add_xpath('imgUrl', 'a/img/@src')
            details_loader.add_xpath('detailUrl', '*[@class="item-info"]/a/@href')
            details_loader.add_value('productsUrl', response.url)

            product_item = details_loader.load_item()
            detail_url = product_item['detailUrl']

            # yield details_loader.load_item()
            yield scrapy.Request(detail_url, callback=self.parse_detail_page, meta={'product_item': product_item, 'dont_redirect': True, 'handle_httpstatus_list': [302]})
        
    def parse_detail_page(self, response):
        product_item = response.meta['product_item']

        details_loader = ItemLoader(item=product_item, response=response)

        product_item['detailProduct'] = {
            'maxResolution': details_loader.get_xpath('//*[@id="product-details"]/div[2]/div[table[caption[contains(., "Details")]]]/table[caption[contains(., "Details")]]/tbody/tr[th[contains(., "Max Resolution")]]/td/text()'),
            'displayPort': details_loader.get_xpath('//*[@id="product-details"]/div[2]/div[table[caption[contains(., "Ports")]]]/table[caption[contains(., "Ports")]]/tbody/tr[th[contains(., "DisplayPort")]]/td/text()'),
            'hdmi': details_loader.get_xpath('//*[@id="product-details"]/div[2]/div[table[caption[contains(., "Ports")]]]/table[caption[contains(., "Ports")]]/tbody/tr[th[contains(., "HDMI")]]/td/text()'),
            'directX': details_loader.get_xpath('//*[@id="product-details"]/div[2]/div[table[caption[contains(., "3D API")]]]/table[caption[contains(., "3D API")]]/tbody/tr[th[contains(., "DirectX")]]/td/text()'),
            'model': details_loader.get_xpath('//*[@id="product-details"]/div[2]/div[table[caption[contains(., "Model")]]]/table[caption[contains(., "Model")]]/tbody/tr[th[contains(., "Model")]]/td/text()')
        }
        # print(product_item, 333333333)
        # details_loader.add_xpath('maxResolution', '//*[@id="product-details"]/div[2]/div[2]/table[8]/tbody/tr[1]/td/text()')
        # details_loader.add_xpath('displayPort', '//*[@id="product-details"]/div[2]/div[2]/table[7]/tbody/tr[3]/td/text()')
        # details_loader.add_xpath('hdmi', '//*[@id="product-details"]/div[2]/div[2]/table[7]/tbody/tr[2]/td/text()')
        # details_loader.add_xpath('directX', '//*[@id="product-details"]/div[2]/div[2]/table[6]/tbody/tr[1]/td/text()')
        # details_loader.add_xpath('model', '//*[@id="product-details"]/div[2]/div[2]/table[2]/tbody/tr[3]/td/text()')

        yield product_item
        # yield details_loader.load_item()

