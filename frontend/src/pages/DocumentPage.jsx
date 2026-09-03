import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "react-toastify";

import Breadcrumbs from "../components/Breadcrumb";
import DocumentsTable from "../components/DocumentsTable";
import {
  getDocuments,
  addDocument,
  getDocument,
  updateDocument,
  deleteDocument,
} from "../services/documentService";
import useAuth from "../hooks/useAuth";

function DocumentPage() {
  const { user: currentUser } = useAuth();
  const [documents, setDocuments] = useState([]);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting: isAdding },
  } = useForm();
  const {
    register: registerEdit,
    handleSubmit: handleEditSubmit,
    reset: resetEdit,
    formState: { errors: editErrors, isSubmitting: isEditing },
  } = useForm();
  const {
    handleSubmit: handleDeleteSubmit,
    reset: resetDelete,
    formState: { isSubmitting: isDeleting },
  } = useForm();

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
  //View Sigle Document
  const handleViewDocument = async (document) => {
    try {
      await getDocument(document.id);
    } catch (error) {
      console.error("Error fetching document:", error);
    }
  };

  const handleDeleteDocument = async (document) => {
    try {
      await deleteDocument(document.id);
      setDocuments((prevDocuments) =>
        prevDocuments.filter((item) => item.id !== document.id),
      );
      window.dispatchEvent(new Event("documents-updated"));
      toast.success("Document deleted successfully.");
    } catch (error) {
      console.error("Error deleting document:", error);
      toast.error(error.message || "Failed to delete document.");
      throw error;
    }
  };

  const handleEditDocument = async (document, file) => {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const updatedDocument = await updateDocument(document.id, formData);
      setDocuments((prevDocuments) =>
        prevDocuments.map((item) =>
          item.id === document.id ? updatedDocument : item,
        ),
      );
      window.dispatchEvent(new Event("documents-updated"));
      toast.success("Document updated successfully.");
    } catch (error) {
      console.error("Error updating document:", error);
      toast.error(error.message || "Failed to update document.");
      throw error;
    }
  };
  // Add Document
  const onSubmit = async (data) => {
    try {
      const formData = new FormData();
      // Append the file to the FormData object
      formData.append("file", data.file[0]);

      const newDocument = await addDocument(formData);
      setDocuments((prevDocuments) => [...prevDocuments, newDocument]);
      window.dispatchEvent(new Event("documents-updated"));

      toast.success("Document added successfully.");
      reset();
    } catch (error) {
      console.error("Error adding document:", error);
      toast.error("Failed to add document.");
      throw error;
    }
  };

  return (
    <div className="flex h-full min-h-2 flex-col bg-gray-50">
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
                  onAddDocument={onSubmit}
                  register={register}
                  handleSubmit={handleSubmit}
                  errors={errors}
                  isSubmitting={isAdding}
                  registerEdit={registerEdit}
                  handleEditSubmit={handleEditSubmit}
                  editErrors={editErrors}
                  isEditing={isEditing}
                  resetEdit={resetEdit}
                  handleDeleteSubmit={handleDeleteSubmit}
                  isDeleting={isDeleting}
                  resetDelete={resetDelete}
                  onViewDocument={handleViewDocument}
                  onDeleteDocument={handleDeleteDocument}
                  onUpdateDocument={handleEditDocument}
                  currentUser={currentUser}
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
