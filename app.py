import streamlit as st
import fitz  # PyMuPDF
import re

# Ρύθμιση Σελίδας
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

    # 2. Τιμολογημένες Μονάδες ΚΑΙ Ακριβής Τιμή (Από τις παρενθέσεις)
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
        match_energy = re.search(r'Χρέωση\s*Ενέργειας\s*Κανονική[\s\S]{0,50}?(\d+[.,]\d+)', processed_text, re.IGNORECASE)
        if match_energy:
            energy_charge = float(match_energy.group(1).replace(',', '.'))
            billed_kwh = round(energy_charge / 0.135)
            exact_avg_rate = energy_charge / billed_kwh if billed_kwh > 0 else 0.139

    # 4. Συνολικό Ποσό Λογαριασμού
    total_bill = None
    match_bill = re.search(r'\*(\d+[.,]\d+)\s*€|Συνολικό\s*ποσό\s*πληρωμής.*?(?:€)?\s*(\d+[.,]\d+)', processed_text, re.IGNORECASE)
    if match_bill:
        total_bill = float((match_bill.group(1) or match_bill.group(2)).replace(',', '.'))

    return total_kwh, billed_kwh, energy_charge, total_bill, exact_avg_rate

# --- UI ---
uploaded_file = st.file_uploader("📄 Επιλέξτε το PDF του λογαριασμού σας", type="pdf")

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    
    with st.spinner('Αναλύεται ο λογαριασμός...'):
        try:
            total_kwh, billed_kwh, energy_charge, total_bill, exact_avg_rate = parse_dei_pdf(file_bytes)
            
            if total_kwh and billed_kwh:
                hidden_kwh = total_kwh - billed_kwh
                
                if hidden_kwh <= 0:
                    st.warning("⚠️ Δεν εντοπίστηκε απόκρυφη έκπτωση. Οι χρεωθείσες kWh είναι ίσες ή περισσότερες από τον μετρητή.")
                else:
                    safe_energy_charge = energy_charge if energy_charge is not None else 0.0
                    safe_total_bill = total_bill if total_bill is not None else 0.0
                    
                    avg_rate_no_vat = exact_avg_rate if exact_avg_rate is not None else 0.139
                    
                    # Υπολογισμός Κέρδους Ενέργειας
                    energy_saved = hidden_kwh * avg_rate_no_vat
                    
                    # Υπολογισμός Κέρδους από Λοιπές Χρεώσεις
                    if safe_total_bill > 0 and safe_energy_charge > 0 and safe_total_bill > safe_energy_charge:
                        ratio = (safe_total_bill - safe_energy_charge) / safe_energy_charge
                    else:
                        ratio = 0.18 
                        
                    taxes_saved = energy_saved * ratio
                    total_saved = energy_saved + taxes_saved

                    # --- ΔΗΜΙΟΥΡΓΙΑ ΕΙΚΟΝΙΚΩΝ (ΧΩΡΙΣ Φ/Β) ΠΟΣΩΝ ---
                    hypo_energy_charge = safe_energy_charge + energy_saved
                    actual_other_charges = safe_total_bill - safe_energy_charge
                    hypo_other_charges = actual_other_charges + taxes_saved
                    hypo_total_bill = safe_total_bill + total_saved

                    # --- ΑΠΟΤΕΛΕΣΜΑΤΑ (ΣΥΓΚΡΙΤΙΚΟΣ ΠΙΝΑΚΑΣ) ---
                    st.success(f"🎉 Το συνολικό σας καθαρό όφελος είναι **{total_saved:.2f} €**")
                    
                    st.markdown("### 📊 Σύγκριση Τιμολόγησης")
                    st.markdown("*Με πράσινο χρώμα βλέπετε τι τελικά πληρώσατε, ενώ με κόκκινο στην παρένθεση τι θα πληρώνατε χωρίς το Φωτοβολταϊκό.*")

                    # HTML/CSS για την εμφάνιση με τα χρώματα που ζήτησες
                    comparison_html = f"""
                    <div style="background-color: #1e1e1e; padding: 20px; border-radius: 15px; border: 1px solid #444; margin-bottom: 25px;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 1.1em;">
                            <tr style="border-bottom: 1px solid #444;">
                                <td style="padding: 10px 0;">⚡ <b>Κατανάλωση (kWh)</b></td>
                                <td style="text-align: right; padding: 10px 0;">
                                    <span style="color: #4CAF50; font-weight: bold; font-size: 1.2em;">{billed_kwh:.1f}</span> 
                                    <span style="color: #F44336; margin-left: 8px;">({total_kwh:.1f})</span>
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
                                <td style="padding: 10px 0;">🛡️ <b>Ρυθμιζόμενες, Φόροι & Λοιπά</b></td>
                                <td style="text-align: right; padding: 10px 0;">
                                    <span style="color: #4CAF50; font-weight: bold; font-size: 1.2em;">{actual_other_charges:.2f} €</span> 
                                    <span style="color: #F44336; margin-left: 8px;">({hypo_other_charges:.2f} €)</span>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 15px 0; font-size: 1.2em;">💰 <b>ΣΥΝΟΛΟ ΛΟΓΑΡΙΑΣΜΟΥ</b></td>
                                <td style="text-align: right; padding: 15px 0;">
                                    <span style="color: #4CAF50; font-weight: bold; font-size: 1.4em;">{safe_total_bill:.2f} €</span> 
                                    <span style="color: #F44336; font-size: 1.2em; margin-left: 8px;">({hypo_total_bill:.2f} €)</span>
                                </td>
                            </tr>
                        </table>
                    </div>
                    """
                    st.markdown(comparison_html, unsafe_allow_html=True)
                    
                    # --- REPORT ΚΕΡΔΟΥΣ ---
                    st.markdown("### 📖 Αναλυτικό Report Κέρδους")
                    
                    st.markdown(f"""
                    **1. Ενέργεια που παράξατε και "γλιτώσατε":** Ο μετρητής κατέγραψε συνολικά **{total_kwh} kWh**, αλλά η ΔΕΗ σας τιμολόγησε μόνο για τις **{billed_kwh} kWh**. 
                    Άρα το φωτοβολταϊκό κάλυψε **{hidden_kwh:.1f} kWh**.
                    
                    **2. Ακριβής Τιμή Ρεύματος:** Σύμφωνα με την ανάλυση του λογαριασμού σας, η καθαρή τιμή ενέργειας είναι ακριβώς **{avg_rate_no_vat:.5f} €/kWh**. Μαζί με το ΦΠΑ διαμορφώνεται στα **{(avg_rate_no_vat * 1.06):.5f} €/kWh**.
                    
                    **3. Οικονομικό Κέρδος:** Αν αγοράζατε αυτές τις {hidden_kwh:.1f} kWh, θα πληρώνατε **{energy_saved:.2f} €** καθαρά για το ρεύμα. Επειδή όμως γλιτώσατε το ρεύμα, γλιτώσατε αυτόματα τις **Ρυθμιζόμενες χρεώσεις** (ΕΤΜΕΑΡ, Δίκτυα κλπ) και τον **ΦΠΑ** που του αναλογούν, κερδίζοντας επιπλέον **{taxes_saved:.2f} €**!
                    """)
                    
                    with st.expander("🔍 Προβολή πρωτογενών δεδομένων του λογαριασμού (Debug)"):
                        st.write(f"- **Σύνολο Μετρητή:** {total_kwh} kWh")
                        st.write(f"- **Τιμολογήθηκαν (Χρεώθηκαν):** {billed_kwh} kWh")
                        st.write(f"- **Ακριβής Τιμή Καθαρής Ενέργειας:** {avg_rate_no_vat:.5f} €/kWh")
                        st.write(f"- **Καθαρή Αξία Ενέργειας:** {safe_energy_charge:.2f} €")
                        st.write(f"- **Σύνολο Πληρωμής:** {safe_total_bill:.2f} €")
                        
            else:
                st.error("❌ Δεν μπορέσαμε να διαβάσουμε την πλήρη κατανάλωση. Βεβαιωθείτε ότι είναι Εκκαθαριστικός.")
        
        except Exception as e:
            st.error(f"Σφάλμα ανάγνωσης: {e}")
