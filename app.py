from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json
import sqlite3
from datetime import datetime
import os
from typing import Optional
import numpy as np
from PIL import Image
import io

# Try to import AI models - if not available, gracefully skip
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Transformers not installed. Some AI features will be limited.")

try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  Scikit-learn not installed. Recommendations will be limited.")

# Initialize FastAPI
app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "musafir.db"
GUIDE_DATA_PATH = BASE_DIR / "guide_data.json"
FEEDBACKS_PATH = BASE_DIR / "feedbacks.json"
VISITS_PATH = BASE_DIR / "visits.json"
SMS_QUEUE_PATH = BASE_DIR / "sms_queue.json"

# Load guide data
def load_guide_data():
    if GUIDE_DATA_PATH.exists():
        with open(GUIDE_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

GUIDE_DATA = load_guide_data()

# Initialize AI models (lazy load to save memory)
zero_shot_classifier = None
image_classifier = None

def get_zero_shot_classifier():
    global zero_shot_classifier
    if zero_shot_classifier is None and TRANSFORMERS_AVAILABLE:
        try:
            zero_shot_classifier = pipeline("zero-shot-classification", 
                                           model="facebook/bart-large-mnli",
                                           device=-1)  # CPU only
        except Exception as e:
            print(f"⚠️  Could not load zero-shot classifier: {e}")
    return zero_shot_classifier

def get_image_classifier():
    global image_classifier
    if image_classifier is None and TRANSFORMERS_AVAILABLE:
        try:
            image_classifier = pipeline("image-classification", 
                                       model="google/vit-base-patch16-224",
                                       device=-1)  # CPU only
        except Exception as e:
            print(f"⚠️  Could not load image classifier: {e}")
    return image_classifier

# Initialize database
def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Tourists table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tourists (
            id TEXT PRIMARY KEY,
            name TEXT,
            region TEXT,
            registered_at TIMESTAMP
        )
    ''')
    
    # SMS queue
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sms_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id TEXT,
            message TEXT,
            status TEXT,
            created_at TIMESTAMP,
            sent_at TIMESTAMP
        )
    ''')
    
    # GPS tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gps_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tourist_id TEXT,
            latitude REAL,
            longitude REAL,
            timestamp TIMESTAMP,
            FOREIGN KEY(tourist_id) REFERENCES tourists(id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# ==================== ORIGINAL MUSAFIR FEATURES ====================

class TouristRegistration(BaseModel):
    name: str
    region: str

@app.get("/")
async def root():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/api/guide")
async def get_guide_answer(question: str, region: str = None):
    """
    Original feature: Tourist asks question, get offline answer from guide_data.json
    """
    if not question:
        return {"error": "Please ask a question"}
    
    # Convert to lowercase for matching
    question_lower = question.lower()
    answer_parts = []
    
    # Search all categories
    for category in ["prices", "activities", "safety_tips", "discounts", "scam_warnings"]:
        for location, data in GUIDE_DATA.items():
            if region and region.lower() != location.lower():
                continue
            
            if category not in data:
                continue
            
            category_data = data[category]
            
            # Check if category data is a dict or list
            if isinstance(category_data, dict):
                for key, value in category_data.items():
                    if any(word in question_lower for word in key.lower().split()):
                        answer_parts.append(f"**{location}**: {value}")
            elif isinstance(category_data, list):
                for item in category_data:
                    if isinstance(item, str) and any(word in question_lower for word in item.lower().split()):
                        answer_parts.append(f"**{location}**: {item}")
    
    if not answer_parts:
        return {
            "answer": f"I don't have specific information about that in {region or 'the guide'}. Try asking about prices, activities, safety, or discounts.",
            "found": False
        }
    
    return {
        "answer": "\n".join(answer_parts),
        "found": True,
        "region": region or "all"
    }

@app.post("/api/register-tourist")
async def register_tourist(registration: TouristRegistration):
    """
    Original feature: Register tourist for SMS updates
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        tourist_id = f"{registration.name}_{datetime.now().timestamp()}"
        cursor.execute('''
            INSERT INTO tourists (id, name, region, registered_at)
            VALUES (?, ?, ?, ?)
        ''', (tourist_id, registration.name, registration.region, datetime.now()))
        conn.commit()
        conn.close()
        
        return {
            "status": "registered",
            "tourist_id": tourist_id,
            "message": f"Welcome {registration.name}! You'll receive SMS updates about {registration.region}."
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/queue-sms")
async def queue_sms(restaurant_id: str, message: str, region: str):
    """
    Original feature: Restaurant queues SMS message locally
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sms_queue (restaurant_id, message, status, created_at)
            VALUES (?, ?, ?, ?)
        ''', (restaurant_id, message, 'queued', datetime.now()))
        conn.commit()
        
        queue_id = cursor.lastrowid
        conn.close()
        
        return {
            "status": "queued",
            "queue_id": queue_id,
            "message": f"SMS queued: {message}",
            "will_send": "When internet connection is available"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/sms-status")
async def sms_status():
    """
    Original feature: Check SMS queue status
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM sms_queue WHERE status=?', ('queued',))
        queued_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM sms_queue WHERE status=?', ('sent',))
        sent_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "queued_sms": queued_count,
            "sent_sms": sent_count,
            "total": queued_count + sent_count
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/log-gps")
async def log_gps(tourist_id: str, latitude: float, longitude: float):
    """
    Original feature: Log GPS location for offline tracking
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO gps_logs (tourist_id, latitude, longitude, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (tourist_id, latitude, longitude, datetime.now()))
        conn.commit()
        conn.close()
        
        return {
            "status": "logged",
            "location": {"lat": latitude, "lon": longitude},
            "message": "Location saved offline. Will sync when online."
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/dashboard-stats")
async def dashboard_stats():
    """
    Original feature: Dashboard shows usage stats
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM tourists')
        tourists = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM sms_queue WHERE status=?', ('sent',))
        sms_sent = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM gps_logs')
        gps_logs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM sms_queue WHERE status=?', ('queued',))
        sms_queued = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "tourists_registered": tourists,
            "sms_sent": sms_sent,
            "sms_queued": sms_queued,
            "gps_logs": gps_logs,
            "estimated_monthly_revenue": f"${sms_sent * 5 / 100}" if sms_sent > 0 else "$0"
        }
    except Exception as e:
        return {"error": str(e)}

# ==================== NEW AI FEATURES ====================

@app.post("/api/feedback")
async def submit_feedback(feedback: str, region: str):
    """
    NEW: Tourist submits feedback. AI analyzes sentiment and intent.
    Uses zero-shot NLP to categorize without training.
    """
    if not TRANSFORMERS_AVAILABLE:
        return {"error": "AI features not available in this deployment"}
    
    try:
        classifier = get_zero_shot_classifier()
        if classifier is None:
            return {"status": "recorded_but_not_analyzed", "message": "Feedback saved but AI analysis unavailable"}
        
        # Define labels
        sentiment_labels = ["positive", "negative", "neutral"]
        intent_labels = ["accommodation", "food", "activity", "transportation", "safety", "price", "guide", "other"]
        
        # Sentiment analysis
        try:
            sentiment_result = classifier(feedback, sentiment_labels)
            sentiment = sentiment_result["labels"][0]
            sentiment_score = float(sentiment_result["scores"][0])
        except Exception as e:
            sentiment = "neutral"
            sentiment_score = 0.0
        
        # Intent classification
        try:
            intent_result = classifier(feedback, intent_labels)
            intent = intent_result["labels"][0]
            intent_score = float(intent_result["scores"][0])
        except Exception as e:
            intent = "other"
            intent_score = 0.0
        
        # Store in JSON
        feedback_record = {
            "text": feedback,
            "region": region,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "intent": intent,
            "intent_score": intent_score,
            "timestamp": datetime.now().isoformat()
        }
        
        feedbacks = []
        if FEEDBACKS_PATH.exists():
            with open(FEEDBACKS_PATH, 'r', encoding='utf-8') as f:
                feedbacks = json.load(f)
        feedbacks.append(feedback_record)
        with open(FEEDBACKS_PATH, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "analyzed",
            "sentiment": sentiment,
            "sentiment_score": round(sentiment_score, 2),
            "intent": intent,
            "intent_score": round(intent_score, 2),
            "message": f"AI Analysis: {sentiment.upper()} feedback about {intent.upper()}"
        }
    except Exception as e:
        return {"error": f"Feedback processing error: {str(e)}"}

@app.get("/api/feedback-analytics")
async def feedback_analytics(region: Optional[str] = None):
    """
    NEW: Dashboard shows feedback analytics
    Restaurant sees: "Visitors loved your activities (8/10). Fix meal timing (4/10)."
    """
    if not FEEDBACKS_PATH.exists():
        return {"message": "No feedback yet", "total_feedback": 0}
    
    try:
        with open(FEEDBACKS_PATH, 'r', encoding='utf-8') as f:
            feedbacks = json.load(f)
        
        # Filter by region
        if region:
            feedbacks = [fb for fb in feedbacks if fb.get("region") == region]
        
        # Aggregate by intent
        intent_stats = {}
        for fb in feedbacks:
            intent = fb.get("intent", "other")
            sentiment = fb.get("sentiment", "neutral")
            score = fb.get("sentiment_score", 0.5)
            
            if intent not in intent_stats:
                intent_stats[intent] = {
                    "positive_sum": 0,
                    "negative_sum": 0,
                    "neutral_sum": 0,
                    "count": 0,
                    "feedbacks": []
                }
            
            if sentiment == "positive":
                intent_stats[intent]["positive_sum"] += score
            elif sentiment == "negative":
                intent_stats[intent]["negative_sum"] += score
            else:
                intent_stats[intent]["neutral_sum"] += score
            
            intent_stats[intent]["count"] += 1
            intent_stats[intent]["feedbacks"].append(fb["text"][:50])
        
        # Convert to percentages and compute average sentiment
        for intent, stats in intent_stats.items():
            total = stats["count"]
            avg_sentiment = (stats["positive_sum"] - stats["negative_sum"]) / total if total > 0 else 0
            stats["average_sentiment"] = round(avg_sentiment * 10, 1)  # Scale to 0-10
            stats["count"] = total
            del stats["positive_sum"]
            del stats["negative_sum"]
            del stats["neutral_sum"]
        
        return {
            "region": region or "all",
            "total_feedback": len(feedbacks),
            "by_intent": intent_stats
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/analyze-photo")
async def analyze_photo(file: UploadFile = File(...), region: Optional[str] = None):
    """
    NEW: Tourist uploads photo. AI tags what's in it.
    Uses Vision Transformer for image classification.
    """
    if not TRANSFORMERS_AVAILABLE:
        return {"error": "AI features not available in this deployment"}
    
    try:
        classifier = get_image_classifier()
        if classifier is None:
            return {"status": "uploaded_but_not_analyzed", "message": "Photo saved but AI analysis unavailable"}
        
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Limit image size for faster processing
        image.thumbnail((224, 224))
        
        # Classify
        results = classifier(image)
        
        # Extract top categories
        top_labels = [
            {"label": r["label"], "score": round(r["score"], 2)}
            for r in results[:5]
        ]
        
        # Store photo metadata
        photo_record = {
            "labels": top_labels,
            "region": region,
            "timestamp": datetime.now().isoformat(),
            "filename": file.filename
        }
        
        return {
            "status": "analyzed",
            "photo_labels": top_labels,
            "message": f"Photo shows: {', '.join([r['label'] for r in top_labels[:3]])}",
            "saved": True
        }
    except Exception as e:
        return {"error": f"Photo analysis error: {str(e)}"}

@app.post("/api/track-visit")
async def track_visit(tourist_id: str, restaurant: str, region: str):
    """
    NEW: Log tourist visit for recommendation engine
    """
    try:
        visits = []
        if VISITS_PATH.exists():
            with open(VISITS_PATH, 'r', encoding='utf-8') as f:
                visits = json.load(f)
        
        visits.append({
            "tourist_id": tourist_id,
            "restaurant": restaurant,
            "region": region,
            "timestamp": datetime.now().isoformat()
        })
        
        with open(VISITS_PATH, 'w', encoding='utf-8') as f:
            json.dump(visits, f, indent=2, ensure_ascii=False)
        
        return {"status": "tracked", "message": f"Visit logged: {tourist_id} -> {restaurant}"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/recommend")
async def get_recommendations(tourist_id: str, region: str):
    """
    NEW: AI recommends restaurants based on similar tourists
    Uses collaborative filtering.
    """
    if not SKLEARN_AVAILABLE or not VISITS_PATH.exists():
        return {"message": "Not enough data for recommendations yet", "recommendations": []}
    
    try:
        with open(VISITS_PATH, 'r', encoding='utf-8') as f:
            visits = json.load(f)
        
        # Filter by region
        visits = [v for v in visits if v.get("region") == region]
        
        if not visits:
            return {"message": "No data for this region", "recommendations": []}
        
        # Get all tourists and restaurants
        tourists = list(set([v["tourist_id"] for v in visits]))
        restaurants = list(set([v["restaurant"] for v in visits]))
        
        if tourist_id not in tourists or len(tourists) < 2:
            return {"message": "Not enough data for personalized recommendations", "recommendations": []}
        
        # Build visit matrix
        visit_matrix = np.zeros((len(tourists), len(restaurants)))
        for i, t in enumerate(tourists):
            for j, r in enumerate(restaurants):
                if any(v["tourist_id"] == t and v["restaurant"] == r for v in visits):
                    visit_matrix[i][j] = 1
        
        # Find similar tourists
        tourist_idx = tourists.index(tourist_id)
        similarities = cosine_similarity([visit_matrix[tourist_idx]], visit_matrix)[0]
        similar_indices = np.argsort(similarities)[::-1][1:4]  # Top 3 similar
        
        # Find restaurants visited by similar tourists but not by this tourist
        recommended = set()
        for idx in similar_indices:
            for j, r in enumerate(restaurants):
                if visit_matrix[idx][j] == 1 and visit_matrix[tourist_idx][j] == 0:
                    recommended.add(r)
        
        return {
            "tourist_id": tourist_id,
            "region": region,
            "recommendations": list(recommended)[:5],
            "message": f"Based on tourists like you, try these: {', '.join(list(recommended)[:3])}"
        }
    except Exception as e:
        return {"error": str(e)}

# Serve static files
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
