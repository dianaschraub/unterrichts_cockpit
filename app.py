

Eingefügter Text(1).txt
Dokument

Nein – in der aktuellen Datei sind diese beiden Kernfunktionen noch nicht wirklich umgesetzt. Gut, dass du das ansprichst.

Die fertige App soll so funktionieren:

Beim Öffnen schaut sie auf Datum und Uhrzeit.

Sie liest den aktuellen Termin aus deinem Google Kalender.

Steht dort beispielsweise „Klavierunterricht Emma, 15:00–15:45“, erscheint automatisch Emma.

Gleichzeitig werden Emmas bisherige Stücke, Aufgaben, Notizen und benötigte Noten geladen.

Über gut sichtbare Schaltflächen öffnest du die zugehörigen Noten mit einem Klick.

Im vorhandenen Code ist die Kalenderfunktion noch leer – sie gibt immer None zurück. Auch das Feld für den Notenlink speichert bislang lediglich Text; es erzeugt noch keinen funktionierenden Noten-Button.

Die schmale Seitenleiste würde ich deshalb ändern:

Der automatisch erkannte Schüler wird oben deutlich angezeigt.

Eine manuelle Schülerauswahl bleibt nur als unauffällige Notlösung bestehen – etwa bei einer Vertretungsstunde, Terminverschiebung oder wenn der Kalender einmal keinen passenden Eintrag findet.

Du musst im normalen Unterricht nichts selbst auswählen.

Bei den Noten gibt es einen wichtigen Unterschied:

Cloud-Dateien können direkt über Schaltflächen geöffnet werden.

Eine angeschlossene SSD kann die App nur direkt lesen, wenn sie auf demselben Laptop lokal läuft. Eine im Internet veröffentlichte App kann aus Sicherheitsgründen nicht auf eine SSD zugreifen, die an deinem Tablet oder Laptop steckt.

Bevor ich weiterbaue, brauche ich deshalb zwei kurze Angaben:

Soll die App später über das Internet auf Tablet und Laptop laufen oder nur lokal auf deinem Laptop?

Wie heißen deine Unterrichtstermine im Google Kalender – zum Beispiel nur „Emma“ oder „Klavierunterricht Emma“?

Danach richte ich das Design konsequent um diese beiden Hauptfunktionen herum aus.


Die App soll später auf meinem Tablet laufen oder auf meinem Handy ein Laptop habe ich nicht Die Unterrichtstermine heißen dann nur immer Luisa also dort wird immer nur der Name von dem Schüler angezeigt oder ein von mir eingetragen 

Perfekt – damit ist die passende Lösung klar: Die App wird als geschützte Web-App veröffentlicht und läuft anschließend im Browser auf Tablet und Handy. Ein Laptop ist dafür nicht nötig.

Der Ablauf wird so gestaltet:

Um 15:00 Uhr öffnest du die App.

Sie prüft automatisch den momentan laufenden Google-Kalendertermin.

Steht im Termintitel nur „Luisa“, verwendet die App genau diesen Namen.

Sie sucht Luisa im Schülerarchiv und zeigt sofort ihre Stücke, letzten Aufgaben, Notizen, Fortschritte und Notenlinks an.

Oben steht beispielsweise: „Luisa · automatisch aus dem Kalender erkannt · 15:00–15:45“.

Nur wenn kein passender Termin gefunden wird, erscheint eine kleine manuelle Schülerauswahl als Notlösung.

Die bisherige Seitenleiste werde ich daher deutlich zurücknehmen. Sie soll nicht deine normale Schülerauswahl sein.

Für die Noten empfehle ich Google Drive. Dann können neben jedem Stück klare Schaltflächen stehen:

„Noten öffnen“

„Tastenforscher öffnen“

„Konzertstück öffnen“

Die Datei öffnet sich direkt auf dem Tablet oder Handy. Eine SSD beziehungsweise Speicherkarte ist dafür leider ungeeignet: Eine veröffentlichte Web-App darf aus Sicherheitsgründen nicht selbstständig auf Dateien zugreifen, die lokal an deinem Mobilgerät angeschlossen sind. Cloudlinks funktionieren dagegen zuverlässig.

