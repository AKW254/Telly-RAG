import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";

import Layout from "../components/Layout";
import Loader from "../components/Loader";

import ProtectedRoute from "./ProtectedRoute";

const LoginPage = lazy(() => import("../pages/LoginPage"));
const RegisterPage = lazy(() => import("../pages/RegistrationPage"));
const ProfilePage = lazy(() => import("../pages/ProfilePage"));
const DocumentPage = lazy(() => import("../pages/DocumentPage"));
const ChatPage = lazy(() => import("../pages/ChatPage"));

function AppRoutes() {
  return (
    <Suspense
      fallback={
        <Loader label="Loading page" subtitle="Preparing the next screen..." />
      }
    >
      <Routes>
        <Route element={<Layout />}>
          {/* Public Routes */}
          <Route path="/" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Routes using Outlet nesting */}
          <Route element={<ProtectedRoute />}>
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/document" element={<DocumentPage />} />
            <Route path="/chat" element={<ChatPage />} />
          </Route>
        </Route>
      </Routes>
    </Suspense>
  );
}

export default AppRoutes;
