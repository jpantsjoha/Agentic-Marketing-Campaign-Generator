import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { MarketingProvider } from "@/contexts/MarketingContext";
import { SettingsProvider } from "@/contexts/SettingsContext";

// Pages
import LandingPage from "./pages/LandingPage";
import AboutPage from "./pages/AboutPage";
import DashboardPage from "./pages/DashboardPage";
import NewCampaignPage from "./pages/NewCampaignPage";
import IdeationPage from "./pages/IdeationPage";
import ProposalsPage from "./pages/ProposalsPage";
import SchedulingPage from "./pages/SchedulingPage";
import NotFound from "./pages/NotFound";
import SettingsPage from "./pages/SettingsPage";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <SettingsProvider>
        <MarketingProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/campaigns" element={<DashboardPage />} />
              <Route path="/new-campaign" element={<NewCampaignPage />} />
              <Route path="/ideation" element={<IdeationPage />} />
              <Route path="/proposals" element={<ProposalsPage />} />
              <Route path="/scheduling" element={<SchedulingPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </MarketingProvider>
      </SettingsProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
