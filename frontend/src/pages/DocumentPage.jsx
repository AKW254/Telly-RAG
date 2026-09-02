import { useEffect, useState } from "react";
import Breadcrumbs from "../components/Breadcrumb";
import DocumentsTable from "../components/DocumentsTable";
import { getDocuments } from "../services/documentService";

function DocumentPage() {
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const data = await getDocuments();
        setDocuments(data);
      } catch (error) {
        console.error("Error fetching documents:", error);
      }
    };
    fetchDocuments();
  }, []);

  const handleViewDocument = (documentId) => {
    console.log("View document with ID:", documentId);
  };

  const handleDeleteDocument = (documentId) => {
    console.log("Delete document with ID:", documentId);
  };

  const handleEditDocument = (documentId) => {
    console.log("Edit document with ID:", documentId);
  };

  return (
    <div className="flex h-full min-h-0 flex-col bg-gray-50">
      <div className="shrink-0 border-b border-gray-200 bg-white px-4 py-3 sm:px-6">
        <Breadcrumbs items={[{ name: "Documents", href: "/documents" }]} />
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="grid grid-cols-1 gap-6">
            <section className="rounded-xl border border-gray-200 bg-white shadow-sm">
              <div className="border-b border-gray-200 px-6 py-2">
                <h1 className="text-xl font-semibold text-gray-800">
                  Available Documents
                </h1>
              </div>
              <div className="px-4 py-2">
                <DocumentsTable
                  documents={documents}
                  onViewDocument={handleViewDocument}
                  onDeleteDocument={handleDeleteDocument}
                  onUpdateDocument={handleEditDocument}
                />
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DocumentPage;
