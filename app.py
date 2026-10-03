"""
Musafir v2: Offline Tourist Guide + SMS Marketing Platform
World Bank Small AI Hackathon 2026
Complete working backend - 44 hours to submit
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from datetime import datetime
import uuid
import os
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use absolute paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "musafir.db"
HTML_PATH = BASE_DIR / "index.html"
JSON_PATH = BASE_DIR / "guide_data.json"

def init_db():
    """Initialize all database tables."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Tourists table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tourists (
            id TEXT PRIMARY KEY,
            phone TEXT UNIQUE,
            region TEXT,
            interests TEXT,
            registered_at TEXT
        )
    ''')
    
    # SMS marketing queue
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sms_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id TEXT,
            business_name TEXT,
            message TEXT,
            target_region TEXT,
            target_phones TEXT,
            created_at TEXT,
            sent INTEGER DEFAULT 0,
            cost_pkr REAL
        )
    ''')
    
    # GPS tracking for guides
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gps_tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guide_id TEXT,
            guide_name TEXT,
            latitude REAL,
            longitude REAL,
            timestamp TEXT
        )
    ''')
    
    # Tourist queries and responses
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tourist_id TEXT,
            question TEXT,
            region TEXT,
            answer TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

def load_guide_data():
    """Load all location and business data."""
    try:
        with open(str(JSON_PATH), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def search_answer(question, region, guide_data):
    """Find answer from database based on question keywords."""
    question_lower = question.lower()
    answer_parts = []
    
    # Search in location info
    if region in guide_data:
        region_data = guide_data[region]
        
        # Scam/Safety questions
        if any(word in question_lower for word in ["scam", "safe", "danger", "watch out", "fraud", "careful", "warning"]):
            answer_parts.append(f"Safety in {region}:\n{region_data.get('safety_tips', 'Generally safe.')}\n\nScam warnings:\n{region_data.get('scam_warnings', 'Use registered services.')}")
        
        # Price/cost/budget/sleep/accommodation questions
        if any(word in question_lower for word in ["price", "cost", "how much", "budget", "expensive", "cheap", "sleep", "stay", "accommodation", "hotel", "lodge"]):
            accommodation = region_data.get("accommodation", {})
            answer = f"Accommodation in {region}:\n"
            if "budget" in accommodation:
                answer += f"💰 Budget: {accommodation['budget']['price_usd']} USD/night\n"
            if "mid_range" in accommodation:
                answer += f"💰 Mid-range: {accommodation['mid_range']['price_usd']} USD/night\n"
            if "luxury" in accommodation:
                answer += f"💰 Luxury: {accommodation['luxury']['price_usd']} USD/night\n"
            answer += f"\n🍽️ Food per meal: {region_data.get('food_per_meal', {}).get('usd', '?')} USD"
            answer_parts.append(answer)
        
        # Best time/season questions
        if any(word in question_lower for word in ["best time", "season", "weather", "when", "visit", "month", "go", "should i"]):
            answer_parts.append(f"Best Season in {region}:\n✅ Best: {region_data.get('best_season', 'varies')}\n❌ Worst: {region_data.get('worst_season', 'varies')}")
        
        # Activity/trekking/hiking questions
        if any(word in question_lower for word in ["activity", "do", "activities", "trek", "hike", "what to", "things to do", "explore", "trekking"]):
            activities = region_data.get("activities", [])
            if activities:
                answer_parts.append(f"Activities in {region}:\n" + "\n".join([f"• {a}" for a in activities[:5]]))
        
        # Discount questions
        if any(word in question_lower for word in ["discount", "group", "week", "long", "bulk", "offer", "deal", "rate"]):
            discounts = region_data.get("group_discounts", {})
            if discounts:
                answer = f"Discounts in {region}:\n"
                for discount, details in discounts.items():
                    answer += f"• {discount}: {details}\n"
                answer_parts.append(answer)
        
        # If we found answers, return them all
        if answer_parts:
            return "\n\n".join(answer_parts)
    
    # If asking to COMPARE multiple regions
    if any(word in question_lower for word in ["vs", "better", "compare", "which", "both"]):
        answer = "Comparison across regions:\n\n"
        for name, data in list(guide_data.items())[:3]:
            answer += f"{name}: {data.get('best_season', 'varies')} | {data.get('accommodation', {}).get('budget', {}).get('price_usd', '?')} USD (budget)\n"
        return answer
    
    # Search in all regions if not found
    for region_name, data in guide_data.items():
        if region_name in question_lower or region_name.split(',')[0].lower() in question_lower:
            return f"Popular destination: {data.get('name', region_name)}.\nBest season: {data.get('best_season', 'varies')}\nBudget stay: {data.get('accommodation', {}).get('budget', {}).get('price_usd', '?')} USD/night"
    
    return "Ask about: prices, best time to visit, activities, discounts, safety, or scams in any region."

# =====================
# API ENDPOINTS
# =====================

@app.get("/favicon.ico")
def favicon():
    """Handle favicon requests."""
    return {"status": "ok"}

@app.get("/")
def root():
    """Serve main interface."""
    try:
        with open(str(HTML_PATH), "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>App not found</h1>", status_code=404)

@app.post("/api/tourist/register")
def register_tourist(phone: str, region: str, interests: str):
    """Tourist registers to receive SMS."""
    tourist_id = str(uuid.uuid4())[:8]
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO tourists (id, phone, region, interests, registered_at) VALUES (?, ?, ?, ?, ?)',
            (tourist_id, phone, region, interests, datetime.now().isoformat())
        )
        conn.commit()
    except:
        return {"status": "already registered"}
    finally:
        conn.close()
    
    return {"tourist_id": tourist_id, "status": "registered for SMS in " + region}

@app.get("/api/guide")
def guide_query(question: str, region: str):
    """Tourist asks question about region - NO INTERNET NEEDED."""
    guide_data = load_guide_data()
    answer = search_answer(question, region, guide_data)
    
    # Log query
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO queries (tourist_id, question, region, answer, timestamp) VALUES (?, ?, ?, ?, ?)',
        ("anonymous", question, region, answer, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    
    return {
        "question": question,
        "region": region,
        "answer": answer,
        "offline": True
    }

@app.post("/api/business/create-sms")
def business_create_sms(business_name: str, message: str, target_region: str, cost_pkr: float = 5.0):
    """Business creates SMS marketing message (queues locally, sends when online)."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Get all tourist phones in target region
    cursor.execute('SELECT phone FROM tourists WHERE region = ?', (target_region,))
    phones = [row[0] for row in cursor.fetchall()]
    
    if not phones:
        conn.close()
        return {"status": "no tourists in region", "messages_queued": 0}
    
    # Create SMS queue entry
    cursor.execute(
        '''INSERT INTO sms_queue (business_id, business_name, message, target_region, target_phones, created_at, cost_pkr)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (str(uuid.uuid4())[:8], business_name, message, target_region, json.dumps(phones), datetime.now().isoformat(), cost_pkr * len(phones))
    )
    conn.commit()
    conn.close()
    
    return {
        "status": "SMS queued",
        "business": business_name,
        "region": target_region,
        "phones_targeted": len(phones),
        "message": message,
        "total_cost_pkr": cost_pkr * len(phones),
        "note": "Ready to send when business has internet"
    }

