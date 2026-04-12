import os
import time
import json
import random
import tempfile
import threading
import telebot
from datetime import datetime
import re
import requests
import shutil
from functools import wraps
import telebot.apihelper
import sys
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")


REQUIRED_CHAT_ID_PODVAL = -1002617724619
REQUIRED_CHAT_ID_DYMENKO = -1002719790558

def is_member(user_id: int, chat_id: int) -> bool:
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        print(f"Ошибка проверки членства в {chat_id}:", e)
        return False

def require_podval(func):
    def wrapper(message, *args, **kwargs):
        thread_id = getattr(message, "message_thread_id", None)

        if not is_member(message.from_user.id, REQUIRED_CHAT_ID_PODVAL):
            bot.send_message(
                chat_id=message.chat.id,
                text="【⛔】• Мы конечно не просим тебя подписатся на дохера мусорных каналов, ботов и чатов, но на один наш хотя бы: https://t.me/+NXaXK5OZ4DZlNTAy",
                message_thread_id=thread_id
            )
            return
        return func(message, *args, **kwargs)
    return wrapper


def require_dymenko(func):
    def wrapper(message, *args, **kwargs):
        thread_id = getattr(message, "message_thread_id", None)

        if not is_member(message.from_user.id, REQUIRED_CHAT_ID_DYMENKO):
            bot.send_message(
                chat_id=message.chat.id,
                text="【⛔】• Давай ты как мужик подпишешься на лучший канал по angry birds https://t.me/AngryBirdsMedia",
                message_thread_id=thread_id
            )
            return
        return func(message, *args, **kwargs)
    return wrapper


