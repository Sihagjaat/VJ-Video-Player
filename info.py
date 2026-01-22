# VJ Video Player - Configuration File
# YouTube: @Tech_VJ | Telegram: @VJ_Bots | GitHub: @VJBots

import re
import os
from os import environ
from Script import script

# Get environment variable helper function
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot Configuration
id_pattern = re.compile(r'^.\d+$')

# ==================== REQUIRED SETTINGS ====================

# Telegram API Credentials (Get from https://my.telegram.org)
API_ID = int(environ.get('API_ID', ''))
API_HASH = environ.get('API_HASH', '')

# Bot Token (Get from @BotFather)
BOT_TOKEN = environ.get('BOT_TOKEN', '')

# Backup Bot Token (Optional - for failover)
BACKUP_BOT_TOKEN = environ.get('BACKUP_BOT_TOKEN', '')

# Log Channel (Channel ID where bot stores files)
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', ''))

# Admin User IDs (Comma separated)
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]

# MongoDB Configuration
MONGODB_URI = environ.get('MONGODB_URI', '')
SESSION = environ.get('SESSION', 'TechVJBot')

# Stream Link (Your app URL - must end with /)
STREAM_LINK = environ.get('STREAM_LINK', '')

# Permanent Link URL (Blogspot page for permanent links)
LINK_URL = environ.get('LINK_URL', '')

# ==================== ADS CONFIGURATION ====================

# Enable/Disable Ads
ENABLE_ADS = is_enabled(environ.get('ENABLE_ADS', 'True'), True)

# Adsterra Configuration
ADSTERRA_SCRIPT_1 = environ.get(
    'ADSTERRA_SCRIPT_1', 
    'https://pl28536872.effectivegatecpm.com/e7/77/82/e777826c5b5ced68f6bd82d00fb2edc5.js'
)

ADSTERRA_SCRIPT_2 = environ.get(
    'ADSTERRA_SCRIPT_2',
    'https://pl28536788.effectivegatecpm.com/b3/00/89/b300894535797cd9fb37cef5b4da3fc4.js'
)

ADSTERRA_POPUNDER = environ.get(
    'ADSTERRA_POPUNDER',
    'https://www.effectivegatecpm.com/f3s66q5u?key=a72949a34fd6ec42f0ca9bb17637a4e6'
)

# Custom Ad Codes (Optional - HTML code for custom ads)
HEADER_AD_CODE = environ.get('HEADER_AD_CODE', '')
SIDEBAR_AD_CODE = environ.get('SIDEBAR_AD_CODE', '')
FOOTER_AD_CODE = environ.get('FOOTER_AD_CODE', '')

# Google AdSense (Optional)
ADSENSE_ID = environ.get('ADSENSE_ID', '')  # ca-pub-XXXXXXXXXXXXXXXX

# ==================== MULTI-CLIENT SUPPORT ====================

# Enable Multi-Client Mode
MULTI_CLIENT = is_enabled(environ.get('MULTI_CLIENT', 'False'), False)

# Multi-Client Tokens (up to 50 bots)
MULTI_TOKEN1 = environ.get('MULTI_TOKEN1', '')
MULTI_TOKEN2 = environ.get('MULTI_TOKEN2', '')
MULTI_TOKEN3 = environ.get('MULTI_TOKEN3', '')
MULTI_TOKEN4 = environ.get('MULTI_TOKEN4', '')
MULTI_TOKEN5 = environ.get('MULTI_TOKEN5', '')
# Add more as needed: MULTI_TOKEN6, MULTI_TOKEN7, etc.

# ==================== OPTIONAL SETTINGS ====================

# Server Port
PORT = int(environ.get('PORT', '8080'))

# Sleep Threshold (Pyrogram flood wait)
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))

# Workers (Pyrogram)
WORKERS = int(environ.get('WORKERS', '200'))

# ==================== EARNINGS & PAYMENTS ====================

# CPM Rate (Earnings per 1000 views)
CPM_RATE = float(environ.get('CPM_RATE', '3.5'))

# Minimum Withdrawal Amount
MIN_WITHDRAWAL = int(environ.get('MIN_WITHDRAWAL', '100'))

# Payment Methods
UPI_ID = environ.get('UPI_ID', '')
BANK_ACCOUNT = environ.get('BANK_ACCOUNT', '')
PAYMENT_QR = environ.get('PAYMENT_QR', '')  # QR code image URL

# ==================== URL SHORTENER (OPTIONAL) ====================

# Enable URL Shortener
USE_SHORTENER = is_enabled(environ.get('USE_SHORTENER', 'False'), False)

# Shortener Configuration
SHORTENER_API = environ.get('SHORTENER_API', '')
SHORTENER_URL = environ.get('SHORTENER_URL', '')

