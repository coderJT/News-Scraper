import { Divider, Typography, Box } from "@mui/material";
import { useNewsContext } from "../../../utils/providers/newsProvider";

export default function DashboardDetails() {

    const { selectedNews } = useNewsContext();

    return (
        <Box 
            sx={{
                padding: "5%",
                color: "primary.appbar",
            }}>
            
            {/* Title */}
            <Typography 
                variant="h6" 
                sx={{p: 3}} 
                display={Object.keys(selectedNews).length ? "block" : "none"}>
                {selectedNews && selectedNews.name}
            </Typography>

            {/* Url */}
            <Typography
                variant="body2"
                sx={{
                    p: 3,
                    textAlign: "center",
                    maxWidth: "80%", 
                    maxHeight: "100%", 
                    wordBreak: 'break-all'
                }}
                display={Object.keys(selectedNews).length ? "block" : "none"}
                >
                {selectedNews && selectedNews.url}
            </Typography>

            {/* Sentiment Analysis */}
            <Typography 
                variant="body2" 
                sx={{p: 2}} 
                display={selectedNews.sa ? "block" : "none"}
                textAlign="center">
                {selectedNews.sa && "Sentiment: " + selectedNews.sa.overall_sentiment}
                {selectedNews.sa && "\n" + selectedNews.sa.weighted_sum}
            </Typography>

            {/* Summary */}
            <Typography
                variant="body2"
                sx={{p: 2}}
                textAlign="center"
                display={selectedNews.sum ? "block" : "none"}>
                {selectedNews.sum && "Summary: " + selectedNews.sum}
            </Typography>

            {/* Temporary divider and hint */}
            <Typography>
                {Object.keys(selectedNews).length 
                ? <Divider>Content</Divider>
                : "Select an item to show its details"}
            </Typography>

            {/* Content */}
            <Typography variant="body1" sx={{pt: 3}} textAlign='center'>
                {selectedNews.content}
            </Typography>
            
        </Box>
    )
}