import streamlit as st
import fitz  # PyMuPDF
import re

# ─────────────────────────────────────────────────────────────────
# ΣΕΛΙΔΑ & ULTRA-MODERN FINTECH STYLE (CSS)
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Net Metering | Zarkolia Health",
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

/* Hide Streamlit default branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Typography */
.app-header {
    text-align: center;
    padding: 2rem 0 3rem 0;
}
.app-title {
    font-size: 2.5rem;
    font-weight: 800;
    letter-spacing: -1px;
    color: #FFFFFF;
    margin-bottom: 0.5rem;
}
.app-subtitle {
    font-size: 1.1rem;
    color: #94A3B8;
    font-weight: 400;
}

/* Minimalist Metric Cards */
.metric-row {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 2rem;
}
.metric-card {
    flex: 1;
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
    font-size: 2rem;
    font-weight: 700;
    color: #F8FAFC;
}
.metric-highlight-green { color: #10B981; }

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
    font-size: 1.1rem;
    font-weight: 700;
}
.text-green { color: #10B981; }
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
    "Χρεώσεις Προμήθειας": {"emoji": "⚡", "desc": "Κόστος ρεύματος (Μειώνεται)", "affected_by_pv": True},
    "Χρέωση Ενέργειας": {"emoji": "⚡", "desc": "Κόστος ρεύματος (Μειώνεται)", "affected_by_pv": True},
    "ΕΤΜΕΑΡ": {"emoji": "🌱", "desc": "Τέλος υπέρ ΑΠΕ (Επί της συνολικής κατανάλωσης)", "affected_by_pv": False},
    "ΥΚΩ": {"emoji": "🏝️", "desc": "Υπηρεσίες Κοινής Ωφέλειας (Επί της συνολικής κατανάλωσης)", "affected_by_pv": False},
    "Χρέωση Χρήσης Συστήματος": {"emoji": "🔌", "desc": "Δίκτυο ΑΔΜΗΕ", "affected_by_pv": False},
    "ΑΔΜΗΕ: Σύστημα Μεταφοράς": {"emoji": "🔌", "desc": "Δίκτυο ΑΔΜΗΕ", "affected_by_pv": False},
    "Χρέωση Χρήσης Δικτύου": {"emoji": "🔌", "desc": "Δίκτυο ΔΕΔΔΗΕ", "affected_by_pv": False},
    "ΔΕΔΔΗΕ: Δίκτυο Διανομής": {"emoji": "🔌", "desc": "Δίκτυο ΔΕΔΔΗΕ", "affected_by_pv": False},
    "Χρέωση Μέτρησης": {"emoji": "📟", "desc": "Πάγιο μετρητή", "affected_by_pv": False},
    "Πάγια Χρέωση": {"emoji": "📋", "desc": "Σταθερό μηνιαίο πάγιο", "affected_by_pv": False},
    "Τέλος Ανακύκλωσης": {"emoji": "♻️", "desc": "Τέλος ανακύκλωσης συσκευών", "affected_by_pv": False},
    "ΦΠΑ": {"emoji": "🧾", "desc": "ΦΠΑ 6% (Μειώνεται αναλογικά)", "affected_by_pv": True},
    "ΕΦΚ": {"emoji": "🏛️", "desc": "Ειδικός Φόρος Κατανάλωσης", "affected_by_pv": False},
    "Τέλος ΑΠΕ": {"emoji": "🌱", "desc": "Τέλος υπέρ ΑΠΕ", "affected_by_pv": False},
    "ΕΔΑΠ": {"emoji": "🏛️", "desc": "Διαχειριστική Αμοιβή ΛΑΓΗΕ", "affected_by_pv": False},
    "Δήμος": {"emoji": "🏛️", "desc": "Δημοτικά Τέλη & ΤΑΠ", "affected_by_pv": False},
    "ΕΡΤ": {"emoji": "📺", "desc": "Τέλος ΕΡΤ", "affected_by_pv": False},
}


