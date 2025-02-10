# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from deal_scraper.items import LaptopItem
import re
from datetime import datetime
import logging
from deal_scraper.items import FIELD_NAMES, PRICE_RECORD_KEYS, NUMERIC_KEYS, BOOL_KEYS


# Loggers
cleaning_logger = logging.getLogger('deal_scraper.pipelines.CleaningPipeline')
sqlalchemy_logger = logging.getLogger('deal_scraper.pipelines.SQLAlchemyPipeline')



class CleaningPipeline:
    """Cleans and standardizes scraped data before piping it into the database."""
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        self._extract_specs(adapter)      
        self._set_defaults_if_none(adapter)
        self._clean_boolean_fields(adapter)
        self._clean_numeric_fields(adapter)
        self._calculate_price_stats(adapter)

        return adapter.item
    
    def _extract_specs(self, adapter):
        attributes = adapter.get('attributes', {})

        # Unpack spec data from attributes dict. Store each spec in its own bin.
        for key, value in attributes.items():
            standardized_key = self.standardize_key(key)

            if standardized_key in FIELD_NAMES:

                # Standardize missing values to None
                if isinstance(value, str):
                    cleaned_value = value.strip().lower()
                    if cleaned_value == '' or 'not' in cleaned_value:
                        adapter[standardized_key] = None
                    else:
                        adapter[standardized_key] = value  

        # Remove original 'attributes' field
        del adapter['attributes'] 
    
    def _set_defaults_if_none(self, adapter):
        adapter['number_of_ethernet_ports'] = adapter.get('number_of_ethernet_ports', 0)
        adapter['media_card_reader'] = adapter.get('media_card_reader', 'false')
        adapter['two_in_one_design'] = adapter.get('two_in_one_design', 'false')
    
    def _clean_numeric_fields(self, adapter):
        for key in NUMERIC_KEYS:
            adapter[key] = self.extract_numeric(adapter.get(key))

    def _clean_boolean_fields(self, adapter):
        for key in BOOL_KEYS:
            if adapter.get(key) and adapter.get(key).lower() == 'true':
                adapter[key] = True
            else:
                adapter[key] = False

    def _calculate_price_stats(self, adapter):
        full_price = adapter.get('full_price') or 0
        price = adapter.get('price') or 0

        if full_price == 0:
            # Avoid division by zero
            adapter['dollars_off'] = 0
            adapter['discount_percentage'] = 0
        else:
            adapter['dollars_off'] = full_price - price
            adapter['discount_percentage'] = round(
                (adapter['dollars_off'] / full_price) * 100, 
                2
            )
   
    @staticmethod
    def standardize_key(key):
        """Converts display names into snake_case and handles specific naming overrides."""
        # Mapping for specific overrides
        overrides = {
            'product_weight': 'product_weight_lbs',
            'battery_life_up_to': 'battery_life_hrs',
            'manufacturers_warranty___labor': 'warranty',
            'screen_size': 'screen_size_inches',
            'refresh_rate': 'refresh_rate_hz',
            'cpu_base_clock_frequency': 'cpu_base_clock_frequency_ghz',
            'cpu_boost_clock_frequency': 'cpu_boost_clock_frequency_ghz',
            'total_storage_capacity': 'total_storage_capacity_gb',
            'system_memory_ram': 'system_memory_ram_gb',
            'system_memory_ram_speed': 'system_memory_ram_speed_mhz',
            '2_in_1_design': 'two_in_one_design'
        }

        # Normalize the key first
        standardized_key = re.sub(r'[()\']', '', re.sub(r'[\s\-]', '_', key.lower().strip()))

        return overrides.get(standardized_key, standardized_key)
    
    @staticmethod
    def extract_numeric(value):
        """Extracts the numeric value from a string."""
        if not value:  # Check if the value is None or an empty string
            return None
        # Use regex to extract the numeric part
        match = re.search(r'\d+(\.\d+)?', re.sub(',', '', value))
        return float(match.group()) if match else None
    



from deal_scraper.models import LaptopTable, PriceHistoryTable, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import smtplib
from email.message import EmailMessage
import ast
from scrapy.exceptions import DropItem
import json

