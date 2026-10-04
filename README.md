# 🎯 Musafir v2: Offline Tourist Guide + SMS Marketing

**World Bank Small AI Hackathon 2026** - Tourism Track

## What It Does

**Musafir** solves a real problem for developing economies:
- **Tourists** get instant answers about safety, pricing, activities (works 100% offline)
- **Local businesses** (restaurants, hotels, guides) market via SMS without paying fees
- **Guides** track their location via GPS
- **All features work offline** - perfect for low connectivity areas

## The Problem It Solves

Tourism hotspots in Pakistan (Hunza, Skardu, Swat) have:
- ❌ No internet for tourists
- ❌ Small businesses can't afford Airbnb/Booking fees (25-30%)
- ❌ Tourists get scammed due to lack of info
- ❌ No way to reach tourists locally

## The Solution

**Musafir** = Offline Guide + Local SMS Marketing

### Tourist Experience
1. Tourist downloads Musafir (one-time with WiFi)
2. Goes offline into mountains
3. Asks: "What's best time to visit Hunza?"
4. Gets instant answer from offline database
5. Receives SMS offers from local restaurants
6. Navigates using offline maps + GPS

### Business Experience
1. Restaurant owner opens Musafir dashboard
2. Creates: "Mama's Kitchen - Fresh trout 800 PKR. GPS: 36.31,74.19"
3. Targets: "Hunza region"
4. Pays: 5 PKR per SMS (~$0.02)
5. SMS sent to tourists via cellular network (NOT internet)

## How It Works (Technical)

```
Frontend (index.html):
- Tourist guide interface
- Offline maps viewer
- SMS marketing dashboard
- GPS tracking
- Business analytics

Backend (app.py):
- Tourist queries → answered from local database
- SMS queue → stores locally, sends when internet
- GPS logging → tracks guides offline
- Dashboard → shows revenue, tourists, etc.

Database (SQLite):
- Tourists table (phone, region, interests)
- SMS queue (pending campaigns)
- GPS tracks (guide locations)
- Queries log (for analytics)

Data (guide_data.json):
- 7 Pakistan destinations
- Prices in USD/PKR
- Activities, discounts
- Safety tips, scam warnings
```

## Demo Script (3 minutes)

### Setup
```bash
cd C:\Users\CG\OneDrive\Desktop\Musafir
pip install -r requirements.txt
python app.py
```

Browser: `http://localhost:8000`

---

### Demo Part 1: Tourist Guide (Offline)
**"WiFi OFF - Tourist asks question"**

1. Go to **🧳 Tourist Guide** tab
2. Select region: **Hunza**
3. Ask: "What are prices in Hunza?"
4. Click **Get Answer**
5. App responds: "Budget: 15 USD/night, Mid-range: 40 USD, Food: 3 USD per meal"

**Key point:** Works 100% offline. No internet needed.

---

### Demo Part 2: SMS Marketing (Local Businesses)
**"Restaurant owner creates SMS campaign"**

1. Go to **📱 SMS Marketing** tab
2. Business Name: "Mama's Kitchen"
3. Region: "Hunza"
4. Message: "Mama's Kitchen - Fresh trout 800 PKR, open til 9pm. GPS: 36.31,74.19"
5. Click **Queue SMS**
6. App shows: "SMS queued for 12 tourists in Hunza. Cost: 60 PKR total"

**Key point:** Restaurants pay 5 PKR per SMS = much cheaper than Airbnb fees.

---

### Demo Part 3: GPS Navigation
**"Tourist navigates using offline maps"**

1. Go to **🗺️ Offline Maps** tab
2. Select destination: "Hunza Valley"
3. Shows: "Hunza Valley - GPS: 36.31, 74.19"
4. Tourist enters GPS in offline map app
5. Phone's built-in GPS guides them there

**Key point:** No internet needed for GPS.

---

### Demo Part 4: Business Dashboard
**"See revenue and tourists"**

1. Go to **📊 Dashboard** tab
2. Click **Refresh Dashboard**
3. Shows:
   - Tourists registered: 12
   - SMS sent: 3
   - Revenue earned: 300 PKR
   - GPS logs: 45

**Key point:** Real business metrics. Real revenue model.

---

## Revenue Model

- **Tourists:** Free app
- **Businesses:** Pay 5 PKR per SMS

### Math
- 100 restaurants in Hunza
- 10 SMS each per day
- 5 PKR per SMS
- **= 5,000 PKR/day = $540/month from ONE region**

Scale to all 7 regions: $3,500+/month

## Why This Wins

✅ **Solves real problem** - tourists safe, businesses earn
✅ **Works offline** - core World Bank requirement
✅ **Global** - works in any developing country
✅ **Revenue model** - not just a demo, real business
✅ **Simple tech** - no AI needed, just smart database
✅ **Existing problem** - SMS marketing exists, we're just repurposing it

## Files

- `app.py` - Backend (FastAPI, SQLite, APIs)
- `index.html` - Frontend (all tabs + interfaces)
- `guide_data.json` - Location database (7 destinations)
- `requirements.txt` - Dependencies
- `README.md` - This file

## Tech Stack

- **Backend:** Python FastAPI
- **Frontend:** HTML/CSS/JavaScript
- **Database:** SQLite (local, works offline)
- **No external APIs needed** - everything runs locally

## To Run

```bash
pip install -r requirements.txt
python app.py
```

Visit: `http://localhost:8000`

---

**Created:** Friday, Oct 1-2, 2026 (44 hours before submission)
**For:** World Bank Small AI Hackathon 2026
**Track:** Tourism
**Category:** Small AI (Offline, Low-Connectivity Solutions)
