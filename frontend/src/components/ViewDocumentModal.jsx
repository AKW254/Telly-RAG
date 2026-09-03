import { useState } from "react";
import { Download, X } from "lucide-react";
import { downloadDocument } from "../services/documentService";

export default function ViewDocumentModal({ isOpen, document, onClose }) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState("");

  if (!isOpen || !document) return null;

  const handleDownload = async () => {
    setIsDownloading(true);
    setDownloadError("");

    try {
      const blob = await downloadDocument(document.id);
      const url = URL.createObjectURL(blob);
      const link = window.document.createElement("a");
      link.href = url;
      link.download = document.filename || "document";
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      setDownloadError(error.message || "Failed to download document.");
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="view-document-title"
    >
      <div className="w-full max-w-lg rounded-lg bg-white shadow-xl p-2">
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <h2
            id="view-document-title"
            className="text-lg font-semibold text-gray-900"
          >
            Document details
          </h2>
          <button
            type="button"
            onClick={onClose}
            title="Close"
            className="text-gray-400 transition hover:text-gray-600"
          >
            <X size={20} />
          </button>
        </div>
        <dl className="space-y-4 px-6 py-5 text-sm">
          <div>
            <dt className="font-medium text-gray-500">Name</dt>
            <dd className="mt-1 break-words text-gray-900">
              {document.filename || "-"}
            </dd>
          </div>
          <div>
            <dt className="font-medium text-gray-500">Type</dt>
            <dd className="mt-1 text-gray-900">{document.file_type || "-"}</dd>
          </div>
          <div>
            <dt className="font-medium text-gray-500">Owner</dt>
            <dd className="mt-1 text-gray-900">{document.user?.name || "-"}</dd>
          </div>
          <div>
            <dt className="font-medium text-gray-500">Created</dt>
            <dd className="mt-1 text-gray-900">
              {document.created_at
                ? new Date(document.created_at).toLocaleString()
                : "-"}
            </dd>
          </div>
          <div>
            <dt className="font-medium text-gray-500">Updated</dt>
            <dd className="mt-1 text-gray-900">
              {document.updated_at
                ? new Date(document.updated_at).toLocaleString()
                : "-"}
            </dd>
          </div>
        </dl>
        <div className="border-t border-gray-200 px-6 py-4">
          {downloadError && (
            <p className="mb-3 text-sm text-red-600">{downloadError}</p>
          )}
          <button
            type="button"
            onClick={handleDownload}
            disabled={isDownloading}
            className="flex w-full items-center justify-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Download size={17} />
            {isDownloading ? "Downloading..." : "Download document"}
          </button>
        </div>
      </div>
    </div>
  );
}
