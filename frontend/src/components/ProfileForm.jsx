

function ProfileForm({user}) {

  return (
    <div className="mt-2 mx-2 mb-2">
          <form>
            {/* Name */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="name"
                  className="block text-sm/6 font-medium text-gray-900"
                >
                  Name
                </label>
    
                <div className="mt-2">
                  <input
                    id="name"
                    type="text"
                    value={user?.name || ""}
                    readOnly
                    className="block w-full rounded-md bg-black/5 px-3 py-1.5 text-base text-black outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                  />
    
                </div>
              </div>
    
              {/* Email */}
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm/6 font-medium text-gray-900"
                >
                  Email address
                </label>
    
                <div className="mt-2">
                  <input
                    id="email"
                    type="email"
                    readOnly
                     value={user?.email || ""}
                    className="block w-full rounded-md bg-black/5 px-3 py-1.5 text-base text-black outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                  />
                 
                </div>
              </div>
    
            
            </div>

          </form>
        </div>
  )
}

export default ProfileForm