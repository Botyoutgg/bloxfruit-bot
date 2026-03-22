"""
====================================================
   UCHIRO STORE — Admin Bot (admin_bot.py)
   Bot សម្រាប់ Owner គ្រប់គ្រងទាំងអស់
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

# ─── CONFIG ───
ADMIN_BOT_TOKEN = os.environ.get("ADMIN_BOT_TOKEN", "8700119551:AAFCeKRMT5knEXrchNboTWTlA1VNmBMFHrY")
ADMIN_CHAT_ID   = int(os.environ.get("ADMIN_CHAT_ID", "6594079594"))

logging.basicConfig(level=logging.INFO)

# ─── STATES ───
(
    ADMIN_MENU,
    WAIT_STORE_NAME, WAIT_ADMIN_USER, WAIT_SUPPORT_HOURS,
    WAIT_ACLEDA_QR, WAIT_FRUIT_LIST_PHOTO,
    WAIT_SERVICE_PHOTO,
    WAIT_FRUIT_NAME, WAIT_FRUIT_PRICE,
    WAIT_SERVICE_NAME, WAIT_SERVICE_PRICE,
    WAIT_ACC_NAME, WAIT_ACC_PRICE, WAIT_ACC_LEVEL,
    WAIT_ACC_FRUITS, WAIT_ACC_BELI, WAIT_ACC_PHOTO,
    WAIT_ACC_USERNAME, WAIT_ACC_PASSWORD,
    WAIT_DEL_FRUIT, WAIT_DEL_SERVICE, WAIT_DEL_ACC,
) = range(22)


# ────────────────────────────────────────────────
#   ពិនិត្យ Admin
# ────────────────────────────────────────────────
def is_admin(update: Update):
    uid = update.message.from_user.id if update.message else update.callback_query.from_user.id
    return uid == ADMIN_CHAT_ID


# ────────────────────────────────────────────────
#   MAIN MENU
# ────────────────────────────────────────────────
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ អ្នកមិនមែន Owner ទេ!")
        return ConversationHandler.END

    data = db.load()
    s    = data["settings"]
    keyboard = [
        [InlineKeyboardButton("⚙️ កំណត់ Store",          callback_data="menu_settings")],
        [InlineKeyboardButton("🍎 គ្រប់គ្រង Fruit",       callback_data="menu_fruits")],
        [InlineKeyboardButton("⚔️ គ្រប់គ្រង Service",     callback_data="menu_services")],
        [InlineKeyboardButton("🎮 គ្រប់គ្រង Account",     callback_data="menu_accounts")],
        [InlineKeyboardButton("📋 Order ទាំងអស់",         callback_data="menu_orders")],
        [InlineKeyboardButton("📦 ពិនិត្យ Stock",         callback_data="menu_stock")],
    ]
    msg = (
        f"🛠 *Admin Panel — {s['store_name']}*\n"
        f"━━━━━━━━━━━━━━\n"
        f"👤 Admin: {s['admin_username']}\n"
        f"📦 Account Stock: {len([a for a in data['accounts'].values() if not a.get('sold')])}\n"
        f"📋 Order រង់ចាំ: {len(data['pending_orders'])}\n"
        f"━━━━━━━━━━━━━━\n"
        f"សូមជ្រើសរើស 👇"
    )
    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown",
                                        reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(msg, parse_mode="Markdown",
                                                       reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_MENU


# ────────────────────────────────────────────────
#   SETTINGS MENU
# ────────────────────────────────────────────────
async def menu_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("✏️ ប្តូរ ឈ្មោះ Store",      callback_data="set_storename")],
        [InlineKeyboardButton("✏️ ប្តូរ Admin Username",   callback_data="set_adminuser")],
        [InlineKeyboardButton("⏰ ប្តូរ ម៉ោង Support",     callback_data="set_hours")],
        [InlineKeyboardButton("💳 Upload QR Acleda",       callback_data="set_acleda_qr")],
        [InlineKeyboardButton("🍎 Upload រូប Fruit List",  callback_data="set_fruit_photo")],
        [InlineKeyboardButton("📸 Upload រូប Service",     callback_data="set_service_photos")],
        [InlineKeyboardButton("🔙 ត្រឡប់",                 callback_data="back_main")],
    ]
    await query.edit_message_text(
        "⚙️ *កំណត់ Store*\nសូមជ្រើស 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ADMIN_MENU


# ─── Store Name ───
async def set_storename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("✏️ វាយ *ឈ្មោះ Store* ថ្មី:", parse_mode="Markdown")
    return WAIT_STORE_NAME

async def save_storename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = db.load()
    data["settings"]["store_name"] = update.message.text
    db.save(data)
    await update.message.reply_text(f"✅ ឈ្មោះ Store បានប្តូរទៅ: *{update.message.text}*", parse_mode="Markdown")
    return await admin_start(update, context)

# ─── Admin Username ───
async def set_adminuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("✏️ វាយ *Admin Username* ថ្មី (ឧ: @noreakyout):", parse_mode="Markdown")
    return WAIT_ADMIN_USER

async def save_adminuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = db.load()
    data["settings"]["admin_username"] = update.message.text
    db.save(data)
    await update.message.reply_text(f"✅ Admin Username: *{update.message.text}*", parse_mode="Markdown")
    return await admin_start(update, context)

# ─── Support Hours ───
async def set_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("⏰ វាយ *ម៉ោង Support* (ឧ: 8:00 - 22:00):", parse_mode="Markdown")
    return WAIT_SUPPORT_HOURS

async def save_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = db.load()
    data["settings"]["support_hours"] = update.message.text
    db.save(data)
    await update.message.reply_text(f"✅ ម៉ោង Support: *{update.message.text}*", parse_mode="Markdown")
    return await admin_start(update, context)

# ─── Acleda QR Upload ───
async def set_acleda_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "💳 សូម *Upload រូប QR Acleda* របស់អ្នក 👇\n\n(ផ្ញើ រូបភាព មក bot នេះ)",
        parse_mode="Markdown"
    )
    return WAIT_ACLEDA_QR

async def save_acleda_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("⚠️ សូម Upload រូបភាព QR!")
        return WAIT_ACLEDA_QR
    file_id = update.message.photo[-1].file_id
    data = db.load()
    data["settings"]["acleda_qr_url"] = file_id
    db.save(data)
    await update.message.reply_text("✅ QR Acleda បានfrugal Upload រួចហើយ! Bot Shop នឹងប្រើ QR ថ្មីនេះភ្លាម ✅")
    return await admin_start(update, context)

# ─── Fruit List Photo ───
async def set_fruit_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "🍎 សូម *Upload រូប Fruit List* 👇\n\n(ផ្ញើ រូបភាព មក bot នេះ)",
        parse_mode="Markdown"
    )
    return WAIT_FRUIT_LIST_PHOTO

async def save_fruit_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("⚠️ សូម Upload រូបភាព!")
        return WAIT_FRUIT_LIST_PHOTO
    file_id = update.message.photo[-1].file_id
    data = db.load()
    data["settings"]["fruit_list_photo"] = file_id
    db.save(data)
    await update.message.reply_text("✅ រូប Fruit List បាន Upload រួចហើយ! ✅")
    return await admin_start(update, context)

# ─── Service Photos ───
async def set_service_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    context.user_data["service_photos_temp"] = []
    await update.callback_query.edit_message_text(
        "📸 សូម Upload *រូប Service* (អាច Upload ច្រើនរូប)\n\n"
        "Upload រូបម្ដងៗ បន្ទាប់មក វាយ /done ពេល Upload ចប់",
        parse_mode="Markdown"
    )
    return WAIT_SERVICE_PHOTO

async def collect_service_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        context.user_data.setdefault("service_photos_temp", []).append(file_id)
        count = len(context.user_data["service_photos_temp"])
        await update.message.reply_text(f"✅ បាន Upload រូប {count} ។ Upload រូបទៀត ឬ វាយ /done ពេលចប់")
    return WAIT_SERVICE_PHOTO

async def done_service_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos = context.user_data.get("service_photos_temp", [])
    if not photos:
        await update.message.reply_text("⚠️ មិនទាន់ Upload រូបណាទេ!")
        return WAIT_SERVICE_PHOTO
    data = db.load()
    data["settings"]["service_photos"] = photos
    db.save(data)
    await update.message.reply_text(f"✅ បាន Upload រូប Service ចំនួន *{len(photos)}* រូប! ✅", parse_mode="Markdown")
    return await admin_start(update, context)


# ────────────────────────────────────────────────
#   FRUIT MANAGEMENT
# ────────────────────────────────────────────────
async def menu_fruits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data   = db.load()
    fruits = data["fruits"]

    fruit_list = "\n".join([f"• {k} — {v}" for k, v in fruits.items()]) or "គ្មាន"
    keyboard = [
        [InlineKeyboardButton("➕ បន្ថែម Fruit",   callback_data="fruit_add")],
        [InlineKeyboardButton("🗑 លុប Fruit",       callback_data="fruit_del")],
        [InlineKeyboardButton("🔙 ត្រឡប់",          callback_data="back_main")],
    ]
    await query.edit_message_text(
        f"🍎 *បញ្ជី Fruit*\n━━━━━━━━━━━━━━\n{fruit_list}\n━━━━━━━━━━━━━━",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ADMIN_MENU

async def fruit_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("🍎 វាយ *ឈ្មោះ Fruit* ថ្មី (ឧ: 🌟 Saber):", parse_mode="Markdown")
    return WAIT_FRUIT_NAME

async def save_fruit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_fruit_name"] = update.message.text
    await update.message.reply_text(f"💰 វាយ *តម្លៃ* សម្រាប់ {update.message.text} (ឧ: $20):", parse_mode="Markdown")
    return WAIT_FRUIT_PRICE

async def save_fruit_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name  = context.user_data["new_fruit_name"]
    price = update.message.text
    data  = db.load()
    data["fruits"][name] = price
    db.save(data)
    await update.message.reply_text(f"✅ បានបន្ថែម: *{name} — {price}* ✅", parse_mode="Markdown")
    return await admin_start(update, context)

async def fruit_del(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data   = db.load()
    fruits = data["fruits"]
    if not fruits:
        await update.callback_query.edit_message_text("📭 គ្មាន Fruit ទេ។")
        return ADMIN_MENU
    keyboard = [[InlineKeyboardButton(f"🗑 {k}", callback_data=f"delfruit_{k}")] for k in fruits]
    keyboard.append([InlineKeyboardButton("🔙 ត្រឡប់", callback_data="back_main")])
    await update.callback_query.edit_message_text(
        "🗑 *ជ្រើស Fruit ដែលចង់លុប:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAIT_DEL_FRUIT

async def confirm_del_fruit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    name  = query.data.replace("delfruit_", "")
    data  = db.load()
    data["fruits"].pop(name, None)
    db.save(data)
    await query.edit_message_text(f"✅ បានលុប Fruit: *{name}* ✅", parse_mode="Markdown")
    return await admin_start(update, context)


# ────────────────────────────────────────────────
#   SERVICE MANAGEMENT
# ────────────────────────────────────────────────
async def menu_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query    = update.callback_query
    await query.answer()
    data     = db.load()
    services = data["services"]
    svc_list = "\n".join([f"• {k} — {v}" for k, v in services.items()]) or "គ្មាន"
    keyboard = [
        [InlineKeyboardButton("➕ បន្ថែម Service",  callback_data="svc_add")],
        [InlineKeyboardButton("🗑 លុប Service",      callback_data="svc_del")],
        [InlineKeyboardButton("🔙 ត្រឡប់",           callback_data="back_main")],
    ]
    await query.edit_message_text(
        f"⚔️ *បញ្ជី Service*\n━━━━━━━━━━━━━━\n{svc_list}\n━━━━━━━━━━━━━━",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ADMIN_MENU

async def svc_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("⚔️ វាយ *ឈ្មោះ Service* ថ្មី:", parse_mode="Markdown")
    return WAIT_SERVICE_NAME

async def save_svc_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_svc_name"] = update.message.text
    await update.message.reply_text(f"💰 វាយ *តម្លៃ* (ឧ: $5):", parse_mode="Markdown")
    return WAIT_SERVICE_PRICE

async def save_svc_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name  = context.user_data["new_svc_name"]
    price = update.message.text
    data  = db.load()
    data["services"][name] = price
    db.save(data)
    await update.message.reply_text(f"✅ បានបន្ថែម: *{name} — {price}* ✅", parse_mode="Markdown")
    return await admin_start(update, context)

async def svc_del(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data     = db.load()
    services = data["services"]
    if not services:
        await update.callback_query.edit_message_text("📭 គ្មាន Service ទេ។")
        return ADMIN_MENU
    keyboard = [[InlineKeyboardButton(f"🗑 {k}", callback_data=f"delsvc_{k}")] for k in services]
    keyboard.append([InlineKeyboardButton("🔙 ត្រឡប់", callback_data="back_main")])
    await update.callback_query.edit_message_text(
        "🗑 *ជ្រើស Service ដែលចង់លុប:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAIT_DEL_SERVICE

async def confirm_del_svc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    name  = query.data.replace("delsvc_", "")
    data  = db.load()
    data["services"].pop(name, None)
    db.save(data)
    await query.edit_message_text(f"✅ បានលុប Service: *{name}* ✅", parse_mode="Markdown")
    return await admin_start(update, context)


# ────────────────────────────────────────────────
#   ACCOUNT MANAGEMENT
# ────────────────────────────────────────────────
async def menu_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = db.load()
    accs  = data["accounts"]

    available = {k: v for k, v in accs.items() if not v.get("sold")}
    sold      = {k: v for k, v in accs.items() if v.get("sold")}

    acc_text = ""
    if available:
        acc_text += "✅ *នៅ Stock:*\n"
        for k, v in available.items():
            acc_text += f"• `{k}` — {v['name']} ({v['price']})\n"
    if sold:
        acc_text += "\n❌ *លក់ហើយ:*\n"
        for k, v in sold.items():
            acc_text += f"• `{k}` — {v['name']}\n"
    if not acc_text:
        acc_text = "គ្មាន Account ទេ"

    keyboard = [
        [InlineKeyboardButton("➕ បន្ថែម Account ថ្មី",  callback_data="acc_add")],
        [InlineKeyboardButton("🗑 លុប Account",           callback_data="acc_del")],
        [InlineKeyboardButton("🔙 ត្រឡប់",                callback_data="back_main")],
    ]
    await query.edit_message_text(
        f"🎮 *Account ទាំងអស់*\n━━━━━━━━━━━━━━\n{acc_text}\n━━━━━━━━━━━━━━",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ADMIN_MENU

async def acc_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    context.user_data["new_acc"] = {}
    await update.callback_query.edit_message_text("🎮 វាយ *ឈ្មោះ Account* (ឧ: Account #3 Max Level):", parse_mode="Markdown")
    return WAIT_ACC_NAME

async def save_acc_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_acc"]["name"] = update.message.text
    await update.message.reply_text("💵 វាយ *តម្លៃ* (ឧ: $15):", parse_mode="Markdown")
    return WAIT_ACC_PRICE

async def save_acc_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_acc"]["price"] = update.message.text
    await update.message.reply_text("⭐ វាយ *Level* (ឧ: Max 2450):", parse_mode="Markdown")
    return WAIT_ACC_LEVEL

async def save_acc_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_acc"]["level"] = update.message.text
    await update.message.reply_text("🍎 វាយ *Fruits* (ឧ: Leopard, Dragon):", parse_mode="Markdown")
    return WAIT_ACC_FRUITS

async def save_acc_fruits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_acc"]["fruits"] = update.message.text
    await update.message.reply_text("💰 វាយ *Beli* (ឧ: 500M):", parse_mode="Markdown")
    return WAIT_ACC_BELI

async def save_acc_beli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_acc"]["beli"] = update.message.text
    await update.message.reply_text("📸 *Upload រូបភាព Account* (Screenshot account):", parse_mode="Markdown")
    return WAIT_ACC_PHOTO

async def save_acc_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("⚠️ សូម Upload រូបភាព!")
        return WAIT_ACC_PHOTO
    context.user_data["new_acc"]["photo_url"] = update.message.photo[-1].file_id
    await update.message.reply_text("👤 វាយ *Roblox Username*:", parse_mode="Markdown")
    return WAIT_ACC_USERNAME

async def save_acc_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_acc"]["username"] = update.message.text
    await update.message.reply_text("🔑 វាយ *Password*:", parse_mode="Markdown")
    return WAIT_ACC_PASSWORD

async def save_acc_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    acc  = context.user_data["new_acc"]
    acc["password"] = update.message.text
    acc["sold"]     = False

    data    = db.load()
    counter = data.get("acc_counter", 1)
    acc_id  = f"ACC{counter:03d}"
    data["accounts"][acc_id] = acc
    data["acc_counter"]      = counter + 1
    db.save(data)

    await update.message.reply_text(
        f"✅ *Account បានបន្ថែមជោគជ័យ!*\n\n"
        f"🆔 ID: `{acc_id}`\n"
        f"🎮 ឈ្មោះ: {acc['name']}\n"
        f"💵 តម្លៃ: {acc['price']}\n"
        f"⭐ Level: {acc['level']}\n"
        f"🍎 Fruits: {acc['fruits']}\n\n"
        f"Account នឹងបង្ហាញក្នុង Shop Bot ភ្លាម! ✅",
        parse_mode="Markdown"
    )
    return await admin_start(update, context)

async def acc_del(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = db.load()
    accs = data["accounts"]
    if not accs:
        await update.callback_query.edit_message_text("📭 គ្មាន Account ទេ។")
        return ADMIN_MENU
    keyboard = [
        [InlineKeyboardButton(
            f"{'❌' if v.get('sold') else '✅'} {v['name']} ({v['price']})",
            callback_data=f"delacc_{k}"
        )] for k, v in accs.items()
    ]
    keyboard.append([InlineKeyboardButton("🔙 ត្រឡប់", callback_data="back_main")])
    await update.callback_query.edit_message_text(
        "🗑 *ជ្រើស Account ដែលចង់លុប:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAIT_DEL_ACC

async def confirm_del_acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    acc_id = query.data.replace("delacc_", "")
    data   = db.load()
    data["accounts"].pop(acc_id, None)
    db.save(data)
    await query.edit_message_text(f"✅ បានលុប Account: `{acc_id}` ✅", parse_mode="Markdown")
    return await admin_start(update, context)


# ────────────────────────────────────────────────
#   ORDERS
# ────────────────────────────────────────────────
async def menu_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data   = db.load()
    orders = data["pending_orders"]

    if not orders:
        keyboard = [[InlineKeyboardButton("🔙 ត្រឡប់", callback_data="back_main")]]
        await query.edit_message_text(
            "📭 *គ្មាន Order រង់ចាំទេ។*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ADMIN_MENU

    msg = "📋 *Order កំពុងរង់ចាំ:*\n━━━━━━━━━━━━━━\n"
    for oid, o in orders.items():
        msg += (
            f"🆔 `{oid}`\n"
            f"👤 {o['customer_name']}\n"
            f"🛒 {o['item']} — {o['price']}\n"
            f"📦 {o['category']}\n"
            f"━━━━━━━━━━━━━━\n"
        )
    msg += "\n✅ /confirm ORDER\\_ID\n❌ /reject ORDER\\_ID"
    keyboard = [[InlineKeyboardButton("🔙 ត្រឡប់", callback_data="back_main")]]
    await query.edit_message_text(msg, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_MENU


# ────────────────────────────────────────────────
#   STOCK CHECK
# ────────────────────────────────────────────────
async def menu_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = db.load()
    accs  = data["accounts"]

    available = [v for v in accs.values() if not v.get("sold")]
    sold      = [v for v in accs.values() if v.get("sold")]

    keyboard = [[InlineKeyboardButton("🔙 ត្រឡប់", callback_data="back_main")]]
    await query.edit_message_text(
        f"📦 *Stock Overview*\n━━━━━━━━━━━━━━\n"
        f"✅ Account នៅ Stock: *{len(available)}*\n"
        f"❌ Account លក់ហើយ: *{len(sold)}*\n"
        f"📋 Order រង់ចាំ: *{len(data['pending_orders'])}*\n"
        f"🍎 Fruit ប្រភេទ: *{len(data['fruits'])}*\n"
        f"⚔️ Service ប្រភេទ: *{len(data['services'])}*\n"
        f"━━━━━━━━━━━━━━",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ADMIN_MENU


# ────────────────────────────────────────────────
#   CONFIRM / REJECT (text commands)
# ────────────────────────────────────────────────
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_CHAT_ID:
        return
    if not context.args:
        await update.message.reply_text("❓ /confirm ORDER_ID")
        return

    order_id = context.args[0]
    data     = db.load()
    order    = data["pending_orders"].get(order_id)

    if not order:
        await update.message.reply_text(f"⚠️ Order `{order_id}` រកមិនឃើញ។", parse_mode="Markdown")
        return

    s = data["settings"]

    if order.get("category") == "Account" and order.get("acc_id"):
        acc = data["accounts"].get(order["acc_id"])
        if acc:
            data["accounts"][order["acc_id"]]["sold"] = True
            await context.bot.send_message(
                chat_id=order["customer_id"],
                text=f"🎉 *បានបញ្ជាក់ការបង់ប្រាក់ហើយ!*\n"
                     f"━━━━━━━━━━━━━━\n"
                     f"🆔 Order: `{order_id}`\n"
                     f"🎮 {acc['name']}\n"
                     f"━━━━━━━━━━━━━━\n"
                     f"🔐 *ព័ត៌មានចូលគណនី:*\n"
                     f"👤 Username: `{acc['username']}`\n"
                     f"🔑 Password: `{acc['password']}`\n\n"
                     f"⚠️ *ប្តូរ Password ភ្លាមៗ!*\n"
                     f"🙏 អរគុណពី *{s['store_name']}* 🇰🇭",
                parse_mode="Markdown"
            )
    else:
        await context.bot.send_message(
            chat_id=order["customer_id"],
            text=f"🎉 *បានបញ្ជាក់ការបង់ប្រាក់ហើយ!*\n"
                 f"━━━━━━━━━━━━━━\n"
                 f"🆔 Order: `{order_id}`\n"
                 f"⚔️ {order['item']}\n"
                 f"🎮 Roblox: {order['roblox']}\n"
                 f"━━━━━━━━━━━━━━\n\n"
                 f"⚡ Online នៅ Roblox ឥឡូវ!\n"
                 f"🙏 អរគុណពី *{s['store_name']}* 🇰🇭",
            parse_mode="Markdown"
        )

    del data["pending_orders"][order_id]
    db.save(data)
    await update.message.reply_text(f"✅ Confirmed `{order_id}`", parse_mode="Markdown")


async def reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_CHAT_ID:
        return
    if not context.args:
        await update.message.reply_text("❓ /reject ORDER_ID")
        return

    order_id = context.args[0]
    data     = db.load()
    order    = data["pending_orders"].get(order_id)

    if not order:
        await update.message.reply_text(f"⚠️ Order `{order_id}` រកមិនឃើញ។", parse_mode="Markdown")
        return

    s = data["settings"]
    await context.bot.send_message(
        chat_id=order["customer_id"],
        text=f"❌ *ពិនិត្យការបង់ប្រាក់មិនឃើញ*\n"
             f"Order: `{order_id}`\n\n"
             f"សូមផ្ញើ screenshot ច្បាស់ ឬទំនាក់ទំនង {s['admin_username']} 🙏",
        parse_mode="Markdown"
    )
    del data["pending_orders"][order_id]
    db.save(data)
    await update.message.reply_text(f"❌ Rejected `{order_id}`", parse_mode="Markdown")


# ────────────────────────────────────────────────
#   CALLBACK ROUTER
# ────────────────────────────────────────────────
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data_cb = update.callback_query.data
    if data_cb == "back_main":       return await admin_start(update, context)
    if data_cb == "menu_settings":   return await menu_settings(update, context)
    if data_cb == "menu_fruits":     return await menu_fruits(update, context)
    if data_cb == "menu_services":   return await menu_services(update, context)
    if data_cb == "menu_accounts":   return await menu_accounts(update, context)
    if data_cb == "menu_orders":     return await menu_orders(update, context)
    if data_cb == "menu_stock":      return await menu_stock(update, context)
    if data_cb == "set_storename":   return await set_storename(update, context)
    if data_cb == "set_adminuser":   return await set_adminuser(update, context)
    if data_cb == "set_hours":       return await set_hours(update, context)
    if data_cb == "set_acleda_qr":   return await set_acleda_qr(update, context)
    if data_cb == "set_fruit_photo": return await set_fruit_photo(update, context)
    if data_cb == "set_service_photos": return await set_service_photos(update, context)
    if data_cb == "fruit_add":       return await fruit_add(update, context)
    if data_cb == "fruit_del":       return await fruit_del(update, context)
    if data_cb == "svc_add":         return await svc_add(update, context)
    if data_cb == "svc_del":         return await svc_del(update, context)
    if data_cb == "acc_add":         return await acc_add(update, context)
    if data_cb == "acc_del":         return await acc_del(update, context)
    if data_cb.startswith("delfruit_"): return await confirm_del_fruit(update, context)
    if data_cb.startswith("delsvc_"):   return await confirm_del_svc(update, context)
    if data_cb.startswith("delacc_"):   return await confirm_del_acc(update, context)


# ────────────────────────────────────────────────
#   MAIN
# ────────────────────────────────────────────────
def main():
    app = ApplicationBuilder().token(ADMIN_BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", admin_start)],
        states={
            ADMIN_MENU: [CallbackQueryHandler(callback_router)],
            WAIT_STORE_NAME:      [MessageHandler(filters.TEXT & ~filters.COMMAND, save_storename)],
            WAIT_ADMIN_USER:      [MessageHandler(filters.TEXT & ~filters.COMMAND, save_adminuser)],
            WAIT_SUPPORT_HOURS:   [MessageHandler(filters.TEXT & ~filters.COMMAND, save_hours)],
            WAIT_ACLEDA_QR:       [MessageHandler(filters.PHOTO, save_acleda_qr)],
            WAIT_FRUIT_LIST_PHOTO:[MessageHandler(filters.PHOTO, save_fruit_photo)],
            WAIT_SERVICE_PHOTO:   [
                MessageHandler(filters.PHOTO, collect_service_photo),
                CommandHandler("done", done_service_photos),
            ],
            WAIT_FRUIT_NAME:      [MessageHandler(filters.TEXT & ~filters.COMMAND, save_fruit_name)],
            WAIT_FRUIT_PRICE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, save_fruit_price)],
            WAIT_SERVICE_NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, save_svc_name)],
            WAIT_SERVICE_PRICE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, save_svc_price)],
            WAIT_ACC_NAME:        [MessageHandler(filters.TEXT & ~filters.COMMAND, save_acc_name)],
            WAIT_ACC_PRICE:       [MessageHandler(filters.TEXT & ~filters.COMMAND, save_acc_price)],
            WAIT_ACC_LEVEL:       [MessageHandler(filters.TEXT & ~filters.COMMAND, save_acc_level)],
            WAIT_ACC_FRUITS:      [MessageHandler(filters.TEXT & ~filters.COMMAND, save_acc_fruits)],
            WAIT_ACC_BELI:        [MessageHandler(filters.TEXT & ~filters.COMMAND, save_acc_beli)],
            WAIT_ACC_PHOTO:       [MessageHandler(filters.PHOTO, save_acc_photo)],
            WAIT_ACC_USERNAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, save_acc_username)],
            WAIT_ACC_PASSWORD:    [MessageHandler(filters.TEXT & ~filters.COMMAND, save_acc_password)],
            WAIT_DEL_FRUIT:       [CallbackQueryHandler(confirm_del_fruit, pattern="^delfruit_")],
            WAIT_DEL_SERVICE:     [CallbackQueryHandler(confirm_del_svc,   pattern="^delsvc_")],
            WAIT_DEL_ACC:         [CallbackQueryHandler(confirm_del_acc,   pattern="^delacc_")],
        },
        fallbacks=[CommandHandler("start", admin_start)],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("confirm", confirm_order))
    app.add_handler(CommandHandler("reject",  reject_order))

    print("🛠 Uchiro Admin Bot កំពុងដំណើរការ...")
    app.run_polling()


if __name__ == "__main__":
    main()
