import os
import sys
import asyncio
import time

from flask import Flask, jsonify
from flask_cors import CORS
from bson import json_util
from bson.objectid import ObjectId
from pymongo import UpdateOne, MongoClient
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to sys.path to ensure imports work on Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import scraper as ScraperModule
import sentiment_analysis as SentimentModule
import summarizer as SummarizerModule

# Use the classes/functions from the modules
Scraper = ScraperModule.Scraper
analyse_sentiment = SentimentModule.analyse_sentiment
lsa_summarize = SummarizerModule.lsa_summarize

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

@app.errorhandler(Exception)
def handle_exception(e):
    """Ensure all errors return JSON instead of HTML for the frontend."""
    if isinstance(e, HTTPException):
        return e
    app.logger.error(f"Unhandled Exception: {e}")
    return jsonify({"error": str(e)}), 500

# Set up logger alias for backward compatibility or use app.logger
logger = app.logger

# MongoDB connection setup - MUST be set in Vercel environment variables or local .env
MONGODB_URI = os.environ.get('MONGODB_URI')

if not MONGODB_URI or "<db_password>" in MONGODB_URI:
    app.logger.error("MONGODB_URI environment variable is not set correctly or contains placeholder!")
    # Do not fall back to a broken placeholder that causes auth errors
    if not MONGODB_URI:
        MONGODB_URI = "mongodb://localhost:27017/news_scraper"

try:
    client = MongoClient(MONGODB_URI)
    # Health check to catch auth errors early
    client.admin.command('ping')
    db = client['news_database']
    collection = db['news_collection']
except Exception as e:
    app.logger.error(f"Failed to connect to MongoDB: {e}")
    db = None
    collection = None

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
        if collection is None:
            logger.error("Database connection not established. Scraped data will not be saved.")
        elif news_scraper.articlesDetails:
            bulk_operations = [UpdateOne({"name": data['name']}, {"$set": data}, upsert=True)
                               for data in news_scraper.articlesDetails]
            collection.bulk_write(bulk_operations)
    except Exception as e:
        logger.error(f"Error updating database: {e}")
    finally:
        logger.info("(Server) Scraping process completed")
        
    # Store in memory as a fallback for analytics features
    app.last_scraped = news_scraper.articlesDetails
        
    if collection is not None:
        result = list(collection.find())
    else:
        result = news_scraper.articlesDetails
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
    if collection is None:
        return jsonify({"error": "Database connection not established"}), 503
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
    if collection is None:
        return jsonify({"error": "Database connection not established"}), 503
    result = collection.delete_many({})
    logger.info("(Server) Reset succeeded")
    return jsonify({"status": "success"})

@app.route('/api/sentimentAnalysis/<string:news_id>')
def sentiment_analysis_route(news_id):
    logger.info(f"Performing sentiment analysis for news_id: {news_id}...")
    if collection is None:
        logger.warning("Database connection is None, sentiment analysis might fail.")
        return jsonify({"error": "Database connection not established."}), 503
    try:
        target = None
        # Try finding by ObjectId
        if len(news_id) == 24: # Typical ObjectId hex length
            try:
                target = collection.find_one({"_id": ObjectId(news_id)})
            except:
                pass
        
        # Fallback: if not found by ID, try finding in the last scraped memory (for fallback-IDs)
        if not target and hasattr(app, 'last_scraped'):
            if news_id.startswith('fallback-'):
                try:
                    # The reversed list is what the frontend usually sees
                    idx = int(news_id.split('-')[1])
                    news_reversed = list(reversed(app.last_scraped))
                    if 0 <= idx < len(news_reversed):
                        target = news_reversed[idx]
                        logger.info(f"Found news item in memory fallback for {news_id}")
                except Exception as e:
                    logger.error(f"Memory fallback failed: {e}")
            
        if not target:
            logger.error(f"News item not found for ID: {news_id}")
            return jsonify({"error": "News not found in database. Try scraping again."}), 404
            
        logger.info(f"Found news item: {target.get('name', 'Unknown')}")
        result = asyncio.run(analyse_sentiment(target))
        logger.info(f"Sentiment result: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/summarize/<string:news_id>')
def summarize_route(news_id):
    logger.info(f"Performing summarizing process for content of: {news_id}...")
    if collection is None:
        return jsonify({"error": "Database connection not established."}), 503
    try:
        target = None
        if len(news_id) == 24:
            try:
                target = collection.find_one({"_id": ObjectId(news_id)})
            except:
                pass
                
        # Fallback: if not found by ID, try finding in the last scraped memory (for fallback-IDs)
        if not target and hasattr(app, 'last_scraped'):
            if news_id.startswith('fallback-'):
                try:
                    idx = int(news_id.split('-')[1])
                    news_reversed = list(reversed(app.last_scraped))
                    if 0 <= idx < len(news_reversed):
                        target = news_reversed[idx]
                        logger.info(f"Found news item in memory fallback for {news_id}")
                except Exception as e:
                    logger.error(f"Memory fallback failed: {e}")

        if not target:
            logger.error(f"News item not found for ID: {news_id}")
            return jsonify({"error": "News not found..."}), 404
            
        logger.info(f"Found news item for summary: {target.get('name', 'Unknown')}")
        result = asyncio.run(lsa_summarize(target))
        if not result:
            logger.warning("Summary returned empty string.")
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
        
    if collection is not None:
        result = list(collection.find({'tag': {'$in': tag_list}})) 
    else:
        result = [a for a in news_scraper.articlesDetails if a.get('tag') in tag_list]
        
    return app.response_class(
        response=json_util.dumps(result),
        status=200,
        mimetype='application/json'
    )

@app.route('/api/newstag=<path:tags>')
def fetch_news_with_tag(tags):
    logger.info(f"Obtaining list of scraped news with tags {tags} from database...")
    if collection is None:
        return jsonify({"error": "Database connection not established"}), 503
    tag_list = tags.split('&')
    news_data = list(collection.find({'tag': {'$in': tag_list}})) 
    return app.response_class(
        response=json_util.dumps(news_data),
        status=200,
        mimetype='application/json'
    )

# For local testing
if __name__ == '__main__':
    app.run(debug=True, port=8000)
