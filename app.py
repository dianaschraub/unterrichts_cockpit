
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from sklearn.cluster import DBSCAN
from fpdf import FPDF

# --- SETUP & KONFIGURATION ---
st.set_page_config(page_title="Klavierlehrer Cockpit", layout="wide")

# --- ECHTE KALENDER-ERKENNUNG ---
def get_aktueller_schueler():
    # Hier wird später die echte Google Kalender API Abfrage stattfinden.
    # Aktuell gibt sie None zurück, um das Auswahlmenü zu triggern.
    return None 

# --- CORE FUNKTIONEN ---
def erstelle_zertifikat_pdf(student, df_archiv):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Jahres-Zertifikat fuer {student}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Gelernt im vergangenen Jahr:", ln=True)
    for s in df_archiv[df_archiv['Schueler'] == student]['Stueck'].unique():
        pdf.cell(200, 10, txt=f"- {s}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Besondere Erfolge (Lobkaertchen):", ln=True)
    lob = df_archiv[(df_archiv['Schueler'] == student) & (df_archiv['Kärtchen_Erhalten'] == 'Ja')]
    for _, row in lob.iterrows():
        pdf.cell(200, 10, txt=f"* {row['Grund']}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- UI LOGIK ---
tab1, tab2, tab3 = st.tabs(["🎹 Cockpit", "📊 Analyse & Scan", "🏆 Zertifikate & TaskCards"])

with tab1:
    st.title("🎹 Klavierlehrer Cockpit")
    
    # Automatische Schüler-Erkennung
    gefundener_schueler = get_aktueller_schueler()
    
    if gefundener_schueler:
        student = gefundener_schueler
        st.success(f"👤 Aktueller Schüler aus Kalender erkannt: {student}")
    else:
        # Fallback: Dropdown
        schueler_liste = ["Emma", "Max", "Lina", "Julian", "Sophie"]
        student = st.selectbox("👤 Kein Kalender-Termin gefunden. Wähle manuell:", schueler_liste)
    
    st.subheader(f"Aktueller Unterricht: {student}")
    
    # Timer & Balken
    st.progress(0.45, text="Stunde läuft - Zeitbalken")
    
    # --- LOBKÄRTCHEN ---
    with st.expander("🏆 Lobkärtchen vergeben & auf TaskCards teilen"):
        grund = st.text_input("Grund für das Lobkärtchen")
        auf_taskcards = st.checkbox("Direkt auf TaskCards veröffentlichen", value=True)
        if st.button("Kärtchen speichern"):
            st.success(f"Kärtchen für {student} gespeichert!")

with tab2:
    st.title("📊 Analyse & Dichte-Scan")
    df_archiv = pd.DataFrame({
        'Schueler': ['Emma', 'Max', 'Lina'], 
        'Dauer_Minuten': [45, 60, 30], 
        'Schwierigkeit': [3, 4, 2], 
        'Kärtchen_Erhalten': ['Ja', 'Nein', 'Ja'], 
        'Grund': ['Dynamik', '', 'Rhythmus']
    })
    
    db = DBSCAN(eps=0.5, min_samples=2).fit(df_archiv[['Dauer_Minuten', 'Schwierigkeit']])
    df_archiv['Cluster'] = db.labels_
    
    fig = px.scatter(df_archiv, x="Dauer_Minuten", y="Schwierigkeit", color="Cluster", symbol="Kärtchen_Erhalten", hover_name="Schueler")
    st.plotly_chart(fig)

with tab3:
    st.title("🏆 Jahres-Zertifikate")
    if st.button(f"Zertifikat für {student} erstellen"):
        st.success("PDF wurde generiert!")
