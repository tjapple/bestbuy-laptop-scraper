import scrapy
from deal_scraper.items import LaptopItem
from datetime import datetime
import json
import logging

spider_logger = logging.getLogger('deal_scraper.spiders.bestbuy_spider.BestBuySpider')


class BestBuySpider(scrapy.Spider):
    name = "bestbuy_spider"
    allowed_domains = ["bestbuy.com"]
    start_urls = ["https://www.bestbuy.com/site/laptop-computers/all-laptops/pcmcat138500050001.c?id=pcmcat138500050001"]

    def parse(self, response):
        # Find the individual product pages and callback with parse_product()
        product_page_links = response.css('a.image-link::attr(href)').getall()
        spider_logger.info(f'product page links: {product_page_links}')
        yield from response.follow_all(product_page_links, self.parse_product)


        # Find the next search pages 
        pagination_links = response.css('a.sku-list-page-next::attr(href)').getall()
        spider_logger.info(f'pagination links: {pagination_links}')
        yield from response.follow_all(pagination_links, self.parse)


    def parse_product(self, response):
        # If item is sold out, skip 
        product_stock = response.css('button.add-to-cart-button::attr(data-button-state)').get()
        if product_stock == 'SOLD_OUT':
            return
        
        # Locate <script> tags and find the one that contains spec data
        scripts = response.css('script::text').getall()
        specifications_json = None
        for script in scripts:
            if "shop-specifications-" in script:
                specifications_json = script
                break

        if specifications_json:
            try:
                data = json.loads(specifications_json)
                specifications = data.get("specifications", {}).get("categories", [])

                item = LaptopItem()
                item['price'] = response.css('div.priceView-hero-price span[aria-hidden="true"]::text').get(default='0')
                item['full_price'] =  response.css('div[data-testid="regular-price"] span[aria-hidden="true"]::text').get(item['price'])
                item['link'] = response.url
                item['timestamp'] = datetime.now().isoformat()

                # Unpack the spec data and structure in key-value pairs
                attributes = {}
                for spec_category in specifications:
                    for spec in spec_category.get("specifications", []):
                        spec_name = spec.get("displayName", "Unknown")
                        spec_value = spec.get("value", "N/A")
                        attributes[spec_name] = spec_value

                item['attributes'] = attributes
                yield item

            except json.JSONDecodeError:
                spider_logger.error("Failed to decode JSON from the specifications script.")
        
        
        else:
            spider_logger.error("Specifications JSON not found on the BestBuy html.")