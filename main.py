from fastapi import FastAPI
from router import process_pdf, query_router

app = FastAPI(lifespan=query_router.lifespan)

app.include_router(process_pdf.router)
app.include_router(query_router.router)

