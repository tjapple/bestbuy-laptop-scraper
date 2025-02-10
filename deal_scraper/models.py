from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class LaptopTable(Base):
    __tablename__ = "laptops"

    id = Column(Integer, primary_key=True, autoincrement=True)
    upc = Column(String, unique=True, nullable=False)

    product_name = Column(String)
    

    # General specs
    brand = Column(String)
    color = Column(String)
    year_of_release = Column(String)
    operating_system = Column(String)
    windows_ai = Column(String)
    product_weight_lbs = Column(Float)
    casing_material = Column(String)
    battery_life_hrs = Column(Float)
    backlit_keyboard = Column(Boolean)
    wireless_networking_standard = Column(String)
    audio_technology = Column(String)
    security_features = Column(String)
    warranty = Column(String)
    two_in_one_design = Column(Boolean)

    # Display
    screen_type = Column(String)
    display_type = Column(String)
    screen_resolution = Column(String)
    brightness = Column(Float)
    screen_size_inches = Column(Float)
    touch_screen = Column(Boolean)
    refresh_rate_hz = Column(Float)

    # GPU
    graphics = Column(String)
    graphics_type = Column(String)

    # CPU
    processor_model = Column(String)
    processor_model_number = Column(String)
    cpu_base_clock_frequency_ghz = Column(Float)
    cpu_boost_clock_frequency_ghz = Column(Float)
    number_of_cpu_cores = Column(Integer)
    number_of_cpu_threads = Column(Integer)

    # NPU
    neural_processing_unit_npu = Column(Boolean)

    # Peripherals
    headphone_jack = Column(Boolean)
    number_of_ethernet_ports = Column(Integer)
    media_card_reader = Column(Boolean)
    display_connectors = Column(String)
    usb_ports = Column(String)

    # Storage
    storage_type = Column(String)
    total_storage_capacity_gb = Column(Float)
    solid_state_drive_interface = Column(String)

    # Memory
    system_memory_ram_gb = Column(Float)
    type_of_memory_ram = Column(String)
    system_memory_ram_speed_mhz = Column(Float)


    # Relationsip to price history rows
    price_history = relationship("PriceHistoryTable", back_populates="laptop")


class PriceHistoryTable(Base):
    __tablename__ = 'price_history'
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to the laptops table
    laptop_id = Column(Integer, ForeignKey('laptops.id'), nullable=False)
    laptop = relationship("LaptopTable", back_populates="price_history")

   
    # Price data
    price = Column(Float)
    full_price = Column(Float)
    dollars_off = Column(Float)
    discount_percentage = Column(Float)
    link = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())