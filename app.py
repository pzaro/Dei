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

.edu-link {
    color: #F5A623;
    text-decoration: none;
    font-size: 0.82rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">☀️ Υπολογιστής Net Metering</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ανεβάστε τον λογαριασμό ΔΕΗ σας (PDF) για πλήρη ανάλυση κερδών φωτοβολταϊκού</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ΒΙΒΛΙΟΘΗΚΗ ΕΞΗΓΗΣΕΩΝ ΧΡΕΩΣΕΩΝ
# ─────────────────────────────────────────────────────────────────
CHARGE_INFO = {
    # ── Χρεώσεις Προμήθειας ──────────────────────────────────────
    "Χρεώσεις Προμήθειας": {
        "category": "⚡ Χρεώσεις Ενέργειας (Προμήθεια)",
        "emoji": "⚡",
        "desc": (
            "Το κόστος της ηλεκτρικής ενέργειας που καταναλώσατε, "
            "χρεωμένο σε κλιμακωτές ζώνες (π.χ. 0–500 kWh, 501–1000 kWh, 1001+). "
            "Αποτελεί συνήθως το μεγαλύτερο τμήμα του λογαριασμού."
        ),
        "formula": "kWh × τιμή ζώνης €/kWh (χωρίς ΦΠΑ)",
        "affected_by_pv": True,
    },
    "Χρέωση Ενέργειας": {
        "category": "⚡ Χρεώσεις Ενέργειας (Προμήθεια)",
        "emoji": "⚡",
        "desc": "Βασική χρέωση ενέργειας βάσει κατανάλωσης kWh.",
        "formula": "kWh × τιμή €/kWh",
        "affected_by_pv": True,
    },

    # ── Ρυθμιζόμενες / Δίκτυο ─────────────────────────────────────
    "ΕΤΜΕΑΡ": {
        "category": "🌱 Ειδικοί Φόροι & Ανανεώσιμες Πηγές",
        "emoji": "🌱",
        "desc": (
            "Ειδικός Φόρος Μείωσης Εκπομπών Αερίων Ρύπων. "
            "Ανακατευθύνεται στο Ειδικό Λογαριασμό ΑΠΕ (ΕΛΑΠΕ) για την επιδότηση "
            "των ανανεώσιμων πηγών ενέργειας. "
            "⚠️ Χρεώνεται επί της ΣΥΝΟΛΙΚΗΣ κατανάλωσης μετρητή — δεν μειώνεται από το net metering."
        ),
        "formula": "ΣΥΝΟΛΙΚΑ kWh μετρητή × 0,02972 €/kWh",
        "affected_by_pv": False,
    },
    "ΥΚΩ": {
        "category": "🏝️ Υπηρεσίες Κοινής Ωφέλειας",
        "emoji": "🏝️",
        "desc": (
            "Χρέωση Υπηρεσιών Κοινής Ωφέλειας. Καλύπτει το κόστος "
            "ηλεκτροδότησης νησιών και απομακρυσμένων περιοχών. "
            "⚠️ Χρεώνεται επί της ΣΥΝΟΛΙΚΗΣ κατανάλωσης μετρητή — δεν μειώνεται από το net metering."
        ),
        "formula": "ΣΥΝΟΛΙΚΑ kWh μετρητή × ρυθμιζόμενη τιμή €/kWh",
        "affected_by_pv": False,
    },
    "Χρέωση Χρήσης Συστήματος": {
        "category": "🔌 Χρεώσεις Δικτύου (ΑΔΜΗΕ / ΔΕΔΔΗΕ)",
        "emoji": "🔌",
        "desc": (
            "Κόστος χρήσης του Συστήματος Μεταφοράς Υψηλής Τάσης (ΑΔΜΗΕ). "
            "⚠️ Χρεώνεται επί της ΣΥΝΟΛΙΚΗΣ κατανάλωσης μετρητή — δεν μειώνεται από το net metering."
        ),
        "formula": "ΣΥΝΟΛΙΚΑ kWh μετρητή × τιμή €/kWh (ρυθμιζόμενη από ΡΑΕ)",
        "affected_by_pv": False,
    },
    "Χρέωση Χρήσης Δικτύου": {
        "category": "🔌 Χρεώσεις Δικτύου (ΑΔΜΗΕ / ΔΕΔΔΗΕ)",
        "emoji": "🔌",
        "desc": (
            "Κόστος χρήσης του Δικτύου Διανομής Χαμηλής/Μέσης Τάσης (ΔΕΔΔΗΕ). "
            "Καλύπτει τη συντήρηση των γραμμών, μετασχηματιστών και λοιπής υποδομής. "
            "⚠️ Χρεώνεται επί της ΣΥΝΟΛΙΚΗΣ κατανάλωσης μετρητή — δεν μειώνεται από το net metering."
        ),
        "formula": "ΣΥΝΟΛΙΚΑ kWh μετρητή × τιμή €/kWh (ρυθμιζόμενη από ΡΑΕ)",
        "affected_by_pv": False,
    },
    "Χρέωση Μέτρησης": {
        "category": "🔌 Χρεώσεις Δικτύου (ΑΔΜΗΕ / ΔΕΔΔΗΕ)",
        "emoji": "📟",
        "desc": (
            "Πάγια χρέωση για τη μίσθωση, συντήρηση και ανάγνωση "
            "του μετρητή (παλιός αναλογικός ή νέος έξυπνος/smart meter)."
        ),
        "formula": "Σταθερό ποσό €/μήνα × μήνες",
        "affected_by_pv": False,
    },

    # ── Πάγιες / Λοιπές ───────────────────────────────────────────
    "Πάγια Χρέωση": {
        "category": "📋 Πάγιες Χρεώσεις",
        "emoji": "📋",
        "desc": (
            "Σταθερό μηνιαίο ποσό που χρεώνεται ανεξάρτητα από την "
            "κατανάλωση. Καλύπτει διοικητικό κόστος, διαχείριση σύμβασης "
            "και διατήρηση της παροχής."
        ),
        "formula": "Σταθερό €/μήνα × μήνες (π.χ. 3,30 €/μήνα × 2)",
        "affected_by_pv": False,
    },
    "Τέλος Ανακύκλωσης": {
        "category": "📋 Πάγιες Χρεώσεις",
        "emoji": "♻️",
        "desc": (
            "Τέλος υπέρ του συστήματος εναλλακτικής διαχείρισης "
            "ηλεκτρικών & ηλεκτρονικών συσκευών (WEEE). "
            "Αποδίδεται στην Ανακύκλωση Συσκευών ΑΕ."
        ),
        "formula": "Σταθερό πάγιο ποσό",
        "affected_by_pv": False,
    },

    # ── Φόροι ──────────────────────────────────────────────────────
    "ΦΠΑ": {
        "category": "🧾 Φόροι",
        "emoji": "🧾",
        "desc": (
            "Φόρος Προστιθέμενης Αξίας 6% επί όλων των χρεώσεων. "
            "✅ Το τμήμα ΦΠΑ που αντιστοιχεί στη χρέωση ενέργειας (Προμήθεια) "
            "μειώνεται μέσω net metering. Το ΦΠΑ των υπόλοιπων χρεώσεων παραμένει σταθερό."
        ),
        "formula": "6% × (σύνολο χρεώσεων πριν ΦΠΑ)",
        "affected_by_pv": True,  # μερικώς — μόνο το ΦΠΑ της ενέργειας
    },
    "ΕΦΚ": {
        "category": "🧾 Φόροι",
        "emoji": "🧾",
        "desc": (
            "Ειδικός Φόρος Κατανάλωσης. Εισπράττεται υπέρ του Ελληνικού Δημοσίου. "
            "⚠️ Χρεώνεται επί της ΣΥΝΟΛΙΚΗΣ κατανάλωσης μετρητή — δεν μειώνεται από το net metering."
        ),
        "formula": "ΣΥΝΟΛΙΚΑ kWh μετρητή × 0,00275 €/kWh",
        "affected_by_pv": False,
    },
    "Τέλος ΑΠΕ": {
        "category": "🌱 Ειδικοί Φόροι & Ανανεώσιμες Πηγές",
        "emoji": "🌱",
        "desc": (
            "Τέλος υπέρ Ανανεώσιμων Πηγών Ενέργειας — αποδίδεται στο ΕΛΑΠΕ. "
            "⚠️ Χρεώνεται επί της ΣΥΝΟΛΙΚΗΣ κατανάλωσης μετρητή — δεν μειώνεται από το net metering."
        ),
        "formula": "ΣΥΝΟΛΙΚΑ kWh μετρητή × ρυθμιζόμενη τιμή",
        "affected_by_pv": False,
    },
    "ΕΔΑΠ": {
        "category": "🌱 Ειδικοί Φόροι & Ανανεώσιμες Πηγές",
        "emoji": "🌱",
        "desc": (
            "Ειδική Διαχειριστική Αμοιβή Παραγωγής. Χρέωση υπέρ "
            "του Λειτουργού της Αγοράς Ηλεκτρικής Ενέργειας (ΛΑΓΗΕ). "
            "⚠️ Χρεώνεται επί της ΣΥΝΟΛΙΚΗΣ κατανάλωσης μετρητή — δεν μειώνεται από το net metering."
        ),
        "formula": "ΣΥΝΟΛΙΚΑ kWh μετρητή × τιμή €/kWh",
        "affected_by_pv": False,
    },
    "Λοιπές Χρεώσεις": {
        "category": "📋 Πάγιες Χρεώσεις",
        "emoji": "📋",
        "desc": "Διάφορες μικρές χρεώσεις (δήμοι, λοιπά τέλη).",
        "formula": "Βάσει ισχύουσας νομοθεσίας",
        "affected_by_pv": False,
    },
}


# ─────────────────────────────────────────────────────────────────
# ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ
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
        (r'(ΕΤΜΕΑΡ)[^\d]+([\d\.,]+)\s*€?', "ΕΤΜΕΑΡ"),
        (r'(ΥΚΩ)[^\d]+([\d\.,]+)\s*€?', "ΥΚΩ"),
        (r'(ΦΠΑ\s+\d+%?)[^\d]+([\d\.,]+)\s*€?', "ΦΠΑ"),
        (r'(ΕΦΚ)[^\d]+([\d\.,]+)\s*€?', "ΕΦΚ"),
        (r'(Πάγια\s+Χρέωση)[^\d]+([\d\.,]+)\s*€?', "Πάγια Χρέωση"),
        (r'(Χρέωση\s+Χρήσης\s+Συστήματος)[^\d]+([\d\.,]+)\s*€?', "Χρέωση Χρήσης Συστήματος"),
        (r'(Χρέωση\s+Χρήσης\s+Δικτύου)[^\d]+([\d\.,]+)\s*€?', "Χρέωση Χρήσης Δικτύου"),
        (r'(Χρέωση\s+Μέτρησης)[^\d]+([\d\.,]+)\s*€?', "Χρέωση Μέτρησης"),
        (r'(Τέλος\s+Ανακύκλωσης)[^\d]+([\d\.,]+)\s*€?', "Τέλος Ανακύκλωσης"),
        (r'(Χρεώσεις\s+Προμήθειας\s+ΔΕΗ)[^\d]+([\d\.,]+)\s*€?', "Χρεώσεις Προμήθειας"),
        (r'(ΕΔΑΠ)[^\d]+([\d\.,]+)\s*€?', "ΕΔΑΠ"),
        (r'(Τέλος\s+ΑΠΕ)[^\d]+([\d\.,]+)\s*€?', "Τέλος ΑΠΕ"),
    ]
    for pattern, key in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                val = clean_number(match.group(2))
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

    return total_kwh, billed_kwh, energy_charge, total_bill, exact_avg_rate, processed_text, all_charges


