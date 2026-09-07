import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";
import { Bot, Send, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { createChat } from "../services/chatService";
import { getMessages, createMessage } from "../services/messagechatService";

function ChatPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues: {
      message: "",
    },
  });

  const [messages, setMessages] = useState([]);
  // Watch the message field so we can disable the Send button
  const inputMessage = watch("message");
  const [isTyping, setIsTyping] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    let isCurrentRoute = true;

    setMessages([]);
    setIsTyping(false);
    reset();

    if (!id)
      return () => {
        isCurrentRoute = false;
      };

    const fetchMessages = async () => {
      try {
        const data = await getMessages(id);
        if (isCurrentRoute) {
          setMessages(data);
        }
      } catch (error) {
        if (isCurrentRoute) {
          console.error("Error fetching messages:", error);
        }
      }
    };
    fetchMessages();

    return () => {
      isCurrentRoute = false;
    };
  }, [id, reset]);

  // ============================
  // Auto Scroll
  // ============================
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isTyping]);

  // ============================
  // Send Message
  // ============================
  const handleSendMessage = async (data) => {
    const content = data.message.trim();
    let pendingMessageId;
    let chatId = id;

    try {
      setIsTyping(true);

      const chat = id ? null : await createChat({ title: content });
      chatId = id || chat?.id;

      if (!chatId) {
        throw new Error("The chat could not be created.");
      }

      if (!id) {
        window.dispatchEvent(new Event("chats-updated"));
      }

      const userMessage = {
        id: `pending-${Date.now()}`,
        chat_id: chatId,
        role: "user",
        content,
        created_at: new Date().toISOString(),
      };
      pendingMessageId = userMessage.id;

      setMessages((prev) => [...prev, userMessage]);
      reset();

      const assistantMessage = await createMessage(chatId, { content });
      setMessages((prev) => [...prev, assistantMessage]);

      if (!id) {
        navigate(`/chat/${chatId}`, { replace: true });
      }
    } catch (error) {
      console.error("Error sending message:", error);

      if (pendingMessageId) {
        setMessages((prev) => [
          ...prev,
          {
            id: `fallback-${Date.now()}`,
            chat_id: chatId,
            role: "assistant",
            content:
              "I received your message, but I could not generate an answer right now. Please try again in a moment.",
            created_at: new Date().toISOString(),
          },
        ]);
      }

      if (!id && chatId) {
        window.dispatchEvent(new Event("chats-updated"));
        navigate(`/chat/${chatId}`, { replace: true });
      }
    } finally {
      setIsTyping(false);
    }
  };
  // ============================
  // Keyboard Handler
  // ============================
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();

      handleSubmit(handleSendMessage)();
    }
  };

  return (
    <div className="flex h-full w-full flex-col overflow-hidden">
      {/* ============================
            Messages
        ============================ */}
      <div className="flex-1 overflow-y-auto bg-gray-50 px-3 py-5 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl space-y-5">
          {messages.length === 0 ? (
            <div className="flex h-full min-h-[400px] flex-col items-center justify-center text-center">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-100">
                <Bot className="h-7 w-7 text-indigo-600" />
              </div>

              <h2 className="text-lg font-semibold text-gray-800">
                Start a conversation
              </h2>

              <p className="mt-1 max-w-md text-sm text-gray-500">
                Ask me about anything about available documents.
              </p>
            </div>
          ) : (
            messages.map((msg) => {
              const isUser = msg.role === "user";

              return (
                <div
                  key={msg.id}
                  className={`flex items-end gap-2 ${
                    isUser ? "justify-end" : "justify-start"
                  }`}
                >
                  {/* Assistant Avatar */}
                  {!isUser && (
                    <div className="hidden h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 sm:flex">
                      <Bot className="h-4 w-4 text-indigo-600" />
                    </div>
                  )}

                  {/* Message */}
                  <div
                    className={`
                        max-w-[85%]
                        rounded-2xl
                        px-4 py-3
                        text-sm
                        leading-6
                        whitespace-pre-wrap
                        break-words
                        shadow-sm
                        sm:max-w-[70%]
                        ${
                          isUser
                            ? "rounded-br-md bg-indigo-600 text-white"
                            : "rounded-bl-md bg-white text-gray-800 ring-1 ring-gray-200"
                        }
                      `}
                  >
                    {isUser ? (
                      msg.content
                    ) : (
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => (
                            <p className="mb-3 last:mb-0">{children}</p>
                          ),
                          ul: ({ children }) => (
                            <ul className="mb-3 list-disc space-y-1 pl-5 last:mb-0">
                              {children}
                            </ul>
                          ),
                          ol: ({ children }) => (
                            <ol className="mb-3 list-decimal space-y-1 pl-5 last:mb-0">
                              {children}
                            </ol>
                          ),
                          li: ({ children }) => <li>{children}</li>,
                          strong: ({ children }) => (
                            <strong className="font-semibold">
                              {children}
                            </strong>
                          ),
                          h1: ({ children }) => (
                            <h1 className="mb-2 text-base font-semibold">
                              {children}
                            </h1>
                          ),
                          h2: ({ children }) => (
                            <h2 className="mb-2 text-base font-semibold">
                              {children}
                            </h2>
                          ),
                          h3: ({ children }) => (
                            <h3 className="mb-2 font-semibold">{children}</h3>
                          ),
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    )}
                  </div>

                  {/* User Avatar */}
                  {isUser && (
                    <div className="hidden h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-200 sm:flex">
                      <User className="h-4 w-4 text-gray-600" />
                    </div>
                  )}
                </div>
              );
            })
          )}

          {/* Typing indicator */}
          {isTyping && (
            <div className="flex items-end gap-2">
              <div className="hidden h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 sm:flex">
                <Bot className="h-4 w-4 text-indigo-600" />
              </div>

              <div className="rounded-2xl rounded-bl-md bg-white px-4 py-3 shadow-sm ring-1 ring-gray-200">
                <div className="flex items-center gap-1">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:150ms]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:300ms]" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* ============================
            Input
        ============================ */}
      <div className="shrink-0 border-t border-gray-200 bg-white px-3 py-3">
        <form
          onSubmit={handleSubmit(handleSendMessage)}
          className="mx-auto flex max-w-4xl items-end gap-2"
        >
          <div className="relative flex-1">
            <textarea
              value={inputMessage}
              {...register("message", { required: "No Message" })}
              onKeyDown={handleKeyDown}
              disabled={isTyping}
              rows={1}
              placeholder="Ask about your available documents"
              className="
                  block
                  w-full
                  resize-none
                  rounded-xl
                  border
                  border-gray-300
                  bg-gray-50
                  px-4
                  py-3
                  pr-12
                  text-sm
                  text-gray-900
                  placeholder:text-gray-400
                  focus:border-indigo-500
                  focus:bg-white
                  focus:outline-none
                  focus:ring-2
                  focus:ring-indigo-500/20
                  disabled:cursor-not-allowed
                  disabled:opacity-60
                "
            />
            {errors.message?.message && (
              <p className="mt-2 text-sm text-red-500">
                {errors.message.message}
              </p>
            )}
            {isSubmitting ? (
              <span className="absolute bottom-2 right-3 hidden text-[10px] text-gray-400 sm:block">
                <svg
                  className="h-4 w-4 animate-spin text-white/90"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Sending
              </span>
            ) : (
              <span className="absolute bottom-2 right-3 hidden text-[10px] text-gray-400 sm:block">
                Enter to Send
              </span>
            )}
          </div>

          <button
            type="submit"
            disabled={!inputMessage.trim() || isTyping}
            className="
                flex
                h-11
                w-11
                shrink-0
                items-center
                justify-center
                rounded-xl
                bg-indigo-600
                text-white
                transition-colors
                hover:bg-indigo-700
                focus:outline-none
                focus:ring-2
                focus:ring-indigo-500
                focus:ring-offset-2
                disabled:cursor-not-allowed
                disabled:bg-gray-300
              "
          >
            <Send className="h-5 w-5" />
          </button>
        </form>

        <p className="mx-auto mt-2 hidden max-w-4xl text-center text-[11px] text-gray-400 sm:block">
          AI responses are based On Available Documents
        </p>
      </div>
    </div>
  );
}

export default ChatPage;
