import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from config import BOT_TOKEN

from keyboards import (
    main_menu,
    subjects_keyboard,
    question_count_keyboard,
    get_answer_keyboard,
    finish_confirm_keyboard,
)

from database import (
    init_db,
    SUBJECT_NAMES,
    get_random_questions,
    get_question_count,
    save_result,
    get_user_results,
    get_top_results,
    add_user,
    get_users_count,
    get_results_count,
    get_questions_count,
    get_subjects_statistics,
)


# =========================
# BOT VA DISPATCHER
# =========================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# =========================
# FOYDALANUVCHI TEST HOLATLARI
# =========================
# Faol testlar vaqtincha RAMda saqlanadi.
# Bot restart bo‘lsa, faol testlar yo‘qoladi.
# Tugagan natijalar esa quiz.db bazasida qoladi.
user_sessions = {}


# =========================
# FOIZ BO‘YICHA BAHO
# =========================
def get_grade(percent: float):
    if percent >= 90:
        return "A'lo 🏆"
    elif percent >= 70:
        return "Yaxshi ✅"
    elif percent >= 50:
        return "Qoniqarli ⚠️"
    return "Qoniqarsiz ❌"


# =========================
# FOYDALANUVCHINI BAZAGA YOZISH
# =========================
def register_user(message: Message):
    add_user(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )


# =========================
# /START
# =========================
@dp.message(CommandStart())
async def start_handler(message: Message):
    register_user(message)

    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "Attestatsiya Quiz botiga xush kelibsiz.\n\n"
        "Quyidagi menyudan kerakli bo‘limni tanlang:",
        reply_markup=main_menu
    )


# =========================
# TEST BOSHLASH
# =========================
@dp.message(F.text == "📚 Test boshlash")
async def start_test_handler(message: Message):
    register_user(message)

    user_id = message.from_user.id

    # Faol test himoyasi
    if user_id in user_sessions and "questions" in user_sessions[user_id]:
        await message.answer(
            "⚠️ Sizda hozir faol test bor.\n\n"
            "Yangi test boshlash uchun avval hozirgi testni yakunlang.\n\n"
            "Pastki menyudan:\n"
            "⏹ Testni yakunlash\n\n"
            "tugmasini bosing yoki testni oxirigacha ishlang.",
            reply_markup=main_menu
        )
        return

    await message.answer(
        "📚 Fan tanlang:",
        reply_markup=subjects_keyboard
    )


# =========================
# MENING NATIJALARIM
# =========================
@dp.message(F.text == "📊 Mening natijalarim")
async def my_results_handler(message: Message):
    register_user(message)

    results = get_user_results(message.from_user.id)

    if not results:
        await message.answer(
            "📊 Sizda hali natijalar yo‘q.\n\n"
            "Avval test ishlang."
        )
        return

    text = "📊 Oxirgi natijalaringiz:\n\n"

    for index, result in enumerate(results, start=1):
        text += (
            f"{index}. 📚 {result['subject_name']}\n"
            f"   📝 Jami: {result['total']} ta\n"
            f"   ✅ To‘g‘ri: {result['correct_count']} ta\n"
            f"   ❌ Xato: {result['wrong_count']} ta\n"
            f"   📈 Foiz: {result['percent']}%\n"
            f"   🕒 Sana: {result['created_at']}\n\n"
        )

    await message.answer(text)


# =========================
# REYTING
# =========================
@dp.message(F.text == "🏆 Reyting")
async def rating_handler(message: Message):
    register_user(message)

    results = get_top_results()

    if not results:
        await message.answer("🏆 Reyting hali bo‘sh.")
        return

    text = "🏆 Top 10 reyting:\n\n"

    for index, result in enumerate(results, start=1):
        name = result["full_name"] or "Foydalanuvchi"

        text += (
            f"{index}. {name}\n"
            f"   📚 {result['subject_name']}\n"
            f"   ✅ {result['correct_count']}/{result['total']}\n"
            f"   📈 {result['percent']}%\n\n"
        )

    await message.answer(text)


