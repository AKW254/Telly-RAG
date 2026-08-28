function Loader({ label = "Loading...", subtitle = "Please wait..." }) {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-gray-50">
      <div className="flex flex-col items-center text-center">
        <div
          className="h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"
          aria-label="Loading"
        />

        <h2 className="mt-4 text-base font-semibold text-gray-800">{label}</h2>

        <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
      </div>
    </div>
  );
}

export default Loader;
