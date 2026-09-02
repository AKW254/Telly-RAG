import RegisterForm from "../components/auth/RegisterForm";
function RegistrationPage() {
  return (
    <div className="flex min-h-screen items-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full sm:mx-auto sm:max-w-3xl">
        <div className="rounded-2xl border border-gray-200 bg-white px-8 py-12 shadow-sm sm:px-12">
          <div className="flex justify-center">
            <img
              src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=500"
              alt="Telly ChatRAG"
              className="h-10 w-10"
            />
          </div>

          <div className="mt-6 text-center">
            <h2 className="text-2xl font-bold tracking-tight text-gray-900">
              Create your account
            </h2>

            <p className="mt-2 text-sm text-gray-500">
              Welcome! Please enter your details to Join.
            </p>
          </div>
            <RegisterForm />
        </div>
      </div>
    </div>
  );
}

export default RegistrationPage;
