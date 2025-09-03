from langchain_gigachat.chat_models import GigaChat
from settings import gigachat_key
from langgraph.prebuilt import create_react_agent
from gigachad.tools import tools
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages.utils import trim_messages, count_tokens_approximately


CHECKPOINT_NS = ""
memorysave = MemorySaver()


giga = GigaChat(
    credentials=gigachat_key,
    model="GigaChat",
    verify_ssl_certs=False,
    timeout=1200,
    scope="GIGACHAT_API_B2B"
)


def pre_model_hook(state):
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=500,
        start_on="human",
        end_on=("human", "tool"),
        include_system=True,
    )
    return {"llm_input_messages": trimmed_messages}


system_prompt = """
Ты — виртуальный помощник абитуриента Находкинского государственного гуманитарно-политехнический колледжа(НГГПК). Твоя цель — помочь с поступлением.

### Правила:
 📘 Если спрашивают про детали колледжа — ВСЕГДА делай вызов:
   get_college_details(question)
   — Вопрос передавай точно, ничего не меняй.
   — Отвечай только на основе данных из функции.
   — Никогда не предлагай уточнять запрос и не упоминай внешние файлы/документы.
   — Если информация не найдена то повторно функцию не вызывай, а скажи, что по этому вопросу информации нет.
   
   


- Если тебе задают вопрос не связанный с темой колледжа ничего не делай,
а ответь "К сожалению, я специализируюсь только на вопросах о поступлении в колледж культуры. 🎭
По другим темам лучше проконсультироваться с моим другом — @gigachat_bot💡."

Можно приветствовать и отвечать на вежливые вопросы ("Как дела?" и т.п.).
"""

agent = create_react_agent(
    giga,
    tools=tools,
    prompt=system_prompt,
    checkpointer=memorysave,
    pre_model_hook=pre_model_hook,
)