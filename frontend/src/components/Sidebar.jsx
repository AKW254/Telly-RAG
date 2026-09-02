import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  User,
  FileText,
  LogOut,
  MessageSquare,
  ChevronRight,
} from "lucide-react";

import useAuth from "../hooks/useAuth";

function Sidebar() {
  const { logout } = useAuth();

  const navLinks = [
    {
      to: "/chat",
      icon: LayoutDashboard,
      label: "Dashboard",
    },
    {
      to: "/profile",
      icon: User,
      label: "Profile",
    },
    {
      to: "/documents",
      icon: FileText,
      label: "Documents",
    },
  ];

  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-gray-200 bg-white md:flex">
      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto px-3 py-5">
        {/* Main Navigation */}
        <div>
          <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
            Menu
          </p>

          <nav className="space-y-1">
            {navLinks.map((item) => {
              const Icon = item.icon;

              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `
                    group flex items-center justify-between
                    rounded-lg px-3 py-2.5
                    text-sm font-medium
                    transition-all duration-150
                    ${
                      isActive
                        ? "bg-indigo-50 text-indigo-600"
                        : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                    }
                    `
                  }
                >
                  {({ isActive }) => (
                    <>
                      <div className="flex items-center gap-3">
                        <Icon
                          className={`h-5 w-5 ${
                            isActive
                              ? "text-indigo-600"
                              : "text-gray-400 group-hover:text-gray-600"
                          }`}
                        />

                        <span>{item.label}</span>
                      </div>

                      {isActive && <ChevronRight className="h-4 w-4" />}
                    </>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Chats */}
        <div className="mt-8">
          <div className="mb-2 flex items-center justify-between px-3">
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Recent Chats
            </p>
          </div>

          <div className="space-y-1">
            <NavLink
              to="/chat/1"
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            >
              <MessageSquare className="h-4 w-4 text-gray-400" />
              <span className="truncate">Job Application Help</span>
            </NavLink>

            <NavLink
              to="/chat/2"
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            >
              <MessageSquare className="h-4 w-4 text-gray-400" />
              <span className="truncate">CV Improvement</span>
            </NavLink>
          </div>
        </div>

        {/* Documents */}
        <div className="mt-8">
          <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
            Recent Documents
          </p>

          <div className="space-y-1">
            <NavLink
              to="/documents/1"
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            >
              <FileText className="h-4 w-4 text-gray-400" />
              <span className="truncate">My CV.pdf</span>
            </NavLink>

            <NavLink
              to="/documents/2"
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            >
              <FileText className="h-4 w-4 text-gray-400" />
              <span className="truncate">Cover Letter.pdf</span>
            </NavLink>
          </div>
        </div>
      </div>

      {/* Logout */}
      <div className="border-t border-gray-200 p-4">
        <button
          onClick={logout}
          className="
            flex w-full items-center gap-3
            rounded-lg px-3 py-2.5
            text-sm font-medium
            text-red-600
            transition-colors
            hover:bg-red-50
          "
        >
          <LogOut className="h-5 w-5" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
