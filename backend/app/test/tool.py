
from app.llm.llm import get_llm
from app.rag.generation.tools.document_email_tool import create_document_email_tool
from app.database.database import SessionLocal
db = SessionLocal()

tool = create_document_email_tool(db=db, user_name="Test", recipient_email="kilonzowambua254@gmail.com")
llm = get_llm().bind_tools([tool])
msg = llm.invoke("Please send document with ID 3 to my email")
print(msg.tool_calls)