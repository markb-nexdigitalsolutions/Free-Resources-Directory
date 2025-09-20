import math
import re
import traceback
import requests
import streamlit as st
from urllib.parse import quote_plus

# -----------------------------
# Streamlit config
# -----------------------------
st.set_page_config(page_title="Free Resources Directory", page_icon="🏛️", layout="wide")

CATEGORY_ICONS = {
    "housing": "🏠","food": "🍽️","healthcare": "🏥","employment": "💼",
    "education": "📚","financial": "💰","legal": "⚖️","family": "👨‍👩‍👧‍👦",
}

# ------------------------------------
# Local demo data (fallback if needed)
# ------------------------------------
BASE_RESOURCES = [
    {"name": "City Housing Authority","type": "government","category": "housing",
     "services": ["Rental assistance","Housing vouchers","Emergency shelter"],
     "phone": "(555) 123-4567","address": "123 Main St, City Hall",
     "description": "Provides affordable housing programs and rental assistance for low-income families.",
     "eligibility": "Income-based eligibility"},
    {"name": "Community Food Bank","type": "nonprofit","category": "food",
     "services": ["Free groceries","Hot meals","Nutrition education"],
     "phone": "(555) 234-5678","address": "456 Oak Ave",
     "description": "Distributes free food to families in need and operates soup kitchens.",
     "eligibility": "No income requirements"},
    {"name": "Department of Social Services","type": "government","category": "financial",
     "services": ["SNAP benefits","TANF","Medicaid enrollment"],
     "phone": "(555) 345-6789","address": "789 Government Blvd",
     "description": "Administers various assistance programs including food stamps and cash aid.",
     "eligibility": "Income and asset limits apply"},
    {"name": "Free Health Clinic","type": "nonprofit","category": "healthcare",
     "services": ["Primary care","Dental services","Mental health"],
     "phone": "(555) 456-7890","address": "321 Health St",
     "description": "Provides free medical and dental care to uninsured residents.",
     "eligibility": "Uninsured or underinsured"},
    {"name": "Workforce Development Center","type": "government","category": "employment",
     "services": ["Job training","Resume help","Interview prep"],
     "phone": "(555) 567-8901","address": "654 Career Way",
     "description": "Offers free job training programs and employment assistance.",
     "eligibility": "Open to all job seekers"},
    {"name": "Legal Aid Society","type": "nonprofit","category": "legal",
     "services": ["Free legal advice","Court representation","Document prep"],
     "phone": "(555) 678-9012","address": "987 Justice Ave",
     "description": "Provides free legal services for civil matters to low-income individuals.",
     "eligibility": "Income-based eligibility"},
    {"name": "Community College Foundation","type": "nonprofit","category": "education",
     "services": ["Scholarships","Textbook vouchers","Tutoring"],
     "phone": "(555) 789-0123","address": "147 Education Blvd",
     "description": "Awards scholarships and provides educational support to students.",
     "eligibility": "Students with financial need"},
    {"name": "Family Resource Center","type": "community","category": "family",
     "services": ["Childcare assistance","Parenting classes","Family counseling"],
     "phone": "(555) 890-1234","address": "258 Family Circle",
     "description": "Supports families with children through various programs and services.",
     "eligibility": "Families with children"},
    {"name": "Utility Assistance Program","type": "government","category": "housing",
     "services": ["Electric bill help","Gas bill assistance","Weatherization"],
     "phone": "(555) 901-2345","address": "369 Energy St",
     "description": "Helps low-income households pay utility bills and improve energy efficiency.",
     "eligibility": "Income guidelines apply"},
    {"name": "Senior Services Center","type": "nonprofit","category": "healthcare",
     "services": ["Meal delivery","Transportation","Medicare help"],
     "phone": "(555) 012-3456","address": "741 Senior Way",
     "description": "Provides comprehensive services for seniors including meals and transportation.",
     "eligibility": "Adults 60 and older"},
]

