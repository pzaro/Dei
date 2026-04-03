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
.text-normal { color: #F8FAFC; }

.math-container { background: #0F172A; border: 1px solid #1E293B; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; border-left: 4px solid #38BDF8; }
.math-header { font-weight: 700; color: #38BDF8; font-size: 1.1rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 8px; }
.math-body { color: #94A3B8; font-size: 0.9rem; line-height: 1.6; }
.math-formula { background: #1E293B; padding: 0.75rem; border-radius: 8px; font-family: 'Fira Code', monospace; color: #E2E8F0; margin-top: 0.75rem; border: 1px solid #334155; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ΒΙΒΛΙΟΘΗΚΗ ΕΞΗΓΗΣΕΩΝ ΧΡΕΩΣΕΩΝ
# ─────────────────────────────────────────────────────────────────
CHARGE_INFO = {
    "Χρεώσεις Προμήθειας": {"emoji": "⚡", "desc": "Το συνολικό κόστος προμήθειας ρεύματος.", "type": "energy"},
    "Χρέωση Ενέργειας Κανονική": {"emoji": "⚡", "desc": "Αξία ρεύματος Ημέρας.", "type": "energy"},
    "Χρέωση Ενέργειας Μειωμένη": {"emoji": "⚡", "desc": "Αξία ρεύματος Νύχτας.", "type": "energy"},
    "Πάγια Χρέωση": {"emoji": "📋", "desc": "Σταθερό μηνιαίο πάγιο βάσει συμβολαίου.", "type": "fixed"},
    "Μηχανισμός Διακύμανσης": {"emoji": "📈", "desc": "Χρέωση/Πίστωση βάσει Χρηματιστηρίου Ενέργειας (ΤΕΑ).", "type": "energy"},
    "ΑΔΜΗΕ: Σύστημα Μεταφοράς": {"emoji": "🔌", "desc": "Δίκτυο Υψηλής Τάσης. Περιλαμβάνει πάγιο ισχύος (kVA) και χρέωση ανά kWh.", "type": "per_kwh"},
    "ΔΕΔΔΗΕ: Δίκτυο Διανομής": {"emoji": "🔌", "desc": "Δίκτυο Μέσης/Χαμηλής Τάσης. Περιλαμβάνει πάγιο ισχύος (kVA) και χρέωση ανά kWh.", "type": "per_kwh"},
    "ΥΚΩ": {"emoji": "🏝️", "desc": "Υπηρεσίες Κοινής Ωφέλειας (Επιδότηση νησιών, ΚΟΤ).", "type": "per_kwh"},
    "ΕΤΜΕΑΡ": {"emoji": "🌱", "desc": "Ειδικό Τέλος Μείωσης Εκπομπών Αερίων Ρύπων. Υποστηρίζει την πράσινη ενέργεια.", "type": "per_kwh"},
    "Χρέωση Μέτρησης": {"emoji": "📟", "desc": "Πάγιο για τη συντήρηση και καταμέτρηση του μετρητή.", "type": "fixed"},
    "ΕΦΚ": {"emoji": "🏛️", "desc": "Ειδικός Φόρος Κατανάλωσης. Σταθερός φόρος 0,0022€ ανά kWh.", "type": "per_kwh"},
    "Ειδικό Τέλος 5‰": {"emoji": "🏛️", "desc": "Ειδικό Τέλος 5/1000 (Ν.2093/92). 0,5% επί της Προμήθειας, Ρυθμιζόμενων και ΕΦΚ.", "type": "percentage_5"},
    "ΦΠΑ": {"emoji": "🧾", "desc": "Φόρος Προστιθέμενης Αξίας (6%).", "type": "percentage_6"},
    "Τέλος Ανακύκλωσης": {"emoji": "♻️", "desc": "Τέλος υπέρ ανακύκλωσης συσκευών.", "type": "fixed"},
    "Δημοτικά Τέλη (ΔΤ)": {"emoji": "🗑️", "desc": "Ανταποδοτικά τέλη καθαριότητας & φωτισμού Δήμου. Υπολογίζεται βάσει τ.μ. ακινήτου.", "type": "municipal"},
    "Δημοτικός Φόρος (ΔΦ)": {"emoji": "🏛️", "desc": "Φόρος ηλεκτροδοτούμενων χώρων. Υπολογίζεται βάσει τ.μ.", "type": "municipal"},
    "ΤΑΠ": {"emoji": "🏠", "desc": "Τέλος Ακίνητης Περιουσίας. Υπολογίζεται βάσει τ.μ., παλαιότητας και Τιμής Ζώνης.", "type": "municipal"},
    "ΕΡΤ": {"emoji": "📺", "desc": "Ανταποδοτικό Τέλος ΕΡΤ (Σταθερό 3€/μήνα).", "type": "ert"},
    "Έκπτ. Πάγιας Εντολής": {"emoji": "🏷️", "desc": "Έκπτωση συνήθως 2% επειδή πληρώνετε μέσω κάρτας/τράπεζας.", "type": "discount"},
    "GreenPass": {"emoji": "🌿", "desc": "Πιστοποιητικό Εγγύησης Προέλευσης (Πράσινη Ενέργεια).", "type": "fixed"},
    "Έκπτωση Σταθμών ΑΠΕ": {"emoji": "☀️", "desc": "Έκπτωση (1%) γιατί κοντά σας λειτουργούν σταθμοί ΑΠΕ.", "type": "discount"},
    "Επιδότηση / ΤΕΜ": {"emoji": "🎁", "desc": "Κρατική Επιδότηση (Ταμείο Ενεργειακής Μετάβασης).", "type": "discount"},
    "Στρογγυλοποίηση": {"emoji": "⚖️", "desc": "Στρογγυλοποίηση ποσού.", "type": "fixed"},
    "Επιβράβευση Αντλ. Θερμ": {"emoji": "🎁", "desc": "Επιβράβευση Αντλίας Θερμότητας", "type": "discount"},
}

# ─────────────────────────────────────────────────────────────────
# ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ
# ─────────────────────────────────────────────────────────────────
def clean_number(s):
    s = s.strip()
    is_negative = False
    if s.startswith('-'):
        is_negative = True
        s = s[1:].strip()
    if '.' in s and ',' in s: 
        s = s.replace('.', '').replace(',', '.')
    elif '.' in s and ',' not in s:
        parts = s.split('.')
        if len(parts) == 2 and len(parts[1]) == 3: s = s.replace('.', '')
    elif ',' in s and '.' not in s: 
        s = s.replace(',', '.')
    try:
        val = float(s)
        return -val if is_negative else val
    except ValueError:
        return 0.0

def get_tariff_rates(text):
    t = text.lower()
    if "myhome enter two" in t: return 0.145, 0.095
    if "myhome enter" in t: return 0.145, 0.145
    if "myhomeonline" in t or "myhome online" in t: return 0.142, 0.132
    if "myhome4all" in t or "myhome 4all" in t: return 0.138, 0.115
    if "myhome4students" in t: return 0.129, 0.129
    if "myhome maxima" in t: return 0.132, 0.122
    if "γ1" in t or "γ1n" in t: return 0.145, 0.129
    return 0.160, 0.160 

def parse_dei_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc: text += page.get_text("text") + "\n"

    processed_text = text.replace("Bkwh", "8kWh").replace("B kwh", "8 kWh").replace("awn", "kWh")

    detected_day_rate, detected_night_rate = get_tariff_rates(processed_text)

    # 1. ΕΝΔΕΙΞΕΙΣ ΜΕΤΡΗΤΗ (Ημέρα & Νύχτα)
    day_kwh = 0.0
    night_kwh = 0.0
    
    meter_11 = re.findall(r'T\d+\s+11\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)', processed_text)
    meter_12 = re.findall(r'T\d+\s+12\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)', processed_text)
    
    if meter_11 or meter_12:
        day_kwh = sum(float(x) for x in meter_11)
        night_kwh = sum(float(x) for x in meter_12)
        total_kwh = day_kwh + night_kwh
    else:
        match = re.search(r'Κατανάλωση Ηλεκτρικής Ενέργειας\s+([\d\.,]+)\s*kWh', processed_text, re.IGNORECASE)
        if match: 
            total_kwh = clean_number(match.group(1))
            day_kwh = total_kwh 

    # 2. ΣΥΝΟΛΙΚΟ ΠΟΣΟ
    total_bill = 0.0
    for pattern in [r'Συνολικό\s+(?:πιστωτικό\s+υπόλοιπο|ποσό\s+πληρωμής)\s*(-?[\d\.,]+)\s*€?', r'ΠΙΣΤΩΤΙΚΟ\s+ΥΠΟΛΟΙΠΟ\s*(-?[\d\.,]+)\s*€?', r'\*\s*(-?[\d\.,]+)\s*€']:
        match = re.search(pattern, processed_text, re.IGNORECASE)
        if match:
            total_bill = clean_number(match.group(1))
            break

    # 3. ΣΑΡΩΣΗ ΧΡΕΩΣΕΩΝ
    all_charges = {}
    patterns = [
        (r'Χρεώσεις\s+Προμήθειας\s+ΔΕΗ[^\n]*', "Χρεώσεις Προμήθειας"),
        (r'Χρέωση\s*Ενέργειας\s*Κανονική[^\n]*', "Χρέωση Ενέργειας Κανονική"),
        (r'Χρέωση\s*Ενέργειας\s*Μειωμένη[^\n]*', "Χρέωση Ενέργειας Μειωμένη"),
        (r'Πάγια\s+Χρέωση[^\n]*', "Πάγια Χρέωση"),
        (r'Μηχανισμός\s+Διακύμανσης[^\n]*', "Μηχανισμός Διακύμανσης"),
        (r'Έκπτ\.?\s*πάγιας\s+εντολής[^\n]*', "Έκπτ. Πάγιας Εντολής"),
        (r'GreenPass[^\n]*', "GreenPass"),
        (r'ΑΔΜΗΕ[^\n]*', "ΑΔΜΗΕ: Σύστημα Μεταφοράς"),
        (r'ΔΕΔΔΗΕ[^\n]*', "ΔΕΔΔΗΕ: Δίκτυο Διανομής"),
        (r'ΥΚΩ[^\n]*', "ΥΚΩ"),
        (r'ΕΤΜΕΑΡ[^\n]*', "ΕΤΜΕΑΡ"),
        (r'Χρέωση\s+Μέτρησης[^\n]*', "Χρέωση Μέτρησης"),
        (r'Τέλος\s+Ανακύκλωσης[^\n]*', "Τέλος Ανακύκλωσης"),
        (r'ΕΡΤ\b[^\n]*', "ΕΡΤ"),
        (r'ΕΔΑΠ[^\n]*', "ΕΔΑΠ"),
        (r'Τέλος\s+ΑΠΕ[^\n]*', "Τέλος ΑΠΕ"),
        (r'Έκπτωση\s+λόγω\s+σταθμών\s+ΑΠΕ[^\n]*', "Έκπτωση Σταθμών ΑΠΕ"),
        (r'Επιβράβευση\s+Αντλ\.\s+Θερμ[^\n]*', "Επιβράβευση Αντλ. Θερμ"),
        (r'Επιβράβευση(?!\s+Αντλ)[^\n]*', "Επιδότηση / ΤΕΜ"),
        (r'Πιστώσεις\s+ΤΕΜ[^\n]*', "Επιδότηση / ΤΕΜ"),
        (r'Στρογγ/ση\s+Πληρ\.\s+Ποσού[^\n]*', "Στρογγυλοποίηση"),
        (r'Ποσό\s+Στρογγ\.?Προηγ\.?Λογ\.[^\n]*', "Στρογγυλοποίηση"),
    ]
    
    for pattern, key in patterns:
        matches = re.finditer(pattern, processed_text, re.IGNORECASE)
        for match in matches:
            line_text = match.group(0)
            if key == "Επιβράβευση / ΤΕΜ" and "Αντλ" in line_text: continue 
            numbers = re.findall(r'-?\d+(?:[\.,]\d+)?', line_text)
            if numbers:
                val = clean_number(numbers[-1])
                if val != 0:
                    all_charges[key] = all_charges.get(key, 0.0) + val

    # 4. ΦΟΡΟΙ ΚΑΙ ΤΕΛΗ
    match_efk = re.search(r'ΕΦΚ\s*\(Ν\.3336/05\)[^\d\n]*([\d\.,]+)', processed_text, re.IGNORECASE)
    if match_efk: all_charges["ΕΦΚ"] = clean_number(match_efk.group(1))

    match_eidt = re.search(r'ΕΙΔ\.ΤΕΛ\.\s*50/00\s*Ν\.2093/92[^\d\n]*([\d\.,]+)', processed_text, re.IGNORECASE)
    if match_eidt: all_charges["Ειδικό Τέλος 5‰"] = clean_number(match_eidt.group(1))

    match_vat = re.search(r'ΦΠΑ\s+ΡΕΥΜΑΤΟΣ[^\d\n]*([\d\.,]+)\s*[xX×]\s*6%\s*(?:=)?\s*([\d\.,]+)', processed_text, re.IGNORECASE)
    if match_vat:
        all_charges["__vat_base__"] = clean_number(match_vat.group(1))
        all_charges["ΦΠΑ"] = clean_number(match_vat.group(2))
    else:
        m_vat2 = re.search(r'ΦΠΑ[^\d\n]{0,20}([\d\.,]+)', processed_text, re.IGNORECASE)
        if m_vat2: all_charges["ΦΠΑ"] = clean_number(m_vat2.group(1))

    match_dt = re.search(r'ΔΤ:[^\d\n]*?([\d\.,]+)(?:\s|$)', processed_text)
    if match_dt: all_charges["Δημοτικά Τέλη (ΔΤ)"] = clean_number(match_dt.group(1))
    
    match_df = re.search(r'ΔΦ:[^\d\n]*?([\d\.,]+)(?:\s|$)', processed_text)
    if match_df: all_charges["Δημοτικός Φόρος (ΔΦ)"] = clean_number(match_df.group(1))
    
    match_tap = re.search(r'ΤΑΠ[^\n]*?=\s*([\d\.,]+)', processed_text)
    if match_tap: all_charges["ΤΑΠ"] = clean_number(match_tap.group(1))

    # 5. KWH ΚΑΙ ΤΙΜΗ (Τιμολογηθείσα Ενέργεια)
    billed_kwh = 0.0
    exact_avg_rate = None
    
    supply_section = re.search(r'(?:Χρεώσεις Προμήθειας|Αναλυτικά οι χρεώσεις)(.*?)(?:Ρυθμιζόμενες Χρεώσεις|Έναντι Κατανάλωσης)', processed_text, re.IGNORECASE | re.DOTALL)
    if supply_section:
        for m in re.finditer(r'(\d+(?:[\.,]\d+)?)\s*[kK][wW][hH]\s*[xX×]\s*([\d,\.]+)', supply_section.group(1), re.IGNORECASE):
            try:
                k, r = float(m.group(1)), clean_number(m.group(2))
                if r >= 0.001: 
                    billed_kwh += k
                    exact_avg_rate = r
            except ValueError: pass

    # Απευθείας εύρεση Καθαρής Ενέργειας 
    explicit_energy = all_charges.get("Χρέωση Ενέργειας Κανονική", 0.0) + all_charges.get("Χρέωση Ενέργειας Μειωμένη", 0.0)
    explicit_energy = round(explicit_energy, 2)
    
    if explicit_energy > 0:
        pure_energy_cost = explicit_energy
    else:
        # Fallback αφαίρεσης παγίων εάν δεν υπάρχει αναλυτική χρέωση
        total_prom = all_charges.get("Χρεώσεις Προμήθειας", 0.0)
        pagia = all_charges.get("Πάγια Χρέωση", 0.0)
        ekpt_pagias = all_charges.get("Έκπτ. Πάγιας Εντολής", 0.0)
        greenpass = all_charges.get("GreenPass", 0.0)
        
        pure_energy_cost = round(total_prom - pagia - ekpt_pagias - greenpass, 2)
        if pure_energy_cost <= 0: pure_energy_cost = 0.0

    # Έξυπνη διόρθωση Billed kWh εάν το OCR απέτυχε στα νούμερα
    if pure_energy_cost > 0 and billed_kwh == 0:
        rate_to_use = exact_avg_rate if exact_avg_rate else detected_day_rate
        billed_kwh = round(pure_energy_cost / rate_to_use)

    return total_kwh, day_kwh, night_kwh, billed_kwh, pure_energy_cost, total_bill, detected_day_rate, detected_night_rate, all_charges


# ─────────────────────────────────────────────────────────────────
# UI APP RENDERING
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="app-header">', unsafe_allow_html=True)
st.markdown('<div class="app-title">Net Metering Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Ολοκληρωμένη Ανάλυση Ενέργειας, Κερδών και Μαθηματική Επαλήθευση Λογαριασμού ΔΕΗ</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

col_upload, col_input1, col_input2 = st.columns([2, 1, 1], gap="large")

with col_upload:
    uploaded_file = st.file_uploader("📄 Ανεβάστε το PDF του λογαριασμού σας", type="pdf")

with col_input1:
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_day_rate = st.number_input("☀️ Τιμή Ημέρας (€/kWh)", value=0.1450, format="%.4f", help="Εισάγετε τη χρέωση Κανονικής Ζώνης βάσει συμβολαίου. Προσαρμόζεται αυτόματα ανάλογα με το τιμολόγιο που ανεβάζετε.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_input2:
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_night_rate = st.number_input("🌙 Τιμή Νύχτας (€/kWh)", value=0.0950, format="%.4f", help="Εισάγετε τη χρέωση Μειωμένης Ζώνης βάσει συμβολαίου (αν έχετε νυχτερινό).")
    st.markdown('</div>', unsafe_allow_html=True)


if uploaded_file is not None:
    file_bytes = uploaded_file.read()

    with st.spinner('Ανάλυση Μετρητή & Δυναμική Σάρωση Χρεώσεων...'):
        try:
            (total_kwh, day_kwh, night_kwh, billed_kwh, pure_energy_cost, total_bill, 
             detected_day_rate, detected_night_rate, all_charges) = parse_dei_pdf(file_bytes)

            if not total_kwh and not total_bill:
                st.error("Δεν ήταν δυνατή η ανάγνωση των Ενδείξεων. Ελέγξτε αν το αρχείο είναι έγκυρο PDF της ΔΕΗ.")
            else:
                # Χρησιμοποιούμε τις τιμές του χρήστη (οι οποίες μπορούν να τροποποιηθούν στο UI)
                hidden_kwh = max(0.0, total_kwh - billed_kwh)

                VAT_RATE = 0.06
                
                # Διαχωρισμός ημέρας/νύχτας για τον υπολογισμό του κέρδους
                if hidden_kwh >= day_kwh:
                    hidden_day = day_kwh
                    hidden_night = hidden_kwh - day_kwh
                else:
                    hidden_day = hidden_kwh
                    hidden_night = 0.0

                saved_energy_day = hidden_day * user_day_rate
                saved_energy_night = hidden_night * user_night_rate
                saved_energy = saved_energy_day + saved_energy_night
                saved_vat = saved_energy * VAT_RATE
                total_saved = saved_energy + saved_vat

                # --- TOP METRICS ---
                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-card">
                        <div class="metric-label">Πληρωτεο Ποσο Λογαριασμου</div>
                        <div class="metric-value text-blue">{total_bill:.2f} €</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Συνολο Μετρητη (Παραχθεισα/Καταναλωθεισα)</div>
                        <div class="metric-value">{total_kwh:.0f} <span style="font-size:1rem; color:#94A3B8;">kWh</span></div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Τιμολογηθησα Ενεργεια (Απο Δικτυο)</div>
                        <div class="metric-value text-orange">{billed_kwh:.0f} <span style="font-size:1rem; color:#94A3B8;">kWh</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # --- HERO SAVINGS BANNER ---
                if hidden_kwh > 0:
                    st.markdown(f"""
                    <div class="hero-card">
                        <div class="hero-label">ΚΑΘΑΡΟ ΚΕΡΔΟΣ ΑΠΟ ΤΟ ΦΩΤΟΒΟΛΤΑΪΚΟ ΣΑΣ</div>
                        <div class="hero-amount">+{total_saved:.2f} €</div>
                        <div class="hero-tags">
                            <span class="tag">☀️ Μη Τιμολογηθείσες (Ημέρας): {hidden_day:.0f} kWh</span>
                            <span class="tag">🌙 Μη Τιμολογηθείσες (Νύχτας): {hidden_night:.0f} kWh</span>
                            <span class="tag">💶 Αξία Καθαρής Ενέργειας: {saved_energy:.2f} €</span>
                            <span class="tag">🧾 Γλιτωμένος ΦΠΑ (6%): {saved_vat:.2f} €</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Δεν εντοπίστηκε έκπτωση Net Metering. Όλες οι kWh του μετρητή τιμολογήθηκαν.")

                if total_bill < 0:
                    st.info(f"🎉 **Ο λογαριασμός σας είναι πιστωτικός!** Η ΔΕΗ σάς επιστρέφει **{abs(total_bill):.2f} €**.")

                # --- COLUMNS FOR CHARGES ---
                col_left, col_right = st.columns(2, gap="large")

                with col_left:
                    st.markdown('<div class="section-title">⚡ Ενέργεια & Net Metering</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="list-item" style="border-color: #10B981;">
                        <div class="list-item-left">
                            <div class="list-item-title">⚡ Αξία Μη Τιμολογηθείσας Ενέργειας</div>
                            <div class="list-item-desc">Το ποσό του ρεύματος που γλιτώσατε λόγω Φ/Β</div>
                        </div>
                        <div class="list-item-amount text-green">{saved_energy:.2f} €</div>
                    </div>
                    <div class="list-item" style="border-color: #F5A623;">
                        <div class="list-item-left">
                            <div class="list-item-title">⚡ Αξία Τιμολογηθείσας Ενέργειας</div>
                            <div class="list-item-desc">Το κόστος ρεύματος που τελικά χρεωθήκατε ({billed_kwh:.0f} kWh)</div>
                        </div>
                        <div class="list-item-amount text-orange">{pure_energy_cost:.2f} €</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_right:
                    st.markdown('<div class="section-title">📋 Αναλυτικές Χρεώσεις Λογαριασμού</div>', unsafe_allow_html=True)
                    standard_html = ""
                    
                    for charge_name, amount in all_charges.items():
                        if charge_name in ["Χρεώσεις Προμήθειας", "Χρέωση Ενέργειας Κανονική", "Χρέωση Ενέργειας Μειωμένη"] or charge_name.startswith("__") or amount == 0: 
                            continue
                            
                        info = CHARGE_INFO.get(charge_name, {"emoji": "📋", "desc": "Πρόσθετη Χρέωση"})
                        amount_color = "text-green" if amount < 0 else "text-normal"
                        sign = "+" if amount > 0 else ""
                        
                        standard_html += f"""
                        <div class="list-item">
                            <div class="list-item-left">
                                <div class="list-item-title">{info['emoji']} {charge_name}</div>
                                <div class="list-item-desc">{info['desc']}</div>
                            </div>
                            <div class="list-item-amount {amount_color}">{sign}{amount:.2f} €</div>
                        </div>
                        """
                    st.markdown(standard_html, unsafe_allow_html=True)

                # --- ΜΑΘΗΜΑΤΙΚΟ ΓΛΩΣΣΑΡΙ ---
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.markdown('<div class="section-title">🧮 Γλωσσάρι & Μαθηματική Επαλήθευση (Πώς προέκυψε το κάθε ποσό)</div>', unsafe_allow_html=True)
                st.markdown("<p style='color:#94A3B8; margin-bottom:1.5rem;'>Το πρόγραμμα έκανε αντίστροφα τα μαθηματικά για να σας αποδείξει πώς ακριβώς χρεωθήκατε την κάθε κατηγορία βάσει της ΔΕΗ.</p>", unsafe_allow_html=True)

                math_html = ""
                
                for charge_name, val in all_charges.items():
                    if charge_name == "Χρεώσεις Προμήθειας" or charge_name.startswith("__") or val == 0:
                        continue
                        
                    info = CHARGE_INFO.get(charge_name, {"emoji": "📌", "desc": "Πρόσθετη Χρέωση", "type": "fixed"})
                    c_type = info.get("type", "fixed")
                    
                    if c_type == "per_kwh" and total_kwh > 0:
                        rate = abs(val) / total_kwh
                        formula = f"{total_kwh:.0f} kWh × {rate:.5f} €/kWh = {val:.2f} €"
                        text = "Η χρέωση υπολογίζεται <b>επί των συνολικών kWh του μετρητή</b> (δηλαδή όλο το ρεύμα που καταναλώσατε). Το Net Metering <u>δεν σας απαλλάσσει</u> από αυτό το κόστος."
                        
                    elif c_type == "percentage_6":
                        base = all_charges.get('__vat_base__', 0)
                        if base > 0:
                            formula = f"{base:.2f} € × 6% = {val:.2f} €"
                        else:
                            formula = f"Βάση Υπολογισμού × 6% = {val:.2f} €"
                        text = "Ο ΦΠΑ υπολογίζεται προσθέτοντας την αξία της Ενέργειας, τις Ρυθμιζόμενες Χρεώσεις και τον ΕΦΚ, και πολλαπλασιάζοντας με το 6%."
                        
                    elif c_type == "percentage_5":
                        formula = f"Βάση Υπολογισμού × 0.5% = {val:.2f} €"
                        text = "Ειδικό τέλος (Νόμος 2093/92). Προκύπτει πολλαπλασιάζοντας την αξία ρεύματος, τις ρυθμιζόμενες και τον ΕΦΚ επί 5 τοις χιλίοις."
                        
                    elif c_type == "municipal":
                        formula = f"Τετραγωνικά (τ.μ.) × Τιμή Ζώνης Δήμου"
                        text = "Η χρέωση αυτή αφορά το Δήμο σας. Δεν έχει καμία σχέση με το ρεύμα ή τις kWh. Υπολογίζεται βάσει των τετραγωνικών μέτρων του σπιτιού και των ημερών του λογαριασμού."
                        
                    elif c_type == "ert":
                        formula = f"3,00 € / μήνα × Ημέρες λογαριασμού"
                        text = "Το ανταποδοτικό τέλος της ΕΡΤ είναι σταθερό στα 3€ το μήνα. Το ποσό προσαρμόζεται ανάλογα με το πόσες μέρες αφορά ο λογαριασμός σας."
                        
                    elif c_type == "energy":
                        formula = f"Τιμολογηθείσες kWh × Τιμή ρεύματος"
                        text = "Η καθαρή αξία της ενέργειας που τραβήξατε από το δίκτυο (χωρίς πάγια και φόρους)."

                    elif c_type == "discount" or val < 0:
                        formula = f"{val:.2f} €"
                        text = "Πρόκειται για έκπτωση (αρνητικό πρόσημο) που αφαιρείται απευθείας από το τελικό ποσό του λογαριασμού σας."
                        
                    else:
                        formula = f"{val:.2f} €"
                        text = "Πρόκειται για σταθερό ποσό ή χρέωση που προκύπτει αυτοτελώς (π.χ. πάγιο βάσει συμβολαίου)."

                    math_html += f"""
                    <div class="math-container">
                        <div class="math-header">{info['emoji']} {charge_name}</div>
                        <div class="math-body">
                            <b>Τι είναι:</b> {info['desc']}<br>
                            <span style="color:#A1A1AA; display:inline-block; margin-top:4px;">{text}</span>
                        </div>
                        <div class="math-formula">{formula}</div>
                    </div>
                    """
                    
                st.markdown(math_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Σφάλμα κατά την ανάλυση: {e}")

# ── ΥΠΟΓΡΑΦΗ ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; padding: 2rem 0; color: #64748B;'>
  <div style='font-size:0.9rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;'>Αναπτυχθηκε απο την</div>
  <div style='font-size:1.4rem; font-weight:800; color:#FFFFFF; letter-spacing: -0.5px;'>Zarkolia Health</div>
  <div style='font-size:0.9rem; margin-top: 4px;'>Πάνος Ζαρογουλίδης • Φαρμακοποιός MSc, MBA, Διαμεσολαβητής</div>
</div>
""", unsafe_allow_html=True)
