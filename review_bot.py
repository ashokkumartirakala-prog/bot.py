import qrcode
from io import BytesIO
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Mapping business short codes to names
business_codes = {
    "salonA": "Salon A",
    "hospitalB": "Hospital B",
}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Send a business short code (e.g., salonA) and I'll generate a QR code for its review page."
    )

# Generate QR for given business code
async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    if code not in business_codes:
        await update.message.reply_text("⚠️ Invalid code. Available codes: " + ", ".join(business_codes.keys()))
        return

    url = f"https://yourapp.onrender.com/r/{code}"  # Replace with your Render app URL

    # Generate QR
    qr = qrcode.make(url)
    bio = BytesIO()
    bio.name = "qr.png"
    qr.save(bio, "PNG")
    bio.seek(0)

    await update.message.reply_photo(photo=bio, caption=f"✅ QR for {business_codes[code]}:\n{url}")

def main():
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_qr))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
