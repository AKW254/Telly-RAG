import { X } from "lucide-react";

export default function DeleteDocumentModal({
  isOpen,
  document,
  onClose,
  onDeleteDocument,
  handleSubmit,
  isSubmitting,
}) {
  if (!isOpen || !document) return null;

  const handleDelete = () => onDeleteDocument(document);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-document-title"
    >
      <div className="w-full max-w-md rounded-lg bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <h2
            id="delete-document-title"
            className="text-lg font-semibold text-gray-900"
          >
            Delete document
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
        <form onSubmit={handleSubmit(handleDelete)} className="px-6 py-5">
          <p className="text-sm text-gray-600">
            Delete{" "}
            <span className="font-medium text-gray-900">
              {document.filename}
            </span>
            ? This action cannot be undone.
          </p>
          <div className="mt-6 flex justify-end gap-3">
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
              className="rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-50"
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
                  Deleting...
                </span>
              ) : (
                "Delete document"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
