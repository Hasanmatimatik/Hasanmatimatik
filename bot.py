import random
import math
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Telegram bot tokeningizni shu yerga kiriting
API_TOKEN = "7864929753:AAGzH3cyzXE1ozYPQgGs13u2Vhp-c-nfUzM"

# Bot va dispatcher
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Foydalanuvchi ma'lumotlari
user_data = {}

# Klaviaturalar
level_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Birinchi daraja 🎯")],
        [KeyboardButton(text="Kvadrat tenglama 🟩")],
        [KeyboardButton(text="Logarifmlar 📈")],
        [KeyboardButton(text="Progressiyalar 🔢")],
        [KeyboardButton(text="Trigonometriya 🔺")]
    ],
    resize_keyboard=True
)

question_count_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="5 savol"), KeyboardButton(text="10 savol")],
        [KeyboardButton(text="20 savol"), KeyboardButton(text="Bekor qilish 🛑")]
    ],
    resize_keyboard=True
)

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Boshlash ✅")],
        [KeyboardButton(text="To'xtatish 🛑")]
    ],
    resize_keyboard=True
)

# Savol generatsiya qilish
def generate_question(level):
    try:
        if level == "Birinchi daraja 🎯":
            a, b = random.randint(1, 20), random.randint(1, 50)
            question = f"{a}x + {b} = 0"
            answer = round(-b / a, 2)

        elif level == "Kvadrat tenglama 🟩":
            a, b, c = random.randint(1, 10), random.randint(-20, 20), random.randint(-10, 10)
            question = f"{a}x² + {b}x + {c} = 0"
            D = b**2 - 4 * a * c
            if D < 0:
                return question, ["Tenglama ildizga ega emas"], "Tenglama ildizga ega emas"
            x1 = round((-b + math.sqrt(D)) / (2 * a), 2)
            x2 = round((-b - math.sqrt(D)) / (2 * a), 2)
            answer = f"x1={x1}, x2={x2}"

        elif level == "Logarifmlar 📈":
            base, num = random.randint(2, 5), random.randint(1, 50)
            question = f"log({num}) / log({base})"
            answer = round(math.log(num) / math.log(base), 2)

        elif level == "Progressiyalar 🔢":
            a, d, n = random.randint(1, 10), random.randint(1, 5), random.randint(5, 10)
            question = f"{n} ga qadar {a} dan {d} qadam bilan arifmetik progressiya yig'indisi"
            answer = n * (2 * a + (n - 1) * d) // 2

        elif level == "Trigonometriya 🔺":
            angle = random.choice([30, 45, 60])
            func = random.choice(["sin", "cos", "tan"])
            question = f"{func}({angle}°)"
            angle_rad = math.radians(angle)
            if func == "sin":
                answer = round(math.sin(angle_rad), 2)
            elif func == "cos":
                answer = round(math.cos(angle_rad), 2)
            else:
                answer = round(math.tan(angle_rad), 2)

        else:
            return None, None, None

        # Variantlar sonini oshirish
        wrong_answers = [answer + random.randint(-3, 3) for _ in range(3)] if isinstance(answer, (int, float)) else []
        wrong_answers = [wa for wa in wrong_answers if wa != answer]
        options = [answer] + wrong_answers[:3]
        random.shuffle(options)

        return question, options, answer

    except Exception as e:
        logging.error(f"Savol yaratishda xatolik: {e}")
        return None, None, None

# Start komanda
@dp.message(F.text == "/start")
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"level": None, "score": 0, "questions_asked": 0, "total_questions": 0}
    await message.answer("Salom! Matematika viktorinasiga xush kelibsiz! Darajani tanlash uchun 'Boshlash ✅' tugmasini bosing.", reply_markup=start_keyboard)

# Boshlash tugmasi
@dp.message(F.text == "Boshlash ✅")
async def ask_level(message: types.Message):
    await message.answer("Darajani tanlang:", reply_markup=level_keyboard)

# Darajani tanlash
@dp.message(F.text.in_(["Birinchi daraja 🎯", "Kvadrat tenglama 🟩", "Logarifmlar 📈", "Progressiyalar 🔢", "Trigonometriya 🔺"]))
async def ask_question_count(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["level"] = message.text
    await message.answer("Nechta savol yechishni xohlaysiz?", reply_markup=question_count_keyboard)

# Savollar sonini tanlash
@dp.message(F.text.in_(["5 savol", "10 savol", "20 savol"]))
async def start_quiz(message: types.Message):
    user_id = message.from_user.id
    count = int(message.text.split()[0])

    user_data[user_id]["score"] = 0
    user_data[user_id]["questions_asked"] = 0
    user_data[user_id]["total_questions"] = count

    await send_question(message)

# Savol yuborish
async def send_question(message: types.Message):
    user_id = message.from_user.id
    level = user_data[user_id]["level"]

    if user_data[user_id]["questions_asked"] >= user_data[user_id]["total_questions"]:
        await show_results(message)
        return

    user_data[user_id]["questions_asked"] += 1

    question, options, correct = generate_question(level)
    if not question:
        await message.answer("Savol yaratishda xatolik yuz berdi! Qayta urinib ko‘ring.")
        return

    user_data[user_id]["correct"] = correct

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(opt))] for opt in options],
        resize_keyboard=True
    )
    await message.answer(f"{user_data[user_id]['questions_asked']}. {question}", reply_markup=keyboard)

# Javobni tekshirish
@dp.message()
async def check_answer(message: types.Message):
    user_id = message.from_user.id

    if message.text == "To'xtatish 🛑":
        await message.answer("O'yin tugatildi. /start buyrug'i bilan qayta boshlashingiz mumkin.")
        return

    if user_id in user_data and "correct" in user_data[user_id]:
        correct_answer = user_data[user_id]["correct"]

        if str(message.text).strip() == str(correct_answer).strip():
            user_data[user_id]["score"] += 1
            await message.answer("To'g'ri! 🎉")
        else:
            await message.answer(f"Noto'g'ri 😔. To'g'ri javob: {correct_answer}")

    await send_question(message)

# Botni ishga tushirish
async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
