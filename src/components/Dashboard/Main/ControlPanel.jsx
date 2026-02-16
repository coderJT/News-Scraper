import { useNewsContext } from "../../../utils/providers/newsProvider"
import { useDashboardContext } from "../../../utils/providers/dashboardProvider";
import { Box, Chip, ButtonGroup, Button, Typography, Paper } from "@mui/material";

export default function DashboardControlPanel() {

    const { status, 
            loading, 
            providerFetchNews, 
            providerScrapeNews,
            providerResetNews,
            providerSentimentAnalysis,
            providerSummarize,
            providerFetchNewsWithTags,
            providerScrapeNewsWithTags,
            selectedNews } = useNewsContext();

    const { tagChips, handleTagChip } = useDashboardContext();

    return (
        <Box sx={{
                width: {xs: "100%", sm: "20%"},
                height: {xs: "auto", sm: "100%"},
                position: "static",
                overflowY: "auto",
                backgroundColor: "primary.control"
            }}>

            <Chip sx={{
                width: "100%", 
                height: "auto", 
                minHeight: "50px",
                padding: 1,
                textAlign: "center",
                "& .MuiChip-label": {
                    display: "block",
                    whiteSpace: "normal",
                    color: "primary.main"
                },
            }} label={status}></Chip>

            <ButtonGroup variant="outlined" 
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                }} 
                fullWidth 
                disabled={loading ? true : false}
                >
                
                <Button onClick={providerFetchNews}>FETCH NEWS</Button>
                <Button onClick={providerScrapeNews}>SCRAPE NEWS</Button>
                <Button onClick={providerResetNews}>RESET</Button>
                <Button onClick={() => providerSentimentAnalysis(selectedNews.id)} 
                        disabled={Object.keys(selectedNews).length ? false : true}>
                        Sentiment Analysis
                </Button>
                <Button onClick={() => providerSummarize(selectedNews.id)} 
                        disabled={Object.keys(selectedNews).length ? false : true}>
                        Summarize
                </Button>
                <Button onClick={() => providerFetchNewsWithTags(tagChips)}>FETCH NEWS (with tags)</Button>
                <Button onClick={() => providerScrapeNewsWithTags(tagChips)}>SCRAPE NEWS (with tags)</Button>

            </ButtonGroup>

            <Box sx={{
                mt: 'auto',
                display: "flex",
                flexWrap: "wrap",
                gap: 1
            }}>
                <Paper elevation={1} sx={{
                    p: 1, 
                    minWidth: 0, 
                    display: "flex", 
                    flexWrap: "wrap"}}>
                        <Typography variant="h6" sx={{width: "100%", m: 2}}>Tags</Typography>
                        {
                            tagChips.map(tag => (
                                <Chip
                                    key={tag.label}
                                    label={tag.label}
                                    sx={{m: 1}}
                                    onClick={() => handleTagChip(tag)}
                                    variant={tag.selected ? "filled": "outlined"}
                                    color="warning"
                                ></Chip>
                            ))
                        }
                    </Paper>
            </Box>

                
            </Box>
    )
}