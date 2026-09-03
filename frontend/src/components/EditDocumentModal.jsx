import { X, Upload } from "lucide-react";

export default function EditDocumentModal({
  isOpen,
  document,
  onClose,
  onUpdateDocument,
  handleSubmit,
  register,
  errors,
  isSubmitting,
}) {
  if (!isOpen || !document) return null;

  const submitUpdate = (data) => onUpdateDocument(document, data.file[0]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="edit-document-title"
    >
      <div className="w-full max-w-md rounded-lg bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <h2
            id="edit-document-title"
            className="text-lg font-semibold text-gray-900"
          >
            Edit document
          </h2>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            title="Close"
            className="text-gray-400 transition hover:text-gray-600 disabled:opacity-50"
          >
            <X size={20} />
          </button>
        </div>
        <form
          onSubmit={handleSubmit(submitUpdate)}
          className="space-y-4 px-6 py-5"
        >
          <p className="truncate text-sm text-gray-600">
            Replace{" "}
            <span className="font-medium text-gray-900">
              {document.filename}
            </span>
          </p>
          <label className="flex cursor-pointer items-center justify-center gap-2 rounded-md border-2 border-dashed border-gray-300 px-4 py-4 text-sm font-medium text-gray-600 transition hover:border-indigo-500 hover:bg-indigo-50">
            <Upload size={18} className="text-gray-400" />
            Choose replacement file
            <input
              type="file"
              className="sr-only"
              accept=".pdf,.docx,.txt,.md"
              {...register("file", {
                required: "A replacement file is required",
                validate: (files) =>
                  !files?.[0] ||
                  files[0].size <= 10 * 1024 * 1024 ||
                  "Maximum file size is 10MB",
              })}
            />
          </label>
          {errors?.file?.message && (
            <p className="text-sm text-red-600">{errors.file.message}</p>
          )}
          <p className="text-xs text-gray-500">
            PDF, DOCX, TXT, or MD files up to 10MB.
          </p>
          <div className="flex justify-end gap-3 border-t border-gray-100 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              aria-busy={isSubmitting}
              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting ? (
                <span className="inline-flex items-center justify-center gap-2">
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
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Updating...
                </span>
              ) : (
                "Update document"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