Ich plane deshalb jetzt fest mit:

Google Kalender zur automatischen Schülererkennung

Google Sheets als dauerhaftem Archiv

Google Drive für die Noten

manueller Schülerauswahl nur als Reserve

Damit arbeiten Kalender, Archiv und Noten in einem gemeinsamen Google-System zusammen.


Kannst du noch ein weiteres Feld hinzufügen nächster Schüler mit Name und Uhrzeit weil manchmal habe ich auch Lücken zwischen den Schülern und dann wäre es natürlich einfach gut zu wissen wann der nächste kommt 

Ja, das Feld ist ergänzt. Im oberen Bereich stehen nun:

Aktueller Schüler mit Unterrichtsdatum und Dauer

Nächster Schüler mit Name und Uhrzeit

Zeit bis zum nächsten Termin, zum Beispiel „in 45 Minuten“

Nach dem letzten Termin: „Heute kein weiterer Schüler“

Die tatsächlichen Namen und Uhrzeiten werden automatisch eingesetzt, sobald wir die Google-Kalender-Verbindung anschließen. Die manuelle Auswahl bleibt nur als Reserve.


Vielleicht kannst du an die Seite auch noch so eine schmale Leiste einfügen wo die Schüler die heute noch kommen alle einmal kurz aufgelistet sind also links finde ich das vielleicht ganz ideal und andersfarbig hinterlegt und dann also so ein Zeitstrahl von oben nach unten auf dem die Schüler eingetragen sind mit ihrem anfangs und Endzeit also so ähnlich ja wie Sonne tagesleiste auf dem Kalender 


Und dass ich die Liste dann einfach weiter verschiebt also die Schüler die schon da waren dass die dann aus der Liste rausrutschen und die Liste so zusammen im Laufe des Tages immer kürzer wird und dann eben beim letzten nach dem letzten Schüler irgendwas lustiges schreibt wie z.B Feierabend 

Die dynamische Tagesleiste ist eingebaut:

Nur laufende und kommende Schüler bleiben sichtbar.

Vergangene Termine rutschen automatisch aus der Liste.

Anfangs- und Endzeiten stehen bei jedem Schüler.

Unterrichtslücken werden als Pause angezeigt.

Die aktuelle Stunde wird farblich hervorgehoben.

Nach dem letzten Schüler erscheint: „Feierabend! Auch der Flügel hat jetzt frei.“

klavier_cockpit_professionell.py

Die echten Namen und Uhrzeiten werden eingesetzt, sobald wir die Google-Kalender-Verbindung anschließen.


klavier_cockpit_professionell.py
Code


Bibliothek
/
klavier_cockpit_professionell.py


import streamlit as st
import pandas as pd
import datetime
import html
import plotly.express as px
from zoneinfo import ZoneInfo
from fpdf import FPDF
import urllib.parse