# Supported Shorteners: GPLinks, Shrinkme, LinkTree, etc.

# ==================== FEATURES ====================

# Enable Quality Selection
ENABLE_QUALITY = is_enabled(environ.get('ENABLE_QUALITY', 'True'), True)

# Enable Download Button
ENABLE_DOWNLOAD = is_enabled(environ.get('ENABLE_DOWNLOAD', 'True'), True)

# Enable View Counter
ENABLE_VIEW_COUNTER = is_enabled(environ.get('ENABLE_VIEW_COUNTER', 'True'), True)

# Enable User Earnings Dashboard
ENABLE_EARNINGS = is_enabled(environ.get('ENABLE_EARNINGS', 'True'), True)

# ==================== CUSTOMIZATION ====================

# Bot Name
BOT_NAME = environ.get('BOT_NAME', 'VJ Video Player')

# Owner Name
OWNER_NAME = environ.get('OWNER_NAME', 'Tech VJ')

# Owner Username
OWNER_USERNAME = environ.get('OWNER_USERNAME', 'VJ_Bots')

# Support Group
SUPPORT_GROUP = environ.get('SUPPORT_GROUP', 'vj_bot_disscussion')

# Updates Channel
UPDATES_CHANNEL = environ.get('UPDATES_CHANNEL', 'VJ_Bots')

# Custom Welcome Message
WELCOME_MSG = environ.get('WELCOME_MSG', script.START_MSG)

# ==================== DATABASE COLLECTIONS ====================

# Collection Names
USERS_COLLECTION = environ.get('USERS_COLLECTION', 'users')
FILES_COLLECTION = environ.get('FILES_COLLECTION', 'files')
EARNINGS_COLLECTION = environ.get('EARNINGS_COLLECTION', 'earnings')
WITHDRAWALS_COLLECTION = environ.get('WITHDRAWALS_COLLECTION', 'withdrawals')

# ==================== SECURITY ====================

# Banned Users
BANNED_USERS = set(int(x) for x in environ.get("BANNED_USERS", "").split())

# Force Subscribe Channel (Optional)
FORCE_SUB_CHANNEL = int(environ.get('FORCE_SUB_CHANNEL', '0')) if environ.get('FORCE_SUB_CHANNEL') else None

# Disable Forward (Prevent file forwarding)
DISABLE_FORWARD = is_enabled(environ.get('DISABLE_FORWARD', 'False'), False)

# Protect Content (Prevent screenshots/screen recording)
PROTECT_CONTENT = is_enabled(environ.get('PROTECT_CONTENT', 'False'), False)

# ==================== LOGGING ====================

# Log All Activities
LOG_ALL = is_enabled(environ.get('LOG_ALL', 'True'), True)

# ==================== VALIDATION ====================

def validate_config():
    """Validate required configuration"""
    errors = []
    
    if not API_ID:
        errors.append("❌ API_ID is required")
    
    if not API_HASH:
        errors.append("❌ API_HASH is required")
    
    if not BOT_TOKEN:
        errors.append("❌ BOT_TOKEN is required")
    
    if not LOG_CHANNEL:
        errors.append("❌ LOG_CHANNEL is required")
    
    if not MONGODB_URI:
        errors.append("❌ MONGODB_URI is required")
    
    if not STREAM_LINK:
        errors.append("❌ STREAM_LINK is required")
    elif not STREAM_LINK.endswith('/'):
        errors.append("❌ STREAM_LINK must end with /")
    
    if not ADMINS:
        errors.append("⚠️ Warning: No ADMINS defined")
    
    if errors:
        print("\n".join(errors))
        return False
    
    return True

# Run validation
if not validate_config():
    print("\n⚠️ Configuration errors found! Please fix them before starting the bot.\n")
    exit(1)

# ==================== DISPLAY CONFIG ====================

print("\n" + "="*50)
print("🎬 VJ VIDEO PLAYER CONFIGURATION")
print("="*50)
print(f"✅ Bot Name: {BOT_NAME}")
print(f"✅ API ID: {API_ID}")
print(f"✅ Log Channel: {LOG_CHANNEL}")
print(f"✅ MongoDB: Connected")
print(f"✅ Stream Link: {STREAM_LINK}")
print(f"✅ Port: {PORT}")
print(f"💰 Ads: {'Enabled (Adsterra)' if ENABLE_ADS else 'Disabled'}")
print(f"🎥 Quality Selection: {'Enabled' if ENABLE_QUALITY else 'Disabled'}")
print(f"📊 Earnings Dashboard: {'Enabled' if ENABLE_EARNINGS else 'Disabled'}")
print(f"👥 Multi-Client: {'Enabled' if MULTI_CLIENT else 'Disabled'}")
print("="*50 + "\n")
