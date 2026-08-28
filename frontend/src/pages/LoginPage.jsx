import { Link } from "react-router-dom";

import LoginForm from "../components/auth/LoginForm";



export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="rounded-2xl border border-gray-200 bg-white px-6 py-8 shadow-sm sm:px-10">
          <div className="flex justify-center">
            <img
              src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=500"
              alt="Telly ChatRAG"
              className="h-10 w-10"
            />
          </div>

          <div className="mt-6 text-center">
            <h2 className="text-2xl font-bold tracking-tight text-gray-900">
              Sign in to your account
            </h2>

            <p className="mt-2 text-sm text-gray-500">
              Welcome back! Please enter your details to continue.
            </p>
          </div>

          <div className="mt-8">
            <LoginForm />
          </div>
        </div>
      </div>
    </div>
  );
}
