import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

telegram_key = os.environ["TELEGRAM_CREDENTIALS"]
gigachat_key = os.environ["GIGACHAT_CREDENTIALS"]
