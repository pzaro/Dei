import streamlit as st
import fitz  # PyMuPDF
import re

# Ρύθμιση της σελίδας
st.set_page_config(page_title="Φ/Β Κέρδος Net Metering", page_icon="☀️")

st.title("☀️ Υπολογιστής Κέρδους Net Metering")
st.markdown("Ανεβάστε τον εκκαθαριστικό λογαριασμό της ΔΕΗ για να δείτε το πραγματικό σας όφελος.")

def parse_dei_pdf(file_bytes):
    # Άνοιγμα του PDF από τα bytes που ανέβασε ο χρήστης
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    
    # Διόρθωση συχνών λαθών OCR
    processed_text = text.replace("Bkwh", "8kWh").replace("B kwh", "8 kWh")

    # 1. Σύνολο Μετρητή
    total_kwh = None
    match_total = re.search(r'ΚΑΤΑΝΑΛΩΣΗ\s*\.*:\s*(\d+)|Σύνολο\s*Κατανάλωσης\s*(\d+)', processed_text, re.IGNORECASE)
    if match_total:
        total_kwh = float(match_total.group(1) or match_total.group(2))

    # 2. Τιμολογημένες Μονάδες (Άθροισμα κλιμακίων)
    billed_kwh = 0
    pattern_billed = r'(\d+)\s*[a-zA-Zα-ωΑ-Ω]*\s*[x×X]\s*(\d+[.,]\d+)'
    matches = re.finditer(pattern_billed, processed_text)
    for match in matches:
        val = float(match.group(1))
        if val < 5000: billed_kwh += val

    # 3. Χρέωση Ενέργειας
    energy_charge = None
    match_energy = re.search(r'Χρέωση\s*Ενέργειας\s*Κανονική\s*(\d+[.,]\d+)', processed_text, re.IGNORECASE)
    if match_energy:
        energy_charge = float(match_energy.group(1).replace(',', '.'))

    # 4. Συνολικό Ποσό
    total_bill = None
    match_bill = re.search(r'\*(\d+[.,]\d+)\s*€|Συνολικό\s*ποσό\s*πληρωμής.*?(?:€)?\s*(\d+[.,]\d+)', processed_text, re.IGNORECASE)
    if match_bill:
        total_bill = float((match_bill.group(1) or match_bill.group(2)).replace(',', '.'))

    return total_kwh, billed_kwh, energy_charge, total_bill

# UI για Upload
uploaded_file = st.file_uploader("Επιλέξτε το PDF του λογαριασμού σας", type="pdf")

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    with st.spinner('Αναλύεται ο λογαριασμός...'):
        total_kwh, billed_kwh, energy_charge, total_bill = parse_dei_pdf(file_bytes)

    if total_kwh and billed_kwh:
        hidden_kwh = total_kwh - billed_kwh
        avg_rate = energy_charge / billed_kwh if billed_kwh > 0 else 0.13
        energy_saved = hidden_kwh * avg_rate
        
        # Υπολογισμός αναλογίας φόρων (τυπικά ~18% αν δεν βρεθεί)
        ratio = (total_bill - energy_charge) / energy_charge if (total_bill and energy_charge) else 0.18
        total_saved = energy_saved * (1 + ratio)

        # Εμφάνιση Αποτελεσμάτων
        st.success(f"Το συνολικό σας όφελος είναι {total_saved:.2f} €")
        
        col1, col2 = st.columns(2)
        col1.metric("Συμψηφισμένες kWh", f"{hidden_kwh} kWh")
        col2.metric("Κέρδος Ενέργειας", f"{energy_saved:.2f} €")
        
        st.info(f"Χωρίς το φωτοβολταϊκό, ο λογαριασμός θα ήταν περίπου **{(total_bill + total_saved):.2f} €** αντί για **{total_bill:.2f} €**.")
    else:
        st.error("Δεν μπορέσαμε να διαβάσουμε όλα τα δεδομένα. Σιγουρευτείτε ότι είναι εκκαθαριστικός λογαριασμός.")