# ─────────────────────────────────────────────────────────────────
# ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ (Λογική ανάγνωσης παραμένει ίδια)
# ─────────────────────────────────────────────────────────────────
def clean_number(s):
    s = s.strip()
    if '.' in s and ',' in s: s = s.replace('.', '').replace(',', '.')
    elif '.' in s and ',' not in s:
        parts = s.split('.')
        if len(parts) == 2 and len(parts[1]) == 3: s = s.replace('.', '')
    elif ',' in s and '.' not in s: s = s.replace(',', '.')
    return float(s)

def parse_all_charges(text):
    charges = {}
    patterns = [
        (r'Χρεώσεις\s+Προμήθειας\s+ΔΕΗ[^\d\n]{0,20}([\d\.,]+)', "Χρεώσεις Προμήθειας"),
        (r'Πάγια\s+Χρέωση[^\d\n]{0,20}([\d\.,]+)', "Πάγια Χρέωση"),
        (r'ΑΔΜΗΕ[^\d\n]{0,50}([\d\.,]+)', "ΑΔΜΗΕ: Σύστημα Μεταφοράς"),
        (r'ΔΕΔΔΗΕ[^\d\n]{0,50}([\d\.,]+)', "ΔΕΔΔΗΕ: Δίκτυο Διανομής"),
        (r'ΥΚΩ[^\d\n]{0,50}([\d\.,]+)', "ΥΚΩ"),
        (r'ΕΤΜΕΑΡ[^\d\n]{0,20}([\d\.,]+)', "ΕΤΜΕΑΡ"),
        (r'Χρέωση\s+Χρήσης\s+Συστήματος[^\d\n]{0,20}([\d\.,]+)', "Χρέωση Χρήσης Συστήματος"),
        (r'Χρέωση\s+Χρήσης\s+Δικτύου[^\d\n]{0,20}([\d\.,]+)', "Χρέωση Χρήσης Δικτύου"),
        (r'Χρέωση\s+Μέτρησης[^\d\n]{0,20}([\d\.,]+)', "Χρέωση Μέτρησης"),
        (r'ΕΔΑΠ[^\d\n]{0,20}([\d\.,]+)', "ΕΔΑΠ"),
        (r'Τέλος\s+ΑΠΕ[^\d\n]{0,20}([\d\.,]+)', "Τέλος ΑΠΕ"),
        (r'Τέλος\s+Ανακύκλωσης[^\d\n]{0,20}([\d\.,]+)', "Τέλος Ανακύκλωσης"),
        (r'Δήμος\b[^\d\n]{0,30}([\d\.,]+)', "Δήμος"),
        (r'ΕΡΤ\b[^\d\n]{0,30}([\d\.,]+)', "ΕΡΤ"),
    ]
    for pattern, key in patterns:
        if key in charges: continue
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                val = clean_number(match.group(1))
                if val > 0: charges[key] = val
            except ValueError: pass
    return charges

