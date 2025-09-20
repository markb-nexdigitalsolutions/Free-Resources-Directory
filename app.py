import math
import streamlit as st

st.set_page_config(page_title="Free Resources Directory", page_icon="🏛️", layout="wide")

# -----------------------------
# Seed data (from your prototype)
# -----------------------------
BASE_RESOURCES = [
    {
        "name": "City Housing Authority",
        "type": "government",
        "category": "housing",
        "services": ["Rental assistance", "Housing vouchers", "Emergency shelter"],
        "phone": "(555) 123-4567",
        "address": "123 Main St, City Hall",
        "description": "Provides affordable housing programs and rental assistance for low-income families.",
        "eligibility": "Income-based eligibility",
    },
    {
        "name": "Community Food Bank",
        "type": "nonprofit",
        "category": "food",
        "services": ["Free groceries", "Hot meals", "Nutrition education"],
        "phone": "(555) 234-5678",
        "address": "456 Oak Ave",
        "description": "Distributes free food to families in need and operates soup kitchens.",
        "eligibility": "No income requirements",
    },
    {
        "name": "Department of Social Services",
        "type": "government",
        "category": "financial",
        "services": ["SNAP benefits", "TANF", "Medicaid enrollment"],
        "phone": "(555) 345-6789",
        "address": "789 Government Blvd",
        "description": "Administers various assistance programs including food stamps and cash aid.",
        "eligibility": "Income and asset limits apply",
    },
    {
        "name": "Free Health Clinic",
        "type": "nonprofit",
        "category": "healthcare",
        "services": ["Primary care", "Dental services", "Mental health"],
        "phone": "(555) 456-7890",
        "address": "321 Health St",
        "description": "Provides free medical and dental care to uninsured residents.",
        "eligibility": "Uninsured or underinsured",
    },
    {
        "name": "Workforce Development Center",
        "type": "government",
        "category": "employment",
        "services": ["Job training", "Resume help", "Interview prep"],
        "phone": "(555) 567-8901",
        "address": "654 Career Way",
        "description": "Offers free job training programs and employment assistance.",
        "eligibility": "Open to all job seekers",
    },
    {
        "name": "Legal Aid Society",
        "type": "nonprofit",
        "category": "legal",
        "services": ["Free legal advice", "Court representation", "Document prep"],
        "phone": "(555) 678-9012",
        "address": "987 Justice Ave",
        "description": "Provides free legal services for civil matters to low-income individuals.",
        "eligibility": "Income-based eligibility",
    },
    {
        "name": "Community College Foundation",
        "type": "nonprofit",
        "category": "education",
        "services": ["Scholarships", "Textbook vouchers", "Tutoring"],
        "phone": "(555) 789-0123",
        "address": "147 Education Blvd",
        "description": "Awards scholarships and provides educational support to students.",
        "eligibility": "Students with financial need",
    },
    {
        "name": "Family Resource Center",
        "type": "community",
        "category": "family",
        "services": ["Childcare assistance", "Parenting classes", "Family counseling"],
        "phone": "(555) 890-1234",
        "address": "258 Family Circle",
        "description": "Supports families with children through various programs and services.",
        "eligibility": "Families with children",
    },
    {
        "name": "Utility Assistance Program",
        "type": "government",
        "category": "housing",
        "services": ["Electric bill help", "Gas bill assistance", "Weatherization"],
        "phone": "(555) 901-2345",
        "address": "369 Energy St",
        "description": "Helps low-income households pay utility bills and improve energy efficiency.",
        "eligibility": "Income guidelines apply",
    },
    {
        "name": "Senior Services Center",
        "type": "nonprofit",
        "category": "healthcare",
        "services": ["Meal delivery", "Transportation", "Medicare help"],
        "phone": "(555) 012-3456",
        "address": "741 Senior Way",
        "description": "Provides comprehensive services for seniors including meals and transportation.",
        "eligibility": "Adults 60 and older",
    },
]

CATEGORY_ICONS = {
    "housing": "🏠",
    "food": "🍽️",
    "healthcare": "🏥",
    "employment": "💼",
    "education": "📚",
    "financial": "💰",
    "legal": "⚖️",
    "family": "👨‍👩‍👧‍👦",
}

TYPE_BADGE = {
    "government": ("bg-blue-100", "text-blue-800"),
    "nonprofit": ("bg-green-100", "text-green-800"),
    "community": ("bg-purple-100", "text-purple-800"),
}

# -----------------------------
# Utilities
# -----------------------------
def synthesize_resources(n=100):
    items = BASE_RESOURCES.copy()
    # Clone to reach n total
    idx = 0
    while len(items) < n:
        t = BASE_RESOURCES[idx % len(BASE_RESOURCES)].copy()
        i = len(items)
        t["name"] = f"{t['name']} - Branch {i//10 + 1}"
        # mutate address/phone a bit
        t["address"] = t["address"].replace("123", str(100 + i)).replace("456", str(100 + i)).replace("789", str(100 + i))
        t["phone"] = f"(555) {100 + (i%900):03d}-{1000 + (i%9000):04d}"
        items.append(t)
        idx += 1
    return items[:n]

