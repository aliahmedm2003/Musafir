# 🎯 Musafir v3: Offline Tourism AI

**World Bank Small AI for Development Hackathon 2026** - Tourism Track

## 🎬 Demo & Links

- **📹 Demo Video:** https://youtu.be/LzlBthMRsTc
- **🌐 Live App:** https://musafir-production-d005.up.railway.app
- **💻 GitHub:** https://github.com/aliahmedm2003/musafir

---

## 📋 Quick Pitch

**Problem:** Tourists in developing countries get scammed. Small tourism operators don't understand what visitors value. Mountain regions have zero internet.

**Solution:** Musafir connects tourists and tourism operators offline using AI.

**Tourists get:**
- Instant answers about prices, safety, activities (Offline Guide)
- AI feedback analysis showing what's trending (Sentiment NLP)
- AI photo tagging of their experiences (Vision Transformer)
- Smart restaurant recommendations based on visitor behavior (Collaborative Filtering)

**Operators get:**
- SMS marketing that works offline (queue locally, send when online)
- Dashboard showing what tourists value (feedback analytics)
- Dashboard showing seasonal trends (photo analysis)
- Visitor insights for business decisions

**Revenue Model:**
- Primary: SMS commission (5 PKR/SMS charged, 3 PKR gateway = 2 PKR margin)
- Secondary: Premium dashboard (1,000 PKR/month)
- Tertiary: White-label for tour operators (50,000 PKR/month)

**Year 1 realistic:** 5-8M PKR (~$17-28K)

---

## 🤖 What's the AI?

### 1. **Zero-Shot NLP for Feedback Analysis** (BART)
Tourist feedback → AI classifies sentiment (positive/negative/neutral) + intent (food/activity/accommodation/price/safety)
No labeled training data needed. Works offline.

### 2. **Vision Transformer for Photo Classification** (ViT)
Tourist uploads photo → AI tags contents (food, activity, landscape, people, etc.)
Helps operators see what tourists photograph most (market signal).

### 3. **Collaborative Filtering for Recommendations**
Tracks which tourists visit which restaurants → AI finds patterns → Recommends places to tourists based on similar visitors.

---

## 🚀 Quick Start

### Local Testing
```bash
pip install -r requirements.txt
python app.py
# Visit http://localhost:8000
```

### Deploy to Railway
```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login and link project
railway login
railway link

# 3. Deploy
git push

# 4. Check logs
railway logs
```

---

## 📊 Features

| Feature | Status | AI? | Offline? |
|---------|--------|-----|----------|
| Tourist Guide (Q&A) | ✅ | Keyword matching (NLP) | ✅ |
| SMS Marketing | ✅ | No | Queue locally, send online |
| Feedback Analysis | ✅ | Zero-shot NLP (BART) | Works offline |
| Photo Tagging | ✅ | Vision Transformer | Works offline |
| Recommendations | ✅ | Collaborative filtering | Works offline |
| Dashboard | ✅ | Aggregation | ✅ |
| GPS Tracking | ✅ | No | ✅ |

---

## 📁 File Structure

```
musafir/
├── app.py                 # FastAPI backend (all routes)
├── index.html            # Full frontend (6 tabs)
├── guide_data.json       # 7 Pakistan regions (prices, activities, safety, scams, discounts)
├── requirements.txt      # Dependencies
├── Procfile              # Railway deployment
├── musafir.db           # SQLite (auto-created)
├── feedbacks.json       # Tourist feedback (auto-created)
├── visits.json          # Visit tracking (auto-created)
└── README.md            # This file
```

---

## 📱 Tabs Overview

### Tab 1: Tourist Guide
- Ask questions about destinations
- Get offline answers from guide_data.json
- Filter by region

### Tab 2: SMS Marketing
- Register as tourist for SMS updates
- Queue SMS campaigns (restaurants)
- Check SMS queue status

### Tab 3: Feedback AI ⭐ NEW
- Tourists submit feedback
- AI analyzes sentiment + intent
- Dashboard shows analytics by intent

### Tab 4: Photo Analysis ⭐ NEW
- Upload photos
- AI tags contents
- See what tourists photograph

### Tab 5: Recommendations ⭐ NEW
- Log visits to restaurants
- Get recommendations based on similar tourists
- Collaborative filtering

### Tab 6: Dashboard
- Real-time stats
- Revenue tracking
- Engagement metrics

---

## 🎥 Video Script (2-5 min)

### Problem Statement (10 sec)
"Because of Musafir, Noor will understand what tourists value (via NLP sentiment analysis), see what visitors photograph (via computer vision), and recommend new experiences (via collaborative filtering)—all offline—rather than guessing; we know because pattern recognition is the World Bank's endorsed use case for low-resource AI."

### AI Capabilities (30 sec)
"Musafir uses three AI models:

1. **Zero-shot NLP** (BART) to analyze visitor feedback without labeled data
2. **Vision Transformer** (ViT) to classify tourist photos and identify interests
3. **Collaborative filtering** to recommend restaurants based on visitor behavior

Why not simpler tools? SMS can't analyze meaning. Photos can't tag themselves. A spreadsheet can't find patterns across tourists. AI does all three—and all work offline."

### Tool Demo (60 sec)
1. Tourist leaves feedback: "Food was amazing but service was slow" → AI shows: **POSITIVE about FOOD, NEGATIVE about SERVICE**
2. Tourist uploads photo → AI tags: **POTTERY, HANDICRAFT, FOOD** → Dashboard shows restaurants visitors photograph most
3. Recommendation engine shows: "Tourists like you also visited XYZ restaurant" → Noor gets personalized leads

