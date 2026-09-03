import { useMemo, useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  ChevronsUpDown,
  Search,
  Eye,
  Pencil,
  Trash2,
  Plus,
} from "lucide-react";
import AddDocumentModal from "./AddDocumentModal";

export default function DocumentsTable({
  documents = [],
  onViewDocument,
  onDeleteDocument,
  onUpdateDocument,
  onAddDocument,
}) {
  const [globalFilter, setGlobalFilter] = useState("");
  const [sortField, setSortField] = useState(null);
  const [sortDirection, setSortDirection] = useState("asc");
  const [pageIndex, setPageIndex] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleAddDocument = async (formData) => {
    if (onAddDocument) {
      await onAddDocument(formData);
    }
  };

  const handleSort = (field) => {
    if (sortField === field) {
      if (sortDirection === "asc") {
        setSortDirection("desc");
      } else {
        setSortField(null);
        setSortDirection("asc");
      }
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const filteredDocuments = useMemo(() => {
    if (!globalFilter.trim()) return documents;
    const query = globalFilter.toLowerCase();
    return documents.filter((doc) => {
      return (
        (doc.name && doc.name.toLowerCase().includes(query)) ||
        (doc.type && doc.type.toLowerCase().includes(query)) ||
        (doc.owner && doc.owner.toLowerCase().includes(query))
      );
    });
  }, [documents, globalFilter]);

  const sortedDocuments = useMemo(() => {
    if (!sortField) return filteredDocuments;
    return [...filteredDocuments].sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];

      if (!aVal) aVal = "";
      if (!bVal) bVal = "";

      if (sortField === "createdAt" || sortField === "updatedAt") {
        aVal = aVal ? new Date(aVal).getTime() : 0;
        bVal = bVal ? new Date(bVal).getTime() : 0;
      }

      if (typeof aVal === "string") {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }

      if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
      if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });
  }, [filteredDocuments, sortField, sortDirection]);

  const totalPages = Math.ceil(sortedDocuments.length / pageSize) || 1;
  const paginatedDocuments = useMemo(() => {
    const start = pageIndex * pageSize;
    return sortedDocuments.slice(start, start + pageSize);
  }, [sortedDocuments, pageIndex, pageSize]);

  const startItem = sortedDocuments.length === 0 ? 0 : pageIndex * pageSize + 1;
  const endItem = Math.min((pageIndex + 1) * pageSize, sortedDocuments.length);

  return (
    <div className="w-full rounded-lg border border-gray-200 bg-white shadow-sm">
      {/* Header & Search Bar */}
      <div className="flex flex-col gap-4 border-b border-gray-200 p-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Documents</h2>
            <p className="text-sm text-gray-500">Manage your documents</p>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="ml-auto flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-700 sm:ml-0"
          >
            <Plus size={18} />
            Add Document
          </button>
        </div>
        <div className="relative w-full sm:w-72">
          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
          />
          <input
            type="text"
            value={globalFilter}
            onChange={(event) => {
              setGlobalFilter(event.target.value);
              setPageIndex(0);
            }}
            placeholder="Search documents..."
            className="w-full rounded-md border border-gray-300 bg-white py-2 pl-10 pr-3 text-sm text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
          />
        </div>
      </div>

      {/* Tailwind Responsive Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {[
                { key: "name", label: "Document Name", sortable: true },
                { key: "type", label: "Type", sortable: true },
                { key: "owner", label: "Owner", sortable: true },
                { key: "createdAt", label: "Created At", sortable: true },
                { key: "updatedAt", label: "Updated At", sortable: true },
                { key: "actions", label: "Actions", sortable: false },
              ].map((column) => {
                const isSorted = sortField === column.key;
                return (
                  <th
                    key={column.key}
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500"
                  >
                    {column.sortable ? (
                      <button
                        type="button"
                        onClick={() => handleSort(column.key)}
                        className="flex cursor-pointer items-center gap-1 hover:text-gray-900"
                      >
                        {column.label}
                        {isSorted ? (
                          sortDirection === "asc" ? (
                            <ChevronUp size={15} />
                          ) : (
                            <ChevronDown size={15} />
                          )
                        ) : (
                          <ChevronsUpDown size={15} className="text-gray-400" />
                        )}
                      </button>
                    ) : (
                      column.label
                    )}
                  </th>
                );
              })}
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-200 bg-white">
            {paginatedDocuments.length > 0 ? (
              paginatedDocuments.map((doc, index) => (
                <tr
                  key={doc.id || index}
                  className="transition hover:bg-gray-50"
                >
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                    <div className="font-medium text-gray-900">
                      {doc.name || "—"}
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                    <span className="inline-flex rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700">
                      {doc.type || "—"}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                    {doc.owner || "—"}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                    {doc.createdAt
                      ? new Date(doc.createdAt).toLocaleDateString()
                      : "—"}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                    {doc.updatedAt
                      ? new Date(doc.updatedAt).toLocaleDateString()
                      : "—"}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => onViewDocument?.(doc)}
                        title="View document"
                        className="rounded-md p-2 text-gray-500 transition hover:bg-indigo-50 hover:text-indigo-600"
                      >
                        <Eye size={17} />
                      </button>
                      <button
                        type="button"
                        onClick={() => onUpdateDocument?.(doc)}
                        title="Update document"
                        className="rounded-md p-2 text-gray-500 transition hover:bg-blue-50 hover:text-blue-600"
                      >
                        <Pencil size={17} />
                      </button>
                      <button
                        type="button"
                        onClick={() => onDeleteDocument?.(doc)}
                        title="Delete document"
                        className="rounded-md p-2 text-gray-500 transition hover:bg-red-50 hover:text-red-600"
                      >
                        <Trash2 size={17} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center">
                  <div className="flex flex-col items-center justify-center">
                    <div className="mb-3 rounded-full bg-gray-100 p-3">
                      <Search size={22} className="text-gray-400" />
                    </div>
                    <p className="text-sm font-medium text-gray-900">
                      No documents found
                    </p>
                    <p className="mt-1 text-sm text-gray-500">
                      Try changing your search criteria.
                    </p>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      <div className="flex flex-col gap-4 border-t border-gray-200 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="text-sm text-gray-500">
          Showing <span className="font-medium text-gray-900">{startItem}</span>{" "}
          to <span className="font-medium text-gray-900">{endItem}</span> of{" "}
          <span className="font-medium text-gray-900">
            {sortedDocuments.length}
          </span>{" "}
          results
        </div>

        <div className="flex items-center gap-2">
          <select
            value={pageSize}
            onChange={(event) => {
              setPageSize(Number(event.target.value));
              setPageIndex(0);
            }}
            className="rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-700 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
          >
            {[5, 10, 20, 30, 50].map((size) => (
              <option key={size} value={size}>
                {size} / page
              </option>
            ))}
          </select>

          <button
            type="button"
            onClick={() => setPageIndex((prev) => Math.max(prev - 1, 0))}
            disabled={pageIndex === 0}
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Previous
          </button>

          <span className="px-2 text-sm text-gray-600">
            Page{" "}
            <span className="font-medium text-gray-900">{pageIndex + 1}</span>{" "}
            of <span className="font-medium text-gray-900">{totalPages}</span>
          </span>

          <button
            type="button"
            onClick={() =>
              setPageIndex((prev) => Math.min(prev + 1, totalPages - 1))
            }
            disabled={pageIndex >= totalPages - 1}
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>

      {/* Add Document Modal */}
      <AddDocumentModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleAddDocument}
      />
    </div>
  );
}