# ─────────────────────────────────────────────────────────────────
# UI
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

                    hypo_energy_charge = safe_energy_charge + saved_energy
                    actual_other_charges = actual_paid - safe_energy_charge
                    hypo_other_charges = actual_other_charges + saved_vat
                    hypo_total_bill = actual_paid + total_saved

                    # ── LEGEND ────────────────────────────────────────────────
                    st.markdown("""
<div class="legend-box">
    <h4>📌 Τι μειώνει το Net Metering στον λογαριασμό σας</h4>
    <div class="legend-row">
        <div class="dot-green"></div>
        <span><b style="color:#4CAF50">Χρέωση Προμήθειας (€/kWh)</b> — μειώνεται κατά τις kWh που κάλυψε το Φ/Β</span>
    </div>
    <div class="legend-row">
        <div class="dot-green"></div>
        <span><b style="color:#4CAF50">ΦΠΑ 6%</b> επί της Προμήθειας — μειώνεται αναλογικά</span>
    </div>
    <div class="legend-row" style="margin-top:6px;">
        <div class="dot-red"></div>
        <span><b style="color:#F44336">Όλες οι υπόλοιπες χρεώσεις</b> (ΕΤΜΕΑΡ, ΥΚΩ, Δίκτυο, ΕΦΚ, Πάγιες κλπ.)
        χρεώνονται επί της <u>συνολικής κατανάλωσης μετρητή</u> — το Φ/Β ΔΕΝ τις μειώνει.</span>
    </div>
</div>
""", unsafe_allow_html=True)

                    # ── ΚΕΡΔΟΣ BANNER ─────────────────────────────────────────
                    st.markdown(f"""
<div class="savings-banner">
    <div class="savings-amount">+{total_saved:.2f} €</div>
    <div class="savings-label">Συνολικό Καθαρό Κέρδος από το Φωτοβολταϊκό σας</div>
    <div style="margin-top:14px; display:flex; gap:8px; justify-content:center; flex-wrap:wrap;">
        <span class="info-pill">⚡ {hidden_kwh:.0f} kWh εξοικονομήθηκαν</span>
        <span class="info-pill">💶 {saved_energy:.2f} € ενέργεια</span>
        <span class="info-pill">🧾 {saved_vat:.2f} € ΦΠΑ</span>
        <span class="info-pill">📊 {avg_rate_no_vat:.4f} €/kWh μέση τιμή</span>
    </div>
</div>
""", unsafe_allow_html=True)

                    if total_bill is not None and total_bill < 0:
                        st.info(f"ℹ️ Ο λογαριασμός σας είναι **πιστωτικός** ({total_bill:.2f} €) — η ΔΕΗ σάς επιστρέφει χρήματα!")

                    st.markdown("### 📊 Σύγκριση Τιμολόγησης")
                    st.markdown(
                        "Τα **🟢 πράσινα** είναι τι πληρώσατε (με Φ/Β) · τα **🔴 κόκκινα** τι θα πληρώνατε χωρίς Φ/Β. "
                        "Μόνο η Προμήθεια + ΦΠΑ της αλλάζουν.",
                        unsafe_allow_html=False
                    )

                    comparison_html = f"""
<div style="background:#111827; padding:20px; border-radius:16px; border:1px solid #2d2d2d; margin-bottom:25px;">
  <table style="width:100%; border-collapse:collapse; font-family:'DM Sans',sans-serif;">
    <tr style="border-bottom:1px solid #2d2d2d;">
      <td style="padding:12px 0; color:#ccc;">⚡ <b>Τιμολογημένες kWh (net)</b></td>
      <td style="text-align:right; padding:12px 0;">
        <span style="color:#4CAF50; font-weight:700; font-size:1.2em;">{billed_kwh:.0f} kWh</span>
        <span style="color:#F44336; margin-left:10px; font-size:0.95em;">({total_kwh:.0f} kWh χωρίς Φ/Β)</span>
      </td>
    </tr>
    <tr style="border-bottom:1px solid #2d2d2d;">
      <td style="padding:12px 0; color:#ccc;">💶 <b>Χρέωση Προμήθειας ΔΕΗ</b> <span style="font-size:0.8em; color:#4CAF50;">✅ μειώνεται</span></td>
      <td style="text-align:right; padding:12px 0;">
        <span style="color:#4CAF50; font-weight:700; font-size:1.2em;">{safe_energy_charge:.2f} €</span>
        <span style="color:#F44336; margin-left:10px; font-size:0.95em;">({hypo_energy_charge:.2f} €)</span>
      </td>
    </tr>
    <tr style="border-bottom:1px solid #2d2d2d;">
      <td style="padding:12px 0; color:#ccc;">🛡️ <b>ΕΤΜΕΑΡ / ΥΚΩ / Δίκτυο / Πάγιες</b> <span style="font-size:0.8em; color:#F44336;">⚠️ σταθερές</span></td>
      <td style="text-align:right; padding:12px 0;">
        <span style="color:#aaa; font-weight:600; font-size:1.1em;">{(actual_paid - safe_energy_charge - (actual_paid - safe_energy_charge - actual_other_charges)):.2f} €</span>
        <span style="color:#aaa; margin-left:10px; font-size:0.9em;">(ίδιο και χωρίς Φ/Β)</span>
      </td>
    </tr>
    <tr style="border-bottom:2px solid #3d3d3d;">
      <td style="padding:12px 0; color:#ccc;">🧾 <b>ΦΠΑ 6%</b> <span style="font-size:0.8em; color:#4CAF50;">✅ μερικά μειώνεται</span></td>
      <td style="text-align:right; padding:12px 0;">
        <span style="color:#4CAF50; font-weight:700; font-size:1.2em;">{actual_other_charges:.2f} €</span>
        <span style="color:#F44336; margin-left:10px; font-size:0.95em;">({hypo_other_charges:.2f} €)</span>
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

                    # ── BAR CHART ΚΑΤΑΝΟΜΗ ΧΡΕΩΣΕΩΝ (native HTML) ───────────
                    st.markdown("### 📈 Κατανομή Χρεώσεων")
                    st.markdown(
                        "🟢 Πράσινο = μειώνεται από net metering &nbsp;|&nbsp; "
                        "🔴 Κόκκινο = χρεώνεται κανονικά (πλήρης κατανάλωση)",
                        unsafe_allow_html=True
                    )

                    if all_charges:
                        sorted_charges = sorted(all_charges.items(), key=lambda x: x[1], reverse=True)
                        max_val = max(v for _, v in sorted_charges) if sorted_charges else 1

                        bars_html = ""
                        for name, val in sorted_charges:
                            info = CHARGE_INFO.get(name, {})
                            is_pv = info.get("affected_by_pv", False)
                            color = "#4CAF50" if is_pv else "#F44336"
                            bg_color = "#1a3a1a" if is_pv else "#2a1a1a"
                            pct = (val / max_val) * 100
                            bars_html += f"""
