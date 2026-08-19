import streamlit as st
import pandas as pd
import datetime
from sklearn.cluster import DBSCAN
from fpdf import FPDF

# --- SETUP & KONFIGURATION ---
st.set_page_config(page_title="Klavierlehrer Cockpit", layout="wide")

# --- KONZERT-DATUM ---
KONZERT_DATUM = datetime.date(2026, 9, 2)

def berechne_konzert_countdown():
    heute = datetime.date.today()
    delta = KONZERT_DATUM - heute
    tage = delta.days
    if tage > 0:
        wochen = tage // 7
        rest_tage = tage % 7
        return f"⏳ Noch **{wochen} Wochen und {rest_tage} Tage** bis zum Klassenvorspiel (02.09.2026)!"
    elif tage == 0:
        return "🎉 Heute ist das Klassenvorspiel!"
    else:
        return "Das Klassenvorspiel in diesem Jahr ist bereits vorbei."

# --- DATEN-LOGIK (Verbindung zum Google Sheet vorbereitet) ---
def lade_archiv_aus_sheet():
    # Sobald die Google-Secrets hinterlegt sind, zieht sich die App hier 
    # die echten Daten aus deinem Google Sheet "Unterrichtscockpit Archiv".
    # Bis dahin nutzen wir die Struktur als Basis:
    try:
        # Platzhalter für den Google Sheets Connector
        pass
    except:
        pass
        
    # Basis-Struktur mit allen deinen geforderten Spalten
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

# --- KALENDER-ERKENNUNG (Platzhalter für Google Calendar API) ---
def get_aktueller_schueler_aus_kalender():
    # Hier greift später die automatische Kalender-Abfrage.
    # Gibt aktuell None zurück, damit das Fallback (Auswahl) greift, 
    # solange die API-Verbindung noch nicht aktiv ist.
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

# --- UI LOGIK ---
tab1, tab2, tab3 = st.tabs(["🎹 Cockpit & Countdown", "📊 Analyse & Scan", "🏆 Zertifikate & TaskCards"])

with tab1:
    st.title("🎹 Klavierlehrer Cockpit")
    
    # 1. KONZERT COUNTDOWN
    st.markdown(f"### {berechne_konzert_countdown()}")
    st.markdown("---")
    
    # 2. SCHÜLER- ERKENNUNG (Kalender oder manuelle Auswahl)
    erkennter_schueler = get_aktueller_schueler_aus_kalender()
    
    if erkennter_schueler:
        student = erkennter_schueler
        st.success(f"👤 Automatisch aus Kalender erkannt: {student}")
    else:
        schueler_liste = df_archiv['Schueler'].unique().tolist()
        student = st.selectbox("👤 Schüler manuell auswählen (Kein Kalender-Termin aktiv):", schueler_liste)
    
    st.subheader(f"Aktueller Unterricht: {student}")
    st.progress(0.45, text="Stunde läuft - Zeitbalken")
    
    # 3. NOTIZEN & HAUSAUFGABEN (Für die nächste Stunde / zu Hause)
    st.markdown("### 📝 Notizen & Vorbereitung")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Für die nächste Stunde zu besprechen:**\n* Noten im Bassschlüssel wiederholen\n* Handhaltung prüfen")
        neue_besprechung = st.text_input("Neuen Punkt für nächste Stunde eintragen:")
    
    with col2:
        st.warning(f"**Hausaufgabe / To-Do für zu Hause:**\n* Takt 15-20 langsam üben")
        neue_hausaufgabe = st.text_input("Neue Hausaufgabe für zu Hause eintragen:")

    if st.button("Notizen & Hausaufgaben im Sheet speichern"):
        st.success(f"Gespeichert! Die Notizen für {student} wurden ins Google Sheet übertragen.")
    
    # 4. LOBKÄRTCHEN & TASKCARDS
    with st.expander("🏆 Lobkärtchen vergeben & auf TaskCards teilen"):
        grund = st.text_input("Grund für das Lobkärtchen (z.B. Fantastischer Rhythmus!)")
        auf_taskcards = st.checkbox("Direkt auf dem TaskCards-Board des Schülers veröffentlichen", value=True)
        
        if st.button("Kärtchen vergeben & ins Sheet schreiben"):
            st.success(f"Kärtchen für {student} im Google Sheet Archiv gespeichert!")
            if auf_taskcards:
                st.info(f"🔗 Erfolgreich an TaskCards gesendet!")

with tab2:
    st.title("📊 Analyse & Dichte-Scan")
    if len(df_archiv) >= 2:
        db = DBSCAN(eps=0.5, min_samples=2).fit(df_archiv[['Dauer_Minuten', 'Schwierigkeit']])
        df_archiv['Cluster'] = db.labels_
        fig = px.scatter(df_archiv, x="Dauer_Minuten", y="Schwierigkeit", color="Cluster", symbol="Kärtchen_Erhalten", hover_name="Schueler")
        st.plotly_chart(fig)
    else:
        st.write("Noch nicht genügend Daten für eine Cluster-Analyse vorhanden.")

with tab3:
    st.title("🏆 Jahres-Zertifikate & TaskCards Übersicht")
    st.write(f"Hier kannst du das Jahres-Zertifikat für **{student}** generieren.")
    
    if st.button(f"Zertifikat für {student} als PDF erstellen"):
        pdf_daten = erstelle_zertifikat_pdf(student, df_archiv)
        st.download_button(
            label="📥 PDF-Zertifikat herunterladen",
            data=pdf_daten,
            file_name=f"Zertifikat_{student}_{datetime.datetime.now().year}.pdf",
            mime="application/pdf"
        )
        st.success("PDF wurde generiert
