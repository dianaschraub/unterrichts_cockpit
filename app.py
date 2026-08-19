

    

import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from sklearn.cluster import DBSCAN
from fpdf import FPDF
import urllib.parse

# --- SETUP & DESIGN-KONFIGURATION ---
st.set_page_config(page_title="Klavierlehrer Cockpit", layout="wide", page_icon="🎹")

st.markdown("""
    <style>
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- KONZERT-DATUM ---
KONZERT_DATUM = datetime.date(2026, 9, 2)

def berechne_konzert_countdown():
    heute = datetime.date.today()
    delta = KONZERT_DATUM - heute
    tage = delta.days
    if tage > 0:
        wochen = tage // 7
        rest_tage = tage % 7
        return f"Noch **{wochen} Wochen und {rest_tage} Tage** bis zum Klassenvorspiel!"
    elif tage == 0:
        return "🎉 Heute ist das Klassenvorspiel!"
    else:
        return "Das Klassenvorspiel in diesem Jahr ist bereits vorbei."

# --- DATEN-LOGIK ---
def lade_archiv_aus_sheet():
    daten = {
        'Schueler': ['Emma', 'Max', 'Lina'],
        'Stueck': ['Sonatine Opus 36', 'Für Elise', 'Inventio 1'],
        'Dauer_Minuten': [45, 60, 30],
        'Schwierigkeit': [3, 4, 2],
        'Kärtchen_Erhalten': ['Ja', 'Nein', 'Ja'],
        'Grund': ['Toller Rhythmus im Takt 12', '', 'Wunderschöne Dynamik'],
        'To_Do_Zuhause': ['Takt 15-20 langsam üben', 'Pedalwechsel weicher gestalten', 'Rhythmus klatschen'],
        'Besprechung_Nächste_Stunde': ['Noten im Bassschlüssel wiederholen', 'Handhaltung prüfen', 'Dynamik im Mittelteil']
    }
    return pd.DataFrame(daten)

def get_aktueller_schueler_aus_kalender():
    return None

# --- ZERTIFIKAT FUNKTION ---
def erstelle_zertifikat_pdf(student, df_archiv):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(200, 10, txt=f"Jahres-Zertifikat fuer {student}", ln=True, align='C')
    
    aktuelles_jahr = datetime.datetime.now().year
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"Du hast im Jahr {aktuelles_jahr} folgende Stuecke gelernt:", ln=True)
    
    pdf.set_font("Arial", size=12)
    stuecke = df_archiv[df_archiv['Schueler'] == student]['Stueck'].unique()
    for s in stuecke:
        pdf.cell(200, 10, txt=f"- {s}", ln=True)
        
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Besondere Erfolge - dafuer habe ich ein Lobkaertchen erhalten:", ln=True)
    pdf.set_font("Arial", size=12)
    
    lob = df_archiv[(df_archiv['Schueler'] == student) & (df_archiv['Kärtchen_Erhalten'] == 'Ja')]
    for _, row in lob.iterrows():
        pdf.cell(200, 10, txt=f"* {row['Grund']}", ln=True)
        
    return pdf.output(dest='S').encode('latin-1')

df_archiv = lade_archiv_aus_sheet()

# --- UI NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["🎹 Live-Cockpit", "📊 Analyse & Fortschritt", "🏆 Zertifikate & TaskCards"])

with tab1:
    st.markdown("## 🎹 Klavierlehrer Cockpit")
    
    st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin:0; color:#31333F;">🎯 Countdown zum Klassenvorspiel (02.09.2026)</h4>
            <p style="margin:5px 0 0 0; font-size:18px; font-weight:bold; color:#ff4b4b;">{berechne_konzert_countdown()}</p>
        </div>
    """, unsafe_allow_html=True)
    
    erkennter_schueler = get_aktueller_schueler_aus_kalender()
    
    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        if erkennter_schueler:
            student = erkennter_schueler
            st.success(f"👤 Automatisch aus Kalender erkannt: **{student}**")
        else:
            schueler_liste = df_archiv['Schueler'].unique().tolist()
            student = st.selectbox("👤 Aktueller Schüler:", schueler_liste)
    
    with col_sel2:
        st.markdown(f"**Status:** Aktive Stunde")
    
    st.markdown(f"### Unterricht mit: {student}")
    st.progress(0.45, text="Stunde läuft - Zeitbalken")
    
    # --- ÜBUNGS- & ETIÜDEN-BEREICH ---
    st.markdown("---")
    st.markdown("### 🎹 Übungs- & Technik-Auswahl")
    
    modus = st.radio("Wähle den Bereich:", ["Klassische Tonleitern", "Heft-Übungen (z.B. Tastenforscher)", "Fortgeschrittene Etüden"], horizontal=True)
    
    if modus == "Klassische Tonleitern":
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            tonleiter_wahl = st.selectbox("Tonart / Tonleiter:", ["C-Dur", "G-Dur", "D-Dur", "A-Dur", "E-Dur", "F-Dur", "B-Dur", "Es-Dur", "A-Moll", "E-Moll", "D-Moll", "G-Moll"])
        with col_t2:
            bewegung_wahl = st.radio("Spielart:", ["Parallelbewegung", "Gegenbewegung"], horizontal=True)
        with col_t3:
            tempo_wahl = st.slider("Tempo (BPM):", min_value=40, max_value=200, value=80, step=2)
        speicher_text = f"Tonleiter: {tonleiter_wahl} ({bewegung_wahl}) bei {tempo_wahl} BPM"
        
    elif modus == "Heft-Übungen (z.B. Tastenforscher)":
        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            heft_titel = st.text_input("Titel der Übung / Heft:", value="Tastenforscher")
        with col_h2:
            seiten_zahl = st.text_input("Seitenzahl:", value="Seite ")
        with col_h3:
            heft_link = st.text_input("Link zur Datei (Cloud/SSD):", value="")
        speicher_text = f"Heft: '{heft_titel}' auf {seiten_zahl}"
        
    else:  # Fortgeschrittene Etüden
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            etuede_titel = st.text_input("Etüde / Name:", value="z.B. Etüde op. 299")
        with col_e2:
            komponist = st.text_input("Komponist:", value="Czerny / Chopin / Burgmüller")
        with col_e3:
            opus_nr = st.text_input("Opus / Werknummer:", value="Op. 299, Nr. 6")
            
        col_e4, col_e5 = st.columns(2)
        with col_e4:
            etuede_takte = st.text_input("Gespielte Takte:", value="Takt 1–32")
        with col_e5:
            etuede_tempo = st.number_input("Tempo (BPM):", min_value=40, max_value=250, value=100, step=2)
            
        etuede_notizen = st.text_area("Weitere Notizen zur Etüde:", value="Fokus auf gleichmäßige Sechzehntel und Artikulation in der linken Hand.")
        speicher_text = f"Etüde: '{etuede_titel}' ({komponist}, {opus_nr}) | Takte: {etuede_takte} | Tempo: {etuede_tempo} BPM"

    aktuelles_stueck_input = st.text_input("Gespieltes Hauptstück:", value="Sonatine Opus 36")
    
    if st.button("💾 Übung & Stück ins Archiv eintragen"):
        st.success(f"Gespeichert für {student}: {speicher_text} + Hauptstück '{aktuelles_stueck_input}'!")

    # Notizen
    st.markdown("---")
    st.markdown("### 📝 Unterrichts- & Vorbereitungsnotizen")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Nächste Stunde besprechen:**\n* Noten im Bassschlüssel wiederholen\n* Handhaltung prüfen")
        neue_besprechung = st.text_input("Neuen Punkt für nächste Stunde:")
    
    with col2:
        st.warning(f"**Hausaufgabe für das Kind:**\n* Takt 15-20 langsam üben")
        neue_hausaufgabe = st.text_input("Neue Hausaufgabe eintragen:")

    st.markdown("---")
    st.markdown(f"### 📌 Meine Aufgaben für zu Hause")
    aufgabe_1 = st.checkbox("Noten für die nächste Stunde raussuchen & kopieren", value=False)
    aufgabe_2 = st.checkbox("TaskCards-Board aktualisieren", value=False)
    neue_lehrer_aufgabe = st.text_input("Weitere eigene Aufgabe hinzufügen:")
    
    if st.button("💾 Alle Änderungen speichern"):
        st.success("Erfolgreich im Hintergrund gespeichert!")
    
    with st.expander("🏆 Lobkärtchen vergeben & auf TaskCards teilen"):
        grund = st.text_input("Grund für das Lobkärtchen (z.B. Fantastischer Rhythmus!)")
        auf_taskcards = st.checkbox("Direkt auf dem TaskCards-Board des Schülers veröffentlichen", value=True)
        
        if st.button("✨ Kärtchen vergeben & ins Sheet schreiben"):
            st.success(f"Kärtchen für {student} gespeichert und an TaskCards gesendet!")