# =========================
# BOT STATISTIKASI
# =========================
@dp.message(F.text == "📈 Statistika")
async def bot_statistics_handler(message: Message):
    register_user(message)

    users_count = get_users_count()
    results_count = get_results_count()
    questions_count = get_questions_count()
    subjects_stats = get_subjects_statistics()

    text = (
        "📈 Bot statistikasi:\n\n"
        f"👥 Foydalanuvchilar soni: {users_count} ta\n"
        f"📝 Bazadagi testlar soni: {questions_count} ta\n"
        f"✅ Ishlangan testlar soni: {results_count} ta\n\n"
        "📚 Fanlar bo‘yicha testlar:\n"
    )

    if subjects_stats:
        for item in subjects_stats:
            text += f"• {item['subject_name']}: {item['count']} ta\n"
    else:
        text += "Hali savollar yo‘q.\n"

    await message.answer(text)


# =========================
# YORDAM
# =========================
@dp.message(F.text == "ℹ️ Yordam")
async def help_handler(message: Message):
    register_user(message)

    await message.answer(
        "ℹ️ Botdan foydalanish:\n\n"
        "1. 📚 Test boshlash tugmasini bosing\n"
        "2. Fan tanlang\n"
        "3. Savollar sonini tanlang\n"
        "4. Javoblarni belgilang\n"
        "5. Oxirida natijangizni ko‘ring\n\n"
        "✅ Himoyalar:\n"
        "• Test tugamasdan yangi test boshlanmaydi\n"
        "• Bitta savolga ikki marta javob berib bo‘lmaydi\n"
        "• Testni muddatidan oldin yakunlash mumkin\n\n"
        "📈 Statistika bo‘limida foydalanuvchilar soni va testlar sonini ko‘rishingiz mumkin."
    )


# =========================
# TESTNI MUDDATIDAN AVVAL YAKUNLASH
# =========================
@dp.message(F.text == "⏹ Testni yakunlash")
async def finish_test_button_handler(message: Message):
    register_user(message)

    user_id = message.from_user.id

    if user_id not in user_sessions or "questions" not in user_sessions[user_id]:
        await message.answer(
            "Sizda hozir faol test yo‘q.\n\n"
            "Test boshlash uchun 📚 Test boshlash tugmasini bosing.",
            reply_markup=main_menu
        )
        return

    await message.answer(
        "⏹ Testni muddatidan avval yakunlamoqchimisiz?\n\n"
        "Eslatma: javob berilmagan savollar xato hisoblanadi.",
        reply_markup=finish_confirm_keyboard
    )


# =========================
# FAN TANLASH
# =========================
@dp.callback_query(F.data.startswith("subject:"))
async def subject_selected_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    # Faol test himoyasi
    if user_id in user_sessions and "questions" in user_sessions[user_id]:
        await callback.message.answer(
            "⚠️ Sizda faol test bor.\n\n"
            "Avval hozirgi testni yakunlang yoki oxirigacha ishlang.",
            reply_markup=main_menu
        )
        await callback.answer()
        return

    subject_key = callback.data.split(":")[1]
    subject_name = SUBJECT_NAMES.get(subject_key, "Noma’lum fan")

    user_sessions[user_id] = {
        "subject_key": subject_key,
        "subject_name": subject_name,
    }

    await callback.message.answer(
        f"✅ Tanlangan fan: {subject_name}\n\n"
        "Nechta savol ishlamoqchisiz?",
        reply_markup=question_count_keyboard
    )

    await callback.answer()