### Challenge/Gap (20 sec)
"Tourism is a major job creator in developing economies, but small operators run on instinct. They know visitors leave happy, but not why, not which parts of the experience are worth building on. Musafir closes that gap with AI that learns from offline data."

### Your Take (20 sec)
"Localizing AI means using small, offline models that learn from local behavior. We're not building for Silicon Valley servers—we're building for village smartphones. That means respecting bandwidth, battery, and trust. These tourists don't have consistent internet, but they have smartphones. Musafir works on the devices people actually have."

---

## 🔧 Tech Stack

- **Backend:** FastAPI + Python
- **AI/ML:** 
  - Transformers (BART for zero-shot NLP)
  - Vision Transformer (google/vit-base-patch16-224)
  - Scikit-learn (cosine similarity for recommendations)
- **Database:** SQLite + JSON files
- **Frontend:** Vanilla JavaScript + HTML/CSS
- **Deployment:** Railway (auto-deploys from GitHub)

---

## 📊 Data Flow

```
Tourist Feedback 
    ↓
[BART NLP] → Sentiment + Intent
    ↓
analytics.json
    ↓
Restaurant Dashboard → Insights

Tourist Photo
    ↓
[Vision Transformer] → Tags (food, activity, etc.)
    ↓
photo_metadata.json
    ↓
Dashboard → What tourists photograph

Tourist Visits
    ↓
[Collaborative Filtering] → Similar Tourists Found
    ↓
Recommendations API
    ↓
Tourist gets: "Try restaurant XYZ"
```

---

## 🏆 Judging Criteria (from World Bank)

| Criterion | Weight | How Musafir Scores |
|-----------|--------|-------------------|
| **Small AI Fidelity** | 25% | Pattern recognition (NLP + Vision + CF). No hallucination. Human-in-loop. |
| **Development Relevance** | 20% | Real problem. Tourism operators NEED this. Small budget works. |
| **Data Grounding** | 15% | Real Pakistan data. Published models. Honest about what models cover. |
| **Evidence It Works** | 15% | Working prototype. Demo video. Live app. |
| **Clarity, Design, Inclusivity** | 15% | Clear AI explanation. Works on phones. Multiple languages possible. |
| **Scalability** | 10% | Copy guide_data.json → Use in any country. Models are pre-trained. |
| **Responsible AI** | Pass/Fail | ✅ Human-in-loop. ✅ No autonomous decisions. ✅ AI flags uncertainty. |

---

## 📦 Deployment Checklist

- [ ] All files in GitHub: app.py, index.html, guide_data.json, requirements.txt, Procfile, README.md
- [ ] Railway linked: `railway link`
- [ ] Latest push: `git push`
- [ ] Live app works: https://musafir-production-d005.up.railway.app
- [ ] Video 2-5 minutes with all 5 sections
- [ ] Team created on Hack-Nation
- [ ] Tourism track (04c) selected
- [ ] Submit before **Oct 4, 6:00 AM PDT / Oct 4, 1:30 PM Pakistan time**

---

## 🎯 Next Steps (Post-Hackathon)

### Phase 1: Validate with 5 restaurants + 20 tourists
- Hunza region first (tourism hotspot)
- Real SMS gateway integration (Zong/Jazz API)
- JazzCash payment integration

### Phase 2: Add restaurant-specific recommendations
- Fine-tune model on regional cuisines
- Seasonal menu tracking
- Pricing intelligence

### Phase 3: Scale to 3-5 regions
- Skardu, Swat, Chitral
- Localize UI to Urdu/Wakhi/Khowar

### Phase 4: Expand beyond Pakistan
- Nepal (Kathmandu, Pokhara)
- Philippines (Cebu, Boracay)
- Indonesia (Bali, Lombok)

---

## 💡 Revenue Projection (Year 1)

**Conservative Model:**
- 100 restaurants × 10 SMS/day = 1,000 SMS/day
- 1,000 SMS × 2 PKR margin = 2,000 PKR/day
- 2,000 PKR × 30 days = 60,000 PKR/month = **720,000 PKR/year ($2,500)**

**Realistic Model:**
- 500 restaurants × 10 SMS/day = 5,000 SMS/day
- 5,000 SMS × 2 PKR margin = 10,000 PKR/day
- 10,000 PKR × 30 days = 300,000 PKR/month = **3.6M PKR/year ($12,500)**

**Optimistic Model:**
- 1,000 restaurants × 15 SMS/day = 15,000 SMS/day
- 15,000 SMS × 2 PKR margin = 30,000 PKR/day
- 30,000 PKR × 30 days = 900,000 PKR/month = **10.8M PKR/year ($37,500)**

Plus premium dashboard + white-label opportunities.

---

## 🎓 What Localizing AI Means

> "AI isn't just deployed in developing countries. It should be **built for** them."

Musafir respects:
- **Bandwidth:** Models run locally, not cloud-dependent
- **Devices:** Works on basic phones, not flagship devices
- **Languages:** Uses models trained on low-resource languages
- **Literacy:** Voice and text interfaces
- **Trust:** Humans make final decisions, AI informs
- **Economy:** Cheap enough for small operators to adopt

---

## 📞 Support

For issues:
1. Check Railway logs: `railway logs`
2. Test locally: `python app.py`
3. Verify requirements.txt installs
4. Check guide_data.json syntax (JSON format)

---

**Built with ❤️ for Pakistan's tourism future.**

*Last updated: Oct 4, 2026*
