
import { useState } from "react";
import { X, Upload } from "lucide-react";

function AddDocumentModal({
  isOpen,
  onClose,
  handleSubmit,
  register,
  errors,
  isSubmitting,
  onAddDocument,
}) {
  const [filePreview, setFilePreview] = useState("");

  // Handle file input change
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];

    if (file) {
      setFilePreview(file.name);
    } else {
      setFilePreview("");
    }
  };

  const handleCancel = () => {
    setFilePreview("");
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      {/* Modal Container */}
      <div className="w-full max-w-md rounded-lg bg-white shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <h3 className="text-lg font-semibold text-gray-900">Add Document</h3>

          <button
            type="button"
            onClick={handleCancel}
            disabled={isSubmitting}
            className="text-gray-400 transition hover:text-gray-600 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <form
          onSubmit={handleSubmit(onAddDocument)}
          method="POST"
          
          className="space-y-4 px-6 py-5"
        >
          {/* File Upload */}
          <div>
            <label
              htmlFor="file"
              className="block text-sm font-medium text-gray-700"
            >
              Upload File <span className="text-red-500">*</span>
            </label>

            <div className="mt-2">
              <label
                htmlFor="file"
                className="flex cursor-pointer items-center justify-center gap-2 rounded-md border-2 border-dashed border-gray-300 px-4 py-4 transition hover:border-indigo-500 hover:bg-indigo-50"
              >
                <Upload size={18} className="text-gray-400" />

                <span className="text-sm font-medium text-gray-600">
                  Choose file
                </span>
              </label>

              <input
                id="file"
                type="file"
                className="sr-only"
                accept=".pdf,.docx,.txt,.md"
                {...register("file", {
                  required: "File is required",
                  validate: {
                    lessThan10MB: (files) =>
                      !files?.[0] ||
                      files[0].size <= 10 * 1024 * 1024 ||
                      "Maximum file size is 10MB",

                    acceptedFormats: (files) => {
                      if (!files?.[0]) return true;

                      const allowedTypes = [
                        "text/plain",
                        "text/markdown",
                        "application/pdf",
                        "application/msword",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                      ];

                      return (
                        allowedTypes.includes(files[0].type) ||
                        "Only PDF, DOCX, TXT, or MD files are allowed"
                      );
                    },
                  },
                })}
                onChange={(event) => {
                  handleFileChange(event);

                  // Preserve React Hook Form's onChange
                  register("file").onChange(event);
                }}
              />

              {/* Selected File */}
              {filePreview && (
                <div className="mt-2 rounded-md bg-green-50 px-3 py-2">
                  <p className="truncate text-sm font-medium text-green-700">
                    {filePreview}
                  </p>
                </div>
              )}

              {/* Validation Error */}
              {errors?.file?.message && (
                <p className="mt-2 text-sm text-red-600">
                  {errors.file.message}
                </p>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="border-t border-gray-100 pt-4">
            <button
              type="submit"
              disabled={isSubmitting}
              aria-busy={isSubmitting}
              className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting ? (
                <span className="inline-flex items-center justify-center gap-2">
                  <svg
                    className="h-4 w-4 animate-spin"
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
                    />

                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Uploading...
                </span>
              ) : (
                "Upload Document"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddDocumentModal;

