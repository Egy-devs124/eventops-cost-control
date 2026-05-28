import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";
import { AppLayout } from "../layouts/AppLayout";
import ClientsPage from "../pages/ClientsPage";
import DashboardPage from "../pages/DashboardPage";
import DriversPage from "../pages/DriversPage";
import FinancePage from "../pages/FinancePage";
import InventoryPage from "../pages/InventoryPage";
import LoginPage from "../pages/LoginPage";
import NotFoundPage from "../pages/NotFoundPage";
import NotificationsPage from "../pages/NotificationsPage";
import OrderDetailsPage from "../pages/OrderDetailsPage";
import OrdersPage from "../pages/OrdersPage";
import PayrollPage from "../pages/PayrollPage";
import ProfilePage from "../pages/ProfilePage";
import QuotationsPage from "../pages/QuotationsPage";
import ReportsPage from "../pages/ReportsPage";
import SettingsPage from "../pages/SettingsPage";
import StaffPage from "../pages/StaffPage";
import VendorsPage from "../pages/VendorsPage";

function RequireAuth({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const { t } = useLanguage();
  if (loading) return <div className="boot-loader">{t("loading")}...</div>;
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="clients" element={<ClientsPage />} />
        <Route path="orders" element={<OrdersPage />} />
        <Route path="orders/:id" element={<OrderDetailsPage />} />
        <Route path="quotations" element={<QuotationsPage />} />
        <Route path="inventory" element={<InventoryPage />} />
        <Route path="vendors" element={<VendorsPage />} />
        <Route path="drivers" element={<DriversPage />} />
        <Route path="staff" element={<StaffPage />} />
        <Route path="payroll" element={<PayrollPage />} />
        <Route path="finance" element={<FinancePage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
