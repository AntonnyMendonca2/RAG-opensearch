from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
import openai

class Embedding:
    def __init__(self):
        pass
        
    def num_tokens_from_string(self, string: str, encoding_name: str = "cl100k_base") -> int:
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(string))
    
    def return_pdf_content(self, pdf):
        full_pdf_in_text = ""
        for page in pdf.pages:
            full_pdf_in_text += page.extract_text() + "\n"
        return full_pdf_in_text
    
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