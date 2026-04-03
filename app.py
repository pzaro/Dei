import streamlit as st
import fitz  # PyMuPDF
import re

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Φ/Β Κέρδος Net Metering", page_icon="☀️", layout="centered")

st.title("☀️ Υπολογιστής Κέρδους Net Metering")
st.markdown("Ανεβάστε τον λογαριασμό της ΔΕΗ (εκκαθαριστικό ή έναντι, σε μορφή PDF) για να δείτε το πραγματικό σας όφελος από το φωτοβολταϊκό σας.")

def clean_number(s):
    """Μετατρέπει string αριθμό (π.χ. '1.060' ή '1,060') σε float."""
    s = s.strip()
    # Αν έχει τελεία ΚΑΙ κόμμα → χιλ. διαχωριστής είναι η τελεία
    if '.' in s and ',' in s:
        s = s.replace('.', '').replace(',', '.')
    # Αν έχει μόνο τελεία → ελέγχουμε αν είναι χιλ. διαχωριστής (π.χ. 1.060)
    elif '.' in s and ',' not in s:
        parts = s.split('.')
        if len(parts) == 2 and len(parts[1]) == 3:
            # Είναι χιλιάδες (π.χ. 1.060)
            s = s.replace('.', '')
        # αλλιώς είναι δεκαδική τελεία (π.χ. 0.069) → αφήνουμε ως έχει
    # Αν έχει μόνο κόμμα → δεκαδικό κόμμα
    elif ',' in s and '.' not in s:
        s = s.replace(',', '.')
    return float(s)

def parse_dei_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"

    # Βασικές διορθώσεις OCR
    processed_text = (text
                      .replace("Bkwh", "8kWh")
                      .replace("B kwh", "8 kWh")
                      .replace("awn", "kWh"))

    # ── 1. ΣΥΝΟΛΟ ΚΑΤΑΝΑΛΩΣΗΣ (kWh μετρητή) ──────────────────────────────────
    total_kwh = None

    # Pattern A: "ΚΑΤΑΝΑΛΩΣΗ ....: 1.060" (χιλ. με τελεία → clean_number)
    match_total = re.search(r'ΚΑΤΑΝΑΛΩΣΗ\s*[\.\s]*:\s*([\d\.]+)', processed_text, re.IGNORECASE)
    if match_total:
        try:
            total_kwh = clean_number(match_total.group(1))
        except ValueError:
            pass

    # Pattern B: "Σύνολο Κατανάλωσης 1060"
    if total_kwh is None:
        match_total2 = re.search(r'Σύνολο\s*Κατανάλωσης\s+([\d\.,]+)', processed_text, re.IGNORECASE)
        if match_total2:
            try:
                total_kwh = clean_number(match_total2.group(1))
            except ValueError:
                pass

    # Pattern C: Αναζήτηση από "Κατανάλωση Ηλεκτρικής Ενέργειας ΧΧΧΧ kWh"
    if total_kwh is None:
        match_total3 = re.search(r'Κατανάλωση\s+Ηλεκτρικής\s+Ενέργειας\s+([\d\.,]+)\s*kWh', processed_text, re.IGNORECASE)
        if match_total3:
            try:
                total_kwh = clean_number(match_total3.group(1))
            except ValueError:
                pass

    # Pattern D: Άθροισμα από πίνακα μετρητή — "Σύνολο Κατανάλωσης" στήλη
    if total_kwh is None:
        meter_totals = re.findall(r'T\d+\s+1[12]\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)', processed_text)
        if meter_totals:
            total_kwh = sum(float(x) for x in meter_totals)

    # ── 2. ΤΙΜΟΛΟΓΗΜΕΝΕΣ kWh & ΜΕΣΗ ΤΙΜΗ ΕΝΕΡΓΕΙΑΣ ───────────────────────────
    billed_kwh = 0.0
    total_tier_cost = 0.0
    exact_avg_rate = None

    supply_section = re.search(r'Αναλυτικά οι χρεώσεις(.*?)Ρυθμιζόμενες\s*Χρεώσεις', processed_text, re.IGNORECASE | re.DOTALL)

    if supply_section:
        section_text = supply_section.group(1)
        pattern_kwh = re.compile(r'\(?\s*(\d+)\s*[kK][wW][hH]\s*[xX×]\s*([\d,\.]+)\s*€?/?\s*[kK][wW][hH]\s*\)?', re.IGNORECASE)
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

    # ── 3. ΧΡΕΩΣΗ ΕΝΕΡΓΕΙΑΣ (Χρεώσεις Προμήθειας ΔΕΗ) ───────────────────────
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
            match_energy2 = re.search(r'Χρέωση\s*Ενέργειας\s*Κανονική[\s\S]{0,50}?([\d,\.]+)', processed_text, re.IGNORECASE)
            if match_energy2:
                try:
                    energy_charge = clean_number(match_energy2.group(1))
                    billed_kwh = round(energy_charge / 0.135)
                    exact_avg_rate = energy_charge / billed_kwh if billed_kwh > 0 else 0.139
                except ValueError:
                    pass

    # ── 4. ΣΥΝΟΛΟ ΛΟΓΑΡΙΑΣΜΟΥ ─────────────────────────────────────────────────
    total_bill = None

    match_bill = re.search(r'Συνολικό\s+(?:πιστωτικό\s+υπόλοιπο|ποσό\s+πληρωμής)\s*(-?[\d\.,]+)\s*€?', processed_text, re.IGNORECASE)
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

    return total_kwh, billed_kwh, energy_charge, total_bill, exact_avg_rate, processed_text

