import os
import shutil
import subprocess
from typing import List, Dict, Tuple
import gradio as gr
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

UPLOAD_DIR = "uploads"
VECTOR_DB_DIR = "vector_store"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

def get_available_models() -> List[str]:
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"Ollama list command failed: {result.stderr}")
            return []
        
        models = []
        for line in result.stdout.split('\n')[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if parts:
                    model_name = parts[0].strip()
                    models.append(model_name)
        
        print(f"Found {len(models)} Ollama models:")
        for model in models:
            print(f"  - {model}")
        return models
    except FileNotFoundError:
        print("Ollama CLI not found. Please install Ollama.")
        return []
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []

class SimpleRAG:
    def __init__(self):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.embedding_model = None
        self.client = None
        self.collection = None
        
    def initialize(self):
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(self.model_name)
        
        if self.client is None:
            self.client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
            
        try:
            self.collection = self.client.get_collection(name="documents")
        except:
            self.collection = self.client.create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_documents(self, chunks: list):
        self.initialize()
        
        texts = [chunk.page_content for chunk in chunks]
        embeddings = self.embedding_model.encode(texts).tolist()
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            metadata = {
                "page": chunk.metadata.get("page", "unknown"),
                "source": chunk.metadata.get("source", "unknown")
            }
            metadatas.append(metadata)
            ids.append(f"doc_{os.urandom(8).hex()}_{i}")
        
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(self, query_text: str, model: str, n_results: int = 4) -> Tuple[str, list]:
        self.initialize()
        
        query_embedding = self.embedding_model.encode([query_text]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        context_texts = results["documents"][0]
        metadatas = results["metadatas"][0]
        
        prompt = f"""Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{''.join([f'[{meta["page"]}]: {text}\n' for text, meta in zip(context_texts, metadatas)])}

Question: {query_text}

Answer:"""
        
        try:
            result = subprocess.run(
                ['ollama', 'run', model, prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"Ollama failed: {result.stderr}")
            
            answer = result.stdout.strip()
            
            sources = [f"Page {meta['page']}" for meta in metadatas]
            
            return answer, sources
        except subprocess.TimeoutExpired:
            raise Exception("Ollama request timed out")
        except Exception as e:
            raise Exception(f"Error calling Ollama: {str(e)}")
    
    def clear(self):
        if self.client:
            try:
                self.client.delete_collection(name="documents")
            except:
                pass
            self.collection = None

rag_system = SimpleRAG()

def process_pdf(file_path: str) -> str:
    if not file_path:
        return "Please upload a PDF file first."
    
    try:
        filename = os.path.basename(file_path)
        dest_path = os.path.join(UPLOAD_DIR, filename)
        shutil.copy2(file_path, dest_path)
        
        loader = PyPDFLoader(dest_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        
        rag_system.add_documents(chunks)
        
        return f"Successfully processed PDF and created vector store with {len(chunks)} chunks"
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

def chat_response(message: str, history: List[List[str]], model_name: str) -> str:
    if not message.strip():
        return "Please ask a question."
    
    if not model_name:
        return "Please select an Ollama model."
    
    try:
        answer, sources = rag_system.query(message, model=model_name)
        
        if sources:
            answer += f"\n\n**Sources:** {', '.join(sorted(sources))}"
        
        return answer
    except Exception as e:
        return f"Error generating response: {str(e)}"

def clear_vector_store() -> str:
    try:
        rag_system.clear()
        return "Vector store cleared successfully."
    except Exception as e:
        return f"Error clearing vector store: {str(e)}"

def reset_chat() -> Tuple[List, str]:
    return [], ""

def create_interface():
    models = get_available_models()
    
    with gr.Blocks(title="Personal Assistant - RAG Chatbot") as interface:
        gr.Markdown("# 📚 Personal Assistant - RAG Chatbot")
        gr.Markdown("Upload a PDF document and ask questions about it using AI-powered retrieval-augmented generation.")
        
        with gr.Row():
            with gr.Column(scale=1):
                file_upload = gr.File(
                    label="Upload PDF",
                    file_types=[".pdf"],
                    type="filepath"
                )
                
                if models:
                    default_model = models[0]
                else:
                    default_model = None
                
                model_dropdown = gr.Dropdown(
                    label="Select Ollama Model",
                    choices=models,
                    value=default_model,
                    interactive=True
                )
                
                refresh_models_btn = gr.Button("🔄 Refresh Models")
                
                process_btn = gr.Button("📥 Process Document", variant="primary")
                
                clear_vector_btn = gr.Button("🗑️ Clear Vector Store", variant="stop")
                
                process_output = gr.Textbox(
                    label="Processing Status",
                    lines=3,
                    interactive=False
                )
            
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Chat with your Document",
                    height=500
                )
                
                chat_input = gr.Textbox(
                    label="Ask a Question",
                    placeholder="Type your question about the document here...",
                    lines=2
                )
                
                with gr.Row():
                    submit_btn = gr.Button("Send", variant="primary")
                    clear_chat_btn = gr.Button("Clear Chat")
        
        def refresh_models():
            new_models = get_available_models()
            return gr.Dropdown(choices=new_models, value=new_models[0] if new_models else None)
        
        refresh_models_btn.click(
            refresh_models,
            inputs=None,
            outputs=model_dropdown
        )
        
        process_btn.click(
            process_pdf,
            inputs=file_upload,
            outputs=process_output
        )
        
        clear_vector_btn.click(
            clear_vector_store,
            inputs=None,
            outputs=process_output
        )
        
        def make_chat_request(message, history, current_model):
            if not current_model:
                return history, "Please select an Ollama model first."
            
            response = chat_response(message, history, current_model)
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})
            return history, ""
        
        submit_btn.click(
            make_chat_request,
            inputs=[chat_input, chatbot, model_dropdown],
            outputs=[chatbot, chat_input]
        )
        
        chat_input.submit(
            make_chat_request,
            inputs=[chat_input, chatbot, model_dropdown],
            outputs=[chatbot, chat_input]
        )
        
        clear_chat_btn.click(
            reset_chat,
            inputs=None,
            outputs=[chatbot, chat_input]
        )
    
    return interface

if __name__ == "__main__":
    app = create_interface()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)