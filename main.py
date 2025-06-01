from fastapi import FastAPI
from router import process_pdf

app = FastAPI()

app.include_router(process_pdf.router)
