from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
# REMOVED: GoogleGenerativeAIEmbeddings 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings # <--- NEW LOCAL EMBEDDINGS
from langchain_community.vectorstores import FAISS

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

from langchain_core.prompts import ChatPromptTemplate
from core.config import settings
import os

class RAGService:
    def __init__(self):
        # FIX: Use Local HuggingFace Embeddings (Free, No Rate Limits)
        # This runs on your CPU, so it never hits the Google API limit.
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # We keep Gemini for the Chat because it's smarter than local models
        self.llm = ChatGoogleGenerativeAI(model=settings.LLM_MODEL, temperature=0)
        
        self.vector_store = None
        self.qa_chain = None
        self.initialize_vector_store()

    def initialize_vector_store(self):
        print("--- Initializing Vector Store ---")
        loader = TextLoader("data/knowledge_base.txt")
        documents = loader.load()
        
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)
        
        self.vector_store = FAISS.from_documents(texts, self.embeddings)
        
        # Modern Chat Prompt
        prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")
        
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        retriever = self.vector_store.as_retriever()
        self.qa_chain = create_retrieval_chain(retriever, document_chain)
        
        print("--- Vector Store Ready ---")

    def get_answer(self, query: str):
        if not self.qa_chain:
            raise ValueError("Pipeline not initialized")
        
        result = self.qa_chain.invoke({"input": query})
        
        return {
            "answer": result["answer"],
            "context": [doc.page_content for doc in result["context"]]
        }