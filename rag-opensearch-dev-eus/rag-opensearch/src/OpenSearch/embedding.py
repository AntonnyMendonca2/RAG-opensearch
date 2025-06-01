from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
import openai
from PyPDF2 import PdfReader


class Embedding:
    def __init__(self):
        pass
        
    def num_tokens_from_string(self, string: str, encoding_name: str = "cl100k_base") -> int:
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(string))
    
    def return_pdf_content(self, reader: PdfReader) -> str:
        full_text = ""
        for page in reader.pages:
            try:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            except Exception as e:
                print(f"Erro ao extrair texto da página: {e}")
        return full_text
    
    def split_text(self, full_pdf_in_text):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100, length_function=self.num_tokens_from_string
        )
        return splitter.split_text(full_pdf_in_text)
    
    def get_embedding(self, text: str, model="text-embedding-3-large"):
        response = openai.embeddings.create(
            input=text,
            model=model,
            dimensions=1536
        )
        return response.data[0].embedding