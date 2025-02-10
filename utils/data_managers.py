import streamlit as st
import pandas as pd
import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
WATCHLIST_FILENAME = os.getenv('WATCHLIST_FILENAME')


@st.cache_data  # Caches the results to speed up re-runs
def load_data():
    """Retrieves the joined laptops and price_history tables"""   
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    query = """
    SELECT 
        L.id AS laptop_id,
        L.upc,
        L.product_name, 
        L.year_of_release,
        L.brand,
        L.operating_system,
        L.windows_ai,

        L.product_weight_lbs,
        L.battery_life_hrs,
        L.casing_material,
        L.two_in_one_design,
        L.headphone_jack, 
        L.number_of_ethernet_ports,
        L.media_card_reader,
        L.display_connectors,
        L.usb_ports,

        L.processor_model,
        L.processor_model_number,
        L.cpu_base_clock_frequency_ghz,
        L.cpu_boost_clock_frequency_ghz,
        L.number_of_cpu_cores,
        L.number_of_cpu_threads,

        L.neural_processing_unit_npu,

        L.graphics,
        L.graphics_type,

        L.system_memory_ram_gb,
        L.system_memory_ram_speed_mhz,
        L.type_of_memory_ram,

        L.storage_type, 
        L.total_storage_capacity_gb,
        L.solid_state_drive_interface,
        
        L.screen_size_inches,
        L.screen_resolution, 
        L.screen_type,
        L.display_type, 
        L.brightness,
        L.touch_screen,
        L.refresh_rate_hz, 
        


        P.timestamp,
        P.price,
        P.full_price,
        P.discount_percentage,
        P.link
    FROM "laptops" AS L
    JOIN "price_history" AS P
      ON L.id = P.laptop_id
    """
    

    full_df = pd.read_sql(query, engine)
    full_df['year_of_release'] = pd.to_numeric(full_df['year_of_release'], errors='coerce')
    full_df['timestamp'] = pd.to_datetime(full_df['timestamp'])
    
    session.close()
    engine.dispose()
    return full_df

def load_upc_watchlist(filename=WATCHLIST_FILENAME):
    """Loads the watchlist from a JSON file. Returns a list of UPC strings."""
    try:
        with open(filename, "r") as f:
            watchlist = json.load(f)
        # Make sure the data is a list
        if not isinstance(watchlist, list):
            return []
        return watchlist
    except FileNotFoundError:
        return []

def write_upc_watchlist(watchlist, filename=WATCHLIST_FILENAME):
    """Writes the watchlist (a list) back to the JSON file."""
    with open(filename, "w") as f:
        json.dump(watchlist, f, indent=4)