class SQLAlchemyPipeline: 
    """Saves cleaned LaptopItem data into a PostgreSQL db via SQLAlchemy"""
    def __init__(self, db_url, mismatch_log, email_config, batch_size, upc_watchlist, alert_discount_threshold):
        # Store the database url
        self.db_url = db_url
        self.mismatch_log = mismatch_log
        self.email_config = email_config
        self.batch_size = batch_size
        self.upc_watchlist = upc_watchlist
        self.alert_discount_threshold = alert_discount_threshold
        self.items_to_commit = []

    @classmethod
    def from_crawler(cls, crawler):
        """Scrapy pattern that allows access to settings.py
        Pulls the db url from scrapy settings"""
        db_url = crawler.settings.get("DATABASE_URL")
        mismatch_log = crawler.settings.get("UPC_MISMATCH_LOG", "mismatch_log.txt")
        email_config = {
            "from_address": crawler.settings.get("EMAIL_FROM"),
            "to_address": crawler.settings.get("EMAIL_TO"),
            "smtp_server": crawler.settings.get("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": crawler.settings.get("SMTP_PORT", 587),
            "email_password": crawler.settings.get("EMAIL_PASSWORD"),
        }
        batch_size = crawler.settings.get("BATCH_SIZE", 100)
        alert_discount_threshold = float(crawler.settings.get("ALERT_DISCOUNT_THRESHOLD", 0))
        watchlist_filename = crawler.settings.get("WATCHLIST_FILENAME")
        upc_watchlist = cls.load_upc_watchlist(filename=watchlist_filename)
        
        return cls(db_url, mismatch_log, email_config, batch_size, upc_watchlist, alert_discount_threshold)
    
    def open_spider(self, spider):
        """Called wen spider starts.
        Create engine, sessionmaker, and create tables if they don't exist. """
        # Create an engine and a session
        if self.db_url.startswith("postgres://"):
            self.db_url = self.db_url.replace("postgres://", "postgresql://", 1)
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine) #tells sqlalchemy to create the products table
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()


    def process_item(self, item, spider):
        """Convert each Scrapy Item to a SQLAlchemy model and add it to the session."""
        adapter = ItemAdapter(item)

        # Ensure the price is numeric and make sure it's not zero
        price = adapter.get('price')
        try:
            price = float(price)
        except (TypeError, ValueError):
            price = 0.0
        if price == 0:
            raise DropItem(f"Item dropped: price is zero for UPC {adapter.get('upc')}")
        
        
        
        # 1) Check if a laptop with the same UPC already exists
        upc = adapter.get('upc')
        laptop_obj = self.session.query(LaptopTable).filter_by(upc=upc).first()

        # 2) If not found, create a new LaptopTable and PriceHistory entry
        if not laptop_obj:
            laptop_obj = self.create_new_product_entry(adapter)
            price_record = self.create_new_price_entry(laptop_obj, adapter)

            self.session.add(laptop_obj)
            self.session.add(price_record)

        else:
            # 3) Compare key specs to ensure upc code refers to same product. If not, log instance to file.
            mismatch_lines = self._check_spec_mismatches(laptop_obj, adapter)
            if mismatch_lines:
                # Update product specs (excluding price-related fields)
                for field in FIELD_NAMES:
                    if field not in PRICE_RECORD_KEYS:
                        new_val = adapter.get(field)
                        if new_val is not None:
                            setattr(laptop_obj, field, new_val)
                # Add laptop_obj to session
                self.session.add(laptop_obj)

                sqlalchemy_logger.warning(f'mismatches found for upc {upc}: {mismatch_lines}')
                with open(self.mismatch_log, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().isoformat()}] UPC={upc}, Link={adapter.get('link', '')}\n")
                    for line in mismatch_lines:
                        f.write(f"  - {line}\n")
                    f.write("\n")


            # 4) Create only a PriceHistory entry because product info already exists in database
            price_record = self.create_new_price_entry(laptop_obj, adapter)
            self.session.add(price_record)

        # Batch commit
        self.items_to_commit.append(item)
        if len(self.items_to_commit) >= self.batch_size:
            self.commit_batch(spider)
   
        # Email alert for watchlist    
        self.check_and_alert(item)
        return item
    
    def create_new_price_entry(self, laptop_obj, adapter):
        data_for_price_history = {}
        for field in PRICE_RECORD_KEYS:
            data_for_price_history[field] = adapter.get(field)

        price_record = PriceHistoryTable(
            laptop = laptop_obj, 
            **data_for_price_history
        )
        return price_record

    def create_new_product_entry(self, adapter):
        data_for_product_entry = {}
        for field in FIELD_NAMES:
            if field not in PRICE_RECORD_KEYS and field != 'attributes':
                data_for_product_entry[field] = adapter.get(field)
        
        laptop_obj = LaptopTable(
            **data_for_product_entry
        )
        return laptop_obj

    def commit_batch(self, spider):
        """Commit the current batch of items to the database."""
        try: 
            self.session.commit()
            sqlalchemy_logger.info(f'batch of length {len(self.items_to_commit)}committed successfully')
            self.items_to_commit = []
        except Exception as e:
            self.session.rollback()
            sqlalchemy_logger.error(f'batch failed to commit: {e}')
        
    def close_spider(self, spider):
        """Called when spider closes.
        Clean up the sesion/enginge. """
        if self.items_to_commit:
            self.commit_batch(spider)
        self.session.close()

    def _check_spec_mismatches(self, db_obj, adapter):
        mismatch_lines = []

        # CPU
        db_cpu = db_obj.processor_model
        new_cpu = adapter.get('processor_model')
        if new_cpu and db_cpu and new_cpu.lower().strip() != db_cpu.lower().strip():
            mismatch_lines.append(f"CPU mismatch: DB='{db_cpu}', New='{new_cpu}'")

        # GPU
        db_gpu = db_obj.graphics
        new_gpu = adapter.get('graphics')
        if new_gpu and db_gpu and new_gpu.lower().strip() != db_gpu.lower().strip():
            mismatch_lines.append(f"GPU mismatch: DB='{db_gpu}', New='{new_gpu}'")

        # RAM
        db_ram = db_obj.system_memory_ram_gb
        new_ram = adapter.get('system_memory_ram_gb')
        if new_ram is not None and db_ram is not None and abs(new_ram - db_ram) > 0.01:
            mismatch_lines.append(f"RAM mismatch: DB={db_ram} GB, New={new_ram} GB")

        # Storage
        db_storage = db_obj.total_storage_capacity_gb
        new_storage = adapter.get('total_storage_capacity_gb')
        if new_storage is not None and db_storage is not None and abs(new_storage - db_storage) > 1:
            mismatch_lines.append(f"Storage mismatch: DB={db_storage} GB, New={new_storage} GB")

        return mismatch_lines

    def send_email_alert(self, to_address, subject, body):
        """Sends an email alert using SMTP."""
        try:
            msg = EmailMessage()
            msg.set_content(body)  
            msg['Subject'] = subject
            msg['From'] = self.email_config["from_address"]
            msg['To'] = to_address

            
            with smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"]) as server:
                server.starttls()
                server.login(self.email_config["from_address"], self.email_config["email_password"])
                server.send_message(msg)
        except Exception as e:
            sqlalchemy_logger.error(f'Failed to send email alert:{e}', exc_info=True)
    
    def check_and_alert(self, adapter):

        """Checks conditions and sends an alert if necessary."""
        discount = adapter.get('discount_percentage')
        upc = adapter.get('upc')
        if upc in self.upc_watchlist:
            if discount is not None and float(discount) >= self.alert_discount_threshold:
                subject = "Scrape Alert"
                body = (
                    f"Check out {adapter.get('link')}\n"
                    f"Price is {adapter.get('price')}\n"
                    f"A {discount}% discount\n"
                    f"Discount percentage alert threshold: {self.alert_discount_threshold}"
                )
                self.send_email_alert(self.email_config["to_address"], subject, body)

    @classmethod
    def load_upc_watchlist(cls, filename):
        """Loads the watchlist from a JSON file. Returns a list of UPC strings."""
        try:
            with open(filename, "r") as f:
                watchlist = json.load(f)
            if not isinstance(watchlist, list):
                return []
            return watchlist
        except FileNotFoundError:
            return []