with tab2:
    st.markdown("## 📊 Analyse & Fortschritt")
    st.markdown(f"Verfolge den Fortschritt im Jahr 2026 für **{student}**.")
    
    verlauf_daten = pd.DataFrame({
        'Datum': ['2026-01-10', '2026-03-15', '2026-05-05', '2026-07-20', '2026-08-18'],
        'Tempo': [60, 72, 90, 110, 128],
        'Tonart': ['C-Dur'] * 5
    })
    
    st.subheader(f"Tempo-Entwicklung: {student}")
    fig = px.line(verlauf_daten, x="Datum", y="Tempo", markers=True, title="Verlauf im Jahr")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### Gesamtes Archiv")
    st.dataframe(df_archiv, use_container_width=True)

with tab3:
    st.markdown("## 🏆 Jahres-Zertifikate & TaskCards")
    st.markdown(f"Generiere hier das offizielle, persönliche Jahres-Zertifikat für **{student}**.")
    
    if st.button("📄 PDF-Zertifikat jetzt generieren"):
        pdf_daten = erstelle_zertifikat_pdf(student, df_archiv)
        
        st.download_button(
            label="📥 PDF-Zertifikat herunterladen",
            data=pdf_daten,
            file_name=f"Zertifikat_{student}_{datetime.datetime.now().year}.pdf",
            mime="application/pdf"
        )
        
        aktuelles_jahr = datetime.datetime.now().year
        whatsapp_text = f"Hallo! Hier ist das offizielle Jahres-Zertifikat {aktuelles_jahr} für {student} von der Klavierstunde. 🎹✨"
        encoded_text = urllib.parse.quote(whatsapp_text)
        whatsapp_url = f"https://wa.me/?text={encoded_text}"
        
        st.markdown(f'<br><a href="{whatsapp_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; font-weight:bold; cursor:pointer; font-size:16px;">💬 Per WhatsApp an Eltern senden</button></a>', unsafe_allow_html=True)
        
        st.success("Zertifikat steht zum Download und Versand bereit!")
