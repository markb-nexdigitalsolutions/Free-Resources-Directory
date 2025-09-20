import math
import traceback
import streamlit as st

st.set_page_config(page_title="Free Resources Directory", page_icon="🏛️", layout="wide")

# -----------------------------
# Seed data
# -----------------------------
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

CATEGORY_ICONS = {
    "housing": "🏠","food": "🍽️","healthcare": "🏥","employment": "💼",
    "education": "📚","financial": "💰","legal": "⚖️","family": "👨‍👩‍👧‍👦",
}

# -----------------------------
# Helpers
# -----------------------------
def synthesize_resources(n=100):
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

def score_resource(resource, q):
    q = (q or "").lower()
    score = 0
    keywords = {
        "housing": ["rent","housing","apartment","eviction","homeless","shelter","utilities","electric","gas","water","heat"],
        "food": ["food","hungry","meal","groceries","snap","food stamps","nutrition"],
        "healthcare": ["medical","doctor","hospital","medicine","health","sick","insurance","medicaid"],
        "employment": ["job","work","unemployed","career","training","resume","interview"],
        "financial": ["money","cash","bills","debt","financial","assistance","emergency"],
        "legal": ["legal","lawyer","court","rights","law","attorney"],
        "education": ["school","education","scholarship","college","student","tuition"],
        "family": ["child","family","kids","parenting","daycare","childcare"],
    }
    for kw in keywords.get(resource["category"], []):
        if kw in q: score += 10
    for s in resource["services"]:
        if s.lower() in q: score += 15
    for w in resource["description"].lower().split():
        if len(w) > 3 and w in q: score += 5
    for w in ["emergency","urgent","immediately","asap","crisis","shut off","eviction"]:
        if w in q: score += 20
    return score

def smart_match(resources, q):
    scored = []
    for r in resources:
        s = score_resource(r, q)
        if s > 0:
            scored.append((s, r))
    if not scored:
        return list(resources)
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [r for _, r in scored]
    expanded = list(top)
    for idx, r in enumerate(top[:5]):
        for i in range(1, 11):
            clone = dict(r)
            clone["name"] = "{} - Branch {}".format(r["name"], i)
            base_addr = r["address"].split(",")[0]
            rest = ", ".join(r["address"].split(",")[1:]) if "," in r["address"] else ""
            clone["address"] = "{} #{}".format(base_addr, 300 + idx * 10 + i) + (", " + rest if rest else "")
            clone["phone"] = "(555) {:03d}-{:04d}".format(200 + (idx * 10 + i), 2000 + (idx * 100 + i))
            expanded.append(clone)
    return expanded[:50]

def card(resource, min_height=360):
    """
    Equal-height card using flex column layout.
    """
    icon = CATEGORY_ICONS.get(resource["category"], "📋")
    services_html = "".join(
        "<span style='background:#eff6ff;color:#1d4ed8;border-radius:8px;padding:4px 8px;font-size:.85rem;margin:2px;display:inline-block;'>{}</span>".format(s)
        for s in resource["services"]
    )
    # wrapper ensures equal height
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
        name=resource["name"],
        type=resource["type"],
        icon=icon,
        category=resource["category"],
        desc=resource["description"],
        services_html=services_html,
        phone=resource["phone"],
        address=resource["address"],
        elig=resource["eligibility"],
    )

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

