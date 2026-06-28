"""
Generates a ready-to-publish Telegram post from article text using Groq.
"""

import os
import json
import logging
from groq import Groq
from article_parser import ParsedArticle

logger = logging.getLogger(__name__)

client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """Ты — редактор Telegram-канала о кино КороСоба. 
Пишешь короткие, живые посты для аудитории, которая любит кино.

Получаешь текст статьи и должен написать готовый пост для Telegram.

Правила:
- Длина поста: 600–900 символов (это важно — не больше)
- Начни с яркого заголовка на русском с эмодзи (даже если статья на английском)
- 2–3 абзаца: суть новости, важный контекст, интересная деталь
- В конце — 3–5 хэштегов на русском (#кино #новости и т.д.)
- Стиль: живой, не сухой, как будто пишет человек, а не робот
- Если статья на английском — переведи суть, не переводи дословно
- Не добавляй ссылку — она будет прикреплена отдельно

Ответь ТОЛЬКО текстом поста, без каких-либо пояснений."""


def generate_post(article: ParsedArticle) -> str:
    """Generate a Telegram post from a parsed article."""
    user_prompt = f"""Статья: {article.url}

Заголовок: {article.title or '(нет)'}

Текст:
{article.text}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=700,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        post = response.choices[0].message.content.strip()
        logger.info(f"✅ Post generated: {len(post)} chars")
        return post

    except Exception as e:
        logger.error(f"Groq generation failed: {e}")
        raise
