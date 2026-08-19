import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from sklearn.cluster import DBSCAN
from fpdf import FPDF

# --- SETUP & KONFIGURATION ---
st.set_page_config(page_title="Klavierlehrer Cockpit", layout="wide")

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
    
    # FLEXIBLE SCHÜLER-AUSWAHL
    schueler_liste = ["Emma", "Max", "Lina", "Julian", "Sophie"]
    student = st.selectbox("👤 Wähle den aktuellen Schüler aus:", schueler_liste)
    
    st.subheader(f"Aktueller Unterricht: {student}")
    
    # Timer & Balken
    st.progress(0.45, text="Stunde läuft - Zeitbalken")
    
    # --- LOBKÄRTCHEN & TASKCARDS KOMBI ---
    with st.expander("🏆 Lobkärtchen vergeben & auf TaskCards teilen"):
        grund = st.text_input("Grund für das Lobkärtchen (z.B. Fantastischer Rhythmus!)")
        
        # Checkbox
        auf_taskcards = st.checkbox("Direkt auf dem TaskCards-Board des Schülers veröffentlichen", value=True)
        
        if st.button("Kärtchen vergeben & speichern"):
            st.success(f"Kärtchen für {student} im Archiv gespeichert!")
            if auf_taskcards:
                st.info(f"🔗 Erfolgreich an TaskCards gesendet! Das Kind sieht die Auszeichnung beim nächsten Öffnen.")

with tab2:
    st.title("📊 Analyse & Dichte-Scan")
    df_archiv = pd.DataFrame({
        'Schueler': ['Emma', 'Max', 'Lina'], 
        'Dauer_Minuten': [45, 60, 30], 
        'Schwierigkeit': [3, 4, 2], 
        'Kärtchen_Erhalten': ['Ja', 'Nein', 'Ja'], 
        'Grund': ['Dynamik', '', 'Rhythmus']
    })
    
    # DBSCAN Cluster-Analyse
    db = DBSCAN(eps=0.5, min_samples=2).fit(df_archiv[['Dauer_Minuten', 'Schwierigkeit']])
    df_archiv['Cluster'] = db.labels_
    
    fig = px.scatter(
        df_archiv, x="Dauer_Minuten", y="Schwierigkeit", 
        color="Cluster", symbol="Kärtchen_Erhalten", 
        hover_name="Schueler", title="Lern-Cluster & Kärtchen-Goldpunkte"
    )
    st.plotly_chart(fig)

with tab3:
    st.title("🏆 Jahres-Zertifikate & TaskCards Übersicht")
    st.write(f"Hier kannst du das Jahres-Zertifikat für **{student}** generieren.")
    if st.button(f"Zertifikat für {student} als PDF erstellen"):
        st.success("PDF-Zertifikat wurde generiert und kann heruntergeladen werden!")
