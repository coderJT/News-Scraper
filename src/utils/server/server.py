import logging
import asyncio
import time

from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from bson import json_util
from bson.objectid import ObjectId
from pymongo import UpdateOne, MongoClient

from scraper.scraper import Scraper
from sentiment_analysis.sentiment_analysis_vader import analyse_sentiment
from summarizer.summarizer import lsa_summarize

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection setup
client = MongoClient('mongodb+srv://justin:Gls6XqWMldsOq7wY@cluster0.b4gf6nx.mongodb.net/?retryWrites=true&w=majority')
db = client['news_database']
collection = db['news_collection']

# Links to be scraped
URL = 'https://www.thestar.com.my'
URL_WITH_TAG = 'https://www.thestar.com.my/news/latest?tag='

# Handle routing 
@app.route('/api/scrape')
@cross_origin()
def server_scrape_news():
    start = time.time()
    logger.info("(Server) Scraping news (All news)...")
    news_scraper = Scraper(url=URL, urlWithTag=URL_WITH_TAG)
    news_scraper.setup_driver()
    end = time.time()
    logger.info(f"Driver setup: {end - start:.4f} seconds")
    news_scraper.get_article_to_scrape()
    end = time.time()
    logger.info(f"Getting articles to scrape: {end - start:.4f} seconds")
    news_scraper.thread_scrape_details()
    end = time.time()
    logger.info(f"Scraped all articles: {end - start:.4f} seconds")
    try: 
        logger.info("(Server) Update database with scraped data...")
        bulk_operations = [UpdateOne({"name": data['name']}, {"$set": data}, upsert=True)
                           for data in news_scraper.articlesDetails]
        collection.bulk_write(bulk_operations)
    finally:
        logger.info("(Server) Scraping process completed")
        news_scraper.tear_down()
    result = list(collection.find())
    end = time.time()
    logger.info(f"{end - start:.4f} seconds")
    return json_util.dumps(result)

@app.route('/api/news')
@cross_origin()
def server_fetch_news():
    logger.info("(Server) Obtaining list of scraped news from database...")
    result = list(collection.find())
    return json_util.dumps(result)

@app.route('/api/reset')
@cross_origin()
def server_reset_news():
    logger.info("(Server) Resetting...")
    result = collection.delete_many({})
    logger.info("(Server) Reset successed")
    return {}

@app.route('/api/sentimentAnalysis/<string:news_id>')
@cross_origin()
def sentiment_analysis(news_id):
    logger.info(f"Performing sentiment analysis for news_id: {news_id}...")
    target = collection.find_one({"_id": ObjectId(news_id)})
    if not target:
        return jsonify({"error": "News not found..."}), 404
    result = asyncio.run(analyse_sentiment(target))
    return result

@app.route('/api/summarize/<string:news_id>')
@cross_origin()
def summarize(news_id):
    logger.info(f"Performing summarizing process for content of: {news_id}...")
    target = collection.find_one({"_id": ObjectId(news_id)})
    if not target:
        return jsonify({"error": "News not found..."}), 404
    result = asyncio.run(lsa_summarize(target))
    return result

@app.route('/api/scrapetag=<path:tags>')
@cross_origin()
def get_scraped_data_by_tag(tags):
    logger.info(f"Scraping news by tag {tags}...")
    tag_list = tags.split('&')
    news_scraper = Scraper(url=URL, urlWithTag=URL_WITH_TAG, tags=tag_list)
    news_scraper.setup_driver()
    news_scraper.get_articles_to_scrape_by_tag()
    news_scraper.thread_scrape_details()
    try: 
        logger.info("(Server) Update database with scraped data...")
        bulk_operations = [UpdateOne({"name": data['name']}, {"$set": data}, upsert=True)
                           for data in news_scraper.articlesDetails]
        collection.bulk_write(bulk_operations)
    finally:
        logger.info("(Server) Scraping process completed")
        news_scraper.tear_down()
    result = list(collection.find({'tag': {'$in': tag_list}})) 
    return json_util.dumps(result)

@app.route('/api/newstag=<path:tags>')
@cross_origin()
def fetch_news_with_tag(tags):
    logger.info(f"Obtaining list of scraped news with tags {tags} from database...")
    tag_list = tags.split('&')
    news_data = list(collection.find({'tag': {'$in': tag_list}})) 
    news_data = json_util.dumps(news_data)
    return news_data

if __name__ == '__main__':
    app.run()







