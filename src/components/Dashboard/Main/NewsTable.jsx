import { Box, TableContainer, Table, TableHead, TableRow, TableCell, Typography } from "@mui/material";
import NewsItems from "./NewsTableItem";
import { useNewsContext } from "../../../utils/providers/newsProvider";

export default function DashboardNewsTable({}) {

    const { news } = useNewsContext();

    return (
        <TableContainer
            sx={{
                overflowY: "auto",
                minHeight: {sm: "100%"},
                width: {xs: "100%", sm: "80%"},
                height: "100%",
                backgroundColor: "primary.main"
            }}>

            <Table stickyHeader>
                <TableHead>
                    <TableRow>
                        <TableCell>No.</TableCell>
                        <TableCell>Title</TableCell>
                        <TableCell>Date</TableCell>
                        <TableCell>Tag / Category</TableCell>
                        <TableCell>Content</TableCell>
                    </TableRow>
                </TableHead>
                { news.length > 0 ? 
                    <NewsItems></NewsItems> : 
                    <Typography variant="h6" sx={{p: 3}}>Choose Fetch News to start
                </Typography>}
            </Table>
        </TableContainer>
    )
}