def score_resource(resource, q: str) -> int:
    q = q.lower()
    score = 0
    keywords = {
        "housing": ["rent", "housing", "apartment", "eviction", "homeless", "shelter", "utilities", "electric", "gas", "water", "heat"],
        "food": ["food", "hungry", "meal", "groceries", "snap", "food stamps", "nutrition"],
        "healthcare": ["medical", "doctor", "hospital", "medicine", "health", "sick", "insurance", "medicaid"],
        "employment": ["job", "work", "unemployed", "career", "training", "resume", "interview"],
        "financial": ["money", "cash", "bills", "debt", "financial", "assistance", "emergency"],
        "legal": ["legal", "lawyer", "court", "rights", "law", "attorney"],
        "education": ["school", "education", "scholarship", "college", "student", "tuition"],
        "family": ["child", "family", "kids", "parenting", "daycare", "childcare"],
    }
    # category keywords
    for kw in keywords.get(resource["category"], []):
        if kw in q:
            score += 10
    # services
    for s in resource["services"]:
        if s.lower() in q:
            score += 15
    # description words (simple contains)
    for w in resource["description"].lower().split():
        if len(w) > 3 and w in q:
            score += 5
    # emergency priority
    for w in ["emergency", "urgent", "immediately", "asap", "crisis", "shut off", "eviction"]:
        if w in q:
            score += 20
    return score

def smart_match(resources, q: str):
    scored = []
    for r in resources:
        s = score_resource(r, q)
        if s > 0:
            scored.append((s, r))
    if not scored:
        return resources[:]  # no match -> show all
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [r for _, r in scored]
    # Expand by cloning top-5 to simulate nearby branches
    expanded = top[:]
    for idx, r in enumerate(top[:5]):
        for i in range(1, 11):
            clone = r.copy()
            clone["name"] = f"{r['name']} - Branch {i}"
            clone["address"] = r["address"].split(",")[0] + f" #{300 + idx*10 + i}, " + (r["address"].split(",")[1] if "," in r["address"] else "")
            clone["phone"] = f"(555) {200 + (idx*10+i):03d}-{2000 + (idx*100+i):04d}"
            expanded.append(clone)
    return expanded[:50]

def card(resource):
    badge_bg, badge_fg = TYPE_BADGE.get(resource["type"], ("bg-gray-100", "text-gray-800"))
    icon = CATEGORY_ICONS.get(resource["category"], "📋")
    services_html = "".join(
        f"<span style='background:#eff6ff;color:#1d4ed8;border-radius:8px;padding:4px 8px;font-size:.85rem;margin:2px;display:inline-block;'>{s}</span>"
        for s in resource["services"]
    )
    return f"""
    <div style="background:#fff;border-radius:16px;box-shadow:0 10px 25px rgba(0,0,0,.06);padding:16px;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
        <div style="font-size:1.1rem;font-weight:700;color:#111827;">{resource['name']}</div>
        <span style="padding:4px 10px;border-radius:999px;font-size:.8rem;font-weight:600;" class="{badge_bg} {badge_fg}">{resource['type']}</span>
      </div>
      <div style="display:flex;align-items:center;margin:6px 0 10px 0;color:#4b5563;">
        <span style="font-size:1.3rem;margin-right:8px;">{icon}</span>
        <span style="font-size:.9rem;text-transform:capitalize;">{resource['category']}</span>
      </div>
      <div style="color:#4b5563;margin-bottom:10px;">{resource['description']}</div>
      <div style="margin-bottom:12px;">
        <div style="font-weight:600;color:#111827;margin-bottom:6px;">Services Offered:</div>
        <div>{services_html}</div>
      </div>
      <div style="border-top:1px solid #e5e7eb;padding-top:10px;color:#4b5563;font-size:.92rem;">
        <div>📞 <a href="tel:{resource['phone']}" style="color:#1f2937;text-decoration:none;">{resource['phone']}</a></div>
        <div>📍 {resource['address']}</div>
        <div>✅ <span style="font-weight:600;">{resource['eligibility']}</span></div>
      </div>
    </div>
    """

def personalized_tip(q: str, n: int) -> str:
    q = q.lower()
    if "rent" in q or "eviction" in q:
        return f"💡 Found {n} resources for housing help! Many offer emergency rental assistance."
    if "food" in q or "hungry" in q:
        return f"💡 Found {n} food resources! Most food banks don’t require appointments."
    if "job" in q or "unemployed" in q:
        return f"💡 Found {n} employment resources! Many offer same-day
