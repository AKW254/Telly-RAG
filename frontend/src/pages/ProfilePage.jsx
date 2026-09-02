import React, { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "react-toastify";

import Breadcrumbs from "../components/Breadcrumb";
import ProfileForm from "../components/ProfileForm";
import SettingsForm from "../components/SettingsForm";

import { updateUser } from "../services/userService";
import useAuth from "../hooks/useAuth";

function ProfilePage() {
  const { user, setUser } = useAuth();
  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm();

  // Sync form fields once real user data is available
  useEffect(() => {
    if (user) reset(user);
  }, [user, reset]);

  const handleupdateUser = async (updatedUser) => {
    const payload = { ...updatedUser };
    if (!payload.password) {
      delete payload.password;
      delete payload.confirmPassword;
    }
    try {
      const userData = await updateUser(payload);
      setUser(userData);
      toast.success("User updated successfully");
    } catch (error) {
      console.error("Error updating user data:", error);
      toast.error("Failed to update user");
    }
  };

  return (
    <div className="flex h-full min-h-0 flex-col bg-gray-50">
      {/* Breadcrumb */}
      <div className="shrink-0 border-b border-gray-200 bg-white px-4 py-3 sm:px-6">
        <Breadcrumbs items={[{ name: "Profile", href: "/profile" }]} />
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="grid grid-cols-1 gap-6 ">
            <section className="rounded-xl border border-gray-200 bg-white shadow-sm">
              <div className="border-b border-gray-200 px-6 py-2">
                <h1 className="text-xl font-semibold text-gray-800">Profile</h1>
              </div>
              <div className="px-6 py-2">
                <ProfileForm user={user} />
              </div>
            </section>

            <section className="rounded-xl border border-gray-200 bg-white shadow-sm">
              <div className="border-b border-gray-200 px-6 py-4">
                <h2 className="text-xl font-semibold text-gray-800">
                  Settings
                </h2>
                <p className="mt-1 text-sm text-gray-500">
                  Manage your account settings and preferences.
                </p>
              </div>
              <div className="p-6">
                <SettingsForm
                  user={user}
                  updateUser={handleupdateUser}
                  register={register}
                  handleSubmit={handleSubmit}
                  isSubmitting={isSubmitting}
                  errors={errors}
                  watch={watch}
                />
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;
