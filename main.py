from fastapi import FastAPI
from router import process_pdf, query_router

app = FastAPI(lifespan=query_router.lifespan)

app.include_router(process_pdf.router)
app.include_router(query_router.router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)