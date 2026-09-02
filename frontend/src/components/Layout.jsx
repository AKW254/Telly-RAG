import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Navigationbar from "./Navigationbar";

function Layout() {
  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-gray-50">
      {/* Top navigation */}
      <Navigationbar />

      {/* Sidebar + Content */}
      <div className="flex min-h-0 flex-1">
        <Sidebar />

        <main className="flex min-w-0 flex-1 flex-col overflow-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default Layout;
