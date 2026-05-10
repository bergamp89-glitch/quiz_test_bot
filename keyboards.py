from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


# =========================
# ASOSIY PASTKI MENYU
# =========================
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Test boshlash")],
        [KeyboardButton(text="📊 Mening natijalarim"), KeyboardButton(text="🏆 Reyting")],
        [KeyboardButton(text="⏹ Testni yakunlash")],
        [KeyboardButton(text="ℹ️ Yordam")],
    ],
    resize_keyboard=True
)


# =========================
# FAN TANLASH TUGMALARI
# =========================
subjects_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💰 Iqtisodiyot",
                callback_data="subject:iqtisodiyot"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📘 DM",
                callback_data="subject:dm"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📊 Mikro-Makro iqtisodiyot",
                callback_data="subject:mikro_makro"
            ),
        ],
        [
            InlineKeyboardButton(
                text="💵 Moliya",
                callback_data="subject:moliya"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📈 Statistika",
                callback_data="subject:statistika"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🚀 Innovatsion iqtisodiyot",
                callback_data="subject:innovatsion_iqtisodiyot"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📚 Menejment-Marketing",
                callback_data="subject:menejment_marketing"
            ),
        ],
    ]
)


# =========================
# SAVOLLAR SONI
# =========================
question_count_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="10 ta", callback_data="count:10"),
            InlineKeyboardButton(text="20 ta", callback_data="count:20"),
        ],
        [
            InlineKeyboardButton(text="50 ta", callback_data="count:50"),
            InlineKeyboardButton(text="100 ta", callback_data="count:100"),
        ],
    ]
)


# =========================
# JAVOB TUGMALARI
# =========================
def get_answer_keyboard(question_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="A",
                    callback_data=f"answer:{question_id}:A"
                ),
                InlineKeyboardButton(
                    text="B",
                    callback_data=f"answer:{question_id}:B"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="C",
                    callback_data=f"answer:{question_id}:C"
                ),
                InlineKeyboardButton(
                    text="D",
                    callback_data=f"answer:{question_id}:D"
                ),
            ],
        ]
    )


# =========================
# TESTNI YAKUNLASHNI TASDIQLASH
# =========================
finish_confirm_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Ha, yakunlash",
                callback_data="finish_confirm"
            ),
        ],
        [
            InlineKeyboardButton(
                text="↩️ Yo‘q, davom etish",
                callback_data="finish_cancel"
            ),
        ],
    ]
)