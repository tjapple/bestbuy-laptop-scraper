import pytest
from unittest.mock import MagicMock, patch
from deal_scraper.pipelines import SQLAlchemyPipeline
from deal_scraper.items import LaptopItem

def test_sqlalchemy_pipeline_process_item():
    # Arrane
    mock_session = MagicMock()
    pipeline = SQLAlchemyPipeline(db_url='fake', mismatch_log='fake.txt', email_config={}, batch_size=10, upc_watchlist=[])
    pipeline.session = mock_session

    item = LaptopItem(upc='123456789', price=999.99, full_price=1299.99)

    # Act
    pipeline.process_item(item, spider=None)

    # Assert
    mock_session.query.assert_called()
    mock_session.add.assert_called()


def test_send_email_alert():
    pipeline = SQLAlchemyPipeline(
        db_url='',
        mismatch_log='',
        email_config={
            'from_address': 'ex@ex.com',
            'email_password': '123',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587
        },
        batch_size=10, 
        upc_watchlist=[]
    )
    
    with patch('smtplib.SMTP') as mock_smtp:
        pipeline.send_email_alert('email@d.com', 'subject', 'body')

    mock_smtp.assert_called_with('smtp.gmail.com', 587)
