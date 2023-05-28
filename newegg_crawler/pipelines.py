# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re
import json
import mysql.connector
from itemadapter import ItemAdapter


class convertStringRating(object):
    def process_item(self, item, spider):
        try:
            if item['rating']:
                item['rating'] = item['rating'].split(' ')[-1]
                item['rating'] = float(item['rating'])
            else:
                item['rating'] = None
        except:
            item['rating'] = None

        return item
        
class convertStringRatingCount(object):
    def process_item(self, item, spider):
        try:
            if item['ratingCount'] and re.match(r'\(\d+\)', item['ratingCount']):
                item['ratingCount'] = int(re.sub(r'\D', '', item['ratingCount']))
            else:
                item['ratingCount'] = None
        except:
            item['ratingCount'] = None

        return item

class mysqlPipeline(object):
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',
            database='newegg'
        )

        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                itemId VARCHAR(255),
                title VARCHAR(255),
                branding VARCHAR(255),
                rating DECIMAL(2, 1),
                ratingCount INT,
                price DECIMAL(6,2),
                shipping VARCHAR(255),
                imgUrl VARCHAR(255),
                productsUrl VARCHAR(255),
                detailUrl VARCHAR(255),
                detailProduct JSON
            )
        ''')
    
    def process_item(self, item, spider):
        query = ''' 
            INSERT INTO products (itemId, title, branding, rating, ratingCount, price, shipping, imgUrl, productsUrl, detailUrl, detailProduct)
            VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''

        values = (
            item.get('itemId'),
            item.get('title'),
            item.get('branding'),
            item.get('rating'),
            item.get('ratingCount'),
            item.get('price'),
            item.get('shipping'),
            item.get('imgUrl'),
            item.get('productsUrl'),
            item.get('detailUrl'),
            json.dumps({
                'model': item.get('detailProduct')['model'],
                'directX': item.get('detailProduct')['directX'],
                'displayPort': item.get('detailProduct')['displayPort'],
                'hdmi': item.get('detailProduct')['hdmi'],
                'maxResolution': item.get('detailProduct')['maxResolution'],
            })
        )

        self.cursor.execute(query, values)
        self.conn.commit()

        return item