# ── UI & ΛΟΓΙΚΗ ───────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("📄 Επιλέξτε το PDF του λογαριασμού σας", type="pdf")

if uploaded_file is not None:
    file_bytes = uploaded_file.read()

    with st.spinner('Αναλύεται ο λογαριασμός...'):
        try:
            total_kwh, billed_kwh, energy_charge, total_bill, exact_avg_rate, raw_text = parse_dei_pdf(file_bytes)

            # ── DEBUG (Επεκτείνεται αν χρειαστείς έλεγχο) ──────────────────────
            with st.expander("🔍 Debug: Τιμές που εντοπίστηκαν (για τεχνικό έλεγχο)"):
                st.write(f"**total_kwh (μετρητής):** {total_kwh}")
                st.write(f"**billed_kwh (τιμολογημένες):** {billed_kwh}")
                st.write(f"**energy_charge (€):** {energy_charge}")
                st.write(f"**total_bill (€):** {total_bill}")
                st.write(f"**exact_avg_rate (€/kWh):** {exact_avg_rate}")

            if not total_kwh or not billed_kwh:
                st.error("❌ Δεν ήταν δυνατή η ανάγνωση των kWh από τον λογαριασμό. "
                         "Βεβαιωθείτε ότι ανεβάσατε εκκαθαριστικό λογαριασμό ΔΕΗ με αναλυτικές χρεώσεις.")
            else:
                hidden_kwh = total_kwh - billed_kwh

                if hidden_kwh <= 0:
                    st.warning("⚠️ Δεν εντοπίστηκε απόκρυφη έκπτωση. Οι χρεωθείσες kWh είναι ίσες ή περισσότερες από τον μετρητή.")
                else:
                    safe_energy_charge = energy_charge if energy_charge is not None else 0.0
                    safe_total_bill = abs(total_bill) if total_bill is not None else 0.0
                    actual_paid = total_bill if total_bill is not None else 0.0
                    avg_rate_no_vat = exact_avg_rate if exact_avg_rate is not None else 0.139

                    VAT_RATE = 0.06  # ΦΠΑ 6%

                    # ── ΝΕΟΣ ΥΠΟΛΟΓΙΣΜΟΣ ΟΦΕΛΟΥΣ (ΜΟΝΟ ΕΝΕΡΓΕΙΑ + ΦΠΑ) ─────────
                    # Κέρδος Ενέργειας
                    saved_energy = hidden_kwh * avg_rate_no_vat
                    
                    # Αναλογούν ΦΠΑ της σωσμένης ενέργειας
                    saved_vat = saved_energy * VAT_RATE
                    
                    # Συνολικό Όφελος
                    total_saved = saved_energy + saved_vat

                    # ── ΕΙΚΟΝΙΚΑ ΠΟΣΑ (χωρίς Φ/Β) ──────────────────────────────
                    hypo_energy_charge = safe_energy_charge + saved_energy
                    actual_other_charges = actual_paid - safe_energy_charge
                    hypo_other_charges = actual_other_charges + saved_vat
                    hypo_total_bill = actual_paid + total_saved

                    # ── ΑΠΟΤΕΛΕΣΜΑΤΑ ───────────────────────────────────────────
                    st.success(f"🎉 Το συνολικό σας καθαρό όφελος είναι **{total_saved:.2f} €**")

                    if total_bill is not None and total_bill < 0:
                        st.info(f"ℹ️ Ο λογαριασμός σας είναι **πιστωτικός** ({total_bill:.2f} €) — η ΔΕΗ σάς επιστρέφει χρήματα!")

                    st.markdown("### 📊 Σύγκριση Τιμολόγησης")
                    st.markdown("*Με πράσινο χρώμα βλέπετε τι τελικά πληρώσατε (ή λάβατε), ενώ με κόκκινο στην παρένθεση τι θα πληρώνατε χωρίς το Φωτοβολταϊκό.*")

                    comparison_html = f"""
                    <div style="background-color: #1e1e1e; padding: 20px; border-radius: 15px; border: 1px solid #444; margin-bottom: 25px;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 1.1em;">
                            <tr style="border-bottom: 1px solid #444;">
                                <td style="padding: 10px 0;">⚡ <b>Κατανάλωση (kWh)</b></td>
                                <td style="text-align: right; padding: 10px 0;">
                                    <span style="color: #4CAF50; font-weight: bold; font-size: 1.2em;">{billed_kwh:.0f}</span>
                                    <span style="color: #F44336; margin-left: 8px;">({total_kwh:.0f})</span>
                                </td>
                            </tr>
                            <tr style="border-bottom: 1px solid #444;">
                                <td style="padding: 10px 0;">💶 <b>Αξία Καθαρής Ενέργειας</b></td>
                                <td style="text-align: right; padding: 10px 0;">
                                    <span style="color: #4CAF50; font-weight: bold; font-size: 1.2em;">{safe_energy_charge:.2f} €</span>
                                    <span style="color: #F44336; margin-left: 8px;">({hypo_energy_charge:.2f} €)</span>
                                </td>
                            </tr>
                            <tr style="border-bottom: 2px solid #666;">
                                <td style="padding: 10px 0;">🛡️ <b>Φόροι & Λοιπά (Περιλ. ΦΠΑ οφέλους)</b></td>
                                <td style="text-align: right; padding: 10px 0;">
                                    <span style="color: #4CAF50; font-weight: bold; font-size: 1.2em;">{actual_other_charges:.2f} €</span>
                                    <span style="color: #F44336; margin-left: 8px;">({hypo_other_charges:.2f} €)</span>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 15px 0; font-size: 1.2em;">💰 <b>ΣΥΝΟΛΟ ΛΟΓΑΡΙΑΣΜΟΥ</b></td>
                                <td style="text-align: right; padding: 15px 0;">
                                    <span style="color: #4CAF50; font-weight: bold; font-size: 1.4em;">{actual_paid:.2f} €</span>
                                    <span style="color: #F44336; font-size: 1.2em; margin-left: 8px;">({hypo_total_bill:.2f} €)</span>
                                </td>
                            </tr>
                        </table>
                    </div>
                    """
                    st.markdown(comparison_html, unsafe_allow_html=True)

                    # ── REPORT ΚΕΡΔΟΥΣ ─────────────────────────────────────────
                    st.markdown("### 📖 Αναλυτικό Report Κέρδους")
                    st.markdown(f"""
**1. Ενέργεια που παράξατε και "γλιτώσατε":** Ο μετρητής κατέγραψε συνολικά **{total_kwh:.0f} kWh**, αλλά η ΔΕΗ σας τιμολόγησε μόνο για τις **{billed_kwh:.0f} kWh** (net metering).
Αυτό σημαίνει ότι **{hidden_kwh:.0f} kWh** καλύφθηκαν από την παραγωγή του φωτοβολταϊκού σας.

**2. Μέση τιμή ενέργειας:** **{avg_rate_no_vat:.4f} €/kWh** (χωρίς ΦΠΑ)

**3. Ανάλυση κέρδους (Βάσει καθαρής αξίας & ΦΠΑ):**
* 💡 Εξοικονόμηση ενέργειας: **{saved_energy:.2f} €**
* 🧾 Εξοικονόμηση ΦΠΑ (6%): **{saved_vat:.2f} €**

**✅ ΣΥΝΟΛΙΚΟ ΟΦΕΛΟΣ: {total_saved:.2f} €**
                    """)

        except Exception as e:
            st.error(f"❌ Παρουσιάστηκε σφάλμα κατά την ανάλυση: {e}")
            st.info("Βεβαιωθείτε ότι ανεβάσατε έγκυρο PDF λογαριασμού ΔΕΗ.")

# --- ΕΠΑΓΓΕΛΜΑΤΙΚΗ ΥΠΟΓΡΑΦΗ ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding-top: 20px;'>
    <p style='font-size: 1.1em;'><i>Μια προσφορά της <b>Zarkolia Health</b></i></p>
    <p>
        <b>Πάνος Ζαρογουλίδης</b><br>
        <span style='font-size: 0.9em;'>Φαρμακοποιός MSc, MBA, Διαμεσολαβητής</span>
    </p>
</div>
""", unsafe_allow_html=True)
