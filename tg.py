from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from settings import telegram_key
from gigachad.giga import CHECKPOINT_NS, agent, memorysave
from langgraph.checkpoint.base import ChannelVersions
from langchain_core.runnables import RunnableConfig
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from langchain_core.messages.utils import trim_messages, count_tokens_approximately

dp = Dispatcher()
bot = Bot(token=telegram_key)

def make_config(thread_id: str) -> RunnableConfig:
    return RunnableConfig(
        configurable={
            "thread_id": thread_id,
            "checkpoint_ns": CHECKPOINT_NS,
        }
    )

@dp.message(Command("start"))
async def start_bot(message: types.Message):
    menu = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/start")], [KeyboardButton(text="/reset")]],
        resize_keyboard=True,
    )

    welcome_text = """
    🌟 <b>Добро пожаловать в Находкинский государственный гуманитарно-политехнический колледж, я умный помощник абитуриента!</b> 🌟

    Я помогу вам с поступлением и отвечу на все вопросы.

    ✨ <b>Чем я могу помочь?</b> ✨

    🎓 <b>Специальности</b> - Расскажу о всех направлениях набора
    📑 <b>Документы и условия</b> - Объясню что нужно подготовить
    🎭 <b>Вступительные испытания</b> - Дату и формат испытаний
    📊 <b>Стоимость обучения</b> - Скажу о стоимости обучения

    🔹 <b>Как начать?</b> Просто спросите:
    • "Назови мне все специальности?"
    • "Какие специальности включают вступительные испытания?"
    • "Расскажи подробно о вступительных испытаниях по специальности - "Лечебное дело"?"
    • "Какие документы нужны для поступления?"
    • "Как подать документы для поступления?"

    📌 <i>Уже выбрали направление? Назовите его - расскажу детали!</i>

    📞 <b>Приемная комиссия:</b>
    ☎ Телефоны:
    • <code>8 (4236) 62-35-02</code>
    • <code>8 (4236) 74-34-71</code>
    • <code>8 (4236) 74-33-96.</code>

    ✉ E-mail: <code>nggpk@yandex.ru</code>

    Для сброса диалога нажмите /reset
    """

    await message.answer(text=welcome_text, reply_markup=menu, parse_mode="HTML")


@dp.message(Command("reset"))
async def reset_memory(message: types.Message):
    if not message.from_user:
        await message.answer(
            "Извините, я работаю только в личных чатах с пользователями."
        )
        return
    user_id = str(message.from_user.id)

    memorysave.delete_thread(user_id)
    await message.answer("Контекст Gigachat возобновлен! Чем могу помочь?")


@dp.message(F.text)
async def handle_message(message: types.Message):
    if not message.from_user:
        await message.answer(
            "Извините, я работаю только в личных чатах с пользователями."
        )
        return

    user_id = str(message.from_user.id)

    config = make_config(user_id)

    result = await agent.ainvoke(
        {"messages": [("user", message.text)]},
        config,
    )
    response = result["messages"][-1].content
    await message.answer(response)

    checkpoint_tuple = await memorysave.aget_tuple(config)
    if checkpoint_tuple and checkpoint_tuple.checkpoint:
        checkpoint = checkpoint_tuple.checkpoint.copy()
        metadata = checkpoint_tuple.metadata  # ✅ берём отсюда
        current_versions = checkpoint["channel_versions"]
        channel = "messages"
        prev_version_str = current_versions.get(channel, "0")
        prev_version = (
            int(str(prev_version_str).split(".")[0]) if prev_version_str else 0
        )
        new_version = prev_version + 1
        new_version_str = f"{new_version:032d}"
        checkpoint["channel_versions"][channel] = new_version_str
        new_versions: ChannelVersions = {channel: new_version_str}  # ✅ формируем здесь

        # обрезаем сообщения
        messages = checkpoint["channel_values"]["messages"]
        trimmed_messages = trim_messages(
            messages,
            strategy="last",
            token_counter=count_tokens_approximately,
            max_tokens=5000,
            start_on="human",
            end_on=("human", "tool"),
            include_system=True,
        )
        checkpoint["channel_values"]["messages"] = trimmed_messages
        await memorysave.aput(config, checkpoint, metadata, new_versions)

async def on_shutdown():
    await bot.session.close()
    await dp.storage.close()


async def run_tg():
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()
