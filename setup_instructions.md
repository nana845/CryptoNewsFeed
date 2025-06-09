# د کریپټو خبرونو تلیګرام بوټ - د پیل کولو لارښوونې
# Telegram Crypto News Bot - Setup Instructions

## 1. د چاپیریال متغیرونو تنظیم - Environment Variables Setup

### Replit کې د متغیرونو اضافه کول - Adding Variables in Replit:

1. د Replit کې د خپل پروژې کې ولاړ شئ
2. د کیڼ اړخ کې "Secrets" ټب ته ورشئ
3. دا دوه متغیرونه اضافه کړئ:

```
BOT_TOKEN = your_actual_bot_token_here
CHANNEL_ID = @YourActualChannelUsername
```

### د بوټ ټوکن اخیستل - Getting Bot Token:

1. تلیګرام کې @BotFather ته ورشئ
2. `/newbot` واستوئ
3. د بوټ نوم ټاکئ
4. د بوټ د کارونکي نوم ټاکئ
5. ټوکن کاپي کړئ او په `BOT_TOKEN` کې یې ورکړئ

### د چینل ID موندل - Finding Channel ID:

1. د خپل چینل ته ورشئ
2. که ستاسو چینل عامه وي: `@YourChannelName`
3. که ستاسو چینل شخصي وي: د چینل ID کارول ضروری دي

## 2. د بوټ د چینل ته اضافه کول - Adding Bot to Channel

1. د خپل چینل ته ورشئ
2. د چینل تنظیمات ته ورشئ
3. "Administrators" ته ورشئ
4. "Add Admin" کلیک کړئ
5. د خپل بوټ نوم ولټوئ
6. بوټ ته د "Post Messages" اجازه ورکړئ

## 3. د کوډ اجرا کول - Running the Code

### Replit کې:
```bash
python telegram_crypto_bot.py
```

### محلي کمپیوټر کې:
```bash
# د کتابتونونو نصبول
pip install flask feedparser requests googletrans==4.0.0rc1

# د چاپیریال متغیرونو تنظیم
export BOT_TOKEN="your_bot_token"
export CHANNEL_ID="@your_channel"

# د کوډ اجرا کول
python telegram_crypto_bot.py
```

## 4. د بوټ ازمویل - Testing the Bot

1. بوټ پیل کړئ
2. د لاګونو کتنه وکړئ
3. د ۱۰ دقیقو انتظار وکړئ
4. د خپل چینل کتنه وکړئ

## 5. د عادي ستونزو حل - Common Issues Solutions

### د بوټ ټوکن ستونزه:
- ډاډ ترلاسه کړئ چې ټوکن سمه ده
- ډاډ ترلاسه کړئ چې د @BotFather څخه ترلاسه شوې

### د چینل ستونزه:
- ډاډ ترلاسه کړئ چې بوټ د چینل ادمین دی
- ډاډ ترلاسه کړئ چې چینل نوم د @ سره پیل کیږي

### د ژباړې ستونزه:
- د انټرنټ اتصال وګورئ
- د Google Translate د محدودیت انتظار وکړئ

## 6. د فایلونو جوړښت - File Structure

```
telegram_crypto_bot.py    # اصلي کوډ
posted_articles.json      # د لېږل شویو خبرونو ډېټا
crypto_bot.log           # د لاګونو فایل
setup_instructions.md    # دا لارښوونې
```

## 7. د بوټ ځانګړتیاوې - Bot Features

- ✅ د هرو ۱۰ دقیقو څخه وروسته د خبرونو کتنه
- ✅ د انګلیسي څخه پښتو ته ژباړه
- ✅ د تکراري خبرونو مخنیوی
- ✅ د تلیګرام چینل ته اتوماتیک لېږل
- ✅ د زړو ثبتونو اتوماتیک پاکول
- ✅ د Replit سره مطابقت

## 8. د پیغام بڼه - Message Format

```
📰 Bitcoin Reaches New All-Time High
📘 بټ کوین نوي ټولوخت لوړوالي ته رسیږي
🔗 https://cointelegraph.com/news/...
```

## 9. د لاګونو کتنه - Monitoring Logs

د لاګونو کتنه کولی شئ:
- د Replit کنسول کې
- د `crypto_bot.log` فایل کې
- د `/health` endpoint کې

## 10. د بوټ ودرول - Stopping the Bot

Replit کې د "Stop" ټوکي کلیک وکړئ یا `Ctrl+C` واستعمال کړئ.