# -----------------------------
# App
# -----------------------------
def main():
    # State
    if "all_resources" not in st.session_state:
        st.session_state.all_resources = synthesize_resources(100)
    if "displayed" not in st.session_state:
        st.session_state.displayed = list(st.session_state.all_resources)
    if "page" not in st.session_state:
        st.session_state.page = 0
    if "tip" not in st.session_state:
        st.session_state.tip = ""
    PER_PAGE = 12

    # Header
    st.markdown(
        "<div style='text-align:center;margin-bottom:18px;'>"
        "<h1 style='margin:0;font-weight:800;color:#111827;font-size:2.2rem;'>🏛️ Free Resources Directory</h1>"
        "<p style='color:#4b5563;max-width:720px;margin:8px auto 0;'>Discover government offices and non-profits in your city that offer free assistance, grants, and support services.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Search box
    box = st.container(border=True)
    with box:
        st.subheader("What do you need help with?")
        needs = st.text_area(
            "Type your situation in your own words",
            placeholder="e.g., I can't pay my rent this month • My electricity is about to be shut off • I need food for my family",
            height=110,
            label_visibility="collapsed",
        )
        c1, c2, c3, c4, c5, c6 = st.columns([1,1,1,1,1,1])
        with c1:
            if st.button("🔍 Find Help Now", use_container_width=True):
                q = (needs or "").strip()
                if not q:
                    st.warning("Please tell us what you need help with first.")
                else:
                    matched = smart_match(st.session_state.all_resources, q)
                    st.session_state.displayed = matched
                    st.session_state.page = 0
                    st.session_state.tip = personalized_tip(q, len(matched))
        with c2:
            if st.button("Clear", use_container_width=True):
                st.session_state.displayed = list(st.session_state.all_resources)
                st.session_state.page = 0
                st.session_state.tip = ""

        with c3:
            if st.button("💰 Rent Help", use_container_width=True):
                q = "rent help"
                matched = smart_match(st.session_state.all_resources, q)
                st.session_state.displayed, st.session_state.page = matched, 0
                st.session_state.tip = personalized_tip(q, len(matched))
        with c4:
            if st.button("🍽️ Food Help", use_container_width=True):
                q = "food assistance"
                matched = smart_match(st.session_state.all_resources, q)
                st.session_state.displayed, st.session_state.page = matched, 0
                st.session_state.tip = personalized_tip(q, len(matched))
        with c5:
            if st.button("💼 Job Help", use_container_width=True):
                q = "job training"
                matched = smart_match(st.session_state.all_resources, q)
                st.session_state.displayed, st.session_state.page = matched, 0
                st.session_state.tip = personalized_tip(q, len(matched))
        with c6:
            if st.button("⚡ Utility Help", use_container_width=True):
                q = "utility bills"
                matched = smart_match(st.session_state.all_resources, q)
                st.session_state.displayed, st.session_state.page = matched, 0
                st.session_state.tip = personalized_tip(q, len(matched))

    # Tip banner
    if st.session_state.tip:
        st.markdown(
            "<div style='background:#ecfdf5;border:1px solid #a7f3d0;border-radius:12px;padding:12px;margin-top:12px;color:#065f46;'>"
            "<div style='display:flex;gap:10px;align-items:flex-start;'>"
            "<div style='font-size:1.2rem;'>✅</div>"
            "<div>"
            "<div style='font-weight:600;'>{}</div>"
            "<div style='font-size:.9rem;margin-top:4px;'>Tip: Call the numbers directly — most organizations have staff ready to help.</div>"
            "</div></div></div>".format(st.session_state.tip),
            unsafe_allow_html=True,
        )

    # Results header
    total = len(st.session_state.displayed)
    st.markdown("**Showing {} resources** in your area".format(total))

    # Grid (equal-height cards)
    start = st.session_state.page * PER_PAGE
    end = min(start + PER_PAGE, total)
    cols = st.columns(3)
    for i in range(start, end):
        res = st.session_state.displayed[i]
        with cols[i % 3]:
            # Card HTML (equal height)
            st.markdown(card(res, min_height=360), unsafe_allow_html=True)
            # Streamlit button (outside HTML, consistent placement because card has fixed min-height)
            st.button("Contact for Help", key="contact_{}".format(i), use_container_width=True)

    # Pagination
    st.write("")
    pages = max(1, math.ceil(total / PER_PAGE))
    if pages > 1:
        pcols = st.columns(3)
        with pcols[0]:
            if st.button("◀️ Previous", disabled=st.session_state.page == 0, use_container_width=True):
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
except Exception as e:
    st.error("An error occurred while rendering the app.")
    st.exception(e)
    st.code(traceback.format_exc())
