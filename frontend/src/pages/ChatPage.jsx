import React, { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { Bot, Send, User } from "lucide-react";

function ChatPage() {
  const { id } = useParams();

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const messagesEndRef = useRef(null);

  // ============================
  // Dummy Chat Data
  // ============================
  useEffect(() => {
    if (!id) {
      setMessages([]);
      return;
    }

    const chats = {
      1: [
        {
          id: 1,
          role: "user",
          content: "Can you help me improve my CV?",
        },
        {
          id: 2,
          role: "assistant",
          content:
            "Sure. Upload your CV and I'll help identify areas for improvement.",
        },
      ],

      2: [
        {
          id: 3,
          role: "user",
          content: "How do I write a good cover letter?",
        },
        {
          id: 4,
          role: "assistant",
          content:
            "A good cover letter should connect your experience directly to the job requirements.",
        },
      ],

      3: [
        {
          id: 5,
          role: "user",
          content: "Find jobs that match my skills.",
        },
        {
          id: 6,
          role: "assistant",
          content:
            "I can help you identify jobs based on your skills, experience, and CV.",
        },
      ],
    };

    setMessages(chats[id] || []);
  }, [id]);

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
  const handleSendMessage = (e) => {
    e.preventDefault();

    const message = inputMessage.trim();

    if (!message || isTyping) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      role: "user",
      content: message,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");

    // Simulate AI response
    setIsTyping(true);

    setTimeout(() => {
      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content:
          "This is a simulated response. Later, this message can come from your FastAPI/LangGraph backend.",
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsTyping(false);
    }, 1200);
  };

  // ============================
  // Keyboard Handler
  // ============================
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();

      handleSendMessage(e);
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
                Ask me about your CV, job applications, cover letters, or
                finding relevant jobs.
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
                        shadow-sm
                        sm:max-w-[70%]
                        ${
                          isUser
                            ? "rounded-br-md bg-indigo-600 text-white"
                            : "rounded-bl-md bg-white text-gray-800 ring-1 ring-gray-200"
                        }
                      `}
                  >
                    {msg.content}
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
          onSubmit={handleSendMessage}
          className="mx-auto flex max-w-4xl items-end gap-2"
        >
          <div className="relative flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isTyping}
              rows={1}
              placeholder="Ask about your CV, jobs, or applications..."
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

            <span className="absolute bottom-2 right-3 hidden text-[10px] text-gray-400 sm:block">
              Enter to send
            </span>
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
          AI responses are simulated for now.
        </p>
      </div>
    </div>
  );
}

export default ChatPage;
