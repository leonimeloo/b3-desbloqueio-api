import openai, os, logging, google.cloud, json
from google.cloud import secretmanager
from google.oauth2 import service_account

openai.api_key = os.getenv("OPENAI_API_KEY")

credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not credentials_path or not os.path.exists(credentials_path):
    raise FileNotFoundError("GOOGLE_APPLICATION_CREDENTIALS não encontrado.")

def get_gcp_credentials():
    if int(os.environ.get("PRODUCTION", 0)) == 1:
        logging_client = google.cloud.logging.Client()
        logging_client.setup_logging()
        manager = secretmanager.SecretManagerServiceClient()
        response = manager.access_secret_version(
            request={"name": credentials_path}
        )
        return service_account.Credentials.from_service_account_info(
            json.loads(response.payload.data.decode("UTF-8"))
        )
    else:
        return service_account.Credentials.from_service_account_file(credentials_path)

credenciais = get_gcp_credentials()