import streamlit as st
import fitz  # PyMuPDF
import re

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Φ/Β Κέρδος Net Metering", page_icon="☀️", layout="centered")

st.title("☀️ Υπολογιστής Κέρδους Net Metering")
st.markdown("Ανεβάστε τον εκκαθαριστικό λογαριασμό της ΔΕΗ (σε μορφή PDF) για να δείτε το πραγματικό σας όφελος.")

def parse_dei_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    
    processed_text = text.replace("Bkwh", "8kWh").replace("B kwh", "8 kWh").replace("awn", "kWh")

    # 1. Σύνολο Μετρητή (Προστέθηκε η 'Διαφορά Ενδείξεων')
    total_kwh = None
    match_total = re.search(r'(?:Διαφορά Ενδείξεων|Ποσότητα|Κατανάλωση|Σύνολο|ΚΑΤΑΝΑΛΩΣΗ)\s*(?:kWh)?\s*[:\-\.]?\s*(\d+)', processed_text, re.IGNORECASE)
    if match_total:
        total_kwh = float(match_total.group(1))

    # 2. Τιμολογημένες Μονάδες
    billed_kwh = 0
    total_tier_cost = 0.0
    exact_avg_rate = None
    
    supply_section = re.search(r'Αναλυτικά οι χρεώσεις(.*?)Ρυθμιζόμενες Χρεώσεις', processed_text, re.IGNORECASE | re.DOTALL)
    
    if supply_section:
        section_text = supply_section.group(1)
        pattern_billed = r'(\d+)\s*[a-zA-Zα-ωΑ-Ω]*\s*[x×X]\s*(\d+[.,]\d+)'
        matches = re.finditer(pattern_billed, section_text)
        
        for match in matches:
            kwh_tier = float(match.group(1))
            rate_tier = float(match.group(2).replace(',', '.'))
            billed_kwh += kwh_tier
            total_tier_cost += kwh_tier * rate_tier
            
    # 3. Υπολογισμός Χρέωσης Ενέργειας
    energy_charge = None
    if billed_kwh > 0:
        exact_avg_rate = total_tier_cost / billed_kwh
        energy_charge = round(total_tier_cost, 2) 
    else:
        # Εναλλακτική αναζήτηση αν αποτύχει η πρώτη
        match_energy = re.search(r'Χρέωση\s*Ενέργειας[\s\S]{0,50}?(\d+[.,]\d+)', processed_text, re.IGNORECASE)
        if match_energy:
            energy_charge = float(match_energy.group(1).replace(',', '.'))
            billed_kwh = round(energy_charge / 0.135) # Εκτίμηση βάσει παλιού τιμολογίου
            exact_avg_rate = energy_charge / billed_kwh if billed_kwh > 0 else 0.139

    # 4. Συνολικό Ποσό Λογαριασμού
    total_bill = None
    match_bill = re.search(r'\*(\d+[.,]\d+)\s*€|Συνολικό\s*ποσό\s*πληρωμής.*?(?:€)?\s*(\d+[.,]\d+)', processed_text, re.IGNORECASE)
    if match_bill:
        total_bill = float((match_bill.group(1) or match_bill.group(2)).replace(',', '.'))

    return total_kwh, billed_kwh, energy_charge, total_bill, exact_avg_rate, processed_text

# --- UI & ΛΟΓΙΚΗ ---
uploaded_file = st.file_uploader("📄 Επιλέξτε το PDF του λογαριασμού σας", type="pdf")

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    
    with st.spinner('Αναλύεται ο λογαριασμός...'):
        try:
            total_kwh, billed_kwh, energy_charge, total_bill, exact_avg_rate, processed_text = parse_dei_pdf(file_bytes)
            
            if total_kwh and billed_kwh:
                hidden_kwh = total_kwh - billed_kwh
                
                if hidden_kwh <= 0:
                    st.warning("⚠️ Δεν εντοπίστηκε διαφορά στις kWh. Οι χρεωθείσες kWh είναι ίσες με τον μετρητή.")
                else:
                    avg_rate_no_vat = exact_avg_rate if exact_avg_rate is not None else 0.139
                    VAT_RATE = 0.06 # ΦΠΑ 6%
                    
                    # 1. Αξία των μη τιμολογηθεισών kWh
                    saved_energy_value = hidden_kwh * avg_rate_no_vat
                    # 2. ΦΠΑ που αναλογεί στην αξία αυτή
                    saved_vat = saved_energy_value * VAT_RATE
                    # Συνολικό Όφελος
                    total_saved = saved_energy_value + saved_vat

                    # Εικονικό συνολικό ποσό αν δεν υπήρχε το Φ/Β
                    safe_total_bill = total_bill if total_bill is not None else 0.0
                    hypo_total_bill = safe_total_bill + total_saved

                    # --- ΑΠΟΤΕΛΕΣΜΑΤΑ ---
                    st.success(f"🎉 Το συνολικό σας όφελος είναι **{total_saved:.2f} €**")
                    
                    st.markdown("### 📊 Ανάλυση Οφέλους")
                    st.write(f"**Μη τιμολογηθείσες kWh:** {hidden_kwh:.0f} kWh")
                    st.write(f"**Καθαρή αξία ενέργειας:** {saved_energy_value:.2f} €")
                    st.write(f"**Αναλογούν ΦΠΑ (6%):** {saved_vat:.2f} €")

                    st.info(f"Χωρίς το Φωτοβολταϊκό, ο λογαριασμός σας θα ήταν **{hypo_total_bill:.2f} €** αντί για **{safe_total_bill:.2f} €**.")
            else:
                # ΕΔΩ ΕΙΝΑΙ Η ΠΡΟΣΘΗΚΗ: Τι γίνεται αν δεν βρει τα νούμερα
                st.error("❌ Το πρόγραμμα δεν μπόρεσε να διαβάσει σωστά τις kWh από το PDF.")
                st.warning(f"Βρέθηκαν: Συνολικές kWh μετρητή: {total_kwh}, Τιμολογημένες kWh: {billed_kwh}")
                
                with st.expander("🛠️ Πατήστε εδώ για να δείτε το κείμενο του PDF (Βοηθάει στον εντοπισμό του λάθους)"):
                    st.text(processed_text)

        except Exception as e:
            st.error(f"Προέκυψε σφάλμα κατά την ανάλυση: {e}")

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