def parse_dei_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc: text += page.get_text("text") + "\n"

    processed_text = text.replace("Bkwh", "8kWh").replace("B kwh", "8 kWh").replace("awn", "kWh")

    total_kwh = None
    for pattern in [r'ΚΑΤΑΝΑΛΩΣΗ\s*[\.\s]*:\s*([\d\.]+)', r'Σύνολο\s*Κατανάλωσης\s+([\d\.,]+)', r'Κατανάλωση\s+Ηλεκτρικής\s+Ενέργειας\s+([\d\.,]+)\s*kWh']:
        match = re.search(pattern, processed_text, re.IGNORECASE)
        if match:
            try: total_kwh = clean_number(match.group(1)); break
            except ValueError: pass
    
    if total_kwh is None:
        meter_totals = re.findall(r'T\d+\s+1[12]\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)', processed_text)
        if meter_totals: total_kwh = sum(float(x) for x in meter_totals)

    billed_kwh, total_tier_cost, exact_avg_rate = 0.0, 0.0, None
    supply_section = re.search(r'Αναλυτικά οι χρεώσεις(.*?)Ρυθμιζόμενες\s*Χρεώσεις', processed_text, re.IGNORECASE | re.DOTALL)
    
    if supply_section:
        for m in re.finditer(r'\(?\s*(\d+)\s*[kK][wW][hH]\s*[xX×]\s*([\d,\.]+)\s*€?/?\s*[kK][wW][hH]\s*\)?', supply_section.group(1), re.IGNORECASE):
            try:
                k, r = float(m.group(1)), clean_number(m.group(2))
                if r >= 0.001: billed_kwh += k; total_tier_cost += k * r
            except ValueError: pass

    energy_charge = None
    if billed_kwh > 0:
        exact_avg_rate = total_tier_cost / billed_kwh
        energy_charge = round(total_tier_cost, 2)
    else:
        for pattern in [r'Χρεώσεις\s+Προμήθειας\s+ΔΕΗ\s+([\d,\.]+)', r'Χρέωση\s*Ενέργειας\s*Κανονική[\s\S]{0,50}?([\d,\.]+)']:
            match = re.search(pattern, processed_text, re.IGNORECASE)
            if match:
                try:
                    energy_charge = clean_number(match.group(1))
                    billed_kwh = round(energy_charge / 0.135)
                    exact_avg_rate = energy_charge / billed_kwh if billed_kwh > 0 else 0.139
                    break
                except ValueError: pass

    total_bill = None
    for pattern in [r'Συνολικό\s+(?:πιστωτικό\s+υπόλοιπο|ποσό\s+πληρωμής)\s*(-?[\d\.,]+)\s*€?', r'ΠΙΣΤΩΤΙΚΟ\s+ΥΠΟΛΟΙΠΟ\s*(-?[\d\.,]+)\s*€?', r'\*\s*(-?[\d\.,]+)\s*€']:
        match = re.search(pattern, processed_text, re.IGNORECASE)
        if match:
            try: total_bill = clean_number(match.group(1)); break
            except ValueError: pass

    all_charges = parse_all_charges(processed_text)
    if energy_charge and energy_charge > 0: all_charges["Χρεώσεις Προμήθειας"] = energy_charge
    if total_kwh and total_kwh > 0: all_charges["ΕΦΚ"] = round(total_kwh * 0.0022, 2)

    vat_base, vat_amount = None, None
    m_vat = re.search(r'ΦΠΑ\s+ΡΕΥΜΑΤΟΣ\s+([\d\.,]+)\s*[xX×]\s*6%\s*=\s*([\d\.,]+)', processed_text, re.IGNORECASE)
    if m_vat:
        try: vat_base, vat_amount = clean_number(m_vat.group(1)), clean_number(m_vat.group(2))
        except ValueError: pass

    if vat_amount is None:
        keys = {"Χρεώσεις Προμήθειας", "Πάγια Χρέωση", "ΑΔΜΗΕ: Σύστημα Μεταφοράς", "ΔΕΔΔΗΕ: Δίκτυο Διανομής", "Χρέωση Χρήσης Συστήματος", "Χρέωση Χρήσης Δικτύου", "ΥΚΩ", "ΕΤΜΕΑΡ", "ΕΦΚ", "ΕΔΑΠ", "Τέλος ΑΠΕ", "Χρέωση Μέτρησης", "Τέλος Ανακύκλωσης"}
        vat_base = sum(v for k, v in all_charges.items() if k in keys)
        vat_amount = round(vat_base * 0.06, 2)

    all_charges["ΦΠΑ"] = vat_amount
    all_charges["__vat_base__"] = vat_base or 0.0

    return total_kwh, billed_kwh, energy_charge, total_bill, exact_avg_rate, processed_text, all_charges


