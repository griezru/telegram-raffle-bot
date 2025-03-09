import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# تنظیمات لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن ربات تلگرام
TELEGRAM_TOKEN = '8020034978:AAHwryR20A3fod_sBJUnvkZpk9tlWzUfmLI'
# AdsGram اطلاعات
ADSGRAM_BLOCK_ID = 'YOUR_BLOCK_ID'  # شناسه بلاک تبلیغاتی را از AdsGram دریافت کنید
ADSGRAM_API_URL = 'https://api.adsgram.ai/v1/reward'

# لیست کاربران و بلیط‌های آن‌ها
user_tickets = {}

# دستور /start برای معرفی ربات
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    update.message.reply_text(
        "👋 سلام! برای دریافت بلیط قرعه‌کشی، لطفاً روی دکمه زیر کلیک کنید و ویدیو را کامل مشاهده کنید:"
        f"\n🎥 [مشاهده تبلیغ و دریافت بلیط](https://sad.adsgram.ai/reward/?blockId={ADSGRAM_BLOCK_ID}&userId={user_id})"
        "\nپس از مشاهده کامل، دستور /check را ارسال کنید تا بلیط شما ثبت شود.",
        parse_mode="Markdown"
    )

# بررسی مشاهده تبلیغ و اضافه کردن بلیط
def check(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # ارسال درخواست به API AdsGram برای بررسی وضعیت تبلیغ
    response = requests.post(ADSGRAM_API_URL, json={
        "blockId": ADSGRAM_BLOCK_ID,
        "userId": str(user_id)
    })

    if response.status_code == 200:
        data = response.json()
        if data.get("rewarded"):
            user_tickets[user_id] = user_tickets.get(user_id, 0) + 1
            update.message.reply_text(f"🎉 تبریک! شما یک بلیط دریافت کردید.\n🎫 تعداد بلیط‌های شما: {user_tickets[user_id]}")
        else:
            update.message.reply_text("⛔ شما هنوز تبلیغ را به‌طور کامل مشاهده نکرده‌اید! لطفاً دوباره تلاش کنید.")
    else:
        update.message.reply_text("❌ خطا در ارتباط با سرور AdsGram. لطفاً بعداً تلاش کنید.")

# نمایش تعداد بلیط‌ها
def my_tickets(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    tickets = user_tickets.get(user_id, 0)
    update.message.reply_text(f"🎫 تعداد بلیط‌های شما: {tickets}")

# اعلام برنده (مدیر فقط می‌تواند اجرا کند)
def announce_winner(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != 295614432:  # آیدی عددی مدیر
        update.message.reply_text("⛔ فقط مدیر می‌تواند قرعه‌کشی را انجام دهد.")
        return

    if not user_tickets:
        update.message.reply_text("❌ هیچ بلیطی ثبت نشده است.")
        return

    # پیدا کردن کاربری که بیشترین بلیط را دارد
    winner_id = max(user_tickets, key=user_tickets.get)
    winner_tickets = user_tickets[winner_id]

    update.message.reply_text(f"🏆 برنده قرعه‌کشی:\n👤 آیدی: `{winner_id}`\n🎫 تعداد بلیط‌ها: {winner_tickets}\n🎁 جایزه: ۱۵ استارز تلگرام", parse_mode="Markdown")

# راه‌اندازی ربات
def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("check", check))
    dispatcher.add_handler(CommandHandler("mytickets", my_tickets))
    dispatcher.add_handler(CommandHandler("winner", announce_winner))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

