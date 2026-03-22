import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters, ConversationHandler
)

# ===================== CONFIG =====================
BOT_TOKEN = "8743632619:AAGoQBL5NaDn_UV71Ad2SXubKKjiDk_uqGE"         # ពី @BotFather
ADMIN_CHAT_ID = 6594079594                  # លេខ ID របស់អ្នក (ពី @userinfobot)
ABA_QR_IMAGE_URL = "https://ibb.co/dJQwhKrZ"  # បញ្ចូល link QR ABA
ADMIN_USERNAME = "@noreakyour"

# ===================== គណនី (ACCOUNTS) =====================
# បន្ថែម account Roblox របស់អ្នកនៅទីនេះ
# photo_url: upload រូបថត account ទៅ imgbb.com រួច paste link
# username/password: នឹងផ្ញើទៅអតិថិជន តែពេល /confirm ប៉ុណ្ណោះ
ACCOUNTS = {
    "ACC001": {
        "name": "🎮 គណនី #1 — Level អតិបរមា",
        "price": "$15",
        "level": "អតិបរមា (2450)",
        "fruits": "Leopard, Dragon",
        "photo_url": "https://your-account1-screenshot.com/img.jpg",  # ជំនួសដោយ link រូបភាពពិត
        "username": "RobloxUser1",        # ជំនួសដោយ username ពិត
        "password": "YourPassword1",      # ជំនួសដោយ password ពិត
        "sold": False,
    },
    "ACC002": {
        "name": "🎮 គណនី #2 — Level មធ្យម",
        "price": "$8",
        "level": "1500",
        "fruits": "Kitsune",
        "photo_url": "https://your-account2-screenshot.com/img.jpg",
        "username": "RobloxUser2",
        "password": "YourPassword2",
        "sold": False,
    },
    # ➕ បន្ថែម account ថ្មីៗនៅទីនេះ
}

# ===================== សេវាកម្ម (SERVICES) =====================
SERVICES = {
    "⚔️ Raid Carry (1 raid)": "$3",
    "👑 Boss Carry": "$2",
    "🏆 កញ្ចប់ Raid ពេញ (5 raids)": "$12",
    "🎯 Carry តាមការកំណត់ (សួរ admin)": "តម្លៃពិសេស",
}

# ===================== STATES =====================
CHOOSE_CATEGORY, CHOOSE_ITEM, CHOOSE_ACCOUNT, ENTER_ROBLOX, WAITING_PAYMENT = range(5)

# ===================== រក្សាទុក order =====================
pending_orders = {}

# ===================== LOGGING =====================
logging.basicConfig(level=logging.INFO)