<div style="margin:8px 0;">
  <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;">
    <span style="font-size:0.9rem; color:#ddd; flex:1;">{name}</span>
    <span style="font-family:'DM Mono',monospace; font-size:0.9rem; color:{color}; font-weight:600; margin-left:12px;">{val:.2f} €</span>
  </div>
  <div style="background:#1e1e1e; border-radius:6px; height:22px; overflow:hidden;">
    <div style="width:{pct:.1f}%; background:{color}; height:100%; border-radius:6px;
                display:flex; align-items:center; padding-left:8px; min-width:4px;
                transition:width 0.5s ease; background: linear-gradient(90deg, {color}cc, {color});"></div>
  </div>
</div>"""

                        st.markdown(
                            f'<div style="background:#111827; padding:20px; border-radius:14px; '
                            f'border:1px solid #2d2d2d;">{bars_html}</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.info("Δεν εντοπίστηκαν αναλυτικές χρεώσεις για γράφημα.")

                    # ── ΠΛΗΡΗΣ ΑΝΑΛΥΣΗ ΚΑΘΕ ΧΡΕΩΣΗΣ ─────────────────────────
                    st.markdown("### 📚 Πλήρης Ανάλυση Κάθε Χρέωσης")
                    st.markdown(
                        "Παρακάτω εξηγείται κάθε γραμμή του λογαριασμού σας — τι είναι, "
                        "πώς υπολογίζεται και αν επηρεάζεται από το φωτοβολταϊκό σας."
                    )

                    # Ομαδοποίηση κατά κατηγορία
                    categories_seen = []
                    charges_by_category = {}
                    for charge_name, amount in all_charges.items():
                        info = CHARGE_INFO.get(charge_name, {
                            "category": "📋 Λοιπές Χρεώσεις",
                            "emoji": "📋",
                            "desc": "Χρέωση που εντοπίστηκε στο λογαριασμό.",
                            "formula": "—",
                            "affected_by_pv": False,
                        })
                        cat = info["category"]
                        if cat not in charges_by_category:
                            charges_by_category[cat] = []
                        charges_by_category[cat].append((charge_name, amount, info))

                    for cat, items in charges_by_category.items():
                        st.markdown(f'<div class="category-header">{cat}</div>', unsafe_allow_html=True)
                        for charge_name, amount, info in items:
                            pv_badge = (
                                '<span style="background:#1a3a1a;color:#4CAF50;border-radius:6px;'
                                'padding:2px 8px;font-size:0.78rem;margin-left:8px;">✅ Μειώνεται με net metering</span>'
                                if info["affected_by_pv"] else
                                '<span style="background:#2a1a1a;color:#F44336;border-radius:6px;'
                                'padding:2px 8px;font-size:0.78rem;margin-left:8px;">⚠️ ΔΕΝ μειώνεται — χρεώνεται κανονικά</span>'
                            )

                            # Εξοικονόμηση ΜΟΝΟ για χρέωση Προμήθειας
                            benefit_note = ""
                            if charge_name == "Χρεώσεις Προμήθειας" and hidden_kwh and avg_rate_no_vat:
                                benefit_note = (
                                    f'<div style="margin-top:6px;font-size:0.85rem;color:#4CAF50;">'
                                    f'💡 Εξοικονόμηση από net metering: {saved_energy:.2f} € '
                                    f'({hidden_kwh:.0f} kWh × {avg_rate_no_vat:.4f} €/kWh)'
                                    f'</div>'
                                )
                            elif charge_name == "ΦΠΑ":
                                benefit_note = (
                                    f'<div style="margin-top:6px;font-size:0.85rem;color:#4CAF50;">'
                                    f'💡 Εξοικονόμηση ΦΠΑ από net metering: {saved_vat:.2f} € '
                                    f'(6% × {saved_energy:.2f} €)'
                                    f'</div>'
                                )

                            st.markdown(f"""
