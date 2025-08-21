import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# telegram credentials
telegram_key = os.environ["TELEGRAM_CREDENTIALS"]

# gigachat credentials
gigachat_key = os.environ["GIGACHAT_CREDENTIALS"]
gigachat_key2 = os.environ["GIGACHAT_CREDENTIALS2"]