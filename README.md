# 🎬 Cinema Post Bot

Личный бот для КороСоба: отправляешь ссылку на статью — получаешь готовый пост для Telegram-канала с картинкой.

## Как работает

1. Отправляешь боту ссылку на статью (русскую или английскую)
2. Бот читает статью через `trafilatura`
3. Достаёт обложку (`og:image`)
4. Groq генерирует живой пост в стиле канала (~700 символов + хэштеги)
5. Бот возвращает: фото + текст поста + ссылка на источник

## Установка

### 1. Узнай свой Telegram User ID
Напиши [@userinfobot](https://t.me/userinfobot) — он вернёт твой числовой ID.

### 2. Создай бота
[@BotFather](https://t.me/BotFather) → `/newbot` → скопируй токен.

### 3. Залей на GitHub
```bash
git init && git add . && git commit -m "post bot"
git remote add origin https://github.com/твой/репо.git
git push -u origin main
```

### 4. Деплой на Render
1. [render.com](https://render.com) → New → Blueprint → подключи репо
2. Добавь переменные окружения:

| Переменная | Значение |
|---|---|
| `TELEGRAM_BOT_TOKEN` | токен от BotFather |
| `ALLOWED_USER_ID` | твой числовой Telegram ID |
| `GROQ_API_KEY` | ключ с console.groq.com |
| `RENDER_URL` | `https://your-app.onrender.com` |
| `WEBHOOK_SECRET` | любая случайная строка |

### 5. Зарегистрируй webhook
После деплоя, один раз локально:
```bash
pip install python-dotenv
cp .env.example .env  # заполни .env
python set_webhook.py
```
Должен вернуть: `{"ok": true, "result": true}`

### 6. Подключи Better Uptime
Добавь пинг на `https://your-app.onrender.com/health` каждые 3 минуты — чтобы Render не засыпал.

---

## Пример результата

```
🎬 Ридли Скотт подтвердил работу над новым фантастическим проектом

Легендарный режиссёр «Чужого» и «Гладиатора» намерен вернуться к 
научной фантастике. По данным Deadline, студия уже согласовала бюджет 
и ищет исполнителей главных ролей.

Скотту 86 лет, но он продолжает работать с темпом молодого режиссёра — 
в прошлом году вышел «Наполеон», сейчас в монтаже «Гладиатор 2».

#кино #РидлиСкотт #фантастика #новости #Голливуд

🔗 Источник
```