@app.get("/api/sms/queue")
def get_sms_queue():
    """Get pending SMS queue (for business to see what's ready to send)."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('SELECT business_name, message, target_region, target_phones, cost_pkr FROM sms_queue WHERE sent = 0')
    queued = cursor.fetchall()
    conn.close()
    
    return {
        "pending_sms": len(queued),
        "messages": [
            {
                "business": msg[0],
                "message": msg[1],
                "region": msg[2],
                "phones_to_send": len(json.loads(msg[3])),
                "cost_pkr": msg[4]
            }
            for msg in queued
        ],
        "note": "Send these SMS when you have internet via SMS gateway"
    }

@app.post("/api/sms/sync")
def sync_sms():
    """Mark SMS as sent (simulates sending when internet returns)."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('UPDATE sms_queue SET sent = 1 WHERE sent = 0')
    rows = cursor.rowcount
    conn.commit()
    conn.close()
    
    return {
        "status": "SMS synced and ready to send",
        "total_messages_synced": rows,
        "next_step": "Use SMS gateway to send queued messages to tourists"
    }

@app.post("/api/gps/track")
def track_guide(guide_id: str, guide_name: str, latitude: float, longitude: float):
    """Log guide's GPS location (works offline)."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO gps_tracks (guide_id, guide_name, latitude, longitude, timestamp) VALUES (?, ?, ?, ?, ?)',
        (guide_id, guide_name, latitude, longitude, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    
    return {"status": "GPS logged", "guide": guide_name, "location": f"{latitude}, {longitude}"}

@app.get("/api/dashboard")
def dashboard():
    """Business dashboard - see SMS sent, tourists registered, revenue."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM tourists')
    total_tourists = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM sms_queue WHERE sent = 1')
    sms_sent = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(cost_pkr) FROM sms_queue WHERE sent = 1')
    revenue = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) FROM gps_tracks')
    total_gps_logs = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_tourists_registered": total_tourists,
        "sms_sent": sms_sent,
        "revenue_earned_pkr": revenue,
        "gps_logs": total_gps_logs,
        "offline": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/locations")
def get_all_locations():
    """Get all location data for offline maps."""
    guide_data = load_guide_data()
    return {
        "locations": {name: {"lat": data.get("lat"), "lng": data.get("lng"), "name": data.get("name")} 
                      for name, data in guide_data.items()},
        "offline": True
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Musafir v2...")
    print("Running at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
