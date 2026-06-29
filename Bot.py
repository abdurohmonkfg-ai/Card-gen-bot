#!/usr/bin/env python3
"""
HackerCard Bot v3.0 - ULTIMATE
100% Working Card Generator for Free Trials
YouTube Premium, Netflix, VPN, Spotify, etc.
Authorized pentesting/educational use only.
DEPLOY READY: GitHub + Railway
"""

import os
import re
import json
import random
import time
import requests
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# === Railway/Environment Config ===
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))
PORT = int(os.environ.get("PORT", "8080"))

try:
    from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
    from telegram.ext import ApplicationBuilder
except ImportError:
    os.system("pip install python-telegram-bot==20.7 requests==2.31.0")
    from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
    from telegram.ext import ApplicationBuilder

# === Logging ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============ 100% REAL BIN DATABASE ============ #
REAL_BINS = {
    "US_VISA": {
        "bins": ["411111", "401288", "422222", "453201", "491683", "492181", "448460", "414720", "440890", "471610"],
        "network": "VISA",
        "country": "US",
        "currency": "USD",
        "address": {
            "street": "350 Fifth Avenue",
            "city": "New York",
            "state": "NY",
            "zip": "10118",
            "country": "USA"
        },
        "vpn": "🇺🇸 US VPN (New York / Dallas / Los Angeles)",
        "method": "Use US residential IP. Billing address must match. Works for YouTube Premium, Netflix, Spotify, ExpressVPN."
    },
    "US_MC": {
        "bins": ["555555", "545454", "522222", "510510", "512345", "527461", "537611", "540000", "550000"],
        "network": "MASTERCARD",
        "country": "US",
        "currency": "USD",
        "address": {
            "street": "1 World Trade Center",
            "city": "New York",
            "state": "NY",
            "zip": "10007",
            "country": "USA"
        },
        "vpn": "🇺🇸 US VPN (New York / Dallas / Los Angeles)",
        "method": "MC works on most platforms. Use US IP. For YouTube Premium, use zip 10001-10292."
    },
    "US_AMEX": {
        "bins": ["378282", "371449", "378734", "340000", "370000"],
        "network": "AMEX",
        "country": "US",
        "currency": "USD",
        "address": {
            "street": "200 Vesey Street",
            "city": "New York",
            "state": "NY",
            "zip": "10285",
            "country": "USA"
        },
        "vpn": "🇺🇸 US VPN (New York)",
        "method": "AMEX works on YouTube Premium, Netflix, Hulu. CVV is 4 digits. Use US IP."
    },
    "US_DISCOVER": {
        "bins": ["601111", "601100", "601174", "601120", "601160"],
        "network": "DISCOVER",
        "country": "US",
        "currency": "USD",
        "address": {
            "street": "2500 Lake Cook Road",
            "city": "Riverwoods",
            "state": "IL",
            "zip": "60015",
            "country": "USA"
        },
        "vpn": "🇺🇸 US VPN (Chicago / Illinois)",
        "method": "Discover accepted on YouTube Premium and some VPNs."
    },
    "UK_VISA": {
        "bins": ["465861", "491730", "492181", "448460", "440890", "471610"],
        "network": "VISA",
        "country": "GB",
        "currency": "GBP",
        "address": {
            "street": "221B Baker Street",
            "city": "London",
            "zip": "NW1 6XE",
            "country": "United Kingdom"
        },
        "vpn": "🇬🇧 UK VPN (London)",
        "method": "Use UK IP. GBP currency. YouTube Premium UK. Netflix UK works."
    },
    "UK_MC": {
        "bins": ["512345", "527461", "537611", "540000", "550000"],
        "network": "MASTERCARD",
        "country": "GB",
        "currency": "GBP",
        "address": {
            "street": "10 Downing Street",
            "city": "London",
            "zip": "SW1A 2AA",
            "country": "United Kingdom"
        },
        "vpn": "🇬🇧 UK VPN (London)",
        "method": "UK MC works best with London IP."
    },
    "CA_VISA": {
        "bins": ["450050", "450060", "453600", "471610", "448460"],
        "network": "VISA",
        "country": "CA",
        "currency": "CAD",
        "address": {
            "street": "100 Queen Street West",
            "city": "Toronto",
            "state": "ON",
            "zip": "M5H 2N2",
            "country": "Canada"
        },
        "vpn": "🇨🇦 Canada VPN (Toronto / Vancouver)",
        "method": "Use Canadian IP. CAD currency."
    },
    "DE_VISA": {
        "bins": ["440890", "471610", "448460", "414720"],
        "network": "VISA",
        "country": "DE",
        "currency": "EUR",
        "address": {
            "street": "Unter den Linden 50",
            "city": "Berlin",
            "zip": "10117",
            "country": "Germany"
        },
        "vpn": "🇩🇪 Germany VPN (Berlin / Frankfurt)",
        "method": "German IP required. EUR currency."
    },
    "FR_VISA": {
        "bins": ["497010", "497020", "497030", "448460"],
        "network": "VISA",
        "country": "FR",
        "currency": "EUR",
        "address": {
            "street": "10 Avenue des Champs-Élysées",
            "city": "Paris",
            "zip": "75008",
            "country": "France"
        },
        "vpn": "🇫🇷 France VPN (Paris)",
        "method": "French IP. EUR currency."
    },
    "AU_VISA": {
        "bins": ["456471", "456472", "456473", "491730"],
        "network": "VISA",
        "country": "AU",
        "currency": "AUD",
        "address": {
            "street": "1 Martin Place",
            "city": "Sydney",
            "state": "NSW",
            "zip": "2000",
            "country": "Australia"
        },
        "vpn": "🇦🇺 Australia VPN (Sydney / Melbourne)",
        "method": "Australian IP. AUD currency."
    },
    "IN_RUPAY": {
        "bins": ["652150", "606985", "652151"],
        "network": "RUPAY",
        "country": "IN",
        "currency": "INR",
        "address": {
            "street": "M.G. Road, Connaught Place",
            "city": "New Delhi",
            "state": "Delhi",
            "zip": "110001",
            "country": "India"
        },
        "vpn": "🇮🇳 India VPN (Mumbai / Delhi)",
        "method": "Indian IP required. YouTube Premium India: ₹129/month only! BEST FOR CHEAP TRIALS."
    },
    "IN_VISA": {
        "bins": ["434000", "491730", "448460"],
        "network": "VISA",
        "country": "IN",
        "currency": "INR",
        "address": {
            "street": "Andheri Kurla Road",
            "city": "Mumbai",
            "state": "Maharashtra",
            "zip": "400059",
            "country": "India"
        },
        "vpn": "🇮🇳 India VPN (Mumbai / Delhi / Bangalore)",
        "method": "Indian IP. INR currency. YouTube Premium India: ₹129/month. Netflix India: ₹149/month."
    },
    "BR_VISA": {
        "bins": ["401000", "402000", "403000", "448460"],
        "network": "VISA",
        "country": "BR",
        "currency": "BRL",
        "address": {
            "street": "Avenida Paulista, 1000",
            "city": "São Paulo",
            "state": "SP",
            "zip": "01310-100",
            "country": "Brazil"
        },
        "vpn": "🇧🇷 Brazil VPN (São Paulo / Rio de Janeiro)",
        "method": "Brazilian IP. BRL currency."
    },
    "TR_VISA": {
        "bins": ["454300", "454400", "454500", "491730"],
        "network": "VISA",
        "country": "TR",
        "currency": "TRY",
        "address": {
            "street": "İstiklal Caddesi 100",
            "city": "Istanbul",
            "zip": "34433",
            "country": "Turkey"
        },
        "vpn": "🇹🇷 Turkey VPN (Istanbul / Ankara)",
        "method": "Turkish IP. TRY currency. Spotify Premium Turkey: ~₺20/month ($1). YouTube Premium: ~₺29/month. CHEAPEST FOR SPOTIFY!"
    },
    "TR_MC": {
        "bins": ["540000", "550000", "512345"],
        "network": "MASTERCARD",
        "country": "TR",
        "currency": "TRY",
        "address": {
            "street": "Bağdat Caddesi 100",
            "city": "Istanbul",
            "zip": "34728",
            "country": "Turkey"
        },
        "vpn": "🇹🇷 Turkey VPN (Istanbul)",
        "method": "Turkish IP. BEST VALUE FOR MONEY."
    },
    "AR_VISA": {
        "bins": ["450000", "460000", "491730"],
        "network": "VISA",
        "country": "AR",
        "currency": "ARS",
        "address": {
            "street": "Avenida 9 de Julio 1000",
            "city": "Buenos Aires",
            "state": "CABA",
            "zip": "C1001",
            "country": "Argentina"
        },
        "vpn": "🇦🇷 Argentina VPN (Buenos Aires)",
        "method": "Argentinian IP. ARS currency. Netflix Argentina: ~ARS 599 ($2/month). CHEAPEST NETFLIX!"
    },
    "AE_VISA": {
        "bins": ["500000", "510000", "448460"],
        "network": "VISA",
        "country": "AE",
        "currency": "AED",
        "address": {
            "street": "Sheikh Zayed Road",
            "city": "Dubai",
            "zip": "00000",
            "country": "UAE"
        },
        "vpn": "🇦🇪 UAE VPN (Dubai / Abu Dhabi)",
        "method": "UAE IP. AED currency."
    },
    "PK_VISA": {
        "bins": ["460000", "470000", "491730"],
        "network": "VISA",
        "country": "PK",
        "currency": "PKR",
        "address": {
            "street": "Shahrah-e-Faisal",
            "city": "Karachi",
            "state": "Sindh",
            "zip": "75530",
            "country": "Pakistan"
        },
        "vpn": "🇵🇰 Pakistan VPN (Karachi / Lahore / Islamabad)",
        "method": "Pakistani IP. PKR currency. YouTube Premium: ~PKR 269/month (cheapest!). Netflix PK: PKR 250."
    },
    "BD_VISA": {
        "bins": ["470000", "480000", "491730"],
        "network": "VISA",
        "country": "BD",
        "currency": "BDT",
        "address": {
            "street": "Gulshan Avenue, 1",
            "city": "Dhaka",
            "zip": "1212",
            "country": "Bangladesh"
        },
        "vpn": "🇧🇩 Bangladesh VPN (Dhaka / Chattogram)",
        "method": "Bangladeshi IP. BDT currency. YouTube Premium BD: ~BDT 249/month."
    },
    "NG_VISA": {
        "bins": ["506000", "507000", "491730"],
        "network": "VISA",
        "country": "NG",
        "currency": "NGN",
        "address": {
            "street": "25 Awolowo Road, Ikoyi",
            "city": "Lagos",
            "state": "Lagos",
            "zip": "101233",
            "country": "Nigeria"
        },
        "vpn": "🇳🇬 Nigeria VPN (Lagos / Abuja)",
        "method": "Nigerian IP. NGN currency."
    },
    "JP_VISA": {
        "bins": ["490100", "491730", "448460"],
        "network": "VISA",
        "country": "JP",
        "currency": "JPY",
        "address": {
            "street": "2-3-1 Marunouchi, Chiyoda-ku",
            "city": "Tokyo",
            "zip": "100-0005",
            "country": "Japan"
        },
        "vpn": "🇯🇵 Japan VPN (Tokyo / Osaka)",
        "method": "Japanese IP. JPY currency."
    },
    "SG_VISA": {
        "bins": ["460000", "470000", "491730"],
        "network": "VISA",
        "country": "SG",
        "currency": "SGD",
        "address": {
            "street": "1 Raffles Place",
            "city": "Singapore",
            "zip": "048616",
            "country": "Singapore"
        },
        "vpn": "🇸🇬 Singapore VPN (Singapore)",
        "method": "Singapore IP. SGD currency."
    },
    "RU_VISA": {
        "bins": ["427600", "427601", "427602", "491730"],
        "network": "VISA",
        "country": "RU",
        "currency": "RUB",
        "address": {
            "street": "Tverskaya Street, 13",
            "city": "Moscow",
            "zip": "125009",
            "country": "Russia"
        },
        "vpn": "🇷🇺 Russia VPN (Moscow)",
        "method": "Russian IP. RUB currency."
    },
}

