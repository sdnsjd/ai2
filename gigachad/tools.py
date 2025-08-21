import json
import random
import uuid
from langchain.tools import tool
from gigachad.embendings import init_retriever
from langchain_core.runnables import RunnableConfig
from datetime import datetime, timedelta, timezone


@tool
async def get_college_details(question: str) -> str:
    """
    Ищет информацию о колледже в векторной базе знаний.

    """
    print("get_college_details is called")
    retriever = init_retriever
    relevant_docs = await retriever.ainvoke(question)

    return str(relevant_docs) if relevant_docs else "Информация не найдена"


tools = [
    get_college_details,
]
