import streamlit as st
import fitz  # PyMuPDF
import re

# ─────────────────────────────────────────────────────────────────
# ΣΕΛΙΔΑ & ΣΤΥΛ
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Φ/Β Κέρδος Net Metering",
    page_icon="☀️",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #F5A623;
    margin-bottom: 0.2rem;
}

.subtitle {
    font-size: 1rem;
    color: #aaa;
    margin-bottom: 2rem;
}

.input-container {
    background: #111827;
    border: 1px solid #2d2d2d;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 20px;
}

.legend-box {
    background: #1a1a2e;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 18px 0;
    border-left: 4px solid #F5A623;
}

.legend-box h4 {
    color: #F5A623;
    margin: 0 0 10px 0;
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.legend-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 6px 0;
    font-size: 0.95rem;
    color: #ddd;
}

.dot-green { width: 12px; height: 12px; border-radius: 50%; background: #4CAF50; flex-shrink: 0; }
.dot-red   { width: 12px; height: 12px; border-radius: 50%; background: #F44336; flex-shrink: 0; }

.charge-card {
    background: #111827;
    border-radius: 14px;
    padding: 16px 20px;
    margin: 10px 0;
    border: 1px solid #2d2d2d;
    transition: border-color 0.2s;
}
.charge-card:hover { border-color: #F5A623; }

.charge-title {
    font-weight: 600;
    font-size: 1.05rem;
    color: #fff;
}

.charge-amount {
    font-family: 'DM Mono', monospace;
    font-size: 1.15rem;
    font-weight: 600;
}

.charge-amount-actual { color: #4CAF50; }
.charge-amount-hypo   { color: #F44336; }

.charge-desc {
    font-size: 0.88rem;
    color: #888;
    margin-top: 6px;
    line-height: 1.5;
}

.charge-formula {
    background: #1e2535;
    border-radius: 8px;
    padding: 8px 12px;
    margin-top: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    color: #7ec8e3;
}

.category-header {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #F5A623;
    margin: 24px 0 8px 0;
    padding-bottom: 4px;
    border-bottom: 1px solid #2d2d2d;
}

.savings-banner {
    background: linear-gradient(135deg, #1a3a1a, #0d2d0d);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    border: 1px solid #2d6a2d;
    margin: 20px 0;
}
.savings-amount {
    font-size: 2.8rem;
    font-weight: 700;
    color: #4CAF50;
    font-family: 'DM Mono', monospace;
}
.savings-label {
    font-size: 1rem;
    color: #aaa;
    margin-top: 4px;
}

.info-pill {
    display: inline-block;
    background: #1e2535;
    color: #7ec8e3;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.82rem;
    margin: 4px 2px;
    border: 1px solid #2a3a50;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">☀️ Υπολογιστής Net Metering</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ανεβάστε τον λογαριασμό της ΔΕΗ (PDF) για πλήρη ανάλυση κερδών και χρεώσεων</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ΒΙΒΛΙΟΘΗΚΗ ΕΞΗΓΗΣΕΩΝ & ΚΑΤΗΓΟΡΙΩΝ
# ─────────────────────────────────────────────────────────────────
CHARGE_INFO = {
    # ── Προμήθεια ──
    "Χρεώσεις Προμήθειας": {"category": "⚡ 1. Χρεώσεις Ενέργειας (Προμήθεια)", "emoji": "⚡", "desc": "Το κόστος του ρεύματος που καταναλώσατε.", "affected_by_pv": True, "type": "energy"},
    "Πάγια Χρέωση": {"category": "📋 2. Πάγιες Χρεώσεις", "emoji": "📋", "desc": "Σταθερό μηνιαίο ποσό.", "affected_by_pv": False, "type": "fixed"},
    "Μηχανισμός Διακύμανσης": {"category": "⚡ 1. Χρεώσεις Ενέργειας (Προμήθεια)", "emoji": "📈", "desc": "Χρέωση/Πίστωση βάσει Χρηματιστηρίου Ενέργειας.", "affected_by_pv": True, "type": "energy"},
    
    # ── Ρυθμιζόμενες ──
    "ΑΔΜΗΕ: Σύστημα Μεταφοράς": {"category": "🔌 3. Χρεώσεις Δικτύου (ΑΔΜΗΕ/ΔΕΔΔΗΕ)", "emoji": "🔌", "desc": "Κόστος χρήσης Δικτύου Υψηλής Τάσης.", "affected_by_pv": False, "type": "per_kwh"},
    "ΔΕΔΔΗΕ: Δίκτυο Διανομής": {"category": "🔌 3. Χρεώσεις Δικτύου (ΑΔΜΗΕ/ΔΕΔΔΗΕ)", "emoji": "🔌", "desc": "Κόστος χρήσης Δικτύου Διανομής.", "affected_by_pv": False, "type": "per_kwh"},
    "ΥΚΩ": {"category": "🏝️ 4. Υπηρεσίες Κοινής Ωφέλειας & ΑΠΕ", "emoji": "🏝️", "desc": "Επιδότηση νησιών και κοινωνικών τιμολογίων.", "affected_by_pv": False, "type": "per_kwh"},
    "ΕΤΜΕΑΡ": {"category": "🌱 4. Υπηρεσίες Κοινής Ωφέλειας & ΑΠΕ", "emoji": "🌱", "desc": "Ειδικό Τέλος Μείωσης Εκπομπών Αερίων Ρύπων.", "affected_by_pv": False, "type": "per_kwh"},
    "Χρέωση Μέτρησης": {"category": "📋 2. Πάγιες Χρεώσεις", "emoji": "📟", "desc": "Πάγιο για καταμέτρηση και συντήρηση μετρητή.", "affected_by_pv": False, "type": "fixed"},
    
    # ── Φόροι & Τέλη ──
    "ΕΦΚ": {"category": "🧾 5. Φόροι", "emoji": "🏛️", "desc": "Ειδικός Φόρος Κατανάλωσης (Σταθερός 0,0022€/kWh).", "affected_by_pv": False, "type": "efk"},
    "Ειδικό Τέλος 5‰": {"category": "🧾 5. Φόροι", "emoji": "🏛️", "desc": "Ειδικό Τέλος 0,5% (Ν.2093/92).", "affected_by_pv": False, "type": "eidiko_telos"},
    "ΦΠΑ": {"category": "🧾 5. Φόροι", "emoji": "🧾", "desc": "Φόρος Προστιθέμενης Αξίας 6%.", "affected_by_pv": True, "type": "vat"},
    "Τέλος Ανακύκλωσης": {"category": "📋 2. Πάγιες Χρεώσεις", "emoji": "♻️", "desc": "Τέλος υπέρ ανακύκλωσης συσκευών.", "affected_by_pv": False, "type": "fixed"},
    "Τέλος ΑΠΕ": {"category": "🌱 4. Υπηρεσίες Κοινής Ωφέλειας & ΑΠΕ", "emoji": "🌱", "desc": "Τέλος υπέρ Ανανεώσιμων Πηγών.", "affected_by_pv": False, "type": "per_kwh"},
    "ΕΔΑΠ": {"category": "🌱 4. Υπηρεσίες Κοινής Ωφέλειας & ΑΠΕ", "emoji": "🏛️", "desc": "Διαχειριστική Αμοιβή ΛΑΓΗΕ.", "affected_by_pv": False, "type": "per_kwh"},
    
    # ── Υπέρ Τρίτων ──
    "Δημοτικά Τέλη (ΔΤ)": {"category": "🏛️ 6. Χρεώσεις Υπέρ Τρίτων (Δήμος, ΕΡΤ)", "emoji": "🗑️", "desc": "Ανταποδοτικά τέλη καθαριότητας & φωτισμού.", "affected_by_pv": False, "type": "fixed"},
    "Δημοτικός Φόρος (ΔΦ)": {"category": "🏛️ 6. Χρεώσεις Υπέρ Τρίτων (Δήμος, ΕΡΤ)", "emoji": "🏛️", "desc": "Φόρος ηλεκτροδοτούμενων χώρων.", "affected_by_pv": False, "type": "fixed"},
    "ΤΑΠ": {"category": "🏛️ 6. Χρεώσεις Υπέρ Τρίτων (Δήμος, ΕΡΤ)", "emoji": "🏠", "desc": "Τέλος Ακίνητης Περιουσίας.", "affected_by_pv": False, "type": "fixed"},
    "ΕΡΤ": {"category": "🏛️ 6. Χρεώσεις Υπέρ Τρίτων (Δήμος, ΕΡΤ)", "emoji": "📺", "desc": "Ανταποδοτικό Τέλος ΕΡΤ.", "affected_by_pv": False, "type": "fixed"},
    
    # ── Εκπτώσεις / Λοιπά ──
    "Έκπτ. Πάγιας Εντολής": {"category": "🎁 7. Εκπτώσεις & Πιστώσεις", "emoji": "🏷️", "desc": "Έκπτωση εξόφλησης μέσω πάγιας εντολής.", "affected_by_pv": False, "type": "fixed"},
    "GreenPass": {"category": "📋 2. Πάγιες Χρεώσεις", "emoji": "🌿", "desc": "Εγγύηση Προέλευσης Πράσινης Ενέργειας.", "affected_by_pv": False, "type": "fixed"},
    "Έκπτωση Σταθμών ΑΠΕ": {"category": "🎁 7. Εκπτώσεις & Πιστώσεις", "emoji": "☀️", "desc": "Έκπτωση (1%) λόγω γειτνίασης με σταθμούς ΑΠΕ.", "affected_by_pv": False, "type": "fixed"},
    "Επιδότηση / ΤΕΜ": {"category": "🎁 7. Εκπτώσεις & Πιστώσεις", "emoji": "🎁", "desc": "Κρατική Επιδότηση.", "affected_by_pv": False, "type": "fixed"},
    "Στρογγυλοποίηση": {"category": "📋 2. Πάγιες Χρεώσεις", "emoji": "⚖️", "desc": "Στρογγυλοποίηση ποσού.", "affected_by_pv": False, "type": "fixed"},
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
    text_lower = text.lower()
    if "myhome enter two" in text_lower: return 0.145
    if "myhome enter" in text_lower: return 0.145
    if "myhomeonline" in text_lower or "myhome online" in text_lower: return 0.142
    if "myhome4all" in text_lower or "myhome 4all" in text_lower: return 0.138
    if "myhome4students" in text_lower: return 0.129
    if "myhome maxima" in text_lower: return 0.132
    return 0.160 

def parse_dei_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc: text += page.get_text("text") + "\n"

    processed_text = text.replace("Bkwh", "8kWh").replace("B kwh", "8 kWh").replace("awn", "kWh")
    detected_rate = get_tariff_rate_from_text(processed_text)

    # ── 1. ΕΝΔΕΙΞΕΙΣ ΜΕΤΡΗΤΗ ──
    total_kwh = 0.0
    meter_totals = re.findall(r'T\d+\s+1[12]\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)', processed_text)
    if meter_totals:
        total_kwh = sum(float(x) for x in meter_totals)
    else:
        match = re.search(r'Κατανάλωση Ηλεκτρικής Ενέργειας\s+([\d\.,]+)\s*kWh', processed_text, re.IGNORECASE)
        if match: total_kwh = clean_number(match.group(1))

    # ── 2. ΣΥΝΟΛΙΚΟ ΠΟΣΟ ──
    total_bill = 0.0
    for pattern in [r'Συνολικό\s+(?:πιστωτικό\s+υπόλοιπο|ποσό\s+πληρωμής)\s*(-?[\d\.,]+)\s*€?', r'ΠΙΣΤΩΤΙΚΟ\s+ΥΠΟΛΟΙΠΟ\s*(-?[\d\.,]+)\s*€?', r'\*\s*(-?[\d\.,]+)\s*€']:
        match = re.search(pattern, processed_text, re.IGNORECASE)
        if match:
            total_bill = clean_number(match.group(1))
            break

    # ── 3. ΣΑΡΩΣΗ ΧΡΕΩΣΕΩΝ ──
    all_charges = {}
    patterns = [
        (r'Χρεώσεις\s+Προμήθειας\s+ΔΕΗ[^\n]*', "Χρεώσεις Προμήθειας"),
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
        (r'Επιβράβευση[^\n]*', "Επιδότηση / ΤΕΜ"),
        (r'Πιστώσεις\s+ΤΕΜ[^\n]*', "Επιδότηση / ΤΕΜ"),
        (r'Στρογγ/ση\s+Πληρ\.\s+Ποσού[^\n]*', "Στρογγυλοποίηση"),
        (r'Ποσό\s+Στρογγ\.?Προηγ\.?Λογ\.[^\n]*', "Στρογγυλοποίηση"),
    ]
    
    for pattern, key in patterns:
        matches = re.finditer(pattern, processed_text, re.IGNORECASE)
        for match in matches:
            line_text = match.group(0)
            numbers = re.findall(r'-?\d+(?:[\.,]\d+)?', line_text)
            if numbers:
                val = clean_number(numbers[-1])
                if val != 0:
                    all_charges[key] = all_charges.get(key, 0.0) + val

    # ── 4. ΦΟΡΟΙ ΚΑΙ ΤΕΛΗ ──
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

    # ── 5. KWH ΚΑΙ ΤΙΜΗ ──
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
    
    pure_energy_cost = round(total_prom - pagia - ekpt_pagias - greenpass, 2)
    if pure_energy_cost <= 0: pure_energy_cost = 0.0
    
    if billed_kwh == 0 and pure_energy_cost > 0 and exact_avg_rate is None:
        billed_kwh = round(pure_energy_cost / detected_rate)
        exact_avg_rate = detected_rate

    return total_kwh, billed_kwh, pure_energy_cost, total_bill, exact_avg_rate, detected_rate, all_charges


# ─────────────────────────────────────────────────────────────────
# UI & ΛΟΓΙΚΗ
# ─────────────────────────────────────────────────────────────────
col_up, col_in = st.columns([1.5, 1])
with col_up:
    uploaded_file = st.file_uploader("📄 Επιλέξτε το PDF του λογαριασμού σας", type="pdf")
with col_in:
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_rate = st.number_input("⚡ Τιμή Ενέργειας Συμβολαίου (€/kWh)", value=0.1600, format="%.4f", 
                                help="Χρησιμοποιείται αν η κατανάλωση μηδενιστεί και το πρόγραμμα δεν βρει το όνομα του τιμολογίου στο PDF.")
    st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    file_bytes = uploaded_file.read()

    with st.spinner('🔍 Ανάλυση λογαριασμού & Μαθηματική Επαλήθευση...'):
        try:
            (total_kwh, billed_kwh, pure_energy_cost, total_bill,
             exact_avg_rate, detected_rate, all_charges) = parse_dei_pdf(file_bytes)

            if not total_kwh:
                st.error("❌ Δεν ήταν δυνατή η ανάγνωση των Ενδείξεων του Μετρητή.")
            else:
                final_rate = exact_avg_rate if exact_avg_rate else (detected_rate if detected_rate != 0.160 else user_rate)
                hidden_kwh = total_kwh - billed_kwh

                if hidden_kwh <= 0:
                    st.warning("⚠️ Δεν εντοπίστηκε απόκρυφη έκπτωση net metering.")
                else:
                    VAT_RATE = 0.06
                    saved_energy = hidden_kwh * final_rate
                    saved_vat = saved_energy * VAT_RATE
                    total_saved = saved_energy + saved_vat

                    actual_paid = total_bill
                    actual_energy_val = pure_energy_cost
                    hypo_energy_val = actual_energy_val + saved_energy
                    hypo_total_bill = actual_paid + total_saved

                    # ── ΚΕΡΔΟΣ BANNER ─────────────────────────────────────────
                    st.markdown(f"""
                    <div class="savings-banner">
                        <div class="savings-amount">+{total_saved:.2f} €</div>
                        <div class="savings-label">Συνολικό Καθαρό Κέρδος από το Φωτοβολταϊκό σας</div>
                        <div style="margin-top:14px; display:flex; gap:8px; justify-content:center; flex-wrap:wrap;">
                            <span class="info-pill">⚡ {hidden_kwh:.0f} kWh εξοικονομήθηκαν</span>
                            <span class="info-pill">💶 {saved_energy:.2f} € ενέργεια</span>
                            <span class="info-pill">🧾 {saved_vat:.2f} € ΦΠΑ</span>
                            <span class="info-pill">📊 Υπολογισμός με: {final_rate:.4f} €/kWh</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if actual_paid < 0:
                        st.info(f"ℹ️ Ο λογαριασμός σας είναι **πιστωτικός** ({actual_paid:.2f} €) — η ΔΕΗ σάς επιστρέφει χρήματα!")

                    # ── ΣΥΓΚΡΙΣΗ ΤΙΜΟΛΟΓΗΣΗΣ ──────────────────────────────────
                    st.markdown("### 📊 Σύγκριση Τιμολόγησης (Με vs Χωρίς Φ/Β)")
                    st.markdown("Τα **🟢 πράσινα** δείχνουν τι πληρώσατε, ενώ τα **🔴 κόκκινα** τι θα πληρώνατε χωρίς το σύστημα Net Metering.")

                    comparison_html = f"""
                    <div style="background:#111827; padding:20px; border-radius:16px; border:1px solid #2d2d2d; margin-bottom:25px;">
                      <table style="width:100%; border-collapse:collapse; font-family:'DM Sans',sans-serif;">
                        <tr style="border-bottom:1px solid #2d2d2d;">
                          <td style="padding:12px 0; color:#ccc;">⚡ <b>Τιμολογημένες kWh (Από Δίκτυο)</b></td>
                          <td style="text-align:right; padding:12px 0;">
                            <span style="color:#4CAF50; font-weight:700; font-size:1.2em;">{billed_kwh:.0f} kWh</span>
                            <span style="color:#F44336; margin-left:10px; font-size:0.95em;">({total_kwh:.0f} kWh)</span>
                          </td>
                        </tr>
                        <tr style="border-bottom:1px solid #2d2d2d;">
                          <td style="padding:12px 0; color:#ccc;">💶 <b>Αξία Καθαρής Ενέργειας</b></td>
                          <td style="text-align:right; padding:12px 0;">
                            <span style="color:#4CAF50; font-weight:700; font-size:1.2em;">{actual_energy_val:.2f} €</span>
                            <span style="color:#F44336; margin-left:10px; font-size:0.95em;">({hypo_energy_val:.2f} €)</span>
                          </td>
                        </tr>
                        <tr>
                          <td style="padding:16px 0; color:#fff; font-size:1.15em;">💰 <b>ΣΥΝΟΛΟ ΛΟΓΑΡΙΑΣΜΟΥ</b></td>
                          <td style="text-align:right; padding:16px 0;">
                            <span style="color:#4CAF50; font-weight:700; font-size:1.4em;">{actual_paid:.2f} €</span>
                            <span style="color:#F44336; margin-left:10px; font-size:1.1em;">({hypo_total_bill:.2f} €)</span>
                          </td>
                        </tr>
                      </table>
                    </div>
                    """
                    st.markdown(comparison_html, unsafe_allow_html=True)

                    # ── ΚΑΤΑΝΟΜΗ & ΜΑΘΗΜΑΤΙΚΗ ΕΠΑΛΗΘΕΥΣΗ ─────────────────────
                    st.markdown("### 📚 Πλήρης Ανάλυση & Μαθηματική Επαλήθευση Χρεώσεων")
                    st.markdown("Ανάλυση όλων των ποσών που εντοπίστηκαν. Δείτε πώς ακριβώς υπολογίστηκε η κάθε χρέωση (ή έκπτωση) βάσει των μαθηματικών τύπων της ΔΕΗ.")

                    # Ομαδοποίηση και Reverse Math
                    charges_by_category = {}
                    for charge_name, amount in all_charges.items():
                        if charge_name.startswith("__") or amount == 0: continue
                        if charge_name == "Χρεώσεις Προμήθειας": continue
                        
                        info = CHARGE_INFO.get(charge_name, {"category": "📌 Άλλες Χρεώσεις", "emoji": "📌", "desc": "Πρόσθετη Χρέωση", "type": "fixed", "affected_by_pv": False})
                        cat = info["category"]
                        if cat not in charges_by_category: charges_by_category[cat] = []
                        charges_by_category[cat].append((charge_name, amount, info))

                    for cat in sorted(charges_by_category.keys()):
                        st.markdown(f'<div class="category-header">{cat}</div>', unsafe_allow_html=True)
                        for charge_name, amount, info in charges_by_category[cat]:
                            # Δυναμικός Υπολογισμός / Formula
                            c_type = info["type"]
                            math_str = ""
                            
                            if c_type == "per_kwh" and total_kwh > 0:
                                rate = abs(amount) / total_kwh
                                math_str = f"{total_kwh:.0f} kWh × {rate:.5f} €/kWh"
                            elif c_type == "efk" and total_kwh > 0:
                                math_str = f"{total_kwh:.0f} kWh × 0.00220 €/kWh"
                            elif c_type == "vat":
                                vat_base = all_charges.get('__vat_base__', 0)
                                math_str = f"{vat_base:.2f} € × 6%" if vat_base > 0 else f"Βάση Υπολογισμού × 6%"
                            elif c_type == "eidiko_telos":
                                math_str = f"Βάση (Ρεύμα + Ρυθμιζόμενες + ΕΦΚ) × 0.5%"
                            elif c_type == "municipal":
                                math_str = f"Τετραγωνικά Ακινήτου × Τιμή Ζώνης Δήμου"
                            elif c_type == "ert":
                                math_str = f"3.00 € / μήνα × Ημέρες λογαριασμού"
                            else:
                                math_str = f"Σταθερό ποσό ή ποσοστιαία Έκπτωση"

                            pv_badge = (
                                '<span style="background:#1a3a1a;color:#4CAF50;border-radius:6px;'
                                'padding:2px 8px;font-size:0.78rem;margin-left:8px;">✅ Μειώνεται με net metering</span>'
                                if info["affected_by_pv"] else
                                '<span style="background:#2a1a1a;color:#F44336;border-radius:6px;'
                                'padding:2px 8px;font-size:0.78rem;margin-left:8px;">⚠️ Χρεώνεται κανονικά</span>'
                            )

                            amount_display = f"{amount:.2f} €" if amount > 0 else f"<span style='color:#4CAF50;'>{amount:.2f} €</span>"

                            st.markdown(f"""
                            <div class="charge-card">
                              <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                                <div>
                                  <span class="charge-title">{info['emoji']} {charge_name}</span>
                                  {pv_badge}
                                </div>
                                <span class="charge-amount" style="color:#ddd;">{amount_display}</span>
                              </div>
                              <div class="charge-desc">{info['desc']}</div>
                              <div class="charge-formula">🧮 <b>Υπολογισμός:</b> {math_str} = {amount:.2f} €</div>
                            </div>
                            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Σφάλμα κατά την ανάλυση: {e}")
            st.info("Βεβαιωθείτε ότι ανεβάσατε έγκυρο PDF λογαριασμού ΔΕΗ.")

# ── ΥΠΟΓΡΑΦΗ ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#666; padding-top:16px;'>
  <p style='font-size:1.05em;'><i>Αναπτύχθηκε και προσφέρεται δωρεάν από την <b style="color:#F5A623">Zarkolia Health</b></i></p>
  <p style='margin:4px 0;'><b>Πάνος Ζαρογουλίδης</b></p>
  <p style='font-size:0.88em; color:#555;'>Φαρμακοποιός MSc, MBA, Διαμεσολαβητής</p>
</div>
""", unsafe_allow_html=True)
