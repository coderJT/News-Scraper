import os
import logging
import asyncio
import time

from flask import Flask, jsonify
from flask_cors import CORS
from bson import json_util
from bson.objectid import ObjectId
from pymongo import UpdateOne, MongoClient

# Import our helper modules
import scraper as ScraperModule
import sentiment_analysis as SentimentModule
import summarizer as SummarizerModule

# Use the classes/functions from the modules
Scraper = ScraperModule.Scraper
analyse_sentiment = SentimentModule.analyse_sentiment
lsa_summarize = SummarizerModule.lsa_summarize

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection setup - MUST be set in Vercel environment variables
MONGODB_URI = os.environ.get('MONGODB_URI')

if not MONGODB_URI:
    # During local development, you can use a .env file or export the variable
    logger.error("MONGODB_URI environment variable is not set!")
    # Fallback to a placeholder for the user to see what's expected
    MONGODB_URI = "mongodb+srv://justin:<db_password>@products.a2ruu.mongodb.net/?appName=Products"

client = MongoClient(MONGODB_URI)
db = client['news_database']
collection = db['news_collection']

# Links to be scraped
URL = 'https://www.thestar.com.my'
URL_WITH_TAG = 'https://www.thestar.com.my/news/latest?tag='

# Handle routing 
@app.route('/api/scrape')
def server_scrape_news():
    start = time.time()
    logger.info("(Server) Scraping news (All news)...")
    news_scraper = Scraper(url=URL, urlWithTag=URL_WITH_TAG)
    news_scraper.get_article_to_scrape()
    news_scraper.thread_scrape_details()
    
    try: 
        logger.info("(Server) Update database with scraped data...")
        if news_scraper.articlesDetails:
            bulk_operations = [UpdateOne({"name": data['name']}, {"$set": data}, upsert=True)
                               for data in news_scraper.articlesDetails]
            collection.bulk_write(bulk_operations)
    except Exception as e:
        logger.error(f"Error updating database: {e}")
    finally:
        logger.info("(Server) Scraping process completed")
        
    result = list(collection.find())
    end = time.time()
    logger.info(f"Total time: {end - start:.4f} seconds")
    return app.response_class(
        response=json_util.dumps(result),
        status=200,
        mimetype='application/json'
    )

@app.route('/api/news')
def server_fetch_news():
    logger.info("(Server) Obtaining list of scraped news from database...")
    try:
        result = list(collection.find())
        return app.response_class(
            response=json_util.dumps(result),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset')
def server_reset_news():
    logger.info("(Server) Resetting...")
    result = collection.delete_many({})
    logger.info("(Server) Reset succeeded")
    return jsonify({"status": "success"})

@app.route('/api/sentimentAnalysis/<string:news_id>')
def sentiment_analysis_route(news_id):
    logger.info(f"Performing sentiment analysis for news_id: {news_id}...")
    try:
        target = collection.find_one({"_id": ObjectId(news_id)})
        if not target:
            return jsonify({"error": "News not found..."}), 404
        result = asyncio.run(analyse_sentiment(target))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/summarize/<string:news_id>')
def summarize_route(news_id):
    logger.info(f"Performing summarizing process for content of: {news_id}...")
    try:
        target = collection.find_one({"_id": ObjectId(news_id)})
        if not target:
            return jsonify({"error": "News not found..."}), 404
        result = asyncio.run(lsa_summarize(target))
        return result
    except Exception as e:
        logger.error(f"Error in summarization: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/scrapetag=<path:tags>')
def get_scraped_data_by_tag(tags):
    logger.info(f"Scraping news by tag {tags}...")
    tag_list = tags.split('&')
    news_scraper = Scraper(url=URL, urlWithTag=URL_WITH_TAG, tags=tag_list)
    news_scraper.get_articles_to_scrape_by_tag()
    news_scraper.thread_scrape_details()
    
    try: 
        logger.info("(Server) Update database with scraped data...")
        if news_scraper.articlesDetails:
            bulk_operations = [UpdateOne({"name": data['name']}, {"$set": data}, upsert=True)
                               for data in news_scraper.articlesDetails]
            collection.bulk_write(bulk_operations)
    except Exception as e:
        logger.error(f"Error updating database: {e}")
    finally:
        logger.info("(Server) Scraping process completed")
        
    result = list(collection.find({'tag': {'$in': tag_list}})) 
    return app.response_class(
        response=json_util.dumps(result),
        status=200,
        mimetype='application/json'
    )

@app.route('/api/newstag=<path:tags>')
def fetch_news_with_tag(tags):
    logger.info(f"Obtaining list of scraped news with tags {tags} from database...")
    tag_list = tags.split('&')
    news_data = list(collection.find({'tag': {'$in': tag_list}})) 
    return app.response_class(
        response=json_util.dumps(news_data),
        status=200,
        mimetype='application/json'
    )

# For local testing
if __name__ == '__main__':
    app.run(debug=True)
