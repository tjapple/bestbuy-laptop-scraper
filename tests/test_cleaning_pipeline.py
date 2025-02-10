import pytest
from deal_scraper.pipelines import CleaningPipeline
from itemadapter import ItemAdapter
from deal_scraper.items import LaptopItem

def test_extract_numeric():
    pipeline = CleaningPipeline()

    assert pipeline.extract_numeric('$999.99') == 999.99
    assert pipeline.extract_numeric('1,234') == 1234.0
    assert pipeline.extract_numeric('No digits') is None
    assert pipeline.extract_numeric('') is None

def test_standardize_key():
    pipeline = CleaningPipeline()
    assert pipeline.standardize_key('Year Of release') == 'year_of_release'
    assert pipeline.standardize_key('CPU Base Clock Frequency') == 'cpu_base_clock_frequency_ghz'
    assert pipeline.standardize_key('battery_life_up_to') == 'battery_life_hrs'


def test_process_item():
    pipeline = CleaningPipeline()
    item = LaptopItem(
        price='$1,299', 
        full_price='$1,499', 
        attributes={
            'Year Of Release':'2020', 
            'Battery Life Up to':'10', 
            'two_in_one_design':'False'
            }
        )

    result_item = pipeline.process_item(item, spider=None)
    assert result_item['price'] == 1299.0
    assert result_item['full_price'] == 1499.0
    assert result_item['dollars_off'] == 200.0
    assert result_item['discount_percentage'] == pytest.approx(13.34, 0.01)
    assert result_item['year_of_release'] == '2020'
    assert result_item['battery_life_hrs'] == 10.0
    assert isinstance(result_item['two_in_one_design'], bool)
    