import AppRoutes from "./routes/AppRoutes"

import { ToastContainer } from "react-toastify";


function App() {
  

  return (
    <>
      <AppRoutes />
      <ToastContainer
        position="top-right"
        autoClose={3000}
        newestOnTop
        closeOnClick
        pauseOnHover
        draggable
        theme="dark"
        limit={3}
      />
    </>
  );
}

export default App
