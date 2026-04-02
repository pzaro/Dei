import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="Φ/Β Κέρδος Net Metering", page_icon="☀️", layout="centered")

st.title("☀️ Υπολογιστής Κέρδους Net Metering")
st.markdown("Ανεβάστε τον εκκαθαριστικό λογαριασμό της ΔΕΗ (σε μορφή PDF) για να δείτε το πραγματικό σας όφελος από το φωτοβολταϊκό σας.")

def parse_dei_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    
    # Διόρθωση OCR
    processed_text = text.replace("Bkwh", "8kWh").replace("B kwh", "8 kWh").replace("awn", "kWh")

    # 1. Σύνολο Μετρητή
    total_kwh = None
    match_total = re.search(r'ΚΑΤΑΝΑΛΩΣΗ\s*\.*:\s*(\d+)|Σύνολο\s*Κατανάλωσης\s*(\d+)', processed_text, re.IGNORECASE)
    if match_total:
        total_kwh = float(match_total.group(1) or match_total.group(2))

    # 2. Χρέωση Ενέργειας
    energy_charge = None
    match_energy = re.search(r'Χρέωση\s*Ενέργειας\s*Κανονική[\s\S]{0,50}?(\d+[.,]\d+)', processed_text, re.IGNORECASE)
    if match_energy:
        energy_charge = float(match_energy.group(1).replace(',', '.'))

    # 3. Τιμολογημένες Μονάδες (Μόνο από την περιοχή της προμήθειας)
    billed_kwh = 0
    supply_section = re.search(r'Αναλυτικά οι χρεώσεις(.*?)Ρυθμιζόμενες Χρεώσεις', processed_text, re.IGNORECASE | re.DOTALL)
    
    if supply_section:
        section_text = supply_section.group(1)
        pattern_billed = r'(\d+)\s*[a-zA-Zα-ωΑ-Ω]*\s*[x×X]\s*(\d+[.,]\d+)'
        matches = re.finditer(pattern_billed, section_text)
        for match in matches:
            billed_kwh += float(match.group(1))
            
    # Δίχτυ Ασφαλείας
    if billed_kwh == 0 and energy_charge is not None and energy_charge > 0:
        billed_kwh = round(energy_charge / 0.135)

    # 4. Συνολικό Ποσό
    total_bill = None
    match_bill = re.search(r'\*(\d+[.,]\d+)\s*€|Συνολικό\s*ποσό\s*πληρωμής.*?(?:€)?\s*(\d+[.,]\d+)', processed_text, re.IGNORECASE)
    if match_bill:
        total_bill = float((match_bill.group(1) or match_bill.group(2)).replace(',', '.'))

    return total_kwh, billed_kwh, energy_charge, total_bill

