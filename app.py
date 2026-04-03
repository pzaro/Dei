import streamlit as st
import fitz  # PyMuPDF
import re

# ─────────────────────────────────────────────────────────────────
# ΣΕΛΙΔΑ & ΜΟΝΤΕΡΝΟ ΣΤΥΛ (DASHBOARD CSS) - ΠΛΗΡΗΣ ΑΝΑΝΕΩΣΗ
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Net Metering Dashboard | Zarkolia Health",
    page_icon="☀️",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Fira+Code&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* Typography */
.main-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #F5A623, #FFD166);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
    text-align: center;
}

.subtitle {
    font-size: 1.2rem;
    color: #9CA3AF;
    margin-bottom: 2.5rem;
    text-align: center;
    font-weight: 300;
}

/* Dashboard Cards (Top Metrics) */
.metric-container {
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    backdrop-filter: blur(10px);
}
.metric-title {
    font-size: 1rem;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 10px;
}
.metric-value {
    font-size: 2.8rem;
    font-weight: 700;
    font-family: 'Fira Code', monospace;
}
.val-green { color: #10B981; }
.val-blue { color: #3B82F6; }
.val-orange { color: #F5A623; }

/* Savings Banner Premium (Glassmorphism) */
.premium-banner {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(4, 120, 87, 0.4) 100%);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 24px;
    padding: 35px;
    text-align: center;
    margin: 30px 0;
    box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.1);
    backdrop-filter: blur(5px);
}
.banner-amount {
    font-size: 4.2rem;
    font-weight: 800;
    color: #10B981;
    font-family: 'Fira Code', monospace;
    text-shadow: 0 2px 10px rgba(16, 185, 129, 0.2);
}
.banner-label {
    font-size: 1.4rem;
    color: #E5E7EB;
    font-weight: 500;
    margin-bottom: 15px;
}
.pill {
    background: rgba(255, 255, 255, 0.1);
    color: #E5E7EB;
    border-radius: 30px;
    padding: 8px 18px;
    font-size: 1rem;
    margin: 6px;
    display: inline-block;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

/* Charge Cards Grid */
.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}
.charge-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 20px;
    padding: 25px;
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
    height: 100%;
    display: flex;
    flex-direction: column;
}
.charge-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    border-color: #475569;
}
.charge-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;
}
.charge-title {
    font-weight: 600;
    font-size: 1.2rem;
    color: #F8FAFC;
}
.charge-amount {
    font-family: 'Fira Code', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    color: #F5A623;
}
.charge-desc {
    font-size: 0.9rem;
    color: #94A3B8;
    line-height: 1.6;
    flex-grow: 1;
}
.charge-footer {
    margin-top: 18px;
    padding-top: 18px;
    border-top: 1px dashed #334155;
    font-size: 0.9rem;
}