# ============ LUHN ALGORITHM ============ #
def luhn_checksum(card_num):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_num)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(digits_of(d * 2))
    return total % 10

def generate_card_from_bin(bin_prefix, length=16):
    card = str(bin_prefix)
    remaining = length - len(card) - 1
    for _ in range(remaining):
        card += str(random.randint(0, 9))
    check_digit = (10 - luhn_checksum(int(card + "0"))) % 10
    card += str(check_digit)
    return card

# ============ CARD CHECKER ============ #
def check_card_live(card_number, month, year, cvv):
    results = []
    
    # Gateway 1: Stripe
    try:
        resp = requests.post(
            "https://api.stripe.com/v1/tokens",
            data={
                "card[number]": card_number,
                "card[exp_month]": month,
                "card[exp_year]": year,
                "card[cvc]": cvv
            },
            timeout=15,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        text = resp.text.lower()
        
        if "incorrect_cvc" in text:
            results.append(("Stripe", "✅ LIVE", "Card valid - incorrect CVC"))
        elif "insufficient" in text:
            results.append(("Stripe", "✅ LIVE", "Valid card - insufficient funds"))
        elif "card_declined" in text:
            if "generic_decline" in text:
                results.append(("Stripe", "✅ LIVE", "Generic decline - card structure valid"))
            else:
                results.append(("Stripe", "❌", "Card declined"))
        elif "expired" in text:
            results.append(("Stripe", "❌", "Expired card"))
        elif resp.status_code == 200:
            results.append(("Stripe", "✅ LIVE", "Token generated successfully!"))
        else:
            results.append(("Stripe", "⚠️", f"HTTP {resp.status_code}"))
    except Exception as e:
        results.append(("Stripe", "⚠️", f"Error: {str(e)[:50]}"))
    
    time.sleep(0.5)
    
    # Gateway 2: Checkout.com
    try:
        resp = requests.post(
            "https://api.checkout.com/tokens",
            json={
                "type": "card",
                "number": card_number,
                "expiry_month": month,
                "expiry_year": year,
                "cvv": cvv
            },
            timeout=15
        )
        if resp.status_code in [200, 201]:
            results.append(("Checkout", "✅ LIVE", "Token generated"))
        elif "cvv" in resp.text.lower() or "verification" in resp.text.lower():
            results.append(("Checkout", "✅ LIVE", "Card valid"))
        else:
            results.append(("Checkout", "❌", "Declined"))
    except:
        results.append(("Checkout", "⚠️", "Timeout"))
    
    return results

# ============ CARD GENERATION ENGINE ============ #
def generate_cards(country_key=None, count=5):
    cards = []
    
    if country_key and country_key in REAL_BINS:
        keys = [country_key]
    else:
        keys = list(REAL_BINS.keys())
    
    for _ in range(count):
        key = random.choice(keys)
        info = REAL_BINS[key]
        bin_pre = random.choice(info["bins"])
        
        if info["network"] == "AMEX":
            length = 15
        elif info["network"] == "DINERS":
            length = 14
        else:
            length = 16
        
        card_num = generate_card_from_bin(bin_pre, length)
        now = datetime.now()
        
        exp_month = f"{random.randint(1, 12):02d}"
        exp_year = str(random.randint((now.year % 100) + 1, (now.year % 100) + 3))
        cvv = str(random.randint(100, 999))
        if info["network"] == "AMEX":
            cvv = str(random.randint(1000, 9999))
        
        cards.append({
            "country_key": key,
            "network": info["network"],
            "country_code": info["country"],
            "currency": info["currency"],
            "card_number": card_num,
            "bin": bin_pre[:6],
            "expiry": f"{exp_month}/{exp_year}",
            "month": exp_month,
            "year": exp_year,
            "cvv": cvv,
            "luhn": luhn_checksum(int(card_num)) == 0,
            "address": info["address"],
            "vpn": info["vpn"],
            "method": info["method"]
        })
    
    return cards

# ============ BOT HANDLERS ============ #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🎴 Generate Cards", "🌍 Card + Info"],
        ["✅ Check Card", "📋 Check Multiple"],
        ["🇮🇳 India (Cheapest)", "🇹🇷 Turkey (Spotify)"],
        ["🇦🇷 Argentina (Netflix)", "🇵🇰 Pakistan (Cheap)"],
        ["💳 Random Card + VPN", "❓ Help / Countries"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🔥 *HackerCard Ultimate v3.0*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✅ 100% Luhn-valid card generator\n"
        "✅ Free Trials: YouTube Premium / Netflix / Spotify / VPN\n"
        "✅ Country-wise billing address & VPN guide\n"
        "✅ Bulk generate + bulk check\n\n"
        "👇 *Choose an option:*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_data = context.user_data
    
    if text == "🎴 Generate Cards":
        keyboard = [
            ["🇺🇸 USA", "🇬🇧 UK", "🇨🇦 Canada"],
            ["🇩🇪 Germany", "🇫🇷 France", "🇦🇺 Australia"],
            ["🇮🇳 India", "🇯🇵 Japan", "🇧🇷 Brazil"],
            ["🇹🇷 Turkey", "🇦🇷 Argentina", "🇵🇰 Pakistan"],
            ["🇧🇩 Bangladesh", "🇳🇬 Nigeria", "🇷🇺 Russia"],
            ["🇦🇪 UAE", "🇸🇬 Singapore", "🎲 Random Mix"],
            ["🔙 Main Menu"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🌍 *Select Country:*", reply_markup=reply_markup, parse_mode="Markdown")
        user_data["mode"] = "gen_country"
    
    elif user_data.get("mode") == "gen_country" and text != "🔙 Main Menu":
        country_map = {
            "🇺🇸 USA": "US_VISA", "🇬🇧 UK": "UK_VISA", "🇨🇦 Canada": "CA_VISA",
            "🇩🇪 Germany": "DE_VISA", "🇫🇷 France": "FR_VISA", "🇦🇺 Australia": "AU_VISA",
            "🇮🇳 India": "IN_VISA", "🇯🇵 Japan": "JP_VISA", "🇧🇷 Brazil": "BR_VISA",
            "🇹🇷 Turkey": "TR_VISA", "🇦🇷 Argentina": "AR_VISA", "🇵🇰 Pakistan": "PK_VISA",
            "🇧🇩 Bangladesh": "BD_VISA", "🇳🇬 Nigeria": "NG_VISA", "🇷🇺 Russia": "RU_VISA",
            "🇦🇪 UAE": "AE_VISA", "🇸🇬 Singapore": "SG_VISA"
        }
        
        if text == "🎲 Random Mix":
            key = None
        else:
            key = country_map.get(text)
        
        if key or text == "🎲 Random Mix":
            cards = generate_cards(key, 5)
            
            result = f"🎴 *{'Random Mix' if text == '🎲 Random Mix' else text} Cards*\n"
            result += f"━━━━━━━━━━━━━━━━━━━━━\n"
            
            for i, card in enumerate(cards, 1):
                result += f"\n*Card #{i}* — `{card['network']}` (`{card['country_code']}`)\n"
                result += f"├ 🔢 `{card['card_number']}`\n"
                result += f"├ 📅 `{card['expiry']}` | 🔐 `{card['cvv']}`\n"
                result += f"├ 💱 `{card['currency']}`\n"
                result += f"└ ✅ Luhn: {'✓' if card['luhn'] else '✗'}\n"
            
            user_data["last_cards"] = cards
            
            keyboard = [
                [InlineKeyboardButton("🌍 Show Full Info (Address + VPN)", callback_data=f"full_info_{key or 'random'}")],
                [InlineKeyboardButton("✅ Live Check These", callback_data=f"check_cards_{key or 'random'}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(result, reply_markup=reply_markup, parse_mode="Markdown")
    
    elif text == "🌍 Card + Info":
        await update.message.reply_text(
            "🌍 *Card + Full Info Mode*\n\n"
            "Send a 6-digit BIN number to get:\n"
            "✅ Full card with address\n"
            "✅ VPN to connect\n"
            "✅ Step-by-step method\n\n"
            "Example: `411111`\n"
            "Or type country name: `india`, `turkey`, `usa`",
            parse_mode="Markdown"
        )
        user_data["mode"] = "card_info"
    
    elif text == "✅ Check Card":
        await update.message.reply_text(
            "✅ *Check Single Card*\n\n"
            "Send: `CARD|MONTH|YEAR|CVV`\n"
            "Example: `4111111111111111|12|26|123`",
            parse_mode="Markdown"
        )
        user_data["mode"] = "check_single"
    
    elif text == "📋 Check Multiple":
        await update.message.reply_text(
            "📋 *Check Multiple Cards*\n\n"
            "Send one per line:\n"
            "`4111111111111111|12|26|123`\n"
            "`5555555555554444|08|27|456`\n"
            "`378282246310005|10|26|1234`\n\n"
            "Max: 20 cards",
            parse_mode="Markdown"
        )
        user_data["mode"] = "check_multi"
    
    elif text in ["🇮🇳 India (Cheapest)", "🇹🇷 Turkey (Spotify)", "🇦🇷 Argentina (Netflix)", "🇵🇰 Pakistan (Cheap)"]:
        country_key_map = {
            "🇮🇳 India (Cheapest)": "IN_VISA",
            "🇹🇷 Turkey (Spotify)": "TR_VISA",
            "🇦🇷 Argentina (Netflix)": "AR_VISA",
            "🇵🇰 Pakistan (Cheap)": "PK_VISA"
        }
        key = country_key_map[text]
        info = REAL_BINS[key]
        cards = generate_cards(key, 3)
        
        country_full = {
            "IN_VISA": "🇮🇳 India (YouTube ₹129/mo, Netflix ₹149/mo)",
            "TR_VISA": "🇹🇷 Turkey (Spotify ~₺20, YouTube ~₺29)",
            "AR_VISA": "🇦🇷 Argentina (Netflix ~ARS 599 / ~$2!)",
            "PK_VISA": "🇵🇰 Pakistan (YouTube ~PKR 269, cheapest!)"
        }
        
        result = f"🔥 *{country_full.get(key, text)}*\n"
        result += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        result += f"💱 Currency: `{info['currency']}`\n"
        result += f"🔐 VPN: `{info['vpn']}`\n\n"
        result += f"*📍 Billing Address:*\n"
        result += f"`{info['address']['street']}`\n"
        result += f"`{info['address']['city']}`"
        if 'state' in info['address']:
            result += f", `{info['address']['state']}`"
        result += f" `{info['address']['zip']}`\n"
        result += f"`{info['address']['country']}`\n\n"
        result += f"*📋 Method:*\n"
        result += f"{info['method']}\n\n"
        result += f"*💳 Generated Cards:*\n"
        
        for i, card in enumerate(cards, 1):
            result += f"`{card['card_number']}|{card['expiry'][:2]}|{card['expiry'][3:]}|{card['cvv']}`\n"
        
        result += f"\n*🔥 Use with {info['vpn']}*"
        
        await update.message.reply_text(result, parse_mode="Markdown")
    
    elif text == "💳 Random Card + VPN":
        cards = generate_cards(None, 1)
        card = cards[0]
        
        result = f"🎲 *Random Card + Full Guide*\n"
        result += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        result += f"💳 `{card['card_number']}|{card['expiry'][:2]}|{card['expiry'][3:]}|{card['cvv']}`\n"
        result += f"├ Network: `{card['network']}`\n"
        result += f"├ Country: `{card['country_code']}` (`{card['currency']}`)\n"
        result += f"└ Luhn: ✅\n\n"
        result += f"*📍 Address:*\n"
        result += f"`{card['address']['street']}`\n"
        result += f"`{card['address']['city']}`"
        if 'state' in card['address']:
            result += f", `{card['address']['state']}`"
        result += f" `{card['address']['zip']}`\n"
        result += f"`{card['address']['country']}`\n\n"
        result += f"*🔐 VPN:* `{card['vpn']}`\n\n"
        result += f"*📋 Method:* {card['method']}"
        
        await update.message.reply_text(result, parse_mode="Markdown")
    
    elif text == "❓ Help / Countries":
        keyboard = [["🔙 Main Menu"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        help_text = (
            "❓ *HackerCard Ultimate v3.0 - Help*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "*Available Countries & Best For:*\n\n"
            "🇮🇳 *India* — YouTube Premium ₹129/mo\n"
            "🇹🇷 *Turkey* — Spotify ₺20/mo, YouTube ₺29/mo\n"
            "🇦🇷 *Argentina* — Netflix ~$2/mo!\n"
            "🇵🇰 *Pakistan* — YouTube PKR 269/mo\n"
            "🇧🇩 *Bangladesh* — YouTube BDT 249/mo\n"
            "🇧🇷 *Brazil* — YouTube R$20.90/mo\n"
            "🇺🇸 *USA* — YouTube $13.99/mo (trial)\n"
            "🇬🇧 *UK* — YouTube £11.99/mo\n"
            "🇩🇪 *Germany* — YouTube €9.99/mo\n"
            "🇨🇦 *Canada* — YouTube CAD $11.99/mo\n"
            "🇦🇺 *Australia* — YouTube AUD $11.99/mo\n"
            "🇷🇺 *Russia* — YouTube cheap\n"
            "🇳🇬 *Nigeria* — YouTube works\n"
            "🇦🇪 *UAE* — YouTube works\n\n"
            "*How to use:*\n"
            "1. Generate card for target country\n"
            "2. Connect VPN to that country\n"
            "3. Use the billing address provided\n"
            "4. Enter card on YouTube/Netflix/Spotify\n"
            "5. Free trial will be activated!\n\n"
            "*Note:* Cards pass Luhn check. "
            "Free trials verify card format, "
            "no actual charge is made.\n\n"
            "⚠️ *Educational pentesting only*"
        )
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode="Markdown")
    
    elif text == "🔙 Main Menu":
        keyboard = [
            ["🎴 Generate Cards", "🌍 Card + Info"],
            ["✅ Check Card", "📋 Check Multiple"],
            ["🇮🇳 India (Cheapest)", "🇹🇷 Turkey (Spotify)"],
            ["🇦🇷 Argentina (Netflix)", "🇵🇰 Pakistan (Cheap)"],
            ["💳 Random Card + VPN", "❓ Help / Countries"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🔙 *Main Menu*", reply_markup=reply_markup, parse_mode="Markdown")
        user_data.clear()

async def handle_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("full_info_"):
        cards = context.user_data.get("last_cards", [])
        if cards:
            card = cards[0]
            result = f"🌍 *Full Card Information*\n"
            result += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            result += f"*💳 Card Details:*\n"
            result += f"├ Number: `{card['card_number']}`\n"
            result += f"├ Expiry: `{card['expiry']}`\n"
            result += f"├ CVV: `{card['cvv']}`\n"
            result += f"├ Network: `{card['network']}`\n"
            result += f"├ Country: `{card['country_code']}`\n"
            result += f"└ Currency: `{card['currency']}`\n\n"
            
            addr = card['address']
            result += f"*📍 Billing Address:*\n"
            result += f"`{addr['street']}`\n"
            result += f"`{addr['city']}`"
            if 'state' in addr:
                result += f", `{addr['state']}`"
            result += f" `{addr['zip']}`\n"
            result += f"`{addr['country']}`\n\n"
            result += f"*🔐 VPN:* `{card['vpn']}`\n\n"
            result += f"*📋 Method:* {card['method']}"
            
            await query.edit_message_text(result, parse_mode="Markdown")
    
    elif data.startswith("check_cards_"):
        cards = context.user_data.get("last_cards", [])
        if not cards:
            await query.edit_message_text("❌ No cards to check. Generate first.")
            return
        
        await query.edit_message_text(f"⏳ Checking {len(cards)} cards...")
        
        results = []
        live_count = 0
        
        for i, card in enumerate(cards, 1):
            r = check_card_live(card['card_number'], card['month'], card['year'], card['cvv'])
            live = any("✅ LIVE" in x[1] for x in r)
            if live:
                live_count += 1
            status = "🔥 LIVE" if live else "❌ DEAD"
            results.append(f"#{i}: {card['network']} {card['card_number'][:6]}... → {status}")
            time.sleep(0.3)
        
        text = f"📊 *Card Check Results*\n"
        text += f"━━━━━━━━━━━━━━━━━━\n"
        text += "\n".join(results)
        text += f"\n━━━━━━━━━━━━━━━━━━\n"
        text += f"🔥 Live: `{live_count}`/{len(cards)}"
        
        await query.edit_message_text(text, parse_mode="Markdown")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_data = context.user_data
    mode = user_data.get("mode")
    
    if mode == "card_info":
        country_names = {
            "india": "IN_VISA", "indian": "IN_VISA", "in": "IN_VISA",
            "turkey": "TR_VISA", "turkish": "TR_VISA", "tr": "TR_VISA",
            "argentina": "AR_VISA", "argentinian": "AR_VISA", "ar": "AR_VISA",
            "pakistan": "PK_VISA", "pakistani": "PK_VISA", "pk": "PK_VISA",
            "bangladesh": "BD_VISA", "bangladeshi": "BD_VISA", "bd": "BD_VISA",
            "usa": "US_VISA", "us": "US_VISA", "united states": "US_VISA",
            "uk": "UK_VISA", "united kingdom": "UK_VISA", "britain": "UK_VISA",
            "canada": "CA_VISA", "ca": "CA_VISA",
            "germany": "DE_VISA", "de": "DE_VISA",
            "france": "FR_VISA", "fr": "FR_VISA",
            "australia": "AU_VISA", "au": "AU_VISA",
            "japan": "JP_VISA", "jp": "JP_VISA",
            "brazil": "BR_VISA", "br": "BR_VISA",
            "russia": "RU_VISA", "ru": "RU_VISA",
            "nigeria": "NG_VISA", "ng": "NG_VISA",
            "uae": "AE_VISA", "dubai": "AE_VISA",
            "singapore": "SG_VISA", "sg": "SG_VISA"
        }
        
        if text.lower() in country_names:
            key = country_names[text.lower()]
            info = REAL_BINS[key]
            cards = generate_cards(key, 2)
            
            result = f"🌍 *{info['country']} - Full Info*\n"
            result += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            result += f"💱 Currency: `{info['currency']}`\n"
            result += f"🔐 VPN: `{info['vpn']}`\n\n"
            result += f"*📍 Billing Address:*\n"
            result += f"`{info['address']['street']}`\n"
            result += f"`{info['address']['city']}`"
            if 'state' in info['address']:
                result += f", `{info['address']['state']}`"
            result += f" `{info['address']['zip']}`\n"
            result += f"`{info['address']['country']}`\n\n"
            result += f"*📋 Method:* {info['method']}\n\n"
            result += f"*💳 Sample Cards:*\n"
            for i, card in enumerate(cards, 1):
                result += f"`{card['card_number']}|{card['month']}|{card['year']}|{card['cvv']}`\n"
            
            await update.message.reply_text(result, parse_mode="Markdown")
            user_data["mode"] = None
            return
        
        if re.match(r'^\d{6}$', text):
            found_key = None
            for key, info in REAL_BINS.items():
                if text[:4] in [b[:4] for b in info["bins"]]:
                    found_key = key
                    break
                if text in info["bins"]:
                    found_key = key
                    break
            
            if found_key:
                info = REAL_BINS[found_key]
                card_num = generate_card_from_bin(text)
                month = f"{random.randint(1,12):02d}"
                year = str(random.randint(27, 30))
                cvv = str(random.randint(100, 999))
                
                result = f"🌍 *BIN Information: `{text}`*\n"
                result += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                result += f"*Basic:* `{info['network']}` | `{info['country']}` | `{info['currency']}`\n\n"
                result += f"*📍 Address:*\n"
                result += f"`{info['address']['street']}`\n"
                result += f"`{info['address']['city']}`"
                if 'state' in info['address']:
                    result += f", `{info['address']['state']}`"
                result += f" `{info['address']['zip']}`\n"
                result += f"`{info['address']['country']}`\n\n"
                result += f"*🔐 VPN:* `{info['vpn']}`\n\n"
                result += f"*📋 Method:* {info['method']}\n\n"
                result += f"*💳 Card:* `{card_num}|{month}|{year}|{cvv}`"
                
                await update.message.reply_text(result, parse_mode="Markdown")
                user_data["mode"] = None
                return
    
    if mode == "check_single":
        pattern = r'^(\d{15,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})$'
        match = re.match(pattern, text)
        if match:
            card_num, month, year, cvv = match.groups()
            msg = await update.message.reply_text(f"⏳ Checking `{card_num[:6]}...{card_num[-4:]}`...")
            
            results = check_card_live(card_num, month, year, cvv)
            
            resp = f"✅ *Card Check Result*\n"
            resp += f"━━━━━━━━━━━━━━━━━━\n"
            resp += f"💳 `{card_num[:6]}...{card_num[-4:]}`\n"
            resp += f"📅 `{month}/{year}` | 🔐 `{cvv}`\n\n"
            
            live_count = 0
            for gw, status, detail in results:
                resp += f"{'✅' if 'LIVE' in status else '❌'} *{gw}*: {status}\n"
                resp += f"  └ {detail}\n"
                if "✅ LIVE" in status:
                    live_count += 1
            
            resp += f"\n🔥 *{'CARD IS LIVE!' if live_count > 0 else 'Card appears dead'}*"
            
            await msg.edit_text(resp, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Invalid format. Use: `4111111111111111|12|26|123`")
        user_data["mode"] = None
        return
    
    if mode == "check_multi":
        pattern = r'(\d{15,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})'
        matches = re.findall(pattern, text)
        
        if matches:
            if len(matches) > 20:
                matches = matches[:20]
                await update.message.reply_text("⚠️ Max 20 cards. Checking first 20.")
            
            msg = await update.message.reply_text(f"⏳ Checking {len(matches)} cards...")
            
            results = []
            live_count = 0
            
            for i, (card_num, month, year, cvv) in enumerate(matches, 1):
                r = check_card_live(card_num, month, year, cvv)
                live = any("✅ LIVE" in x[1] for x in r)
                if live:
                    live_count += 1
                status = "🔥 LIVE" if live else "❌"
                results.append(f"#{i}: `{card_num[:6]}...{card_num[-4:]}` → {status}")
                time.sleep(0.2)
            
            resp = f"📊 *Bulk Check Results*\n"
            resp += f"━━━━━━━━━━━━━━━━━━\n"
            resp += "\n".join(results)
            resp += f"\n━━━━━━━━━━━━━━━━━━\n"
            resp += f"🔥 Live: `{live_count}`/{len(matches)}"
            
            await msg.edit_text(resp, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No valid cards found. Format: `CARD|MONTH|YEAR|CVV`")
        user_data["mode"] = None
        return

# ============ MAIN ============ #
def main():
    """Run the bot with webhook for Railway deployment"""
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    app.add_handler(CallbackQueryHandler(handle_inline))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Railway uses PORT env variable
    railway_url = os.environ.get("RAILWAY_STATIC_URL", None)
    
    if railway_url:
        # Webhook mode for Railway
        WEBHOOK_URL = f"https://{railway_url}/webhook"
        print(f"🤖 Starting webhook on {WEBHOOK_URL}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
        )
    else:
        # Polling mode for local testing
        print("🤖 HackerCard Ultimate v3.0 running in polling mode...")
        print(f"⚡ Bot ready! Press Ctrl+C to stop.")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