# =========================
# SAVOLLAR SONINI TANLASH
# =========================
@dp.callback_query(F.data.startswith("count:"))
async def count_selected_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    # Agar test allaqachon boshlangan bo‘lsa, eski count tugmasi orqali qayta boshlashni bloklaymiz.
    if user_id in user_sessions and "questions" in user_sessions[user_id]:
        await callback.message.answer(
            "⚠️ Sizda hozir faol test bor.\n\n"
            "Avval hozirgi testni yakunlang yoki oxirigacha ishlang.",
            reply_markup=main_menu
        )
        await callback.answer()
        return

    count = int(callback.data.split(":")[1])

    if user_id not in user_sessions or "subject_key" not in user_sessions[user_id]:
        await callback.message.answer(
            "Avval fan tanlang.",
            reply_markup=subjects_keyboard
        )
        await callback.answer()
        return

    subject_key = user_sessions[user_id]["subject_key"]
    subject_name = user_sessions[user_id]["subject_name"]

    available_count = get_question_count(subject_key)

    if available_count == 0:
        await callback.message.answer(
            f"❌ {subject_name} fanida hali savollar yo‘q."
        )
        await callback.answer()
        return

    if count > available_count:
        count = available_count
        await callback.message.answer(
            f"ℹ️ Bazada hozir {available_count} ta savol bor.\n"
            f"Test {available_count} ta savol bilan boshlanadi."
        )

    questions = get_random_questions(subject_key, count)

    user_sessions[user_id] = {
        "subject_key": subject_key,
        "subject_name": subject_name,
        "questions": questions,
        "current_index": 0,
        "correct_count": 0,
        "wrong_count": 0,

        # Ikki marta javob berishdan himoya
        "answered_questions": set(),
    }

    await callback.message.answer(
        f"🚀 Test boshlandi!\n\n"
        f"📚 Fan: {subject_name}\n"
        f"📝 Savollar soni: {len(questions)} ta\n\n"
        f"Testni muddatidan oldin tugatish uchun pastki menyudan:\n"
        f"⏹ Testni yakunlash\n\n"
        f"tugmasini bosing."
    )

    await send_question(callback.message, user_id)
    await callback.answer()


# =========================
# SAVOL YUBORISH
# =========================
async def send_question(message: Message, user_id: int):
    session = user_sessions[user_id]
    current_index = session["current_index"]
    questions = session["questions"]

    question = questions[current_index]

    text = (
        f"📝 {current_index + 1}/{len(questions)}-savol\n\n"
        f"{question['question']}\n\n"
        f"A) {question['option_a']}\n"
        f"B) {question['option_b']}\n"
        f"C) {question['option_c']}\n"
        f"D) {question['option_d']}"
    )

    await message.answer(
        text,
        reply_markup=get_answer_keyboard(question["id"])
    )


# =========================
# YAKUNLASHNI BEKOR QILISH
# =========================
@dp.callback_query(F.data == "finish_cancel")
async def finish_cancel_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in user_sessions or "questions" not in user_sessions[user_id]:
        await callback.message.answer(
            "Sizda faol test yo‘q.",
            reply_markup=main_menu
        )
        await callback.answer()
        return

    await callback.message.answer(
        "✅ Test davom etadi.\n\n"
        "Joriy savolga javob berishda davom eting."
    )

    await callback.answer()


# =========================
# YAKUNLASHNI TASDIQLASH
# =========================
@dp.callback_query(F.data == "finish_confirm")
async def finish_confirm_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in user_sessions or "questions" not in user_sessions[user_id]:
        await callback.message.answer(
            "Sizda faol test yo‘q.",
            reply_markup=main_menu
        )
        await callback.answer()
        return

    session = user_sessions[user_id]
    answered_count = session["correct_count"] + session["wrong_count"]

    if answered_count == 0:
        await callback.message.answer(
            "⏹ Test yakunlandi.\n\n"
            "Siz hali birorta savolga javob bermadingiz, "
            "shuning uchun natija saqlanmadi.",
            reply_markup=main_menu
        )

        del user_sessions[user_id]
        await callback.answer()
        return

    await finish_test(callback.message, callback, early=True)
    await callback.answer()


