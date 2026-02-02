import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Agentic Honeypot Scam AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ===================== CSS (FINAL) =====================
st.markdown(
    """
    <style>
    #MainMenu, footer, header {visibility: hidden;}

    .stApp{
      background: linear-gradient(180deg, #0b1220, #020617);
      color: #e5e7eb !important;
      font-family: "Segoe UI", sans-serif;
    }
    h1,h2,h3,h4,p,span,div,label { color:#e5e7eb !important; }

    /* Card */
    .card{
      background: rgba(15,23,42,0.95);
      border: 1px solid rgba(148,163,184,0.22);
      border-radius: 18px;
      padding: 22px;
      margin-bottom: 22px;
      box-shadow: 0 12px 30px rgba(0,0,0,0.35);
    }

    /* ===================== INPUTS (NO WHITE) ===================== */
    /* BaseWeb wrappers used by Streamlit */
    div[data-baseweb="base-input"],
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"] > div{
      background: #1e293b !important;
      border-radius: 12px !important;
    }

    div[data-baseweb="input"]{
      border: 1px solid #64748b !important;
    }

    div[data-baseweb="input"] input{
      background: transparent !important;
      color: #ffffff !important;
      font-weight: 650 !important;
      border: none !important;
      box-shadow: none !important;
    }

    div[data-baseweb="input"] input::placeholder{
      color: #94a3b8 !important;
    }

    /* ✅ Password eye icon visible */
    button[title="Show password"],
    button[title="Hide password"]{
      color: #ffffff !important;
      fill: #ffffff !important;
      opacity: 1 !important;
    }
    button[title="Show password"]:hover,
    button[title="Hide password"]:hover{
      color: #22c55e !important;
      fill: #22c55e !important;
    }

    /* ===================== TEXTAREA ===================== */
    .stTextArea textarea{
      background: #1e293b !important;
      color: #ffffff !important;
      border: 2px solid #14b8a6 !important;
      border-radius: 14px !important;
      font-size: 15px !important;
      font-weight: 650 !important;
    }
    .stTextArea textarea::placeholder{ color:#94a3b8 !important; }

    /* Buttons */
    button { border-radius: 12px !important; font-weight: 900 !important; }
    button[kind="primary"]{
      background: linear-gradient(135deg, #14b8a6, #0d9488) !important;
      color: #020617 !important;
      border: none !important;
    }
    button[kind="secondary"]{
      background: linear-gradient(135deg, #ef4444, #dc2626) !important;
      color: #ffffff !important;
      border: none !important;
    }

    /* Tabs */
    div[role="radiogroup"]{ display:flex; gap:14px; flex-wrap:wrap; }
    div[role="radiogroup"] label{
      background: #0b1020 !important;
      border: 1px solid rgba(148,163,184,0.25) !important;
      border-radius: 14px !important;
      padding: 10px 18px !important;
      font-weight: 900 !important;
    }
    div[role="radiogroup"] label[data-selected="true"]{
      background: rgba(20,184,166,0.25) !important;
      border-color: #14b8a6 !important;
    }

    /* Remove white code chips */
    code { background: transparent !important; padding:0 !important; }

    /* Intel tags */
    .tag{
      display:inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      margin: 6px 8px 0 0;
      background: rgba(20,184,166,0.18);
      border: 1px solid rgba(20,184,166,0.45);
      color: #d1fae5 !important;
      font-weight: 800;
      font-size: 13px;
    }
    .tag-red{
      background: rgba(239,68,68,0.18);
      border: 1px solid rgba(239,68,68,0.45);
      color: #fee2e2 !important;
    }
    .muted{ color: rgba(226,232,240,0.70) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===================== HELPERS =====================
def api_post(path, payload):
    try:
        return requests.post(f"{API}{path}", json=payload, timeout=15).json()
    except:
        st.error("❌ Backend not running. Start:\nuvicorn app.main:app --reload --port 8000")
        st.stop()

def api_get(path):
    try:
        return requests.get(f"{API}{path}", timeout=15).json()
    except:
        st.error("❌ Backend not running.")
        st.stop()

def clear_msg():
    st.session_state.scam_msg = ""

def logout():
    st.session_state.auth = False
    st.session_state.scam_msg = ""
    st.session_state.session_id = None
    st.session_state.session = None

def show_tags(items, red=False):
    if not items:
        st.markdown('<span class="muted">None detected</span>', unsafe_allow_html=True)
        return
    cls = "tag-red" if red else "tag"
    html = "".join([f'<span class="tag {cls}">{x}</span>' for x in items])
    st.markdown(html, unsafe_allow_html=True)

# ===================== SESSION STATE =====================
if "auth" not in st.session_state:
    st.session_state.auth = False
if "scam_msg" not in st.session_state:
    st.session_state.scam_msg = ""
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "session" not in st.session_state:
    st.session_state.session = None

# ===================== LOGIN PAGE =====================
if not st.session_state.auth:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## 🔐 Login")

    st.text_input("Email", placeholder="demo@project.com")
    st.text_input("Password", type="password", placeholder="demo123")

    if st.button("Login", type="primary"):
        st.session_state.auth = True
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ===================== HEADER =====================
c1, c2 = st.columns([7, 1])
with c1:
    st.markdown("## 🛡️ Agentic Honeypot Scam Detection System")
    st.caption("Scam Analyzer • Automated Honeypot • Threat Intelligence")
with c2:
    st.button("Logout", type="secondary", on_click=logout)

# ===================== NAV =====================
page = st.radio(
    "",
    ["🔍 Scam Analyzer", "🎭 Honeypot Conversation", "📊 Threat Intelligence"],
    horizontal=True,
    label_visibility="collapsed",
)

# ===================== SCAM ANALYZER =====================
if "Scam Analyzer" in page:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Scam Analyzer")

    st.text_area(
        "Paste suspicious message",
        key="scam_msg",
        height=160,
        placeholder="Paste your scam message here..."
    )

    threshold = st.slider("Auto-send to Honeypot when score ≥", 0.0, 1.0, 0.6)

    col1, col2 = st.columns(2)
    analyze = col1.button("Analyze", type="primary")
    col2.button("Clear", type="secondary", on_click=clear_msg)

    if analyze:
        if not st.session_state.scam_msg.strip():
            st.warning("Please paste a message first.")
        else:
            res = api_post("/analyze", {"message": st.session_state.scam_msg})
            score = float(res.get("scam_score", 0.0))

            st.success(f"Scam Score: {score:.2f}")
            st.write("**Scam Type:**", res.get("scam_type"))

            st.markdown("#### Reasons")
            for r in res.get("reasons", []):
                st.markdown(f"- ✅ {r}")

            if res.get("is_scam") and score >= threshold:
                hp = api_post("/honeypot/start", {"message": st.session_state.scam_msg, "analyze_result": res})
                st.session_state.session_id = hp.get("session_id")
                st.session_state.session = hp.get("session")
                st.success("✅ Auto-sent to Honeypot")

    st.markdown("</div>", unsafe_allow_html=True)

# ===================== HONEYPOT =====================
elif "Honeypot" in page:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🎭 Honeypot Conversation")

    if not st.session_state.session_id:
        st.info("No active honeypot session.")
    else:
        s = api_get(f"/honeypot/session/{st.session_state.session_id}")
        st.session_state.session = s

        for m in s.get("messages", []):
            who = "🟩 Honeypot" if m["role"] == "honeypot" else "🟥 Scammer"
            st.write(f"**{who}:** {m['text']}")

        incoming = st.text_input("Incoming scammer message", placeholder="Type scammer reply here...")

        if st.button("Send to Honeypot", type="primary"):
            api_post("/honeypot/incoming", {"session_id": s["id"], "message": incoming})
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ===================== THREAT INTELLIGENCE =====================
else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Threat Intelligence")

    if not st.session_state.session:
        st.info("No intelligence collected yet.")
    else:
        intel = st.session_state.session.get("intel", {})

        st.markdown("#### UPI IDs")
        show_tags(intel.get("upi_ids", []), red=True)

        st.markdown("#### Phone Numbers")
        show_tags(intel.get("phone_numbers", []))

        st.markdown("#### Links")
        show_tags(intel.get("links", []))

        st.markdown("#### Domains")
        show_tags(intel.get("domains", []))

    st.markdown("</div>", unsafe_allow_html=True)