/* Badges */
.badge-success { background: rgba(16, 185, 129, 0.1); color: #10B981; padding: 5px 10px; border-radius: 8px; font-weight: 500; font-size: 0.8rem; border: 1px solid rgba(16, 185, 129, 0.2); }
.badge-warning { background: rgba(244, 63, 94, 0.1); color: #F43F5E; padding: 5px 10px; border-radius: 8px; font-weight: 500; font-size: 0.8rem; border: 1px solid rgba(244, 63, 94, 0.2); }

/* Math Verification Box */
.math-box {
    background: #0F172A;
    border-left: 4px solid #3B82F6;
    padding: 20px;
    border-radius: 0 16px 16px 0;
    margin-bottom: 15px;
    font-size: 1rem;
}
.math-title { color: #3B82F6; font-weight: 600; margin-bottom: 6px; font-size: 1.1rem; }
.math-calc { font-family: 'Fira Code', monospace; color: #E2E8F0; margin-top: 10px; background: #1E293B; padding: 10px 15px; border-radius: 8px; display: inline-block; }

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">☀️ Net Metering Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ανεβάστε τον εκκαθαριστικό λογαριασμό ΔΕΗ σας (PDF) για πλήρη ανάλυση κερδών και χρεώσεων</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ΒΙΒΛΙΟΘΗΚΗ ΕΞΗΓΗΣΕΩΝ ΧΡΕΩΣΕΩΝ
# ─────────────────────────────────────────────────────────────────
CHARGE_INFO = {
    # ── Χρεώσεις Προμήθειας ──────────────────────────────────────
    "Χρεώσεις Προμήθειας": {
        "emoji": "⚡",
        "desc": "Το κόστος της ενέργειας που καταναλώσατε. Αυτό είναι το ποσό που μειώνει το φωτοβολταϊκό.",
        "affected_by_pv": True,
    },
    "Χρέωση Ενέργειας": {
        "emoji": "⚡",
        "desc": "Βασική χρέωση ενέργειας.",
        "affected_by_pv": True,
    },

    # ── Ρυθμιζόμενες / Δίκτυο ─────────────────────────────────────
    "ΕΤΜΕΑΡ": {
        "emoji": "🌱",
        "desc": "Ειδικό Τέλος υπέρ ΑΠΕ. Χρεώνεται επί της ΣΥΝΟΛΙΚΗΣ κατανάλωσης του μετρητή.",
        "affected_by_pv": False,
    },
    "ΥΚΩ": {
        "emoji": "🏝️",
        "desc": "Υπηρεσίες Κοινής Ωφέλειας (επιδότηση νησιών κλπ). Χρεώνεται επί της ΣΥΝΟΛΙΚΗΣ κατανάλωσης.",
        "affected_by_pv": False,
    },
    "Χρέωση Χρήσης Συστήματος": {
        "emoji": "🔌",
        "desc": "Κόστος χρήσης του Δικτύου Μεταφοράς Υψηλής Τάσης (ΑΔΜΗΕ).",
        "affected_by_pv": False,
    },
    "Χρέωση Χρήσης Δικτύου": {
        "emoji": "🔌",
        "desc": "Κόστος χρήσης του Δικτύου Διανομής Χαμηλής Τάσης (ΔΕΔΔΗΕ).",
        "affected_by_pv": False,
    },
    "Χρέωση Μέτρησης": {
        "emoji": "📟",
        "desc": "Πάγια χρέωση για τη συντήρηση και ανάγνωση του μετρητή.",
        "affected_by_pv": False,
    },

    # ── Πάγιες / Λοιπές ───────────────────────────────────────────
    "Πάγια Χρέωση": {
        "emoji": "📋",
        "desc": "Σταθερό μηνιαίο ποσό που χρεώνεται ανεξάρτητα από την κατανάλωση.",
        "affected_by_pv": False,
    },
    "Τέλος Ανακύκλωσης": {
        "emoji": "♻️",
        "desc": "Τέλος υπέρ του συστήματος ανακύκλωσης συσκευών.",
        "affected_by_pv": False,
    },

    # ── Φόροι ──────────────────────────────────────────────────────
    "ΦΠΑ": {
        "emoji": "🧾",
        "desc": "ΦΠΑ 6% επί των χρεώσεων ρεύματος. Μειώνεται αναλογικά με την ενέργεια που γλιτώνετε.",
        "affected_by_pv": True,
    },
    "ΕΦΚ": {
        "emoji": "🏛️",
        "desc": "Ειδικός Φόρος Κατανάλωσης (0,0022 €/kWh). Χρεώνεται επί της ΣΥΝΟΛΙΚΗΣ κατανάλωσης.",
        "affected_by_pv": False,
    },
    "Τέλος ΑΠΕ": {
        "emoji": "🌱",
        "desc": "Τέλος υπέρ Ανανεώσιμων Πηγών Ενέργειας.",
        "affected_by_pv": False,
    },
    "ΕΔΑΠ": {
        "emoji": "🏛️",
        "desc": "Ειδική Διαχειριστική Αμοιβή Παραγωγής.",
        "affected_by_pv": False,
    },
}


# ─────────────────────────────────────────────────────────────────
# ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ (Όπως ήταν)
# ─────────────────────────────────────────────────────────────────
def clean_number(s):
    """Μετατρέπει string αριθμό (π.χ. '1.060' ή '1,060') σε float."""
    s = s.strip()
    if '.' in s and ',' in s:
        s = s.replace('.', '').replace(',', '.')
    elif '.' in s and ',' not in s:
        parts = s.split('.')
        if len(parts) == 2 and len(parts[1]) == 3:
            s = s.replace('.', '')
    elif ',' in s and '.' not in s:
        s = s.replace(',', '.')
    return float(s)


def parse_all_charges(text):
    """Εξάγει όλες τις γραμμές χρεώσεων από το κείμενο."""
    charges = {}
    patterns = [
        # ── Χρεώσεις ρεύματος (έχουν ΦΠΑ) ───────────────────────
        (r'Χρεώσεις\s+Προμήθειας\s+ΔΕΗ[^\d\n]{0,20}([\d\.,]+)', "Χρεώσεις Προμήθειας"),
        (r'Πάγια\s+Χρέωση[^\d\n]{0,20}([\d\.,]+)',                "Πάγια Χρέωση"),
        (r'ΑΔΜΗΕ[^\d\n]{0,50}([\d\.,]+)',                          "ΑΔΜΗΕ: Σύστημα Μεταφοράς"),
        (r'ΔΕΔΔΗΕ[^\d\n]{0,50}([\d\.,]+)',                         "ΔΕΔΔΗΕ: Δίκτυο Διανομής"),
        (r'ΥΚΩ[^\d\n]{0,50}([\d\.,]+)',                            "ΥΚΩ"),
        (r'ΕΤΜΕΑΡ[^\d\n]{0,20}([\d\.,]+)',                         "ΕΤΜΕΑΡ"),
        (r'Χρέωση\s+Χρήσης\s+Συστήματος[^\d\n]{0,20}([\d\.,]+)', "Χρέωση Χρήσης Συστήματος"),
        (r'Χρέωση\s+Χρήσης\s+Δικτύου[^\d\n]{0,20}([\d\.,]+)',    "Χρέωση Χρήσης Δικτύου"),
        (r'Χρέωση\s+Μέτρησης[^\d\n]{0,20}([\d\.,]+)',              "Χρέωση Μέτρησης"),
        (r'ΕΔΑΠ[^\d\n]{0,20}([\d\.,]+)',                           "ΕΔΑΠ"),
        (r'Τέλος\s+ΑΠΕ[^\d\n]{0,20}([\d\.,]+)',                   "Τέλος ΑΠΕ"),
        (r'Τέλος\s+Ανακύκλωσης[^\d\n]{0,20}([\d\.,]+)',           "Τέλος Ανακύκλωσης"),
        # ── Χρεώσεις χωρίς ΦΠΑ ───────────────────────────────────
        (r'Δήμος\b[^\d\n]{0,30}([\d\.,]+)',                        "Δήμος"),
        (r'ΕΡΤ\b[^\d\n]{0,30}([\d\.,]+)',                          "ΕΡΤ"),
    ]
    for pattern, key in patterns:
        if key in charges:
            continue
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                val = clean_number(match.group(1))
                if val > 0:
                    charges[key] = val
            except ValueError:
                pass
    return charges


def parse_dei_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"

    processed_text = (text
                      .replace("Bkwh", "8kWh")
                      .replace("B kwh", "8 kWh")
                      .replace("awn", "kWh"))

    # ── 1. ΣΥΝΟΛΟ ΚΑΤΑΝΑΛΩΣΗΣ ─────────────────────────────────────
    total_kwh = None

    match_total = re.search(r'ΚΑΤΑΝΑΛΩΣΗ\s*[\.\s]*:\s*([\d\.]+)', processed_text, re.IGNORECASE)
    if match_total:
        try:
            total_kwh = clean_number(match_total.group(1))
        except ValueError:
            pass

    if total_kwh is None:
        match_total2 = re.search(r'Σύνολο\s*Κατανάλωσης\s+([\d\.,]+)', processed_text, re.IGNORECASE)
        if match_total2:
            try:
                total_kwh = clean_number(match_total2.group(1))
            except ValueError:
                pass

    if total_kwh is None:
        match_total3 = re.search(r'Κατανάλωση\s+Ηλεκτρικής\s+Ενέργειας\s+([\d\.,]+)\s*kWh', processed_text, re.IGNORECASE)
        if match_total3:
            try:
                total_kwh = clean_number(match_total3.group(1))
            except ValueError:
                pass

    if total_kwh is None:
        meter_totals = re.findall(r'T\d+\s+1[12]\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)', processed_text)
        if meter_totals:
            total_kwh = sum(float(x) for x in meter_totals)

    # ── 2. ΤΙΜΟΛΟΓΗΜΕΝΕΣ kWh & ΜΕΣΗ ΤΙΜΗ ────────────────────────
    billed_kwh = 0.0
    total_tier_cost = 0.0
    exact_avg_rate = None

    supply_section = re.search(
        r'Αναλυτικά οι χρεώσεις(.*?)Ρυθμιζόμενες\s*Χρεώσεις',
        processed_text, re.IGNORECASE | re.DOTALL
    )

    if supply_section:
        section_text = supply_section.group(1)
        pattern_kwh = re.compile(
            r'\(?\s*(\d+)\s*[kK][wW][hH]\s*[xX×]\s*([\d,\.]+)\s*€?/?\s*[kK][wW][hH]\s*\)?',
            re.IGNORECASE
        )
        for m in pattern_kwh.finditer(section_text):
            try:
                kwh_val = float(m.group(1))
                rate_val = clean_number(m.group(2))
                if rate_val < 0.001:
                    continue
                billed_kwh += kwh_val
                total_tier_cost += kwh_val * rate_val
            except ValueError:
                continue

    # ── 3. ΧΡΕΩΣΗ ΕΝΕΡΓΕΙΑΣ ──────────────────────────────────────
    energy_charge = None

    if billed_kwh > 0:
        exact_avg_rate = total_tier_cost / billed_kwh
        energy_charge = round(total_tier_cost, 2)
    else:
        match_energy = re.search(r'Χρεώσεις\s+Προμήθειας\s+ΔΕΗ\s+([\d,\.]+)', processed_text, re.IGNORECASE)
        if match_energy:
            try:
                energy_charge = clean_number(match_energy.group(1))
                billed_kwh = round(energy_charge / 0.135)
                exact_avg_rate = energy_charge / billed_kwh if billed_kwh > 0 else 0.139
            except ValueError:
                pass

        if energy_charge is None:
            match_energy2 = re.search(
                r'Χρέωση\s*Ενέργειας\s*Κανονική[\s\S]{0,50}?([\d,\.]+)',
                processed_text, re.IGNORECASE
            )
            if match_energy2:
                try:
                    energy_charge = clean_number(match_energy2.group(1))
                    billed_kwh = round(energy_charge / 0.135)
                    exact_avg_rate = energy_charge / billed_kwh if billed_kwh > 0 else 0.139
                except ValueError:
                    pass

    # ── 4. ΣΥΝΟΛΟ ΛΟΓΑΡΙΑΣΜΟΥ ────────────────────────────────────
    total_bill = None

    match_bill = re.search(
        r'Συνολικό\s+(?:πιστωτικό\s+υπόλοιπο|ποσό\s+πληρωμής)\s*(-?[\d\.,]+)\s*€?',
        processed_text, re.IGNORECASE
    )
    if match_bill:
        try:
            total_bill = clean_number(match_bill.group(1))
        except ValueError:
            pass

    if total_bill is None:
        match_bill2 = re.search(r'ΠΙΣΤΩΤΙΚΟ\s+ΥΠΟΛΟΙΠΟ\s*(-?[\d\.,]+)\s*€?', processed_text, re.IGNORECASE)
        if match_bill2:
            try:
                total_bill = clean_number(match_bill2.group(1))
            except ValueError:
                pass

    if total_bill is None:
        match_bill3 = re.search(r'\*\s*(-?[\d\.,]+)\s*€', processed_text)
        if match_bill3:
            try:
                total_bill = clean_number(match_bill3.group(1))
            except ValueError:
                pass

    # ── 5. ΟΛΕΣ ΟΙ ΧΡΕΩΣΕΙΣ ──────────────────────────────────────
    all_charges = parse_all_charges(processed_text)

    # Αν εξήχθη χρέωση ενέργειας, βεβαιωνόμαστε ότι είναι στο dict
    if energy_charge and energy_charge > 0:
        all_charges["Χρεώσεις Προμήθειας"] = energy_charge

    # ΕΦΚ: υπολογίζεται από συνολικές kWh μετρητή × 0,0022
    if total_kwh and total_kwh > 0:
        all_charges["ΕΦΚ"] = round(total_kwh * 0.0022, 2)

    # ΦΠΑ: διαβάζουμε απευθείας από τη γραμμή "ΦΠΑ ΡΕΥΜΑΤΟΣ XX,XX x 6% = Y,YY"
    vat_base = None
    vat_amount = None

    m_vat = re.search(
        r'ΦΠΑ\s+ΡΕΥΜΑΤΟΣ\s+([\d\.,]+)\s*[xX×]\s*6%\s*=\s*([\d\.,]+)',
        processed_text, re.IGNORECASE
    )
    if m_vat:
        try:
            vat_base   = clean_number(m_vat.group(1))
            vat_amount = clean_number(m_vat.group(2))
        except ValueError:
            pass

    if vat_amount is None:
        ELECTRICITY_KEYS = {
            "Χρεώσεις Προμήθειας", "Πάγια Χρέωση",
            "ΑΔΜΗΕ: Σύστημα Μεταφοράς", "ΔΕΔΔΗΕ: Δίκτυο Διανομής",
            "Χρέωση Χρήσης Συστήματος", "Χρέωση Χρήσης Δικτύου",
            "ΥΚΩ", "ΕΤΜΕΑΡ", "ΕΦΚ", "ΕΔΑΠ", "Τέλος ΑΠΕ",
            "Χρέωση Μέτρησης", "Τέλος Ανακύκλωσης",
        }
        vat_base   = sum(v for k, v in all_charges.items() if k in ELECTRICITY_KEYS)
        vat_amount = round(vat_base * 0.06, 2)

    all_charges["ΦΠΑ"] = vat_amount
    all_charges["__vat_base__"] = vat_base or 0.0

    return total_kwh, billed_kwh, energy_charge, total_bill, exact_avg_rate, processed_text, all_charges


# ─────────────────────────────────────────────────────────────────
# UI APP
# ─────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("📄 Επιλέξτε το PDF του λογαριασμού σας", type="pdf")

if uploaded_file is not None:
    file_bytes = uploaded_file.read()

    with st.spinner('🔍 Ανάλυση λογαριασμού...'):
        try:
            (total_kwh, billed_kwh, energy_charge, total_bill,
             exact_avg_rate, raw_text, all_charges) = parse_dei_pdf(file_bytes)

            with st.expander("🔧 Debug: Ακατέργαστες τιμές"):
                st.write(f"**total_kwh:** {total_kwh} | **billed_kwh:** {billed_kwh} | "
                         f"**energy_charge:** {energy_charge} | **total_bill:** {total_bill} | "
                         f"**avg_rate:** {exact_avg_rate}")
                st.write(f"**Εντοπισμένες χρεώσεις:** {all_charges}")

            if not total_kwh or not billed_kwh:
                st.error("❌ Δεν ήταν δυνατή η ανάγνωση kWh. Βεβαιωθείτε ότι ανεβάσατε εκκαθαριστικό ΔΕΗ.")
            else:
                hidden_kwh = total_kwh - billed_kwh

                if hidden_kwh <= 0:
                    st.warning("⚠️ Δεν εντοπίστηκε απόκρυφη έκπτωση net metering.")
                else:
                    safe_energy_charge = energy_charge if energy_charge is not None else 0.0
                    actual_paid = total_bill if total_bill is not None else 0.0
                    avg_rate_no_vat = exact_avg_rate if exact_avg_rate is not None else 0.139
                    VAT_RATE = 0.06

                    saved_energy = hidden_kwh * avg_rate_no_vat
                    saved_vat = saved_energy * VAT_RATE
                    total_saved = saved_energy + saved_vat

                    # --- TOP DASHBOARD METRICS ---
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-title">Πληρωτεο Ποσο</div>
                            <div class="metric-value val-blue">{actual_paid:.2f} €</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-title">Μη Τιμολογηθεισες kWh</div>
                            <div class="metric-value val-orange">{hidden_kwh:.0f} <span style="font-size:1rem; color:#9CA3AF;">kWh</span></div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-title">Μέση Τιμή Ενέργειας</div>
                            <div class="metric-value val-green">{avg_rate_no_vat:.4f} <span style="font-size:1rem; color:#9CA3AF;">€/kWh</span></div>
                        </div>
                        """, unsafe_allow_html=True)

                    # --- SAVINGS PREMIUM BANNER ---
                    st.markdown(f"""
                    <div class="premium-banner">
                        <div class="banner-label">Συνολικό Καθαρό Κέρδος από το Φωτοβολταϊκό σας</div>
                        <div class="banner-amount">+{total_saved:.2f} €</div>
                        <div style="margin-top:15px;">
                            <span class="pill">⚡ {hidden_kwh:.0f} kWh εξοικονομήθηκαν</span>
                            <span class="pill">💶 {saved_energy:.2f} € αξία ενέργειας</span>
                            <span class="pill">🧾 {saved_vat:.2f} € ΦΠΑ</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if total_bill is not None and total_bill < 0:
                        st.info(f"ℹ️ Ο λογαριασμός σας είναι **πιστωτικός** ({total_bill:.2f} €) — η ΔΕΗ σάς επιστρέφει χρήματα!")

                    st.markdown("---")

                    # --- FULL ANALYSIS GRIDS ---
                    st.markdown("### 📊 Πλήρης Ανάλυση Χρεώσεων Λογαριασμού")
                    st.markdown("Δείτε αναλυτικά *κάθε* χρέωση του λογαριασμού σας. Οι χρεώσεις χωρίζονται σε αυτές που μειώνονται από το Net Metering και σε αυτές που χρεώνονται κανονικά στο σύνολο του μετρητή.")
                    
                    # Ομαδοποίηση Χρεώσεων για το Grid
                    pv_affected_html = ""
                    normal_charges_html = ""

                    for charge_name, amount in all_charges.items():
                        if charge_name.startswith("__"): continue
                        
                        info = CHARGE_INFO.get(charge_name, {
                            "emoji": "📋", "desc": "Πρόσθετη χρέωση που βρέθηκε.", "affected_by_pv": False
                        })
                        
                        badge = '<span class="badge-success">✅ Μειώνεται (Net Metering)</span>' if info["affected_by_pv"] else '<span class="badge-warning">⚠️ Πλήρης Χρέωση</span>'
                        
                        card_html = f"""
                        <div class="charge-card">
                            <div class="charge-header">
                                <span class="charge-title">{info['emoji']} {charge_name}</span>
                                {badge}
                            </div>
                            <div class="charge-desc">{info['desc']}</div>
                            <div class="charge-footer">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span style="color:#94A3B8; font-size:0.85rem;">Αξία Χρέωσης</span>
                                    <span class="charge-amount">{amount:.2f} €</span>
                                </div>
                            </div>
                        </div>
                        """
                        
                        if info["affected_by_pv"]:
                            pv_affected_html += card_html
                        else:
                            normal_charges_html += card_html

                    # Εμφάνιση Grid
                    st.markdown("#### 🟢 Χρεώσεις που ευνοούνται από το Φωτοβολταϊκό")
                    st.markdown(f'<div class="grid-container">{pv_affected_html}</div>', unsafe_allow_html=True)
                    
                    st.markdown("#### 🔴 Ρυθμιζόμενες & Λοιπές (Σταθερές Χρεώσεις)")
                    st.markdown(f'<div class="grid-container">{normal_charges_html}</div>', unsafe_allow_html=True)


                    # --- ΜΑΘΗΜΑΤΙΚΗ ΕΠΑΛΗΘΕΥΣΗ ---
                    st.markdown("---")
                    st.markdown("### 🧮 Γλωσσάρι & Μαθηματική Επαλήθευση (Ανάλυση όλων των φόρων)")
                    st.markdown("Πώς ακριβώς μεταφράζονται τα αρχικά των φόρων και ποια είναι η **ακριβής χρέωση ανά kWh** που εφαρμόστηκε στον δικό σας λογαριασμό:")

                    abbreviations_info = {
                        "ΑΔΜΗΕ: Σύστημα Μεταφοράς": ("Α.Δ.Μ.Η.Ε.", "Δίκτυο Υψηλής Τάσης", True),
                        "ΔΕΔΔΗΕ: Δίκτυο Διανομής": ("Δ.Ε.Δ.Δ.Η.Ε.", "Δίκτυο Διανομής Γειτονιάς", True),
                        "ΥΚΩ": ("Υ.Κ.Ω.", "Υπηρεσίες Κοινής Ωφέλειας", True),
                        "ΕΤΜΕΑΡ": ("Ε.Τ.Μ.Ε.Α.Ρ.", "Τέλος υπέρ Ανανεώσιμων Πηγών", True),
                        "ΕΦΚ": ("Ε.Φ.Κ.", "Ειδικός Φόρος Κατανάλωσης (Σταθερό 0.0022)", True),
                        "ΕΔΑΠ": ("Ε.Δ.Α.Π.", "Ειδική Διαχειριστική Αμοιβή Παραγωγής", True),
                        "Τέλος ΑΠΕ": ("Α.Π.Ε.", "Τέλος Ανανεώσιμων Πηγών Ενέργειας", True),
                        "ΦΠΑ": ("Φ.Π.Α.", "Φόρος Προστιθέμενης Αξίας (6%)", False)
                    }

                    for dict_key, (abbr, full_name, per_kwh) in abbreviations_info.items():
                        val = all_charges.get(dict_key)
                        if val is not None and val > 0:
                            if dict_key == "ΦΠΑ":
                                math_text = f"Εφαρμόστηκε 6% επί της αξίας του ρεύματος και των ρυθμιζόμενων χρεώσεων: <br><b style='color:#7ec8e3;'>{all_charges.get('__vat_base__', 0):.2f} € × 6% = {val:.2f} €</b>"
                            elif per_kwh and total_kwh and total_kwh > 0:
                                rate = val / total_kwh
                                math_text = f"Χρεώθηκε επί των συνολικών {total_kwh:.0f} kWh του μετρητή. Το Φ/Β δεν σας γλιτώνει από αυτή τη χρέωση.<br><b style='color:#7ec8e3;'>{total_kwh:.0f} kWh × {rate:.5f} €/kWh = {val:.2f} €</b>"
                            else:
                                math_text = f"Χρεώθηκε το ποσό των <b style='color:#7ec8e3;'>{val:.2f} €</b>."

                            st.markdown(f"""
                            <div class="math-box">
                                <div class="math-title">{abbr} - {full_name}</div>
                                {math_text}
                            </div>
                            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Σφάλμα κατά την ανάλυση: {e}")
            st.info("Βεβαιωθείτε ότι ανεβάσατε έγκυρο PDF λογαριασμού ΔΕΗ.")

# ── ΥΠΟΓΡΑΦΗ ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; padding-top:30px; padding-bottom: 20px;'>
  <p style='font-size:1.1em; color:#9CA3AF; margin-bottom: 5px;'><i>Αναπτύχθηκε και προσφέρεται δωρεάν από την <b style="color:#F5A623; letter-spacing: 0.5px;">Zarkolia Health</b></i></p>
  <p style='margin:0; font-size: 1.2rem; font-weight: 600; color: #E5E7EB;'>Πάνος Ζαρογουλίδης</p>
  <p style='font-size:0.95em; color:#64748B; margin-top: 5px;'>Φαρμακοποιός MSc, MBA, Διαμεσολαβητής</p>
</div>
""", unsafe_allow_html=True)