# =========================
# JAVOBNI QABUL QILISH
# =========================
@dp.callback_query(F.data.startswith("answer:"))
async def answer_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in user_sessions or "questions" not in user_sessions[user_id]:
        await callback.message.answer(
            "Sizda faol test yo‘q.\n\n"
            "Test boshlash uchun 📚 Test boshlash tugmasini bosing.",
            reply_markup=main_menu
        )
        await callback.answer()
        return

    _, question_id, selected_answer = callback.data.split(":")
    question_id = int(question_id)

    session = user_sessions[user_id]
    current_index = session["current_index"]
    question = session["questions"][current_index]

    # Eski savol tugmasini bosib yuborsa
    if question["id"] != question_id:
        await callback.answer(
            "Bu eski savol. Hozirgi savolga javob bering.",
            show_alert=True
        )
        return

    # Ikki marta javob berishni bloklash
    if question_id in session["answered_questions"]:
        await callback.answer(
            "Bu savolga allaqachon javob bergansiz.",
            show_alert=True
        )
        return

    session["answered_questions"].add(question_id)

    # Javob berilgandan keyin tugmalarni o‘chirib qo‘yamiz
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    correct_answer = str(question["correct_answer"]).strip().upper()
    selected_answer = selected_answer.strip().upper()

    if selected_answer == correct_answer:
        session["correct_count"] += 1
        answer_text = "✅ To‘g‘ri javob!"
    else:
        session["wrong_count"] += 1
        answer_text = (
            f"❌ Xato javob.\n"
            f"✅ To‘g‘ri javob: {correct_answer}"
        )

    if question.get("explanation"):
        answer_text += f"\n\n💡 Izoh: {question['explanation']}"

    await callback.message.answer(answer_text)

    session["current_index"] += 1

    if session["current_index"] >= len(session["questions"]):
        await finish_test(callback.message, callback, early=False)
    else:
        await send_question(callback.message, user_id)

    await callback.answer()


# =========================
# TESTNI YAKUNLASH
# =========================
async def finish_test(message: Message, callback: CallbackQuery, early=False):
    user_id = callback.from_user.id
    session = user_sessions[user_id]

    selected_total = len(session["questions"])
    answered_count = session["correct_count"] + session["wrong_count"]
    unanswered_count = selected_total - answered_count

    correct_count = session["correct_count"]

    if early:
        wrong_count = session["wrong_count"] + unanswered_count
        total = selected_total
        title = "⏹ Test muddatidan avval yakunlandi!"
    else:
        wrong_count = session["wrong_count"]
        total = selected_total
        title = "✅ Test yakunlandi!"

    percent = round((correct_count / total) * 100, 2) if total > 0 else 0
    grade = get_grade(percent)

    full_name = callback.from_user.full_name
    username = callback.from_user.username

    save_result(
        user_id=user_id,
        full_name=full_name,
        username=username,
        subject_key=session["subject_key"],
        total=total,
        correct_count=correct_count,
        wrong_count=wrong_count,
        percent=percent,
    )

    text = (
        f"{title}\n\n"
        f"📚 Fan: {session['subject_name']}\n"
        f"📝 Jami savol: {total} ta\n"
        f"✅ To‘g‘ri: {correct_count} ta\n"
        f"❌ Xato: {wrong_count} ta\n"
        f"📈 Natija: {percent}%\n"
        f"🏆 Baho: {grade}"
    )

    if early:
        text += (
            f"\n\n"
            f"ℹ️ Javob berilgan savollar: {answered_count} ta\n"
            f"⏳ Javobsiz qolgan savollar: {unanswered_count} ta"
        )

    await message.answer(text, reply_markup=main_menu)

    del user_sessions[user_id]


# =========================
# NOMA’LUM XABAR
# =========================
@dp.message()
async def unknown_message_handler(message: Message):
    register_user(message)

    await message.answer(
        "Men sizni tushunmadim.\n\n"
        "Quyidagi menyudan foydalaning:",
        reply_markup=main_menu
    )


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================
async def main():
    init_db()
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())