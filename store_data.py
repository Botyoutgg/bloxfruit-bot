"""
====================================================
   UCHIRO STORE — Shared Data (store_data.py)
   ទិន្នន័យចែករំលែករវាង Bot ទាំង 2
====================================================
"""
import json
import os

DATA_FILE = "data.json"

DEFAULT_DATA = {
    "settings": {
        "store_name":        "🏪 Uchiro Store",
        "admin_username":    "@noreakyout",
        "acleda_qr_url":     "",
        "fruit_list_photo":  "",
        "service_photos":    [],
        "support_hours":     "8:00 - 22:00",
    },
    "fruits": {
        "🐆 Leopard":  "$50",
        "🐉 Dragon":   "$30",
        "🦊 Kitsune":  "$25",
        "☀️ Solar":    "$20",
        "🌊 Tsunami":  "$15",
    },
    "services": {
        "⚔️ Raid Service":         "$3",
        "👑 Boss Carry":            "$2",
        "🏆 Full Raid Package x5": "$12",
        "⭐ Level Up Service":      "$5",
    },
    "accounts": {},
    "pending_orders": {},
    "acc_counter": 1,
}


def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # merge missing keys
            for k, v in DEFAULT_DATA.items():
                if k not in data:
                    data[k] = v
            return data
    return dict(DEFAULT_DATA)


def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
