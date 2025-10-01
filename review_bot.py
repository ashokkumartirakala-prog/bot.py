import os
import qrcode
from io import BytesIO
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
        "👋 Hi! Send me a business short code (e.g., salonA) and I'll generate a QR code for its review page."
    )

# Generate QR for given business code
async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    if code not in business_codes:
        await update.message.reply_text(
            "⚠️ Invalid code.\nAvailable codes: " + ", ".join(business_codes.keys())
        )
        return

    # Replace with your Render app base URL
    base_url = os.environ.get("APP_BASE_URL", "https://app-py-pn4q.onrender.com")
    url = f"{base_url}/r/{code}"

    # Generate QR
    qr = qrcode.make(url)
    bio = BytesIO()
    bio.name = "qr.png"
    qr.save(bio, "PNG")
    bio.seek(0)

    await update.message.reply_photo(
        photo=bio, caption=f"✅ QR for {business_codes[code]}:\n{url}"
    )

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("❌ TELEGRAM_BOT_TOKEN not set in environment!")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_qr))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()

