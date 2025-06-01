from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from src.OpenSearch.embedding import Embedding
from src.OpenSearch.configuration import OpenSearchIterations
from src.OpenSearch.calls_openai import create_openai_prompt, generate_openai_completion
from PyPDF2 import PdfReader
import os
import io
from dotenv import load_dotenv
import logging
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware
logger = logging.getLogger()
logger.setLevel(logging.INFO)

load_dotenv()
app = FastAPI()

amplify_url = os.getenv("AMPLIFY_URL")
origins = [
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "https://www.youtube.com"
]
if amplify_url:
    origins.append(amplify_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str


@app.post("/index-pdf")
async def index_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        e = Embedding()
        op = OpenSearchIterations()
        index_name = os.getenv("index_name")        
        reader = PdfReader(io.BytesIO(contents))
        pdf_content_splited = e.return_pdf_content(reader)
        chunks = e.split_text(pdf_content_splited)

        docs = []
        for i, chunk in enumerate(chunks):
            embedding = e.get_embedding(chunk)
            doc = {
                "_op_type": "index",
                "_index": index_name,
                "_id": f"doc_{i}",
                "_source": {
                    "titulo": file.filename,
                    "conteudo": chunk,
                    "embedding": embedding
                }
            }
            docs.append(doc)

        op.index_content(docs)
        return {"message": "PDF indexado com sucesso", "chunks": len(docs)}
    except Exception as e:
        import traceback
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask-model")
def ask_model(req: QuestionRequest):
    try:
        op = OpenSearchIterations()
        elasticsearch_results = op.get_elasticsearch_results(req.question)
        context_prompt = create_openai_prompt(elasticsearch_results, op.index_source_fields)
        openai_completion = generate_openai_completion(context_prompt, req.question)
        return {"answer": openai_completion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
handler = Mangum(app)