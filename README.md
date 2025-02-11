# BestBuy Laptop Scraper
A Scrapy + PostgreSQL project that retrieves laptop product data from BestBuy.com and stores it in a database. Price data for specific laptop models are stored based on unique UPC codes. A Streamlit app is used to explore patterns in the current laptop listing using 
various specifications. Historical price movements and discounts can also be investigated.

I have deployed a version using Docker and Heroku, which anyone can view to explore the data: https://bestbuy-laptop-scraper-e5de86899165.herokuapp.com/ 

Cloning and running the project locally will allow for creating a UPC watchlist and setting up an email alert system that will trigger if the discount amount crosses a set threshold on any of your watchlist items. 



## Instalation
1. Clone the Repo:
```python
git clone https://github.com/tjapple/bestbuy-laptop-scraper.git
cd bestbuy-laptop-scraper
```
2. Create Environment:
```python
conda env create -f environment.yml -n myenv
conda activate myenv
```
3. Create a .env based on .env.example. You will need to set filepaths, email information, alert threshold, and database connection. 

## Usage
1. Running the Scraper:
```python
scrapy crawl bestbuy_spider
```
*This will fetch product information and store it in your configured database. 

2. Running the Streamlit App:
```python
streamlit run Laptop_Explorer_App.py
```
* The main page provides interactive filters for specifications and data visualization charts.
* The watchlist page provides historical prices for watchlist items. You can add/remove UPC codes here, or modify the list in your upc_watchlist.json file. 



## Future Improvements
* Open Box Deals: add scraping logic to retrieve open box prices.
* More Sites: add spiders to scrape more sites.
* User Accounts: possibly create a public site with individual accounts and watchlists.
* Parse Ports: add logic to create data fields for USB, media, and hdmi ports.
  
