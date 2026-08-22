from app.rag.retrieval.RetrieverService import RetrieverService

retriever = RetrieverService()
docs = retriever.retrieve(query="send me the company profile", top_k=5)

for d in docs:
    print(d.metadata)
    print(d.page_content[:200])
    print("---")