# ===================== /START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🍎 ទិញ Fruit", callback_data="cat_fruits")],
        [InlineKeyboardButton("⚔️ សេវា Carry / Raid", callback_data="cat_services")],
        [InlineKeyboardButton("🎮 ទិញ គណនី Roblox", callback_data="cat_accounts")],
        [InlineKeyboardButton("📦 ពិនិត្យ Order របស់ខ្ញុំ", callback_data="order_status")],
        [InlineKeyboardButton("📞 ទំនាក់ទំនង Admin", callback_data="contact")],
    ]
    await update.message.reply_text(
        "👋 សូមស្វាគមន៍មក *BloxFruits KH Shop* 🍎🇰🇭\n\n"
        "យើងលក់ Fruits, គណនី និងសេវា Carry!\n"
        "⚡ ផ្ញើរហ័ស | ✅ គួរជឿទុកចិត្ត | 💳 បង់ ABA\n\n"
        "សូមជ្រើសរើស៖",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSE_CATEGORY


# ===================== ជ្រើសរើសប្រភេទ =====================
async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # 🍎 FRUITS — redirect ទៅ admin
    if data == "cat_fruits":
        keyboard = [
            [InlineKeyboardButton("💬 ចាប់ផ្ដើមជជែកជាមួយ Admin", url="https://t.me/noreakyour")],
            [InlineKeyboardButton("🔙 ត្រឡប់ក្រោយ", callback_data="back_start")]
        ]
        await query.edit_message_text(
            "🍎 *ទិញ Fruit*\n\n"
            "សម្រាប់ការទិញ Fruit សូមទំនាក់ទំនង admin ដោយផ្ទាល់៖\n\n"
            f"👉 {ADMIN_USERNAME}\n\n"
            "ប្រាប់ admin ថា Fruit អ្វីដែលអ្នកចង់បាន!\n"
            "⚡ ឆ្លើយតបរហ័ស | ✅ គួរជឿទុកចិត្ត",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHOOSE_CATEGORY

    # ⚔️ SERVICES
    elif data == "cat_services":
        context.user_data["category"] = "Service"
        keyboard = [
            [InlineKeyboardButton(f"{item} — {price}", callback_data=f"item_{item}")]
            for item, price in SERVICES.items()
        ]
        keyboard.append([InlineKeyboardButton("🔙 ត្រឡប់ក្រោយ", callback_data="back_start")])
        await query.edit_message_text(
            "⚔️ *ជ្រើសរើសសេវាកម្ម៖*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHOOSE_ITEM

    # 🎮 ACCOUNTS
    elif data == "cat_accounts":
        context.user_data["category"] = "Account"
        available = {k: v for k, v in ACCOUNTS.items() if not v["sold"]}
        if not available:
            keyboard = [[InlineKeyboardButton("🔙 ត្រឡប់ក្រោយ", callback_data="back_start")]]
            await query.edit_message_text(
                "😔 *គ្មាន Account ទំនេរពេលនេះទេ។*\n\nសូមត្រឡប់មកក្រោយ ឬទំនាក់ទំនង admin។",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return CHOOSE_CATEGORY

        keyboard = [
            [InlineKeyboardButton(f"{v['name']} — {v['price']}", callback_data=f"acc_{k}")]
            for k, v in available.items()
        ]
        keyboard.append([InlineKeyboardButton("🔙 ត្រឡប់ក្រោយ", callback_data="back_start")])
        await query.edit_message_text(
            "🎮 *គណនី Roblox ដែលអាចទិញបាន៖*\n"
            "ចុចលើ account ណាមួយ ដើម្បីមើលរូបភាព និងព័ត៌មានលម្អិត 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHOOSE_ACCOUNT

    elif data == "contact":
        keyboard = [[InlineKeyboardButton("💬 ជជែកជាមួយ Admin", url="https://t.me/noreakyour")]]
        await query.edit_message_text(
            f"📞 ទំនាក់ទំនង admin: {ADMIN_USERNAME}\n\nយើងនឹងឆ្លើយតបឱ្យបានឆាប់! ⚡",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    elif data == "order_status":
        await query.edit_message_text(
            f"📦 ដើម្បីពិនិត្យ order សូមទំនាក់ទំនង admin:\n{ADMIN_USERNAME}\n\nផ្ញើ *Order ID* របស់អ្នក។ ✅",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    elif data == "back_start":
        return await restart(update, context)


# ===================== ជ្រើសរើស Account =====================
async def choose_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_start":
        return await restart(update, context)

    if data.startswith("acc_"):
        acc_id = data.replace("acc_", "")
        acc = ACCOUNTS.get(acc_id)

        if not acc or acc["sold"]:
            await query.edit_message_text("❌ Account នេះលែងមានទំនេរហើយ។")
            return CHOOSE_CATEGORY

        context.user_data["item"] = acc["name"]
        context.user_data["price"] = acc["price"]
        context.user_data["acc_id"] = acc_id

        keyboard = [
            [InlineKeyboardButton("✅ ទិញ Account នេះ", callback_data=f"buy_acc_{acc_id}")],
            [InlineKeyboardButton("🔙 ត្រឡប់ទៅបញ្ជី Account", callback_data="cat_accounts")],
        ]
        await query.message.reply_photo(
            photo=acc["photo_url"],
            caption=(
                f"🎮 *{acc['name']}*\n"
                f"━━━━━━━━━━━━━━\n"
                f"⭐ Level: {acc['level']}\n"
                f"🍎 Fruits: {acc['fruits']}\n"
                f"💰 តម្លៃ: {acc['price']}\n"
                f"━━━━━━━━━━━━━━\n\n"
                f"ចុច *ទិញ Account នេះ* ដើម្បីបញ្ជាទិញ! 👇"
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.delete_message()
        return CHOOSE_ACCOUNT

    if data.startswith("buy_acc_"):
        acc_id = data.replace("buy_acc_", "")
        acc = ACCOUNTS.get(acc_id)

        context.user_data["item"] = acc["name"]
        context.user_data["price"] = acc["price"]
        context.user_data["acc_id"] = acc_id
        context.user_data["category"] = "Account"
        context.user_data["roblox"] = "គ្មាន (ទិញ Account)"

        user = query.from_user
        order_id = f"ORD{user.id}{query.message.message_id}"
        context.user_data["order_id"] = order_id

        await query.message.reply_text(
            f"📋 *សង្ខេប Order*\n"
            f"━━━━━━━━━━━━━━\n"
            f"🆔 Order ID: `{order_id}`\n"
            f"🎮 Account: {acc['name']}\n"
            f"⭐ Level: {acc['level']}\n"
            f"🍎 Fruits: {acc['fruits']}\n"
            f"💰 តម្លៃ: {acc['price']}\n"
            f"━━━━━━━━━━━━━━\n\n"
            f"💳 សូមបង់ប្រាក់តាម *ABA QR* ខាងក្រោម។\n"
            f"បន្ទាប់ពីបង់រួច សូម *ផ្ញើ screenshot* មកវិញ។ 📸",
            parse_mode="Markdown"
        )
        await query.message.reply_photo(
            photo=ABA_QR_IMAGE_URL,
            caption=f"Scan QR ដើម្បីបង់ *{acc['price']}*\nយោង: `{order_id}`",
            parse_mode="Markdown"
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🔔 *Order Account ថ្មី!*\n"
                 f"━━━━━━━━━━━━━━\n"
                 f"🆔 Order ID: `{order_id}`\n"
                 f"👤 អតិថិជន: @{user.username or user.first_name}\n"
                 f"🎮 Account: {acc['name']}\n"
                 f"💰 តម្លៃ: {acc['price']}\n"
                 f"━━━━━━━━━━━━━━\n"
                 f"⏳ រង់ចាំ screenshot ការបង់ប្រាក់...",
            parse_mode="Markdown"
        )
        return WAITING_PAYMENT


# ===================== ជ្រើសរើសសេវា =====================
async def choose_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_start":
        return await restart(update, context)

    item_name = data.replace("item_", "")
    context.user_data["item"] = item_name
    price = SERVICES.get(item_name, "តម្លៃពិសេស")
    context.user_data["price"] = price

    await query.edit_message_text(
        f"✅ អ្នកបានជ្រើស: *{item_name}*\n"
        f"💰 តម្លៃ: *{price}*\n\n"
        f"សូមវាយ *ឈ្មោះ Roblox* របស់អ្នក ដើម្បីបន្ត:",
        parse_mode="Markdown"
    )
    return ENTER_ROBLOX


# ===================== វាយ Roblox Username =====================
async def enter_roblox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    roblox_username = update.message.text
    context.user_data["roblox"] = roblox_username
    context.user_data["category"] = "Service"

    item = context.user_data["item"]
    price = context.user_data["price"]
    user = update.message.from_user

    order_id = f"ORD{user.id}{update.message.message_id}"
    context.user_data["order_id"] = order_id

    await update.message.reply_text(
        f"📋 *សង្ខេប Order*\n"
        f"━━━━━━━━━━━━━━\n"
        f"🆔 Order ID: `{order_id}`\n"
        f"🛒 សេវា: {item}\n"
        f"💰 តម្លៃ: {price}\n"
        f"🎮 Roblox: {roblox_username}\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"💳 សូមបង់ប្រាក់តាម *ABA QR* ខាងក្រោម។\n"
        f"បន្ទាប់ពីបង់រួច សូម *ផ្ញើ screenshot* មកវិញ។ 📸",
        parse_mode="Markdown"
    )
    await update.message.reply_photo(
        photo=ABA_QR_IMAGE_URL,
        caption=f"Scan QR ដើម្បីបង់ *{price}*\nយោង: `{order_id}`",
        parse_mode="Markdown"
    )
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"🔔 *Order សេវា ថ្មី!*\n"
             f"━━━━━━━━━━━━━━\n"
             f"🆔 Order ID: `{order_id}`\n"
             f"👤 អតិថិជន: @{user.username or user.first_name}\n"
             f"🛒 សេវា: {item}\n"
             f"💰 តម្លៃ: {price}\n"
             f"🎮 Roblox: {roblox_username}\n"
             f"━━━━━━━━━━━━━━\n"
             f"⏳ រង់ចាំ screenshot ការបង់ប្រាក់...",
        parse_mode="Markdown"
    )
    return WAITING_PAYMENT


# ===================== ទទួល Screenshot =====================
async def receive_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    order_id = context.user_data.get("order_id", "N/A")
    item = context.user_data.get("item", "N/A")
    roblox = context.user_data.get("roblox", "N/A")
    price = context.user_data.get("price", "N/A")
    category = context.user_data.get("category", "Service")
    acc_id = context.user_data.get("acc_id", None)

    pending_orders[order_id] = {
        "customer_id": user.id,
        "customer_name": user.username or user.first_name,
        "item": item,
        "price": price,
        "roblox": roblox,
        "category": category,
        "acc_id": acc_id,
    }

    await update.message.reply_text(
        f"✅ *ទទួលបាន screenshot ហើយ!*\n\n"
        f"🆔 Order ID: `{order_id}`\n"
        f"⏳ Admin កំពុងពិនិត្យការបង់ប្រាក់...\n"
        f"⚡ អ្នកនឹងទទួលបាន order របស់អ្នកឆាប់ៗ!\n\n"
        f"បើមិនទទួលបានក្នុង 10 នាទី សូមទំនាក់ទំនង: {ADMIN_USERNAME}",
        parse_mode="Markdown"
    )

    if update.message.photo:
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"💳 *Screenshot ការបង់ប្រាក់*\n"
                    f"🆔 Order: `{order_id}`\n"
                    f"👤 @{user.username or user.first_name}\n"
                    f"🛒 {item} — {price}\n"
                    f"📦 ប្រភេទ: {category}\n"
                    f"🎮 Roblox: {roblox}\n\n"
                    f"✅ /confirm {order_id}\n"
                    f"❌ /reject {order_id}",
            parse_mode="Markdown"
        )
    else:
        await update.message.forward(chat_id=ADMIN_CHAT_ID)

    return ConversationHandler.END


# ===================== ADMIN: /confirm =====================
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ អ្នកគ្មានសិទ្ធិប្រើពាក្យបញ្ជានេះទេ។")
        return

    if not context.args:
        await update.message.reply_text("❓ របៀបប្រើ: `/confirm ORDER_ID`", parse_mode="Markdown")
        return

    order_id = context.args[0]
    order = pending_orders.get(order_id)

    if not order:
        await update.message.reply_text(
            f"⚠️ Order `{order_id}` រកមិនឃើញ។ សូមប្រើ /orders ។",
            parse_mode="Markdown"
        )
        return

    # 🎮 ACCOUNT ORDER — ផ្ញើ credentials ដោយស្វ័យប្រវត្តិ
    if order.get("category") == "Account" and order.get("acc_id"):
        acc = ACCOUNTS.get(order["acc_id"])
        if acc:
            ACCOUNTS[order["acc_id"]]["sold"] = True
            await context.bot.send_message(
                chat_id=order["customer_id"],
                text=f"🎉 *បញ្ជាក់ការបង់ប្រាក់រួចហើយ!*\n"
                     f"━━━━━━━━━━━━━━\n"
                     f"🆔 Order ID: `{order_id}`\n"
                     f"🎮 Account: {acc['name']}\n"
                     f"💰 តម្លៃ: {acc['price']}\n"
                     f"━━━━━━━━━━━━━━\n\n"
                     f"🔐 *ព័ត៌មានចូលគណនីរបស់អ្នក:*\n"
                     f"👤 Username: `{acc['username']}`\n"
                     f"🔑 Password: `{acc['password']}`\n\n"
                     f"⚠️ សូម *ប្តូរ password ភ្លាមៗ* បន្ទាប់ពី login!\n\n"
                     f"អរគុណសម្រាប់ការទិញពី *BloxFruits KH Shop* 🍎🇰🇭",
                parse_mode="Markdown"
            )
    else:
        # ⚔️ SERVICE ORDER
        await context.bot.send_message(
            chat_id=order["customer_id"],
            text=f"🎉 *បញ្ជាក់ការបង់ប្រាក់រួចហើយ!*\n"
                 f"━━━━━━━━━━━━━━\n"
                 f"🆔 Order ID: `{order_id}`\n"
                 f"🛒 សេវា: {order['item']}\n"
                 f"🎮 Roblox: {order['roblox']}\n"
                 f"━━━━━━━━━━━━━━\n\n"
                 f"⚡ សូម *online នៅ Roblox* ឥឡូវនេះ!\n"
                 f"Admin នឹងចូលជួបអ្នកឆាប់ៗ។ ✅\n\n"
                 f"អរគុណសម្រាប់ការទិញពី *BloxFruits KH Shop* 🍎🇰🇭",
            parse_mode="Markdown"
        )

    await update.message.reply_text(
        f"✅ Order `{order_id}` បានបញ្ជាក់!\n👤 @{order['customer_name']} ទទួលបានការជូនដំណឹងហើយ។ 🔔",
        parse_mode="Markdown"
    )
    del pending_orders[order_id]


# ===================== ADMIN: /reject =====================
async def reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ អ្នកគ្មានសិទ្ធិប្រើពាក្យបញ្ជានេះទេ។")
        return

    if not context.args:
        await update.message.reply_text("❓ របៀបប្រើ: `/reject ORDER_ID`", parse_mode="Markdown")
        return

    order_id = context.args[0]
    order = pending_orders.get(order_id)

    if not order:
        await update.message.reply_text(f"⚠️ Order `{order_id}` រកមិនឃើញ។", parse_mode="Markdown")
        return

    await context.bot.send_message(
        chat_id=order["customer_id"],
        text=f"❌ *ពិនិត្យការបង់ប្រាក់មិនឃើញ*\n"
             f"━━━━━━━━━━━━━━\n"
             f"🆔 Order ID: `{order_id}`\n"
             f"━━━━━━━━━━━━━━\n\n"
             f"យើងមិនអាចបញ្ជាក់ការបង់ប្រាក់របស់អ្នកបានទេ។ សូម:\n"
             f"1. ផ្ញើ screenshot ច្បាស់ជាងនេះ 📸\n"
             f"2. ឬទំនាក់ទំនង admin: {ADMIN_USERNAME}\n\n"
             f"សូមអភ័យទោសសម្រាប់ការរអាក់រអួល! 🙏",
        parse_mode="Markdown"
    )
    await update.message.reply_text(
        f"❌ Order `{order_id}` ត្រូវបានបដិសេធ។ @{order['customer_name']} ទទួលបានការជូនដំណឹងហើយ។",
        parse_mode="Markdown"
    )
    del pending_orders[order_id]


# ===================== ADMIN: /orders =====================
async def list_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ អ្នកគ្មានសិទ្ធិប្រើពាក្យបញ្ជានេះទេ។")
        return

    if not pending_orders:
        await update.message.reply_text("📭 គ្មាន order កំពុងរង់ចាំនៅពេលនេះទេ។")
        return

    msg = "📋 *Order កំពុងរង់ចាំ:*\n━━━━━━━━━━━━━━\n"
    for oid, o in pending_orders.items():
        msg += (
            f"🆔 `{oid}`\n"
            f"👤 @{o['customer_name']}\n"
            f"🛒 {o['item']} — {o['price']}\n"
            f"📦 ប្រភេទ: {o['category']}\n"
            f"✅ /confirm {oid}  ❌ /reject {oid}\n"
            f"━━━━━━━━━━━━━━\n"
        )
    await update.message.reply_text(msg, parse_mode="Markdown")


# ===================== RESTART =====================
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🍎 ទិញ Fruit", callback_data="cat_fruits")],
        [InlineKeyboardButton("⚔️ សេវា Carry / Raid", callback_data="cat_services")],
        [InlineKeyboardButton("🎮 ទិញ គណនី Roblox", callback_data="cat_accounts")],
        [InlineKeyboardButton("📦 ពិនិត្យ Order របស់ខ្ញុំ", callback_data="order_status")],
        [InlineKeyboardButton("📞 ទំនាក់ទំនង Admin", callback_data="contact")],
    ]
    query = update.callback_query
    await query.edit_message_text(
        "👋 សូមស្វាគមន៍មក *BloxFruits KH Shop* 🍎🇰🇭\n\nសូមជ្រើសរើស៖",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSE_CATEGORY


# ===================== CANCEL =====================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Order ត្រូវបានលុបចោល។ វាយ /start ដើម្បីចាប់ផ្ដើមឡើងវិញ។")
    return ConversationHandler.END


# ===================== MAIN =====================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_CATEGORY: [CallbackQueryHandler(choose_category)],
            CHOOSE_ITEM: [CallbackQueryHandler(choose_item)],
            CHOOSE_ACCOUNT: [CallbackQueryHandler(choose_account)],
            ENTER_ROBLOX: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_roblox)],
            WAITING_PAYMENT: [MessageHandler(filters.PHOTO | filters.TEXT, receive_payment)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("confirm", confirm_order))
    app.add_handler(CommandHandler("reject", reject_order))
    app.add_handler(CommandHandler("orders", list_orders))
    print("🤖 BloxFruits KH Bot កំពុងដំណើរការ...")
    app.run_polling()


if __name__ == "__main__":
    main()