# ─────────────────────────────────────────────────────────────────
# UI APP RENDERING
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="app-header">', unsafe_allow_html=True)
st.markdown('<div class="app-title">Net Metering Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Ανεβάστε το PDF της ΔΕΗ για να δείτε την ανάλυση του κέρδους σας.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type="pdf")

if uploaded_file is not None:
    file_bytes = uploaded_file.read()

    with st.spinner('Ανάλυση...'):
        try:
            (total_kwh, billed_kwh, energy_charge, total_bill,
             exact_avg_rate, raw_text, all_charges) = parse_dei_pdf(file_bytes)

            if not total_kwh or not billed_kwh:
                st.error("Δεν ήταν δυνατή η ανάγνωση των δεδομένων.")
            else:
                hidden_kwh = total_kwh - billed_kwh
                if hidden_kwh <= 0:
                    st.warning("⚠️ Δεν εντοπίστηκε έκπτωση Net Metering (Μηδενικό κέρδος).")
                else:
                    safe_energy_charge = energy_charge if energy_charge is not None else 0.0
                    actual_paid = total_bill if total_bill is not None else 0.0
                    avg_rate_no_vat = exact_avg_rate if exact_avg_rate is not None else 0.139
                    VAT_RATE = 0.06

                    saved_energy = hidden_kwh * avg_rate_no_vat
                    saved_vat = saved_energy * VAT_RATE
                    total_saved = saved_energy + saved_vat

                    # --- TOP METRICS ---
                    st.markdown(f"""
                    <div class="metric-row">
                        <div class="metric-card">
                            <div class="metric-label">Πληρωτεο Ποσο</div>
                            <div class="metric-value">{actual_paid:.2f} €</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Αναλωθεισες KWh (Χωρις Χρεωση)</div>
                            <div class="metric-value">{hidden_kwh:.0f}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Μεση Τιμη (Χωρις ΦΠΑ)</div>
                            <div class="metric-value">{avg_rate_no_vat:.4f} €</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # --- HERO SAVINGS BANNER ---
                    st.markdown(f"""
                    <div class="hero-card">
                        <div class="hero-label">ΚΑΘΑΡΟ ΚΕΡΔΟΣ ΑΠΟ ΤΟ ΦΩΤΟΒΟΛΤΑΪΚΟ</div>
                        <div class="hero-amount">+{total_saved:.2f} €</div>
                        <div class="hero-tags">
                            <span class="tag">⚡ Αξία Ενέργειας: {saved_energy:.2f} €</span>
                            <span class="tag">🧾 Γλιτωμένος ΦΠΑ: {saved_vat:.2f} €</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # --- COLUMNS FOR CHARGES ---
                    col_left, col_right = st.columns(2, gap="large")

                    with col_left:
                        st.markdown('<div class="section-title">✅ Μειώθηκαν από το Net Metering</div>', unsafe_allow_html=True)
                        pv_html = ""
                        for charge_name, amount in all_charges.items():
                            if charge_name.startswith("__"): continue
                            info = CHARGE_INFO.get(charge_name, {"emoji": "📋", "desc": "", "affected_by_pv": False})
                            
                            if info["affected_by_pv"]:
                                pv_html += f"""
                                <div class="list-item">
                                    <div class="list-item-left">
                                        <div class="list-item-title">{info['emoji']} {charge_name}</div>
                                        <div class="list-item-desc">{info['desc']}</div>
                                    </div>
                                    <div class="list-item-amount text-green">{amount:.2f} €</div>
                                </div>
                                """
                        st.markdown(pv_html, unsafe_allow_html=True)

                    with col_right:
                        st.markdown('<div class="section-title">🔴 Σταθερές & Ρυθμιζόμενες Χρεώσεις</div>', unsafe_allow_html=True)
                        standard_html = ""
                        for charge_name, amount in all_charges.items():
                            if charge_name.startswith("__"): continue
                            info = CHARGE_INFO.get(charge_name, {"emoji": "📋", "desc": "", "affected_by_pv": False})
                            
                            if not info["affected_by_pv"]:
                                standard_html += f"""
                                <div class="list-item">
                                    <div class="list-item-left">
                                        <div class="list-item-title">{info['emoji']} {charge_name}</div>
                                        <div class="list-item-desc">{info['desc']}</div>
                                    </div>
                                    <div class="list-item-amount text-normal">{amount:.2f} €</div>
                                </div>
                                """
                        st.markdown(standard_html, unsafe_allow_html=True)

                    # --- MATH VERIFICATION (Clean Box style) ---
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    st.markdown('<div class="section-title">🧮 Ανάλυση Υπολογισμών (Φόροι & Τέλη)</div>', unsafe_allow_html=True)

                    abbreviations_info = {
                        "ΑΔΜΗΕ: Σύστημα Μεταφοράς": ("Α.Δ.Μ.Η.Ε.", "Δίκτυο Υψηλής Τάσης", True),
                        "Χρέωση Χρήσης Συστήματος": ("Α.Δ.Μ.Η.Ε.", "Δίκτυο Υψηλής Τάσης", True),
                        "ΔΕΔΔΗΕ: Δίκτυο Διανομής": ("Δ.Ε.Δ.Δ.Η.Ε.", "Δίκτυο Διανομής (Γειτονιάς)", True),
                        "Χρέωση Χρήσης Δικτύου": ("Δ.Ε.Δ.Δ.Η.Ε.", "Δίκτυο Διανομής (Γειτονιάς)", True),
                        "ΥΚΩ": ("Υ.Κ.Ω.", "Υπηρεσίες Κοινής Ωφέλειας", True),
                        "ΕΤΜΕΑΡ": ("Ε.Τ.Μ.Ε.Α.Ρ.", "Ειδικό Τέλος υπέρ ΑΠΕ", True),
                        "ΕΦΚ": ("Ε.Φ.Κ.", "Ειδικός Φόρος Κατανάλωσης", True),
                        "ΕΔΑΠ": ("Ε.Δ.Α.Π.", "Διαχειριστική Αμοιβή Παραγωγής", True),
                        "Τέλος ΑΠΕ": ("Α.Π.Ε.", "Τέλος Ανανεώσιμων Πηγών", True),
                        "ΦΠΑ": ("Φ.Π.Α.", "Φόρος Προστιθέμενης Αξίας 6%", False),
                        "Δήμος": ("ΔΗΜΟΣ", "Δημοτικά Τέλη & ΤΑΠ", False),
                    }

                    math_html = ""
                    for dict_key, (abbr, full_name, per_kwh) in abbreviations_info.items():
                        val = all_charges.get(dict_key)
                        if val is not None and val > 0:
                            if dict_key == "ΦΠΑ":
                                formula = f"{all_charges.get('__vat_base__', 0):.2f} € × 6% = {val:.2f} €"
                                text = "Υπολογίζεται επί της καθαρής αξίας ενέργειας και των ρυθμιζόμενων χρεώσεων."
                            elif per_kwh and total_kwh and total_kwh > 0:
                                rate = val / total_kwh
                                formula = f"{total_kwh:.0f} kWh × {rate:.5f} €/kWh = {val:.2f} €"
                                text = "Υπολογίζεται αυστηρά επί των συνολικών kWh του μετρητή. Το net metering δεν επηρεάζει αυτό το ποσό."
                            else:
                                formula = f"{val:.2f} €"
                                text = "Σταθερό ποσό ή υπολογιζόμενο βάσει τετραγωνικών μέτρων του ακινήτου."

                            math_html += f"""
                            <div class="math-container">
                                <div class="math-header">{abbr} — {full_name}</div>
                                <div class="math-body">{text}</div>
                                <div class="math-formula">{formula}</div>
                            </div>
                            """
                    
                    st.markdown(math_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Σφάλμα: {e}")

# ── ΥΠΟΓΡΑΦΗ ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; padding: 2rem 0; color: #64748B;'>
  <div style='font-size:0.9rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;'>Powered by</div>
  <div style='font-size:1.4rem; font-weight:800; color:#FFFFFF; letter-spacing: -0.5px;'>Zarkolia Health</div>
  <div style='font-size:0.9rem; margin-top: 4px;'>Πάνος Ζαρογουλίδης • Φαρμακοποιός MSc, MBA</div>
</div>
""", unsafe_allow_html=True)