<div class="charge-card">
  <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
    <div>
      <span class="charge-title">{info.get('emoji','')} {charge_name}</span>
      {pv_badge}
    </div>
    <span class="charge-amount charge-amount-actual">{amount:.2f} €</span>
  </div>
  <div class="charge-desc">{info['desc']}</div>
  <div class="charge-formula">🧮 {info['formula']}</div>
  {benefit_note}
</div>
""", unsafe_allow_html=True)

                    # ── REPORT ────────────────────────────────────────────────
                    st.markdown("### 📖 Αναλυτικό Report Κέρδους")
                    st.markdown(f"""
**1. Ενέργεια που παράξατε και "γλιτώσατε":**
Ο μετρητής κατέγραψε **{total_kwh:.0f} kWh** συνολικά, αλλά η ΔΕΗ τιμολόγησε μόνο **{billed_kwh:.0f} kWh** (net metering).
→ **{hidden_kwh:.0f} kWh** καλύφθηκαν από το φωτοβολταϊκό σας.

**2. Μέση τιμή ενέργειας:** **{avg_rate_no_vat:.4f} €/kWh** (χωρίς ΦΠΑ)

**3. Ανάλυση κέρδους:**
- 💡 Εξοικονόμηση ενέργειας: **{saved_energy:.2f} €**
- 🧾 Εξοικονόμηση ΦΠΑ 6%: **{saved_vat:.2f} €**

**✅ ΣΥΝΟΛΙΚΟ ΟΦΕΛΟΣ: {total_saved:.2f} €**
""")

        except Exception as e:
            st.error(f"❌ Σφάλμα κατά την ανάλυση: {e}")
            st.info("Βεβαιωθείτε ότι ανεβάσατε έγκυρο PDF λογαριασμού ΔΕΗ.")

# ── ΥΠΟΓΡΑΦΗ ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#666; padding-top:16px;'>
  <p style='font-size:1.05em;'><i>Μια προσφορά της <b style="color:#F5A623">Zarkolia Health</b></i></p>
  <p style='margin:4px 0;'><b>Πάνος Ζαρογουλίδης</b></p>
  <p style='font-size:0.88em; color:#555;'>Φαρμακοποιός MSc, MBA, Διαμεσολαβητής</p>
</div>
""", unsafe_allow_html=True)
