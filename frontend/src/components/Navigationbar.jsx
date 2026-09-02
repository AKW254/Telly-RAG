import { NavLink } from "react-router-dom";
import {
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
} from "@headlessui/react";

import {
  LayoutDashboard,
  User,
  FileText,
  LogOut,
  Bell,
  Menu as Bars3Icon,
  X as XMarkIcon,
} from "lucide-react";

import useAuth from "../hooks/useAuth";

const navigation = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Profile",
    href: "/profile",
    icon: User,
  },
  {
    name: "Documents",
    href: "/documents",
    icon: FileText,
  },
];

function Navigationbar() {
  const { logout, user } = useAuth();

  return (
    <Disclosure
      as="nav"
      className="
        sticky top-0 z-40
        border-b border-gray-200
        bg-white/95
        backdrop-blur
      "
    >
      <div className="mx-auto w-full px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">

          {/* Mobile / Tablet Menu Button */}
          <div className="flex items-center lg:hidden">
            <DisclosureButton
              className="
                inline-flex items-center justify-center
                rounded-lg p-2
                text-gray-500
                hover:bg-gray-100
                hover:text-gray-900
                focus:outline-none
                focus:ring-2
                focus:ring-indigo-500
              "
            >
              <span className="sr-only">
                Open main menu
              </span>

              <Bars3Icon
                aria-hidden="true"
                className="block h-6 w-6 group-data-open:hidden"
              />

              <XMarkIcon
                aria-hidden="true"
                className="hidden h-6 w-6 group-data-open:block"
              />
            </DisclosureButton>
          </div>

          {/* Logo */}
          <div className="flex items-center lg:hidden">
            <NavLink
              to="/dashboard"
              className="flex items-center gap-2"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600">
                <FileText className="h-5 w-5 text-white" />
              </div>

              <span className="hidden font-bold text-gray-900 sm:block">
                Telly RAG
              </span>
            </NavLink>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex lg:flex-1 lg:items-center lg:gap-8">
            <NavLink
              to="/chat"
              className="flex items-center gap-2 font-bold text-gray-900"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600">
                <FileText className="h-5 w-5 text-white" />
              </div>

              Telly RAG
            </NavLink>

            <nav className="flex items-center gap-1">
              {navigation.map((item) => {
                const Icon = item.icon;

                return (
                  <NavLink
                    key={item.href}
                    to={item.href}
                    className={({ isActive }) =>
                      `
                      flex items-center gap-2
                      rounded-lg px-3 py-2
                      text-sm font-medium
                      transition-colors
                      ${
                        isActive
                          ? "bg-indigo-50 text-indigo-600"
                          : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                      }
                      `
                    }
                  >
                    <Icon className="h-4 w-4" />
                    {item.name}
                  </NavLink>
                );
              })}
            </nav>
          </div>

          {/* Right Side */}
          <div className="flex items-center gap-2 sm:gap-4">

           

            {/* User Menu */}
            <Menu as="div" className="relative">
              <MenuButton
                className="
                  flex items-center gap-2
                  rounded-full
                  focus:outline-none
                  focus:ring-2
                  focus:ring-indigo-500
                "
              >
                <img
                  alt="User profile"
                  src={
                    user?.avatar ||
                    "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop"
                  }
                  className="
                    h-8 w-8
                    rounded-full
                    object-cover
                    ring-2 ring-gray-100
                  "
                />

                <span className="hidden text-sm font-medium text-gray-700 md:block">
                  {user?.name || "User"}
                </span>
              </MenuButton>

              <MenuItems
                transition
                className="
                  absolute right-0 z-50 mt-2
                  w-48
                  origin-top-right
                  rounded-xl
                  bg-white
                  py-1
                  shadow-lg
                  ring-1 ring-black/5
                  focus:outline-none
                  data-closed:scale-95
                  data-closed:opacity-0
                  data-enter:duration-100
                  data-leave:duration-75
                "
              >
                <MenuItem>
                  <NavLink
                    to="/profile"
                    className="
                      block px-4 py-2.5
                      text-sm text-gray-700
                      data-focus:bg-gray-50
                    "
                  >
                    Your profile
                  </NavLink>
                </MenuItem>

                <MenuItem>
                  <button
                    onClick={logout}
                    className="
                      flex w-full items-center gap-2
                      px-4 py-2.5
                      text-left text-sm text-red-600
                      data-focus:bg-red-50
                    "
                  >
                    <LogOut className="h-4 w-4" />
                    Sign out
                  </button>
                </MenuItem>
              </MenuItems>
            </Menu>
          </div>
        </div>
      </div>

      {/* Mobile + Tablet Navigation */}
      <DisclosurePanel className="border-t border-gray-200 bg-white lg:hidden">
        <div className="space-y-1 px-3 py-3 sm:px-6">
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <DisclosureButton
                key={item.href}
                as={NavLink}
                to={item.href}
                className={({ isActive }) =>
                  `
                  flex items-center gap-3
                  rounded-lg px-3 py-3
                  text-sm font-medium
                  ${
                    isActive
                      ? "bg-indigo-50 text-indigo-600"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  }
                  `
                }
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </DisclosureButton>
            );
          })}
        </div>
      </DisclosurePanel>
    </Disclosure>
  );
}

export default Navigationbar;