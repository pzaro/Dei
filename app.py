import streamlit as st
import fitz  # PyMuPDF
import re

# ─────────────────────────────────────────────────────────────────
# ΣΕΛΙΔΑ & ULTRA-MODERN FINTECH STYLE (CSS)
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Net Metering Pro | Zarkolia Health",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: #0F172A;
    color: #F8FAFC;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.app-header { text-align: center; padding: 2rem 0 2rem 0; }
.app-title {
    font-size: 2.8rem; font-weight: 800; letter-spacing: -1px;
    background: linear-gradient(90deg, #38BDF8, #818CF8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.app-subtitle { font-size: 1.1rem; color: #94A3B8; font-weight: 400; }

.input-container {
    background: #1E293B; border: 1px solid #3B82F6; border-radius: 16px;
    padding: 1.5rem; margin-bottom: 2rem; box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1);
}

.metric-row { display: flex; gap: 1.5rem; margin-bottom: 2rem; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 200px; background: #1E293B; border: 1px solid #334155;
    border-radius: 16px; padding: 1.5rem; transition: transform 0.2s ease;
}
.metric-card:hover { transform: translateY(-2px); border-color: #475569; }
.metric-label { font-size: 0.85rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; margin-bottom: 0.5rem; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #F8FAFC; font-family: 'Fira Code', monospace; }
.text-green { color: #10B981 !important; }
.text-blue { color: #38BDF8 !important; }
.text-orange { color: #F5A623 !important; }

.hero-card {
    background: linear-gradient(145deg, #064E3B 0%, #022C22 100%);
    border: 1px solid #047857; border-radius: 24px; padding: 3rem 2rem;
    text-align: center; margin-bottom: 3rem; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
}
.hero-label { font-size: 1.1rem; color: #A7F3D0; font-weight: 500; margin-bottom: 1rem; }
.hero-amount { font-size: 4.5rem; font-weight: 800; color: #10B981; line-height: 1; letter-spacing: -2px; margin-bottom: 1.5rem; font-family: 'Fira Code', monospace; }
.hero-tags { display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; }
.tag {
    background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2);
    color: #6EE7B7; padding: 0.5rem 1rem; border-radius: 99px; font-size: 0.9rem; font-weight: 500;
}

.section-title { font-size: 1.2rem; font-weight: 700; color: #FFFFFF; margin-bottom: 1.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid #334155; }
.list-item { background: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; }
.list-item-left { display: flex; flex-direction: column; gap: 0.2rem; }
.list-item-title { font-size: 1rem; font-weight: 600; color: #E2E8F0; }
.list-item-desc { font-size: 0.8rem; color: #64748B; }
.list-item-amount { font-size: 1.2rem; font-weight: 700; font-family: 'Fira Code', monospace; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# ΛΟΓΙΚΗ & ΥΠΟΛΟΓΙΣΜΟΙ
# ─────────────────────────────────────────────────────────────────

def clean_number(s):
    s = s.strip()
    is_neg = s.startswith('-') or s.endswith('-')
    s = re.sub(r'[^\d,\.]', '', s)
    if ',' in s and '.' in s: s = s.replace('.', '').replace(',', '.')
    elif ',' in s: s = s.replace(',', '.')
    try:
        val = float(s)
        return -val if is_neg else val
    except: return 0.0

def parse_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc: text += page.get_text("text") + "\n"
    
    # 1. Συνολική Κατανάλωση Μετρητή (π.χ. 1060)
    total_kwh = 0.0
    match_total = re.search(r'Κατανάλωση Ηλεκτρικής Ενέργειας\s+([\d\.,]+)\s*kWh', text, re.IGNORECASE)
    if match_total: total_kwh = clean_number(match_total.group(1))
    
    # Διαχωρισμός 11/12 (Ημέρα/Νύχτα)
    day_kwh, night_kwh = 0.0, 0.0
    meters = re.findall(r'T\d+\s+(11|12)\s+\d+\s+\d+\s+\d+\s+\d+\s+([\d\.,]+)', text)
    for m_type, m_val in meters:
        if m_type == "11": day_kwh = clean_number(m_val)
        if m_type == "12": night_kwh = clean_number(m_val)
    
    if total_kwh == 0: total_kwh = day_kwh + night_kwh

    # 2. Τιμολογηθείσες kWh (Προμήθεια)
    billed_kwh = 0.0
    # Ψάχνουμε γραμμές όπως "400kWh x 0,165" ή "Χρέωση Ενέργειας ... kWh"
    energy_lines = re.findall(r'(\d+)\s*kWh\s*[x×X]\s*[\d,\.]+', text, re.IGNORECASE)
    # ΠΡΟΣΟΧΗ: Παίρνουμε μόνο αυτές που είναι στο section "Χρεώσεις Προμήθειας"
    supply_block = re.search(r'Χρεώσεις Προμήθειας ΔΕΗ(.*?)Ρυθμιζόμενες Χρεώσεις', text, re.DOTALL | re.IGNORECASE)
    if supply_block:
        supply_text = supply_block.group(1)
        billed_lines = re.findall(r'(\d+)\s*kWh', supply_text, re.IGNORECASE)
        billed_kwh = sum(float(x) for x in billed_lines)

    # 3. Οικονομικά Στοιχεία
    total_bill = 0.0
    match_bill = re.search(r'Συνολικό πιστωτικό υπόλοιπο\s*(-?[\d\.,]+)', text, re.IGNORECASE)
    if match_bill: total_bill = clean_number(match_bill.group(1))

    return total_kwh, day_kwh, night_kwh, billed_kwh, total_bill

# UI Rendering
st.markdown('<div class="app-header">', unsafe_allow_html=True)
st.markdown('<div class="app-title">Net Metering Analytics Pro</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📄 Ανεβάστε τον λογαριασμό (PDF)", type="pdf")

if uploaded_file:
    with st.spinner('Αναλύεται ο λογαριασμός...'):
        total_kwh, day_kwh, night_kwh, billed_kwh, total_bill = parse_pdf(uploaded_file.read())
        
        hidden_kwh = total_kwh - billed_kwh
        # Χρησιμοποιούμε μια μέση τιμή 0.145€ αν δεν βρούμε άλλη
        saved_energy_val = hidden_kwh * 0.145 
        total_saved = saved_energy_val * 1.06 # + 6% ΦΠΑ

        # Dashboard
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Σύνολο Μετρητή</div><div class="metric-value">{total_kwh:.0f} kWh</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Τιμολογηθείσες (Net)</div><div class="metric-value text-orange">{billed_kwh:.0f} kWh</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Ποσό Πληρωμής</div><div class="metric-value text-blue">{total_bill:.2f} €</div></div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="hero-card">
            <div class="hero-label">ΠΡΑΓΜΑΤΙΚΟ ΟΦΕΛΟΣ NET METERING</div>
            <div class="hero-amount">+{total_saved:.2f} €</div>
            <div class="hero-tags">
                <span class="tag">⚡ {hidden_kwh:.0f} kWh δωρεάν ενέργεια</span>
                <span class="tag">☀️ Ημέρας: {day_kwh:.0f} kWh</span>
                <span class="tag">🌙 Νύχτας: {night_kwh:.0f} kWh</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if billed_kwh == 0 and total_kwh > 0:
            st.info("💡 **Ανάλυση:** Παρόλο που βλέπετε kWh στις ρυθμιζόμενες χρεώσεις, η ΔΕΗ σας χρέωσε **0 € για την αξία του ρεύματος**, καθώς η παραγωγή σας κάλυψε το 100% της κατανάλωσης.")
