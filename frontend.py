import re
import requests
import streamlit as st

# ---------------- Page Setup ----------------
st.set_page_config(page_title="ReelOrReal", page_icon="🎣", layout="centered")

# ---------------- Styling ----------------
st.markdown(
    """
    <style>
      /* App background + typography */
      .stApp { background: #fbfbf9; } /* clean off-white */
      html, body, [class*="css"] { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }

      /* Tidy content width and spacing */
      .block-container { max-width: 900px; padding-top: 3.5rem; padding-bottom: 3rem; }

      /* Title + subtitle vibe */
      .brand {
        text-align: center;
        font-size: 2.45rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #101010;
        margin-bottom: 0.35rem;
      }
      .tagline {
        text-align: center;
        font-size: 0.95rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #5f6368;
        margin-bottom: 1.8rem;
      }
      .accent-line {
        width: 120px;
        height: 2px;
        background: #101010;
        margin: 0 auto 2.0rem auto;
        opacity: 0.12;
      }

      /* Input styling (FIXED: typed text is black) */
      .stTextInput input {
        height: 3.2rem;
        border-radius: 10px;
        border: 1px solid rgba(16,16,16,0.25);
        background: white;
        font-size: 1.03rem;
        padding-left: 12px;

        color: #111 !important;        /* typed text */
        caret-color: #111 !important;  /* cursor */
      }
      .stTextInput input::placeholder {
        color: rgba(17,17,17,0.45) !important; /* placeholder */
      }
      .stTextInput input:focus {
        border-color: rgba(16,16,16,0.65);
        box-shadow: none !important;
      }

      /* Button styling */
      div.stButton > button {
        height: 3.2rem;
        border-radius: 10px;
        border: 1px solid #101010;
        background: #101010;
        color: #fbfbf9;
        font-weight: 800;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        width: 100%;
      }
      div.stButton > button:hover {
        background: #2a2a2a;
        border-color: #2a2a2a;
      }

      /* Result card styling */
      .card {
        margin-top: 1.6rem;
        padding: 1.1rem 1.2rem;
        border-radius: 14px;
        border: 1px solid rgba(16,16,16,0.12);
        background: white;
      }
      .pill {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-weight: 800;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        font-size: 0.78rem;
        border: 1px solid rgba(16,16,16,0.18);
        background: rgba(16,16,16,0.03);
        color: #000000 !important;
      }
      .pill-red { background: rgba(220, 38, 38, 0.10); border-color: rgba(220, 38, 38, 0.30); color: #000000 !important; }
      .pill-green { background: rgba(16, 185, 129, 0.10); border-color: rgba(16, 185, 129, 0.30); color: #000000 !important;}

      .card-title {
        margin-top: 0.7rem;
        font-size: 1.35rem;
        font-weight: 800;
        color: #101010;
      }
      .card-sub {
        margin-top: 0.2rem;
        color: #404040;
        font-size: 0.98rem;
      }
      .meta {
        margin-top: 0.8rem;
        color: #6b7280;
        font-size: 0.9rem;
      }

      /* Sidebar heading */
      .sidebar-title {
        font-weight: 900;
        letter-spacing: 0.10em;
        text-transform: uppercase;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("<div class='sidebar-title'>ReelDefense</div>", unsafe_allow_html=True)
    st.caption("🎣 Reel in risky links before they hook you.")

    st.divider()
    st.subheader("Backend Settings")

    # Defaults without requiring secrets.toml
    default_base = "http://127.0.0.1:5000"
    try:
        default_base = st.secrets.get("BACKEND_BASE_URL", default_base)
    except Exception:
        pass

    base_url = st.text_input("Backend Base URL", value=default_base)
    endpoint = st.text_input("Predict Endpoint", value="/predict")
    timeout = st.number_input(
        "Request timeout (seconds)", min_value=1, max_value=60, value=10
    )

    st.divider()
    show_debug = st.toggle("Show debug response", value=False)

predict_url = base_url.rstrip("/") + "/" + endpoint.lstrip("/")


# ---------------- Helpers ----------------
def normalize_url(u: str) -> str:
    u = u.strip()
    if u and not re.match(r"^https?://", u, re.IGNORECASE):
        u = "https://" + u
    return u


def looks_like_url(u: str) -> bool:
    return bool(re.match(r"^https?://", u.strip(), re.IGNORECASE))


# ---------------- Main UI ----------------
st.markdown("<div class='brand'>ReelDefense 🎣</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='tagline'>Reel in risky links before they hook you!</div>",
    unsafe_allow_html=True,
)
st.markdown("<div class='accent-line'></div>", unsafe_allow_html=True)

url_input = st.text_input(
    "URL",
    placeholder="Paste a link (example.com or https://example.com)",
    label_visibility="collapsed",
)

scan = st.button("Scan", type="primary", use_container_width=True)

result_area = st.empty()

if scan:
    url = normalize_url(url_input)

    if not url:
        result_area.warning("Please enter a URL.")
    elif not looks_like_url(url):
        result_area.warning("Please enter a valid URL.")
    else:
        try:
            # Looping loading circle
            with st.spinner("Casting the line... 🎣"):
                r = requests.post(
                    predict_url,
                    json={"url": url},
                    timeout=float(timeout),
                )
                r.raise_for_status()
                data = r.json()

            label = str(data.get("label", "")).lower()
            confidence = data.get("confidence", None)
            message = data.get("message", None)

            is_phish = label in ("phishing", "phish", "malicious", "bad")
            is_legit = label in ("legitimate", "legit", "benign", "safe", "not phishing", "clean")
            is_uncertain = label in ("uncertain", "unclear", "unknown", "suspicious")

            if is_phish:
                pill = "<span class='pill pill-red'>⚠️ Phishing</span>"
                title = "Hook detected — suspicious link."
                sub = "Avoid clicking or entering any credentials."
            elif is_legit:
                pill = "<span class='pill pill-green'>✅ Legit</span>"
                title = "Looks clean — no hook detected."
                sub = "Still stay cautious with unexpected links."
            elif is_uncertain:
                pill = "<span class='pill'>⚠️ Uncertain</span>"
                title = "Suspicious patterns detected."
                sub = "Proceed with caution."
            else:
                pill = "<span class='pill'>ℹ️ Unknown</span>"
                title = "Couldn’t classify confidently."
                sub = "Backend returned an unexpected label."

            conf_text = ""
            if isinstance(confidence, (int, float)):
                conf = max(0.0, min(1.0, float(confidence)))
                conf_text = f"Confidence: {conf * 100:.1f}%"

            result_area.markdown(
                f"""
                <div class="card">
                  {pill}
                  <div class="card-title">{title}</div>
                  <div class="card-sub">{sub}</div>
                  <div class="meta">URL: <code>{url}</code></div>
                  <div class="meta">{conf_text}</div>
                  <div class="meta">{message or ""}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if show_debug:
                with st.expander("Debug"):
                    st.write("Calling:", predict_url)
                    st.json(data)

        except requests.exceptions.Timeout:
            result_area.error("Backend request timed out. Try increasing timeout.")
        except requests.exceptions.ConnectionError:
            result_area.error("Could not connect to backend. Is Flask running?")
        except requests.exceptions.HTTPError as e:
            result_area.error(f"Backend returned an HTTP error: {e}")
            try:
                st.code(r.text)
            except Exception:
                pass
        except ValueError:
            result_area.error("Backend did not return valid JSON.")
            st.code(r.text if "r" in locals() else "")
