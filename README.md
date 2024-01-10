# News scraper app made with Javascript and Python with NLP
![Screenshot](https://github.com/coderJT/news_scraper_with_analytics/blob/master/src/Screenshot.png) \
This project mainly consists of a scraper and a dashboard. \
The scraper is made with Selenium and BeautifulSoup, and tested on a news website https://thestar.com.my. \
The dashboard is made with React.JS and styled with Material UI. \
NLP methods: 
1. Sentiment Analysis - Made with HuggingFace transformer module
2. Summarizer - Made with Sumy's LsaSummarizer 

## Dashboard overview
1. A table of data consisting of fields (No, Title, Date, Tag/Category, Content) is displayed on the left side of the screen after data is fetched or scraped.
   
2.  Functionalities are provided and interactable through buttons in the middle part of the screen:
  - Fetch news = Fetch previously scraped news from database (mongoDB) (~1-3 seconds)
  - Scrape news = Create instance of scraper to scrape news from source (~15-20 seconds)
  - Reset news = Clear data from database (~1-3 seconds)
  - Sentiment analysis = Perform sentiment analysis on selected news article (~4-8 seconds)
  - Summarize = Perform summarizing on selected news article (~1-3 seconds)
  - Fetch news (With Tags) = Fetch previously scraped new from database according to tags
  - Scrape news (With Tags) = Scrape news from source according to tags

3. A details column on the right side of the screen then displays the following info when a news is selected:
   - Title
   - Url
   - Sentiment Analysis Result
   - Summary
   - Content

4. Limited selection of themes is added can be exposed through the sidebar.
