import { createContext, useContext, useState, useReducer, useMemo } from "react";
import {
    apiFetchNews,
    apiScrapeNews,
    apiResetNews,
    apiSentimentAnalysis,
    apiSummarize,
    apiScrapeNewsWithTags,
    apiFetchNewsWithTags
} from "../../api/newsApi";

const NewsContext = createContext();

export const useNewsContext = () => {
    return useContext(NewsContext);
}

export const NewsProvider = ({ children }) => {

    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState("unknown");
    const [selectedNews, setSelectedNews] = useState({});

    const [_news, dispatch] = useReducer(
        newsReducer, []);

    const news = useMemo(() => _news, [_news]);

    const providerFetchNews = async () => {
        try {
            setStatus("Attempting to fetch news...");
            setLoading(true);
            const result = await apiFetchNews();
            setStatus("News fetched successfully")
            dispatch({ type: 'FETCH_SUCCESS', payload: result });
        } 
        catch (error) {
            setStatus("Error fetching news");
            console.error("Error fetching news", error);
            dispatch({ type: 'FETCH_FAILURE', payload: error });
        }
        setLoading(false);
    }

    const providerScrapeNews = async () => {
        try {
            setStatus("Attempting to scrape news...");
            setLoading(true);
            const result = await apiScrapeNews();
            setStatus("News scraped successfully")
            dispatch({ type: 'SCRAPE_SUCCESS', payload: result });
        } 
        catch (error) {
            setStatus("Error scraping news");
            console.error("Error scraping news", error);
            dispatch({ type: 'SCRAPE_FAILURE', payload: error });
        }
        setLoading(false);
    }

    const providerResetNews = async () => {
        try {
            setStatus("Attempting to reset database...");
            setLoading(true);
            const result = await apiResetNews();
            setStatus("Database resetted successfully")
            dispatch({ type: 'RESET_SUCCESS', payload: result });
        } 
        catch (error) {
            setStatus("Error resetting news");
            console.error("Error resetting news", error);
            dispatch({ type: 'RESET_FAILURE', payload: error });
        }
        setLoading(false);
    }

    const providerSentimentAnalysis = async (id) => {
        try {
            setStatus("Attempting to perform sentiment analysis...");
            setLoading(true);
            const result = await apiSentimentAnalysis(id);
            setStatus("Sentiment analysis performed successfully")
            setSelectedNews({ ...selectedNews, sa: result })
        } 
        catch (error) {
            setStatus("Error performing sentiment analysis");
            console.error("Error performing sentiment analysis", error);
        }
        setLoading(false);
    }

    const providerSummarize = async (id) => {
        try {
            setStatus("Attempting to summarize article...");
            setLoading(true);
            const result = await apiSummarize(id);
            setStatus("Article summarized successfully")
            setSelectedNews({ ...selectedNews, sum: result })
        } 
        catch (error) {
            setStatus("Error summarizing article");
            console.error("Error summarizing article", error);
        }
        setLoading(false);
    }

    const providerFetchNewsWithTags = async (tags) => {
        try {
            setStatus("Attempting to fetch news with tag");
            setLoading(true);
            const result = await apiFetchNewsWithTags(tags);
            setStatus("News fetched successfully");
            dispatch({ type: 'FETCH_TAG_SUCCESS', payload: result });
        }
        catch (error) {
            setStatus("Error fetching news with tag");
            console.error("Error fetching news with tag", error);
            dispatch({ type: 'FETCH_TAG_FAILURE', payload: error });
        }
        setLoading(false);
    }

    const providerScrapeNewsWithTags = async (tags) => {
        try {
            setStatus("Attempting to scrape news with tag");
            setLoading(true);
            const result = await apiScrapeNewsWithTags(tags);
            setStatus("News scraped successfully");
            dispatch({ type: 'SCRAPE_TAG_SUCCESS', payload: result });
        }
        catch (error) {
            setStatus("Error scraping news with tag");
            console.error("Error scraping news with tag", error);
            dispatch({ type: 'SCRAPE_TAG_FAILURE', payload: error });
        }
        setLoading(false);
    }
    
    const handleSelectedNews = ({ id, name, url, content, category, sa, sum }) => {
        setSelectedNews({ id, name, url, content,category, sa, sum });
    }

    const values = {
        news,
        status,
        selectedNews,
        loading, 
        providerFetchNews,
        providerScrapeNews,
        providerResetNews,
        providerSentimentAnalysis,
        providerSummarize,
        providerFetchNewsWithTags,
        providerScrapeNewsWithTags,
        handleSelectedNews
    }

    return (
        <NewsContext.Provider value={values}>
            {children}
        </NewsContext.Provider>
    )
};

const newsReducer = (news, action)  => {
    switch (action.type) {
            case 'FETCH_SUCCESS': 
            case 'SCRAPE_SUCCESS':
            case 'RESET_SUCCESS':
            case 'FETCH_TAG_SUCCESS':
            case 'SCRAPE_TAG_SUCCESS':
                return action.payload;

            case 'FETCH_FAILURE': 
            case 'SCRAPE_FAILURE':
            case 'RESET_FAILURE':
            case 'FETCH_TAG_FAILURE':
            case 'SCRAPE_TAG_FAILURE':
                return news;
            default:
                return news;
        }
    }