# ------------------------------------
# Helpers: UI, scoring, fallbacks
# ------------------------------------
def synthesize_resources(n=36):
    items = list(BASE_RESOURCES)
    i = 0
    while len(items) < n:
        t = dict(BASE_RESOURCES[i % len(BASE_RESOURCES)])
        idx = len(items)
        t["name"] = "{} - Branch {}".format(t["name"], idx // 10 + 1)
        t["address"] = t["address"].replace("123", str(100 + idx)).replace("456", str(100 + idx)).replace("789", str(100 + idx))
        t["phone"] = "(555) {:03d}-{:04d}".format(100 + (idx % 900), 1000 + (idx % 9000))
        items.append(t)
        i += 1
    return items[:n]

def personalized_tip(q, n):
    q = (q or "").lower()
    if ("rent" in q) or ("eviction" in q):
        return "💡 Found {} resources for housing help! Many offer emergency rental assistance.".format(n)
    if ("food" in q) or ("hungry" in q):
        return "💡 Found {} food resources! Most food banks don't require appointments.".format(n)
    if ("job" in q) or ("unemployed" in q):
        return "💡 Found {} employment resources! Many offer same-day resume help and placements.".format(n)
    if ("medical" in q) or ("health" in q):
        return "💡 Found {} healthcare resources! Several offer free services regardless of insurance.".format(n)
    return "💡 Found {} resources that can help your situation! Many offer immediate assistance.".format(n)

def card(resource, min_height=360):
    icon = CATEGORY_ICONS.get(resource.get("category",""), "📋")
    services = resource.get("services") or []
    services_html = "".join(
        "<span style='background:#eff6ff;color:#1d4ed8;border-radius:8px;padding:4px 8px;font-size:.85rem;margin:2px;display:inline-block;'>{}</span>".format(s)
        for s in services
    )
    return (
        "<div style='background:#fff;border-radius:16px;box-shadow:0 10px 25px rgba(0,0,0,.06);"
        "padding:16px;display:flex;flex-direction:column;justify-content:space-between;"
        "height:100%;min-height:{min_h}px;'>"
          "<div>"
            "<div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;'>"
              "<div style='font-size:1.1rem;font-weight:700;color:#111827;'>{name}</div>"
              "<span style='padding:4px 10px;border-radius:999px;font-size:.8rem;font-weight:600;background:#e5e7eb;color:#111827;'>{type}</span>"
            "</div>"
            "<div style='display:flex;align-items:center;margin:6px 0 10px 0;color:#4b5563;'>"
              "<span style='font-size:1.3rem;margin-right:8px;'>{icon}</span>"
              "<span style='font-size:.9rem;text-transform:capitalize;'>{category}</span>"
            "</div>"
            "<div style='color:#4b5563;margin-bottom:10px;'>{desc}</div>"
            "<div style='margin-bottom:12px;'>"
              "<div style='font-weight:600;color:#111827;margin-bottom:6px;'>Services Offered:</div>"
              "<div>{services_html}</div>"
            "</div>"
          "</div>"
          "<div style='border-top:1px solid #e5e7eb;padding-top:10px;color:#4b5563;font-size:.92rem;'>"
            "<div>📞 <a href='tel:{phone}' style='color:#1f2937;text-decoration:none;'>{phone}</a></div>"
            "<div>📍 {address}</div>"
            "<div>✅ <span style='font-weight:600;'>{elig}</span></div>"
          "</div>"
        "</div>"
    ).format(
        min_h=min_height,
        name=resource.get("name",""),
        type=resource.get("type",""),
        icon=icon,
        category=resource.get("category",""),
        desc=resource.get("description",""),
        services_html=services_html,
        phone=resource.get("phone",""),
        address=resource.get("address",""),
        elig=resource.get("eligibility",""),
    )

# ------------------------------------
# FREE, OPEN GOV PROVIDERS (NO KEYS)
# ------------------------------------
def norm_item(name, category, address, phone="", website="", email="", desc="", type_="nonprofit", eligibility=""):
    return {
        "name": name, "type": type_, "category": category, "services": [],
        "phone": phone, "email": email, "website": website,
        "address": address, "description": desc, "eligibility": eligibility,
    }

def _safe_get(url, params=None, timeout=12):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

# HRSA: Federally supported health centers (clinics) — NO KEY
def fetch_hrsa(zip_code=None, lat=None, lon=None, radius_mi=25):
    base = "https://data.hrsa.gov/HDWAPI3_External/api/v1"
    if zip_code:
        url = "{}/GetHealthCentersByArea".format(base); params = {"ZipCode": str(zip_code)}
    elif lat and lon:
        url = "{}/GetHealthCentersAroundALocation".format(base); params = {"Latitude": lat, "Longitude": lon, "Radius": radius_mi}
    else:
        return []
    data = _safe_get(url, params)
    items = []
    if not data or "HCC" not in data: return items
    for row in data["HCC"]:
        addr = ", ".join(filter(None, [
            row.get("SITE_ADDRESS",""), row.get("SITE_CITY",""), row.get("SITE_STATE_ABBR",""), row.get("SITE_ZIP","")
        ]))
        items.append(norm_item(
            name=row.get("SITE_NM","Health Center"),
            category="healthcare",
            address=addr,
            phone=row.get("SITE_PHONE_NUM",""),
            website=row.get("SITE_URL","") or "",
            desc=row.get("HCC_LOC_DESC","Community health center"),
            type_="nonprofit"
        ))
    return items

# HUD: Public Housing Authorities — NO KEY
def fetch_hud_phas(limit=50):
    url = "https://services.arcgis.com/hRUr1F8lE8Jq2uJo/arcgis/rest/services/Public_Housing_Authorities/FeatureServer/0/query"
    params = {"where":"1=1","outFields":"*","f":"json","resultRecordCount":limit}
    data = _safe_get(url, params)
    items = []
    if not data or "features" not in data: return items
    for f in data["features"]:
        a = f.get("attributes", {})
        name = a.get("PHA_NAME") or a.get("NAME") or "Public Housing Authority"
        addr = a.get("ADDRESS") or ""
        phone = a.get("PHONE") or ""
        web = a.get("WEBSITE") or ""
        items.append(norm_item(
            name=name, category="housing", address=addr, phone=phone, website=web,
            desc="Public Housing Authority", type_="government", eligibility="Varies by program"
        ))
    return items

# HUD: Public Housing Developments (addresses) — NO KEY
def fetch_hud_developments(limit=50):
    url = "https://services.arcgis.com/hRUr1F8lE8Jq2uJo/arcgis/rest/services/Public_Housing_Developments/FeatureServer/0/query"
    params = {"where":"1=1","outFields":"*","f":"json","resultRecordCount":limit}
    data = _safe_get(url, params)
    items = []
    if not data or "features" not in data: return items
    for f in data["features"]:
        a = f.get("attributes", {})
        name = a.get("DEV_NAME") or "Public Housing Development"
        pha = a.get("PHA_NAME") or ""
        addr = a.get("DEV_ADDRESS") or ""
        items.append(norm_item(
            name="{} ({})".format(name, pha) if pha else name,
            category="housing", address=addr, type_="government",
            desc="HUD public housing development"
        ))
    return items

def get_resources_free(query, city_or_zip):
    # Try to infer a ZIP (simple)
    zip_guess = None
    if city_or_zip:
        m = re.search(r"\b\d{5}\b", city_or_zip)
        if m: zip_guess = m.group(0)

    results = []
    # Healthcare (HRSA) near ZIP (if provided)
    if zip_guess:
        results += fetch_hrsa(zip_code=zip_guess)

    # Housing (HUD national)
    results += fetch_hud_phas(limit=50)
    results += fetch_hud_developments(limit=50)

    # Fallback to local demo if nothing
    if not results:
        results = synthesize_resources(36)

    # Quick keyword relevance to user's need
    q = (query or "").lower()
    if q:
        def score(r):
            text = " ".join([r.get("name",""), r.get("description",""), r.get("category","")]).lower()
            s = 0
            for w in ["rent","eviction","housing","shelter","utility"]:
                if w in q and w in text: s += 10
            for w in ["food","pantry","meal","nutrition"]:
                if w in q and w in text: s += 10
            for w in ["health","clinic","medical","dental","mental"]:
                if w in q and w in text: s += 10
            for w in ["job","employment","career","training","workforce"]:
                if w in q and w in text: s += 10
            for w in ["legal","attorney","court","aid"]:
                if w in q and w in text: s += 10
            return s
        results.sort(key=score, reverse=True)

    return results

# ------------------------------------
# App
# ------------------------------------
def main():
    if "displayed" not in st.session_state:
        st.session_state.displayed = synthesize_resources(36)
    if "page" not in st.session_state:
        st.session_state.page = 0
    if "tip" not in st.session_state:
        st.session_state.tip = ""

    PER_PAGE = 12

    # Header
    st.markdown(
        "<div style='text-align:center;margin-bottom:18px;'>"
        "<h1 style='margin:0;font-weight:800;color:#111827;font-size:2.2rem;'>🏛️ Free Resources Directory</h1>"
        "<p style='color:#4b5563;max-width:780px;margin:8px auto 0;'>Find real, official resources near you—housing, clinics, food, jobs, legal aid.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.subheader("What do you need help with?")
        needs = st.text_area(
            "Describe your situation",
            placeholder="e.g., I can't pay my rent • My electricity is about to be shut off • I need food for my family",
            height=110,
            label_visibility="collapsed",
        )
        city_or_zip = st.text_input("City or ZIP (US only for live data)", placeholder="e.g., Cleveland, OH or 44110")

        c1, c2, c3, c4 = st.columns([1,1,1,1])
        with c1:
            if st.button("🔍 Find Help Now", use_container_width=True):
                q = (needs or "").strip()
                if not q:
                    st.warning("Please tell us what you need help with first.")
                else:
                    data = get_resources_free(q, (city_or_zip or "").strip())
                    st.session_state.displayed = data
                    st.session_state.page = 0
                    st.session_state.tip = personalized_tip(q, len(data))

        with c2:
            if st.button("💰 Rent Help", use_container_width=True):
                q = "rent assistance"
                data = get_resources_free(q, (city_or_zip or "").strip())
                st.session_state.displayed, st.session_state.page = data, 0
                st.session_state.tip = personalized_tip(q, len(data))

        with c3:
            if st.button("🍽️ Food Help", use_container_width=True):
                q = "food pantry"
                data = get_resources_free(q, (city_or_zip or "").strip())
                st.session_state.displayed, st.session_state.page = data, 0
                st.session_state.tip = personalized_tip(q, len(data))

        with c4:
            if st.button("🏥 Clinic Help", use_container_width=True):
                q = "medical clinic"
                data = get_resources_free(q, (city_or_zip or "").strip())
                st.session_state.displayed, st.session_state.page = data, 0
                st.session_state.tip = personalized_tip(q, len(data))

    # Tip banner
    if st.session_state.tip:
        st.markdown(
            "<div style='background:#ecfdf5;border:1px solid #a7f3d0;border-radius:12px;padding:12px;margin-top:12px;color:#065f46;'>"
            "<div style='display:flex;gap:10px;align-items:flex-start;'>"
            "<div style='font-size:1.2rem;'>✅</div>"
            "<div>"
            "<div style='font-weight:600;'>{}</div>"
            "<div style='font-size:.9rem;margin-top:4px;'>Tip: Start with official websites and call ahead to confirm hours.</div>"
            "</div></div></div>".format(st.session_state.tip),
            unsafe_allow_html=True,
        )

    # Results header
    total = len(st.session_state.displayed)
    st.markdown("**Showing {} resources**".format(total))

    # Grid (equal-height cards)
    start = st.session_state.page * PER_PAGE
    end = min(start + PER_PAGE, total)
    cols = st.columns(3)

    for i in range(start, end):
        res = st.session_state.displayed[i]
        with cols[i % 3]:
            st.markdown(card(res, min_height=360), unsafe_allow_html=True)

            # Contact actions: Website → Email → Phone. Always add Directions + More Info.
            website = res.get("website") or ""
            email = res.get("email") or ""
            phone = res.get("phone") or ""
            addr = res.get("address","")
            name = res.get("name","")

            row = st.columns(3)
            with row[0]:
                if website:
                    st.link_button("🌐 Website", website, use_container_width=True)
                elif email:
                    st.link_button("✉️ Email", "mailto:{}".format(email), use_container_width=True)
                elif phone:
                    st.link_button("📞 Call", "tel:{}".format(phone), use_container_width=True)
                else:
                    st.link_button("ℹ️ Info", "https://www.google.com/search?q={}".format(
                        quote_plus("{} {}".format(name, addr))
                    ), use_container_width=True)

            with row[1]:
                st.link_button("📍 Directions", "https://www.google.com/maps/search/?api=1&query={}".format(
                    quote_plus(addr if addr else name)
                ), use_container_width=True)

            with row[2]:
                st.link_button("🔎 More Info", "https://www.google.com/search?q={}".format(
                    quote_plus("{} {}".format(name, addr))
                ), use_container_width=True)

    # Pagination
    st.write("")
    pages = max(1, math.ceil(total / PER_PAGE))
    if pages > 1:
        pcols = st.columns(3)
        with pcols[0]:
            if st.button("◀️ Previous", disabled=start == 0, use_container_width=True):
                st.session_state.page -= 1
                st.rerun()
        with pcols[1]:
            st.markdown(
                "<div style='text-align:center;color:#4b5563;'>Page {} of {}</div>".format(st.session_state.page + 1, pages),
                unsafe_allow_html=True,
            )
        with pcols[2]:
            if st.button("Next ▶️", disabled=end >= total, use_container_width=True):
                st.session_state.page += 1
                st.rerun()

# Safety net: show errors on-screen instead of a blank page
try:
    main()
except Exception:
    st.error("An error occurred while rendering the app.")
    st.exception(Exception)
    st.code(traceback.format_exc())
