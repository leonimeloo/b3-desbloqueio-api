import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.pdf_router import pdf_router

from google.cloud import secretmanager
from google.oauth2 import service_account

credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not credentials_path or not os.path.exists(credentials_path):
    raise FileNotFoundError("GOOGLE_APPLICATION_CREDENTIALS não encontrado.")

if int(os.environ.get("PRODUCTION", 0)) == 1:
    logging_client = google.cloud.logging.Client()
    logging_client.setup_logging()
    manager = secretmanager.SecretManagerServiceClient()
    response = manager.access_secret_version(
        request={"name": credentials_path}
    )
    credenciais = service_account.Credentials.from_service_account_info(
        json.loads(response.payload.data.decode("UTF-8"))
    )
else:
    credenciais = service_account.Credentials.from_service_account_file(credentials_path)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://testes-desbloq.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(pdf_router)

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))