# د UptimeRobot د 24/7 فعالیت لپاره بشپړ لارښوونې
# Complete UptimeRobot Setup Guide for 24/7 Activity

## 1. د Environment Variables تنظیم - Environment Variables Setup

### د Replit کې د Secrets اضافه کول:

```bash
# د Secrets tab کې دا متغیرونه اضافه کړئ:
BOT_TOKEN = 7406620776:AAGL4W9WcQePvTBmfff-CxoElGnZdIofogg
CHANNEL_ID = crayptonews
```

⚠️ **مهم نکته**: د channel ID یوازې نوم (crayptonews) ورکړئ، د @ یا https://t.me/ پرته

---

## 2. د تلیګرام چینل تنظیمات - Telegram Channel Setup

### د بوټ د چینل ته اضافه کول:

1. د خپل تلیګرام چینل ته ولاړ شئ
2. Channel Settings > Administrators ته ولاړ شئ
3. "Add Admin" کلیک کړئ
4. `@CoinFlashNewsBot` ولټوئ
5. بوټ ته دا اجازې ورکړئ:
   - ✅ Post Messages
   - ✅ Edit Messages
   - ❌ Delete Messages (اختیاري)

---

## 3. د UptimeRobot Monitor جوړول - UptimeRobot Monitor Creation

### د Replit URL موندل:

```
https://[your-repl-name]--[your-username].replit.app
```

### د UptimeRobot کې د Monitor تنظیمات:

```
Monitor Type: HTTP(s)
Friendly Name: Crypto News Bot
URL/IP: https://[your-repl-name]--[your-username].replit.app
Monitoring Interval: 5 minutes
HTTP Method: GET
Keyword Monitoring: "Bot is Running!" (اختیاري)
```

---

## 4. د Web Server Endpoints معلومات - Web Server Endpoints Information

### موجود Endpoints:

| Endpoint | وضیفه | د UptimeRobot لپاره |
|----------|-------|-------------------|
| `/` | اصلي پاڼه | ✅ غوره |
| `/health` | روغتیا کتنه | ✅ غوره |
| `/ping` | ساده ping | ✅ د UptimeRobot لپاره |
| `/stats` | احصایې | ❌ د نظارت لپاره نه |

---

## 5. د بوټ د فعالیت تصدیق - Bot Activity Verification

### د سمون نښې:

```bash
# د logs کتنه:
✅ "د بوټ تنظیمات تصدیق شول - Bot configuration validated"
✅ "Flask سرور د UptimeRobot لپاره پیل شو"
✅ "بریالیتوب سره X خبرونه واخیستل شول"
✅ "خبر بریالیتوب سره ولېږل شو"
```

### د ستونزو نښې:

```bash
# د logs کتنه:
❌ "400 Client Error: Bad Request"
❌ "BOT_TOKEN نه دی ورکړل شوی"
❌ "CHANNEL_ID نه دی ورکړل شوی"
```

---

## 6. د عادي ستونزو حل - Common Issues Solutions

### د 400 Bad Request حل:

```bash
# د channel نوم د @ پرته ورکړئ:
CHANNEL_ID = crayptonews  # ✅ سم
CHANNEL_ID = @crayptonews  # ❌ غلط

# یا د بشپړ URL پرته:
CHANNEL_ID = https://t.me/crayptonews  # ❌ غلط
```

### د بوټ د چینل Permissions:

1. بوټ باید د چینل Admin وي
2. "Post Messages" اجازه ورکړل شوې وي
3. چینل باید Public وي یا بوټ member وي

---

## 7. د UptimeRobot د Monitor تنظیمات - UptimeRobot Monitor Settings

### بهترین تنظیمات:

```json
{
  "monitor_type": "HTTP(s)",
  "url": "https://your-repl--username.replit.app/ping",
  "interval": 300,
  "timeout": 30,
  "keyword": "alive",
  "alert_contacts": ["your-email@example.com"]
}
```

### د Alert تنظیمات:

- **Down Alert**: د 2 ناکامیو وروسته
- **Up Alert**: د بیا فعالیت سره سمدلاسه
- **Email Notifications**: فعال
- **SMS Notifications**: اختیاري

---

## 8. د کارکرد ازمویل - Performance Testing

### د Manual ازمویلو لارې:

```bash
# د health check:
curl https://your-repl--username.replit.app/health

# د ping:
curl https://your-repl--username.replit.app/ping

# د stats:
curl https://your-repl--username.replit.app/stats
```

### موڅنه Response:

```json
{
  "status": "healthy",
  "message": "د کریپټو خبرونو بوټ فعال دی",
  "timestamp": "2025-06-09T00:00:00.000000",
  "uptime_ready": true
}
```

---

## 9. د فایلونو جوړښت - File Structure

```
├── crypto_bot_main.py      # اصلي بوټ فایل
├── posted_articles.json    # د لېږل شویو خبرونو ډېټا
├── crypto_bot.log         # د logs فایل
├── keep_alive.py          # د ژوندي ساتلو سیسټم (زاړه)
└── UptimeRobot_Setup_Guide.md  # دا لارښوونې
```

---

## 10. د بریالیتوب ټولګه - Success Checklist

### ✅ د بشپړیدو لیست:

- [ ] BOT_TOKEN په Secrets کې ورکړل شوی
- [ ] CHANNEL_ID په Secrets کې ورکړل شوی
- [ ] بوټ د چینل Admin جوړ شوی
- [ ] د "Post Messages" اجازه ورکړل شوې
- [ ] Replit بوټ run کوي
- [ ] د Web Server port 5000 فعال دی
- [ ] UptimeRobot monitor جوړ شوی
- [ ] د 5 دقیقو interval تنظیم شوی
- [ ] Alert contacts اضافه شوي

### د بریالیتوب وروستي ازمونه:

1. د Replit کنسول کې د logs کتنه
2. د Web browser کې د URL کتنه
3. د UptimeRobot dashboard کتنه
4. د تلیګرام چینل کې د خبرونو انتظار (۱۰ دقیقې)

---

## 11. د روزانه ساتنې لارښوونې - Daily Maintenance Guide

### هره ورځ:

- [ ] د UptimeRobot alerts کتنه
- [ ] د Replit workflow status کتنه
- [ ] د چینل کې د نویو خبرونو کتنه

### هره اونۍ:

- [ ] د logs فایل کتنه
- [ ] د posted_articles.json cleanup
- [ ] د bot د performance کتنه

### هره میاشت:

- [ ] د UptimeRobot statistics کتنه
- [ ] د RSS feed د فعالیت کتنه
- [ ] د translation service ازمونه

---

## 🎯 پایله - Final Result

ستاسو Crypto News Bot اوس:

✅ د Cointelegraph څخه خبرونه اخلي
✅ انګلیسي څخه پښتو ته ژباړي
✅ بیلابیل ژبو کې پوسټ کوي
✅ د تکرار څخه مخنیوی کوي
✅ هره ۱۰ دقیقې کتنه کوي
✅ د UptimeRobot سره 24/7 فعال پاتې کیږي

**د UptimeRobot URL**: `https://your-repl--username.replit.app/ping`