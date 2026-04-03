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

/* Typography */
.app-header {
    text-align: center;
    padding: 2rem 0 2rem 0;
}
.app-title {
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(90deg, #38BDF8, #818CF8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.app-subtitle {
    font-size: 1.1rem;
    color: #94A3B8;
    font-weight: 400;
}

/* User Input Box */
.input-container {
    background: #1E293B;
    border: 1px solid #3B82F6;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1);
}

/* Metric Cards */
.metric-row {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}
.metric-card {
    flex: 1;
    min-width: 200px;
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 1.5rem;
    transition: transform 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    border-color: #475569;
}
.metric-label {
    font-size: 0.85rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #F8FAFC;
    font-family: 'Fira Code', monospace;
}
.text-green { color: #10B981 !important; }
.text-blue { color: #38BDF8 !important; }
.text-orange { color: #F5A623 !important; }
.text-red { color: #EF4444 !important; }

/* The Hero Savings Card */
.hero-card {
    background: linear-gradient(145deg, #064E3B 0%, #022C22 100%);
    border: 1px solid #047857;
    border-radius: 24px;
    padding: 3rem 2rem;
    text-align: center;
    margin-bottom: 3rem;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
}
.hero-label {
    font-size: 1.1rem;
    color: #A7F3D0;
    font-weight: 500;
    margin-bottom: 1rem;
}
.hero-amount {
    font-size: 4.5rem;
    font-weight: 800;
    color: #10B981;
    line-height: 1;
    letter-spacing: -2px;
    margin-bottom: 1.5rem;
    font-family: 'Fira Code', monospace;
}
.hero-tags {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}
.tag {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    color: #6EE7B7;
    padding: 0.5rem 1rem;
    border-radius: 99px;
    font-size: 0.9rem;
    font-weight: 500;
}

/* VAT Compare Card */
.vat-card {
    background: #1E293B;
    border: 1px dashed #3B82F6;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    text-align: center;
}
.vat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-top: 1rem;
}
.vat-box {
    background: #0F172A;
    padding: 1rem;
    border-radius: 12px;
    border: 1px solid #334155;
}

/* Clean List Cards for Charges */
.section-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #334155;
}
.list-item {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.list-item-left {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}
.list-item-title {
    font-size: 1rem;
    font-weight: 600;
    color: #E2E8F0;
}
.list-item-desc {
    font-size: 0.8rem;
    color: #64748B;
}
.list-item-amount {
    font-size: 1.2rem;
    font-weight: 700;
    font-family: 'Fira Code', monospace;
}
.text-normal { color: #F8FAFC; }

/* Math Box */
.math-container {
    background: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.math-header {
    font-weight: 600;
    color: #38BDF8;
    font-size: 1.05rem;
    margin-bottom: 0.5rem;
}
.math-body {
    color: #94A3B8;
    font-size: 0.9rem;
    line-height: 1.6;
}
.math-formula {
    background: #1E293B;
    padding: 0.75rem;
    border-radius: 8px;
    font-family: monospace;
    color: #E2E8F0;
    margin-top: 0.75rem;
    border: 1px solid #334155;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ΒΙΒΛΙΟΘΗΚΗ ΕΞΗΓΗΣΕΩΝ ΧΡΕΩΣΕΩΝ
# ─────────────────────────────────────────────────────────────────
CHARGE_INFO = {
    "ΕΤΜΕΑΡ": {"emoji": "🌱", "desc": "Ειδικό Τέλος υπέρ ΑΠΕ", "affected_by_pv": False},
    "ΥΚΩ": {"emoji": "🏝️", "desc": "Υπηρεσίες Κοινής Ωφέλειας (Επιδότηση νησιών κ.ά.)", "affected_by_pv": False},
    "ΑΔΜΗΕ: Σύστημα Μεταφοράς": {"emoji": "🔌", "desc": "Δίκτυο Υψηλής Τάσης", "affected_by_pv": False},
    "Χρέωση Χρήσης Συστήματος": {"emoji": "🔌", "desc": "Δίκτυο Υψηλής Τάσης (ΑΔΜΗΕ)", "affected_by_pv": False},
    "ΔΕΔΔΗΕ: Δίκτυο Διανομής": {"emoji": "🔌", "desc": "Δίκτυο Διανομής Γειτονιάς", "affected_by_pv": False},
    "Χρέωση Χρήσης Δικτύου": {"emoji": "🔌", "desc": "Δίκτυο Διανομής Γειτονιάς (ΔΕΔΔΗΕ)", "affected_by_pv": False},
    "Χρέωση Μέτρησης": {"emoji": "📟", "desc": "Πάγιο χρήσης μετρητή", "affected_by_pv": False},
    "Πάγια Χρέωση": {"emoji": "📋", "desc": "Σταθερό μηνιαίο πάγιο ΔΕΗ", "affected_by_pv": False},
    "Τέλος Ανακύκλωσης": {"emoji": "♻️", "desc": "Τέλος ανακύκλωσης συσκευών", "affected_by_pv": False},
    "ΕΦΚ": {"emoji": "🏛️", "desc": "Ειδικός Φόρος Κατανάλωσης (0.0022 €/kWh)", "affected_by_pv": False},
    "Ειδικό Τέλος 5‰": {"emoji": "🏛️", "desc": "Ειδικό Τέλος 5/1000 (Ν.2093/92)", "affected_by_pv": False},
    "Τέλος ΑΠΕ": {"emoji": "🌱", "desc": "Τέλος υπέρ Ανανεώσιμων Πηγών", "affected_by_pv": False},
    "ΕΔΑΠ": {"emoji": "🏛️", "desc": "Διαχειριστική Αμοιβή ΛΑΓΗΕ", "affected_by_pv": False},
    "Δημοτικά Τέλη (ΔΤ)": {"emoji": "🗑️", "desc": "Τέλη καθαριότητας & φωτισμού", "affected_by_pv": False},
    "Δημοτικός Φόρος (ΔΦ)": {"emoji": "🏛️", "desc": "Φόρος ηλεκτροδοτούμενων χώρων", "affected_by_pv": False},
    "ΤΑΠ": {"emoji": "🏠", "desc": "Τέλος Ακίνητης Περιουσίας", "affected_by_pv": False},
    "ΕΡΤ": {"emoji": "📺", "desc": "Ανταποδοτικό Τέλος ΕΡΤ", "affected_by_pv": False},
    "Έκπτ. Πάγιας Εντολής": {"emoji": "🏷️", "desc": "Έκπτωση λόγω εξόφλησης μέσω πάγιας εντολής", "affected_by_pv": False},
    "GreenPass": {"emoji": "🌿", "desc": "Χρέωση για εγγύηση προέλευσης ενέργειας από ΑΠΕ", "affected_by_pv": False},
    "Έκπτωση Σταθμών ΑΠΕ": {"emoji": "☀️", "desc": "Ειδική έκπτωση στους λογαριασμούς (ΑΠΕ 1%)", "affected_by_pv": False},
    "Επιδότηση / Επιβράβευση": {"emoji": "🎁", "desc": "Κρατική Επιδότηση ή Επιβράβευση", "affected_by_pv": False},
    "Στρογγυλοποίηση": {"emoji": "⚖️", "desc": "Στρογγυλοποίηση τρέχοντος ή προηγούμενου λογαριασμού", "affected_by_pv": False},
    "Λοιπές Εκπτώσεις": {"emoji": "🏷️", "desc": "Εκπτώσεις συνέπειας ή άλλα προωθητικά", "affected_by_pv": False},
    "ΦΠΑ": {"emoji": "🧾", "desc": "ΦΠΑ 6%", "affected_by_pv": False},
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

def get_tariff_rate_from_text(text):
    """Ανιχνεύει το όνομα του τιμολογίου και επιστρέφει την προεπιλεγμένη τιμή κιλοβατώρας."""
    text_lower = text.lower()
    if "myhome enter two" in text_lower: return 0.145
    if "myhome enter" in text_lower: return 0.145
    if "myhomeonline" in text_lower or "myhome online" in text_lower: return 0.142
    if "myhome4all" in text_lower or "myhome 4all" in text_lower: return 0.138
    if "myhome4students" in text_lower: return 0.129
    if "myhome maxima" in text_lower: return 0.132
    return 0.160 # Γενικό Fallback αν δεν βρεθεί τίποτα

def parse_dei_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc: text += page.get_text("text") + "\n"

    processed_text = text.replace("Bkwh", "8kWh").replace("B kwh", "8 kWh").replace("awn", "kWh")

    # --- 0. ΑΝΙΧΝΕΥΣΗ ΤΙΜΟΛΟΓΙΟΥ ---
    detected_rate = get_tariff_rate_from_text(processed_text)

    # --- 1. ΕΝΔΕΙΞΕΙΣ ΜΕΤΡΗΤΗ ---
    total_kwh = 0.0
    meter_totals = re.findall(r'T\d+\s+1[12]\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)', processed_text)
    if meter_totals:
        total_kwh = sum(float(x) for x in meter_totals)
    else:
        match = re.search(r'Κατανάλωση Ηλεκτρικής Ενέργειας\s+([\d\.,]+)\s*kWh', processed_text, re.IGNORECASE)
        if match: total_kwh = clean_number(match.group(1))

    # --- 2. ΣΥΝΟΛΙΚΟ ΠΟΣΟ ΛΟΓΑΡΙΑΣΜΟΥ ---
    total_bill = 0.0
    for pattern in [r'Συνολικό\s+(?:πιστωτικό\s+υπόλοιπο|ποσό\s+πληρωμής)\s*(-?[\d\.,]+)\s*€?', r'ΠΙΣΤΩΤΙΚΟ\s+ΥΠΟΛΟΙΠΟ\s*(-?[\d\.,]+)\s*€?', r'\*\s*(-?[\d\.,]+)\s*€']:
        match = re.search(pattern, processed_text, re.IGNORECASE)
        if match:
            total_bill = clean_number(match.group(1))
            break

    # --- 3. ΣΑΡΩΣΗ ΟΛΩΝ ΤΩΝ ΜΠΛΕ & ΓΚΡΙ ΠΙΝΑΚΩΝ ---
    all_charges = {}
    
    patterns = [
        (r'Χρεώσεις\s+Προμήθειας\s+ΔΕΗ[^\n]*', "Χρεώσεις Προμήθειας"),
        (r'Πάγια\s+Χρέωση[^\n]*', "Πάγια Χρέωση"),
        (r'Έκπτ\.?\s*πάγιας\s+εντολής[^\n]*', "Έκπτ. Πάγιας Εντολής"),
        (r'GreenPass[^\n]*', "GreenPass"),
        (r'ΑΔΜΗΕ[^\n]*', "ΑΔΜΗΕ: Σύστημα Μεταφοράς"),
        (r'ΔΕΔΔΗΕ[^\n]*', "ΔΕΔΔΗΕ: Δίκτυο Διανομής"),
        (r'ΥΚΩ[^\n]*', "ΥΚΩ"),
        (r'ΕΤΜΕΑΡ[^\n]*', "ΕΤΜΕΑΡ"),
        (r'Χρέωση\s+Χρήσης\s+Συστήματος[^\n]*', "Χρέωση Χρήσης Συστήματος"),
        (r'Χρέωση\s+Χρήσης\s+Δικτύου[^\n]*', "Χρέωση Χρήσης Δικτύου"),
        (r'Χρέωση\s+Μέτρησης[^\n]*', "Χρέωση Μέτρησης"),
        (r'ΕΔΑΠ[^\n]*', "ΕΔΑΠ"),
        (r'Τέλος\s+ΑΠΕ[^\n]*', "Τέλος ΑΠΕ"),
        (r'Τέλος\s+Ανακύκλωσης[^\n]*', "Τέλος Ανακύκλωσης"),
        (r'ΕΡΤ\b[^\n]*', "ΕΡΤ"),
        (r'Έκπτωση\s+λόγω\s+σταθμών\s+ΑΠΕ[^\n]*', "Έκπτωση Σταθμών ΑΠΕ"),
        (r'Επιβράβευση[^\n]*', "Επιδότηση / Επιβράβευση"),
        (r'Πιστώσεις\s+ΤΕΜ[^\n]*', "Επιδότηση / Επιβράβευση"),
        (r'Στρογγ/ση\s+Πληρ\.\s+Ποσού[^\n]*', "Στρογγυλοποίηση"),
        (r'Ποσό\s+Στρογγ\.?Προηγ\.?Λογ\.[^\n]*', "Στρογγυλοποίηση"),
        (r'Έκπτωση\s+Συνέπειας[^\n]*', "Λοιπές Εκπτώσεις"),
    ]
    
    for pattern, key in patterns:
        matches = re.finditer(pattern, processed_text, re.IGNORECASE)
        for match in matches:
            line_text = match.group(0)
            numbers = re.findall(r'-?\d+(?:[\.,]\d+)?', line_text)
            if numbers:
                val = clean_number(numbers[-1])
                if val != 0:
                    if key in all_charges:
                        all_charges[key] += val
                    else:
                        all_charges[key] = val

    # --- 4. ΠΙΝΑΚΑΣ "ΔΙΑΦΟΡΑ" (ΕΦΚ & ΕΙΔ. ΤΕΛ.) ---
    match_efk = re.search(r'ΕΦΚ\s*\(Ν\.3336/05\)[^\d\n]*([\d\.,]+)', processed_text, re.IGNORECASE)
    if match_efk: all_charges["ΕΦΚ"] = clean_number(match_efk.group(1))

    match_eidt = re.search(r'ΕΙΔ\.ΤΕΛ\.\s*50/00\s*Ν\.2093/92[^\d\n]*([\d\.,]+)', processed_text, re.IGNORECASE)
    if match_eidt: all_charges["Ειδικό Τέλος 5‰"] = clean_number(match_eidt.group(1))

    # --- 5. ΠΙΝΑΚΑΣ "ΦΠΑ" ---
    vat_amount = 0.0
    match_vat = re.search(r'ΦΠΑ\s+ΡΕΥΜΑΤΟΣ[^\d\n]*([\d\.,]+)\s*[xX×]\s*6%\s*(?:=)?\s*([\d\.,]+)', processed_text, re.IGNORECASE)
    if match_vat:
        all_charges["__vat_base__"] = clean_number(match_vat.group(1))
        vat_amount = clean_number(match_vat.group(2))
    elif "ΦΠΑ" not in all_charges:
        m_vat2 = re.search(r'ΦΠΑ[^\d\n]{0,20}([\d\.,]+)', processed_text, re.IGNORECASE)
        if m_vat2: vat_amount = clean_number(m_vat2.group(1))
    
    if vat_amount != 0:
        all_charges["ΦΠΑ"] = vat_amount

    # --- 6. ΠΙΝΑΚΑΣ "ΔΗΜΟΣ" (ΔΤ, ΔΦ, ΤΑΠ) ---
    match_dt = re.search(r'ΔΤ:[^\d\n]*?([\d\.,]+)(?:\s|$)', processed_text)
    if match_dt: all_charges["Δημοτικά Τέλη (ΔΤ)"] = clean_number(match_dt.group(1))
    
    match_df = re.search(r'ΔΦ:[^\d\n]*?([\d\.,]+)(?:\s|$)', processed_text)
    if match_df: all_charges["Δημοτικός Φόρος (ΔΦ)"] = clean_number(match_df.group(1))
    
    match_tap = re.search(r'ΤΑΠ[^\n]*?=\s*([\d\.,]+)', processed_text)
    if match_tap: all_charges["ΤΑΠ"] = clean_number(match_tap.group(1))

    # --- 7. ΕΞΑΓΩΓΗ ΤΙΜΟΛΟΓΗΜΕΝΩΝ KWH Ή ΚΑΘΑΡΗΣ ΕΝΕΡΓΕΙΑΣ ---
    billed_kwh = 0.0
    exact_avg_rate = None

    supply_section = re.search(r'Αναλυτικά οι χρεώσεις(.*?)Ρυθμιζόμενες\s*Χρεώσεις', processed_text, re.IGNORECASE | re.DOTALL)
    if supply_section:
        for m in re.finditer(r'\(?\s*(\d+)\s*[kK][wW][hH]\s*[xX×]\s*([\d,\.]+)\s*€?/?\s*[kK][wW][hH]\s*\)?', supply_section.group(1), re.IGNORECASE):
            try:
                k, r = float(m.group(1)), clean_number(m.group(2))
                if r >= 0.001: 
                    billed_kwh += k
                    exact_avg_rate = r
            except ValueError: pass

    total_prom = all_charges.get("Χρεώσεις Προμήθειας", 0.0)
    pagia = all_charges.get("Πάγια Χρέωση", 0.0)
    ekpt_pagias = all_charges.get("Έκπτ. Πάγιας Εντολής", 0.0)
    greenpass = all_charges.get("GreenPass", 0.0)
    
    pure_energy_cost = total_prom - pagia - ekpt_pagias - greenpass
    pure_energy_cost = round(pure_energy_cost, 2)
    
    if pure_energy_cost <= 0:
        pure_energy_cost = 0.0
        billed_kwh = 0.0 

    return total_kwh, billed_kwh, pure_energy_cost, total_bill, exact_avg_rate, detected_rate, all_charges


# ─────────────────────────────────────────────────────────────────
# UI APP RENDERING
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="app-header">', unsafe_allow_html=True)
st.markdown('<div class="app-title">Net Metering Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Ανάλυση Ενέργειας, Κερδών και Φορολογικών Χρεώσεων ΔΕΗ</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

col_upload, col_input = st.columns([1, 1], gap="large")

with col_upload:
    uploaded_file = st.file_uploader("📄 Ανεβάστε το PDF του λογαριασμού σας", type="pdf")

with col_input:
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_rate = st.number_input(
        "⚡ Τιμή Ενέργειας Συμβολαίου (€/kWh)", 
        value=0.1600, 
        format="%.4f",
        help="Η τιμή της κιλοβατώρας βάσει του συμβολαίου σας (π.χ. 0.1250). Το πρόγραμμα ανιχνεύει αυτόματα το τιμολόγιό σας, αλλά μπορείτε να την αλλάξετε χειροκίνητα εάν επιθυμείτε."
    )
    st.markdown('</div>', unsafe_allow_html=True)


if uploaded_file is not None:
    file_bytes = uploaded_file.read()

    with st.spinner('Ανάλυση Μετρητή & Χρεώσεων...'):
        try:
            (total_kwh, billed_kwh, pure_energy_cost, total_bill,
             exact_avg_rate, detected_rate, all_charges) = parse_dei_pdf(file_bytes)

            if not total_kwh:
                st.error("Δεν ήταν δυνατή η ανάγνωση των Ενδείξεων του Μετρητή.")
            else:
                # Επιλογή Τιμής: Προτεραιότητα έχει το τι γράφει το PDF (exact), μετά η αυτόματη ανίχνευση (detected), μετά το user input.
                if exact_avg_rate:
                    final_rate = exact_avg_rate
                elif detected_rate != 0.160: # Αν βρήκε όντως όνομα τιμολογίου (π.χ. myHome Enter)
                    final_rate = detected_rate
                else:
                    final_rate = user_rate

                hidden_kwh = total_kwh - billed_kwh
                if hidden_kwh <= 0:
                    st.warning("⚠️ Δεν εντοπίστηκε έκπτωση Net Metering (Μηδενικό κέρδος).")
                else:
                    VAT_RATE = 0.06
                    
                    billed_energy_value = pure_energy_cost
                    billed_vat = billed_energy_value * VAT_RATE
                    
                    saved_energy = hidden_kwh * final_rate
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
                    st.markdown(f"""
                    <div class="hero-card">
                        <div class="hero-label">ΚΑΘΑΡΟ ΚΕΡΔΟΣ ΑΠΟ ΤΟ ΦΩΤΟΒΟΛΤΑΪΚΟ ΣΑΣ</div>
                        <div class="hero-amount">+{total_saved:.2f} €</div>
                        <div class="hero-tags">
                            <span class="tag">⚡ Μη Τιμολογηθείσες: {hidden_kwh:.0f} kWh</span>
                            <span class="tag">💶 Αξία Καθαρής Ενέργειας: {saved_energy:.2f} €</span>
                            <span class="tag">📊 Χρησιμοποιούμενη Τιμή: {final_rate:.4f} €/kWh</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if total_bill < 0:
                        st.info(f"🎉 **Ο λογαριασμός σας είναι πιστωτικός!** Η ΔΕΗ σάς επιστρέφει **{abs(total_bill):.2f} €**.")

                    # --- VAT COMPARISON CARD ---
                    st.markdown(f"""
                    <div class="vat-card">
                        <h4 style="color: #F8FAFC; margin-bottom: 0.5rem; font-weight: 700;">Ανάλυση Οφέλους Φ.Π.Α. (6%)</h4>
                        <p style="color: #94A3B8; font-size: 0.9rem; margin-bottom: 1rem;">Πόσο ΦΠΑ πληρώσατε για την ενέργεια που τραβήξατε, και πόσο ΦΠΑ γλιτώσατε χάρη στο Net Metering.</p>
                        <div class="vat-grid">
                            <div class="vat-box">
                                <div style="color: #F5A623; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 0.5rem; font-weight: 600;">ΦΠΑ που Τιμολογηθηκε</div>
                                <div style="font-size: 1.5rem; font-family: 'Fira Code', monospace; color: #F8FAFC; font-weight: 700;">{billed_vat:.2f} €</div>
                                <div style="font-size: 0.75rem; color: #64748B; margin-top: 0.3rem;">({billed_energy_value:.2f} € Καθαρή Ενέργεια × 6%)</div>
                            </div>
                            <div class="vat-box" style="border-color: #10B981; background: rgba(16, 185, 129, 0.05);">
                                <div style="color: #10B981; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 0.5rem; font-weight: 600;">ΦΠΑ που Γλιτωσατε (Κερδος)</div>
                                <div style="font-size: 1.5rem; font-family: 'Fira Code', monospace; color: #10B981; font-weight: 700;">+{saved_vat:.2f} €</div>
                                <div style="font-size: 0.75rem; color: #64748B; margin-top: 0.3rem;">({saved_energy:.2f} € Γλιτωμένη Ενέργεια × 6%)</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("---")

                    # --- COLUMNS FOR CHARGES ---
                    col_left, col_right = st.columns(2, gap="large")

                    with col_left:
                        st.markdown('<div class="section-title">⚡ Ενέργεια & Net Metering</div>', unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="list-item" style="border-color: #10B981;">
                            <div class="list-item-left">
                                <div class="list-item-title">⚡ Αξία Μη Τιμολογηθείσας Ενέργειας</div>
                                <div class="list-item-desc">Το ποσό που θα πληρώνατε χωρίς το Φ/Β</div>
                            </div>
                            <div class="list-item-amount text-green">{saved_energy:.2f} €</div>
                        </div>
                        <div class="list-item" style="border-color: #F5A623;">
                            <div class="list-item-left">
                                <div class="list-item-title">⚡ Αξία Τιμολογηθείσας Ενέργειας</div>
                                <div class="list-item-desc">Η καθαρή αξία της ενέργειας (Χωρίς Πάγια)</div>
                            </div>
                            <div class="list-item-amount text-orange">{billed_energy_value:.2f} €</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col_right:
                        st.markdown('<div class="section-title">📋 Αναλυτικές Χρεώσεις (Μπλε & Γκρι Πίνακες)</div>', unsafe_allow_html=True)
                        standard_html = ""
                        
                        if not all_charges:
                            standard_html = "<div style='color:#94A3B8; font-size:0.9rem;'>Δεν εντοπίστηκαν ρυθμιζόμενες χρεώσεις.</div>"
                        else:
                            for charge_name, amount in all_charges.items():
                                if charge_name == "Χρεώσεις Προμήθειας" or charge_name.startswith("__"): continue
                                
                                info = CHARGE_INFO.get(charge_name, {"emoji": "📋", "desc": "Πρόσθετη Χρέωση / Έκπτωση"})
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

                    # --- MATH VERIFICATION (ΔΥΝΑΜΙΚΗ ΑΠΕΙΚΟΝΙΣΗ ΟΛΩΝ ΤΩΝ ΧΡΕΩΣΕΩΝ) ---
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    st.markdown('<div class="section-title">🧮 Γλωσσάρι & Υπολογισμός ΟΛΩΝ των Χρεώσεων</div>', unsafe_allow_html=True)

                    abbreviations_info = {
                        "ΑΔΜΗΕ: Σύστημα Μεταφοράς": ("Α.Δ.Μ.Η.Ε.", "Δίκτυο Υψηλής Τάσης", True),
                        "Χρέωση Χρήσης Συστήματος": ("Α.Δ.Μ.Η.Ε.", "Δίκτυο Υψηλής Τάσης", True),
                        "ΔΕΔΔΗΕ: Δίκτυο Διανομής": ("Δ.Ε.Δ.Δ.Η.Ε.", "Δίκτυο Διανομής (Γειτονιάς)", True),
                        "Χρέωση Χρήσης Δικτύου": ("Δ.Ε.Δ.Δ.Η.Ε.", "Δίκτυο Διανομής (Γειτονιάς)", True),
                        "ΥΚΩ": ("Υ.Κ.Ω.", "Υπηρεσίες Κοινής Ωφέλειας (Επιδότηση νησιών)", True),
                        "ΕΤΜΕΑΡ": ("Ε.Τ.Μ.Ε.Α.Ρ.", "Ειδικό Τέλος υπέρ ΑΠΕ", True),
                        "ΕΦΚ": ("Ε.Φ.Κ.", "Ειδικός Φόρος Κατανάλωσης", True),
                        "Ειδικό Τέλος 5‰": ("ΕΙΔ. ΤΕΛΟΣ", "Ειδικό Τέλος 5/1000", False),
                        "ΕΔΑΠ": ("Ε.Δ.Α.Π.", "Διαχειριστική Αμοιβή ΛΑΓΗΕ", True),
                        "Τέλος ΑΠΕ": ("Α.Π.Ε.", "Τέλος Ανανεώσιμων Πηγών", True),
                        "Δημοτικά Τέλη (ΔΤ)": ("ΔΗΜΟΣ", "Δημοτικά Τέλη Καθαριότητας & Φωτισμού", False),
                        "Δημοτικός Φόρος (ΔΦ)": ("ΔΗΜΟΣ", "Δημοτικός Φόρος", False),
                        "ΤΑΠ": ("ΔΗΜΟΣ", "Τέλος Ακίνητης Περιουσίας", False),
                        "ΦΠΑ": ("Φ.Π.Α.", "Φόρος Προστιθέμενης Αξίας 6%", False)
                    }

                    math_html = ""
                    # Σαρώνουμε τη ΣΤΑΘΕΡΗ λίστα abbreviations_info αντί για τις τρέχουσες χρεώσεις!
                    for dict_key, (abbr, full_name, per_kwh) in abbreviations_info.items():
                        val = all_charges.get(dict_key, 0.0) # Παίρνει την τιμή αν υπάρχει, αλλιώς 0.0
                        
                        if dict_key == "ΦΠΑ":
                            vat_base = all_charges.get('__vat_base__', 0)
                            formula = f"{vat_base:.2f} € × 6% = {val:.2f} €"
                            text = "Υπολογίζεται επί της καθαρής αξίας ενέργειας και των ρυθμιζόμενων χρεώσεων."
                        elif per_kwh and total_kwh and total_kwh > 0:
                            rate = val / total_kwh
                            formula = f"{total_kwh:.0f} kWh × {rate:.5f} €/kWh = {val:.2f} €"
                            text = "Υπολογίζεται αυστηρά επί των συνολικών kWh του μετρητή. Το net metering δεν σας απαλλάσσει από αυτή τη χρέωση."
                        else:
                            formula = f"{val:.2f} €"
                            text = "Σταθερό ποσό ή υπολογιζόμενο βάσει των τετραγωνικών μέτρων του ακινήτου."

                        math_html += f"""
                        <div class="math-container">
                            <div class="math-header">{abbr} — {full_name}</div>
                            <div class="math-body">{text}</div>
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
