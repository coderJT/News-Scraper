// Make API calls to server.py 

// API call to scraper
export const apiScrapeNews = async () => {
    try {
        const response = await fetch(`/api/scrape`);
        const data = await response.json();
        return data;
    } 
    catch (error) {
        console.error("(API) Error encountered at apiScrapeNews.", error);
        throw error;
    }
}

export const apiFetchNews = async () => {
    try {
        const response = await fetch(`/api/news`);
        const data = await response.json();
        return data;
    } 
    catch (error) {
        console.error("(API) Error encountered at apiFetchNews.", error);
        throw error;
    }
}

export const apiResetNews = async () => {
    try {
        const response = await fetch(`/api/reset`);
        const data = await response.json();
        return [];
    } 
    catch (error) {
        console.error("(API) Error encountered at apiResetNews.", error);
        throw error;
    }
}

export const apiScrapeNewsWithTags = async (tags) => {
    try {
        const tag_list = tags.filter((tag) => {
            return tag.selected === true
        }).map(tag => tag.label).join("&");
        const response = await fetch(`/api/scrapetag=${tag_list}`);
        const data = await response.json();
        return data;
    }
    catch (error) {
        console.error("(API) Error encountered at apiScrapeNewsWithTag.", error);
        throw error;
    }
}

export const apiFetchNewsWithTags = async (tags) => {

    try {
        const tag_list = tags.filter((tag) => {
            return tag.selected === true
        }).map(tag => tag.label).join("&");
        const response = await fetch(`/api/newstag=${tag_list}`);
        const data = await response.json();
        return data;
    }
    catch (error) {
        console.error("(API) Error encountered at apiFetchNewsWithTag.", error);
        throw error;
    }
}

// API call to sentiment analysis
export const apiSentimentAnalysis = async (id) => {
    try {
        const response = await fetch(`/api/sentimentAnalysis/${id}`);
        const data = await response.json();
        return data;
    }
    catch (error) {
        console.error("(API) Error encountered at apiSentimentAnalysis.", error);
        throw error;
    }
}

// API call to summarize
export const apiSummarize = async (id) => {
    try {
        const response = await fetch(`/api/summarize/${id}`);
        const data = await response.text();
        return data;
    }
    catch (error) {
        console.error("(API) Error encountered at apiSummarize.", error);
        throw error;
    }
}

