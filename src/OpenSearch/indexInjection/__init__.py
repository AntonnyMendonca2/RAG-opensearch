from embedding import Embedding
from configuration import OpenSearchIterations
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os
load_dotenv()

e = Embedding()
op = OpenSearchIterations()
index_name = os.getenv("index_name")
reader = PdfReader("../../data/Santos.pdf")
pdf_content_splited = e.return_pdf_content(reader)
chunks = e.split_text(pdf_content_splited)

docs = []
for i, chunk in enumerate(chunks):
    embedding = e.get_embedding(chunk)
    print(f"Embedding tamanho: {len(embedding)}")
    print(f"Tipo de item: {type(embedding[0])}")
    doc = {
        "_op_type": "index",
        "_index": index_name,
        "_id": f"doc_{i}",
        "_source": {
            "titulo": "Documento Exemplo",
            "conteudo": chunk,
            "embedding": embedding
        }
    }
    docs.append(doc)

op.index_content(docs)