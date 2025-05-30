### ecommerce_pipeline/components/web_scraping.py
from typing import NamedTuple
import json

def web_scraping_component(
    domains_json: str = '["rowingblazers.com"]',
    db_host: str = 'localhost',
    db_user: str = 'root',
    db_password: str = '',
    db_name: str = 'ecommerce_data'
) -> NamedTuple('Outputs', [('scraping_status', str), ('products_scraped', str)]):
    from bs4 import BeautifulSoup
    import mysql.connector
    import requests
    from datetime import datetime
    import logging
    import json
    from typing import NamedTuple

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def clean_html(html):
        return BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)

    def safe_get(obj, *keys, default=None):
        for key in keys:
            obj = obj.get(key) if isinstance(obj, dict) else None
            if obj is None:
                return default
        return obj

    def parse_datetime(dt_str):
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return None

    def insert_variant(cursor, product, variant, product_image, variant_image):
        query = """
        INSERT INTO shopify_products_variants (
            product_id, title, handle, description, vendor, product_type, tags,
            published_at, created_at, updated_at,
            variant_id, variant_title, option1, option2, option3, sku, requires_shipping,
            taxable, available, price, compare_at_price, grams,
            variant_created_at, variant_updated_at,
            variant_featured_image_url, variant_featured_image_width, variant_featured_image_height,
            product_main_image_url, product_main_image_width, product_main_image_height,
            option_color, option_size
        ) VALUES (
            %(product_id)s, %(title)s, %(handle)s, %(description)s, %(vendor)s, %(product_type)s, %(tags)s,
            %(published_at)s, %(created_at)s, %(updated_at)s,
            %(variant_id)s, %(variant_title)s, %(option1)s, %(option2)s, %(option3)s, %(sku)s, %(requires_shipping)s,
            %(taxable)s, %(available)s, %(price)s, %(compare_at_price)s, %(grams)s,
            %(variant_created_at)s, %(variant_updated_at)s,
            %(variant_featured_image_url)s, %(variant_featured_image_width)s, %(variant_featured_image_height)s,
            %(product_main_image_url)s, %(product_main_image_width)s, %(product_main_image_height)s,
            %(option_color)s, %(option_size)s
        )
        ON DUPLICATE KEY UPDATE variant_updated_at=VALUES(variant_updated_at), price=VALUES(price), available=VALUES(available);
        """

        data = {
            'product_id': product.get('id'),
            'title': product.get('title'),
            'handle': product.get('handle'),
            'description': clean_html(product.get('body_html', '')),
            'vendor': product.get('vendor'),
            'product_type': product.get('product_type'),
            'tags': json.dumps(product.get('tags', [])),
            'published_at': parse_datetime(product.get('published_at')),
            'created_at': parse_datetime(product.get('created_at')),
            'updated_at': parse_datetime(product.get('updated_at')),

            'variant_id': variant.get('id'),
            'variant_title': variant.get('title'),
            'option1': variant.get('option1'),
            'option2': variant.get('option2'),
            'option3': variant.get('option3'),
            'sku': variant.get('sku'),
            'requires_shipping': variant.get('requires_shipping'),
            'taxable': variant.get('taxable'),
            'available': variant.get('available'),
            'price': float(variant.get('price')) if variant.get('price') else None,
            'compare_at_price': float(variant.get('compare_at_price')) if variant.get('compare_at_price') else None,
            'grams': variant.get('grams'),
            'variant_created_at': parse_datetime(variant.get('created_at')),
            'variant_updated_at': parse_datetime(variant.get('updated_at')),

            'variant_featured_image_url': safe_get(variant_image, 'src'),
            'variant_featured_image_width': safe_get(variant_image, 'width'),
            'variant_featured_image_height': safe_get(variant_image, 'height'),

            'product_main_image_url': safe_get(product_image, 'src'),
            'product_main_image_width': safe_get(product_image, 'width'),
            'product_main_image_height': safe_get(product_image, 'height'),

            'option_color': variant.get('option1'),
            'option_size': variant.get('option2')
        }

        cursor.execute(query, data)

    def scrape_and_insert(domain, conn):
        page = 1
        cursor = conn.cursor()
        total_products = 0
        while True:
            try:
                response = requests.get(f"https://{domain}/products.json?page={page}", timeout=30)
                if response.status_code != 200:
                    break
                data = response.json().get('products', [])
                if not data:
                    break
                for product in data:
                    product_image = product.get('images', [{}])[0] if product.get('images') else {}
                    for variant in product.get('variants', []):
                        variant_image = variant.get('featured_image', {}) or {}
                        insert_variant(cursor, product, variant, product_image, variant_image)
                        total_products += 1
                page += 1
            except Exception as e:
                break
        conn.commit()
        cursor.close()
        return total_products

    domains = json.loads(domains_json)
    total_scraped = 0
    success = []
    fail = []
    try:
        conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        for domain in domains:
            try:
                count = scrape_and_insert(domain, conn)
                total_scraped += count
                success.append(domain)
            except:
                fail.append(domain)
        conn.close()
        return json.dumps({'status': 'done', 'ok': success, 'fail': fail}), str(total_scraped)
    except Exception as e:
        return json.dumps({'status': 'error', 'error': str(e)}), "0"
