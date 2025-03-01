from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import random
import math
import asyncio
import logging

# Loglarni yoqish
logging.basicConfig(level=logging.INFO)

# API tokeningizni shu yerga joylashtiring
API_TOKEN = "7864929753:AAGzH3cyzXE1ozYPQgGs13u2Vhp-c-nfUzM"

# Bot va dispatcher obyektlarini yaratish
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

user_data = {}

# Klaviaturalar
level_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Oson😃"), KeyboardButton(text="O'rta😅")],
        [KeyboardButton(text="Qiyin🧐")]
    ],
    resize_keyboard=True
)

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Boshlash👍")],
        [KeyboardButton(text="boshlamaslik🤐")]
    ],
    resize_keyboard=True
)

# Savol generatsiyasi
def generate_question(level):
    try:
        if level == "Oson😃":
            num1, num2 = random.randint(1, 10), random.randint(1, 10)
            operator = random.choice(["+", "-"])
            question = f"{num1} {operator} {num2}"
            answer = eval(question)

        elif level == "O'rta😅":
            num1, num2 = random.randint(1, 20), random.randint(1, 10)
            operator = random.choice(["*", "/"])
            question = f"{num1} {operator} {num2}"
            answer = round(eval(question), 2) if operator == "/" else eval(question)

        elif level == "Qiyin🧐":
            if random.choice([True, False]):
                base = random.randint(1, 10)
                exp = random.randint(2, 4)
                question = f"{base} ^ {exp} (Bu daraja, ya'ni {base} ning {exp}-darajasi)"
                answer = base ** exp
            else:
                num = random.randint(1, 100)
                question = f"√{num} (👨‍🎓Bu ildiz, ya'ni {num} ning kvadrat ildizi)"
                answer = round(math.sqrt(num), 2)

        else:
            return None, None, None

        wrong_answers = [answer + random.randint(-3, 3) for _ in range(2)]
        options = [answer] + wrong_answers
        random.shuffle(options)

        return question, options, answer

    except Exception as e:
        logging.error(f"Savol yaratishda xatolik: {e}")
        return None, None, None

# /start komandasi
@dp.message(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"level": None, "score": 0, "questions_asked": 0}
    await message.answer("📗📓💸🇺🇿 Matematika viktorinasiga xush kelibsiz!\n\nDarajani tanlash uchun 'Boshlash👍' tugmasini bosing.", reply_markup=start_keyboard)

# Daraja tanlash
@dp.message(lambda message: message.text == "Boshlash👍")
async def ask_level(message: types.Message):
    await message.answer("Darajani tanlang:", reply_markup=level_keyboard)

# Savollarni boshlash
@dp.message(lambda message: message.text in ["Oson😃", "O'rta😅", "Qiyin🧐"])
async def start_quiz(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id].update({"level": message.text, "score": 0, "questions_asked": 0})
    await send_question(message)

# Savol yuborish
async def send_question(message: types.Message):
    user_id = message.from_user.id
    level = user_data[user_id]["level"]
    user_data[user_id]["questions_asked"] += 1

    if user_data[user_id]["questions_asked"] > 10:
        await show_results(message)
        return

    question, options, correct = generate_question(level)
    if not question:
        await message.answer("Savol yaratishda xatolik! 😔")
        return

    user_data[user_id]["correct"] = correct
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(str(opt))] for opt in options],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    keyboard.keyboard.append([KeyboardButton("Boshlash👍")])

    await message.answer(f"{user_data[user_id]['questions_asked']}. {question}", reply_markup=keyboard)

# Javobni tekshirish
@dp.message()
async def check_answer(message: types.Message):
    user_id = message.from_user.id

    if message.text == "boshlamaslik🤐":
        await show_results(message)
        return

    if user_id in user_data and "correct" in user_data[user_id]:
        correct_answer = user_data[user_id]["correct"]
        if message.text == str(correct_answer):
            user_data[user_id]["score"] += 1
            await message.answer("✅ To'g'ri javob! Barakalla!")
        else:
            await message.answer(f"❌ Noto'g'ri! To'g'ri javob: {correct_answer}")

        del user_data[user_id]["correct"]

    await send_question(message)

# Natijani ko'rsatish
async def show_results(message: types.Message):
    user_id = message.from_user.id
    score = user_data[user_id]["score"]

    if score >= 8:
        result_message = f"🏆 Zo'r natija! {score} / 10 ta to'g'ri javob berdingiz. 🎉"
    elif score >= 5:
        result_message = f"😊 Yaxshi natija! {score} / 10 ta to'g'ri javob. Harakatda davom eting!"
    else:
        result_message = f"😕 Juda past natija! {score} / 10 ta to'g'ri javob. Yana urinib ko'ring!"

    await message.answer(result_message, reply_markup=start_keyboard)

# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
