# 🏛️ Free Resources Directory

Discover government offices and non-profits that offer free assistance, grants, and support services.  
Type your need in plain English (e.g., “I can’t pay rent”, “need food”, “lost my job”) and get the most relevant resources.

---

## ✨ Features
- Smart matching from natural-language needs (rent, food, utilities, jobs, medical, etc.)
- 100 sample resources (auto-synthesized branches for demo)
- Clean cards with category icons, services, phone, address, eligibility
- Quick suggestion chips (Rent, Food, Job, Utility)
- Pagination for fast browsing

> This version uses local demo data. You can swap in a live database/API later.

---

## 🚀 Run locally

```bash
git clone https://github.com/<your-username>/free-resources-directory.git
cd free-resources-directory
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
