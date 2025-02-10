# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LaptopItem(scrapy.Item):
    product_name = scrapy.Field()
    upc = scrapy.Field()
    link = scrapy.Field()
    timestamp = scrapy.Field()
    attributes = scrapy.Field()

    # Price data
    price = scrapy.Field()
    full_price = scrapy.Field()
    dollars_off = scrapy.Field()
    discount_percentage = scrapy.Field()
    
    # General
    brand = scrapy.Field()
    color = scrapy.Field()
    year_of_release = scrapy.Field()
    operating_system = scrapy.Field()
    windows_ai = scrapy.Field() 
    product_weight_lbs = scrapy.Field()  
    casing_material = scrapy.Field() 
    battery_life_hrs = scrapy.Field() 
    backlit_keyboard = scrapy.Field()
    wireless_networking_standard = scrapy.Field()
    audio_technology = scrapy.Field()
    security_features = scrapy.Field() #TODO: not sure, maybe leave alone and not worth filtering for
    warranty = scrapy.Field() 
    two_in_one_design = scrapy.Field()

    # Display
    screen_type = scrapy.Field()
    display_type = scrapy.Field()
    screen_resolution = scrapy.Field()
    brightness = scrapy.Field() 
    screen_size_inches = scrapy.Field()
    touch_screen = scrapy.Field()
    refresh_rate_hz = scrapy.Field()
    
    # GPU
    graphics = scrapy.Field()
    graphics_type = scrapy.Field()

    # CPU
    processor_model = scrapy.Field()
    processor_model_number = scrapy.Field()
    cpu_base_clock_frequency_ghz = scrapy.Field() 
    cpu_boost_clock_frequency_ghz = scrapy.Field() 
    number_of_cpu_cores = scrapy.Field() 
    number_of_cpu_threads = scrapy.Field()

    # NPU
    neural_processing_unit_npu = scrapy.Field()

    # Peripherals
    headphone_jack = scrapy.Field()
    number_of_ethernet_ports = scrapy.Field() 
    media_card_reader = scrapy.Field()
    display_connectors = scrapy.Field() #TODO: parse out connector types and versions. Will prolly have to make a few more data fields. 
    usb_ports = scrapy.Field() #TODO: parse out the usb types somehow so you could filter based on version

    # Storage
    storage_type = scrapy.Field()
    total_storage_capacity_gb = scrapy.Field() 
    solid_state_drive_interface = scrapy.Field()

    # Memory
    system_memory_ram_gb = scrapy.Field()
    type_of_memory_ram = scrapy.Field() 
    system_memory_ram_speed_mhz = scrapy.Field()
    
#####################################################    
# Field name constants
#####################################################
FIELD_NAMES = list(LaptopItem.fields.keys())

PRICE_RECORD_KEYS = [
    'price',
    'full_price',
    'dollars_off',
    'discount_percentage',
    'link',
    'timestamp'
]
               
NUMERIC_KEYS = [
    'price',
    'full_price',
    'product_weight_lbs',
    'battery_life_hrs',
    'brightness',
    'screen_size_inches',
    'refresh_rate_hz',
    'cpu_base_clock_frequency_ghz',
    'cpu_boost_clock_frequency_ghz',
    'number_of_cpu_cores',
    'total_storage_capacity_gb',
    'system_memory_ram_gb',
    'system_memory_ram_speed_mhz'
]
BOOL_KEYS = [
    'backlit_keyboard', 
    'two_in_one_design', 
    'touch_screen', 
    'neural_processing_unit_npu', 
    'headphone_jack', 
    'media_card_reader'
    ]
    


    # could set up separate classes for each product type and have 
    # it inherit from ProductItem.
    
