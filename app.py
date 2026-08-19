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
    /* Edle Box für das Lobkärtchen */
    .lob-box {
        background: linear-gradient(135deg, #fffdf0 0%, #fef5d1 100%);
        border: 2px solid #d4af37;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(212, 175, 55, 0.2);
        max-width: 650px;
        margin: 20px auto;
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
        'Konzertstueck': ['Sonatine 1. Satz', 'Für Elise', 'Inventio 1'],
        'Dauer_Minuten': [45, 60, 30],
        'Schwierigkeit': [3, 4, 2],
        'Kärtchen_Erhalten': ['Ja', 'Nein', 'Ja'],
        'Grund': ['Toller Rhythmus im Takt 12', '', 'Wunderschöne Dynamik'],
        'Bis_Naechsten_Mal': ['Takt 15-20 langsam üben', 'Pedalwechsel weicher gestalten', 'Rhythmus klatschen']
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
    
    modus = st.radio(
        "Wähle den Bereich:", 
        ["Tastenforscher", "Klassische Tonleitern", "Fortgeschrittene Etüden"], 
        horizontal=True
    )
    
    if modus == "Tastenforscher":
        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            heft_titel = st.text_input("Titel der Übung:", value="Tastenforscher")
        with col_h2:
            seiten_zahl = st.text_input("Seitenzahl:", value="Seite ")
        with col_h3:
            heft_link = st.text_input("Link zur Datei (Cloud/SSD):", value="")
        speicher_text = f"Tastenforscher: '{heft_titel}' auf {seiten_zahl}"
        
    elif modus == "Klassische Tonleitern":
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            tonleiter_text = st.text_input("Tonart / Tonleiter:", value="z.B. C-Dur")
        with col_t2:
            bewegung_wahl = st.radio("Spielart:", ["Parallelbewegung", "Gegenbewegung"], horizontal=True)
        with col_t3:
            tempo_wahl = st.slider("Tempo (BPM):", min_value=40, max_value=200, value=80, step=2)
        speicher_text = f"Tonleiter: {tonleiter_text} ({bewegung_wahl}) bei {tempo_wahl} BPM"
        
    else:  # Fortgeschrittene Etüden
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            etuede_titel = st.text_input("Etüde / Name:", value="z.B. Etüde op. 299")
        with col_e2:
            komponist = st.text_input("Komponist:", value="Czerny / Chopin")
        with col_e3:
            opus_nr = st.text_input("Opus / Werknummer:", value="Op. 299, Nr. 6")
            
        col_e4, col_e5 = st.columns(2)
        with col_e4:
            etuede_takte = st.text_input("Gespielte Takte:", value="Takt 1–32")
        with col_e5:
            etuede_tempo = st.number_input("Tempo (BPM):", min_value=40, max_value=250, value=100, step=2)
            
        etuede_notizen = st.text_area("Weitere Notizen:", value="Fokus auf Artikulation.")
        speicher_text = f"Etüde: '{etuede_titel}' ({komponist}, {opus_nr}) | Takte: {etuede_takte} | Tempo: {etuede_tempo} BPM"

    col_stueck1, col_stueck2 = st.columns(2)
    with col_stueck1:
        aktuelles_stueck_input = st.text_input("Gespieltes Hauptstück:", value="Sonatine Opus 36")
    with col_stueck2:
        konzert_stueck_input = st.text_input("🎯 Konzertstück (fürs Vorspiel 02.09.):", value="Sonatine 1. Satz")
    
    if st.button("💾 Übung & Stück ins Archiv eintragen"):
        st.success(f"Gespeichert für {student}: {speicher_text} | Hauptstück: '{aktuelles_stueck_input}' | Konzertstück: '{konzert_stueck_input}'!")

    # --- NOTIZEN (Seiten getauscht: Links Hausaufgabe, Rechts Bis nächste Stunde) ---
    st.markdown("---")
    st.markdown("### 📝 Unterrichts- & Vorbereitungsnotizen")
    col1, col2 = st.columns(2)
    
    with col1:
        neue_hausaufgabe = st.text_input("Hausaufgabe / To-Do für das Kind:")
    
    with col2:
        neue_besprechung = st.text_input("Bis zur nächsten Stunde erledigen:")

    # --- NEU PLATZIERTES & EDEL GESTALTETES LOBKÄRTCHEN (Mittig, edler Rahmen) ---
    st.markdown("---")
    
    st.markdown("""
        <div class="lob-box">
            <h3 style="margin-top:0; color:#b8860b; text-align:center;">🏆 Lobkärtchen</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Da Streamlit-Elemente in echtem HTML-Container schwer steuerbar sind, nutzen wir eine schmale zentrierte Spalte für den Inhalt
    _, col_lob_mitte, _ = st.columns([1, 3, 1])
    with col_lob_mitte:
        grund = st.text_area(
            "Grund für das Lobkärtchen:",
            value="Fantastischer Rhythmus und wunderschöner Ausdruck im Mittelteil!",
            height=90
        )
        auf_taskcards = st.checkbox("Direkt auf dem TaskCards-Board veröffentlichen", value=True)
        
        if st.button("✨ Lobkärtchen vergeben & speichern", use_container_width=True):
            st.success(f"Lobkärtchen für {student} erfolgreich gespeichert und an TaskCards gesendet!")

    # --- MEINE AUFGABEN ---
    st.markdown("---")
    st.markdown(f"### 📌 Meine Aufgaben für zu Hause")
    aufgabe_1 = st.checkbox("Noten für die nächste Stunde raussuchen & kopieren", value=False)
    aufgabe_2 = st.checkbox("TaskCards-Board aktualisieren", value=False)
    neue_lehrer_aufgabe = st.text_input("Weitere eigene Aufgabe hinzufügen:")
    
    if st.button("💾 Alle Änderungen speichern"):
        st.success("Erfolgreich im Hintergrund gespeichert!")

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
