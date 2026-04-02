import streamlit as st
import fitz  # PyMuPDF
import re

# Ρύθμιση της σελίδας (Τίτλος και εικονίδιο στον browser)
st.set_page_config(page_title="Φ/Β Κέρδος Net Metering", page_icon="☀️", layout="centered")

st.title("☀️ Υπολογιστής Κέρδους Net Metering")
st.markdown("Ανεβάστε τον εκκαθαριστικό λογαριασμό της ΔΕΗ (σε μορφή PDF) για να δείτε το πραγματικό σας όφελος από το φωτοβολταϊκό σας.")

def parse_dei_pdf(file_bytes):
    """Διαβάζει το PDF της ΔΕΗ και εξάγει τα 4 βασικά νούμερα."""
    # Άνοιγμα του PDF από τα bytes
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    
    # Διόρθωση συχνών λαθών OCR (το PDF συχνά διαβάζει το 8 ως B)
    processed_text = text.replace("Bkwh", "8kWh").replace("B kwh", "8 kWh")

    # 1. Σύνολο Μετρητή (Συνολική κατανάλωση)
    total_kwh = None
    match_total = re.search(r'ΚΑΤΑΝΑΛΩΣΗ\s*\.*:\s*(\d+)|Σύνολο\s*Κατανάλωσης\s*(\d+)', processed_text, re.IGNORECASE)
    if match_total:
        total_kwh = float(match_total.group(1) or match_total.group(2))

    # 2. Τιμολογημένες Μονάδες (Πόσες kWh πραγματικά χρεώθηκαν)
    billed_kwh = 0
    pattern_billed = r'(\d+)\s*[a-zA-Zα-ωΑ-Ω]*\s*[x×X]\s*(\d+[.,]\d+)'
    matches = re.finditer(pattern_billed, processed_text)
    for match in matches:
        val = float(match.group(1))
        if val < 5000:  # Αποφυγή παρερμηνείας άλλων αριθμών (π.χ. συντελεστές ΤΑΠ)
            billed_kwh += val

    # 3. Χρέωση Ενέργειας (Ελαστικό regex για τυχόν αλλαγές γραμμής)
    energy_charge = None
    match_energy = re.search(r'Χρέωση\s*Ενέργειας\s*Κανονική[\s\S]{0,50}?(\d+[.,]\d+)', processed_text, re.IGNORECASE)
    if match_energy:
        energy_charge = float(match_energy.group(1).replace(',', '.'))

    # 4. Συνολικό Ποσό Λογαριασμού
    total_bill = None
    match_bill = re.search(r'\*(\d+[.,]\d+)\s*€|Συνολικό\s*ποσό\s*πληρωμής.*?(?:€)?\s*(\d+[.,]\d+)', processed_text, re.IGNORECASE)
    if match_bill:
        total_bill = float((match_bill.group(1) or match_bill.group(2)).replace(',', '.'))

    return total_kwh, billed_kwh, energy_charge, total_bill

# --- UI & Λογική Εφαρμογής (Streamlit) ---
uploaded_file = st.file_uploader("📄 Επιλέξτε το PDF του λογαριασμού σας", type="pdf")

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    
    with st.spinner('Αναλύεται ο λογαριασμός...'):
        try:
            total_kwh, billed_kwh, energy_charge, total_bill = parse_dei_pdf(file_bytes)
            
            # Έλεγχος αν βρέθηκαν τα βασικά δεδομένα κατανάλωσης
            if total_kwh and billed_kwh:
                hidden_kwh = total_kwh - billed_kwh
                
                if hidden_kwh <= 0:
                    st.warning("⚠️ Δεν εντοπίστηκε απόκρυφη έκπτωση. Οι χρεωθείσες kWh είναι ίσες ή περισσότερες από τον μετρητή. Πιθανώς το Φ/Β δεν είχε παραγωγή.")
                else:
                    # --- ΑΣΦΑΛΕΙΣ ΥΠΟΛΟΓΙΣΜΟΙ (Πρόληψη TypeError) ---
                    # Μετατρέπουμε τα None σε 0.0 αν δεν βρέθηκαν στο PDF
                    safe_energy_charge = energy_charge if energy_charge is not None else 0.0
                    safe_total_bill = total_bill if total_bill is not None else 0.0
                    
                    # Υπολογισμός μέσης τιμής ρεύματος
                    if safe_energy_charge > 0 and billed_kwh > 0:
                        avg_rate = safe_energy_charge / billed_kwh
                    else:
                        avg_rate = 0.13  # Προεπιλεγμένη τιμή ασφαλείας αν λείπει η χρέωση
                        
                    energy_saved = hidden_kwh * avg_rate
                    
                    # Υπολογισμός αναλογίας ρυθμιζόμενων & φόρων
                    if safe_total_bill > 0 and safe_energy_charge > 0 and safe_total_bill > safe_energy_charge:
                        ratio = (safe_total_bill - safe_energy_charge) / safe_energy_charge
                    else:
                        ratio = 0.18  # Προεπιλεγμένη αναλογία ~18% αν λείπουν δεδομένα
                        
                    total_saved = energy_saved * (1 + ratio)

                    # --- ΕΜΦΑΝΙΣΗ ΑΠΟΤΕΛΕΣΜΑΤΩΝ ---
                    st.success(f"🎉 Το συνολικό σας όφελος σε αυτόν τον λογαριασμό είναι **{total_saved:.2f} €**")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric(label="Συμψηφισμένες kWh", value=f"{hidden_kwh:.1f}")
                    col2.metric(label="Κέρδος Ενέργειας", value=f"{energy_saved:.2f} €")
                    col3.metric(label="Κέρδος Φόρων/Τελών", value=f"{(total_saved - energy_saved):.2f} €")
                    
                    st.divider()
                    
                    st.info(f"💡 **Χωρίς το φωτοβολταϊκό σύστημα**, ο τελικός σας λογαριασμός θα ήταν περίπου **{(safe_total_bill + total_saved):.2f} €** αντί για **{safe_total_bill:.2f} €** που καλείστε να πληρώσετε τώρα.")
                    
                    # Debugging / Διαφάνεια (Βοηθάει να δεις αν το πρόγραμμα διάβασε σωστά το PDF)
                    with st.expander("🔍 Προβολή δεδομένων που διαβάστηκαν από το PDF"):
                        st.write(f"- **Σύνολο Μετρητή:** {total_kwh} kWh")
                        st.write(f"- **Τιμολογημένες (Χρεώθηκαν):** {billed_kwh} kWh")
                        st.write(f"- **Χρέωση Ενέργειας:** {energy_charge} €")
                        st.write(f"- **Συνολικό Ποσό Λογαριασμού:** {total_bill} €")
                        
            else:
                st.error("❌ Δεν μπορέσαμε να διαβάσουμε την πλήρη κατανάλωση. Σιγουρευτείτε ότι ανεβάσατε Εκκαθαριστικό λογαριασμό και όχι Έναντι.")
        
        except Exception as e:
            st.error(f"Προέκυψε ένα απροσδόκητο σφάλμα κατά την ανάγνωση του αρχείου: {e}")