def require_topic(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        data = load_data()


        allowed_topics = data.get("allowed_topics", {})


        allowed_topic = allowed_topics.get(str(message.chat.id), None)


        current_topic = getattr(message, "message_thread_id", None)


        if allowed_topic is None:
            return func(message, *args, **kwargs)

        try:
            chat_info = bot.get_chat(message.chat.id)
            is_forum = getattr(chat_info, "is_forum", False)
        except Exception:
            is_forum = False


        if not is_forum:
            return func(message, *args, **kwargs)


        if current_topic == allowed_topic:
            return func(message, *args, **kwargs)


        bot.send_message(
            message.chat.id,
            "⚠️ Брат, теперь команды работают только в закреплённой теме.\n"
            "Тут чат для общения. Общайся спокойно.",
            parse_mode="HTML",
            message_thread_id=current_topic
        )
        return

    return wrapper








def _thread_id_of(message):
    return getattr(message, "message_thread_id", None)


COOLDOWN_SECONDS = 4 * 60 * 60
DATA_FILE = "case_data.json"


RARITY_WEIGHTS = {
    "Эксклюзивная I степени": 0,
    "Эксклюзивная II степени": 0,
    "Эксклюзивная III степени": 0.001,
    "Великоимператорская": 0.1,
    "Царская": 1,
    "Легендарная": 4,
    "Мифическая": 5,
    "Эпическая": 15,
    "Сверхредкая": 20,
    "Редкая": 25,
    "Обычная": 30,
}

SCORE_WEIGHTS = {
    "Эксклюзивная I степени": 0,
    "Эксклюзивная II степени": 0,
    "Эксклюзивная III степени": 0,
    "Великоимператорская": 1000,
    "Царская": 100,
    "Легендарная": 50,
    "Мифическая": 45,
    "Эпическая": 20,
    "Сверхредкая": 10,
    "Редкая": 5,
    "Обычная": 1,
}


CARDS = [
   {"id": "o1", "name": "Классический Кабаненко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/gcQXdgjZ/Bez-nazvania1848-20260213192220.png"},
{"id": "o2", "name": "Голограмма", "rarity": "Обычная", "image_url": "https://i.postimg.cc/pXPrJr0c/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213194542.png"},
{"id": "o3", "name": "Лысенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/sDKX6zqR/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213200639.png"},
{"id": "o4", "name": "Торговец", "rarity": "Обычная", "image_url": "https://i.postimg.cc/pXkTGv4n/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213200419.png"},
{"id": "o5", "name": "Санта Клаусенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/9McKN6vW/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213200921.png"},
{"id": "o6", "name": "Сыренко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/fLMpgG6L/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213201108.png"},
{"id": "o7", "name": "Неправильный формат файла", "rarity": "Обычная", "image_url": "https://i.postimg.cc/gJ4Q9MWj/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213201416.png"},
{"id": "o8", "name": "Пчеленко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/rpTqMYvn/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213204055.png"},
{"id": "o9", "name": "Пузыренко", "rarity": "Обычная", "image_url": " https://i.postimg.cc/NMJt8G5h/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213204705.png"},
{"id": "o10", "name": "Гуленко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/9McKN6vC/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213200122.png"},
{"id": "o11", "name": "Клоуненко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/DwQC7RPN/Без_названия1848_20260213230052.png"},
{"id": "o12", "name": "Многокабание", "rarity": "Обычная", "image_url": "https://i.postimg.cc/T3jkTBJZ/Без_названия1848_20260213230145.png"},
{"id": "o13", "name": "Беззубенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/76s41Pbp/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213205039.png"},
{"id": "o14", "name": "Ботаненко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/3NpXnDLB/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213215848.png"},
{"id": "o15", "name": "Вишненко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/vm9Nxcy5/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213211044.png"},
{"id": "o16", "name": "Гидроцефал", "rarity": "Обычная", "image_url": "https://i.postimg.cc/hjyn84fg/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213205941.png"},
{"id": "o17", "name": "Каб - Mango Mango Mango", "rarity": "Обычная", "image_url": "https://i.postimg.cc/SxLZmHG4/Без_названия1848_20260213230628.png"},
{"id": "o18", "name": "Пикселенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/0yz3xVHt/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213210614.png"},
{"id": "o19", "name": "Доскенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/7ZTkXPD2/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1862_20260217150421.png"},
{"id": "o20", "name": "Огузокенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/GhkBkPWq/Без_названия1848_20260213211740.png"},
{"id": "o21", "name": "Зомбенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/Yq9DfXkL/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213211948.png"},
{"id": "o22", "name": "ЕА-енко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/PqZRvPHZ/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213211541.png"},
{"id": "o23", "name": "Пельменко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/4djv611Y/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213213132.png"},
{"id": "o24", "name": "Анонименко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/sDN6npDP/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213212600.png"},
{"id": "o25", "name": "Дедпул", "rarity": "Обычная", "image_url": "https://i.postimg.cc/h471SHSM/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213213440.png"},
{"id": "o26", "name": "Дядя Джефф", "rarity": "Обычная", "image_url": "https://i.postimg.cc/3wKtN9Lk/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260214002801.png"},
{"id": "o27", "name": "Под прицелом", "rarity": "Обычная", "image_url": "https://i.postimg.cc/s2VTxKnR/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260214075808.png"},
{"id": "o28", "name": "Алюминий", "rarity": "Обычная", "image_url": "https://i.postimg.cc/yYndQKtx/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213194753.png"},
{"id": "o29", "name": "Токсик", "rarity": "Обычная", "image_url": "https://i.postimg.cc/02ZQWvFP/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213200534.png"},
{"id": "o30", "name": "Ангеленко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/44hQJrJL/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213220103.png"},
{"id": "o31", "name": "Рентгененко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/mZV69xxr/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213212227.png"},
{"id": "o32", "name": "Строителенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/8C1ZcwZ2/Без_названия1848_20260213231129.png"},
{"id": "o33", "name": "Лучникенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/pLPfJrK8/Без_названия1848_20260213220556.png"},
{"id": "o34", "name": "Арктический Кабаненко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/zGwdq4Fd/Без_названия1848_20260213225951.png"},
{"id": "o35", "name": "Художник", "rarity": "Обычная", "image_url": "https://i.postimg.cc/65rVZn4c/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213221128.png"},
{"id": "o36", "name": "Граффитенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/BnJTBb2T/Без_названия1848_20260213221325.png"},
{"id": "o37", "name": "Наш Слоник", "rarity": "Обычная", "image_url": "https://i.postimg.cc/jjHr08DR/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213221500.png"},
{"id": "o38", "name": "Шарик", "rarity": "Обычная", "image_url": "https://i.postimg.cc/PxdntmD8/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213222420.png"},
{"id": "o39", "name": "Кредитенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/V6zPYjt9/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213222115.png"},
{"id": "o40", "name": "Димека", "rarity": "Обычная", "image_url": "https://i.postimg.cc/qRQVgzcZ/Без_названия1848_20260213222758.png"},
{"id": "o41", "name": "Тыквенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/qRQVgzcZ/Без_названия1848_20260213222758.png"},
{"id": "o42", "name": "Хулиган", "rarity": "Обычная", "image_url": "https://i.postimg.cc/rmgXzKCF/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213222939.png"},
{"id": "o43", "name": "Баканенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/6QrNJH8t/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213221741.png"},
{"id": "o44", "name": "Пейнтенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/2SdHCg74/Без_названия1848_20260213225438.png"},
{"id": "o45", "name": "Пубертатенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/Y0y5fZs4/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213223205.png"},
{"id": "o46", "name": "Кабаненко с динамитом", "rarity": "Обычная", "image_url": "https://i.postimg.cc/JzC6VRZp/Без_названия1848_20260213225137.png"},
{"id": "o47", "name": "Кабаненко с копьём", "rarity": "Обычная", "image_url": "https://i.postimg.cc/RCJJ0xXq/Без_названия1848_20260213225109.png"},
{"id": "o48", "name": "Кабаненко с битой", "rarity": "Обычная", "image_url": "https://i.postimg.cc/dVcHPJrd/Без_названия1848_20260213225039.png"},
{"id": "o49", "name": "Костенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/jjNFnLTQ/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213211227.png"},
{"id": "o50", "name": "Фейковый Рэденко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/ZKd7MW9Q/Без_названия1848_20260213224458.png"},
{"id": "o51", "name": "Торрентенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/XY6HSndw/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213224643.png"},
{"id": "o52", "name": "Лунатикенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/vTBRnb37/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213223416.png"},
{"id": "o53", "name": "Лунатикенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/vTBRnb37/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213223416.png"},
{"id": "o54", "name": "Кляренко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/RZ4WG69W/Без_названия1848_20260213224236.png"},
{"id": "o55", "name": "Свинки Гамми", "rarity": "Обычная", "image_url": "https://i.postimg.cc/KvP7TB3b/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213220359.png"},
{"id": "o56", "name": "Бомженко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/qqZPXS5x/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213223628.png"},
{"id": "o57", "name": "Гладкий Кабаненко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/5tBDg4Kg/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213200255.png"},
{"id": "o58", "name": "Ретроенко", "rarity": "Обычная", "image_url": "https://i.postimg.cc/J7B5191x/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213215622.png"},
{"id": "o59", "name": "Блад и крип", "rarity": "Обычная", "image_url": "https://i.postimg.cc/sDh6NMQB/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213224824.png"},
{"id": "o60", "name": "Кабаненко с Киркой", "rarity": "Обычная", "image_url": "https://i.postimg.cc/QdZ4Gj1x/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1848_20260213225013.png"},
    {"id": "r1", "name": "Элитный Дименко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/MDNCVSLj/0f49483b-b391-427f-aa9e-91e0ce9f1821.png"},
    {"id": "r2", "name": "Жиденко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/LdYN3848/2ca1bdbf-0c70-4d15-8d1a-706677c3dc74.png"},
    {"id": "r3", "name": "Куплиненко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/wNB70W24/e706bdab-f7c1-40ff-a0d5-8847fc12276e.png"},
    {"id": "r4", "name": "Шевцовенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/1GYw9Fkq/b6ae066d-93b3-4c57-be62-19304b4bfd82.png"},
    {"id": "r5", "name": "Перс Дименко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/JRkX5sdT/36157630-9b74-41c9-9da9-ec86278f199d.png"},
    {"id": "r6", "name": "Рот занят", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/4ZmDpb1H/44e1ffda-2df7-4e99-92f8-7f90a6779209.png"},
    {"id": "r7", "name": "Гартик Дименко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/gLmdbv89/a7d59230-7143-4a51-b0b0-b4c228d9d6e0.png"},
    {"id": "r8", "name": "Невидименко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/TqPFYr8W/133d0056-1458-48e1-bf53-6fc99c6256a7.png"},
    {"id": "r9", "name": "Негативенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/Vc8nD2HX/IMG-20251017-155218-840.png"},
    {"id": "r10", "name": "Спаменко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/MDDLrWLB/ea2d20bf-8faa-4bf7-9691-5468921509d8.png"},
    {"id": "r11", "name": "YNовец", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/tkP40qS/eba8c801-93c7-40ad-a509-20591536bc23.png"},
    {"id": "r12", "name": "Фриманенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/HfVQybyp/ef6c9caf-d744-4c2a-87f1-3e9855facfe8.png"},
    {"id": "r13", "name": "Сененко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/KjkXRvYw/9a75b293-dc81-464e-831c-444c9db9aab6-1.png"},
    {"id": "r14", "name": "Феденко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/6cydMrSS/36775b1c-8982-4cc3-bbc9-1b1ddbe33d1d.png"},
    {"id": "r15", "name": "Мумиенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/1f7jm2vz/4e849350-8a44-45b7-a0c9-247861fb15ee.png"},
    {"id": "r16", "name": "Рак", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/0j0rVMTz/fb7059b5-eef5-4e9f-9b23-71c4f1cdbfd2.png"},
    {"id": "r17", "name": "Кловеренко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/ymJV8v16/e21e19d8-53ea-402a-82ff-e2a0f300065b.png"},
    {"id": "r18", "name": "Эль Димстинг", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/S41K1C9T/0676db6c-3f9b-4383-801c-109edf7cc35d.png"},
    {"id": "r19", "name": "Дым Примо", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/Vd0VdHq/8b1be8e0-1a23-4c3e-af30-472e23426740.png"},
    {"id": "r20", "name": "Дурка", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/gLPfDjmx/d41abbe0-4100-4395-b01b-9ece94cff6ed.png"},
    {"id": "r21", "name": "Дименка в клетке", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/RpqsT52c/deeeb850-a393-4e30-8720-cd550e1362b1.png"},
    {"id": "r22", "name": "Иноагент Росситиенко 17", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/rG5NPhd9/1ddf6017-5783-4965-8b03-de31dae9faf8.png"},
    {"id": "r23", "name": "Фроггенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/qLmHMzQG/a018ffdf-26b3-4dcd-8eda-98df1314e112.png"},
    {"id": "r24", "name": "Пластеленко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/6c0Z42JZ/b0642654-6fed-4e2e-84ff-f7a7989d3d97.png"},
    {"id": "r25", "name": "Скибиди Сигменко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/n8c9qXV0/b9455a21-e1b1-4b7b-81c9-c444cb34fdb1-1.png"},
    {"id": "r26", "name": "Дым и енко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/9mP5cQzg/1833555e-b656-4773-8ba8-5bf3760f8879.png"},
    {"id": "r27", "name": "Лудоманенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/Jw8v6RH3/415d0068-d021-421b-a394-968ed9df2222.png"},
    {"id": "r28", "name": "Туристенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/VW80Rr2f/915b4453-8b79-4bd3-9257-4707f44c188b-1.png"},
    {"id": "r29", "name": "Пугливый Дым", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/Nnjcy6BH/2a2fe768-df89-4571-90ef-0801ebb9a4c6.png"},
    {"id": "r30", "name": "Амальгаменко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/G3J4snnm/269445a6-708e-4cfa-91d1-2f4e22b3fcac.png"},
    {"id": "r31", "name": "Бесячий Дым", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/KcnG2JpY/72384da8-2473-488d-9bc3-804d9deec8fe.png"},
    {"id": "r32", "name": "Архитекторенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/GfMcxRZc/9d96abcd-5e7d-4422-ae2a-10fe8080776a.png"},
    {"id": "r33", "name": "Пиццаненко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/n854rrqf/1c0c5f39-6e26-4250-8be1-83518a37aab0.png"},
    {"id": "r34", "name": "Тут скоро будет новая карта", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/gFWgMRhd/bc8eb7c7-3612-48dc-839e-f9ed8b0e94eb.png"},
    {"id": "r35", "name": "Соевый Дименко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/gFWgMRhd/bc8eb7c7-3612-48dc-839e-f9ed8b0e94eb.png"},
    {"id": "r36", "name": "Нигеренко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/1YV2Y5hf/908aa801-6916-4d7b-a8de-db508021e6d8.png"},
    {"id": "r37", "name": "Аксолотенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/prns2LwP/97de9618-3f90-4edb-83e7-ad93fedb3772.png"},
    {"id": "r38", "name": "Сушенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/nqz5bYrW/540169aa-5763-4150-877b-625c1941d72c.png"},
    {"id": "r39", "name": "Окнемид", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/SXXjFWNv/60ccb0d5-b68b-47ff-aa39-6fe491131a8a.png"},
    {"id": "r40", "name": "Обитатель дименко бэкрумс", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/PZZQHH5h/34164612-13fc-4dc7-8261-70efc9ac33ff.png"},
    {"id": "r41", "name": "Жуликенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/1GnWpZWr/3b212fbd-8344-4b8f-ae7e-c6808aaaa426.png"},
    {"id": "r42", "name": "Глаукома", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/5hg2CT2S/93956bb8-c9fa-47e1-ab86-2894191e8609-1.png"},
    {"id": "r43", "name": "HDенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/kgfz17TG/aec85607-5861-4333-8f15-ad8c38c06fdb-1.png"},
    {"id": "r44", "name": "Лысый", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/JwBTd5V9/315-20251109142358.png"},
    {"id": "r45", "name": "Лев Абрикосенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/7dJwsC64/316-20251124181516.png"},
    {"id": "r46", "name": "Дым Механик", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/YYF8XFn/IMG-20251213-123909-945.jpg"},
    {"id": "r47", "name": "Гыченко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/27hBxTpx/365-20251222235422.png"},
    {"id": "r48", "name": "ТЦКенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/5x9C0rLv/tckenko.png"},
    {"id": "s1", "name": "Шампиньоненко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/xqJ02JzF/0c051dfe-b94f-4962-a0b4-4a6d383e06be.png"},
    {"id": "s2", "name": "Кедамоненко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/xK30cBnG/d6bbbbad-cda4-4ae4-9a38-ec57f8a938f5.png"},
    {"id": "s3", "name": "Мистер Стейненко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/Y4g1zNyz/cbb2f748-ff6c-4c66-99d1-ba037d839a3a.png"},
    {"id": "s4", "name": "Кактусенко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/FLJnZySk/bf2b1a68-4671-4912-bf66-b56a2c9b558f.png"},
    {"id": "s5", "name": "Безумный Дейвенко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/0j1zyQ2y/a41ccf69-79ab-4d83-984c-24e51c1afdcf.png"},
    {"id": "s6", "name": "Хитрый Перец", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/W4dRfzS3/5dc34405-13aa-4fb9-b009-fe776cd125c3.png"},
    {"id": "s7", "name": "Эликсирный Дым", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/0pt34j1J/2e2bad87-6216-4904-a4a2-b798dd98a571.png"},
    {"id": "s8", "name": "Happy Tree Dimenkos", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/RTzLbLYQ/4da75116-8c49-4165-bfb7-09fdf8afabb2.png"},
    {"id": "s9", "name": "Кубенко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/8Dr4pG7y/902a48c2-d1a3-4836-ab14-9db0c5fd3ce7.jpg"},
    {"id": "s10", "name": "Угаденко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/7tVpqRnH/185af583-9856-4633-97ed-5ce2ac3c59ed.png"},
    {"id": "s11", "name": "Расчлененко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/35q4gkQz/c559273a-5f79-4d28-9944-84fcb9e737dd.jpg"},
    {"id": "s12", "name": "Бананенко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/BKtGNrx7/cd23986f-9557-4b64-88e7-9a98a523036b.png"},
    {"id": "s13", "name": "Оглушенный Дым", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/Mykc9gGt/40e3e270-9109-45f1-829a-78c8ccbb83de.png"},
    {"id": "s14", "name": "Штурмовенко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/RkwKRP3W/c9a4c6ab-c7e7-4779-8d14-f35b3363a211.png"},
    {"id": "s15", "name": "Плюшевенко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/k2VT1DpW/a7d117d6-32df-453d-9631-e7a679bd47c1.png"},
    {"id": "s16", "name": "Хог Райденко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/WWhsmgzZ/1137560c-09b6-405c-91c5-c598d7f7a5b5.png"},
    {"id": "s17", "name": "День независимости Греции", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/rRrCSq3C/388033fd-1d41-47ce-80ba-b8cc0960a03a.png"},
    {"id": "s18", "name": "Дымовуха", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/JFMY7n5J/1474-2-20251005003900.png"},
    {"id": "s19", "name": "Тут никогда не будет новой карты", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/Q7SLQ711/9e75a30c-ff2b-4a26-9a6b-c72713f162f9.jpg"},
    {"id": "s20", "name": "Загрузенко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/TM4h97Ff/bb7964a9-1289-4643-93cd-71082ca3ad27.png"},
    {"id": "s21", "name": "Флешбекенко", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/932rDZZ5/d4ac6a03-b5f7-438d-b081-e08a85b935fd.png"},
    {"id": "s22", "name": "Эль Витаминенко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/vx32m6hw/42d5afe7-148d-4beb-b715-5e047fad289f.png"},
    {"id": "s23", "name": "Бульбенко", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/zTqXY2f2/cf54325b-3ba8-449d-9768-950ed169c701.png"},
    {"id": "s24", "name": "Король Дименок", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/fz4fFbrt/2f0b5ad5-4248-4844-9c53-a2e3527bdff6.png"},
    {"id": "s25", "name": "Астродым", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/0R6CbGCJ/20251120212508.png"},
    {"id": "s26", "name": "Дименко на прозрачном фоне", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/pBcQw7dR/20251120212840.png"},
    {"id": "s27", "name": "Фиолетовый Дым", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/xKc45VRp/345-20251212015216.png"},
    {"id": "s28", "name": "Ъуъенко", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/yFMwkGdg/295-20251213203008.png"},
    {"id": "s29", "name": "Сигма Бимбенко", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/d05cWm9w/343-20251212024124.png"},
    {"id": "s30", "name": "Дым в ночном горшке", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/6JyttZjx/360-20251217222435.png"},
    {"id": "s31", "name": "Чернильный Дым", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/hRFwQ6CQ/355-20251215163205.png"},
    {"id": "s32", "name": "Дименко с ложкой", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/BHb4103K/357-20251217012828.png"},
    {"id": "s33", "name": "Плейсхолдер", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/BHb4103K/357-20251217012828.png"},
    {"id": "s34", "name": "Сулустаненко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/SwgqdtMb/355-20251215211615.png"},
    {"id": "s35", "name": "Киборг Джордженко", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/gZs0KNVd/355-20251215160553.png"},
    {"id": "s36", "name": "Шайлушаенко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/rGCJvYdN/361-20251217225350.png"},
    {"id": "s37", "name": "Крымская кружка", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/7xTKYyPP/335-20251215213719.png"},
    {"id": "s38", "name": "Мистер Пепперенко", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/bMZj6c4H/310-20251215215411.png"},
    {"id": "s39", "name": "Импенко", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/207sT1HF/355-20251215210951.png"},
    {"id": "s40", "name": "Снежный Дым", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/23bmnCFq/338-20251215220410.png"},
    {"id": "s41", "name": "Крысенко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/x8f30ywF/304.png"},
    {"id": "s42", "name": "Димпрессия", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/27284MxC/338-20251215220940.png"},
    {"id": "e1", "name": "Растаман", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/LdkcJCzf/1428-20250813232820.png"},
    {"id": "e2", "name": "Гассисключительный", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/DPfLYsTp/c24f61e8-b560-480f-b521-23a5d4b5b0e1.png"},
    {"id": "e3", "name": "Дугиненко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/8gttvvqF/0ef8bc81-7e79-4239-a5d1-2e29e65dd7d1.png"},
    {"id": "e4", "name": "Джоненко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/1Y7hf05V/c9fd3535-e5e2-4d35-92ff-9ed3c8e98658.png"},
    {"id": "e5", "name": "Мисс Циркуленко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/bRrXjqFv/34dbb1d3-ac2b-4377-b837-b84b22a2f0e8.png"},
    {"id": "e6", "name": "Диденко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/DgYSYX35/9d790150-9477-47c5-95df-602938ac70b8-1.png"},
    {"id": "e7", "name": "Глитченко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/60nRbYg7/8d99d496-c5fe-41e4-8b75-6f886cd42665.png"},
    {"id": "e8", "name": "Хентаенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/39BqWrz3/c6c2a453-0d6f-43da-8608-b82988145a15.png"},
    {"id": "e9", "name": "Чувакенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/ShLFMrx/e0f9390d-da26-465f-84c5-8bb8b9a18dbc.png"},
    {"id": "e10", "name": "Шефенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/7xHrNt9D/4f80f546-b46a-4c21-9936-800ac80fb5e2.png"},
    {"id": "e11", "name": "Картеленко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/60rxQQ7h/cfdcace9-dab9-481d-977b-b6fdb73afd7c.png"},
    {"id": "e12", "name": "Гойденко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/qLVBHp0c/3f98341c-8bb2-4f93-9ad2-45881c4d1f8c.png"},
    {"id": "e13", "name": "Дядя Дима", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/yFdrcX6Q/8e9ae518-7ce1-496d-bb40-efcfb33f82c5.png"},
    {"id": "e14", "name": "Щепик", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/XvKrbh5/b04aa115-47d3-4aa8-819b-3b837af84516.png"},
    {"id": "e15", "name": "Купитменко Дым-Венеролог", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/8nGKPJCD/c2f94ee7-37bd-4ac1-babf-ada911dff7a1.png"},
    {"id": "e16", "name": "Текстура не найдена", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/r2xDqF6Y/0674f87f-5ec0-4385-9ee4-b9dab8af0515.png"},
    {"id": "e17", "name": "Аналоговый Хорроренко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/GQkjNwgJ/27514051-e7cb-42e1-84e9-ea2f8263248e.png"},
    {"id": "e18", "name": "Дименко на графике функций", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/TMsstX4y/b428f1c0-b13b-45ca-badd-14ec272cef92.png"},
    {"id": "e19", "name": "Дименковский бур", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/Zz4tPJDw/9cfea299-342c-477d-b099-9b1cb8a4a31d.png"},
    {"id": "e20", "name": "Атоменко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/pBWqtmJd/8679d37e-6f39-4f71-8edb-867a11ed4954.png"},
    {"id": "e21", "name": "ДЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫМ", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/sdywzqQ5/63e0bcd1-fd30-4f4f-ab02-e4670fb7c8ea.png"},
    {"id": "e22", "name": "Чуркенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/N6kh8NSh/37d1ca14-b520-4f63-b117-07ea568ab0c1.png"},
    {"id": "e23", "name": "Мелстроенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/PzVwHzJ3/300-20251119103808.png"},
    {"id": "e24", "name": "Дименко (made in China)", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/fV62n6bd/b68a8cb7-4111-4055-a735-c1d8a858670a.png"},
    {"id": "e25", "name": "EXE.енко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/hRXsv4n2/558009d1-7bc6-4143-8bcc-8e1cc175cc79.jpg"},
    {"id": "e26", "name": "Дуо Растений", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/6c65XwPB/a2cbe691-3b6e-41cc-b2d5-89a45d4f83b5.png"},
    {"id": "e27", "name": "Криповенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/s4vxC5J/0c8458ab-db0d-456e-843d-f6049c9974f1-1.png"},
    {"id": "e28", "name": "Bad Dimenko", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/4RDqdptK/8253b871-badc-46a8-a49d-4f579345d80b.png"},
    {"id": "e29", "name": "Старик Рокусенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/99BZfSc7/9fc27259-376c-4e44-ac01-7a99813f4647.png"},
    {"id": "e30", "name": "Эйнштейненко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/8npWvZF4/cc138967-0215-43a3-9578-0a02356d4aa0.png"},
    {"id": "e31", "name": "Элитные Дымы", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/rKjxGQXR/91b2f81e-79a0-4b3c-a24b-1f581024e931.jpg"},
    {"id": "e32", "name": "Сыненко", "rarity": "Эпическая",
    "image_url": "https://i.ibb.co/PzsF3Cw5/fc14689e-328a-43a4-a412-a82e3e6cf717.png"},
    {"id": "e33", "name": "Майк Маерсенко", "rarity": "Эпическая",
    "image_url": "https://i.ibb.co/Nn75HWxg/317-20251115142113.png"},
    {"id": "e34", "name": "D2-C3Pенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/Kc8xv7s8/328-20251122205639.png"},
    {"id": "e35", "name": "Это Енко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/b5zy39Xn/20251120212447.png"},
    {"id": "e36", "name": "Яичко Владенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/Xx0QB3th/Untitled381-20251123010200.png"},
    {"id": "e37", "name": "Вудиенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/qMR3SCgB/380-20260102161506.png"},
    {"id": "e38", "name": "Дименко в @ostrovkreb", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/SDnmv3PX/346-20260102152429.png"},
    {"id": "e39", "name": "Партенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/fGdV2XHm/330-20251212011447.png"},
    {"id": "e40", "name": "Дым 31 с ноутбуком", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/FL8Mz9j6/336-20251217210728.png"},
    {"id": "e41", "name": "Nullенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/kVw9qbq6/358-20251217205253.png"},
    {"id": "e42", "name": "Шаверминенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/W49FGq8M/334-20251216224310.png"},
    {"id": "m1", "name": "Члеренко", "rarity": "Мифическая",
     "image_url": "https://i.ibb.co/n8B5PV8j/354.png"},
    {"id": "m2", "name": "BEST DIMGAME", "rarity": "Мифическая",
     "image_url": "https://i.ibb.co/F4PDyYRF/341-20251231183755.png"},
    {"id": "m3", "name": "Миндикенко", "rarity": "Мифическая",
     "image_url": "https://i.ibb.co/bMLczmNq/353-20251215001056.png"},
    {"id": "m4", "name": "Давидменко", "rarity": "Мифическая",
     "image_url": "https://i.ibb.co/ksq392pJ/356-20260102224649.png"},
    {"id": "m5", "name": "Иван Вортенко", "rarity": "Мифическая",
     "image_url": "https://i.ibb.co/Gv29VzZx/367-20251222214904.png"},
    {"id": "m6", "name": "Ката Барсенко", "rarity": "Мифическая",
     "image_url": "https://i.ibb.co/Fb9HwzMJ/366-20251223003451.png"},
    {"id": "m7", "name": "Маффенко", "rarity": "Мифическая",
     "image_url": "https://i.ibb.co/207Yc4S6/371-20260102150634.png"},
    {"id": "m8", "name": "Бебраменко", "rarity": "Мифическая",
     "image_url": "https://i.ibb.co/60bp7mfj/IMG-20251230-225810-517.jpg"},
   {"id": "m9", "name": "Цезиц", "rarity": "Мифическая",
     "image_url": "https://i.ibb.co/207Yc4S6/371-20260102150634.png"},
    {"id": "m10", "name": "Платоненко", "rarity": "Мифическая",
    "image_url": "https://i.ibb.co/PZb9r4Mp/362-20251231131624.png"},
    {"id": "l1", "name": "Груша", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/0ydqqRZ2/e7ae2c54-6af7-40e4-bc95-c36bac283b20.png"},
    {"id": "l2", "name": "Летовенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/Z6cm0FR8/2d82aa70-507a-4e7a-9b07-26329e084caf.png"},
    {"id": "l3", "name": "Кейканенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/FkWDK2Cc/4a403185-fa55-4e71-98a9-63f75c5e141c.png"},
    {"id": "l4", "name": "Херобренко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/nNYsxbM9/2757c639-229b-4b86-81cf-d9e3b6315139.png"},
    {"id": "l5", "name": "Супер Дименко Мен", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/wNfhQ9Gp/8b3ed4a3-a272-40c1-8fad-0ec82d3a80f7-1.png"},
    {"id": "l6", "name": "Крымский портенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/k6qh5Chc/ce834096-1fd3-4957-ba69-05ec4b1136a3.png"},
    {"id": "l7", "name": "Кобенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/nMCdr9Zb/cbfed704-2ec2-4f57-b7ec-68ea8adda283.png"},
    {"id": "l8", "name": "Кратосенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/RGXmshG2/83d63fc8-5d96-4110-853d-10ba64e1de49.png"},
    {"id": "l9", "name": "Ретро Дименко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/3PvHPBw/5a47ec13-08d8-41e8-ae0f-fad7a03d4356.png"},
    {"id": "l10", "name": "Васап Бро", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/1JJrNZnn/3b6dfa64-db5c-42ab-9c63-3eb15f98c146.png"},
    {"id": "l11", "name": "Макс Хедруменко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/7dxKnKZQ/09d011e6-6434-429b-a17b-4e13de7d9e79.png"},
    {"id": "l12", "name": "Малышенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/DPBSyFC8/55b2faf3-be7a-4ec9-b82f-eab038f6bd7b-2.png"},
    {"id": "l13", "name": "Дилденко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/4wzTrVMK/7f35f322-6f64-45b9-8241-5085d1416613-3.png"},
    {"id": "l14", "name": "Старец Мерселенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/k6cLT1cj/7951e19d-d6df-4c5a-98ab-395904e3cff6-1.png"},
    {"id": "l15", "name": "Санс Серов", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/dwtb9x0B/b3606f4d-6d46-40e7-83d7-1c501a3884af.png"},
    {"id": "l16", "name": "Мориартенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/6JGpRznk/084e582b-c23c-434b-a0d6-5ed28278c7c1.png"},
    {"id": "l17", "name": "Лермонтенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/SwnXQyW3/9ae17d98-bc37-41af-938e-6607c964a714.png"},
    {"id": "l18", "name": "Аркаденко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/dwbVDzy5/b48fa888-69de-4c0d-bca4-9b245b698d12.png"},
    {"id": "l19", "name": "Вселенненко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/GjDyGDW/27bf7e73-3509-448b-b9a8-16be8cafa296.png"},
    {"id": "l20", "name": "Вайомингский дым", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/FLSY8C4Q/e5b0d03d-59c0-4305-9758-a0a57c449247.png"},
    {"id": "l21", "name": "4dimenko", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/1tZyV0SM/db7937ba-00e6-4210-84aa-60876fe35cbf.png"},
    {"id": "l22", "name": "Жертва Демократиенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/q3sBnzMR/63255c3b-6e88-46f8-a1ff-684a2895914c-1.png"},
    {"id": "l23", "name": "Палпатенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/Mxxw7zbV/03b26eb5-2046-402c-83cf-a9b009808d93.png"},
    {"id": "l24", "name": "Усавиченко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/93h0v2Yq/24915a9b-b43d-49d1-a98b-e2f83b7bb25d.png"},
    {"id": "l25", "name": "【🃏】• Соизвольте-съ принять арканъ! Вамъ выпала новая карта: Димѣнко Правилусъ(Легендарная)","rarity": "Легендарная",
     "image_url": "https://i.ibb.co/nN9ThJzF/623430a6-cea2-4c8d-9250-db6a29f3bb62.png"},
    {"id": "l26", "name": "Мортенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/LzFBLSyf/18e4246c-eb18-4c92-9892-08ceab0d0f39.png"},
    {"id": "l27", "name": "Металенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/0Rn3358g/1474-20250912174841.png"},
    {"id": "l28", "name": "Ержан, ты где?", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/fYWhS7DQ/f55613d2-ceaf-4ab7-8811-4aaf4c91bfec.png"},
    {"id": "l29", "name": "Уолтер Бланко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/BKH7ZWMg/04a90519-78de-4876-a4f1-1c66c0a54687.png"},
    {"id": "l30", "name": "Мегадым", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/MkwcVcMR/923d006a-034e-405c-9600-d0120ea16fe6.png"},
    {"id": "l31", "name": "Генеральские котлы", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/fJsLR7G/3dbed048-6aaf-426c-89b7-88ae242c1fdf.png"},
    {"id": "l32", "name": "Император Духов", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/t14DH91/4efd6181-0bbe-4339-b9df-c132e0441ce7.png"},
    {"id": "l33", "name": "Параппыченко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/wNvNH72L/9466bfd7-ef12-4cf2-9fdf-8ba8b1ff44e0.png"},
    {"id": "l34", "name": "Элитный мегапаровоз", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/mVDPh8ry/4ecb219a-df90-4929-926f-88e874328482.png"},
    {"id": "l35", "name": "Свинплейсенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/BHpWSh76/e3b083da-3de7-4f65-b94a-2ba4ef3cf99b.png"},
    {"id": "l36", "name": "Никенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/nMrxrKn2/8d64cef1-1e39-415e-ad47-6696497c245f-1.png"},
    {"id": "l37", "name": "Мистер Пеппер", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/KQVV8JK/20251122121720.png"},
    {"id": "l38", "name": "Аномаленко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/KQVV8JK/20251122121720.png"},
    {"id": "l39", "name": "Русишенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/XxqsgQnV/327.png"},
    {"id": "l40", "name": "Плюхенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/hxrfvz1g/322-20251212011556.png"},
    {"id": "l41", "name": "Эндеренко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/FLnwRBf2/344-20251212021938.png"},
    {"id": "l42", "name": "НБенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/d4BSCWgn/340-20251215023013.png"},
    {"id": "c1", "name": "Мелкий", "rarity": "Царская",
     "image_url": "https://i.ibb.co/d4fXnpqn/1428-20250813233209.png"},
    {"id": "c2", "name": "Южный Паркенко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/23PQQDNp/6d152fa3-17b7-44d2-b8f7-f58315ccf8a4.png"},
    {"id": "c3", "name": "Клэренсенко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/tT25Ftk0/9bb114cb-650b-438a-8861-127d5f7a7101.png"},
    {"id": "c4", "name": "Ариеценко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/N09X0Ry/1d469294-d10a-4d53-a9d1-d2e2eeac64fa-1.png"},
    {"id": "c5", "name": "ВОенко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/jZ1XkXqC/1d1ea2d2-09ec-48ad-838f-5a293c7715b1.png"},
    {"id": "c6", "name": "Грек", "rarity": "Царская",
     "image_url": "https://i.ibb.co/pvQd7dRC/b39d780f-59f1-43fb-926f-41c99667af45-1.png"},
    {"id": "c7", "name": "Гостенко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/whqp6fhz/a595913a-40e5-4b1e-9fad-08824f6bd0ab.png"},
    {"id": "c8", "name": "Дым 3Dименко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/jkJ6QCpY/8c7ca436-7ad5-401a-a267-26e9e49fb8d7.png"},
    {"id": "c9", "name": "Архангел", "rarity": "Царская",
     "image_url": "https://i.ibb.co/XxqRPXkW/e8b6ab30-ffb2-48b2-b190-d2d9fde2542a.png"},
    {"id": "c10", "name": "Житель Сити 17енко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/84dCjQDS/8df5c115-9328-42c2-bebe-921925e34888-1.png"},
    {"id": "c11", "name": "Hotline Dimenko", "rarity": "Царская",
     "image_url": "https://i.ibb.co/GQvFJ6Kg/575a84bf-bc5f-4fcd-bf07-a74e953988fa.png"},
    {"id": "c12", "name": "Старый пост с двача", "rarity": "Царская",
     "image_url": "https://i.ibb.co/HLcRqq7W/3911e5d9-2d5c-4065-a047-a2d0852c9b23.png"},
    {"id": "c13", "name": "Friday Night Dimenko", "rarity": "Царская",
     "image_url": "https://i.ibb.co/TMtMZggw/05dd3845-c66d-4699-8cd1-3e5aac395dce.png"},
    {"id": "c14", "name": "Двуликенко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/7NKKWdwj/7fdaa990-6bc7-4b76-801b-af4bb1d14268.png"},
    {"id": "c15", "name": "Кожаное дымцо", "rarity": "Царская",
     "image_url": "https://i.ibb.co/8n96M2z1/317-20251115142129.png"},
    {"id": "c16", "name": "Фидонетенко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/wZZXj8hq/314-20251106223754.png"},
    {"id": "c17", "name": "Wazzupенко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/Qv82crNJ/317-20251115142123.png"},
    {"id": "c18", "name": "Кирпиченко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/DH4PpKyG/261-20251116124913.png"},
    {"id": "c19", "name": "Ну это... Как его... А! Дэбиленко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/XrfZ460t/20251117214808.png"},
    {"id": "c20", "name": "Цезиенко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/1tn5GybV/35-20251129213417.png"},
    {"id": "c21", "name": "Дименко Младший", "rarity": "Царская",
     "image_url": "https://i.ibb.co/fV8RrFWd/313-20251124221031.png"},
    {"id": "c22", "name": "Желтобрюхенко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/2Ynkk9n7/275-20251115180721.png"},
    {"id": "c23", "name": "Мерселенко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/jZPs7TtV/331-1.png"},
    {"id": "c24", "name": "Эмиленко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/vvrVtPHH/348-20251212003115.png"},
    {"id": "c25", "name": "Келлеренко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/xpkhFtF/333-20251215154944.png"},
    {"id": "c26", "name": "Брялокенко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/ds4MHw6p/339-20251215021238.png"},
    {"id": "v1", "name": "Дименко", "rarity": "Великоимператорская",
     "image_url": "https://i.ibb.co/jv2cYbfp/350-20251211212947.png"},
    {"id": "v2", "name": "Гектор Поркенко", "rarity": "Великоимператорская",
     "image_url": "https://i.ibb.co/Y4rnS3CN/40a5cafa-2462-436c-9c71-06046f8eb2a2.png"},
    {"id": "ve1", "name": "Губенко", "rarity": "Эксклюзивная I степени",
     "image_url": "https://i.ibb.co/XZ3zRkQt/05a707ce-1dc1-4a6d-a1cb-d4d71ab59fdf.png"},
    {"id": "ve2", "name": "Димнайт, яйца, я Дым", "rarity": "Эксклюзивная I степени",
     "image_url": "https://i.ibb.co/YTjFN6Lb/2ea87918-3218-40e4-8e57-7d81c058e2fb.png"},
    {"id": "ve3", "name": "Луменко", "rarity": "Эксклюзивная I степени",
     "image_url": "https://i.ibb.co/v7MqyDJ/d7749886-b391-48bf-b4a5-293238a4baef.png"},
    {"id": "ve4", "name": "56 лет ученикенко", "rarity": "Эксклюзивная I степени",
     "image_url": "https://i.ibb.co/4ZsFSnQ4/7a1442ba-4b14-41c4-a871-521072db6577.png"},
    {"id": "ve5", "name": "Барсукенко", "rarity": "Эксклюзивная I степени",
     "image_url": "https://i.ibb.co/5gw5KxNT/5ccd9315-4536-463b-a5a7-f2349f9b625a.png"},
    {"id": "ve6", "name": "Интерненко. Прайм Версия", "rarity": "Эксклюзивная I степени",
     "image_url": "https://i.ibb.co/KxCtHVXS/c1c65afd-f1eb-4c74-b0d1-b735ce109518.png"},
    {"id": "ve7", "name": "Дименко/Дым. Эксклюзивная Версия", "rarity": "Эксклюзивная I степени",
     "image_url": "https://i.ibb.co/9H0zmXgX/396692cb-601f-4ea3-87a6-b5537076acae.png"},
    {"id": "ve8", "name": "56 лет ученикенко. Первоначальная версия", "rarity": "Эксклюзивная I степени",
     "image_url": "https://i.ibb.co/XxnRvr6H/7e20b3fc-3425-4188-9dda-6976e7ca0227.png"},
    {"id": "ve9", "name": "Мифическая редкость", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/1tdBST8k/e81cc083-ab16-4716-aba3-d5f470c62c4b.jpg"},
    {"id": "ve10", "name": "Универсальная редкость", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/s9r1RXkW/50066aab-ad19-4df8-bccb-dbf35f3aff54.jpg"},
    {"id": "ve11", "name": "Дым Сидиус (до добавления в бота)", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/tk2bbLp/9f38f833-1dc2-436b-bed3-1443498d8836.png"},
    {"id": "ve12", "name": "Семён Жеваник", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/xtFvTgwS/5bb4f673-feea-4066-a86b-ad632a7972e4.png"},
    {"id": "ve13", "name": "Княжеская редкость", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/WNkHc0Lg/f50bc17e-d042-4b36-bc75-e443fc62beb2.jpg"},
    {"id": "ve14", "name": "4Dimenko. Универсальный", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/HpH46jN3/977a4d76-6b92-4fd5-a718-b0f1610ceb2a.png"},
    {"id": "ve15", "name": "Старый Элитный Дименко", "rarity": "Эксклюзивная II степени",
    "image_url": "https://i.ibb.co/Swq06ws7/97fa66f9-b5b9-47c5-bf87-c4158064c4c5.png"},
    {"id": "ve16", "name": "Варишенко", "rarity": "Эксклюзивная II степени",
    "image_url": "https://i.ibb.co/whVG79YC/edad1ee4-e9ee-468b-a71e-d68f5000c7aa.png"},
    {"id": "ve17", "name": "Старый наш слон", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/wHSqMwg/c6ca7986-80ce-4314-ad9a-6c0b907cdc66.png"},
    {"id": "ve18", "name": "Уолтер Батенко", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/rfqqxHbR/f77a883e-5c43-4eba-bf8d-4e901705bddf.png"},
    {"id": "ve19", "name": "ди-менко", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/1ffQDkhn/2d923500-a630-43ab-bb08-e4f5549d9d05.png"},
    {"id": "ve20", "name": "гибрид Херобренко и Груши", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/pBVYQR3w/89ece119-4b82-46ca-b141-5775ea790e08.png"},
    {"id": "ve21", "name": "гибрид Лермонтенко и Груши", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/JjTgdKtB/191a0d1d-9c46-44db-8616-ac24cca0b569.png"},
    {"id": "ve23", "name": "Гибрид Летовенко и Груши", "rarity": "Эксклюзивная II степени",
    "image_url": "https://i.ibb.co/ZRdRcjFk/f7449a40-c52a-4f53-b386-63f0a0f10b4d.png"},
    {"id": "ve24", "name": "Отменённый Эволюционный Клоуненко", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/HD8QbTvx/IMG-20251010-123844-694.png"},
    {"id": "ve25", "name": "Табесенко 24", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/6JWBRxvn/ab8c618a-57d8-4081-a3d4-a2b45f1ac77e.png"},
    {"id": "ve26", "name": "Гибрид Малышенко и Дилденко", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/WvJr235W/c0a123da-5fef-47d3-815f-cffaa40cb982.png"},
    {"id": "ve27", "name": "Эмиленко. Водяной боб", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/1JRMvwXs/e221e629-a5c0-4b38-a92f-6311e0087d57.png"},
    {"id": "ve28", "name": "Волзеренко", "rarity": "Эксклюзивная II степени",
    "image_url": "https://i.ibb.co/F43SPFHb/b8d9d5e0-6c39-434f-8c46-914e5bf20a81.png"},
    {"id": "ve29", "name": "Старый привет соседенко", "rarity": "Эксклюзивная II степени",
    "image_url": "https://i.ibb.co/tPX6MCcW/c02df6cd-8606-495e-884a-a56cc255937b.png"},
    {"id": "ve33", "name": "Прототип Штурмовенко Ччоо", "rarity": "Эксклюзивная I степени",
     "image_url": "https://i.ibb.co/LdQZddYN/a6af6263-baf3-4025-a1c1-c896c72ca724.png"},
    {"id": "ve31", "name": "Абиссинский Дым", "rarity": "Эксклюзивная II степени",
    "image_url": "https://i.ibb.co/rK4kbbPM/5ef8e229-2c5f-446c-9625-f7e183eb1e51.jpg"},
    {"id": "ve32", "name": "Старый Жиденко", "rarity": "Эксклюзивная II степени",
    "image_url": "https://i.ibb.co/rKMCz0F2/246c109b-4c52-4567-9e8d-2a068f1a6a26.png"},
    {"id": "ve30", "name": "Дарт Вейдер", "rarity": "Эксклюзивная I степени",
    "image_url": "https://i.ibb.co/tM9yJSW9/286-20251117235837.png"},
    {"id": "ve34", "name": "Неиспользуемый С3Pенко", "rarity": "Эксклюзивная II степени",
    "image_url": "https://i.ibb.co/ycFZfVYN/308-20251117235132.png"},
    {"id": "ve35", "name": "Бонненко", "rarity": "Эксклюзивная I степени",
    "image_url": "https://i.ibb.co/6754J8vB/321-20251121210601.png"},
    {"id": "ve36", "name": "Удалённый Дартенко Дисиней", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/nqRnyjqw/e59723a5-09a1-4aac-9589-d1a9002ad587.png"},
    {"id": "ve37", "name": "Первое место", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/cKFSTRwk/20251121180109.png"},
    {"id": "ve38", "name": "Второе место", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/Kz98fjtZ/20251121180112.png"},
    {"id": "ve39", "name": "Третье место", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/CKdVdf8Q/20251121180116.png"},
    {"id": "ve40", "name": "120енко", "rarity": "Эксклюзивная I степени",
     "image_url": "https://i.ibb.co/wrBxW3ZM/20251128084830.png"},
    {"id": "ve41", "name": "Дименко в чашке", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/4gV0c3CW/18ad73c8-01ca-44fc-8b26-9eb477837d28.png"},
    {"id": "ve42", "name": "Старый Отец Нации/Дименко", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/1ydwKvy/a6b557a4-21f1-4a94-bd13-86ec375051b1.jpg"},
    {"id": "ve43", "name": "Старая Эволюция на Отца Нации/Дименко", "rarity": "Эксклюзивная II степени",
     "image_url": "https://i.ibb.co/q3mvPpnP/260-20251017155032.png"},
    {"id": "ve44", "name": "Зиггенко", "rarity": "Эксклюзивная I степени",
     "image_url": "https://i.ibb.co/WpswDsLh/321-20251212011527.png"},
    {"id": "ve45", "name": "Эволюционная Миценко", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/r29rfMBX/43d2cdc0-38f6-43a6-88b6-c99123a1d03d.png"},
    {"id": "ve46", "name": "Миценко", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/0p7ZTYDD/20251120212515.png"},
]

EVENT_CARDS = [
    {"id": "ev1", "name": "Джедай Дименко", "rarity": "Обычная",
     "image_url": "https://i.ibb.co/RpwXZPYq/a63cea15-87c8-4122-b9dc-586d7b033670.png"},
    {"id": "ev2", "name": "Ситх Дименко. Дым Гневус", "rarity": "Обычная",
     "image_url": "https://i.ibb.co/Qj34HVp2/4e57a156-855a-44ef-b0cb-88a7f8962449.png"},
    {"id": "ev3", "name": "Люк Дымволкер", "rarity": "Царская",
     "image_url": "https://i.ibb.co/gM2Ct7YX/74d54dd5-aa84-4caa-b037-7d5aaf4edba9.png"},
    {"id": "ev4", "name": "Мейс Винденко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/whQCzc0K/3154dbfc-6a4b-4e9e-8e5d-6fa57a0747ce.png"},
    {"id": "ev5", "name": "Энакенко Дымволкер", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/9k7VSN2W/65f2cb20-12e5-4433-bab6-09cd44687958.png"},
    {"id": "ev6", "name": "Гранд-Мофф Таркенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/kgZhNgDh/56e87fe7-9c98-4481-bdf7-d2d8a6bd2d96-1.png"},
    {"id": "ev7", "name": "Кит Фистенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/QvZxnKyT/127384e0-9bf8-4adc-a2ea-4cf17f3887f9.png"},
    {"id": "ev8", "name": "Дым Сидиус", "rarity": "Царская",
     "image_url": "https://i.ibb.co/8DSRjMpP/9c882612-920d-4e10-8f76-2fc77f1f6878.png"},
    {"id": "ev9", "name": "Хан Соленко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/qYc5L6zQ/e2832048-bd58-4aad-8d09-c9c128d83718.png"},
    {"id": "ev10", "name": "Лея Органенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/Ls6y1xp/5badc36c-d6ef-4d21-869c-b6e346779b21.png"},
    {"id": "ev11", "name": "Генерал Дымус", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/3yjqv3Wd/90849659-84c1-4e41-a381-5aea3fd3d48b.png"},
    {"id": "ev12", "name": "Бен Дымоби", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/tT3Qwp9V/9c36fc6a-e3be-42d8-9efc-75edb22c506f.png"},
    {"id": "ev13", "name": "Чубакенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/mrjhNN0F/f7fa1896-8b51-4183-b0f9-d02c096ebf13.png"},
    {"id": "ev14", "name": "Дим-Ван Дымоби", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/1fkJJWMP/bb61a86e-de0a-4283-8c93-2bc54fe10826.png"},
    {"id": "ev15", "name": "Лэндо Калриссенко", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/tw06qzLN/2fdb7fd4-20b9-4010-8f27-fec0443f24a8.png"},
    {"id": "ev16", "name": "Падме Амидаленко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/qMJGzGnv/047bc5f4-9d4d-4357-8dd3-a95924d83d3b-1.png"},
    {"id": "ev17", "name": "Боба Феттенко", "rarity": "Царская",
     "image_url": "https://i.ibb.co/pBfcqwBt/56f8822c-e04b-4134-a199-6def2dd5cda4.png"},
    {"id": "ev18", "name": "Джанго Феттенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/PsCJWH4w/fd76465a-f26b-4357-a247-1b572a4005fe.png"},
    {"id": "ev19", "name": "Призрак Силы Йоденко", "rarity": "Обычная",
     "image_url": "https://i.ibb.co/5XxyJsQT/90659ec6-308c-4777-a52b-036ff39217bf.png"},
    {"id": "ev20", "name": "Квай-Дым Джинненко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/5gJ6zJXV/fd3e3a60-cfa6-498b-a510-692aae4de135.png"},
    {"id": "ev21", "name": "Граф Дымку", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/N2vdXK9c/f28e65ca-0323-4c68-8220-f182e98ac48a.png"},
    {"id": "ev22", "name": "Дым Мол", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/39KZRvHY/f0b36081-5698-47e4-a25d-fcc615b40e67-1.png"},
    {"id": "ev23", "name": "Джа-Джа Блинксенко", "rarity": "Обычная",
     "image_url": "https://i.ibb.co/bRRBDkrx/7ff5c979-1e4d-4ce3-9097-90754fd507d2.png"},
    {"id": "ev24", "name": "Дым Плегас", "rarity": "Эпическая",
     "image_url": "https://i.ibb.co/B5HYNJGM/bbb44ee9-3f40-40f8-af17-75503b73ef79-1.png"},
    {"id": "ev25", "name": "Зам Уэссенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/XZ6FwjvW/311-20251104004022.png"},
    {"id": "ev26", "name": "Джаба Хатенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/h1VxMTFT/319-20251117234326.png"},
    {"id": "ev27", "name": "Капитан Рексенко", "rarity": "Обычная",
     "image_url": "https://i.ibb.co/PZkWD6dN/324-20251122132959.png"},
    {"id": "ev28", "name": "Дым Вейдер", "rarity": "Царская",
     "image_url": "https://i.ibb.co/XxD3WfCq/325-20251122141821.png"},
    {"id": "ev29", "name": "C3Pенко", "rarity": "Легендарная",
     "image_url": "https://i.ibb.co/j9mM75N2/326-20251122144309.png"},
    {"id": "ev30", "name": "D2-E2", "rarity": "Царская",
     "image_url": "https://i.ibb.co/nsx2Pt5G/328-20251122210011.png"},
    {"id": "ev31", "name": "Имперский штурмовенко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/TMqPyZtH/IMG-20251122-132857-342.png"},
    {"id": "eo1", "name": "Дименко под прицелом", "rarity": "Обычная",
     "image_url": "https://i.ibb.co/krtVB3g/b8b604df-75f9-44a6-8936-37282f63c714.png"},
    {"id": "ab1", "name": "Реденко", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/qLbz8Gft/315-20251129011450.png"},
    {"id": "ab2", "name": "Синенко Троенко", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/XZmXbdzv/315-20251129011559.png"},
    {"id": "ab3", "name": "Чакенко", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/MkcxGSVp/315-20251129011610.png"},
    {"id": "ab4", "name": "Бомбенко", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/Q76vsWWs/315-20251129011719.png"},
    {"id": "ab5", "name": "Матильденко", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/Y4Z7Bn4v/315-20251129011620-2.png"},
    {"id": "ab6", "name": "Дименко с красным подарком", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/F2ZVpdS/315-20251129014757.png"},
    {"id": "ab7", "name": "Дым с венком и новогодним шариком", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/tMsz49V2/315-20251129014652.png"},
    {"id": "ab8", "name": "Королевский Дым-Мороз", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/LXbJSCTH/315-20251129014605.png"},
    {"id": "ab9", "name": "Дименко с большой шапкой", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/HDJggDbh/315-20251129021321.png"},
    {"id": "ab10", "name": "Дым с оранжевой шапкой", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/5Xn6NgNV/315-20251129021215.png"},
    {"id": "ab11", "name": "Дименко с шапкой", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/fdHH6MrQ/315-20251129021715.png"},
    {"id": "ab12", "name": "Дименко с большим колоколом", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/bjgSx5v7/315-20251129020902.png"},
    {"id": "ab13", "name": "Дима с синим подарком", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/39cCwY6x/315-20251129022155.png"},
    {"id": "ab14", "name": "Дименко с маленьким колокольчиком", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/5XTF96zT/315-20251129022643.png"},
    {"id": "ab15", "name": "Дименко с полосатым подарком", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/Sw6r942M/315-20251129021557.png"},
    {"id": "ab16", "name": "Хэленко", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/G4Y3p8X3/315-20251129011947.png"},
    {"id": "ab17", "name": "Димеренс", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/JwYKyB87/315-20251129011929.png"},
    {"id": "ab18", "name": "Могучий Орленко", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/7dFQ0Jpv/315-20251129011918-2.png"},
    {"id": "ab19", "name": "Дым-миньон", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/C3Hk46BK/315-20251129012532-2.png"},
    {"id": "ab20", "name": "Короленко Свиненко", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/vx7rnJsh/315-20251129012514.png"},
    {"id": "ab21", "name": "Дым на снежных блоках", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/Lzfq2QpC/315-20251129103423.png"},
    {"id": "ab22", "name": "Дименко с пряником", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/WNJZDZZh/315-20251129112342.png"},
    {"id": "ab23", "name": "Дименко с пряниками", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/HT2v517n/315-20251129023313.png"},
    {"id": "ab24", "name": "Дименко с лучшими пряниками", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/fRDRy0r/315-20251129023418.png"},
    {"id": "ab25", "name": "Дименко с новогодними шариками", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/FLb73CbV/315-20251129024503.png"},
    {"id": "ab26", "name": "Дым в шапке эльфа", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/Ng87PHBB/315-20251129112508.png"},
    {"id": "ab27", "name": "Финский Дым", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/WWwhvY3G/315-20251129114033.png"},
    {"id": "ab28", "name": "Новогодний Носок", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/W4WqbD8S/315-20251129113657.png"},
    {"id": "ab29", "name": "Дименко с Леденцом ", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/rfXXFs3n/315-20251129113646.png"},
    {"id": "ab30", "name": "Уровень 2-25", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/SXvWbG3B/315-20251129113908.png"},
    {"id": "ab31", "name": "Бабленко", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/Hf9tQ6xd/315-20251129012008.png"},
    {"id": "ab32", "name": "Димелла", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/1SYPpFW/315-20251129012027-2.png"},
    {"id": "ab33", "name": "Капраленко", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/hxnRnnht/315-20251129012151.png"},
    {"id": "ab34", "name": "Усатый Дым", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/MDHfVvfh/315-20251129012306.png"},
    {"id": "ab35", "name": "Стая Птиц", "rarity": "Эксклюзивная III степени",
     "image_url": "https://i.ibb.co/7NxVwgP5/315-20251129115540.png"},
    {"id": "ab36", "name": "Банда Свиней", "rarity": "Эксклюзивная III степени",
    "image_url": "https://i.ibb.co/ynRhRwww/315-20251129121606.png"},
    {"id": "ab37", "name": "Дименко и гора подарков", "rarity": "Эксклюзивная III степени",
    "image_url": "https://i.ibb.co/qMPfNw7W/315-20251129121020.png"},
    {"id": "ab38", "name": "Дым с зелённым колоколом", "rarity": "Эксклюзивная III степени",
    "image_url": "https://i.ibb.co/qFYQWhB8/315-20251129130151.png"},
    {"id": "ab39", "name": "Бонусные уровни", "rarity": "Эксклюзивная III степени",
    "image_url": "https://i.ibb.co/ZpngnxHq/315-20251129111601.png"},
    {"id": "ab40", "name": "Intel яиценко", "rarity": "Эксклюзивная III степени",
    "image_url": "https://i.ibb.co/v6H954MT/315-20251129111646.png"},
    {"id": "ab41", "name": "Сосуленко", "rarity": "Эксклюзивная III степени",
    "image_url": "https://i.ibb.co/hFY581R7/315-20251129134108.png"},
    {"id": "ab42", "name": "Дымирлянда", "rarity": "Эксклюзивная III степени",
    "image_url": "https://i.ibb.co/Pv1Fqfkv/315-20251129135052.png"},
    {"id": "ab43", "name": "Эльфенко ", "rarity": "Эксклюзивная III степени",
    "image_url": "https://i.ibb.co/nqptL2Jc/315-20251129125654.png"},
    {"id": "ab44", "name": "Новогодний Дименко", "rarity": "Эксклюзивная III степени",
    "image_url": "https://i.ibb.co/xtFQwvJf/315-20251129133522.png"},
    {"id": "ab45", "name": "Дым в снежной крепости", "rarity": "Эксклюзивная III степени",
    "image_url": "https://i.ibb.co/ycNfGfQS/315-20251129132542.png"},
    {"id": "ok1", "name": "Крэбенко", "rarity": "Обычная",
    "image_url": "https://i.ibb.co/mVwjD3PZ/398-20260107203724.png"},
    {"id": "ok2", "name": "Ультра Платоненко", "rarity": "Эксклюзивная II степени",
    "image_url": "https://i.ibb.co/84jzjJv8/397-20260107212155.png"},
    {"id": "ok3", "name": "Некий ДН и его крутой тюленко", "rarity": "Царская",
    "image_url": "https://i.ibb.co/jPcNmhR6/377-20251231142951.png"},
    {"id": "ok4", "name": "Фениксенко", "rarity": "Мифическая",
    "image_url": "https://i.ibb.co/PGtFn0mP/IMG-20251231-132152-428.jpg"},
    {"id": "ok5", "name": "Кнуефенко", "rarity": "Сверхредкая",
    "image_url": "https://i.ibb.co/PGtFn0mP/IMG-20251231-132152-428.jpg"},
    {"id": "ok6", "name": "Сандерсенко", "rarity": "Эпическая",
    "image_url": "https://i.ibb.co/vxdMrJWD/373-20251231131404.png"},
    {"id": "ok7", "name": "Триченко", "rarity": "Эпическая",
    "image_url": "https://i.ibb.co/fdgJCfrt/372-20251231131100.png"},
    {"id": "ok8", "name": "Веранденко", "rarity": "Легендарная",
    "image_url": "https://i.ibb.co/NnGzJjXY/381-20260103023158.png"},
    {"id": "ok9", "name": "Даркенко", "rarity": "Обычная",
    "image_url": "https://i.ibb.co/MyYzqfSF/379-20251231132605.png"},
    {"id": "ok10", "name": "Дымакс", "rarity": "Обычная",
    "image_url": "https://i.ibb.co/fRj1f50/374-20260103000415.png"},
    {"id": "ok11", "name": "Клотянко", "rarity": "Эпическая",
    "image_url": "https://i.ibb.co/0jBM5zrW/378.png"},
    {"id": "ok12", "name": "Бламленко", "rarity": "Легендарная",
    "image_url": ""},
    {"id": "ok13", "name": "Букашенко", "rarity": "Редкая",
    "image_url": "https://i.ibb.co/xpGvLXh/401-20260107195841.png"},
    {"id": "ok14", "name": "Фаеренко", "rarity": "Редкая",
     "image_url": "https://i.ibb.co/DXtVTbW/399-20260107195722.png"},
    {"id": "ok15", "name": "Михдукенко", "rarity": "Сверхредкая",
     "image_url": "https://i.ibb.co/rn1Qx7z/396-20260107214737.png"},
    {"id": "cn1", "name": "Сенсей", "rarity": "Обычная",
     "image_url": "https://i.postimg.cc/fLrVj2j5/Без_названия1850_20260216211946.png"},
    {"id": "cn2", "name": "Бамбук", "rarity": "Обычная",
     "image_url": "https://i.postimg.cc/KYm3Zg85/Без_названия1850_20260217002330.png"},
    {"id": "cn3", "name": "Гражданин", "rarity": "Обычная",
     "image_url": "https://i.postimg.cc/FRRfS5ch/Без_названия1850_20260216212611.png"},
    {"id": "cn4", "name": "Фонарь", "rarity": "Обычная",
     "image_url": "https://i.postimg.cc/NMzK7J7D/Без_названия1850_20260216211504.png"},
    {"id": "cn5", "name": "Мудрец", "rarity": "Обычная",
     "image_url": "https://i.postimg.cc/rmPDCnCH/Без_названия1850_20260216210323.png"},
    {"id": "cn6", "name": "Панденко", "rarity": "Обычная",
     "image_url": "https://i.postimg.cc/ZnvCf8V1/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F1850_20260216201047.png"},
    {"id": "cn7", "name": "Мандарин", "rarity": "Обычная",
     "image_url": "https://i.postimg.cc/KzJGCZz5/Bez-nazvania1850-20260217135814.png"},
]





EVO_CARDS = [
    {"id": "de1", "name": "Эволюционный Растаман", "rarity": "Бронзовая Эпическая Эволюция",
     "image_url": "https://i.ibb.co/W4WMkTxS/ac226a83-8140-4f0b-aff1-775feb2f0849.png"},
    {"id": "de2", "name": "Деловой Кабаненко", "rarity": "Бронзовая Обычная Эволюция",
     "image_url": "https://i.postimg.cc/pVhHKp0S/IMG-20260301-174955-021.png"},
    {"id": "de3", "name": "Эволюционный Ариеценко", "rarity": "Бронзовая Царская Эволюция",
     "image_url": "https://i.ibb.co/sXyxfWM/00cf490c-f3e2-4bdf-a830-0868c0fe14fd.png"},
    {"id": "de4", "name": "Эволюционный Жиденко", "rarity": "Бронзовая Редкая Эволюция",
     "image_url": "https://i.ibb.co/xqnLjJhB/d5680f10-690e-4b13-b61b-5c438dfba66f.png"},
    {"id": "de5", "name": "Эволюционный Херобренко", "rarity": "Бронзовая Легендарная Эволюция",
     "image_url": "https://i.ibb.co/4wwtHcj3/25da6496-4a34-47d4-a3e9-4c196e146d8a-1.png"},
    {"id": "de6", "name": "Банда Хряковичей", "rarity": "Бронзовая Обычная Эволюция",
     "image_url": "https://i.ibb.co/6cXprkQy/e994f39e-0e38-4f56-b506-5403d6d1c0bf.png"},
    {"id": "de7", "name": "Эволюционный Элитный Дименко", "rarity": "Бронзовая Редкая Эволюция",
     "image_url": "https://i.ibb.co/TqBnNXCy/a3b8fc27-aafd-4e2b-b06c-2302805757e5.png"},
    {"id": "de8", "name": "Прогрессивный Рак", "rarity": "Бронзовая Редкая Эволюция",
     "image_url": "https://i.ibb.co/4rh1RtC/fa8d1e06-c8fd-4251-93ab-a59af116f5a6.png"},
    {"id": "de9", "name": "Эволюционный Скибиди Сигма Ризлер Огайо босс", "rarity": "Бронзовая Редкая Эволюция",
     "image_url": "https://i.ibb.co/zMLDdnK/806bae10-b15f-4cba-b368-4b5e37ccd942-1.png"},
    {"id": "de10", "name": "Бывалый Строителенко", "rarity": "Бронзовая Редкая Эволюция",
     "image_url": "https://i.ibb.co/5Q3xSYW/050a3546-c1d4-47b4-acf1-4960b0abd2f0.png"},
    {"id": "de11", "name": "Успешный Архитекторенко", "rarity": "Бронзовая Редкая Эволюция",
     "image_url": "https://i.ibb.co/Fqc6nQ46/b9ad93c9-a85e-457d-853b-dc7f9e116b32.png"},
    {"id": "de12", "name": "Арбалетчик", "rarity": "Бронзовая Обычная Эволюция",
     "image_url": "https://i.ibb.co/qM7PWfwN/b986b04c-aa71-4080-b398-9548f6eec67f.png"},
    {"id": "de13", "name": "Эволюционный Токсик", "rarity": "Бронзовая Обычная Эволюция",
     "image_url": "https://i.ibb.co/zhtZr04w/0881f1a4-5139-4a8c-bff8-27077f007be0.png"},
    {"id": "de14", "name": "Пушкин", "rarity": "Бронзовая Редкая Эволюция",
     "image_url": "https://i.ibb.co/Cs0nphrB/832f2f10-6bd9-48ea-a9dd-6157ba835389-1.png"},
    {"id": "de15", "name": "Супер Дупер Дименко Мен", "rarity": "Бронзовая Легендарная Эволюция",
     "image_url": "https://i.ibb.co/tTpvfhBN/3a4c2b58-caa2-4944-8657-f29b7d6976eb.png"},
    {"id": "de16", "name": "Абсолютно прогрессирующий в интеллектуальных способностях Ботаненко", "rarity": "Бронзовая Обычная Эволюция",
     "image_url": "https://i.ibb.co/cc6Mq44p/b7732f7d-71c8-41d5-916b-cb4665212265.png"},
    {"id": "de17", "name": "Владыка жуликов","rarity": "Бронзовая Редкая Эволюция",
     "image_url": "https://i.ibb.co/jSV5sCr/3d9bcd1e-f3be-47a7-a884-5921d5d596c7.png"},
    {"id": "de18", "name": "Эволюционный Император Духов","rarity": "Бронзовая Легендарная Эволюция",
     "image_url": "https://i.ibb.co/F48Pjrt7/3ed3ad35-44e1-4652-a5ed-f86f534dac92.png"},
    {"id": "de19", "name": "Зомбоссенко","rarity": "Бронзовая Обычная Эволюция",
     "image_url": "https://i.ibb.co/W4Xd5wps/be587c8a-7ff9-426e-bc2e-83a7b13cf668.png"},
    {"id": "de20", "name": "Теория бесконечных денег фанатов АБ","rarity": "Бронзовая Обычная Эволюция",
     "image_url": "https://i.ibb.co/PZL1dzsd/3c7f624f-af33-47c0-bc8d-e5b885d292a1.png"},
    {"id": "de21", "name": "Эволюционный Хог Райденко","rarity": "Бронзовая Сверхредкая Эволюция",
     "image_url": "https://i.ibb.co/8LGtzKL0/4885f58d-67b0-49f6-9820-9f4ac5d4731e.jpg"},
    {"id": "de22", "name": "Эволюционный Желтобрюхенко","rarity": "Бронзовая Царская Эволюция",
     "image_url": "https://i.ibb.co/YF56Y10q/275-20251215025910.png"},
    {"id": "de23", "name": "Гектор Поркенко в Зеркальном Мире","rarity": "Бронзовая Великоимператорская Эволюция",
     "image_url": "https://i.ibb.co/hFyxY6cY/161e8d81-a3c8-4b33-9aa5-2d6f4437087b.png"},
    {"id": "de24", "name": "Эволюционные Элитные Дымы", "rarity": "Бронзовая Эпическая Эволюция",
     "image_url": "https://i.ibb.co/btDyD4P/1d315424-3e3f-4d79-bee3-e663025d8d16.png"},
    {"id": "de25", "name": "Классический Отец Нации","rarity": "Бронзовая Великоимператорская Эволюция",
     "image_url": "https://i.ibb.co/391710LN/350-20251211212557.png"},
    {"id": "de26", "name": "22 братство","rarity": "Бронзовая Сверхредкая Эволюция",
     "image_url": "https://i.ibb.co/N6yVVp25/364-20251223011058.png"},
    {"id": "de27", "name": "Слив новой карты","rarity": "Бронзовая Сверхредкая Эволюция",
     "image_url": "https://i.ibb.co/Y4D5t3zh/134d075a-4b75-458b-8ca0-a099993491e8.png"},
    {"id": "de28", "name": "Царь Дименко","rarity": "Бронзовая Легендарная Эволюция",
     "image_url": "https://i.ibb.co/cS7kxhkj/269.png"},
    {"id": "de29", "name": "Тут скоро будет новая эволюция","rarity": "Бронзовая Редкая Эволюция",
     "image_url": "https://i.ibb.co/tTRn27mL/20251120212436.png"},
    {"id": "de30", "name": "Чурка выбил Чуркенко","rarity": "Бронзовая Эпическая Эволюция",
     "image_url": "https://i.ibb.co/tTRn27mL/20251120212436.png"},
    {"id": "de31", "name": "Праймовый Гассисключительный","rarity": "Бронзовая Эпическая Эволюция",
     "image_url": "https://i.ibb.co/tTYXGYYh/320-20251118215815.png"},
    {"id": "de32", "name": "Эволюционный Лев Абрикосенко","rarity": "Бронзовая Редкая Эволюция",
     "image_url": "https://i.ibb.co/0yrtdNw7/316-20251212011540.png"},
    {"id": "de33", "name": "Династия Дименковых","rarity": "Бронзовая Царская Эволюция",
     "image_url": "https://i.ibb.co/qL5Yhkxh/313-20251215024905.png"},
    {"id": "de34", "name": "Эволюционный Партенко","rarity": "Бронзовая Эпическая Эволюция",
     "image_url": "https://i.ibb.co/vxJfcRZ5/330-20251212011108.png"},
    {"id": "de35", "name": "Эмильсхуем","rarity": "Бронзовая Царская Эволюция",
     "image_url": "https://i.ibb.co/qMKgPcsY/348-20251212010500.png"},
    {"id": "de36", "name": "Эволюционный Пейнтенко","rarity": "Бронзовая Обычная Эволюция",
     "image_url": "https://i.ibb.co/hRJDkqwq/347-20251212012530.png"},
    {"id": "de37", "name": "Эволюционный Дым Механик","rarity": "Бронзовая Редкая Эволюция",
     "image_url": "https://i.ibb.co/j9kDct9K/IMG-20251213-123910-144.jpg"},
    {"id": "de38", "name": "Егор Пухенко","rarity": "Бронзовая Царская Эволюция",
     "image_url": "https://i.ibb.co/W4Tmr8fK/352-20251216203150.png"},
    {"id": "de39", "name": "Лучший мем 2025","rarity": "Бронзовая Обычная Эволюция",
     "image_url": "https://i.ibb.co/N28pN7jq/332-20251215162503.png"},
    {"id": "de40", "name": "Эволюционный Сулустаненко", "rarity": "Бронзовая Сверхредкая Эволюция",
     "image_url": "https://i.ibb.co/gbzVnxD9/338-20251215113733.png"},
    {"id": "de41", "name": "Эволюционный Чернильный Дым", "rarity": "Бронзовая Сверхредкая Эволюция",
     "image_url": "https://i.ibb.co/dwk8ygbr/355-20251215163259.png"},
    {"id": "de42", "name": "Дименко с эволюционной ложкой", "rarity": "Бронзовая Сверхредкая Эволюция",
     "image_url": "https://i.ibb.co/67tPCJkq/357-20251217012812.png"},
    {"id": "de43", "name": "Спейс Миндикенко", "rarity": "Бронзовая Мифическая Эволюция",
     "image_url": "https://i.ibb.co/yBRWCDmL/353-20251222221013.png"},
    {"id": "de44", "name": "Эволюционный Соседенко", "rarity": "Бронзовая Обычная Эволюция",
     "image_url": "https://i.ibb.co/gbGLrtWj/404-20260103000930.png"},
    {"id": "de45", "name": "Будни Дыма", "rarity": "Бронзовая Сверхредкая Эволюция",
     "image_url": "https://i.ibb.co/j9nZhY5p/360-20251224012722.png"},
    {"id": "de46", "name": "Легчайший путь", "rarity": "Бронзовая Сверхредкая Эволюция",
     "image_url": "https://i.ibb.co/5hVzrtCK/20260103025653.png"},
    {"id": "de47", "name": "Флэш Томсон", "rarity": "Бронзовая Обычная Эволюция",
     "image_url": "https://i.ibb.co/tMrTjCHj/363-20251223011612.png"},
    {"id": "de48", "name": "Я твой хороший Дым", "rarity": "Бронзовая Эпическая Эволюция",
     "image_url": "https://i.ibb.co/Psx4LXx7/361-20260102161545.png"},
    {"id": "de49", "name": "Ката Барсенко победил Магнуса Карлсона в шахматах", "rarity": "Бронзовая Мифическая Эволюция",
     "image_url": "https://i.ibb.co/TBV3SXkm/366-20251223003714.png"},
    {"id": "de50", "name": "Точно не фейковый Реденко", "rarity": "Бронзовая Обычная Эволюция",
     "image_url": "https://i.ibb.co/0RCMsRX5/351-20251223235538.png"},
    {"id": "so1", "name": "Успешный Кабаненко", "rarity": "Серебряная Обычная Эволюция",
     "image_url": "https://i.postimg.cc/RhfyyJyN/IMG-20260301-174952-836.png"},
    {"id": "zo1", "name": "Популяренко", "rarity": "Золотая Обычная Эволюция",
     "image_url": "https://i.postimg.cc/fTn6X5Sc/IMG-20260301-174951-601.png"},
]



ARCHIVE_CARDS = {
"so1", "zo1", "ev1", "ev2", "ev3", "ev4", "ev5", "ev6", "ev7", "ev8", "ev9", "ev10", "ev11", "ev12", "ev13", "ev14", "ev15", "ev16", "ev17", "ev18", "ev19", "ev20", "ev21", "ev22", "ev23", "ev24", "ev25", "ev26", "ev27", "ev28", "ev29", "ev30", "ev31", "eo1", "ab1", "ab2", "ab3", "ab4", "ab5", "ab6", "ab7", "ab8", "ab9", "ab10", "ab11", "ab12", "ab13", "ab14", "ab15", "ab16", "ab17", "ab18", "ab19", "ab20", "ab21", "ab22", "ab23", "ab24", "ab25", "ab26", "ab27", "ab28", "ab29", "ab30", "ab31", "ab32", "ab33", "ab34", "ab35", "ab36", "ab37", "ab38", "ab39", "ab40", "ab41", "ab42", "ab43", "ab44", "ab45", "ok2",  "ok3", "ok4",  "ok5",  "ok1",  "ok6",  "ok7",  "ok8", "ok9", "ok10", "ok11",  "ok12", "ok13", "ok14", "ok15", "cn1", "cn2", "cn3", "cn4", "cn5", "cn6", "cn7"
}


CARDS += EVO_CARDS

ALL_CARDS = CARDS + EVO_CARDS + EVENT_CARDS
CARD_BY_ID = {c["id"]: c for c in ALL_CARDS}

RARITY_ORDER = {
    "Великоимператорская": 1,
    "Царская": 2,
    "Легендарная": 3,
    "Мифическая": 4,
    "Эпическая": 5,
    "Сверхредкая": 6,
    "Редкая": 7,
    "Обычная": 8,
}

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
_lock = threading.Lock()



EVOLUTION_THRESHOLD = 2


OLD_EVOLUTIONS_BY_NAME = {
    "Ди4менко": "Классический Отец Нации",
    "Рас4таман": "Эволюционный Растаман",
    "Кла4ссический Кабаненко": "Деловой Кабаненко",
    "Ари5кеценко": "Эволюционный Ариеценко",
    "Жиде5нко": "Эволюционный Жиденко",
    "Хе5робренко": "Эволюционный Херобренко",
    "Кр5якенко": "Банда Хряковичей",
    "Эл5итный Дименко": "Эволюционный Элитный Дименко",
    "Ра5к": "Прогрессивный Рак",
    "Ск5ибиди Сигменко": "Эволюционный Скибиди Сигма Ризлер Огайо босс",
    "Ст5роителенко": "Бывалый Строителенко",
    "Ар5хитекторенко": "Успешный Архитекторенко",
    "То5ксик": "Эволюционный Токсик",
    "Л5учникенко": "Арбалетчик",
    "Ни5геренко": "Пушкин",
    "С5упер Дименко Мен": "Супер Дупер Дименко Мен",
    "Б5отаненко": "Абсолютно прогрессирующий в интеллектуальных способностях Ботаненко",
    "Жу5ликенко": "Владыка жуликов",
    "Им5ператор Духов": "Эволюционный Император Духов",
    "З5ондренко": "Зомбоссенко",
    "Це5левая АБ": "Теория бесконечных денег фанатов АБ",
    "Х5ог Райденко": "Эволюционный Хог Райденко",
    "Г5ектор Поркенко": "Гектор Поркенко в Зеркальном Мире",
    "Эл5итные Дымы": "Эволюционные Элитные Дымы",
    "За5грузенко": "Слив новой карты",
    "Ре5тро Дименко": "Царь Дименко",
    #"Миценко": "Эволюционная Миценко",
    "Чу5ркенко": "Чурка выбил Чуркенко",
    "Га6ссисключительный": "Праймовый Гассисключительный",
    "Л5ев Абрикосенко": "Эволюционный Лев Абрикосенко",
    "Ди5менко Младший": "Династия Дименковых",
    "Па5ртенко": "Эволюционный Партенко",
    "Эм5иленко": "Эмильсхуем",
    "Пе5йнтенко": "Эволюционный Пейнтенко",
    "Ды5м Механик": "Эволюционный Дым Механик",
    "Же5лтобрюхенко": "Эволюционный Желтобрюхенко",
    "Б5рялокенко": "Егор Пухенко",
    "Ди5манго": "Лучший мем 2025",
    "Су5лустаненко": "Эволюционный Сулустаненко",
    "Че5рнильный Дым": "Эволюционный Чернильный Дым",
    "Ди5менко с ложкой": "Дименко с эволюционной ложкой",
    "Ди5мпрессия": "Легчайший путь",
    "Пр5ивет Соседенко": "Эволюционный Соседенко",
    "Д5ым в ночном горшке": "Будни Дыма",
    "Ми5ндикенко": "Спейс Миндикенко",
    "Бу5лленко": "Флэш Томсон",
    "Ву5диенко": "Я твой хороший Дым",
    "Ка5та Барсенко": "Ката Барсенко победил Магнуса Карлсона в шахматах",
    "Фе5йковый Реденко": "Точно не фейковый Реденко",
    "Эль5 Витаминенко": "22 братство"
}


AUTO_EVOLUTIONS = {}

for base, evo in OLD_EVOLUTIONS_BY_NAME.items():
    AUTO_EVOLUTIONS.setdefault(base, []).append(evo)

NEW_EVOLUTIONS_BY_NAME = {
    "Классический Кабаненко": ["", ""],
}

EVOLUTIONS_BY_NAME = {}

# сначала старые эво как первая стадия
for base, chain in AUTO_EVOLUTIONS.items():
    EVOLUTIONS_BY_NAME[base] = chain[:]  # копия

# теперь добавляем новые стадии
for base, new_chain in NEW_EVOLUTIONS_BY_NAME.items():
    if base not in EVOLUTIONS_BY_NAME:
        EVOLUTIONS_BY_NAME[base] = []
    EVOLUTIONS_BY_NAME[base].extend(new_chain)




EVOLUTIONS_ID = {}

for base_name, evo_list in EVOLUTIONS_BY_NAME.items():
    base_id = next((cid for cid, c in CARD_BY_ID.items() if c["name"] == base_name), None)
    if not base_id:
        continue

    chain_ids = []
    for evo_name in evo_list:
        evo_id = next((cid for cid, c in CARD_BY_ID.items() if c["name"] == evo_name), None)
        if evo_id:
            chain_ids.append(evo_id)

    if chain_ids:
        EVOLUTIONS_ID[base_id] = chain_ids




def grant_card_no_score(data, user, card):
    u = get_or_init_user(data, user)
    rarity = card["rarity"]
    u["counts"][rarity] = u["counts"].get(rarity, 0) + 1
    u["total"] += 1
    prev = u["cards"].get(card["id"], 0)
    u["cards"][card["id"]] = prev + 1
    if prev == 0:
        u["unique"] = u.get("unique", 0) + 1
    u["updated_at"] = int(time.time())
    data["users"][str(user.id)] = u  # Явно преобразуем в строку для ключа
    return prev == 0


def process_evolution_if_ready(data, user, base_card):
    base_id = base_card["id"]
    evo_chain = EVOLUTIONS_ID.get(base_id)
    if not evo_chain:
        return None

    u = get_or_init_user(data, user)

    # Определяем текущую стадию по наличию эволюций
    current_stage = -1
    for i, evo_id in enumerate(evo_chain):
        if u["cards"].get(evo_id, 0) > 0:
            current_stage = i

    # Считаем количество базовых карт (включая текущую)
    base_count = u["cards"].get(base_id, 0)

    # Для эволюции нужно: (текущая_стадия + 2) базовых карт
    # Если current_stage = -1 (нет эво), нужно 1 базовая карта для первой эво
    # Если есть 1 эво (current_stage = 0), нужно 2 базовых карты для второй эво и т.д.
    required_base = current_stage + 2

    if base_count < required_base:
        return None

    # Стадий больше нет
    next_stage = current_stage + 1
    if next_stage >= len(evo_chain):
        return None

    evo_id = evo_chain[next_stage]
    evo_card = CARD_BY_ID.get(evo_id)
    if not evo_card:
        return None

    # Уже есть — не выдаём
    if u["cards"].get(evo_id, 0) > 0:
        return None

    # Начисляем бонус (x2 очков базовой карты)
    rarity = base_card["rarity"]
    bonus = SCORE_WEIGHTS.get(rarity, 0) * 2
    u["score"] += bonus

    # Выдаём эво
    grant_card_no_score(data, user, evo_card)

    return {"evo_card": evo_card, "bonus": bonus}





GENERAL_ROTATION_EXCLUDED_RARITIES = {
    "Эволюционная",
    "Эксклюзивная I степени",
    "Эксклюзивная II степени",
    "Эксклюзивная III степени",
    "Бронзовая Обычная Эволюция",
    "Бронзовая Редкая Эволюция",
    "Бронзовая Сверхредкая Эволюция",
    "Бронзовая Эпическая Эволюция",
    "Бронзовая Легендарная Эволюция",
    "Бронзовая Царская Эволюция",
    "Бронзовая Мифическая Эволюция",
    "Бронзовая Великоимператорская Эволюция",
    "Серебряная Обычная Эволюция",
    "Серебряная Редкая Эволюция",
    "Серебряная Сверхредкая Эволюция",
    "Серебряная Эпическая Эволюция",
    "Серебряная Легендарная Эволюция",
    "Серебряная Царская Эволюция",
    "Серебряная Мифическая Эволюция",
    "Серебряная Великоимператорская Эволюция",
    "Золотая Обычная Эволюция",
    "Золотая Редкая Эволюция",
    "Золотая Сверхредкая Эволюция",
    "Золотая Эпическая Эволюция",
    "Золотая Легендарная Эволюция",
    "Золотая Царская Эволюция",
    "Золотая Мифическая Эволюция",
    "Золотая Великоимператорская Эволюция"
}


def is_in_general_rotation(card):
    return (
        card["id"] not in ARCHIVE_CARDS
        and card.get("rarity") not in GENERAL_ROTATION_EXCLUDED_RARITIES
    )

def pick_guaranteed_new_card(user_data):
    owned = set(cid for cid, qty in user_data.get("cards", {}).items() if qty > 0)

    # Исключаем все типы карт, которые не должны выпадать
    excluded_rarities = GENERAL_ROTATION_EXCLUDED_RARITIES.copy()
    excluded_rarities.update({
        "Эволюционная",
        "Эксклюзивная I степени",
        "Эксклюзивная II степени",
        "Эксклюзивная III степени"
    })

    available_by_rarity = {}
    for c in CARDS:
        if not is_in_general_rotation(c):
            continue
        if c["id"] in owned:
            continue
        if c["id"] in ARCHIVE_CARDS:
            continue
        if c.get("rarity") in excluded_rarities:
            continue
        r = c.get("rarity")
        available_by_rarity.setdefault(r, []).append(c)

    if not available_by_rarity:
        return None

    rarities = list(available_by_rarity.keys())
    weights = [RARITY_WEIGHTS.get(r, 0) for r in rarities]
    total_w = sum(weights)

    if total_w <= 0:
        chosen_rarity = random.choice(rarities)
    else:
        chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]

    pool = available_by_rarity[chosen_rarity]
    return random.choice(pool) if pool else None



def ensure_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_case": {}, "users": {}}, f, ensure_ascii=False)


def load_data():
    ensure_data()
    with _lock:
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            data = {"last_case": {}, "users": {}}
            save_data_atomic(data)
            return data


def save_data_atomic(data):
    with _lock:

        tmp_dir = os.path.dirname(os.path.abspath(DATA_FILE))
        fd, tmp = tempfile.mkstemp(prefix="case_", suffix=".json", dir=tmp_dir)
        with os.fdopen(fd, "w", encoding="utf-8") as w:
            json.dump(data, w, ensure_ascii=False, indent=2)

        shutil.move(tmp, DATA_FILE)


def pick_rarity():
    rarities = list(RARITY_WEIGHTS.keys())
    weights = [RARITY_WEIGHTS[r] for r in rarities]
    return random.choices(rarities, weights=weights, k=1)[0]


def pick_card_by_rarity(rarity):
    pool = [c for c in CARDS if c["rarity"] == rarity and c["id"] not in ARCHIVE_CARDS]
    return random.choice(pool) if pool else None


def display_name(user):
    parts = [user.first_name or "", user.last_name or ""]
    name = " ".join(p for p in parts if p).strip()
    if not name:
        name = f"User {user.id}"
    return name


def profile_link(user):
    if user.username:
        return f"https://t.me/{user.username}"
    return f"tg://user?id={user.id}"


def get_or_init_user(data, user):
    uid = str(user.id)  # Оставляем строку для ключа в словаре
    users = data.setdefault("users", {})
    u = users.get(uid)
    if not u:
        u = {
            "id": user.id,  # Но здесь храним как число
            "name": display_name(user),
            "username": user.username,
            "counts": {r: 0 for r in RARITY_WEIGHTS.keys()},
            "total": 0,
            "score": 0,
            "updated_at": int(time.time()),
            "cards": {},
            "unique": 0,
            "repeat_streak": 0,
            "event_repeat_streak": 0,
        }
        users[uid] = u
    return u

def find_card_by_id(card_id: str):
    for c in CARDS:
        if str(c.get("id")) == str(card_id):
            return c
    for c in EVENT_CARDS:
        if str(c.get("id")) == str(card_id):
            return c
    return None


def update_user_stats_with_card(data, user, card):

    u = get_or_init_user(data, user)
    rarity = card["rarity"]


    u["name"] = display_name(user)
    u["username"] = user.username


    u["counts"][rarity] = u["counts"].get(rarity, 0) + 1
    u["total"] += 1


    prev = u["cards"].get(card["id"], 0)
    u["cards"][card["id"]] = prev + 1

    added_score = 0
    is_new = False
    if prev == 0:
        added_score = SCORE_WEIGHTS.get(rarity, 0)
        u["score"] += added_score
        is_new = True
        u["unique"] = u.get("unique", 0) + 1

    u["updated_at"] = int(time.time())
    data["users"][str(user.id)] = u
    return added_score, is_new


def sort_users_for_top(users_dict):
    users = list(users_dict.values())
    users.sort(key=lambda x: (x.get("score", 0), x.get("total", 0), -(x.get("updated_at", 0))), reverse=True)
    return users[:20]



DIRECT_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")


def is_direct_image_url(url: str) -> bool:
    if not url:
        return False
    low = url.lower()
    return any(low.endswith(ext) for ext in DIRECT_EXTENSIONS)


def resolve_direct_image_url(url: str, timeout: int = 10) -> str:
    if not url:
        return url
    if is_direct_image_url(url):
        return url

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code != 200 or not resp.text:
            return url
        html = resp.text

        m = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if m:
            og = m.group(1).strip()
            if ("i.imgur.com" in og) and not is_direct_image_url(og):
                og += ".jpg"
            return og

        m2 = re.search(r'<link\s+rel=["\']image_src["\']\s+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if m2:
            href = m2.group(1).strip()
            if ("i.imgur.com" in href) and not is_direct_image_url(href):
                href += ".jpg"
            return href

        m3 = re.search(r'(https://i\.imgur\.com/[A-Za-z0-9]+(?:\.(?:jpg|jpeg|png|gif|webp))?)', html)
        if m3:
            return m3.group(1)
    except Exception:
        pass
    return url



def _thread_id_of(msg_or_call):
    if hasattr(msg_or_call, "message_thread_id"):
        return msg_or_call.message_thread_id
    if hasattr(msg_or_call, "message") and hasattr(msg_or_call.message, "message_thread_id"):
        return msg_or_call.message.message_thread_id
    return None


def send_message_in_topic(message, text, **kwargs):
    bot.send_message(
        message.chat.id, text,
        message_thread_id=_thread_id_of(message),
        **kwargs
    )


def send_photo_in_topic(message, photo, caption=None, **kwargs):
    bot.send_photo(
        message.chat.id, photo=photo, caption=caption,
        message_thread_id=_thread_id_of(message),
        **kwargs
    )



def send_message_in_topic_cb(call, text, **kwargs):
    bot.send_message(
        call.message.chat.id, text,
        message_thread_id=_thread_id_of(call),
        **kwargs
    )


def send_photo_in_topic_cb(call, photo, caption=None, **kwargs):
    bot.send_photo(
        call.message.chat.id, photo=photo, caption=caption,
        message_thread_id=_thread_id_of(call),
        **kwargs
    )


def get_user_record(data, user_id: int):
    users = data.get("users", {})
    return users.get(str(user_id))

def ensure_user_record(data, user_id: int, username=None, first_name=None):
    users = data.setdefault("users", {})
    key = str(user_id)
    if key not in users:
        users[key] = {
            "id": user_id,  # Сохраняем как число, а не строку
            "username": username,
            "name": first_name or "",
            "score": 0,
            "cards": {},
            "description": "",
            "favorite_card": None,
            "counts": {r: 0 for r in RARITY_WEIGHTS.keys()},
            "total": 0,
            "unique": 0,
            "repeat_streak": 0,
            "event_repeat_streak": 0,
            "updated_at": int(time.time())
        }
    return users[key]



def extract_target_user(message, data):
    if message.reply_to_message:
        ru = message.reply_to_message.from_user
        if ru:
            return ru

    args = message.text.split()
    if len(args) > 1:
        arg = args[1].lstrip("@")
        for uid, u in data.get("users", {}).items():
            if u.get("username") == arg or str(uid) == arg:
                return type("U", (), {
                    "id": int(uid),
                    "username": u.get("username"),
                    "first_name": u.get("name", "")
                })()

    if message.from_user:
        return message.from_user

    return None






@bot.message_handler(commands=["start", "restartenko"])
@require_topic
def start_cmd(message):
    handle_start(message)

def handle_start(message):
    text = (
        "👋 Добро пожаловать в Hog Cards, дорогой!\n\n"
        "Этот бот — переосмысление кастомных ролей Discord‑сервера <b>Подвала Димкона</b>, "
        "вдохновлённое другими карточными ботами.\n\n"
        "🎲 Чтобы получить свою первую карту Кабаненко, используй команду /caseenko\n"
        "📖 Если нужен список всех команд — /helpenko тебе в помощь!"
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        message_thread_id=_thread_id_of(message)
    )


@bot.message_handler(commands=["help", "helpenko"])
@require_podval
@require_topic
def help_cmd(message):
    text = (
        "📖 <b>Список команд</b>\n\n"
        "🎲 <b>/caseenko</b> | <b>/case</b> | <b>?кейс</b>\n"
        "Не нажимай, умоляю.\n\n"
        "🎁 <b>/dailygift</b> | <b>/dailyenko</b>\n"
        "ПОДАРОК\n\n"
        "🔄 <b>/restartenko</b> | <b>/start</b>\n"
        "Перезапуск или старт бота.\n\n"
        "📖 <b>/helpenko</b> | <b>/help</b>\n"
        "Показать весь функционал бота.\n\n"
        "🏆 <b>/topenko</b> | <b>/top</b>\n"
        "Список самых крутых участников.\n\n"
        "📦 <b>/collectionenko</b> | <b>/collection</b>\n"
        "Команды коллекций.\n\n"
        "🪬 <b>/evocollectionenko</b> | <b>/evocollection</b>\n"
        "Команды эволюционной коллекций.\n\n"
        "👤 <b>/infoprofilenko</b> | <b>/infoprofile</b>\n"
        "Информация про профиль, его настройку и команды\n\n"
        "📩 <b>/infogiftenko</b> | <b>/infogift</b>\n"
        "Информация о том, как дарить карты"
    )

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        message_thread_id=_thread_id_of(message)
    )


@bot.message_handler(commands=["dailygift", "dailyenko"])
@require_podval

@require_topic
def daily_gift_cmd(message):
    handle_daily_gift(message)


def handle_daily_gift(message):
    user = message.from_user
    user_id = str(user.id)
    thread_id = getattr(message, "message_thread_id", None)

    data = load_data()
    u = get_or_init_user(data, user)

    last_gift = data.get("last_daily_gift", {}).get(user_id, 0)
    now = int(time.time())
    COOLDOWN_SECONDS = 86400

    if now - last_gift < COOLDOWN_SECONDS:
        remaining = COOLDOWN_SECONDS - (now - last_gift)
        h, rem = divmod(remaining, 3600)
        m, s = divmod(rem, 60)
        cooldown_texts = [
            f"【⏳】• Ежедневный подарок уже получен. Следующий через {h} ч {m} мин {s} сек",
            f"【🕐】• Брат, подарок будет доступен через {h} ч {m} мин {s} сек",
            f"【⚠️】• Подожди ещё {h} ч {m} мин {s} сек до следующего подарка"
        ]
        bot.send_message(message.chat.id, random.choice(cooldown_texts), message_thread_id=thread_id)
        return

    rarity_weights = {
        "Сверхредкая": 3,
        "Эпическая": 3,
        "Мифическая": 3,
        "Легендарная": 3,
        "Царская": 1
    }

    archive_ids = set(ARCHIVE_CARDS)
    event_ids = {c["id"] for c in EVENT_CARDS}

    pool = [c for c in CARDS if c["rarity"] in rarity_weights and c["id"] not in archive_ids and c["id"] not in event_ids]

    owned = set(u.get("cards", {}).keys())
    unique_candidates = [c for c in pool if c["id"] not in owned]

    if unique_candidates:
        card = random.choice(unique_candidates)
    else:
        rarities = [c["rarity"] for c in pool]
        weights = [rarity_weights[r] for r in rarities]
        card = random.choices(pool, weights=weights, k=1)[0]

    results = []

    rarity = card["rarity"]
    added_score, is_new = update_user_stats_with_card(data, user, card)
    caption = f'【🎁】• ЭТО ТОЧНО НОВАЯ КАРТА "{card["name"]}" ({rarity})'
    if is_new and added_score > 0:
        caption += f"\n+{added_score} ауры."
    else:
        caption += "\n【📊】• У тебя итак все карты, куда больше то?"
    results.append((card, caption, is_new))

    num_cards = random.randint(1, 3)
    for _ in range(num_cards - 1):
        rarities = [c["rarity"] for c in pool]
        weights = [rarity_weights[r] for r in rarities]
        card = random.choices(pool, weights=weights, k=1)[0]

        rarity = card["rarity"]
        added_score, is_new = update_user_stats_with_card(data, user, card)

        drop_texts = [
            f'【🎁】• Дополнительный подарок: "{card["name"]}" ({rarity})',
            f'【✨】• Кабанчик как всегда щедрый: "{card["name"]}" ({rarity})',
            f'【🎲】• Держи самого дешёвого и лоховского медведя за 15 звезд! "{card["name"]}" ({rarity})'
        ]
        caption = random.choice(drop_texts)

        if is_new and added_score > 0:
            caption += f"\n+{added_score} ауры."
        else:
            duplicate_texts = [
                "【📊】• эх повторка",
                "【⚠️】• Это лучше чем ничего",
                "【📉】• МОЛОДЁЖНЫЙ МЕМЧИК ОКАК ПОВТОРКА"
            ]
            caption += "\n" + random.choice(duplicate_texts)

        results.append((card, caption, is_new))

    data.setdefault("last_daily_gift", {})[user_id] = now
    save_data_atomic(data)

    rare_unique = None
    for card, caption, is_new in results:
        if is_new:
            if rare_unique is None or RARITY_ORDER[card["rarity"]] > RARITY_ORDER[rare_unique[0]["rarity"]]:
                rare_unique = (card, caption)

    text_parts = []
    for card, caption, is_new in results:
        if rare_unique and card["id"] == rare_unique[0]["id"]:
            continue
        text_parts.append(caption)

    final_text = "".join(text_parts)

    if rare_unique:
        url = rare_unique[0].get("image_url")
        if url:
            try:
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=resolve_direct_image_url(url),
                    caption=rare_unique[1] + "\n\n" + final_text,
                    parse_mode="HTML",
                    message_thread_id=thread_id
                )
                return
            except Exception:
                pass

    bot.send_message(
        chat_id=message.chat.id,
        text=final_text,
        parse_mode="HTML",
        message_thread_id=thread_id
    )



@bot.message_handler(commands=["infogift", "infogiftenko"])
@require_podval
@require_topic
def hyihyi_cmd(message):
    handle_hyihyi(message)


def handle_hyihyi(message):

    text = (
        "🎁 <b>ВСЁ о дарении карт</b>\n\n"
        "Чтобы подарить <b>ОДНУ</b> карту другому пользователю, у вас должно быть 4 ПОВТОРНЫХ минимум\n\n"

        "🪬 На эволюционные карты дарение не действует.\n"
        "⚠️ У вас должно быть минимум 2 карты во владении, иначе дарить невозможно.\n"
        "❗ Исключение: эксклюзивные карты. При дарении одной эксклюзивной карты она полностью пропадает из вашей коллекции.\n\n"

        "📈 Когда вы дарите карту:\n"
        "- Получатель получает одну уникальную карту.\n"
        "- У вас списывается 2 ваши повторные карты.\n\n"

        "📌 Дарить карты можно командой:\n"
        "Пример1: <code>/giftenko v1 @dimenko</code>\n"
        "Пример2: <code>/gift v1 1488516622</code>\n"
        "Вариации команд: /gift /giftenko\n"
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="HTML",
        message_thread_id=_thread_id_of(message)
    )

@bot.message_handler(commands=["infoprofile", "infoprofilenko"])
@require_podval
@require_topic
def profile_info_cmd(message):
    thread_id = message.message_thread_id if message.message_thread_id else None

    text = (
        "👤 <b>ВСЁ о профиле</b>\n\n"
        "Профиль показывает общую статистику пользователя\n\n"

        "📋 <b>Как посмотреть профиль:</b>\n"
        "• <code>/profile</code> — твой профиль.\n"
        "• <code>/profilenko</code> — то же самое.\n"
        "• <code>/profile @dimenko</code> — профиль указанного участника.\n"
        "• <code>/profile 1488516622</code> — профиль по ID.\n"
        "• Ответом на сообщение: /profile — профиль автора того сообщения\n\n"

        "📝 <b>Описание профиля:</b>\n"
        "• <code>/setdescenko Текст</code> — установить описание (до 200 символов).\n"
        "Пример: <code>/setdescenko Люблю коллекционировать редкие карты</code>\n\n"

        "❤️ <b>Любимая карта:</b>\n"
        "• <code>/setfavenko ID карты</code> — выбрать любимую карту из своей коллекции.\n"
        "Пример: <code>/setfavenko v1</code>"
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        message_thread_id=thread_id
    )


@bot.message_handler(commands=["china", "si"])
@require_topic
@require_podval
def event_case_cmd(message):
    handle_event_case(message)


def handle_event_case(message):
    user = message.from_user
    user_id = str(user.id)
    thread_id = getattr(message, "message_thread_id", None)

    data = load_data()
    u = get_or_init_user(data, user)

    last_case = data.get("last_event_case", {}).get(user_id, 0)
    now = int(time.time())
    COOLDOWN_SECONDS_LOCAL = 14400  # 4 часа

    # отображение имени
    if user.username:
        user_display = f"@{user.username}"
    else:
        user_display = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'

    # КУЛДАУН
    if now - last_case < COOLDOWN_SECONDS_LOCAL:
        remaining = COOLDOWN_SECONDS_LOCAL - (now - last_case)
        h, rem = divmod(remaining, 3600)
        m, s = divmod(rem, 60)

        cooldown_text = (
            f"{user_display}\n"
            f"🇪🇺🔧 稍等片刻，我们正在窃取西方的技术。\n"
            f"⏳ Осталось: {h} ч {m} мин {s} сек."
        )

        bot.send_message(
            message.chat.id,
            cooldown_text,
            message_thread_id=thread_id,
            parse_mode="HTML"
        )
        return

    archive_ids = set(ARCHIVE_CARDS)
    pool = [c for c in EVENT_CARDS if c["id"] not in archive_ids]

    if not pool:
        bot.send_message(
            chat_id=message.chat.id,
            text="【⚠️】• Новые ивенты скоро будут...",
            message_thread_id=thread_id
        )
        return

    owned = set(u.get("cards", {}).keys())

    event_streak = u.get("event_repeat_streak", 0)

    if event_streak >= 2:
        available = [c for c in pool if c["id"] not in owned]
        if available:
            card = random.choice(available)
            added_score, is_new = update_user_stats_with_card(data, user, card)
            u["event_repeat_streak"] = 0
        else:
            card = random.choice(pool)
            added_score, is_new = update_user_stats_with_card(data, user, card)
            u["event_repeat_streak"] = 0
    else:
        card = random.choice(pool)
        added_score, is_new = update_user_stats_with_card(data, user, card)

        if is_new:
            u["event_repeat_streak"] = 0
        else:
            u["event_repeat_streak"] = event_streak + 1

    # === ТЕКСТЫ ===
    if is_new:
        caption = (
            user_display +
            f'<blockquote>🇨🇳🀄️ 偉大的領袖給了你一張新牌 🎴🐼 "{card["name"]}"\n'
            f'🎴 Редкость: Китайская\n'
            f'🪙 Социал-кредит: +{added_score}</blockquote>'
        )
    else:
        caption = (
            user_display +
            f'<blockquote>认清台湾！你不配拥有新地图！🇹🇼 "{card["name"]}"</blockquote>'
        )

    # === СОХРАНЕНИЕ КД ===
    data.setdefault("last_event_case", {})[user_id] = now
    save_data_atomic(data)

    # === ОТПРАВКА КАРТИНКИ ===
    url = card.get("image_url")
    if url:
        try:
            bot.send_photo(
                chat_id=message.chat.id,
                photo=resolve_direct_image_url(url),
                caption=caption,
                message_thread_id=thread_id,
                parse_mode="HTML"
            )
            return
        except Exception as e:
            print("Ошибка send_photo (eventcase):", e)

    bot.send_message(
        chat_id=message.chat.id,
        text=caption + (f"\n(Ссылка: {url})" if url else ""),
        disable_web_page_preview=False,
        parse_mode="HTML",
        message_thread_id=thread_id
    )





COOLDOWN_IMAGES = [
    "https://i.postimg.cc/SxHjSNmp/Без_названия1853_20260217152346.png",
    "https://i.postimg.cc/jjN2L0jW/Без_названия1853_20260217152252.png",
    "https://i.postimg.cc/L8Gh96mX/Без_названия1853_20260217152225.png",
    "https://i.postimg.cc/0NmjbRNj/Без_названия1853_20260217152159.png",
    "https://i.postimg.cc/x1BqfT9D/Без_названия1853_20260217152319.png",
    "https://i.postimg.cc/bw4dyNq8/Без_названия1853_20260217152331.png"
]

@bot.message_handler(commands=["case", "caseenko", "tatare", "pic", "card", "cardenko"])
@require_podval
@require_topic
def case_cmd(message):
    handle_case(message)

@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "?кейс")
@require_podval
@require_topic
def case_word(message):
    handle_case(message)


def handle_case(message):
    user = message.from_user
    user_id = str(user.id)
    thread_id = getattr(message, "message_thread_id", None)

    data = load_data()
    u = get_or_init_user(data, user)

    last_case = data.get("last_case", {}).get(user_id, 0)
    now = int(time.time())
    COOLDOWN_SECONDS_LOCAL = 1800

    if now - last_case < COOLDOWN_SECONDS_LOCAL:
        remaining = COOLDOWN_SECONDS_LOCAL - (now - last_case)
        m, s = divmod(remaining, 60)

        cooldown_texts = [
            "<blockquote>⏳ | Осталось: {m} мин {s} сек</blockquote>",
        ]

        cooldown_image = random.choice(COOLDOWN_IMAGES)

        bot.send_photo(
            chat_id=message.chat.id,
            photo=cooldown_image,
            caption=random.choice(cooldown_texts).format(m=m, s=s),
            message_thread_id=thread_id
        )
        return

    # --- ИСКЛЮЧЕНИЯ ---
    EVENT_CARD_IDS = {c["id"] for c in EVENT_CARDS}
    EVO_CARDS_IDS = {c["id"] for c in EVO_CARDS}

    BRONZE_RARITIES = {
        "Бронзовая Обычная Эволюция",
        "Бронзовая Редкая Эволюция",
        "Бронзовая Сверхредкая Эволюция",
        "Бронзовая Эпическая Эволюция",
        "Бронзовая Легендарная Эволюция",
        "Бронзовая Царская Эволюция",
        "Бронзовая Мифическая Эволюция",
        "Бронзовая Великоимператорская Эволюция"
        "Серебряная Обычная Эволюция",
        "Серебряная Редкая Эволюция",
        "Серебряная Сверхредкая Эволюция",
        "Серебряная Эпическая Эволюция",
        "Серебряная Легендарная Эволюция",
        "Серебряная Царская Эволюция",
        "Серебряная Мифическая Эволюция",
        "Серебряная Великоимператорская Эволюция"
        "Золотая Обычная Эволюция",
        "Золотая Редкая Эволюция",
        "Золотая Сверхредкая Эволюция",
        "Золотая Эпическая Эволюция",
        "Золотая Легендарная Эволюция",
        "Золотая Царская Эволюция",
        "Золотая Мифическая Эволюция",
        "Золотая Великоимператорская Эволюция"
    }

    # --- ВЫБОР РЕДКОСТИ ---
    rarity = pick_rarity()
    while rarity == "Эволюционная" or rarity in BRONZE_RARITIES:
        rarity = pick_rarity()

    # --- ПУЛ КАРТ ---
    pool = [
        c for c in CARDS
        if c["id"] not in EVENT_CARD_IDS
        and c["id"] not in ARCHIVE_CARDS
        and c["id"] not in EVO_CARDS_IDS
        and c["rarity"] != "Эволюционная"
        and c["rarity"] not in BRONZE_RARITIES
    ]

    candidates = [c for c in pool if c["rarity"] == rarity]
    card = random.choice(candidates) if candidates else random.choice(pool)
    rarity = card["rarity"]

    # --- ГАРАНТ ---
    if u.get("repeat_streak", 0) >= 4:
        guaranteed = pick_guaranteed_new_card(u)
        if guaranteed and guaranteed["rarity"] not in BRONZE_RARITIES and guaranteed["rarity"] != "Эволюционная":
            card = guaranteed
            rarity = card["rarity"]
            u["repeat_streak"] = 0

    added_score, is_new = update_user_stats_with_card(data, user, card)
    evo_result = process_evolution_if_ready(data, user, card)

    u["repeat_streak"] = 0 if is_new else u.get("repeat_streak", 0) + 1
    data.setdefault("last_case", {})[user_id] = now
    save_data_atomic(data)

    drop_texts = [
        '<blockquote>🔶 | Редкость: {rarity}\n💳 | Индикатор: {id}</blockquote>',
    ]

    duplicate_texts = [
        '<blockquote>🔶 | Редкость: {rarity}\n💳 | Индикатор: {id}\n(Эта карта у вас уже была)</blockquote>',
    ]

    if is_new:
        caption = random.choice(drop_texts).format(
            name=card["name"], rarity=rarity, id=card["id"]
        )
        if added_score > 0:
            caption += f"\n<blockquote>✨️ | Аура: +{added_score} ауры.</blockquote>"
    else:
        caption = random.choice(duplicate_texts).format(
            name=card["name"], rarity=rarity, id=card["id"]
        )

    url = card.get("image_url")
    sent = False
    if url:
        try:
            bot.send_photo(
                chat_id=message.chat.id,
                photo=resolve_direct_image_url(url),
                caption=caption,
                message_thread_id=thread_id
            )
            sent = True
        except:
            pass

    if not sent:
        bot.send_message(
            chat_id=message.chat.id,
            text=caption,
            message_thread_id=thread_id
        )

    # --- ЭВОЛЮЦИЯ ---
    if evo_result:
        evo_card = evo_result["evo_card"]
        bonus = evo_result["bonus"]

        evo_caption = (
            f'<blockquote>🔷️ | Редкость Эволюции: {evo_card["rarity"]}\n'
            f'💳 | Индикатор: {evo_card["id"]}\n'
            f'✨️ | Аура:+{bonus} ауры.</blockquote>'
        )

        url2 = evo_card.get("image_url")
        if url2:
            try:
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=resolve_direct_image_url(url2),
                    caption=evo_caption,
                    message_thread_id=thread_id
                )
                return
            except:
                pass

        bot.send_message(
            chat_id=message.chat.id,
            text=evo_caption,
            message_thread_id=thread_id
        )










@bot.message_handler(commands=["top", "topenko"])
@require_podval
@require_topic
def top_cmd(message):
    handle_top(message)


def handle_top(message):
    user = message.from_user

    data = load_data()
    users = data.get("users", {})
    top_users = sort_users_for_top(users)[:20]

    header = "🏆 Самая настоящая школа 🏆\n"
    lines = []
    for i, u in enumerate(top_users, start=1):
        display_name = u.get("name") or f'User {u.get("id")}'
        link = f'https://t.me/{u["username"]}' if u.get("username") else f'tg://user?id={u.get("id")}'
        score = u.get("score", 0)
        lines.append(f'{i}. <a href="{link}">{display_name}</a> — аура: {score}')
    if not lines:
        lines.append("тут никогда не будет пусто хых")

    bot.send_message(
        chat_id=message.chat.id,
        text=header + "\n".join(lines),
        parse_mode="HTML",
        disable_web_page_preview=True,
        message_thread_id=_thread_id_of(message)
    )



@bot.message_handler(commands=["giftenko", "gift"])
@require_topic
@require_podval
def gift_cmd(message):
    handle_gift(message)


def handle_gift(message):
    user = message.from_user
    thread_id = _thread_id_of(message)

    args = message.text.split()
    if len(args) < 3:
        bot.send_message(
            chat_id=message.chat.id,
            text="【⚠️】• Использование: /giftenko [ID карты] [@username или ID получателя]",
            message_thread_id=thread_id
        )
        return

    card_id = args[1]
    recipient_arg = args[2].lstrip("@")

    data = load_data()
    sender_data = get_or_init_user(data, user)

    recipient_user = None
    for uid, u in data.get("users", {}).items():
        if u.get("username") == recipient_arg or str(uid) == recipient_arg:
            recipient_user = u
            break

    if not recipient_user:
        bot.send_message(
            message.chat.id,
            f"【⚠️】• Получатель {recipient_arg} не найден.",
            message_thread_id=thread_id
        )
        return

    card = CARD_BY_ID.get(card_id)
    if not card:
        bot.send_message(
            message.chat.id,
            "【⚠️】• Карта с таким ID не найдена.",
            message_thread_id=thread_id
        )
        return

    rarity = card["rarity"]
    sender_cards = sender_data.get("cards", {})
    if card_id not in sender_cards:
        bot.send_message(
            message.chat.id,
            "【⚠️】• У тебя нет такой карты.",
            message_thread_id=thread_id
        )
        return

    card_count = sender_cards[card_id]

    rarity_rules = {
        "Великоимператорская": (3, 2),
        "Царская": (4, 2),
        "Легендарная": (4, 2),
        "Мифическая": (4, 2),
        "Эпическая": (4, 2),
        "Сверхредкая": (4, 2),
        "Редкая": (4, 2),
        "Обычная": (4, 2),
    }

    recipient_cards = recipient_user.setdefault("cards", {})
    had_card = card_id in recipient_cards

    sender_display = f"@{user.username}" if user.username else f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
    recipient_display = f"@{recipient_user.get('username')}" if recipient_user.get("username") else f'<a href="tg://user?id={recipient_user.get("id")}">Игрок</a>'

    if rarity in ("Эксклюзивная I степени", "Эксклюзивная II степени", "Эксклюзивная III степени"):
        if card_count < 1:
            bot.send_message(
                message.chat.id,
                f"【⚠️】• У тебя нет карты {rarity} для подарка.",
                message_thread_id=thread_id
            )
            return

        sender_cards.pop(card_id)
        recipient_cards[card_id] = recipient_cards.get(card_id, 0) + 1

        if not had_card:
            added_score = SCORE_WEIGHTS.get(rarity, 0)
            recipient_user["score"] = recipient_user.get("score", 0) + added_score
            recipient_user["unique"] = recipient_user.get("unique", 0) + 1
            main_text = f"【🎁】• {sender_display} подарил карту \"{card['name']}\" ({rarity}) {recipient_display}!\n+{added_score} ауры получателю"
        else:
            main_text = f"【🎁】• {sender_display} подарил карту \"{card['name']}\" ({rarity}) {recipient_display}!"

    else:
        if rarity not in rarity_rules:
            bot.send_message(
                message.chat.id,
                "【⚠️】• Эту карту нельзя подарить.",
                message_thread_id=thread_id
            )
            return

        need, remove = rarity_rules[rarity]
        if card_count < need:
            bot.send_message(
                message.chat.id,
                f"【⚠️】• Нужно минимум {need} карт этой редкости, чтобы подарить.",
                message_thread_id=thread_id
            )
            return

        sender_cards[card_id] -= remove
        if sender_cards[card_id] <= 0:
            sender_cards.pop(card_id)

        recipient_cards[card_id] = recipient_cards.get(card_id, 0) + 1

        if not had_card:
            added_score = SCORE_WEIGHTS.get(rarity, 0)
            recipient_user["score"] = recipient_user.get("score", 0) + added_score
            recipient_user["unique"] = recipient_user.get("unique", 0) + 1
            main_text = f"【🎁】• {sender_display} подарил карту \"{card['name']}\" ({rarity}) {recipient_display}!\n+{added_score} ауры получателю"
        else:
            main_text = f"【🎁】• {sender_display} подарил карту \"{card['name']}\" ({rarity}) {recipient_display}!"

    bot.send_message(
        message.chat.id,
        main_text,
        parse_mode="HTML",
        message_thread_id=thread_id
    )

    notify_text = f"【📩】• {sender_display} подарил тебе карту \"{card['name']}\" ({rarity})!"
    try:
        bot.send_message(
            chat_id=recipient_user["id"],
            text=notify_text,
            parse_mode="HTML"
        )
    except Exception:
        bot.send_message(
            message.chat.id,
            f"{recipient_display}, тебе подарок!\n{notify_text}",
            parse_mode="HTML",
            message_thread_id=thread_id
        )

    save_data_atomic(data)






def _safe_sklad_sort_key(cid: str):
    match = re.search(r'(\d+)', cid)
    if match:
        return (cid[:match.start()], int(match.group(1)))
    return (cid, 0)


def chunk_and_send(chat_id, thread_id, lines, chunk_size=100):
    for i in range(0, len(lines), chunk_size):
        chunk = lines[i:i+chunk_size]
        msg_text = "\n".join(chunk)
        bot.send_message(
            chat_id=chat_id,
            text=msg_text,
            parse_mode="HTML",
            message_thread_id=thread_id,
            disable_web_page_preview=False
        )


@bot.message_handler(commands=["evoraritycountenko"])
@require_podval
@require_topic
def evoraritycount_cmd(message):
    data = load_data()
    u = get_or_init_user(data, message.from_user)
    cards_data = CARD_BY_ID
    EVENT_CARDS_IDS = {c["id"] for c in EVENT_CARDS}

    # --- РЕДКОСТИ ПО ГРУППАМ ---
    BRONZE = [
        ("🩵", "Бронзовая Обычная Эволюция"),
        ("🧡", "Бронзовая Редкая Эволюция"),
        ("💚", "Бронзовая Сверхредкая Эволюция"),
        ("💜", "Бронзовая Эпическая Эволюция"),
        ("🤍", "Бронзовая Легендарная Эволюция"),
        ("💛", "Бронзовая Царская Эволюция"),
        ("❤️‍", "Бронзовая Мифическая Эволюция"),
        ("❤️‍🔥", "Бронзовая Великоимператорская Эволюция"),
    ]

    SILVER = [
        ("🩵", "Серебряная Обычная Эволюция"),
        ("🧡", "Серебряная Редкая Эволюция"),
        ("💚", "Серебряная Сверхредкая Эволюция"),
        ("💜", "Серебряная Эпическая Эволюция"),
        ("🤍", "Серебряная Легендарная Эволюция"),
        ("💛", "Серебряная Царская Эволюция"),
        ("❤️‍", "Серебряная Мифическая Эволюция"),
        ("❤️‍🔥", "Серебряная Великоимператорская Эволюция"),
    ]

    GOLD = [
        ("🩵", "Золотая Обычная Эволюция"),
        ("🧡", "Золотая Редкая Эволюция"),
        ("💚", "Золотая Сверхредкая Эволюция"),
        ("💜", "Золотая Эпическая Эволюция"),
        ("🤍", "Золотая Легендарная Эволюция"),
        ("💛", "Золотая Царская Эволюция"),
        ("❤️‍", "Золотая Мифическая Эволюция"),
        ("❤️‍🔥", "Золотая Великоимператорская Эволюция"),
    ]

    # --- ФУНКЦИЯ ПОДСЧЁТА ---
    def count_rarity(rarity):
        total = sum(
            1 for c in cards_data.values()
            if c.get("rarity") == rarity
            and c["id"] not in ARCHIVE_CARDS
            and c["id"] not in EVENT_CARDS_IDS
        )

        unique = len([
            cid for cid, qty in u["cards"].items()
            if qty > 0
            and cards_data[cid]["rarity"] == rarity
            and cid not in ARCHIVE_CARDS
            and cid not in EVENT_CARDS_IDS
        ])

        return unique, total

    # --- ФОРМИРОВАНИЕ ТЕКСТА ---
    text = "🧬 <b>Эволюционные редкости</b>:\n\n"

    # БРОНЗА
    text += "🥉 <b>Бронзовые Эволюции:</b>\n"
    for emoji, rarity in BRONZE:
        u_count, t_count = count_rarity(rarity)
        text += f"{emoji} <b>{rarity}</b>: {u_count} из {t_count}\n"
    text += "\n"

    # СЕРЕБРО
    text += "🥈 <b>Серебряные Эволюции:</b>\n"
    for emoji, rarity in SILVER:
        u_count, t_count = count_rarity(rarity)
        text += f"{emoji} <b>{rarity}</b>: {u_count} из {t_count}\n"
    text += "\n"

    # ЗОЛОТО
    text += "🥇 <b>Золотые Эволюции:</b>\n"
    for emoji, rarity in GOLD:
        u_count, t_count = count_rarity(rarity)
        text += f"{emoji} <b>{rarity}</b>: {u_count} из {t_count}\n"

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="HTML",
        message_thread_id=_thread_id_of(message)
    )





@bot.message_handler(commands=["collection", "collectionenko"])
@require_podval
@require_topic
def collection_cmd(message):
    """Обычные коллекции"""
    thread_id = _thread_id_of(message)

    text = (
        "📦 <b>Команды Коллекций:</b>\n\n"
        "🩵 Обычные — /commonenko\n"
        "🧡 Редкие — /rareenko\n"
        "💚 Сверхредкие — /superrareenko\n"
        "💜 Эпические — /epicenko\n"
        "❤️‍ Мифические — /mythicalenko\n"
        "🤍 Легендарные — /legendaryenko\n"
        "💛 Царские — /cesarenko\n"
        "❤️‍🔥 Великоимператорские — /imperatorenko\n"
        "💌 Эксклюзивные — /exclusiveenko\n"
        "💝‍ Ивентовые — /eventenko\n"
        "📊 Счетчик карт — /raritycountenko\n"
        "🃏 Посмотреть одну конкретную карту — /view либо /viewenko (ID карты)\n"
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="HTML",
        message_thread_id=thread_id
    )

# Удаляем старую функцию skvad_cmd или перенаправляем
@bot.message_handler(commands=["skvad", "skvadenko"])
@require_podval
@require_topic
def skvad_cmd(message):
    # Перенаправляем на collection_cmd
    collection_cmd(message)


def send_sklad_by_rarity(message, rarity_name):
    data = load_data()
    u = get_or_init_user(data, message.from_user)
    cards_data = CARD_BY_ID

    grouped = []
    for cid, qty in u["cards"].items():
        if qty > 0 and cid in cards_data:
            card = cards_data[cid]
            if card.get("rarity") == rarity_name:
                grouped.append((cid, card, qty))

    if not grouped:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"【📭】 У тебя пока нет карт редкости <b>{rarity_name}</b>",
            parse_mode="HTML",
            message_thread_id=_thread_id_of(message)
        )
        return

    grouped.sort(key=lambda x: _safe_sklad_sort_key(x[0]))

    lines = [f"<b>{rarity_name}</b>"]
    for cid, card, qty in grouped:
        name = card.get("name", "Безымянная")
        url = card.get("image_url")
        if url:
            lines.append(f'<a href="{url}">{name}</a> — {qty} шт (ID: {cid})')
        else:
            lines.append(f"{name} — {qty} шт (ID: {cid})")

    # Отправляем порциями по 50 строк, чтобы не превысить лимит Telegram
    chunk_and_send(message.chat.id, _thread_id_of(message), lines, chunk_size=50)


def send_sklad_by_specific_rarity(message, rarity_name):
    data = load_data()
    u = get_or_init_user(data, message.from_user)
    cards_data = CARD_BY_ID

    grouped = [
        (cid, cards_data[cid], qty)
        for cid, qty in u["cards"].items()
        if qty > 0 and cid in cards_data and cards_data[cid].get("rarity") == rarity_name
    ]

    if not grouped:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"У тебя пока нет карт редкости <b>{rarity_name}</b>",
            parse_mode="HTML",
            message_thread_id=_thread_id_of(message)
        )
        return

    grouped.sort(key=lambda x: _safe_sklad_sort_key(x[0]))

    lines = [f"<b>{rarity_name}</b>"]
    for cid, card, qty in grouped:
        name = card.get("name", "Безымянная")
        url = card.get("image_url")
        if url:
            lines.append(f'<a href="{url}">{name}</a> — {qty} шт (ID: {cid})')
        else:
            lines.append(f"{name} — {qty} шт (ID: {cid})")

    chunk_and_send(message.chat.id, _thread_id_of(message), lines, chunk_size=100)


@bot.message_handler(commands=["commonenko"])
@require_podval
@require_topic
def sklad_common_cmd(message):
    send_sklad_by_rarity(message, "Обычная")

@bot.message_handler(commands=["rareenko"])
@require_podval
@require_topic
def sklad_rare_cmd(message):
    send_sklad_by_rarity(message, "Редкая")

@bot.message_handler(commands=["superrareenko"])
@require_podval
@require_topic
def sklad_superrare_cmd(message):
    send_sklad_by_rarity(message, "Сверхредкая")

@bot.message_handler(commands=["epicenko"])
@require_podval
@require_topic
def sklad_epic_cmd(message):
    send_sklad_by_rarity(message, "Эпическая")

@bot.message_handler(commands=["mythicalenko"])
@require_podval
@require_topic
def sklad_mific_cmd(message):
    send_sklad_by_rarity(message, "Мифическая")

@bot.message_handler(commands=["legendaryenko"])
@require_podval
@require_topic
def sklad_legendary_cmd(message):
    send_sklad_by_rarity(message, "Легендарная")

@bot.message_handler(commands=["cesarenko"])
@require_podval
@require_topic
def sklad_cesar_cmd(message):
    send_sklad_by_rarity(message, "Царская")

@bot.message_handler(commands=["imperatorenko"])
@require_podval
@require_topic
def sklad_dimenko_cmd(message):
    send_sklad_by_rarity(message, "Великоимператорская")

@bot.message_handler(commands=["exclusiveenko"])
@require_podval
@require_topic
def sklad_exclusive_cmd(message):
    send_exclusive_degrees(message)


def send_exclusive_degrees(message):
    exclusive_degrees = [
        "Эксклюзивная I степени",
        "Эксклюзивная II степени",
        "Эксклюзивная III степени",
    ]
    for degree in exclusive_degrees:
        send_sklad_by_specific_rarity(message, degree)


@bot.message_handler(commands=["evoenko"])
@require_podval
@require_topic
def sklad_evo_cmd(message):
    send_sklad_by_rarity(message, "Эволюционная")

@bot.message_handler(commands=["Cuevocommonenko"])
@require_podval
@require_topic
def evo_bronze_common(message):
    send_sklad_by_rarity(message, "Бронзовая Обычная Эволюция")

@bot.message_handler(commands=["Cuevorareenko"])
@require_podval
@require_topic
def evo_bronze_rare(message):
    send_sklad_by_rarity(message, "Бронзовая Редкая Эволюция")

@bot.message_handler(commands=["Cuevosuperrareenko"])
@require_podval
@require_topic
def evo_bronze_superrare(message):
    send_sklad_by_rarity(message, "Бронзовая Сверхредкая Эволюция")

@bot.message_handler(commands=["Cuevoepicenko"])
@require_podval
@require_topic
def evo_bronze_epic(message):
    send_sklad_by_rarity(message, "Бронзовая Эпическая Эволюция")

@bot.message_handler(commands=["Cuevomythicalenko"])
@require_podval
@require_topic
def evo_bronze_mythical(message):
    send_sklad_by_rarity(message, "Бронзовая Мифическая Эволюция")

@bot.message_handler(commands=["Cuevolegendaryenko"])
@require_podval
@require_topic
def evo_bronze_legendary(message):
    send_sklad_by_rarity(message, "Бронзовая Легендарная Эволюция")

@bot.message_handler(commands=["Cuevocesarenko"])
@require_podval
@require_topic
def evo_bronze_cesar(message):
    send_sklad_by_rarity(message, "Бронзовая Царская Эволюция")

@bot.message_handler(commands=["Cuevoimperatorenko"])
@require_podval
@require_topic
def evo_bronze_imperator(message):
    send_sklad_by_rarity(message, "Бронзовая Великоимператорская Эволюция")

@bot.message_handler(commands=["Agevocommonenko"])
@require_podval
@require_topic
def evo_silver_common(message):
    send_sklad_by_rarity(message, "Серебряная Обычная Эволюция")

@bot.message_handler(commands=["Agevorareenko"])
@require_podval
@require_topic
def evo_silver_rare(message):
    send_sklad_by_rarity(message, "Серебряная Редкая Эволюция")

@bot.message_handler(commands=["Agevosuperrareenko"])
@require_podval
@require_topic
def evo_silver_superrare(message):
    send_sklad_by_rarity(message, "Серебряная Сверхредкая Эволюция")

@bot.message_handler(commands=["Agevoepicenko"])
@require_podval
@require_topic
def evo_silver_epic(message):
    send_sklad_by_rarity(message, "Серебряная Эпическая Эволюция")

@bot.message_handler(commands=["Agevomythicalenko"])
@require_podval
@require_topic
def evo_silver_mythical(message):
    send_sklad_by_rarity(message, "Серебряная Мифическая Эволюция")

@bot.message_handler(commands=["Agevolegendaryenko"])
@require_podval
@require_topic
def evo_silver_legendary(message):
    send_sklad_by_rarity(message, "Серебряная Легендарная Эволюция")

@bot.message_handler(commands=["Agevocesarenko"])
@require_podval
@require_topic
def evo_silver_cesar(message):
    send_sklad_by_rarity(message, "Серебряная Царская Эволюция")

@bot.message_handler(commands=["Agevoimperatorenko"])
@require_podval
@require_topic
def evo_silver_imperator(message):
    send_sklad_by_rarity(message, "Серебряная Великоимператорская Эволюция")

@bot.message_handler(commands=["Auevocommonenko"])
@require_podval
@require_topic
def evo_gold_common(message):
    send_sklad_by_rarity(message, "Золотая Обычная Эволюция")

@bot.message_handler(commands=["Auevorareenko"])
@require_podval
@require_topic
def evo_gold_rare(message):
    send_sklad_by_rarity(message, "Золотая Редкая Эволюция")

@bot.message_handler(commands=["Auevosuperrareenko"])
@require_podval
@require_topic
def evo_gold_superrare(message):
    send_sklad_by_rarity(message, "Золотая Сверхредкая Эволюция")

@bot.message_handler(commands=["Auevoepicenko"])
@require_podval
@require_topic
def evo_gold_epic(message):
    send_sklad_by_rarity(message, "Золотая Эпическая Эволюция")

@bot.message_handler(commands=["Auevomythicalenko"])
@require_podval
@require_topic
def evo_gold_mythical(message):
    send_sklad_by_rarity(message, "Золотая Мифическая Эволюция")

@bot.message_handler(commands=["Auevolegendaryenko"])
@require_podval
@require_topic
def evo_gold_legendary(message):
    send_sklad_by_rarity(message, "Золотая Легендарная Эволюция")

@bot.message_handler(commands=["Auevocesarenko"])
@require_podval
@require_topic
def evo_gold_cesar(message):
    send_sklad_by_rarity(message, "Золотая Царская Эволюция")

@bot.message_handler(commands=["Auevoimperatorenko"])
@require_podval
@require_topic
def evo_gold_imperator(message):
    send_sklad_by_rarity(message, "Золотая Великоимператорская Эволюция")

@bot.message_handler(commands=["eventenko"])
@require_podval
@require_topic
def sklad_event_cmd(message):
    send_event_cards(message)


def send_event_cards(message):
    data = load_data()
    u = get_or_init_user(data, message.from_user)
    cards_data = CARD_BY_ID

    grouped = []
    for cid, qty in u["cards"].items():
        if qty > 0 and cid in cards_data:
            if cid in {c["id"] for c in EVENT_CARDS} or cid in ARCHIVE_CARDS:
                grouped.append((cid, cards_data[cid], qty))

    if not grouped:
        bot.send_message(
            chat_id=message.chat.id,
            text="У тебя пока нет ивентовых карт.",
            parse_mode="HTML",
            message_thread_id=_thread_id_of(message)
        )
        return

    grouped.sort(key=lambda x: _safe_sklad_sort_key(x[0]))

    lines = ["<b>Ивентовые карты</b>"]
    for cid, card, qty in grouped:
        name = card.get("name", "Безымянная")
        url = card.get("image_url")
        if url:
            lines.append(f'<a href="{url}">{name}</a> — {qty} шт (ID: {cid})')
        else:
            lines.append(f"{name} — {qty} шт (ID: {cid})")

    chunk_and_send(message.chat.id, _thread_id_of(message), lines, chunk_size=100)


@bot.message_handler(commands=["raritycountenko"])
@require_podval
@require_topic
def raritycount_cmd(message):
    data = load_data()
    u = get_or_init_user(data, message.from_user)
    cards_data = CARD_BY_ID
    EVENT_CARDS_IDS = {c["id"] for c in EVENT_CARDS}

    def count_rarity(rarity):
        total = sum(1 for c in cards_data.values()
                    if c.get("rarity") == rarity
                    and c["id"] not in ARCHIVE_CARDS
                    and c["id"] not in EVENT_CARDS_IDS)
        unique = len([cid for cid, qty in u["cards"].items()
                      if qty > 0 and cards_data[cid]["rarity"] == rarity
                      and cid not in ARCHIVE_CARDS and cid not in EVENT_CARDS_IDS])
        return unique, total

    common_u, common_t = count_rarity("Обычная")
    rare_u, rare_t = count_rarity("Редкая")
    super_u, super_t = count_rarity("Сверхредкая")
    epic_u, epic_t = count_rarity("Эпическая")
    mific_u, mific_t = count_rarity("Мифическая")
    legend_u, legend_t = count_rarity("Легендарная")
    cesium_u, cesium_t = count_rarity("Царская")
    dimenko_u, dimenko_t = count_rarity("Великоимператорская")
    evo_u, evo_t = count_rarity("Эволюционная")

    exclusive_degrees = {
        "Эксклюзивная I степени",
        "Эксклюзивная II степени",
        "Эксклюзивная III степени",
    }

    exclusive_u = len([
        cid for cid, qty in u["cards"].items()
        if qty > 0 and cards_data[cid].get("rarity") in exclusive_degrees
    ])

    events_u = len([cid for cid, qty in u["cards"].items()
                    if qty > 0 and (cid in ARCHIVE_CARDS or cid in EVENT_CARDS_IDS)])

    total_all = sum(1 for c in cards_data.values()
                    if c["id"] not in ARCHIVE_CARDS
                    and c["id"] not in EVENT_CARDS_IDS
                    and c.get("rarity") not in exclusive_degrees
                    and c.get("rarity") != "Эволюционная")
    unique_all = len([cid for cid, qty in u["cards"].items()
                      if qty > 0 and cid in cards_data
                      and cid not in ARCHIVE_CARDS
                      and cid not in EVENT_CARDS_IDS
                      and cards_data[cid].get("rarity") not in exclusive_degrees
                      and cards_data[cid].get("rarity") != "Эволюционная"])

    total_score = u.get("score", 0)
    all_users = [(uid, usr.get("score", 0)) for uid, usr in data["users"].items()]
    all_users.sort(key=lambda x: x[1], reverse=True)
    rank = next((i + 1 for i, (uid, _) in enumerate(all_users) if uid == str(message.from_user.id)), None)

    text = (
        f"🎴 Постоянные карты: {unique_all} из {total_all}\n"
        f"⭐ Аура: {total_score}\n"
        f"🏆 Место в топе: {rank} из {len(all_users)}\n\n"
        f"🩵 <b>Обычные</b>: {common_u} из {common_t}\n"
        f"🧡 <b>Редкие</b>: {rare_u} из {rare_t}\n"
        f"💚 <b>Сверхредкие</b>: {super_u} из {super_t}\n"
        f"💜 <b>Эпические</b>: {epic_u} из {epic_t}\n"
        f"❤️ <b>Мифические</b>: {mific_u} из {mific_t}\n"
        f"🤍 <b>Легендарные</b>: {legend_u} из {legend_t}\n"
        f"💛 <b>Царские</b>: {cesium_u} из {cesium_t}\n"
        f"❤️‍🔥 <b>Великоимператорские</b>: {dimenko_u} из {dimenko_t}\n"
        f"💝‍ <b>Ивентовые</b>: {events_u}\n"
        f"💌 <b>Эксклюзивные</b>: {exclusive_u}\n"
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="HTML",
        message_thread_id=_thread_id_of(message)
    )



@bot.message_handler(commands=["evocollection", "evocollectionenko"])
@require_podval
@require_topic
def evocollection_cmd(message):
    """Эволюционные коллекции"""
    thread_id = _thread_id_of(message)

    text = (
        "📦 <b>Команды Эволюционных Коллекций:</b>\n\n"

        "🥉 <b>Бронзовые Эволюции:</b>\n\n"
        "🩵 Обычные — /Cuevocommonenko\n"
        "🧡 Редкие — /Cuevorareenko\n"
        "💚 Сверхредкие — /Cuevosuperrareenko\n"
        "💜 Эпические — /Cuevoepicenko\n"
        "❤️‍ Мифические — /Cuevomythicalenko\n"
        "🤍 Легендарные — /Cuevolegendaryenko\n"
        "💛 Царские — /Cuevocesarenko\n"
        "❤️‍🔥 Великоимператорские — /Cuevoimperatorenko\n\n"

        "🥈 <b>Серебряные Эволюции:</b>\n\n"
        "🩵 Обычные — /Agevocommonenko\n"
        "🧡 Редкие — /Agevorareenko\n"
        "💚 Сверхредкие — /Agevosuperrareenko\n"
        "💜 Эпические — /Agevoepicenko\n"
        "❤️‍ Мифические — /Agevomythicalenko\n"
        "🤍 Легендарные — /Agevolegendaryenko\n"
        "💛 Царские — /Agevocesarenko\n"
        "❤️‍🔥 Великоимператорские — /Agevoimperatorenko\n\n"

        "🥇 <b>Золотые Эволюции:</b>\n\n"
        "🩵 Обычные — /Auevocommonenko\n"
        "🧡 Редкие — /Auevorareenko\n"
        "💚 Сверхредкие — /Auevosuperrareenko\n"
        "💜 Эпические — /Auevoepicenko\n"
        "❤️‍ Мифические — /Auevomythicalenko\n"
        "🤍 Легендарные — /Auevolegendaryenko\n"
        "💛 Царские — /Auevocesarenko\n"
        "❤️‍🔥 Великоимператорские — /Auevoimperatorenko\n"
        "📊 Счетчик эволюционных карт — /evoraritycountenko\n"
        "🃏 Посмотреть одну конкретную карту — /view либо /viewenko (ID карты)\n"
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="HTML",
        message_thread_id=thread_id
    )




@bot.message_handler(commands=["view", "viewenko"])
@require_podval
@require_topic
def card_cmd(message):
    handle_card(message)


def handle_card(message):
    user = message.from_user
    thread_id = getattr(message, "message_thread_id", None)

    args = message.text.split()
    if len(args) < 2:
        bot.send_message(
            message.chat.id,
            "【⚠️】• Использование: /card [ID карты]",
            message_thread_id=thread_id,
            parse_mode="HTML"
        )
        return

    card_id = args[1]

    data = load_data()
    u = get_or_init_user(data, user)

    # Проверяем наличие карты у пользователя
    if card_id not in u.get("cards", {}) or u["cards"][card_id] <= 0:
        bot.send_message(
            message.chat.id,
            f"🪫 У тебя нет карты с ID {card_id}",
            parse_mode="HTML",
            message_thread_id=thread_id
        )
        return

    card = CARD_BY_ID.get(card_id)
    if not card:
        bot.send_message(
            message.chat.id,
            f"【⚠️】• Карта с ID {card_id} не найдена в базе",
            message_thread_id=thread_id
        )
        return

    name = card.get("name", "Безымянная")
    rarity = card.get("rarity", "?")
    url = card.get("image_url")
    qty = u["cards"][card_id]

    caption = (
        f"🎴 <b>{name}</b>\n"
        f"Редкость: {rarity}\n"
        f"ID: {card_id}\n"
        f"Количество: {qty}"
    )

    if url:
        try:
            bot.send_photo(
                message.chat.id,
                resolve_direct_image_url(url),
                caption=caption,
                parse_mode="HTML",
                message_thread_id=thread_id
            )
            return
        except:
            pass

    bot.send_message(
        message.chat.id,
        caption + (f"\n(Ссылка: {url})" if url else ""),
        parse_mode="HTML",
        message_thread_id=thread_id
    )





@bot.message_handler(commands=["profile", "profilenko"])
@require_podval
@require_topic
def profile_cmd(message):
    handle_profile(message)


def handle_profile(message):
    thread_id = _thread_id_of(message)
    data = load_data()

    target_user = None

    # --- 1) Если реплай ---
    if message.reply_to_message and message.reply_to_message.from_user:
        root_id = getattr(message, "message_thread_id", None)
        if root_id is None or message.reply_to_message.message_id != root_id:
            target_user = message.reply_to_message.from_user

    # --- 2) Аргумент /profile @user ---
    if not target_user:
        args = message.text.split()
        if len(args) > 1:
            arg = args[1].lstrip("@")
            for uid, u in data.get("users", {}).items():
                if u.get("username") == arg or str(uid) == arg:
                    target_user = type("U", (), {
                        "id": int(uid),
                        "username": u.get("username"),
                        "first_name": u.get("name", "")
                    })()
                    break

    # --- 3) По умолчанию — сам пользователь ---
    if not target_user:
        target_user = message.from_user

    # Проверка членства
    if not is_member(target_user.id, message.chat.id):
        bot.send_message(
            chat_id=message.chat.id,
            text="【⛔】• Пользователь не состоит в чате",
            message_thread_id=thread_id
        )
        return

    u = ensure_user_record(data, target_user.id, target_user.username, target_user.first_name)

    username = target_user.username if target_user.username else (target_user.first_name or "Пользователь")
    score = u.get("score", 0)

    exclusive_degrees = {"Эксклюзивная I степени", "Эксклюзивная II степени", "Эксклюзивная III степени"}
    EVENT_CARDS_IDS = {c["id"] for c in EVENT_CARDS}
    EVO_CARDS_IDS = {c["id"] for c in EVO_CARDS}

    # --- ОБНОВЛЁННЫЕ СЧЁТЧИКИ ---

    # ✔ Обычные карты (НЕ эво)
    total_cards = len([
        cid for cid, qty in u.get("cards", {}).items()
        if qty > 0
        and cid in CARD_BY_ID
        and cid not in ARCHIVE_CARDS
        and cid not in EVENT_CARDS_IDS
        and cid not in EVO_CARDS_IDS
        and CARD_BY_ID[cid].get("rarity") not in exclusive_degrees
        and CARD_BY_ID[cid].get("rarity") != "Эволюционная"
    ])

    # ✔ Эволюционные карты
    total_evo = len([
        cid for cid, qty in u.get("cards", {}).items()
        if qty > 0 and (
            cid in EVO_CARDS_IDS or
            CARD_BY_ID.get(cid, {}).get("rarity") == "Эволюционная"
        )
    ])

    # ✔ Эксклюзивные
    total_exclusive = len([
        cid for cid, qty in u.get("cards", {}).items()
        if qty > 0 and CARD_BY_ID.get(cid, {}).get("rarity") in exclusive_degrees
    ])

    # ✔ Ивентовые
    events_u = len([
        cid for cid, qty in u.get("cards", {}).items()
        if qty > 0 and (cid in ARCHIVE_CARDS or cid in EVENT_CARDS_IDS)
    ])

    description = u.get("description", "— не задано —")
    fav_id = u.get("favorite_card")

    # Рейтинг
    sorted_users = sorted(
        data.get("users", {}).items(),
        key=lambda x: x[1].get("score", 0),
        reverse=True
    )
    rank = next(
        (i + 1 for i, (uid, usr) in enumerate(sorted_users) if str(uid) == str(target_user.id)),
        None
    )

    caption = (
        f"📋 <b>АНКЕТА НА РАБОТУ</b>\n"
        f"🆔 ID: {target_user.id}\n"
        f"👤 Пользователь: {username}\n"
        f"🏆 Место в рейтинге: {rank if rank else '—'}\n\n"
        f"⭐ Накопленная аура: {score}\n"
        f"🃏 Постоянные карты: {total_cards}\n"
        f"🪬 Эволюционные карты: {total_evo}\n"
        f"💌 Эксклюзивные карты: {total_exclusive}\n"
        f"🎉 Ивентовые карты: {events_u}\n\n"
        f"📝 Описание: {description}"
    )

    # Любимая карта
    if fav_id and str(fav_id) in CARD_BY_ID and u.get("cards", {}).get(fav_id, 0) > 0:
        fav_card = CARD_BY_ID[str(fav_id)]
        fav_caption = caption + f"\n\n❤️ Любимая карта: {fav_card['name']} ({fav_card['rarity']})"
        url = fav_card.get("image_url")
        if url:
            try:
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=resolve_direct_image_url(url),
                    caption=fav_caption,
                    parse_mode="HTML",
                    message_thread_id=thread_id
                )
                return
            except Exception:
                fav_caption += f"\n(Ссылка: {url})"

        bot.send_message(
            chat_id=message.chat.id,
            text=fav_caption,
            parse_mode="HTML",
            message_thread_id=thread_id
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=caption + "\n❤️ Любимая карта: — не выбрана —",
            parse_mode="HTML",
            message_thread_id=thread_id
        )






@bot.message_handler(commands=["setdescenko"])
@require_podval
@require_topic
def set_description_cmd(message):
    thread_id = _thread_id_of(message)
    user = message.from_user
    data = load_data()
    u = get_or_init_user(data, user)

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(
            message.chat.id,
            "【⚠️】• Использование: /setdesc [текст описания]",
            message_thread_id=thread_id
        )
        return

    desc = args[1].strip()

    if len(desc) > 200:
        bot.send_message(
            message.chat.id,
            "【⚠️】• Описание слишком длинное. Максимум 200 символов.",
            message_thread_id=thread_id
        )
        return

    if message.from_user.id != user.id:
        bot.send_message(
            message.chat.id,
            "【⛔】• Ты не можешь менять чужое описание",
            message_thread_id=thread_id
        )
        return

    u["description"] = desc
    save_data_atomic(data)
    bot.send_message(
        message.chat.id,
        "✅ Описание обновлено!",
        message_thread_id=thread_id
    )


@bot.message_handler(commands=["setfavenko"])
@require_podval
@require_topic
def set_favorite_cmd(message):
    thread_id = _thread_id_of(message)  # поддержка тем
    user = message.from_user
    data = load_data()
    u = get_or_init_user(data, user)

    args = message.text.split()
    if len(args) < 2:
        bot.send_message(
            message.chat.id,
            "【⚠️】• Использование: /setfav [ID карты]",
            message_thread_id=thread_id
        )
        return

    card_id = args[1]
    if card_id not in u.get("cards", {}) or u["cards"][card_id] <= 0:
        bot.send_message(
            message.chat.id,
            f"🪫 У тебя нет карты с ID {card_id}",
            message_thread_id=thread_id
        )
        return

    if message.from_user.id != user.id:
        bot.send_message(
            message.chat.id,
            "【⛔】• Ты не можешь менять чужую любимую карту",
            message_thread_id=thread_id
        )
        return

    u["favorite_card"] = card_id
    save_data_atomic(data)
    bot.send_message(
        message.chat.id,
        f"✅ Любимая карта установлена: {CARD_BY_ID[card_id]['name']}",
        message_thread_id=thread_id
    )



ADMIN_IDS = {6869524426, 8005820607, 1046126527, 7690604299, 5072903681, 8343634136}

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@bot.message_handler(commands=["supergiftenko"])
def handle_giftenko(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "【⛔】• У тебя нет прав для этой команды")
        return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "【⚠️】• Используй: /supergiftenko <telegram_id> <card_id>")
        return

    target_id, card_id = args[1], args[2]

    card = next((c for c in CARDS + EVENT_CARDS if str(c["id"]) == str(card_id)), None)
    if not card:
        bot.reply_to(message, f"【⚠️】• Карта с id {card_id} не найдена")
        return

    data = load_data()
    users = data.setdefault("users", {})
    target_user = get_or_init_user(
        data,
        type("U", (), {"id": int(target_id), "first_name": "", "username": None})()
    )

    user_cards = target_user.setdefault("cards", {})

    if card_id in user_cards and user_cards[card_id] > 0:
        user_cards[card_id] += 1
        save_data_atomic(data)
        bot.reply_to(
            message,
            f"【🎁】• Повторная карта {card['name']} ({card['rarity']}) выдана пользователю {target_id}\nаура не начислены"
        )
    else:
        rarity = card["rarity"]
        score = SCORE_WEIGHTS.get(rarity, 0)

        user_cards[card_id] = 1
        target_user["score"] = target_user.get("score", 0) + score

        save_data_atomic(data)

        bot.reply_to(
            message,
            f"【🎁】• Карта {card['name']} ({rarity}) успешно выдана пользователю {target_id}\n+{score} ауры"
        )


@bot.message_handler(commands=["takeenko"])
def handle_takeenko(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "【⛔】• У тебя нет прав для этой команды")
        return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "【⚠️】• Используй: /takeenko <telegram_id> <card_id>")
        return

    target_id, card_id = args[1], args[2]

    data = load_data()
    users = data.setdefault("users", {})
    target_user = users.get(target_id)
    if not target_user:
        bot.reply_to(message, f"【⚠️】• Пользователь {target_id} не найден")
        return

    user_cards = target_user.get("cards", {})
    if card_id not in user_cards or user_cards[card_id] <= 0:
        bot.reply_to(message, f"【⚠️】• У пользователя {target_id} нет карты {card_id}")
        return

    user_cards[card_id] -= 1
    if user_cards[card_id] == 0:
        del user_cards[card_id]

    card = CARD_BY_ID.get(card_id)
    if card:
        rarity = card["rarity"]
        score_to_remove = SCORE_WEIGHTS.get(rarity, 0)
        target_user["score"] = max(0, target_user.get("score", 0) - score_to_remove)
    else:
        rarity = "?"

    save_data_atomic(data)

    bot.reply_to(
        message,
        f"【🗑】• У пользователя {target_id} забрана карта {card_id} ({rarity}), "
        f"списано {score_to_remove} ауры"
    )

@bot.message_handler(commands=["resetenko"])
def handle_resetenko(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "【⛔】• У тебя нет прав для этой команды")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "【⚠️】• Используй: /resetenko <telegram_id>")
        return

    target_id = args[1]

    data = load_data()
    users = data.setdefault("users", {})
    target_user = users.get(target_id)
    if not target_user:
        bot.reply_to(message, f"【⚠️】• Пользователь {target_id} не найден")
        return

    target_user["cards"] = {}
    target_user["score"] = 0
    save_data_atomic(data)

    bot.reply_to(message, f"【🗑】• Коллекция пользователя {target_id} полностью обнулена")

@bot.message_handler(commands=["allcardsenko"])
def handle_allcardsenko(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "【⛔】• У тебя нет прав для этой команды")
        return

    EVENT_CARDS_IDS = {c["id"] for c in EVENT_CARDS}
    rarity_order = {
        "Обычная": 1,
        "Редкая": 2,
        "Сверхредкая": 3,
        "Эпическая": 4,
        "Мифическая": 5,
        "Легендарная": 6,
        "Царская": 7,
        "Великоимператорская": 8,
        "Эксклюзивная I cтепени": 9,
        "Эксклюзивная II степени": 10,
        "Эксклюзивная III степени": 11,
        "Эволюционная": 12,
    }


    filtered = []
    for c in CARD_BY_ID.values():
        r = c.get("rarity")
        cid = c.get("id")
        is_daily = r in ("Обычная", "Редкая", "Сверхредкая", "Эпическая", "Мифическая", "Легендарная", "Царская", "Великоимператорская", "Эксклюзивная I cтепени", "Эксклюзивная II степени","Эксклюзивная III степени", "Эволюционная")

        is_event = cid in EVENT_CARDS_IDS or cid in ARCHIVE_CARDS
        if is_daily or is_event:
            filtered.append(c)

    def sort_key_card(card):
        cid = card["id"]
        m = re.search(r'(\d+)', cid)
        num = int(m.group(1)) if m else 0
        prefix = cid[:m.start()] if m else cid
        return (rarity_order.get(card.get("rarity"), 999), prefix, num)

    filtered.sort(key=sort_key_card)

    lines = [f"{c['id']} — {c['name']} ({c.get('rarity','?')})" for c in filtered]

    header = "📋 Все карты (повседневные + ивентовые):\n\n"
    max_chunk = 3500
    chunk = header
    for line in lines:
        if len(chunk) + len(line) + 1 > max_chunk:
            bot.send_message(
                chat_id=message.chat.id,
                text=chunk.rstrip(),
                parse_mode="HTML",
                disable_web_page_preview=True,
                message_thread_id=_thread_id_of(message)
            )
            chunk = ""
        chunk += line + "\n"

    if chunk.strip():
        bot.send_message(
            chat_id=message.chat.id,
            text=chunk.rstrip(),
            parse_mode="HTML",
            disable_web_page_preview=True,
            message_thread_id=_thread_id_of(message)
        )


@bot.message_handler(commands=["a"])
def handle_admhelp(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "【⛔】• У тебя нет прав для этой команды")
        return

    text = (
        "👑 <b>Админ-команды</b>\n\n"

        "🎁 <b>/supergiftenko</b> <code>telegram_id</code> <code>card_id</code>\n"
        "Подарить карту любую карту игроку, не смотря на наличие её в своей коллекции.\n"
        "Пример: <code>/supergiftenko 1488516622 l34</code>\n\n"

        "🗑 <b>/takeenko</b> <code>telegram_id</code> <code>card_id</code>\n"
        "Забрать карту у игрока и списать очки.\n"
        "Пример: <code>/takeenko 1488516622 r1</code>\n\n"

        "🧹 <b>/resetenko</b> <code>telegram_id</code>\n"
        "Полностью обнулить коллекцию и очки игрока.\n"
        "Пример: <code>/resetenko 1488516622</code>\n\n"

        "📋 <b>/allcardsenko</b>\n"
        "Показать список всех карт (повседневные и ивентовые).\n"
        "Пример: <code>/allcardsenko</code>\n\n"

        "ℹ️ Все команды доступны только администраторам."
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="HTML",
        message_thread_id=_thread_id_of(message)
    )


@bot.message_handler(commands=["massgive_loud"])
def massgive_loud(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ У тебя нет прав для этой команды")
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠ Использование: /massgive_loud <card_id>")
        return

    card_id = args[1]
    card = CARD_BY_ID.get(card_id)

    if not card:
        bot.reply_to(message, f"⚠ Карта с ID {card_id} не найдена")
        return

    rarity = card["rarity"]
    score_gain = SCORE_WEIGHTS.get(rarity, 0)

    data = load_data()
    users = data.get("users", {})

    given = 0
    new_count = 0

    for uid, u in users.items():
        cards = u.setdefault("cards", {})
        had_before = cards.get(card_id, 0) > 0

        cards[card_id] = cards.get(card_id, 0) + 1

        if not had_before and score_gain > 0:
            u["score"] = u.get("score", 0) + score_gain
            u["unique"] = u.get("unique", 0) + 1
            new_count += 1

        given += 1


        try:
            bot.send_message(
                uid,
                f"🎁 Массовая раздача! Ты получил карту: {card['name']} ({rarity})!"
            )
        except:
            pass

    save_data_atomic(data)

    bot.send_message(
        message.chat.id,
        f"📢 Массовая раздача завершена!\n"
        f"Карта: <b>{card['name']}</b> ({rarity})\n"
        f"Выдано игрокам: {given}\n"
        f"Новых уникальных: {new_count}\n"
        f"Очки начислены: {'да' if score_gain > 0 else 'нет'}",
        parse_mode="HTML"
    )




@bot.message_handler(commands=["massgive_silent"])
def massgive_silent(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ У тебя нет прав для этой команды")
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠ Использование: /massgive_silent <card_id>")
        return

    card_id = args[1]
    card = CARD_BY_ID.get(card_id)

    if not card:
        bot.reply_to(message, f"⚠ Карта с ID {card_id} не найдена")
        return

    rarity = card["rarity"]
    score_gain = SCORE_WEIGHTS.get(rarity, 0)

    data = load_data()
    users = data.get("users", {})

    for uid, u in users.items():
        cards = u.setdefault("cards", {})
        had_before = cards.get(card_id, 0) > 0

        cards[card_id] = cards.get(card_id, 0) + 1

        if not had_before and score_gain > 0:
            u["score"] = u.get("score", 0) + score_gain
            u["unique"] = u.get("unique", 0) + 1

    save_data_atomic(data)

    bot.reply_to(message, f"✅ Тихая массовая раздача карты {card_id} выполнена.")


@bot.message_handler(commands=["settopic"])
@require_podval
def set_topic_cmd(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status != "creator":
            bot.send_message(
                chat_id,
                "❗ Только создатель чата может устанавливать тему.",
                parse_mode="HTML"
            )
            return
    except Exception:
        bot.send_message(chat_id, "Не удалось проверить права пользователя.")
        return

    data = load_data()

    try:
        chat_info = bot.get_chat(chat_id)
        is_forum = getattr(chat_info, "is_forum", False)
    except Exception:
        is_forum = False

    # Если чат не форум — просто отключаем темы
    if not is_forum:
        allowed = data.setdefault("allowed_topics", {})
        allowed[str(chat_id)] = None
        save_data_atomic(data)

        bot.send_message(
            chat_id,
            "✅ Тема установлена.\nБот теперь работает в этом чате (темы отсутствуют).",
            parse_mode="HTML"
        )
        return

    thread_id = getattr(message, "message_thread_id", None)
    if thread_id is None:
        bot.send_message(
            chat_id,
            "❗ Эту команду нужно использовать внутри темы форума.",
            parse_mode="HTML"
        )
        return

    allowed = data.setdefault("allowed_topics", {})
    allowed[str(chat_id)] = thread_id
    save_data_atomic(data)

    bot.send_message(
        chat_id,
        f"✅ Тема установлена.\nТеперь бот работает только здесь.\n\nID темы: <code>{thread_id}</code>",
        parse_mode="HTML",
        message_thread_id=thread_id
    )


@bot.message_handler(commands=["unsettopic"])
@require_podval
def unset_topic_cmd(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status != "creator":
            bot.send_message(
                chat_id,
                "❗ Только создатель чата может отключить тему.",
                parse_mode="HTML"
            )
            return
    except Exception:
        bot.send_message(chat_id, "Не удалось проверить права пользователя.")
        return

    data = load_data()

    allowed = data.setdefault("allowed_topics", {})
    if str(chat_id) in allowed:
        del allowed[str(chat_id)]
        save_data_atomic(data)

        bot.send_message(
            chat_id,
            "✅ Тема откреплена.\nБот снова работает в любом месте чата.",
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            chat_id,
            "ℹ️ Для этого чата не была установлена тема.",
            parse_mode="HTML"
        )



if __name__ == "__main__":
    if not BOT_TOKEN:
        raise RuntimeError("8097953848:AAFExh6UX4saJzuBgV4gcNHjPyHZou3Ctyw")
    print("Dimenko pedofil...")

    try:
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"Ошибка в polling: {e}")