# --- SETUP & DESIGN-KONFIGURATION ---
st.set_page_config(page_title="Klavierlehrer Cockpit", layout="wide", page_icon="🎹")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
    :root {
        --navy: #17243b;
        --navy-soft: #253653;
        --gold: #b8954b;
        --gold-light: #e6d4a7;
        --ivory: #f7f4ed;
        --paper: #fffdf8;
        --ink: #263247;
        --muted: #687386;
        --line: #e6dfd1;
    }
    .stApp {
        background: linear-gradient(145deg, #f7f4ed 0%, #fbfaf6 55%, #f1ede4 100%);
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }
    .block-container { max-width: 1280px; padding-top: 1.4rem; padding-bottom: 3rem; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: var(--navy) !important; }
    [data-baseweb="tab-list"] {
        gap: 8px; background: rgba(255,255,255,.72); padding: 7px;
        border: 1px solid var(--line); border-radius: 14px; box-shadow: 0 8px 24px rgba(23,36,59,.06);
    }
    [data-baseweb="tab"] { border-radius: 9px; padding: 10px 18px; font-weight: 650; }
    [data-baseweb="tab"][aria-selected="true"] { background: var(--navy) !important; color: white !important; }
    .stButton>button {
        border-radius: 10px; font-weight: 700; border: 1px solid var(--navy);
        background: var(--navy); color: white; min-height: 44px;
        box-shadow: 0 5px 14px rgba(23,36,59,.14); transition: .18s ease;
    }
    .stButton>button:hover { background: var(--navy-soft); color: white; border-color: var(--gold); transform: translateY(-1px); }
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input, [data-baseweb="select"] > div {
        background: rgba(255,255,255,.88); border-color: #d9d1c2; border-radius: 9px;
    }
    .hero {
        background: linear-gradient(125deg, #17243b 0%, #263955 75%, #344967 100%);
        color: white; padding: 26px 30px; border-radius: 18px; margin-bottom: 18px;
        box-shadow: 0 15px 35px rgba(23,36,59,.18); position: relative; overflow: hidden;
    }
    .hero:after { content:'♪'; position:absolute; right:28px; top:-28px; font-size:130px; color:rgba(230,212,167,.12); }
    .hero-kicker { color: var(--gold-light); text-transform: uppercase; letter-spacing: .14em; font-size: 12px; font-weight: 700; }
    .hero-title { font-family:'Playfair Display',serif; font-size: 34px; font-weight: 700; margin: 4px 0; }
    .hero-subtitle { color: #dfe5ec; margin: 0; font-size: 15px; }
    .metric-card {
        background: rgba(255,253,248,.95); padding: 18px 20px; border-radius: 13px;
        border: 1px solid var(--line); border-left: 4px solid var(--gold); margin-bottom: 20px;
        box-shadow: 0 8px 22px rgba(23,36,59,.06);
    }
    .section-card { background:rgba(255,253,248,.78); border:1px solid var(--line); border-radius:14px; padding:5px 18px 15px; margin:12px 0 18px; }
    .section-head { margin: 30px 0 13px; }
    .section-kicker { color: var(--gold); text-transform: uppercase; letter-spacing: .12em; font-size: 11px; font-weight: 800; }
    .section-title { color: var(--navy); font-family:'Playfair Display',serif; font-size: 24px; font-weight:700; margin:1px 0 2px; }
    .section-copy { color: var(--muted); font-size: 14px; margin:0; }
    .summary-card {
        min-height: 126px; background: rgba(255,253,248,.92); border:1px solid var(--line);
        border-radius:14px; padding:17px 18px; box-shadow:0 7px 18px rgba(23,36,59,.055);
    }
    .summary-label { color:var(--muted); text-transform:uppercase; letter-spacing:.09em; font-size:10px; font-weight:800; }
    .summary-value { color:var(--navy); font-family:'Playfair Display',serif; font-size:23px; font-weight:700; margin:7px 0 3px; }
    .summary-note { color:var(--muted); font-size:12px; line-height:1.35; }
    .save-panel {
        background:linear-gradient(125deg,#17243b,#283b58); color:white; padding:20px 22px;
        border-radius:15px; margin-top:26px; box-shadow:0 12px 28px rgba(23,36,59,.16);
    }
    .save-panel-title { font-family:'Playfair Display',serif; font-size:21px; font-weight:700; }
    .save-panel-copy { color:#dbe2eb; font-size:13px; margin-top:3px; }
    [data-testid="stSidebar"] { background:#e8edf4; border-right:1px solid #d5dce6; }
    [data-testid="stSidebar"] .block-container { padding-top:1.8rem; }
    [data-testid="stSidebar"] h2 { font-size:22px; }
    .day-label { color:#687386; text-transform:uppercase; letter-spacing:.12em; font-size:10px; font-weight:800; }
    .day-title { color:#17243b; font-family:'Playfair Display',serif; font-size:24px; font-weight:700; margin:2px 0 3px; }
    .day-date { color:#687386; font-size:12px; margin-bottom:17px; }
    .day-rail { position:relative; margin:8px 0 20px; }
    .day-rail:before { content:''; position:absolute; left:9px; top:8px; bottom:8px; width:2px; background:#c3ccd8; }
    .rail-entry { position:relative; padding-left:29px; margin:0 0 12px; }
    .rail-dot { position:absolute; left:3px; top:17px; width:14px; height:14px; border-radius:50%; background:#fff; border:3px solid #8b98aa; z-index:1; }
    .rail-card { background:rgba(255,255,255,.78); border:1px solid #d5dce6; border-radius:10px; padding:10px 11px; }
    .rail-time { color:#687386; font-size:10px; font-weight:800; letter-spacing:.03em; }
    .rail-name { color:#263247; font-size:14px; font-weight:750; margin-top:2px; }
    .rail-entry.active .rail-dot { background:#b8954b; border-color:#17243b; box-shadow:0 0 0 4px rgba(184,149,75,.22); }
    .rail-entry.active .rail-card { background:#17243b; border-color:#17243b; box-shadow:0 7px 17px rgba(23,36,59,.16); }
    .rail-entry.active .rail-time { color:#e6d4a7; }
    .rail-entry.active .rail-name { color:#fff; }
    .rail-entry.past { opacity:.53; }
    .rail-gap { position:relative; margin:0 0 12px 29px; color:#687386; font-size:10px; font-weight:700; }
    .rail-gap span { background:#dbe2eb; border-radius:20px; padding:4px 8px; }
    .rail-empty { background:rgba(255,255,255,.62); border:1px dashed #aeb9c7; border-radius:10px; padding:12px; color:#687386; font-size:12px; }
    [data-testid="stMetric"] {
        background:rgba(255,253,248,.9); border:1px solid var(--line); padding:15px 17px;
        border-radius:12px; box-shadow:0 6px 16px rgba(23,36,59,.045);
    }
    /* Edle Box für das Lobkärtchen */
    .lob-box {
        background: linear-gradient(135deg, #fffdf7 0%, #f5ead0 100%);
        border: 1px solid var(--gold); padding: 18px; border-radius: 14px;
        box-shadow: 0 8px 22px rgba(184,149,75,.15);
        max-width: 650px;
        margin: 20px auto;
    }
    hr { border-color: var(--line) !important; }
    div[data-testid="stProgress"] > div > div { background-color: var(--gold); }
    @media (max-width: 900px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1rem; }
        .hero { padding: 22px 20px; border-radius: 14px; }
        .hero-title { font-size: 28px; }
        .hero:after { font-size: 95px; right: 14px; }
        .summary-card { min-height: 116px; padding: 14px; }
        .summary-value { font-size: 19px; }
        [data-baseweb="tab"] { padding: 9px 11px; font-size: 13px; }
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
        return f"Noch {wochen} Wochen und {rest_tage} Tage"
    elif tage == 0:
        return "Heute ist das Klassenvorspiel!"
    else:
        return "Das Vorspiel ist bereits vorbei"

def berechne_fortschritt_unterricht(start_minute=0, dauer=45):
    """Platzhalter für die spätere automatische Kalender-/Zeiterkennung."""
    return min(max(start_minute / dauer, 0.0), 1.0)

def abschnitt(kicker, titel, beschreibung):
    st.markdown(
        f"""
        <div class="section-head">
            <div class="section-kicker">{kicker}</div>
            <div class="section-title">{titel}</div>
            <p class="section-copy">{beschreibung}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

def get_heutige_unterrichtstermine_aus_kalender():
    """Liefert nach der Google-Anbindung Termine als Name-, Start- und Ende-Dicts."""
    return None

def finde_aktuellen_und_naechsten_termin(termine, jetzt=None):
    if not termine:
        return None, None

    jetzt = jetzt or datetime.datetime.now(ZoneInfo("Europe/Berlin"))
    sortierte_termine = sorted(termine, key=lambda termin: termin["start"])
    aktueller_termin = next(
        (termin for termin in sortierte_termine if termin["start"] <= jetzt < termin["ende"]),
        None,
    )
    naechster_termin = next(
        (termin for termin in sortierte_termine if termin["start"] > jetzt),
        None,
    )
    return aktueller_termin, naechster_termin

def formatiere_pause(minuten):
    if minuten >= 60:
        stunden, rest = divmod(minuten, 60)
        return f"Pause · {stunden} Std. {rest} Min."
    return f"Pause · {minuten} Min."

def erstelle_tagesleisten_html(termine, jetzt=None):
    if termine is None:
        return '<div class="rail-empty">Die Tagesleiste erscheint hier, sobald der Google Kalender verbunden ist.</div>'

    if not termine:
        return '<div class="rail-empty"><strong>Heute keine Termine.</strong><br>Zeit für freie Improvisation.</div>'

    jetzt = jetzt or datetime.datetime.now(ZoneInfo("Europe/Berlin"))
    sortierte_termine = sorted(termine, key=lambda termin: termin["start"])
    verbleibende_termine = [termin for termin in sortierte_termine if termin["ende"] > jetzt]

    if not verbleibende_termine:
        return '<div class="rail-empty"><strong>Feierabend!</strong><br>Auch der Flügel hat jetzt frei.</div>'

    bausteine = ['<div class="day-rail">']
    erster_termin = verbleibende_termine[0]
    if erster_termin["start"] > jetzt:
        minuten_pause = int((erster_termin["start"] - jetzt).total_seconds() // 60)
        if minuten_pause >= 5:
            bausteine.append(f'<div class="rail-gap"><span>{formatiere_pause(minuten_pause)}</span></div>')

    vorheriges_ende = None
    for termin in verbleibende_termine:
        if vorheriges_ende and termin["start"] > vorheriges_ende:
            minuten_luecke = int((termin["start"] - vorheriges_ende).total_seconds() // 60)
            if minuten_luecke >= 5:
                bausteine.append(f'<div class="rail-gap"><span>{formatiere_pause(minuten_luecke)}</span></div>')

        status = "active" if termin["start"] <= jetzt < termin["ende"] else "future"
        name = html.escape(str(termin.get("name", "Ohne Namen")))
        zeit = f'{termin["start"].strftime("%H:%M")}–{termin["ende"].strftime("%H:%M")} Uhr'
        bausteine.append(
            f'<div class="rail-entry {status}"><div class="rail-dot"></div>'
            f'<div class="rail-card"><div class="rail-time">{zeit}</div>'
            f'<div class="rail-name">{name}</div></div></div>'
        )
        vorheriges_ende = termin["ende"]

    bausteine.append("</div>")
    return "".join(bausteine)

def formatiere_naechsten_termin(termin, kalender_verbunden=False):
    if not termin and not kalender_verbunden:
        return "Noch nicht verbunden", "Google Kalender wird im nächsten Schritt angeschlossen"
    if not termin:
        return "Heute niemand mehr", "Feierabend – auch der Flügel hat jetzt frei"

    name = termin.get("name", "Unbekannt")
    start = termin.get("start")
    if not start:
        return name, "Uhrzeit nicht verfügbar"

    jetzt = datetime.datetime.now(start.tzinfo) if start.tzinfo else datetime.datetime.now()
    minuten_bis_start = max(0, int((start - jetzt).total_seconds() // 60))
    if minuten_bis_start >= 60:
        stunden, minuten = divmod(minuten_bis_start, 60)
        abstand = f"in {stunden} Std. {minuten} Min."
    else:
        abstand = f"in {minuten_bis_start} Minuten"
    return f"{name} · {start.strftime('%H:%M')} Uhr", abstand

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

# --- DAUERHAFTE STEUERUNG IN DER SEITENLEISTE ---
schueler_liste = df_archiv["Schueler"].dropna().unique().tolist()
jetzt = datetime.datetime.now(ZoneInfo("Europe/Berlin"))
heutige_termine = get_heutige_unterrichtstermine_aus_kalender()
aktueller_termin, naechster_termin = finde_aktuellen_und_naechsten_termin(heutige_termine, jetzt)
erkennter_schueler = aktueller_termin["name"] if aktueller_termin else None
naechster_titel, naechster_hinweis = formatiere_naechsten_termin(
    naechster_termin,
    kalender_verbunden=heutige_termine is not None,
)

with st.sidebar:
    st.markdown('<div class="day-label">Tagesübersicht</div>', unsafe_allow_html=True)
    st.markdown('<div class="day-title">Heute im Unterricht</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="day-date">{datetime.date.today().strftime("%d.%m.%Y")}</div>', unsafe_allow_html=True)
    st.markdown(erstelle_tagesleisten_html(heutige_termine, jetzt), unsafe_allow_html=True)

    if erkennter_schueler:
        student = erkennter_schueler
        unterrichtsdatum = datetime.date.today()
        dauer_minuten = int((aktueller_termin["ende"] - aktueller_termin["start"]).total_seconds() // 60)
        st.success(f"Aktuell: {student}")
        fortschritt = (jetzt - aktueller_termin["start"]).total_seconds() / (aktueller_termin["ende"] - aktueller_termin["start"]).total_seconds()
        st.progress(min(max(fortschritt, 0.0), 1.0), text=f'{aktueller_termin["start"].strftime("%H:%M")}–{aktueller_termin["ende"].strftime("%H:%M")} Uhr')
    else:
        with st.expander("Schüler manuell auswählen", expanded=heutige_termine is None):
            student = st.selectbox("Schüler", schueler_liste, label_visibility="collapsed")
            unterrichtsdatum = st.date_input("Datum", value=datetime.date.today(), format="DD.MM.YYYY")
            dauer_minuten = st.selectbox("Dauer", [30, 45, 60], index=1, format_func=lambda x: f"{x} Minuten")
        st.caption("Die manuelle Auswahl wird nur benötigt, wenn gerade kein Kalendertermin läuft.")

# --- UI NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["Live-Cockpit", "Analyse & Fortschritt", "Zertifikate & TaskCards"])

with tab1:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Digitales Unterrichtsstudio</div>
            <div class="hero-title">Klavierlehrer Live-Cockpit</div>
            <p class="hero-subtitle">Konzentriert unterrichten. Fortschritte sichtbar machen. Besonderes festhalten.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uebersicht1, uebersicht2, uebersicht3 = st.columns([1.05, 1.2, 1.25])
    with uebersicht1:
        st.markdown(
            f"""<div class="summary-card"><div class="summary-label">Aktueller Schüler</div>
            <div class="summary-value">{student}</div><div class="summary-note">{unterrichtsdatum.strftime('%d.%m.%Y')} · {dauer_minuten} Minuten · Unterricht aktiv</div></div>""",
            unsafe_allow_html=True,
        )
    with uebersicht2:
        st.markdown(
            f"""<div class="summary-card"><div class="summary-label">Nächster Schüler</div>
            <div class="summary-value">{naechster_titel}</div><div class="summary-note">{naechster_hinweis}</div></div>""",
            unsafe_allow_html=True,
        )
    with uebersicht3:
        st.markdown(
            f"""<div class="summary-card"><div class="summary-label">Klassenvorspiel · 02.09.2026</div>
            <div class="summary-value">{berechne_konzert_countdown()}</div><div class="summary-note">Konzertvorbereitung im Blick behalten</div></div>""",
            unsafe_allow_html=True,
        )

    abschnitt("01 · Technik", "Übungs- und Technikbereich", "Wähle den passenden Bereich und dokumentiere nur das, was heute relevant ist.")
    modus = st.radio(
        "Bereich auswählen",
        ["Tastenforscher", "Klassische Tonleitern", "Fortgeschrittene Etüden"],
        horizontal=True,
    )

    if modus == "Tastenforscher":
        col_h1, col_h2, col_h3 = st.columns([1.2, 0.8, 1.4])
        with col_h1:
            heft_titel = st.text_input("Titel der Übung", value="Tastenforscher")
        with col_h2:
            seiten_zahl = st.text_input("Seite", placeholder="z. B. 12–13")
        with col_h3:
            heft_link = st.text_input("Dateilink · Cloud oder SSD", placeholder="Optional")
        speicher_text = f"Tastenforscher: {heft_titel}, {seiten_zahl or 'ohne Seitenangabe'}"

    elif modus == "Klassische Tonleitern":
        col_t1, col_t2 = st.columns([1, 1.4])
        with col_t1:
            tonleiter_text = st.text_input("Tonart oder Tonleiter", placeholder="z. B. C-Dur")
        with col_t2:
            bewegung_wahl = st.radio("Spielart", ["Parallelbewegung", "Gegenbewegung"], horizontal=True)
        tempo_wahl = st.slider("Tempo", min_value=40, max_value=200, value=80, step=2, format="%d BPM")
        speicher_text = f"Tonleiter: {tonleiter_text or 'ohne Tonart'} · {bewegung_wahl} · {tempo_wahl} BPM"

    else:
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            etuede_titel = st.text_input("Etüde oder Name", placeholder="z. B. Etüde Nr. 6")
        with col_e2:
            komponist = st.text_input("Komponist", placeholder="z. B. Czerny")
        with col_e3:
            opus_nr = st.text_input("Opus oder Werknummer", placeholder="z. B. op. 299")
        col_e4, col_e5 = st.columns([1.2, 0.8])
        with col_e4:
            etuede_takte = st.text_input("Gespielte Takte", placeholder="z. B. Takt 1–32")
        with col_e5:
            etuede_tempo = st.number_input("Tempo in BPM", min_value=40, max_value=250, value=100, step=2)
        etuede_notizen = st.text_area("Technische Beobachtung", placeholder="z. B. Fokus auf Artikulation", height=90)
        speicher_text = f"Etüde: {etuede_titel or 'ohne Titel'} · {komponist or 'ohne Komponist'} · {opus_nr or 'ohne Werknummer'} · {etuede_takte or 'ohne Taktangabe'} · {etuede_tempo} BPM"

    abschnitt("02 · Repertoire", "Stücke und Konzertziel", "Trenne das aktuell erarbeitete Repertoire klar vom ausgewählten Vorspielstück.")
    col_stueck1, col_stueck2 = st.columns(2)
    with col_stueck1:
        aktuelles_stueck_input = st.text_input("Gespieltes Hauptstück", placeholder="Titel und Komponist")
    with col_stueck2:
        konzert_stueck_input = st.text_input("Konzertstück · Vorspiel am 02.09.", placeholder="Ausgewähltes Vorspielstück")

    abschnitt("03 · Transfer", "Aufgaben und Vorbereitung", "Links steht der klare Übeauftrag für das Kind, rechts deine Vorbereitung für die nächste Stunde.")
    col1, col2 = st.columns(2)
    with col1:
        neue_hausaufgabe = st.text_area("Hausaufgabe für das Kind", placeholder="Konkret, kurz und gut überprüfbar formulieren", height=125)
    with col2:
        neue_besprechung = st.text_area("Bis zur nächsten Stunde erledigen", placeholder="Noten, Material, Rückfragen oder organisatorische Punkte", height=125)

    abschnitt("04 · Würdigung", "Lobkärtchen", "Ein besonderer Erfolg wird wertschätzend festgehalten und kann später für TaskCards genutzt werden.")
    _, col_lob_mitte, _ = st.columns([0.7, 3, 0.7])
    with col_lob_mitte:
        lob_vergeben = st.checkbox("Für diese Stunde ein Lobkärtchen vergeben")
        if lob_vergeben:
            grund = st.text_area("Persönliche Würdigung", placeholder="Was ist heute besonders gut gelungen?", height=105)
            auf_taskcards = st.checkbox("Für die Veröffentlichung auf TaskCards vormerken", value=True)
        else:
            grund = ""
            auf_taskcards = False

    with st.expander("Meine Vorbereitung und internen Aufgaben", expanded=False):
        aufgabe_1 = st.checkbox("Noten für die nächste Stunde heraussuchen und kopieren")
        aufgabe_2 = st.checkbox("TaskCards-Board aktualisieren")
        neue_lehrer_aufgabe = st.text_input("Weitere eigene Aufgabe", placeholder="Optional")

    st.markdown(
        """<div class="save-panel"><div class="save-panel-title">Unterricht vollständig dokumentieren</div>
        <div class="save-panel-copy">Technik, Repertoire, Aufgaben und Lob werden gemeinsam als ein Unterrichtseintrag gesichert.</div></div>""",
        unsafe_allow_html=True,
    )
    if st.button("Unterrichtseintrag speichern", type="primary", use_container_width=True):
        st.success(f"Unterrichtseintrag für {student} am {unterrichtsdatum.strftime('%d.%m.%Y')} ist vollständig erfasst.")
        st.caption("Die dauerhafte Übertragung in Google Sheets wird im nächsten Schritt angeschlossen.")

with tab2:
    st.markdown("## Analyse & Fortschritt")
    st.caption(f"Entwicklung und Jahresüberblick für {student}")

    verlauf_daten = pd.DataFrame(
        {
            "Datum": ["2026-01-10", "2026-03-15", "2026-05-05", "2026-07-20", "2026-08-18"],
            "Tempo": [60, 72, 90, 110, 128],
            "Tonart": ["C-Dur"] * 5,
        }
    )
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Archivierte Einträge", len(df_archiv[df_archiv["Schueler"] == student]))
    kpi2.metric("Aktuelles Tempo", "128 BPM", "+18 BPM")
    kpi3.metric("Erarbeitete Stücke", df_archiv[df_archiv["Schueler"] == student]["Stueck"].nunique())
    kpi4.metric("Lobkärtchen", len(df_archiv[(df_archiv["Schueler"] == student) & (df_archiv["Kärtchen_Erhalten"] == "Ja")]))

    abschnitt("Jahresverlauf", "Tempo-Entwicklung", "Die Beispielkurve wird nach der Google-Sheets-Anbindung automatisch aus den Unterrichtseinträgen gespeist.")
    fig = px.line(verlauf_daten, x="Datum", y="Tempo", markers=True)
    fig.update_traces(line_color="#b8954b", line_width=3, marker=dict(size=9, color="#17243b"))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,253,248,.7)",
        font=dict(family="DM Sans", color="#263247"),
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title=None,
        yaxis_title="Tempo · BPM",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    abschnitt("Archiv", "Alle Unterrichtseinträge", "Durchsuche und kontrolliere die bisher erfassten Daten.")
    st.dataframe(df_archiv, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("## Zertifikate & TaskCards")
    st.caption(f"Persönlicher Jahresabschluss 2026 für {student}")

    info_col, action_col = st.columns([1.35, 1])
    with info_col:
        abschnitt("Jahreszertifikat", "Fortschritt sichtbar würdigen", "Das Zertifikat bündelt erarbeitete Stücke und besondere Erfolge aus dem Archiv.")
        st.info("Vor der Erstellung kannst du die Einträge im Analyse-Tab noch einmal kontrollieren.")
    with action_col:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        zertifikat_erstellen = st.button("PDF-Zertifikat erstellen", type="primary", use_container_width=True)

    if zertifikat_erstellen:
        pdf_daten = erstelle_zertifikat_pdf(student, df_archiv)
        st.success("Das Zertifikat ist bereit.")
        download_col, whatsapp_col = st.columns(2)
        with download_col:
            st.download_button(
                label="PDF herunterladen",
                data=pdf_daten,
                file_name=f"Zertifikat_{student}_{datetime.datetime.now().year}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with whatsapp_col:
            aktuelles_jahr = datetime.datetime.now().year
            whatsapp_text = f"Hallo! Hier ist das Jahres-Zertifikat {aktuelles_jahr} für {student} aus der Klavierstunde."
            whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(whatsapp_text)}"
            st.link_button("Über WhatsApp teilen", whatsapp_url, use_container_width=True)
