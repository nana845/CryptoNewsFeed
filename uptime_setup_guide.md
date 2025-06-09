# د UptimeRobot د ژوندي ساتلو سیسټم لارښوونې
# UptimeRobot Keep-Alive System Guide

## 1. د بوټ د 24/7 فعالیت لپاره تنظیمات - Bot Configuration for 24/7 Activity

### ✅ د Replit Environment Variables تنظیم کول:

Replit کې د "Secrets" برخې ته ولاړ شئ او دا دوه متغیرونه اضافه کړئ:

```
BOT_TOKEN = your_actual_telegram_bot_token
CHANNEL_ID = @YourActualChannelUsername
```

⚠️ **مهم**: د `@MyCryptoNewsChannel` پر ځای د خپل ریښتیني چینل username ورکړئ!

---

## 2. د UptimeRobot سره د نظارت تنظیم - UptimeRobot Monitoring Setup

### ✅ ستاسو د Replit URL:
```
https://your-repl-name--your-username.replit.app
```

### ✅ د UptimeRobot تنظیمات:
- **Monitor Type**: HTTP(s)
- **URL**: ستاسو د replit URL
- **Monitoring Interval**: 5 minutes
- **Keyword Monitoring**: "Bot is Running!" (اختیاري)

---

## 3. د Web Server معلومات - Web Server Information

### د موجودو Endpoints:

1. **اصلي پاڼه - Main Page**: `/`
   - د بوټ د حالت ښودنه
   - د UptimeRobot لپاره مناسب

2. **روغتیا کتنه - Health Check**: `/health`
   - JSON ځواب
   - د بوټ د فعالیت تصدیق

3. **پینګ - Ping**: `/ping`
   - ساده JSON ځواب
   - د UptimeRobot لپاره بریښنايي

4. **احصایې - Statistics**: `/stats`
   - د لېږل شویو خبرونو شمیر
   - د ډېټابیس معلومات

---

## 4. د کوډ جوړښت - Code Structure

```
├── main.py                 # اصلي فایل
├── keep_alive.py          # د ژوندي ساتلو سیسټم
├── bot.py                 # د بوټ لاجیک
├── config.py              # تنظیمات
├── rss_fetcher.py         # د RSS اخیستل
├── storage.py             # د ډېټا ساتنه
└── templates/
    └── index.html         # د ویب پاڼې ټیمپلیټ
```

---

## 5. د بوټ ازمویل - Bot Testing

### د لومړي ځل لپاره:

1. ډاډ ترلاسه کړئ چې `BOT_TOKEN` سمه ده
2. ډاډ ترلاسه کړئ چې `CHANNEL_ID` د @ سره پیل کیږي
3. د بوټ د چینل ادمین جوړول ضروری دي
4. د "Post Messages" اجازه ورکړئ

### د ګرځنده توګه ازمویل:

```bash
# د محلي ازمویلو لپاره
python keep_alive.py
```

---

## 6. د عادي ستونزو حل - Troubleshooting

### د 400 Bad Request تیروتنه:
- د `CHANNEL_ID` سمتوب وګورئ
- ډاډ ترلاسه کړئ چې بوټ د چینل ادمین دی
- د چینل د عامه یا شخصي کیدو کتنه وکړئ

### د Flask Port Conflict:
- keep_alive.py: پورټ 8080
- main.py: پورټ 3000 (اصلي Flask)
- د Replit اصلي URL: پورټ 5000

### د UptimeRobot نه ځواب:
- د URL سمتوب وګورئ
- د Replit د دومین فعالیت وکتلئ
- د 5 دقیقو د پروسې انتظار وکړئ

---

## 7. د بریالیتوب نښې - Success Indicators

### د بوټ سمه کار:
```
✅ د ژوندي ساتلو سیسټم فعال شو
✅ Flask سرور په شالید کې پیل شو  
✅ د کریپټو خبرونو نظارت فعال دی
✅ بریالیتوب سره X خبرونه ولېږل شول
```

### د ویب سایټ د فعالیت نښې:
```
✅ Bot is Running!
✅ Crypto news monitoring active
✅ UptimeRobot ready for monitoring
```

---

## 8. د UptimeRobot تنظیمات - UptimeRobot Configuration

### د نظارت ډولونه:

1. **HTTP Monitor**:
   - URL: `https://your-repl-name--username.replit.app`
   - Method: GET
   - Interval: 5 minutes

2. **Keyword Monitor** (اختیاري):
   - Keyword: "Bot is Running!"
   - یا: "alive"

3. **Port Monitor** (اختیاري):
   - Port: 8080
   - Protocol: HTTP

---

## 9. د لاګونو کتنه - Log Monitoring

### د بوټ د فعالیت نښې:
```bash
# د کریپټو خبرونو کتنه
INFO - Checking for new crypto news...

# د RSS بریالیتوب
INFO - Successfully fetched X articles

# د پیغام لېږل
INFO - Successfully posted: Article Title...

# د ژوندي ساتلو سیسټم
INFO - Keep-alive system activated
```

---

## 10. د عملي کولو لارښوونې - Implementation Steps

### A. د Replit کې:
1. دا کوډ د خپل repl کې واچوئ
2. د Secrets کې BOT_TOKEN او CHANNEL_ID اضافه کړئ
3. Run ټوکي کلیک کړئ

### B. د UptimeRobot کې:
1. نوی monitor جوړ کړئ
2. د خپل repl URL ورکړئ
3. د 5 دقیقو interval ټاکئ
4. Save کړئ

### C. د چینل کې:
1. د خپل بوټ @username ومومئ
2. د چینل ته یې د admin په توګه اضافه کړئ
3. د "Post Messages" اجازه ورکړئ

---

✅ **پایله**: ستاسو بوټ اوس 24/7 فعال پاتې کیږي او د UptimeRobot لخوا نظارت کیږي!