# --- UI ---
uploaded_file = st.file_uploader("📄 Επιλέξτε το PDF του λογαριασμού σας", type="pdf")

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    
    with st.spinner('Αναλύεται ο λογαριασμός...'):
        try:
            total_kwh, billed_kwh, energy_charge, total_bill = parse_dei_pdf(file_bytes)
            
            if total_kwh and billed_kwh:
                hidden_kwh = total_kwh - billed_kwh
                
                if hidden_kwh <= 0:
                    st.warning("⚠️ Δεν εντοπίστηκε απόκρυφη έκπτωση. Οι χρεωθείσες kWh είναι ίσες ή περισσότερες από τον μετρητή.")
                else:
                    safe_energy_charge = energy_charge if energy_charge is not None else 0.0
                    safe_total_bill = total_bill if total_bill is not None else 0.0
                    
                    if safe_energy_charge > 0 and billed_kwh > 0:
                        avg_rate = safe_energy_charge / billed_kwh
                    else:
                        avg_rate = 0.13
                        
                    energy_saved = hidden_kwh * avg_rate
                    
                    if safe_total_bill > 0 and safe_energy_charge > 0 and safe_total_bill > safe_energy_charge:
                        ratio = (safe_total_bill - safe_energy_charge) / safe_energy_charge
                    else:
                        ratio = 0.18
                        
                    taxes_saved = total_saved - energy_saved if 'total_saved' in locals() else energy_saved * ratio
                    total_saved = energy_saved + taxes_saved

                    st.success(f"🎉 Το συνολικό σας όφελος σε αυτόν τον λογαριασμό είναι **{total_saved:.2f} €**")
                    
                    # Εμφάνιση των 3 βασικών μετρήσεων
                    col1, col2, col3 = st.columns(3)
                    col1.metric(label="Συμψηφισμένες kWh", value=f"{hidden_kwh:.1f}")
                    col2.metric(label="Κέρδος Ενέργειας", value=f"{energy_saved:.2f} €")
                    col3.metric(label="Κέρδος Φόρων/Τελών", value=f"{taxes_saved:.2f} €")
                    
                    st.divider()

                    # --- ΑΝΑΛΥΤΙΚΗ ΕΠΕΞΗΓΗΣΗ ΣΕ ΑΠΛΑ ΕΛΛΗΝΙΚΑ ---
                    st.markdown("### 📖 Πώς ακριβώς προκύπτει αυτό το κέρδος;")
                    
                    st.markdown(f"""
                    **1. Ενέργεια που παράξατε και "γλιτώσατε" (Συμψηφισμένες kWh):** Ο μετρητής σας στο ρολόι κατέγραψε συνολικά **{total_kwh} kWh**, αλλά η ΔΕΗ σας τιμολόγησε μόνο για τις **{billed_kwh} kWh**. 
                    Αυτό σημαίνει ότι το φωτοβολταϊκό σας "απορρόφησε" **{hidden_kwh:.1f} kWh**, τις οποίες χρησιμοποιήσατε εντελώς δωρεάν!
                    
                    **2. Κέρδος από την καθαρή ενέργεια:** Αν πληρώνατε αυτές τις {hidden_kwh:.1f} kWh με τη μέση τιμή ρεύματος αυτού του λογαριασμού (που ήταν περίπου *{avg_rate:.3f} € ανά kWh*), θα σας κόστιζαν **{energy_saved:.2f} €**. Αυτά τα χρήματα έμειναν στην τσέπη σας.
                    
                    **3. Κέρδος από Φόρους και Ρυθμιζόμενες Χρεώσεις:** Επειδή δεν χρεωθήκατε αυτές τις {hidden_kwh:.1f} kWh, αυτόματα γλιτώσατε και τις αναλογικές χρεώσεις που τις συνοδεύουν (Χρήση Δικτύων, ΕΤΜΕΑΡ, ΦΠΑ, κλπ). Αυτό σας έδωσε ένα επιπλέον όφελος **{taxes_saved:.2f} €**.
                    """)
                    
                    st.info(f"💡 **Συμπέρασμα:** Αν δεν είχατε το φωτοβολταϊκό, ο λογαριασμός σας δεν θα ήταν **{safe_total_bill:.2f} €**, αλλά θα έφτανε περίπου τα **{(safe_total_bill + total_saved):.2f} €**!")

                    # Κουμπί για debug δεδομένων
                    with st.expander("🔍 Προβολή πρωτογενών δεδομένων του λογαριασμού"):
                        st.write(f"- **Σύνολο Μετρητή:** {total_kwh} kWh")
                        st.write(f"- **Τιμολογήθηκαν (Χρεώθηκαν):** {billed_kwh} kWh")
                        st.write(f"- **Χρέωση Ενέργειας:** {energy_charge} €")
                        st.write(f"- **Σύνολο Πληρωμής:** {total_bill} €")
                        
            else:
                st.error("❌ Δεν μπορέσαμε να διαβάσουμε την πλήρη κατανάλωση. Βεβαιωθείτε ότι είναι Εκκαθαριστικός.")
        
        except Exception as e:
            st.error(f"Σφάλμα ανάγνωσης: {e}")
