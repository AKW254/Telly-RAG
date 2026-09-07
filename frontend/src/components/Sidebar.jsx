import { useState, useEffect } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import {
  LayoutDashboard,
  User,
  FileText,
  LogOut,
  MessageSquare,
  ChevronRight,
  Trash2,
} from "lucide-react";

import useAuth from "../hooks/useAuth";
import { getDocuments } from "../services/documentService";
import { getChats, deleteChat } from "../services/chatService";

function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [chats, setChats] = useState([]);
  const [deletechatid, setDeletechatid] = useState(null);
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

  const fetchDocuments = async () => {
    try {
      const response = await getDocuments();
      setDocuments(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error("Error fetching documents:", error);
    }
  };
  const fetchChats = async () => {
    try {
      const response = await getChats();
      setChats(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error("Error fetching chats:", error);
    }
  };

  const handleDeleteChat = async (e, chatId) => {
    e.preventDefault();
    e.stopPropagation();

    const confirmed = window.confirm(
      "Are you sure you want to delete this chat? This action cannot be undone.",
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletechatid(chatId);

      await deleteChat(chatId);

      // Remove deleted chat from sidebar
      setChats((prevChats) => prevChats.filter((chat) => chat.id !== chatId));

      // If currently viewing this chat, go back to /chat
      if (location.pathname === `/chat/${chatId}`) {
        navigate("/chat");
      }

      // Notify other components
      window.dispatchEvent(new Event("chats-updated"));

      toast.success("Chat deleted successfully.");
    } catch (error) {
      console.error("Error deleting chat:", error);

      const message =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        "Failed to delete chat.";

      toast.error(message);
    } finally {
      setDeletechatid(null);
    }
  };

  useEffect(() => {
    const refreshTimer = window.setTimeout(fetchDocuments, 0);

    window.addEventListener("documents-updated", fetchDocuments);

    return () => {
      window.clearTimeout(refreshTimer);
      window.removeEventListener("documents-updated", fetchDocuments);
    };
  }, []);

  useEffect(() => {
    const refreshTimer = window.setTimeout(fetchChats, 0);

    window.addEventListener("chats-updated", fetchChats);

    return () => {
      window.clearTimeout(refreshTimer);
      window.removeEventListener("chats-updated", fetchChats);
    };
  }, [location.pathname]);

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
            {chats?.map((chat) => (
              <NavLink
                key={chat.id}
                to={`/chat/${chat.id}`}
                className={({ isActive }) =>
                  `
        group flex w-full items-center gap-2
        rounded-lg px-3 py-2.5
        text-sm
        transition-colors
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
                    {/* Chat Icon */}
                    <MessageSquare
                      className={`h-4 w-4 shrink-0 ${
                        isActive ? "text-indigo-600" : "text-gray-400"
                      }`}
                    />

                    {/* Chat Title */}
                    <span className="min-w-0 flex-1 truncate">
                      {chat.title || "Untitled Chat"}
                    </span>

                    {/* Delete Button */}
                    <button
                      type="button"
                      onClick={(e) => handleDeleteChat(e, chat.id)}
                      disabled={deletechatid === chat.id}
                      title="Delete chat"
                      className="
              shrink-0
              rounded-md
              p-1.5
              text-gray-400
              transition-colors
              hover:bg-red-50
              hover:text-red-600
              focus:outline-none
              focus:ring-2
              focus:ring-red-200
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
                    >
                      {deletechatid === chat.id ? (
                        <span
                          className="
                  block
                  h-4
                  w-4
                  animate-spin
                  rounded-full
                  border-2
                  border-gray-300
                  border-t-red-500
                "
                        />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </button>
                  </>
                )}
              </NavLink>
            ))}
          </div>
        </div>

        {/* Documents */}
        <div className="mt-8">
          <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
            Available Documents
          </p>

          <div className="space-y-1">
            <ol>
              {documents?.map((document) => (
                <li
                  key={document.id}
                  to="/documents"
                  className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                >
                  <FileText className="h-4 w-4 text-gray-400" />
                  <span className="truncate">{document.filename}</span>
                </li>
              ))}
            </ol>
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
