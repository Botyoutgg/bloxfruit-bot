"""
====================================================
   UCHIRO STORE — Shop Bot (shop_bot.py)
   Bot សម្រាប់អតិថិជន
====================================================
"""
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters, ConversationHandler
)
import store_data as db

SHOP_BOT_TOKEN = os.environ.get("SHOP_BOT_TOKEN", "8743632619:AAGoQBL5NaDn_UV71Ad2SXubKKjiDk_uqGE")
ADMIN_CHAT_ID  = int(os.environ.get("ADMIN_CHAT_ID", "6594079594"))

logging.basicConfig(level=logging.INFO)

(CHOOSE_CATEGORY, CHOOSE_ITEM, CHOOSE_ACCOUNT,
 ENTER_ROBLOX, WAITING_PAYMENT) = range(5)


# ────────────────────────────────────────────────
#   MAIN MENU
# ────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = db.load()
    s    = data["settings"]
    keyboard = [
        [InlineKeyboardButton("🍎 ទិញ Fruit",              callback_data="cat_fruits")],
        [InlineKeyboardButton("⚔️ Service Blox Fruit",     callback_data="cat_services")],
        [InlineKeyboardButton("🎮 ទិញ Account Blox Fruit", callback_data="cat_accounts")],
        [InlineKeyboardButton("📖 របៀបទិញ",                callback_data="how_to_buy")],
        [InlineKeyboardButton("🆘 ជំនួយ / Support",        callback_data="support")],
        [InlineKeyboardButton("📞 ទំនាក់ទំនង Admin",       callback_data="contact")],
    ]
    text = (
        f"👋 សូមស្វាគមន៍មក *{s['store_name']}* 🇰🇭\n"
        f"━━━━━━━━━━━━━━\n"
        f"🍎 Fruits | 🎮 Account | ⚔️ Service\n"
        f"💳 បង់តាម *Acleda* | ⚡ ផ្ញើរហ័ស\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"សូមជ្រើសរើស 👇"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown",
                                        reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown",
                                                       reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_CATEGORY


# ────────────────────────────────────────────────
#   CATEGORY
# ────────────────────────────────────────────────
async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data
    store = db.load()
    s     = store["settings"]

    # 🍎 FRUITS
    if data == "cat_fruits":
        admin_url = f"https://t.me/{s['admin_username'].replace('@','')}"
        keyboard  = [
            [InlineKeyboardButton("💬 ទំនាក់ទំនង Admin", url=admin_url)],
            [InlineKeyboardButton("🔙 ត្រឡប់", callback_data="back_main")],
        ]
        fruit_list = "\n".join([f"• {k} — {v}" for k, v in store["fruits"].items()])
        if s.get("fruit_list_photo"):
            await query.message.reply_photo(
                photo=s["fruit_list_photo"],
                caption=(
                    f"🍎 *បញ្ជី Fruit — {s['store_name']}*\n"
                    f"━━━━━━━━━━━━━━\n{fruit_list}\n"
                    f"━━━━━━━━━━━━━━\n\n"
                    f"👉 ទំនាក់ទំនង: {s['admin_username']}"
                ),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await query.delete_message()
        else:
            await query.edit_message_text(
                f"🍎 *បញ្ជី Fruit*\n━━━━━━━━━━━━━━\n{fruit_list}\n"
                f"━━━━━━━━━━━━━━\n\n👉 {s['admin_username']}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        return CHOOSE_CATEGORY

    # ⚔️ SERVICES
    elif data == "cat_services":
        context.user_data["category"] = "Service"
        photos = s.get("service_photos", [])
        for i, photo in enumerate(photos, 1):
            try:
                await query.message.reply_photo(photo=photo, caption=f"📸 Service {i}")
            except:
                pass

        services = store["services"]
        keyboard = [[InlineKeyboardButton(f"{k} — {v}", callback_data=f"item_{k}")]
                    for k, v in services.items()]
        keyboard.append([InlineKeyboardButton("🔙 ត្រឡប់", callback_data="back_main")])
        await query.message.reply_text(
            f"⚔️ *Service Blox Fruit*\n━━━━━━━━━━━━━━\nជ្រើសសេវា 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.delete_message()
        return CHOOSE_ITEM

    # 🎮 ACCOUNTS
    elif data == "cat_accounts":
        available = {k: v for k, v in store["accounts"].items() if not v.get("sold")}
        if not available:
            keyboard = [[InlineKeyboardButton("🔙 ត្រឡប់", callback_data="back_main")]]
            await query.edit_message_text(
                "😔 *គ្មាន Account ទំនេរ*\nសូមទំនាក់ទំនង admin ឬមកពិនិត្យម្ដងទៀត!",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return CHOOSE_CATEGORY

        await query.edit_message_text(
            f"🎮 *Account Blox Fruit*\n━━━━━━━━━━━━━━\n"
            f"📦 Account ទំនេរ: *{len(available)}* គណនី\n━━━━━━━━━━━━━━"
        )
        for acc_id, acc in available.items():
            keyboard = [[InlineKeyboardButton(
                f"✅ ទិញ — {acc['price']}", callback_data=f"buy_acc_{acc_id}"
            )]]
            try:
                await query.message.reply_photo(
                    photo=acc["photo_url"],
                    caption=(
                        f"🎮 *{acc['name']}*\n━━━━━━━━━━━━━━\n"
                        f"⭐ Level: {acc['level']}\n"
                        f"🍎 Fruits: {acc['fruits']}\n"
                        f"💰 Beli: {acc['beli']}\n"
                        f"💵 តម្លៃ: *{acc['price']}*\n━━━━━━━━━━━━━━"
                    ),
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
                    f"🎮 *{acc['name']}* — {acc['price']}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

        back = [[InlineKeyboardButton("🔙 ត្រឡប់ម៉ឺនុយ", callback_data="back_main")]]
        await query.message.reply_text("👆 Account ទាំងអស់ — ជ្រើសរើស!",
                                        reply_markup=InlineKeyboardMarkup(back))
        return CHOOSE_ACCOUNT

    # 📖 HOW TO BUY
    elif data == "how_to_buy":
        keyboard = [[InlineKeyboardButton("🔙 ត្រឡប់", callback_data="back_main")]]
        await query.edit_message_text(
            f"📖 *របៀបទិញ — {s['store_name']}*\n"
            f"━━━━━━━━━━━━━━\n\n"
            f"1️⃣ ជ្រើស Fruit / Service / Account\n\n"
            f"2️⃣ ជ្រើសអ្វីដែលចង់ទិញ\n\n"
            f"3️⃣ វាយ *Roblox Username* (Service/Carry)\n\n"
            f"4️⃣ Scan *QR Acleda* ហើយបង់ប្រាក់\n\n"
            f"5️⃣ Screenshot slip ហើយ *ផ្ញើមក bot* នេះ\n\n"
            f"6️⃣ រង់ចាំ Admin *Confirm* (5-15 នាទី)\n\n"
            f"7️⃣ ទទួលបាន Account / Service ✅\n\n"
            f"━━━━━━━━━━━━━━\n"
            f"📞 បញ្ហា? {s['admin_username']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHOOSE_CATEGORY

    # 🆘 SUPPORT
    elif data == "support":
        admin_url = f"https://t.me/{s['admin_username'].replace('@','')}"
        keyboard  = [
            [InlineKeyboardButton("💬 ទំនាក់ទំនង Support", url=admin_url)],
            [InlineKeyboardButton("🔙 ត្រឡប់", callback_data="back_main")],
        ]
        await query.edit_message_text(
            f"🆘 *Support — {s['store_name']}*\n"
            f"━━━━━━━━━━━━━━\n\n"
            f"🔹 *ទិញហើយ មិនទទួល?*\n→ ផ្ញើ Order ID ទៅ {s['admin_username']}\n\n"
            f"🔹 *Screenshot ផ្ញើហើយ មិន confirm?*\n→ រង់ចាំ 10-15 នាទី\n\n"
            f"🔹 *Account Login មិនបាន?*\n→ ទំនាក់ទំនង admin ភ្លាម\n\n"
            f"🔹 *ចង់ដឹងថ្លៃ Fruit ផ្សេង?*\n→ DM {s['admin_username']}\n\n"
            f"━━━━━━━━━━━━━━\n"
            f"⏰ ម៉ោង Support: *{s['support_hours']}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHOOSE_CATEGORY

    # 📞 CONTACT
    elif data == "contact":
        admin_url = f"https://t.me/{s['admin_username'].replace('@','')}"
        keyboard  = [
            [InlineKeyboardButton("💬 ជជែក", url=admin_url)],
            [InlineKeyboardButton("🔙 ត្រឡប់", callback_data="back_main")],
        ]
        await query.edit_message_text(
            f"📞 *{s['store_name']}*\n👤 {s['admin_username']}\n⏰ {s['support_hours']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHOOSE_CATEGORY

    elif data == "back_main":
        return await start(update, context)


# ────────────────────────────────────────────────
#   ACCOUNT BUY
# ────────────────────────────────────────────────
async def choose_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data

    if data == "back_main":
        return await start(update, context)

    if data.startswith("buy_acc_"):
        acc_id = data.replace("buy_acc_", "")
        store  = db.load()
        acc    = store["accounts"].get(acc_id)
        s      = store["settings"]

        if not acc or acc.get("sold"):
            await query.answer("❌ Account នេះលែងមាន!", show_alert=True)
            return CHOOSE_ACCOUNT

        user     = query.from_user
        order_id = f"ORD{user.id}{query.message.message_id}"
        context.user_data.update({
            "item": acc["name"], "price": acc["price"],
            "acc_id": acc_id, "category": "Account",
            "roblox": "N/A", "order_id": order_id
        })

        await query.message.reply_text(
            f"📋 *សង្ខេប Order*\n━━━━━━━━━━━━━━\n"
            f"🆔 `{order_id}`\n🎮 {acc['name']}\n⭐ {acc['level']}\n"
            f"🍎 {acc['fruits']}\n💵 *{acc['price']}*\n"
            f"━━━━━━━━━━━━━━\n💳 Scan QR Acleda ខាងក្រោម 👇\nបង់រួច ផ្ញើ screenshot 📸",
            parse_mode="Markdown"
        )
        if s.get("acleda_qr_url"):
            await query.message.reply_photo(
                photo=s["acleda_qr_url"],
                caption=f"💳 បង់ *{acc['price']}*\nយោង: `{order_id}`",
                parse_mode="Markdown"
            )

        store["pending_orders"][order_id] = {
            "customer_id":   user.id,
            "customer_name": user.username or user.first_name,
            "item": acc["name"], "price": acc["price"],
            "roblox": "N/A", "category": "Account", "acc_id": acc_id,
        }
        db.save(store)

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🔔 *Order Account ថ្មី!*\n🆔 `{order_id}`\n"
                 f"👤 @{user.username or user.first_name}\n"
                 f"🎮 {acc['name']} — {acc['price']}\n\n"
                 f"✅ /confirm {order_id}\n❌ /reject {order_id}",
            parse_mode="Markdown"
        )
        return WAITING_PAYMENT


# ────────────────────────────────────────────────
#   SERVICE SELECT
# ────────────────────────────────────────────────
async def choose_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data

    if data == "back_main":
        return await start(update, context)

    item_name = data.replace("item_", "")
    store     = db.load()
    price     = store["services"].get(item_name, "តម្លៃពិសេស")
    context.user_data.update({"item": item_name, "price": price})

    await query.edit_message_text(
        f"✅ *{item_name}*\n💵 {price}\n\nវាយ *Roblox Username* 👇",
        parse_mode="Markdown"
    )
    return ENTER_ROBLOX


# ────────────────────────────────────────────────
#   ROBLOX USERNAME
# ────────────────────────────────────────────────
async def enter_roblox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    roblox   = update.message.text
    user     = update.message.from_user
    item     = context.user_data["item"]
    price    = context.user_data["price"]
    order_id = f"ORD{user.id}{update.message.message_id}"
    context.user_data.update({"roblox": roblox, "category": "Service", "order_id": order_id})

    store = db.load()
    s     = store["settings"]

    store["pending_orders"][order_id] = {
        "customer_id":   user.id,
        "customer_name": user.username or user.first_name,
        "item": item, "price": price,
        "roblox": roblox, "category": "Service", "acc_id": None,
    }
    db.save(store)

    await update.message.reply_text(
        f"📋 *សង្ខេប Order*\n━━━━━━━━━━━━━━\n"
        f"🆔 `{order_id}`\n⚔️ {item}\n💵 {price}\n🎮 {roblox}\n"
        f"━━━━━━━━━━━━━━\n💳 Scan QR Acleda ខាងក្រោម 👇\nបង់រួច ផ្ញើ screenshot 📸",
        parse_mode="Markdown"
    )
    if s.get("acleda_qr_url"):
        await update.message.reply_photo(
            photo=s["acleda_qr_url"],
            caption=f"💳 បង់ *{price}*\nយោង: `{order_id}`",
            parse_mode="Markdown"
        )
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"🔔 *Order Service ថ្មី!*\n🆔 `{order_id}`\n"
             f"👤 @{user.username or user.first_name}\n"
             f"⚔️ {item} — {price}\n🎮 {roblox}\n\n"
             f"✅ /confirm {order_id}\n❌ /reject {order_id}",
        parse_mode="Markdown"
    )
    return WAITING_PAYMENT


# ────────────────────────────────────────────────
#   PAYMENT SCREENSHOT
# ────────────────────────────────────────────────
async def receive_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user     = update.message.from_user
    order_id = context.user_data.get("order_id", "N/A")
    store    = db.load()
    s        = store["settings"]

    await update.message.reply_text(
        f"✅ *ទទួលបាន Screenshot!*\n🆔 `{order_id}`\n"
        f"⏳ Admin កំពុងពិនិត្យ... (5-15 នាទី)\n"
        f"📞 បញ្ហា? {s['admin_username']}",
        parse_mode="Markdown"
    )
    order = store["pending_orders"].get(order_id, {})
    if update.message.photo:
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"💳 Screenshot\n🆔 `{order_id}`\n"
                    f"👤 @{user.username or user.first_name}\n"
                    f"🛒 {order.get('item','?')} — {order.get('price','?')}\n\n"
                    f"✅ /confirm {order_id}\n❌ /reject {order_id}",
            parse_mode="Markdown"
        )
    else:
        await update.message.forward(chat_id=ADMIN_CHAT_ID)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ លុបចោល។ /start ដើម្បីចាប់ផ្ដើម")
    return ConversationHandler.END


# ────────────────────────────────────────────────
#   MAIN
# ────────────────────────────────────────────────
def main():
    app = ApplicationBuilder().token(SHOP_BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_CATEGORY: [CallbackQueryHandler(choose_category)],
            CHOOSE_ITEM:     [CallbackQueryHandler(choose_item)],
            CHOOSE_ACCOUNT:  [CallbackQueryHandler(choose_account)],
            ENTER_ROBLOX:    [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_roblox)],
            WAITING_PAYMENT: [MessageHandler(filters.PHOTO | filters.TEXT, receive_payment)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    print("🛒 Uchiro Shop Bot កំពុងដំណើរការ...")
    app.run_polling()


if __name__ == "__main__":
    main()
