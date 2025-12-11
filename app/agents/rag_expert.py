import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class RagExpert:
    def __init__(self, documents_dir: str = "./documents"):
        self.documents_dir = documents_dir
        self.vectorstores = {"parents": None, "teachers": None}
        self.chains = {"parents": None, "teachers": None}

        if os.environ.get("OPENAI_API_KEY"):
            self.refresh_knowledge_base()
        else:
            print("WARNING: RAG no inicializado. Falta OPENAI_API_KEY")

    def refresh_knowledge_base(self):
        """Carga documentos diferenciados por rol"""
        for role in ["parents", "teachers"]:
            try:
                role_dir = os.path.join(self.documents_dir, role)
                if not os.path.exists(role_dir):
                    os.makedirs(role_dir)
                    print(f"Created directory: {role_dir}")
                    continue

                docs = []
                for filename in os.listdir(role_dir):
                    filepath = os.path.join(role_dir, filename)
                    if filename.endswith(".txt"):
                        loader = TextLoader(filepath, encoding="utf-8")
                        docs.extend(loader.load())
                    elif filename.endswith(".pdf"):
                        loader = PyPDFLoader(filepath)
                        docs.extend(loader.load())
                    elif filename.endswith(".docx"):
                        from langchain_community.document_loaders import Docx2txtLoader
                        loader = Docx2txtLoader(filepath)
                        docs.extend(loader.load())
                
                if not docs:
                    print(f"No documents found for {role} in {role_dir}")
                    continue

                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                splits = text_splitter.split_documents(docs)
                
                embeddings = OpenAIEmbeddings()
                self.vectorstores[role] = FAISS.from_documents(splits, embeddings)
                
                # Construir cadena específica para este rol
                self._build_chain(role)
                print(f"RAG Knowledge Base for {role} refreshed with {len(splits)} chunks.")
                
            except Exception as e:
                print(f"Error initializing RAG for {role}: {e}")

    def _build_chain(self, role):
        retriever = self.vectorstores[role].as_retriever(search_kwargs={"k": 2})
        
        # Prompts diferenciados
        if role == "parents":
            role_description = "un consejero empático para familias"
            context_instruction = "Usa lenguaje claro, tranquilizador y sin tecnicismos."
        else:
            role_description = "un experto técnico en protocolos escolares"
            context_instruction = "Usa terminología precisa, legal y enfócate en el procedimiento."

        template = f"""Eres {role_description}.
        Utiliza el siguiente contexto para responder.
        {context_instruction}
        Si la respuesta no está en el contexto, avisa y da una recomendación general.

        Contexto: {{context}}

        Pregunta: {{question}}

        Respuesta:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.chains[role] = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

    def get_advice(self, query: str, role: str = "parents") -> str:
        if role not in self.chains or not self.chains[role]:
            return f"El sistema RAG para '{role}' no está activo o no tiene documentos."
        return self.chains[role].invoke(query)

rag_system = RagExpert()
