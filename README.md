# 🏪 Uchiro Store — Bot Setup Guide

## 📁 Files ទាំងអស់
- `store_data.py` — ទិន្នន័យចែករំលែក
- `shop_bot.py`   — Bot សម្រាប់អតិថិជន
- `admin_bot.py`  — Bot សម្រាប់ Owner
- `requirements.txt`
- `Procfile`

## ⚙️ Variables នៅ Railway

| Variable | តម្លៃ |
|---|---|
| `SHOP_BOT_TOKEN` | Token Bot Shop (ពី @BotFather) |
| `ADMIN_BOT_TOKEN` | Token Bot Admin (ពី @BotFather) |
| `ADMIN_CHAT_ID` | ID របស់អ្នក (ពី @userinfobot) |

## 🚀 Deploy នៅ Railway

### Bot ទាំង 2 ក្នុង Repo តែមួយ
1. Upload files ទាំងអស់ទៅ GitHub repo
2. Deploy ទៅ Railway
3. បន្ថែម Variables ទាំង 3 ខាងលើ

### Procfile (សម្រាប់ run ទាំង 2 bot)
```
web: python shop_bot.py & python admin_bot.py
```

## 🛠 Admin Bot — Commands
- /start → Admin Panel ពេញ
- /confirm ORDER_ID → បញ្ជាក់ Order
- /reject ORDER_ID → បដិសេធ Order

## ✨ Admin Bot Features
- ប្តូរឈ្មោះ Store
- Upload QR Acleda ថ្មី
- Upload រូប Fruit List
- Upload រូប Service (ច្រើនរូប)
- បន្ថែម/លុប Fruit + តម្លៃ
- បន្ថែម/លុប Service + តម្លៃ
- បន្ថែម/លុប Account (Upload រូប + credentials)
- មើល Order ទាំងអស់
- ពិនិត្យ Stock
