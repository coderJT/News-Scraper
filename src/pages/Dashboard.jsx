import DashboardAppBar from "../components/Dashboard/AppBar/AppBar";
import DashboardSidebar from "../components/Dashboard/Sidebar/Sidebar";
import DashboardNewsTable from "../components/Dashboard/Main/NewsTable";
import DashboardControlPanel from "../components/Dashboard/Main/ControlPanel";
import DashboardDetails from "../components/Dashboard/Details/Details";
import { useDashboardContext } from "../utils/providers/dashboardProvider";
import { Hidden, Dialog, Box, ThemeProvider, Button, CircularProgress } from "@mui/material";
import { useNewsContext } from "../utils/providers/newsProvider";

export default function Dashboard() {
  const { theme, dialogOpen, handleDialogOpen } = useDashboardContext();
  const { providerSentimentAnalysis, providerSummarize, selectedNews, loading } = useNewsContext();

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            sm: "repeat(4, 1fr)",
          },
          gridTemplateRows: {
            xs: "70px 2fr",
            sm: "10% 1fr 1fr",
          },
          gridTemplateAreas: {
            xs: `'appbar'
                             'main'`,
            sm: `'appbar appbar appbar appbar'
                             'main main main details'
                             'main main main details'`,
          },
          height: { xs: "200vh", sm: "100vh" },
        }}
      >

        {/* Appbar */}
        <Box
          sx={{
            gridArea: "appbar",
          }}
        >
          <DashboardAppBar></DashboardAppBar>
          <DashboardSidebar></DashboardSidebar>
        </Box>
        
        {/* Main content */}
        <Box
          sx={{
            gridArea: "main",
            overflowX: "auto",
            overflowY: "auto",
            display: "flex",
            flexDirection: { xs: "column", sm: "row" },
            justifyContent: "center",
            alignItem: "center",
            height: "100%",
          }}
        >
          <DashboardNewsTable></DashboardNewsTable>
          <Hidden smDown>
            <DashboardControlPanel></DashboardControlPanel>
          </Hidden>
        </Box>

        {/* Details (mobile) */}
        <Hidden smUp>
            <Dialog fullWidth
            open={dialogOpen}
            onClose={handleDialogOpen}
              sx={{
                bgcolor: "primary.details",
                overflowX: "auto",
                overflowY: "auto",
              }}
            >
                 <Box sx={{display: loading ? 'block' : 'none'}}>
                    <CircularProgress sx={{color: "primary.details"}}/>
                </Box>
                <Button sx={{ backgroundColor: "primary.details", color: "primary.appbar"}} onClick={() => providerSentimentAnalysis(selectedNews.id)}>Sentiment Analysis</Button>
                <Button sx={{ backgroundColor: "primary.details", color: "primary.appbar"}} onClick={() => providerSummarize(selectedNews.id)}>Summarize</Button>
                <DashboardDetails></DashboardDetails>
            </Dialog>
        </Hidden>

        {/* Details */}
        <Hidden smDown>
          <Box
            sx={{
              gridArea: "details",
              bgcolor: "primary.details",
              overflowX: "auto",
              overflowY: "auto"
            }}
          >
            <DashboardDetails></DashboardDetails>
          </Box>
        </Hidden>
      </Box>
    </ThemeProvider>
  );
}
