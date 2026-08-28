import { Outlet } from "react-router-dom"

function Layout(){
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="border-b bg-white">
          <div className="w-full px-4 sm:px-6 lg:px-8">{/* Navbar */}</div>
        </header>

        {/* Main content */}
        <main className="w-full px-4 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    );

}
export default Layout;