# Klavierlehrer Live-Cockpit
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import datetime
import html
import json
import plotly.express as px
from zoneinfo import ZoneInfo
from fpdf import FPDF
import urllib.parse

try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    GSheetsConnection = None

# --- SETUP & DESIGN-KONFIGURATION ---
st.set_page_config(page_title="Klavierlehrer Cockpit", layout="wide", page_icon="\U0001F3B9")

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
    .block-container { max-width: 1280px; padding-top: 4.8rem; padding-bottom: 1.2rem; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: var(--navy) !important; }
    .cockpit-nav {
        display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px;
        background:#fffdf8; padding:7px; margin:0 0 14px;
        border:1px solid var(--line); border-radius:14px;
        box-shadow:0 8px 24px rgba(23,36,59,.08);
    }
    .cockpit-nav a {
        display:flex; align-items:center; justify-content:center; min-height:52px;
        padding:10px 14px; border:2px solid #cfc5b3; border-radius:9px;
        background:#f7f4ed !important; color:#17243b !important;
        font-family:'DM Sans',sans-serif !important; font-size:16px !important;
        font-weight:800 !important; line-height:1.2 !important; text-align:center;
        text-decoration:none !important; opacity:1 !important;
    }
    .cockpit-nav a:visited { color:#17243b !important; }
    .cockpit-nav a:hover {
        background:#eee8dc !important; border-color:var(--gold);
        color:#17243b !important; text-decoration:none !important;
    }
    .cockpit-nav a.active,
    .cockpit-nav a.active:visited,
    .cockpit-nav a.active:hover {
        background:#17243b !important; border-color:#17243b !important;
        color:#ffffff !important; box-shadow:0 5px 14px rgba(23,36,59,.2);
    }
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
    .hero:after { content:'\u266A'; position:absolute; right:28px; top:-28px; font-size:130px; color:rgba(230,212,167,.12); }
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
    .repertoire-hint {
        color:var(--muted); font-size:13px; margin:-3px 0 12px;
    }
    .tablet-overview {
        display:grid; grid-template-columns:1.35fr 1fr 1.2fr 1.1fr; gap:8px;
        background:linear-gradient(125deg,#17243b,#2d4260); color:#fff;
        padding:10px; border-radius:15px; margin:0 0 10px;
        box-shadow:0 10px 26px rgba(23,36,59,.16);
    }
    .tablet-brand, .tablet-fact {
        min-width:0; padding:10px 12px; border-radius:10px;
    }
    .tablet-brand { background:rgba(255,255,255,.06); }
    .tablet-fact { background:rgba(255,255,255,.1); }
    .tablet-kicker, .tablet-label {
        color:#e6d4a7; text-transform:uppercase; letter-spacing:.08em;
        font-size:9px; font-weight:800;
    }
    .tablet-title {
        color:#fff; font-family:'Playfair Display',serif; font-size:20px;
        font-weight:700; line-height:1.1; margin-top:3px;
    }
    .tablet-value {
        color:#fff; font-size:15px; font-weight:800; line-height:1.15;
        margin-top:4px; overflow-wrap:anywhere;
    }
    .tablet-note { color:#dfe5ec; font-size:10px; line-height:1.2; margin-top:3px; }
    .compact-head { margin:4px 0 8px; }
    .compact-kicker {
        color:var(--gold); font-size:10px; font-weight:800;
        letter-spacing:.1em; text-transform:uppercase;
    }
    .compact-title {
        color:var(--navy); font-family:'Playfair Display',serif;
        font-size:20px; font-weight:700; line-height:1.15;
    }
    .st-key-save_bar {
        position:sticky; bottom:0; z-index:50; background:rgba(247,244,237,.96);
        border-top:1px solid var(--line); padding:8px 0 5px;
        backdrop-filter:blur(8px);
    }
    .autosave-status {
        color:var(--muted); font-size:11px; text-align:center; margin-top:2px;
    }
    .notes-links { display:flex; flex-wrap:wrap; gap:6px; margin:6px 0 2px; }
    .notes-links a {
        background:#eef1f5; border:1px solid #cbd3dd; border-radius:8px;
        color:#17243b !important; font-size:11px; font-weight:800;
        padding:6px 9px; text-decoration:none !important;
    }
    .notes-links a:hover { border-color:var(--gold); background:#fffdf8; }
    .mini-shell {
        background:linear-gradient(145deg,#17243b,#2c4261); color:#fff;
        border-radius:16px; padding:16px 18px; margin-bottom:10px;
        box-shadow:0 10px 26px rgba(23,36,59,.2);
    }
    .mini-kicker {
        color:#e6d4a7; text-transform:uppercase; letter-spacing:.1em;
        font-size:10px; font-weight:800;
    }
    .mini-student {
        color:#fff; font-family:'Playfair Display',serif;
        font-size:26px; font-weight:700; margin-top:2px;
    }
    .mini-info { color:#dfe5ec; font-size:12px; margin-top:3px; }
    .mini-note-link {
        display:block; background:#f6ecd4; border:1px solid #d8bd7e;
        border-radius:10px; color:#17243b !important; font-weight:800;
        padding:10px 12px; margin:8px 0 12px; text-align:center;
        text-decoration:none !important;
    }
    [data-testid="stSidebar"] {
        background:#e8edf4; border-right:1px solid #d5dce6;
        width:225px !important; min-width:225px !important; max-width:225px !important;
    }
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
    .rail-entry.finish .rail-dot { background:#b8954b; border-color:#b8954b; }
    .rail-entry.finish .rail-card { background:#f6ecd4; border-color:#d8bd7e; }
    .rail-entry.finish .rail-time { color:#8b6c2f; }
    .rail-entry.finish .rail-name { color:#17243b; }
    .rail-entry.past { opacity:.53; }
    .rail-gap { position:relative; margin:0 0 12px 29px; color:#687386; font-size:10px; font-weight:700; }
    .rail-gap span { background:#dbe2eb; border-radius:20px; padding:4px 8px; }
    .rail-empty { background:rgba(255,255,255,.62); border:1px dashed #aeb9c7; border-radius:10px; padding:12px; color:#687386; font-size:12px; }
    [data-testid="stMetric"] {
        background:rgba(255,253,248,.9); border:1px solid var(--line); padding:15px 17px;
        border-radius:12px; box-shadow:0 6px 16px rgba(23,36,59,.045);
    }
    /* Edle Box f\u00FCr das Lobk\u00E4rtchen */
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
        .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 4.6rem; }
        .hero { padding: 22px 20px; border-radius: 14px; }
        .hero-title { font-size: 28px; }
        .hero:after { font-size: 95px; right: 14px; }
        .summary-card { min-height: 116px; padding: 14px; }
        .summary-value { font-size: 19px; }
        .cockpit-nav { gap:5px; padding:5px; }
        .cockpit-nav a {
            min-height:58px; padding:8px 6px; font-size:12px !important;
            line-height:1.18 !important;
        }
        .block-container { padding:4.6rem .55rem 4.5rem; }
        .tablet-overview { grid-template-columns:repeat(3,minmax(0,1fr)); gap:5px; padding:6px; }
        .tablet-brand { grid-column:1 / -1; }
        .tablet-brand, .tablet-fact { padding:7px 8px; }
        .tablet-title { font-size:18px; }
        .tablet-value { font-size:13px; }
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
    """Platzhalter f\u00FCr die sp\u00E4tere automatische Kalender-/Zeiterkennung."""
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

def hole_query_parameter(name, standard=""):
    try:
        wert = st.query_params.get(name, standard)
    except AttributeError:
        wert = st.experimental_get_query_params().get(name, [standard])
    if isinstance(wert, list):
        return wert[0] if wert else standard
    return wert

def hole_aktive_ansicht():
    """Liest die gewÃ¤hlte Hauptansicht aus der URL und bleibt abwÃ¤rtskompatibel."""
    ansicht = hole_query_parameter("ansicht", "live")
    return ansicht if ansicht in {"live", "analyse", "zertifikate"} else "live"

REPERTOIRE_SPALTEN = [
    "Titel",
    "Komponist",
    "Cloud-Link",
    "Verwendung",
    "Programm angemeldet",
]

def leere_repertoire_tabelle(anzahl=2):
    return pd.DataFrame(
        [
            {
                "Titel": "",
                "Komponist": "",
                "Cloud-Link": "",
                "Verwendung": "Unterricht",
                "Programm angemeldet": False,
            }
            for _ in range(anzahl)
        ],
        columns=REPERTOIRE_SPALTEN,
    )

def weiteres_stueck_hinzufuegen():
    anzahl = min(7, st.session_state.anzahl_stuecke + 1)
    tabelle = st.session_state.get(
        "repertoire_tabelle",
        leere_repertoire_tabelle(st.session_state.anzahl_stuecke),
    ).copy()
    if len(tabelle) < anzahl:
        tabelle = pd.concat([tabelle, leere_repertoire_tabelle(1)], ignore_index=True)
    st.session_state.repertoire_tabelle = tabelle.iloc[:anzahl].reset_index(drop=True)
    st.session_state.anzahl_stuecke = anzahl

def letztes_stueck_entfernen():
    anzahl = max(2, st.session_state.anzahl_stuecke - 1)
    tabelle = st.session_state.get(
        "repertoire_tabelle",
        leere_repertoire_tabelle(st.session_state.anzahl_stuecke),
    ).copy()
    st.session_state.repertoire_tabelle = tabelle.iloc[:anzahl].reset_index(drop=True)
    st.session_state.anzahl_stuecke = anzahl

def aktualisiere_repertoire_tabelle(bestehende_daten, neue_zeilen):
    spalten = [
        "SchÃ¼ler",
        "Titel",
        "Komponist",
        "Cloud-Link",
        "Verwendung",
        "Programm angemeldet",
    ]
    if bestehende_daten is None or bestehende_daten.empty:
        bestehende_daten = pd.DataFrame(columns=spalten)
    else:
        bestehende_daten = bestehende_daten.copy()
        for spalte in spalten:
            if spalte not in bestehende_daten.columns:
                bestehende_daten[spalte] = ""

    for neue_zeile in neue_zeilen:
        maske = (
            bestehende_daten["SchÃ¼ler"].fillna("").astype(str).str.casefold().eq(neue_zeile["SchÃ¼ler"].casefold())
            & bestehende_daten["Titel"].fillna("").astype(str).str.casefold().eq(neue_zeile["Titel"].casefold())
            & bestehende_daten["Komponist"].fillna("").astype(str).str.casefold().eq(neue_zeile["Komponist"].casefold())
        )
        if maske.any():
            for spalte in spalten:
                bestehende_daten.loc[maske, spalte] = neue_zeile[spalte]
        else:
            bestehende_daten = pd.concat(
                [bestehende_daten, pd.DataFrame([neue_zeile], columns=spalten)],
                ignore_index=True,
            )
    return bestehende_daten[spalten]

def speichere_in_google_sheets(archiv_zeile, repertoire_zeilen):
    if GSheetsConnection is None:
        return False

    try:
        verbindung = st.connection("gsheets", type=GSheetsConnection)

        archiv_bisher = verbindung.read(worksheet="Unterrichtsarchiv", ttl=0)
        if archiv_bisher is None:
            archiv_bisher = pd.DataFrame()
        archiv_bisher = archiv_bisher.copy()
        for spalte in ["Sch\u00FCler", "Datum", "Status"]:
            if spalte not in archiv_bisher.columns:
                archiv_bisher[spalte] = ""
        if archiv_zeile.get("Status") == "Abgeschlossen":
            entwurf_maske = (
                archiv_bisher["Sch\u00FCler"].fillna("").astype(str).eq(archiv_zeile["Sch\u00FCler"])
                & archiv_bisher["Datum"].fillna("").astype(str).eq(archiv_zeile["Datum"])
                & archiv_bisher["Status"].fillna("").astype(str).eq("Zwischenstand")
            )
            archiv_bisher = archiv_bisher.loc[~entwurf_maske].copy()
        archiv_aktuell = pd.concat(
            [archiv_bisher, pd.DataFrame([archiv_zeile])],
            ignore_index=True,
        )
        verbindung.update(worksheet="Unterrichtsarchiv", data=archiv_aktuell)

        if repertoire_zeilen:
            repertoire_bisher = verbindung.read(worksheet="Repertoire", ttl=0)
            repertoire_aktuell = aktualisiere_repertoire_tabelle(
                repertoire_bisher,
                repertoire_zeilen,
            )
            verbindung.update(worksheet="Repertoire", data=repertoire_aktuell)
        return True
    except Exception:
        return False

def speichere_unterrichtspaket(archiv_zeile, repertoire_zeilen):
    """HÃ¤lt Archiv und Repertoire getrennt und schreibt sie in ihre ZielblÃ¤tter."""
    st.session_state.setdefault("Unterrichtsarchiv", []).append(archiv_zeile)
    repertoire_speicher = st.session_state.setdefault("Repertoire", [])

    for neue_zeile in repertoire_zeilen:
        vorhandene_zeile = next(
            (
                zeile
                for zeile in repertoire_speicher
                if zeile["SchÃ¼ler"] == neue_zeile["SchÃ¼ler"]
                and zeile["Titel"].casefold() == neue_zeile["Titel"].casefold()
                and zeile["Komponist"].casefold() == neue_zeile["Komponist"].casefold()
            ),
            None,
        )
        if vorhandene_zeile:
            vorhandene_zeile.update(neue_zeile)
        else:
            repertoire_speicher.append(neue_zeile)

    st.session_state["letzter_unterrichtseintrag"] = {
        "Unterrichtsarchiv": archiv_zeile,
        "Repertoire": repertoire_zeilen,
    }
    return speichere_in_google_sheets(archiv_zeile, repertoire_zeilen)

def kompakt_titel(nummer, titel):
    st.markdown(
        f'<div class="compact-head"><div class="compact-kicker">{html.escape(nummer)}</div>'
        f'<div class="compact-title">{html.escape(titel)}</div></div>',
        unsafe_allow_html=True,
    )

def zeige_technikbereich():
    kompakt_titel("01 \u00B7 Technik", "\u00DCbungs- und Technikbereich")
    modus = st.radio(
        "Bereich",
        ["Tastenforscher", "Klassische Tonleitern", "Fortgeschrittene Et\u00FCden"],
        horizontal=True,
        key="technik_modus",
    )

    if modus == "Tastenforscher":
        titel_spalte, seiten_spalte = st.columns([1.35, 0.65])
        with titel_spalte:
            heft_titel = st.text_input(
                "Titel der \u00DCbung",
                value="Tastenforscher",
                key="technik_heft_titel",
            )
        with seiten_spalte:
            seiten_zahl = st.text_input(
                "Seite",
                placeholder="12\u201313",
                key="technik_heft_seite",
            )
        heft_link = st.text_input(
            "Cloud-Link zu den Noten",
            placeholder="Link einf\u00FCgen",
            key="technik_heft_link",
        )
        return modus, (
            f"Tastenforscher: {heft_titel}, {seiten_zahl or 'ohne Seitenangabe'}"
            f" \u00B7 Cloud-Link: {heft_link or 'nicht hinterlegt'}"
        )

    if modus == "Klassische Tonleitern":
        tonart_spalte, spielart_spalte = st.columns([0.9, 1.1])
        with tonart_spalte:
            tonleiter_text = st.text_input(
                "Tonart oder Tonleiter",
                placeholder="z. B. C-Dur",
                key="technik_tonleiter",
            )
        with spielart_spalte:
            bewegung_wahl = st.selectbox(
                "Spielart",
                ["Parallelbewegung", "Gegenbewegung"],
                key="technik_spielart",
            )
        tempo_wahl = st.slider(
            "Tempo",
            min_value=40,
            max_value=200,
            value=80,
            step=2,
            format="%d BPM",
            key="technik_tonleiter_tempo",
        )
        return modus, (
            f"Tonleiter: {tonleiter_text or 'ohne Tonart'} \u00B7 "
            f"{bewegung_wahl} \u00B7 {tempo_wahl} BPM"
        )

    titel_spalte, komponist_spalte = st.columns(2)
    with titel_spalte:
        etuede_titel = st.text_input(
            "Et\u00FCde oder Name",
            placeholder="z. B. Et\u00FCde Nr. 6",
            key="technik_etuede_titel",
        )
    with komponist_spalte:
        komponist = st.text_input(
            "Komponist",
            placeholder="z. B. Czerny",
            key="technik_etuede_komponist",
        )
    opus_spalte, takte_spalte, tempo_spalte = st.columns([0.8, 1.1, 0.7])
    with opus_spalte:
        opus_nr = st.text_input(
            "Opus",
            placeholder="op. 299",
            key="technik_etuede_opus",
        )
    with takte_spalte:
        etuede_takte = st.text_input(
            "Takte",
            placeholder="1\u201332",
            key="technik_etuede_takte",
        )
    with tempo_spalte:
        etuede_tempo = st.number_input(
            "BPM",
            min_value=40,
            max_value=250,
            value=100,
            step=2,
            key="technik_etuede_tempo",
        )
    etuede_notizen = st.text_input(
        "Technische Beobachtung",
        placeholder="Fokus, Artikulation oder Bewegung",
        key="technik_etuede_notiz",
    )
    return modus, (
        f"Et\u00FCde: {etuede_titel or 'ohne Titel'} \u00B7 {komponist or 'ohne Komponist'} \u00B7 "
        f"{opus_nr or 'ohne Werknummer'} \u00B7 {etuede_takte or 'ohne Taktangabe'} \u00B7 "
        f"{etuede_tempo} BPM \u00B7 {etuede_notizen or 'ohne Beobachtung'}"
    )

def zeige_repertoirebereich(student, stundenende):
    kompakt_titel("02 \u00B7 Repertoire", "St\u00FCcke und Konzertziel")
    if "anzahl_stuecke" not in st.session_state:
        st.session_state.anzahl_stuecke = 2
    if "repertoire_tabelle" not in st.session_state:
        st.session_state.repertoire_tabelle = leere_repertoire_tabelle(2)

    anzahl = st.session_state.anzahl_stuecke
    tabelle = st.session_state.repertoire_tabelle.iloc[:anzahl].copy()
    while len(tabelle) < anzahl:
        tabelle = pd.concat([tabelle, leere_repertoire_tabelle(1)], ignore_index=True)

    bearbeitet = st.data_editor(
        tabelle,
        hide_index=True,
        use_container_width=True,
        height=min(315, 72 + anzahl * 35),
        key=f"repertoire_editor_{anzahl}",
        column_config={
            "Titel": st.column_config.TextColumn("Titel", width="medium"),
            "Komponist": st.column_config.TextColumn("Komponist", width="small"),
            "Cloud-Link": st.column_config.TextColumn(
                "Cloud-Link",
                width="medium",
                help="G\u00FCltigen Cloud-Link zu den Noten einf\u00FCgen.",
            ),
            "Verwendung": st.column_config.SelectboxColumn(
                "Verwendung",
                options=["Unterricht", "Konzertziel", "Unterricht & Konzert", "Wettbewerb"],
                width="medium",
                required=True,
            ),
            "Programm angemeldet": st.column_config.CheckboxColumn(
                "Angemeldet",
                width="small",
            ),
        },
    )
    st.session_state.repertoire_tabelle = bearbeitet.copy()

    knopf_hinzufuegen, knopf_entfernen = st.columns(2)
    with knopf_hinzufuegen:
        st.button(
            "Weiteres St\u00FCck",
            on_click=weiteres_stueck_hinzufuegen,
            disabled=anzahl >= 7,
            use_container_width=True,
            key="stueck_hinzufuegen",
        )
    with knopf_entfernen:
        st.button(
            "Letztes entfernen",
            on_click=letztes_stueck_entfernen,
            disabled=anzahl <= 2,
            use_container_width=True,
            key="stueck_entfernen",
        )
    st.caption(f"{anzahl} von maximal 7 St\u00FCcken \u00B7 zuerst Mini-Cockpit, danach Noten \u00F6ffnen")

    repertoire_eintraege = []
    noten_optionen = []
    for index, zeile in bearbeitet.iterrows():
        titel = "" if pd.isna(zeile["Titel"]) else str(zeile["Titel"]).strip()
        komponist = "" if pd.isna(zeile["Komponist"]) else str(zeile["Komponist"]).strip()
        cloud_link = "" if pd.isna(zeile["Cloud-Link"]) else str(zeile["Cloud-Link"]).strip()
        verwendung = "Unterricht" if pd.isna(zeile["Verwendung"]) else str(zeile["Verwendung"])
        ist_programmstueck = verwendung in {"Konzertziel", "Unterricht & Konzert", "Wettbewerb"}
        angemeldet = bool(zeile["Programm angemeldet"]) if not pd.isna(zeile["Programm angemeldet"]) else False
        repertoire_eintraege.append(
            {
                "Sch\u00FCler": str(student),
                "Titel": titel,
                "Komponist": komponist,
                "Cloud-Link": cloud_link,
                "Verwendung": verwendung,
                "Programm angemeldet": "Ja" if ist_programmstueck and angemeldet else "Nein",
            }
        )
        if ist_gueltiger_cloud_link(cloud_link):
            link_text = titel or f"St\u00FCck {index + 1}"
            noten_optionen.append(
                {
                    "Bezeichnung": f"{index + 1}. {link_text}",
                    "Titel": link_text,
                    "Link": cloud_link,
                }
            )

    if noten_optionen:
        auswahl = st.selectbox(
            "Noten f\u00FCr die Hochformat-Ansicht",
            options=list(range(len(noten_optionen))),
            format_func=lambda position: noten_optionen[position]["Bezeichnung"],
            key="noten_auswahl",
        )
        gewaehlte_noten = noten_optionen[auswahl]
        zeige_mini_cockpit_starter(
            student,
            stundenende,
            gewaehlte_noten["Link"],
            gewaehlte_noten["Titel"],
        )
    return repertoire_eintraege

def zeige_transferbereich():
    kompakt_titel("03 \u00B7 Aufgaben", "F\u00FCr das Kind und f\u00FCr mich")
    neue_hausaufgabe = st.text_area(
        "Hausaufgabe \u00B7 f\u00FCr das Kind",
        placeholder="Konkret und kurz formulieren",
        height=82,
        key="transfer_hausaufgabe",
    )
    neue_besprechung = st.text_area(
        "Bis zur n\u00E4chsten Stunde erledigen \u00B7 meine Aufgabe",
        placeholder="Meine Vorbereitung, Noten oder organisatorische Punkte",
        height=82,
        key="transfer_vorbereitung",
    )
    return neue_hausaufgabe, neue_besprechung

def zeige_lobbereich():
    kompakt_titel("04 \u00B7 W\u00FCrdigung", "Lobk\u00E4rtchen f\u00FCr das Kind")
    lob_vergeben = st.checkbox(
        "Lobk\u00E4rtchen jetzt erstellen",
        key="lob_vergeben",
    )
    if lob_vergeben:
        grund = st.text_input(
            "Grund f\u00FCr das Lobk\u00E4rtchen",
            placeholder="Was ist heute besonders gut gelungen?",
            key="lob_grund",
        )
    else:
        grund = ""
    st.caption("Das Lobk\u00E4rtchen geh\u00F6rt ausschlie\u00DFlich zum Kind und wird direkt erstellt.")
    return lob_vergeben, grund

def speichere_zwischenstand(entwurf):
    daten_json = json.dumps(entwurf, ensure_ascii=False, sort_keys=True)
    st.session_state["aktueller_zwischenstand"] = entwurf
    if st.session_state.get("zwischenstand_hash") == daten_json:
        return st.session_state.get("zwischenstand_dauerhaft", False)

    zeitpunkt = datetime.datetime.now(ZoneInfo("Europe/Berlin"))
    st.session_state["zwischenstand_hash"] = daten_json
    st.session_state["zwischenstand_zeit"] = zeitpunkt
    dauerhaft = False

    if GSheetsConnection is not None:
        try:
            verbindung = st.connection("gsheets", type=GSheetsConnection)
            bisher = verbindung.read(worksheet="Unterrichtsarchiv", ttl=0)
            if bisher is None or bisher.empty:
                bisher = pd.DataFrame(
                    columns=["Sch\u00FCler", "Datum", "Status", "Gespeichert_am", "Daten_JSON"]
                )
            else:
                bisher = bisher.copy()
                for spalte in ["Sch\u00FCler", "Datum", "Status", "Gespeichert_am", "Daten_JSON"]:
                    if spalte not in bisher.columns:
                        bisher[spalte] = ""

            neue_zeile = {
                "Sch\u00FCler": entwurf["Sch\u00FCler"],
                "Datum": entwurf["Datum"],
                "Status": "Zwischenstand",
                "Gespeichert_am": zeitpunkt.isoformat(timespec="seconds"),
                "Daten_JSON": daten_json,
            }
            maske = (
                bisher["Sch\u00FCler"].fillna("").astype(str).eq(entwurf["Sch\u00FCler"])
                & bisher["Datum"].fillna("").astype(str).eq(entwurf["Datum"])
                & bisher["Status"].fillna("").astype(str).eq("Zwischenstand")
            )
            if maske.any():
                for spalte, wert in neue_zeile.items():
                    bisher.loc[maske, spalte] = wert
            else:
                bisher = pd.concat([bisher, pd.DataFrame([neue_zeile])], ignore_index=True)
            verbindung.update(worksheet="Unterrichtsarchiv", data=bisher)
            dauerhaft = True
        except Exception:
            dauerhaft = False

    st.session_state["zwischenstand_dauerhaft"] = dauerhaft
    return dauerhaft

def ist_gueltiger_cloud_link(link):
    try:
        adresse = urllib.parse.urlparse(str(link).strip())
        return adresse.scheme in {"http", "https"} and bool(adresse.netloc)
    except ValueError:
        return False

def zeige_mini_cockpit_starter(student, stundenende, noten_url, noten_titel):
    ende_text = stundenende.isoformat() if stundenende else ""
    parameter = {
        "mini": "1",
        "student": str(student),
        "ende": ende_text,
        "noten": noten_url,
        "embed": "true",
    }
    parameter_json = json.dumps(parameter, ensure_ascii=False)
    titel_json = json.dumps(noten_titel or "Noten", ensure_ascii=False)
    components.html(
        f"""
        <button id="mini-start" type="button">Mini-Cockpit f\u00FCr diese Noten \u00F6ffnen</button>
        <div id="mini-status"></div>
        <style>
            body {{ margin:0; font-family:Arial,sans-serif; background:transparent; }}
            #mini-start {{
                width:100%; min-height:42px; border:1px solid #17243b; border-radius:9px;
                background:#17243b; color:white; font-size:13px; font-weight:700; cursor:pointer;
            }}
            #mini-start:hover {{ background:#253653; border-color:#b8954b; }}
            #mini-status {{ color:#687386; font-size:10px; text-align:center; margin-top:3px; }}
        </style>
        <script>
            const params = {parameter_json};
            const noteTitle = {titel_json};
            const button = document.getElementById('mini-start');
            const status = document.getElementById('mini-status');
            button.addEventListener('click', async () => {{
                let parentUrl = document.referrer || '';
                try {{
                    if (!parentUrl && window.parent.location.href) parentUrl = window.parent.location.href;
                }} catch (error) {{}}
                const baseUrl = parentUrl.split('?')[0].split('#')[0];
                const miniUrl = baseUrl + '?' + new URLSearchParams(params).toString();
                try {{
                    const host = window.parent;
                    if (host.documentPictureInPicture) {{
                        const pip = await host.documentPictureInPicture.requestWindow({{width:420,height:720}});
                        pip.document.title = 'Mini-Cockpit \u00B7 ' + noteTitle;
                        pip.document.body.style.margin = '0';
                        const frame = pip.document.createElement('iframe');
                        frame.src = miniUrl;
                        frame.style.cssText = 'width:100%;height:100vh;border:0;background:#f7f4ed';
                        pip.document.body.appendChild(frame);
                        status.textContent = 'Mini-Cockpit schwebt jetzt im Vordergrund.';
                        return;
                    }}
                }} catch (error) {{}}
                const popup = window.open(
                    miniUrl,
                    'MiniCockpit',
                    'width=430,height=740,resizable=yes,scrollbars=yes'
                );
                status.textContent = popup
                    ? 'Mini-Cockpit ge\u00F6ffnet. Dort jetzt die Noten gro\u00DF \u00F6ffnen.'
                    : 'Das Mini-Cockpit wurde vom Browser blockiert.';
            }});
        </script>
        """,
        height=62,
    )

def zeige_mini_cockpit(student, stundenende, noten_url):
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"], [data-testid="collapsedControl"] { display:none !important; }
            .block-container { max-width:430px !important; padding:.7rem .7rem 1rem !important; }
            header[data-testid="stHeader"] { display:none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    ende_anzeige = stundenende.strftime("%H:%M Uhr") if stundenende else "nicht festgelegt"
    st.markdown(
        f"""
        <div class="mini-shell">
            <div class="mini-kicker">Reduziertes Unterrichts-Cockpit</div>
            <div class="mini-student">{html.escape(str(student))}</div>
            <div class="mini-info">Stundenende: {html.escape(ende_anzeige)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if stundenende:
        ende_json = json.dumps(stundenende.isoformat())
        components.html(
            f"""
            <div class="timer"><span>Verbleibende Unterrichtszeit</span><strong id="restzeit">--:--</strong></div>
            <style>
                body {{ margin:0; font-family:Arial,sans-serif; background:transparent; }}
                .timer {{ display:flex; justify-content:space-between; align-items:center; padding:8px 12px;
                    background:#f6ecd4; border:1px solid #d8bd7e; border-radius:10px; color:#17243b; }}
                .timer span {{ font-size:12px; font-weight:700; }}
                .timer strong {{ font-size:22px; }}
            </style>
            <script>
                const ende = new Date({ende_json});
                function aktualisieren() {{
                    const sekunden = Math.max(0, Math.floor((ende - new Date()) / 1000));
                    const minuten = Math.floor(sekunden / 60);
                    const rest = String(sekunden % 60).padStart(2, '0');
                    document.getElementById('restzeit').textContent = minuten + ':' + rest;
                }}
                aktualisieren(); setInterval(aktualisieren, 1000);
            </script>
            """,
            height=52,
        )

    if ist_gueltiger_cloud_link(noten_url):
        st.markdown(
            f'<a class="mini-note-link" href="{html.escape(noten_url, quote=True)}" '
            f'target="_blank" rel="noopener">Noten erneut gro\u00DF \u00F6ffnen</a>',
            unsafe_allow_html=True,
        )

    kurznotiz = st.text_area(
        "Kurze Unterrichtsnotiz",
        height=95,
        key="mini_kurznotiz",
    )
    bis_naechstes_mal = st.text_area(
        "Aufgabe bis zur n\u00E4chsten Stunde",
        height=95,
        key="mini_bis_naechstes_mal",
    )
    programm_angemeldet = st.checkbox(
        "Konzertprogramm ist angemeldet",
        key="mini_programm_angemeldet",
    )

    if st.button(
        "Schnelleintrag speichern",
        type="primary",
        use_container_width=True,
        key="mini_schnelleintrag_speichern",
    ):
        zeitpunkt = datetime.datetime.now(ZoneInfo("Europe/Berlin"))
        mini_eintrag = {
            "Datum": zeitpunkt.strftime("%Y-%m-%d"),
            "Uhrzeit": zeitpunkt.strftime("%H:%M:%S"),
            "Sch\u00FCler": str(student),
            "Status": "Mini-Cockpit",
            "Programm_Angemeldet": "Ja" if programm_angemeldet else "Nein",
            "Bis_Naechsten_Mal": bis_naechstes_mal.strip(),
            "Kurznotiz": kurznotiz.strip(),
            "Eintragsart": "Mini-Cockpit",
        }
        dauerhaft = speichere_unterrichtspaket(mini_eintrag, [])
        if dauerhaft:
            st.success("Der Schnelleintrag wurde im Unterrichtsarchiv gespeichert.")
        else:
            st.warning("Der Schnelleintrag ist in dieser Sitzung gesichert; Google Sheets war nicht erreichbar.")

# --- DATEN-LOGIK ---
def lade_archiv_aus_sheet():
    daten = {
        'Schueler': ['Emma', 'Max', 'Lina'],
        'Stueck': ['Sonatine Opus 36', 'F\u00FCr Elise', 'Inventio 1'],
        'Konzertstueck': ['Sonatine 1. Satz', 'F\u00FCr Elise', 'Inventio 1'],
        'Dauer_Minuten': [45, 60, 30],
        'Schwierigkeit': [3, 4, 2],
        'K\u00E4rtchen_Erhalten': ['Ja', 'Nein', 'Ja'],
        'Grund': ['Toller Rhythmus im Takt 12', '', 'Wundersch\u00F6ne Dynamik'],
        'Bis_Naechsten_Mal': ['Takt 15-20 langsam \u00FCben', 'Pedalwechsel weicher gestalten', 'Rhythmus klatschen']
    }
    return pd.DataFrame(daten)

def hole_konzertprogramm(student, archiv):
    auswahl = archiv.loc[archiv["Schueler"] == student, "Konzertstueck"].dropna()
    auswahl = [str(stueck).strip() for stueck in auswahl if str(stueck).strip()]
    if not auswahl:
        return "Noch nicht festgelegt"
    return " \u00B7 ".join(dict.fromkeys(auswahl))

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
        return f"Pause \u00B7 {stunden} Std. {rest} Min."
    return f"Pause \u00B7 {minuten} Min."

def erstelle_tagesleisten_html(termine, jetzt=None):
    if termine is None:
        return '<div class="rail-empty">Die Tagesleiste erscheint hier, sobald der Google Kalender verbunden ist.</div>'

    if not termine:
        return '<div class="rail-empty"><strong>Heute keine Termine.</strong><br>Zeit f\u00FCr freie Improvisation.</div>'

    jetzt = jetzt or datetime.datetime.now(ZoneInfo("Europe/Berlin"))
    sortierte_termine = sorted(termine, key=lambda termin: termin["start"])
    verbleibende_termine = [termin for termin in sortierte_termine if termin["ende"] > jetzt]

    if not verbleibende_termine:
        return '<div class="rail-empty"><strong>Feierabend!</strong><br>Auch der Fl\u00FCgel hat jetzt frei.</div>'

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
        zeit = f'{termin["start"].strftime("%H:%M")}\u2013{termin["ende"].strftime("%H:%M")} Uhr'
        bausteine.append(
            f'<div class="rail-entry {status}"><div class="rail-dot"></div>'
            f'<div class="rail-card"><div class="rail-time">{zeit}</div>'
            f'<div class="rail-name">{name}</div></div></div>'
        )
        vorheriges_ende = termin["ende"]

    feierabend_zeit = sortierte_termine[-1]["ende"].strftime("%H:%M")
    bausteine.append(
        '<div class="rail-entry finish"><div class="rail-dot"></div>'
        f'<div class="rail-card"><div class="rail-time">ab {feierabend_zeit} Uhr</div>'
        '<div class="rail-name">Feierabend</div></div></div>'
    )
    bausteine.append("</div>")
    return "".join(bausteine)

def formatiere_naechsten_termin(termin, kalender_verbunden=False):
    if not termin and not kalender_verbunden:
        return "Noch nicht verbunden", "Google Kalender wird im n\u00E4chsten Schritt angeschlossen"
    if not termin:
        return "Heute niemand mehr", "Feierabend \u2013 auch der Fl\u00FCgel hat jetzt frei"

    name = termin.get("name", "Unbekannt")
    start = termin.get("start")
    if not start:
        return name, "Uhrzeit nicht verf\u00FCgbar"

    jetzt = datetime.datetime.now(start.tzinfo) if start.tzinfo else datetime.datetime.now()
    minuten_bis_start = max(0, int((start - jetzt).total_seconds() // 60))
    if minuten_bis_start >= 60:
        stunden, minuten = divmod(minuten_bis_start, 60)
        abstand = f"in {stunden} Std. {minuten} Min."
    else:
        abstand = f"in {minuten_bis_start} Minuten"
    return f"{name} \u00B7 {start.strftime('%H:%M')} Uhr", abstand

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
    
    lob = df_archiv[(df_archiv['Schueler'] == student) & (df_archiv['K\u00E4rtchen_Erhalten'] == 'Ja')]
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

mini_modus = hole_query_parameter("mini", "0") == "1"

if mini_modus:
    student = hole_query_parameter("student", st.session_state.get("aktueller_student", "Sch\u00FCler"))
    unterrichtsdatum = datetime.date.today()
    ende_parameter = hole_query_parameter("ende", "")
    try:
        stundenende = datetime.datetime.fromisoformat(ende_parameter) if ende_parameter else None
        if stundenende and stundenende.tzinfo is None:
            stundenende = stundenende.replace(tzinfo=ZoneInfo("Europe/Berlin"))
    except ValueError:
        stundenende = None
    dauer_minuten = max(
        0,
        int((stundenende - jetzt).total_seconds() // 60) if stundenende else 0,
    )
else:
    with st.sidebar:
        st.markdown('<div class="day-label">Tages\u00FCbersicht</div>', unsafe_allow_html=True)
        st.markdown('<div class="day-title">Heute im Unterricht</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="day-date">{datetime.date.today().strftime("%d.%m.%Y")}</div>', unsafe_allow_html=True)
        st.markdown(erstelle_tagesleisten_html(heutige_termine, jetzt), unsafe_allow_html=True)

        if erkennter_schueler:
            student = erkennter_schueler
            unterrichtsdatum = datetime.date.today()
            dauer_minuten = int((aktueller_termin["ende"] - aktueller_termin["start"]).total_seconds() // 60)
            stundenende = aktueller_termin["ende"]
            st.success(f"Aktuell: {student}")
            fortschritt = (jetzt - aktueller_termin["start"]).total_seconds() / (aktueller_termin["ende"] - aktueller_termin["start"]).total_seconds()
            st.progress(min(max(fortschritt, 0.0), 1.0), text=f'{aktueller_termin["start"].strftime("%H:%M")}\u2013{aktueller_termin["ende"].strftime("%H:%M")} Uhr')
        else:
            with st.expander("Sch\u00FCler manuell ausw\u00E4hlen", expanded=heutige_termine is None):
                student = st.selectbox("Sch\u00FCler", schueler_liste, label_visibility="collapsed")
                unterrichtsdatum = st.date_input("Datum", value=datetime.date.today(), format="DD.MM.YYYY")
                dauer_minuten = st.selectbox("Dauer", [30, 45, 60], index=1, format_func=lambda x: f"{x} Minuten")
            stundenende = jetzt + datetime.timedelta(minutes=int(dauer_minuten))
            st.caption("Die manuelle Auswahl wird nur ben\u00F6tigt, wenn gerade kein Kalendertermin l\u00E4uft.")

    st.session_state["aktueller_student"] = str(student)
    st.session_state["unterrichtsende"] = stundenende.isoformat() if stundenende else ""

if mini_modus:
    zeige_mini_cockpit(
        student,
        stundenende,
        hole_query_parameter("noten", ""),
    )
    st.stop()

# --- UI NAVIGATION ---
aktive_ansicht = hole_aktive_ansicht()
navigation = [
    ("live", "Live-Cockpit"),
    ("analyse", "Analyse & Fortschritt"),
    ("zertifikate", "Zertifikate & TaskCards"),
]
navigation_html = '<nav class="cockpit-nav" aria-label="Hauptnavigation">'
for ansicht_id, beschriftung in navigation:
    aktive_klasse = " active" if ansicht_id == aktive_ansicht else ""
    navigation_html += (
        f'<a class="{aktive_klasse.strip()}" href="?ansicht={ansicht_id}" target="_self">'
        f'{html.escape(beschriftung)}</a>'
    )
navigation_html += "</nav>"
st.markdown(navigation_html, unsafe_allow_html=True)

if aktive_ansicht == "live":
    konzertprogramm = hole_konzertprogramm(student, df_archiv)
    st.markdown(
        f"""
        <div class="tablet-overview">
            <div class="tablet-brand">
                <div class="tablet-kicker">Digitales Unterrichtsstudio</div>
                <div class="tablet-title">Klavierlehrer Live-Cockpit</div>
                <div class="tablet-note">Klassenvorspiel am 02.09.2026</div>
            </div>
            <div class="tablet-fact">
                <div class="tablet-label">Aktueller Sch\u00FCler</div>
                <div class="tablet-value">{html.escape(str(student))}</div>
                <div class="tablet-note">{unterrichtsdatum.strftime('%d.%m.%Y')} \u00B7 {dauer_minuten} Minuten</div>
            </div>
            <div class="tablet-fact">
                <div class="tablet-label">Konzertprogramm</div>
                <div class="tablet-value">{html.escape(konzertprogramm)}</div>
                <div class="tablet-note">{html.escape(berechne_konzert_countdown())}</div>
            </div>
            <div class="tablet-fact">
                <div class="tablet-label">N\u00E4chster Sch\u00FCler</div>
                <div class="tablet-value">{html.escape(naechster_titel)}</div>
                <div class="tablet-note">{html.escape(naechster_hinweis)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    technik_spalte, repertoire_spalte = st.columns([0.93, 1.07])
    with technik_spalte:
        with st.container(border=True):
            modus, speicher_text = zeige_technikbereich()
    with repertoire_spalte:
        with st.container(border=True):
            repertoire_eintraege = zeige_repertoirebereich(student, stundenende)

    transfer_spalte, lob_spalte = st.columns([1, 1])
    with transfer_spalte:
        with st.container(border=True):
            neue_hausaufgabe, neue_besprechung = zeige_transferbereich()
    with lob_spalte:
        with st.container(border=True):
            lob_vergeben, grund = zeige_lobbereich()

    entwurf = {
        "Sch\u00FCler": str(student),
        "Datum": unterrichtsdatum.strftime("%Y-%m-%d"),
        "Dauer_Minuten": int(dauer_minuten),
        "Technik_Bereich": modus,
        "Technik_Details": speicher_text,
        "Repertoire": repertoire_eintraege,
        "Hausaufgabe": neue_hausaufgabe.strip(),
        "Bis_zur_n\u00E4chsten_Stunde": neue_besprechung.strip(),
        "Lobk\u00E4rtchen_Erhalten": "Ja" if lob_vergeben else "Nein",
        "Lob_Grund": grund.strip(),
        "F\u00FCr_TaskCards": "Ja" if lob_vergeben else "Nein",
    }
    zwischenstand_dauerhaft = speichere_zwischenstand(entwurf)
    zwischenstand_zeit = st.session_state.get("zwischenstand_zeit", jetzt)

    with st.container(key="save_bar"):
        speichern_geklickt = st.button(
            "Unterrichtseintrag speichern",
            type="primary",
            use_container_width=True,
            key="unterrichtseintrag_speichern",
        )
        speicherort = "Google Sheets" if zwischenstand_dauerhaft else "dieser Sitzung"
        st.markdown(
            f'<div class="autosave-status">Zwischenstand automatisch um '
            f'{zwischenstand_zeit.strftime("%H:%M:%S")} Uhr in {speicherort} gesichert</div>',
            unsafe_allow_html=True,
        )

    if speichern_geklickt:
        unvollstaendige_stuecke = [
            eintrag
            for eintrag in repertoire_eintraege
            if not eintrag["Titel"] and (eintrag["Komponist"] or eintrag["Cloud-Link"])
        ]
        if unvollstaendige_stuecke:
            st.error("Bitte erg\u00E4nze bei jedem ausgef\u00FCllten St\u00FCck noch den Titel.")
        else:
            repertoire_zum_speichern = [
                eintrag for eintrag in repertoire_eintraege if eintrag["Titel"]
            ]
            archiv_zeile = {
                "Sch\u00FCler": str(student),
                "Datum": unterrichtsdatum.strftime("%Y-%m-%d"),
                "Status": "Abgeschlossen",
                "Dauer_Minuten": int(dauer_minuten),
                "Technik_Bereich": modus,
                "Technik_Details": speicher_text,
                "St\u00FCcke": " \u00B7 ".join(
                    eintrag["Titel"] for eintrag in repertoire_zum_speichern
                ),
                "Hausaufgabe": neue_hausaufgabe.strip(),
                "Bis_zur_n\u00E4chsten_Stunde": neue_besprechung.strip(),
                "Lobk\u00E4rtchen_Erhalten": "Ja" if lob_vergeben else "Nein",
                "Lob_Grund": grund.strip(),
                "F\u00FCr_TaskCards": "Ja" if lob_vergeben else "Nein",
            }
            dauerhaft_gespeichert = speichere_unterrichtspaket(
                archiv_zeile,
                repertoire_zum_speichern,
            )
            st.success(
                f"Unterrichtseintrag f\u00FCr {student} am "
                f"{unterrichtsdatum.strftime('%d.%m.%Y')} wurde gespeichert."
            )
            if dauerhaft_gespeichert:
                st.caption(
                    "Technik, Aufgaben und Lob wurden in Google Sheets im Blatt "
                    "Unterrichtsarchiv gespeichert; "
                    f"{len(repertoire_zum_speichern)} St\u00FCck(e) wurden mit Cloud-Link, "
                    "Verwendung und Anmeldestatus im Blatt Repertoire gespeichert."
                )
            else:
                st.warning(
                    "Der Eintrag ist im ge\u00F6ffneten Cockpit gesichert, konnte aber nicht "
                    "dauerhaft an Google Sheets \u00FCbertragen werden. Bitte pr\u00FCfe die "
                    "eingerichtete gsheets-Verbindung und das Zusatzpaket streamlit-gsheets."
                )

elif aktive_ansicht == "analyse":
    st.markdown("## Analyse & Fortschritt")
    st.caption(f"Entwicklung und Jahres\u00FCberblick f\u00FCr {student}")

    verlauf_daten = pd.DataFrame(
        {
            "Datum": ["2026-01-10", "2026-03-15", "2026-05-05", "2026-07-20", "2026-08-18"],
            "Tempo": [60, 72, 90, 110, 128],
            "Tonart": ["C-Dur"] * 5,
        }
    )
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Archivierte Eintr\u00E4ge", len(df_archiv[df_archiv["Schueler"] == student]))
    kpi2.metric("Aktuelles Tempo", "128 BPM", "+18 BPM")
    kpi3.metric("Erarbeitete St\u00FCcke", df_archiv[df_archiv["Schueler"] == student]["Stueck"].nunique())
    kpi4.metric("Lobk\u00E4rtchen", len(df_archiv[(df_archiv["Schueler"] == student) & (df_archiv["K\u00E4rtchen_Erhalten"] == "Ja")]))

    abschnitt("Jahresverlauf", "Tempo-Entwicklung", "Die Beispielkurve wird nach der Google-Sheets-Anbindung automatisch aus den Unterrichtseintr\u00E4gen gespeist.")
    fig = px.line(verlauf_daten, x="Datum", y="Tempo", markers=True)
    fig.update_traces(line_color="#b8954b", line_width=3, marker=dict(size=9, color="#17243b"))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,253,248,.7)",
        font=dict(family="DM Sans", color="#263247"),
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title=None,
        yaxis_title="Tempo \u00B7 BPM",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    abschnitt("Archiv", "Alle Unterrichtseintr\u00E4ge", "Durchsuche und kontrolliere die bisher erfassten Daten.")
    st.dataframe(df_archiv, use_container_width=True, hide_index=True)

elif aktive_ansicht == "zertifikate":
    st.markdown("## Zertifikate & TaskCards")
    st.caption(f"Pers\u00F6nlicher Jahresabschluss 2026 f\u00FCr {student}")

    info_col, action_col = st.columns([1.35, 1])
    with info_col:
        abschnitt("Jahreszertifikat", "Fortschritt sichtbar w\u00FCrdigen", "Das Zertifikat b\u00FCndelt erarbeitete St\u00FCcke und besondere Erfolge aus dem Archiv.")
        st.info("Vor der Erstellung kannst du die Eintr\u00E4ge im Analyse-Tab noch einmal kontrollieren.")
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
            whatsapp_text = f"Hallo! Hier ist das Jahres-Zertifikat {aktuelles_jahr} f\u00FCr {student} aus der Klavierstunde."
            whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(whatsapp_text)}"
            st.link_button("\u00DCber WhatsApp teilen", whatsapp_url, use_container_width=True)





#________________________ALTE VERSION___________________________________________
# Klavierlehrer Live-Cockpit
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import datetime
import html
import json
import plotly.express as px
from zoneinfo import ZoneInfo
from fpdf import FPDF
import urllib.parse

try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    GSheetsConnection = None

# --- SETUP & DESIGN-KONFIGURATION ---
st.set_page_config(page_title="Klavierlehrer Cockpit", layout="wide", page_icon="\U0001F3B9")

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
    .block-container { max-width: 1280px; padding-top: .7rem; padding-bottom: 1.2rem; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: var(--navy) !important; }
    .cockpit-nav {
        display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px;
        background:#fffdf8; padding:7px; margin:0 0 14px;
        border:1px solid var(--line); border-radius:14px;
        box-shadow:0 8px 24px rgba(23,36,59,.08);
    }
    .cockpit-nav a {
        display:flex; align-items:center; justify-content:center; min-height:52px;
        padding:10px 14px; border:2px solid #cfc5b3; border-radius:9px;
        background:#f7f4ed !important; color:#17243b !important;
        font-family:'DM Sans',sans-serif !important; font-size:16px !important;
        font-weight:800 !important; line-height:1.2 !important; text-align:center;
        text-decoration:none !important; opacity:1 !important;
    }
    .cockpit-nav a:visited { color:#17243b !important; }
    .cockpit-nav a:hover {
        background:#eee8dc !important; border-color:var(--gold);
        color:#17243b !important; text-decoration:none !important;
    }
    .cockpit-nav a.active,
    .cockpit-nav a.active:visited,
    .cockpit-nav a.active:hover {
        background:#17243b !important; border-color:#17243b !important;
        color:#ffffff !important; box-shadow:0 5px 14px rgba(23,36,59,.2);
    }
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
    .hero:after { content:'\u266A'; position:absolute; right:28px; top:-28px; font-size:130px; color:rgba(230,212,167,.12); }
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
    .repertoire-hint {
        color:var(--muted); font-size:13px; margin:-3px 0 12px;
    }
    .tablet-overview {
        display:grid; grid-template-columns:1.35fr 1fr 1.2fr 1.1fr; gap:8px;
        background:linear-gradient(125deg,#17243b,#2d4260); color:#fff;
        padding:10px; border-radius:15px; margin:0 0 10px;
        box-shadow:0 10px 26px rgba(23,36,59,.16);
    }
    .tablet-brand, .tablet-fact {
        min-width:0; padding:10px 12px; border-radius:10px;
    }
    .tablet-brand { background:rgba(255,255,255,.06); }
    .tablet-fact { background:rgba(255,255,255,.1); }
    .tablet-kicker, .tablet-label {
        color:#e6d4a7; text-transform:uppercase; letter-spacing:.08em;
        font-size:9px; font-weight:800;
    }
    .tablet-title {
        color:#fff; font-family:'Playfair Display',serif; font-size:20px;
        font-weight:700; line-height:1.1; margin-top:3px;
    }
    .tablet-value {
        color:#fff; font-size:15px; font-weight:800; line-height:1.15;
        margin-top:4px; overflow-wrap:anywhere;
    }
    .tablet-note { color:#dfe5ec; font-size:10px; line-height:1.2; margin-top:3px; }
    .compact-head { margin:4px 0 8px; }
    .compact-kicker {
        color:var(--gold); font-size:10px; font-weight:800;
        letter-spacing:.1em; text-transform:uppercase;
    }
    .compact-title {
        color:var(--navy); font-family:'Playfair Display',serif;
        font-size:20px; font-weight:700; line-height:1.15;
    }
    .st-key-save_bar {
        position:sticky; bottom:0; z-index:50; background:rgba(247,244,237,.96);
        border-top:1px solid var(--line); padding:8px 0 5px;
        backdrop-filter:blur(8px);
    }
    .autosave-status {
        color:var(--muted); font-size:11px; text-align:center; margin-top:2px;
    }
    .notes-links { display:flex; flex-wrap:wrap; gap:6px; margin:6px 0 2px; }
    .notes-links a {
        background:#eef1f5; border:1px solid #cbd3dd; border-radius:8px;
        color:#17243b !important; font-size:11px; font-weight:800;
        padding:6px 9px; text-decoration:none !important;
    }
    .notes-links a:hover { border-color:var(--gold); background:#fffdf8; }
    .mini-shell {
        background:linear-gradient(145deg,#17243b,#2c4261); color:#fff;
        border-radius:16px; padding:16px 18px; margin-bottom:10px;
        box-shadow:0 10px 26px rgba(23,36,59,.2);
    }
    .mini-kicker {
        color:#e6d4a7; text-transform:uppercase; letter-spacing:.1em;
        font-size:10px; font-weight:800;
    }
    .mini-student {
        color:#fff; font-family:'Playfair Display',serif;
        font-size:26px; font-weight:700; margin-top:2px;
    }
    .mini-info { color:#dfe5ec; font-size:12px; margin-top:3px; }
    .mini-note-link {
        display:block; background:#f6ecd4; border:1px solid #d8bd7e;
        border-radius:10px; color:#17243b !important; font-weight:800;
        padding:10px 12px; margin:8px 0 12px; text-align:center;
        text-decoration:none !important;
    }
    [data-testid="stSidebar"] {
        background:#e8edf4; border-right:1px solid #d5dce6;
        width:225px !important; min-width:225px !important; max-width:225px !important;
    }
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
    .rail-entry.finish .rail-dot { background:#b8954b; border-color:#b8954b; }
    .rail-entry.finish .rail-card { background:#f6ecd4; border-color:#d8bd7e; }
    .rail-entry.finish .rail-time { color:#8b6c2f; }
    .rail-entry.finish .rail-name { color:#17243b; }
    .rail-entry.past { opacity:.53; }
    .rail-gap { position:relative; margin:0 0 12px 29px; color:#687386; font-size:10px; font-weight:700; }
    .rail-gap span { background:#dbe2eb; border-radius:20px; padding:4px 8px; }
    .rail-empty { background:rgba(255,255,255,.62); border:1px dashed #aeb9c7; border-radius:10px; padding:12px; color:#687386; font-size:12px; }
    [data-testid="stMetric"] {
        background:rgba(255,253,248,.9); border:1px solid var(--line); padding:15px 17px;
        border-radius:12px; box-shadow:0 6px 16px rgba(23,36,59,.045);
    }
    /* Edle Box f\u00FCr das Lobk\u00E4rtchen */
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
        .cockpit-nav { gap:5px; padding:5px; }
        .cockpit-nav a {
            min-height:58px; padding:8px 6px; font-size:12px !important;
            line-height:1.18 !important;
        }
        .block-container { padding:.45rem .55rem 4.5rem; }
        .tablet-overview { grid-template-columns:repeat(3,minmax(0,1fr)); gap:5px; padding:6px; }
        .tablet-brand { grid-column:1 / -1; }
        .tablet-brand, .tablet-fact { padding:7px 8px; }
        .tablet-title { font-size:18px; }
        .tablet-value { font-size:13px; }
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
    """Platzhalter f\u00FCr die sp\u00E4tere automatische Kalender-/Zeiterkennung."""
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

def hole_query_parameter(name, standard=""):
    try:
        wert = st.query_params.get(name, standard)
    except AttributeError:
        wert = st.experimental_get_query_params().get(name, [standard])
    if isinstance(wert, list):
        return wert[0] if wert else standard
    return wert

def hole_aktive_ansicht():
    """Liest die gewÃ¤hlte Hauptansicht aus der URL und bleibt abwÃ¤rtskompatibel."""
    ansicht = hole_query_parameter("ansicht", "live")
    return ansicht if ansicht in {"live", "analyse", "zertifikate"} else "live"

REPERTOIRE_SPALTEN = [
    "Titel",
    "Komponist",
    "Cloud-Link",
    "Verwendung",
    "Programm angemeldet",
]

def leere_repertoire_tabelle(anzahl=2):
    return pd.DataFrame(
        [
            {
                "Titel": "",
                "Komponist": "",
                "Cloud-Link": "",
                "Verwendung": "Unterricht",
                "Programm angemeldet": False,
            }
            for _ in range(anzahl)
        ],
        columns=REPERTOIRE_SPALTEN,
    )

def weiteres_stueck_hinzufuegen():
    anzahl = min(7, st.session_state.anzahl_stuecke + 1)
    tabelle = st.session_state.get(
        "repertoire_tabelle",
        leere_repertoire_tabelle(st.session_state.anzahl_stuecke),
    ).copy()
    if len(tabelle) < anzahl:
        tabelle = pd.concat([tabelle, leere_repertoire_tabelle(1)], ignore_index=True)
    st.session_state.repertoire_tabelle = tabelle.iloc[:anzahl].reset_index(drop=True)
    st.session_state.anzahl_stuecke = anzahl

def letztes_stueck_entfernen():
    anzahl = max(2, st.session_state.anzahl_stuecke - 1)
    tabelle = st.session_state.get(
        "repertoire_tabelle",
        leere_repertoire_tabelle(st.session_state.anzahl_stuecke),
    ).copy()
    st.session_state.repertoire_tabelle = tabelle.iloc[:anzahl].reset_index(drop=True)
    st.session_state.anzahl_stuecke = anzahl

def aktualisiere_repertoire_tabelle(bestehende_daten, neue_zeilen):
    spalten = [
        "SchÃ¼ler",
        "Titel",
        "Komponist",
        "Cloud-Link",
        "Verwendung",
        "Programm angemeldet",
    ]
    if bestehende_daten is None or bestehende_daten.empty:
        bestehende_daten = pd.DataFrame(columns=spalten)
    else:
        bestehende_daten = bestehende_daten.copy()
        for spalte in spalten:
            if spalte not in bestehende_daten.columns:
                bestehende_daten[spalte] = ""

    for neue_zeile in neue_zeilen:
        maske = (
            bestehende_daten["SchÃ¼ler"].fillna("").astype(str).str.casefold().eq(neue_zeile["SchÃ¼ler"].casefold())
            & bestehende_daten["Titel"].fillna("").astype(str).str.casefold().eq(neue_zeile["Titel"].casefold())
            & bestehende_daten["Komponist"].fillna("").astype(str).str.casefold().eq(neue_zeile["Komponist"].casefold())
        )
        if maske.any():
            for spalte in spalten:
                bestehende_daten.loc[maske, spalte] = neue_zeile[spalte]
        else:
            bestehende_daten = pd.concat(
                [bestehende_daten, pd.DataFrame([neue_zeile], columns=spalten)],
                ignore_index=True,
            )
    return bestehende_daten[spalten]

def speichere_in_google_sheets(archiv_zeile, repertoire_zeilen):
    if GSheetsConnection is None:
        return False

    try:
        verbindung = st.connection("gsheets", type=GSheetsConnection)

        archiv_bisher = verbindung.read(worksheet="Unterrichtsarchiv", ttl=0)
        if archiv_bisher is None:
            archiv_bisher = pd.DataFrame()
        archiv_bisher = archiv_bisher.copy()
        for spalte in ["Sch\u00FCler", "Datum", "Status"]:
            if spalte not in archiv_bisher.columns:
                archiv_bisher[spalte] = ""
        if archiv_zeile.get("Status") == "Abgeschlossen":
            entwurf_maske = (
                archiv_bisher["Sch\u00FCler"].fillna("").astype(str).eq(archiv_zeile["Sch\u00FCler"])
                & archiv_bisher["Datum"].fillna("").astype(str).eq(archiv_zeile["Datum"])
                & archiv_bisher["Status"].fillna("").astype(str).eq("Zwischenstand")
            )
            archiv_bisher = archiv_bisher.loc[~entwurf_maske].copy()
        archiv_aktuell = pd.concat(
            [archiv_bisher, pd.DataFrame([archiv_zeile])],
            ignore_index=True,
        )
        verbindung.update(worksheet="Unterrichtsarchiv", data=archiv_aktuell)

        if repertoire_zeilen:
            repertoire_bisher = verbindung.read(worksheet="Repertoire", ttl=0)
            repertoire_aktuell = aktualisiere_repertoire_tabelle(
                repertoire_bisher,
                repertoire_zeilen,
            )
            verbindung.update(worksheet="Repertoire", data=repertoire_aktuell)
        return True
    except Exception:
        return False

def speichere_unterrichtspaket(archiv_zeile, repertoire_zeilen):
    """HÃ¤lt Archiv und Repertoire getrennt und schreibt sie in ihre ZielblÃ¤tter."""
    st.session_state.setdefault("Unterrichtsarchiv", []).append(archiv_zeile)
    repertoire_speicher = st.session_state.setdefault("Repertoire", [])

    for neue_zeile in repertoire_zeilen:
        vorhandene_zeile = next(
            (
                zeile
                for zeile in repertoire_speicher
                if zeile["SchÃ¼ler"] == neue_zeile["SchÃ¼ler"]
                and zeile["Titel"].casefold() == neue_zeile["Titel"].casefold()
                and zeile["Komponist"].casefold() == neue_zeile["Komponist"].casefold()
            ),
            None,
        )
        if vorhandene_zeile:
            vorhandene_zeile.update(neue_zeile)
        else:
            repertoire_speicher.append(neue_zeile)

    st.session_state["letzter_unterrichtseintrag"] = {
        "Unterrichtsarchiv": archiv_zeile,
        "Repertoire": repertoire_zeilen,
    }
    return speichere_in_google_sheets(archiv_zeile, repertoire_zeilen)

def kompakt_titel(nummer, titel):
    st.markdown(
        f'<div class="compact-head"><div class="compact-kicker">{html.escape(nummer)}</div>'
        f'<div class="compact-title">{html.escape(titel)}</div></div>',
        unsafe_allow_html=True,
    )

def zeige_technikbereich():
    kompakt_titel("01 \u00B7 Technik", "\u00DCbungs- und Technikbereich")
    modus = st.radio(
        "Bereich",
        ["Tastenforscher", "Klassische Tonleitern", "Fortgeschrittene Et\u00FCden"],
        horizontal=True,
        key="technik_modus",
    )

    if modus == "Tastenforscher":
        titel_spalte, seiten_spalte = st.columns([1.35, 0.65])
        with titel_spalte:
            heft_titel = st.text_input(
                "Titel der \u00DCbung",
                value="Tastenforscher",
                key="technik_heft_titel",
            )
        with seiten_spalte:
            seiten_zahl = st.text_input(
                "Seite",
                placeholder="12\u201313",
                key="technik_heft_seite",
            )
        heft_link = st.text_input(
            "Cloud-Link zu den Noten",
            placeholder="Link einf\u00FCgen",
            key="technik_heft_link",
        )
        return modus, (
            f"Tastenforscher: {heft_titel}, {seiten_zahl or 'ohne Seitenangabe'}"
            f" \u00B7 Cloud-Link: {heft_link or 'nicht hinterlegt'}"
        )

    if modus == "Klassische Tonleitern":
        tonart_spalte, spielart_spalte = st.columns([0.9, 1.1])
        with tonart_spalte:
            tonleiter_text = st.text_input(
                "Tonart oder Tonleiter",
                placeholder="z. B. C-Dur",
                key="technik_tonleiter",
            )
        with spielart_spalte:
            bewegung_wahl = st.selectbox(
                "Spielart",
                ["Parallelbewegung", "Gegenbewegung"],
                key="technik_spielart",
            )
        tempo_wahl = st.slider(
            "Tempo",
            min_value=40,
            max_value=200,
            value=80,
            step=2,
            format="%d BPM",
            key="technik_tonleiter_tempo",
        )
        return modus, (
            f"Tonleiter: {tonleiter_text or 'ohne Tonart'} \u00B7 "
            f"{bewegung_wahl} \u00B7 {tempo_wahl} BPM"
        )

    titel_spalte, komponist_spalte = st.columns(2)
    with titel_spalte:
        etuede_titel = st.text_input(
            "Et\u00FCde oder Name",
            placeholder="z. B. Et\u00FCde Nr. 6",
            key="technik_etuede_titel",
        )
    with komponist_spalte:
        komponist = st.text_input(
            "Komponist",
            placeholder="z. B. Czerny",
            key="technik_etuede_komponist",
        )
    opus_spalte, takte_spalte, tempo_spalte = st.columns([0.8, 1.1, 0.7])
    with opus_spalte:
        opus_nr = st.text_input(
            "Opus",
            placeholder="op. 299",
            key="technik_etuede_opus",
        )
    with takte_spalte:
        etuede_takte = st.text_input(
            "Takte",
            placeholder="1\u201332",
            key="technik_etuede_takte",
        )
    with tempo_spalte:
        etuede_tempo = st.number_input(
            "BPM",
            min_value=40,
            max_value=250,
            value=100,
            step=2,
            key="technik_etuede_tempo",
        )
    etuede_notizen = st.text_input(
        "Technische Beobachtung",
        placeholder="Fokus, Artikulation oder Bewegung",
        key="technik_etuede_notiz",
    )
    return modus, (
        f"Et\u00FCde: {etuede_titel or 'ohne Titel'} \u00B7 {komponist or 'ohne Komponist'} \u00B7 "
        f"{opus_nr or 'ohne Werknummer'} \u00B7 {etuede_takte or 'ohne Taktangabe'} \u00B7 "
        f"{etuede_tempo} BPM \u00B7 {etuede_notizen or 'ohne Beobachtung'}"
    )

def zeige_repertoirebereich(student, stundenende):
    kompakt_titel("02 \u00B7 Repertoire", "St\u00FCcke und Konzertziel")
    if "anzahl_stuecke" not in st.session_state:
        st.session_state.anzahl_stuecke = 2
    if "repertoire_tabelle" not in st.session_state:
        st.session_state.repertoire_tabelle = leere_repertoire_tabelle(2)

    anzahl = st.session_state.anzahl_stuecke
    tabelle = st.session_state.repertoire_tabelle.iloc[:anzahl].copy()
    while len(tabelle) < anzahl:
        tabelle = pd.concat([tabelle, leere_repertoire_tabelle(1)], ignore_index=True)

    bearbeitet = st.data_editor(
        tabelle,
        hide_index=True,
        use_container_width=True,
        height=min(315, 72 + anzahl * 35),
        key=f"repertoire_editor_{anzahl}",
        column_config={
            "Titel": st.column_config.TextColumn("Titel", width="medium"),
            "Komponist": st.column_config.TextColumn("Komponist", width="small"),
            "Cloud-Link": st.column_config.TextColumn(
                "Cloud-Link",
                width="medium",
                help="G\u00FCltigen Cloud-Link zu den Noten einf\u00FCgen.",
            ),
            "Verwendung": st.column_config.SelectboxColumn(
                "Verwendung",
                options=["Unterricht", "Konzertziel", "Unterricht & Konzert", "Wettbewerb"],
                width="medium",
                required=True,
            ),
            "Programm angemeldet": st.column_config.CheckboxColumn(
                "Angemeldet",
                width="small",
            ),
        },
    )
    st.session_state.repertoire_tabelle = bearbeitet.copy()

    knopf_hinzufuegen, knopf_entfernen = st.columns(2)
    with knopf_hinzufuegen:
        st.button(
            "Weiteres St\u00FCck",
            on_click=weiteres_stueck_hinzufuegen,
            disabled=anzahl >= 7,
            use_container_width=True,
            key="stueck_hinzufuegen",
        )
    with knopf_entfernen:
        st.button(
            "Letztes entfernen",
            on_click=letztes_stueck_entfernen,
            disabled=anzahl <= 2,
            use_container_width=True,
            key="stueck_entfernen",
        )
    st.caption(f"{anzahl} von maximal 7 St\u00FCcken \u00B7 zuerst Mini-Cockpit, danach Noten \u00F6ffnen")

    repertoire_eintraege = []
    noten_optionen = []
    for index, zeile in bearbeitet.iterrows():
        titel = "" if pd.isna(zeile["Titel"]) else str(zeile["Titel"]).strip()
        komponist = "" if pd.isna(zeile["Komponist"]) else str(zeile["Komponist"]).strip()
        cloud_link = "" if pd.isna(zeile["Cloud-Link"]) else str(zeile["Cloud-Link"]).strip()
        verwendung = "Unterricht" if pd.isna(zeile["Verwendung"]) else str(zeile["Verwendung"])
        ist_programmstueck = verwendung in {"Konzertziel", "Unterricht & Konzert", "Wettbewerb"}
        angemeldet = bool(zeile["Programm angemeldet"]) if not pd.isna(zeile["Programm angemeldet"]) else False
        repertoire_eintraege.append(
            {
                "Sch\u00FCler": str(student),
                "Titel": titel,
                "Komponist": komponist,
                "Cloud-Link": cloud_link,
                "Verwendung": verwendung,
                "Programm angemeldet": "Ja" if ist_programmstueck and angemeldet else "Nein",
            }
        )
        if ist_gueltiger_cloud_link(cloud_link):
            link_text = titel or f"St\u00FCck {index + 1}"
            noten_optionen.append(
                {
                    "Bezeichnung": f"{index + 1}. {link_text}",
                    "Titel": link_text,
                    "Link": cloud_link,
                }
            )

    if noten_optionen:
        auswahl = st.selectbox(
            "Noten f\u00FCr die Hochformat-Ansicht",
            options=list(range(len(noten_optionen))),
            format_func=lambda position: noten_optionen[position]["Bezeichnung"],
            key="noten_auswahl",
        )
        gewaehlte_noten = noten_optionen[auswahl]
        zeige_mini_cockpit_starter(
            student,
            stundenende,
            gewaehlte_noten["Link"],
            gewaehlte_noten["Titel"],
        )
    return repertoire_eintraege

def zeige_transferbereich():
    kompakt_titel("03 \u00B7 Transfer", "Aufgaben und Vorbereitung")
    neue_hausaufgabe = st.text_area(
        "Hausaufgabe f\u00FCr das Kind",
        placeholder="Konkret und kurz formulieren",
        height=82,
        key="transfer_hausaufgabe",
    )
    neue_besprechung = st.text_area(
        "Bis zur n\u00E4chsten Stunde erledigen",
        placeholder="Material, Noten oder organisatorische Punkte",
        height=82,
        key="transfer_vorbereitung",
    )
    return neue_hausaufgabe, neue_besprechung

def zeige_lobbereich():
    kompakt_titel("04 \u00B7 W\u00FCrdigung", "Lobk\u00E4rtchen und eigene Aufgaben")
    lob_vergeben = st.checkbox(
        "F\u00FCr diese Stunde ein Lobk\u00E4rtchen vergeben",
        key="lob_vergeben",
    )
    if lob_vergeben:
        grund = st.text_input(
            "Pers\u00F6nliche W\u00FCrdigung",
            placeholder="Was ist heute besonders gut gelungen?",
            key="lob_grund",
        )
        auf_taskcards = st.checkbox(
            "F\u00FCr TaskCards vormerken",
            value=True,
            key="lob_taskcards",
        )
    else:
        grund = ""
        auf_taskcards = False

    aufgaben_spalte_1, aufgaben_spalte_2 = st.columns(2)
    with aufgaben_spalte_1:
        aufgabe_1 = st.checkbox(
            "Noten vorbereiten",
            key="lehrer_noten_vorbereiten",
        )
    with aufgaben_spalte_2:
        aufgabe_2 = st.checkbox(
            "TaskCards aktualisieren",
            key="lehrer_taskcards_aktualisieren",
        )
    neue_lehrer_aufgabe = st.text_input(
        "Weitere eigene Aufgabe",
        placeholder="Optional",
        key="lehrer_weitere_aufgabe",
    )
    return lob_vergeben, grund, auf_taskcards, aufgabe_1, aufgabe_2, neue_lehrer_aufgabe

def speichere_zwischenstand(entwurf):
    daten_json = json.dumps(entwurf, ensure_ascii=False, sort_keys=True)
    st.session_state["aktueller_zwischenstand"] = entwurf
    if st.session_state.get("zwischenstand_hash") == daten_json:
        return st.session_state.get("zwischenstand_dauerhaft", False)

    zeitpunkt = datetime.datetime.now(ZoneInfo("Europe/Berlin"))
    st.session_state["zwischenstand_hash"] = daten_json
    st.session_state["zwischenstand_zeit"] = zeitpunkt
    dauerhaft = False

    if GSheetsConnection is not None:
        try:
            verbindung = st.connection("gsheets", type=GSheetsConnection)
            bisher = verbindung.read(worksheet="Unterrichtsarchiv", ttl=0)
            if bisher is None or bisher.empty:
                bisher = pd.DataFrame(
                    columns=["Sch\u00FCler", "Datum", "Status", "Gespeichert_am", "Daten_JSON"]
                )
            else:
                bisher = bisher.copy()
                for spalte in ["Sch\u00FCler", "Datum", "Status", "Gespeichert_am", "Daten_JSON"]:
                    if spalte not in bisher.columns:
                        bisher[spalte] = ""

            neue_zeile = {
                "Sch\u00FCler": entwurf["Sch\u00FCler"],
                "Datum": entwurf["Datum"],
                "Status": "Zwischenstand",
                "Gespeichert_am": zeitpunkt.isoformat(timespec="seconds"),
                "Daten_JSON": daten_json,
            }
            maske = (
                bisher["Sch\u00FCler"].fillna("").astype(str).eq(entwurf["Sch\u00FCler"])
                & bisher["Datum"].fillna("").astype(str).eq(entwurf["Datum"])
                & bisher["Status"].fillna("").astype(str).eq("Zwischenstand")
            )
            if maske.any():
                for spalte, wert in neue_zeile.items():
                    bisher.loc[maske, spalte] = wert
            else:
                bisher = pd.concat([bisher, pd.DataFrame([neue_zeile])], ignore_index=True)
            verbindung.update(worksheet="Unterrichtsarchiv", data=bisher)
            dauerhaft = True
        except Exception:
            dauerhaft = False

    st.session_state["zwischenstand_dauerhaft"] = dauerhaft
    return dauerhaft

def ist_gueltiger_cloud_link(link):
    try:
        adresse = urllib.parse.urlparse(str(link).strip())
        return adresse.scheme in {"http", "https"} and bool(adresse.netloc)
    except ValueError:
        return False

def zeige_mini_cockpit_starter(student, stundenende, noten_url, noten_titel):
    ende_text = stundenende.isoformat() if stundenende else ""
    parameter = {
        "mini": "1",
        "student": str(student),
        "ende": ende_text,
        "noten": noten_url,
        "embed": "true",
    }
    parameter_json = json.dumps(parameter, ensure_ascii=False)
    titel_json = json.dumps(noten_titel or "Noten", ensure_ascii=False)
    components.html(
        f"""
        <button id="mini-start" type="button">Mini-Cockpit f\u00FCr diese Noten \u00F6ffnen</button>
        <div id="mini-status"></div>
        <style>
            body {{ margin:0; font-family:Arial,sans-serif; background:transparent; }}
            #mini-start {{
                width:100%; min-height:42px; border:1px solid #17243b; border-radius:9px;
                background:#17243b; color:white; font-size:13px; font-weight:700; cursor:pointer;
            }}
            #mini-start:hover {{ background:#253653; border-color:#b8954b; }}
            #mini-status {{ color:#687386; font-size:10px; text-align:center; margin-top:3px; }}
        </style>
        <script>
            const params = {parameter_json};
            const noteTitle = {titel_json};
            const button = document.getElementById('mini-start');
            const status = document.getElementById('mini-status');
            button.addEventListener('click', async () => {{
                let parentUrl = document.referrer || '';
                try {{
                    if (!parentUrl && window.parent.location.href) parentUrl = window.parent.location.href;
                }} catch (error) {{}}
                const baseUrl = parentUrl.split('?')[0].split('#')[0];
                const miniUrl = baseUrl + '?' + new URLSearchParams(params).toString();
                try {{
                    const host = window.parent;
                    if (host.documentPictureInPicture) {{
                        const pip = await host.documentPictureInPicture.requestWindow({{width:420,height:720}});
                        pip.document.title = 'Mini-Cockpit \u00B7 ' + noteTitle;
                        pip.document.body.style.margin = '0';
                        const frame = pip.document.createElement('iframe');
                        frame.src = miniUrl;
                        frame.style.cssText = 'width:100%;height:100vh;border:0;background:#f7f4ed';
                        pip.document.body.appendChild(frame);
                        status.textContent = 'Mini-Cockpit schwebt jetzt im Vordergrund.';
                        return;
                    }}
                }} catch (error) {{}}
                const popup = window.open(
                    miniUrl,
                    'MiniCockpit',
                    'width=430,height=740,resizable=yes,scrollbars=yes'
                );
                status.textContent = popup
                    ? 'Mini-Cockpit ge\u00F6ffnet. Dort jetzt die Noten gro\u00DF \u00F6ffnen.'
                    : 'Das Mini-Cockpit wurde vom Browser blockiert.';
            }});
        </script>
        """,
        height=62,
    )

def zeige_mini_cockpit(student, stundenende, noten_url):
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"], [data-testid="collapsedControl"] { display:none !important; }
            .block-container { max-width:430px !important; padding:.7rem .7rem 1rem !important; }
            header[data-testid="stHeader"] { display:none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    ende_anzeige = stundenende.strftime("%H:%M Uhr") if stundenende else "nicht festgelegt"
    st.markdown(
        f"""
        <div class="mini-shell">
            <div class="mini-kicker">Reduziertes Unterrichts-Cockpit</div>
            <div class="mini-student">{html.escape(str(student))}</div>
            <div class="mini-info">Stundenende: {html.escape(ende_anzeige)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if stundenende:
        ende_json = json.dumps(stundenende.isoformat())
        components.html(
            f"""
            <div class="timer"><span>Verbleibende Unterrichtszeit</span><strong id="restzeit">--:--</strong></div>
            <style>
                body {{ margin:0; font-family:Arial,sans-serif; background:transparent; }}
                .timer {{ display:flex; justify-content:space-between; align-items:center; padding:8px 12px;
                    background:#f6ecd4; border:1px solid #d8bd7e; border-radius:10px; color:#17243b; }}
                .timer span {{ font-size:12px; font-weight:700; }}
                .timer strong {{ font-size:22px; }}
            </style>
            <script>
                const ende = new Date({ende_json});
                function aktualisieren() {{
                    const sekunden = Math.max(0, Math.floor((ende - new Date()) / 1000));
                    const minuten = Math.floor(sekunden / 60);
                    const rest = String(sekunden % 60).padStart(2, '0');
                    document.getElementById('restzeit').textContent = minuten + ':' + rest;
                }}
                aktualisieren(); setInterval(aktualisieren, 1000);
            </script>
            """,
            height=52,
        )

    if ist_gueltiger_cloud_link(noten_url):
        st.markdown(
            f'<a class="mini-note-link" href="{html.escape(noten_url, quote=True)}" '
            f'target="_blank" rel="noopener">Noten erneut gro\u00DF \u00F6ffnen</a>',
            unsafe_allow_html=True,
        )

    kurznotiz = st.text_area(
        "Kurze Unterrichtsnotiz",
        height=95,
        key="mini_kurznotiz",
    )
    bis_naechstes_mal = st.text_area(
        "Aufgabe bis zur n\u00E4chsten Stunde",
        height=95,
        key="mini_bis_naechstes_mal",
    )
    programm_angemeldet = st.checkbox(
        "Konzertprogramm ist angemeldet",
        key="mini_programm_angemeldet",
    )

    if st.button(
        "Schnelleintrag speichern",
        type="primary",
        use_container_width=True,
        key="mini_schnelleintrag_speichern",
    ):
        zeitpunkt = datetime.datetime.now(ZoneInfo("Europe/Berlin"))
        mini_eintrag = {
            "Datum": zeitpunkt.strftime("%Y-%m-%d"),
            "Uhrzeit": zeitpunkt.strftime("%H:%M:%S"),
            "Sch\u00FCler": str(student),
            "Status": "Mini-Cockpit",
            "Programm_Angemeldet": "Ja" if programm_angemeldet else "Nein",
            "Bis_Naechsten_Mal": bis_naechstes_mal.strip(),
            "Kurznotiz": kurznotiz.strip(),
            "Eintragsart": "Mini-Cockpit",
        }
        dauerhaft = speichere_unterrichtspaket(mini_eintrag, [])
        if dauerhaft:
            st.success("Der Schnelleintrag wurde im Unterrichtsarchiv gespeichert.")
        else:
            st.warning("Der Schnelleintrag ist in dieser Sitzung gesichert; Google Sheets war nicht erreichbar.")

# --- DATEN-LOGIK ---
def lade_archiv_aus_sheet():
    daten = {
        'Schueler': ['Emma', 'Max', 'Lina'],
        'Stueck': ['Sonatine Opus 36', 'F\u00FCr Elise', 'Inventio 1'],
        'Konzertstueck': ['Sonatine 1. Satz', 'F\u00FCr Elise', 'Inventio 1'],
        'Dauer_Minuten': [45, 60, 30],
        'Schwierigkeit': [3, 4, 2],
        'K\u00E4rtchen_Erhalten': ['Ja', 'Nein', 'Ja'],
        'Grund': ['Toller Rhythmus im Takt 12', '', 'Wundersch\u00F6ne Dynamik'],
        'Bis_Naechsten_Mal': ['Takt 15-20 langsam \u00FCben', 'Pedalwechsel weicher gestalten', 'Rhythmus klatschen']
    }
    return pd.DataFrame(daten)

def hole_konzertprogramm(student, archiv):
    auswahl = archiv.loc[archiv["Schueler"] == student, "Konzertstueck"].dropna()
    auswahl = [str(stueck).strip() for stueck in auswahl if str(stueck).strip()]
    if not auswahl:
        return "Noch nicht festgelegt"
    return " \u00B7 ".join(dict.fromkeys(auswahl))

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
        return f"Pause \u00B7 {stunden} Std. {rest} Min."
    return f"Pause \u00B7 {minuten} Min."

def erstelle_tagesleisten_html(termine, jetzt=None):
    if termine is None:
        return '<div class="rail-empty">Die Tagesleiste erscheint hier, sobald der Google Kalender verbunden ist.</div>'

    if not termine:
        return '<div class="rail-empty"><strong>Heute keine Termine.</strong><br>Zeit f\u00FCr freie Improvisation.</div>'

    jetzt = jetzt or datetime.datetime.now(ZoneInfo("Europe/Berlin"))
    sortierte_termine = sorted(termine, key=lambda termin: termin["start"])
    verbleibende_termine = [termin for termin in sortierte_termine if termin["ende"] > jetzt]

    if not verbleibende_termine:
        return '<div class="rail-empty"><strong>Feierabend!</strong><br>Auch der Fl\u00FCgel hat jetzt frei.</div>'

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
        zeit = f'{termin["start"].strftime("%H:%M")}\u2013{termin["ende"].strftime("%H:%M")} Uhr'
        bausteine.append(
            f'<div class="rail-entry {status}"><div class="rail-dot"></div>'
            f'<div class="rail-card"><div class="rail-time">{zeit}</div>'
            f'<div class="rail-name">{name}</div></div></div>'
        )
        vorheriges_ende = termin["ende"]

    feierabend_zeit = sortierte_termine[-1]["ende"].strftime("%H:%M")
    bausteine.append(
        '<div class="rail-entry finish"><div class="rail-dot"></div>'
        f'<div class="rail-card"><div class="rail-time">ab {feierabend_zeit} Uhr</div>'
        '<div class="rail-name">Feierabend</div></div></div>'
    )
    bausteine.append("</div>")
    return "".join(bausteine)

def formatiere_naechsten_termin(termin, kalender_verbunden=False):
    if not termin and not kalender_verbunden:
        return "Noch nicht verbunden", "Google Kalender wird im n\u00E4chsten Schritt angeschlossen"
    if not termin:
        return "Heute niemand mehr", "Feierabend \u2013 auch der Fl\u00FCgel hat jetzt frei"

    name = termin.get("name", "Unbekannt")
    start = termin.get("start")
    if not start:
        return name, "Uhrzeit nicht verf\u00FCgbar"

    jetzt = datetime.datetime.now(start.tzinfo) if start.tzinfo else datetime.datetime.now()
    minuten_bis_start = max(0, int((start - jetzt).total_seconds() // 60))
    if minuten_bis_start >= 60:
        stunden, minuten = divmod(minuten_bis_start, 60)
        abstand = f"in {stunden} Std. {minuten} Min."
    else:
        abstand = f"in {minuten_bis_start} Minuten"
    return f"{name} \u00B7 {start.strftime('%H:%M')} Uhr", abstand

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
    
    lob = df_archiv[(df_archiv['Schueler'] == student) & (df_archiv['K\u00E4rtchen_Erhalten'] == 'Ja')]
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

mini_modus = hole_query_parameter("mini", "0") == "1"

if mini_modus:
    student = hole_query_parameter("student", st.session_state.get("aktueller_student", "Sch\u00FCler"))
    unterrichtsdatum = datetime.date.today()
    ende_parameter = hole_query_parameter("ende", "")
    try:
        stundenende = datetime.datetime.fromisoformat(ende_parameter) if ende_parameter else None
        if stundenende and stundenende.tzinfo is None:
            stundenende = stundenende.replace(tzinfo=ZoneInfo("Europe/Berlin"))
    except ValueError:
        stundenende = None
    dauer_minuten = max(
        0,
        int((stundenende - jetzt).total_seconds() // 60) if stundenende else 0,
    )
else:
    with st.sidebar:
        st.markdown('<div class="day-label">Tages\u00FCbersicht</div>', unsafe_allow_html=True)
        st.markdown('<div class="day-title">Heute im Unterricht</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="day-date">{datetime.date.today().strftime("%d.%m.%Y")}</div>', unsafe_allow_html=True)
        st.markdown(erstelle_tagesleisten_html(heutige_termine, jetzt), unsafe_allow_html=True)

        if erkennter_schueler:
            student = erkennter_schueler
            unterrichtsdatum = datetime.date.today()
            dauer_minuten = int((aktueller_termin["ende"] - aktueller_termin["start"]).total_seconds() // 60)
            stundenende = aktueller_termin["ende"]
            st.success(f"Aktuell: {student}")
            fortschritt = (jetzt - aktueller_termin["start"]).total_seconds() / (aktueller_termin["ende"] - aktueller_termin["start"]).total_seconds()
            st.progress(min(max(fortschritt, 0.0), 1.0), text=f'{aktueller_termin["start"].strftime("%H:%M")}\u2013{aktueller_termin["ende"].strftime("%H:%M")} Uhr')
        else:
            with st.expander("Sch\u00FCler manuell ausw\u00E4hlen", expanded=heutige_termine is None):
                student = st.selectbox("Sch\u00FCler", schueler_liste, label_visibility="collapsed")
                unterrichtsdatum = st.date_input("Datum", value=datetime.date.today(), format="DD.MM.YYYY")
                dauer_minuten = st.selectbox("Dauer", [30, 45, 60], index=1, format_func=lambda x: f"{x} Minuten")
            stundenende = jetzt + datetime.timedelta(minutes=int(dauer_minuten))
            st.caption("Die manuelle Auswahl wird nur ben\u00F6tigt, wenn gerade kein Kalendertermin l\u00E4uft.")

    st.session_state["aktueller_student"] = str(student)
    st.session_state["unterrichtsende"] = stundenende.isoformat() if stundenende else ""

if mini_modus:
    zeige_mini_cockpit(
        student,
        stundenende,
        hole_query_parameter("noten", ""),
    )
    st.stop()

# --- UI NAVIGATION ---
aktive_ansicht = hole_aktive_ansicht()
navigation = [
    ("live", "Live-Cockpit"),
    ("analyse", "Analyse & Fortschritt"),
    ("zertifikate", "Zertifikate & TaskCards"),
]
navigation_html = '<nav class="cockpit-nav" aria-label="Hauptnavigation">'
for ansicht_id, beschriftung in navigation:
    aktive_klasse = " active" if ansicht_id == aktive_ansicht else ""
    navigation_html += (
        f'<a class="{aktive_klasse.strip()}" href="?ansicht={ansicht_id}" target="_self">'
        f'{html.escape(beschriftung)}</a>'
    )
navigation_html += "</nav>"
st.markdown(navigation_html, unsafe_allow_html=True)

if aktive_ansicht == "live":
    konzertprogramm = hole_konzertprogramm(student, df_archiv)
    st.markdown(
        f"""
        <div class="tablet-overview">
            <div class="tablet-brand">
                <div class="tablet-kicker">Digitales Unterrichtsstudio</div>
                <div class="tablet-title">Klavierlehrer Live-Cockpit</div>
                <div class="tablet-note">Klassenvorspiel am 02.09.2026</div>
            </div>
            <div class="tablet-fact">
                <div class="tablet-label">Aktueller Sch\u00FCler</div>
                <div class="tablet-value">{html.escape(str(student))}</div>
                <div class="tablet-note">{unterrichtsdatum.strftime('%d.%m.%Y')} \u00B7 {dauer_minuten} Minuten</div>
            </div>
            <div class="tablet-fact">
                <div class="tablet-label">Konzertprogramm</div>
                <div class="tablet-value">{html.escape(konzertprogramm)}</div>
                <div class="tablet-note">{html.escape(berechne_konzert_countdown())}</div>
            </div>
            <div class="tablet-fact">
                <div class="tablet-label">N\u00E4chster Sch\u00FCler</div>
                <div class="tablet-value">{html.escape(naechster_titel)}</div>
                <div class="tablet-note">{html.escape(naechster_hinweis)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    technik_spalte, repertoire_spalte = st.columns([0.93, 1.07])
    with technik_spalte:
        with st.container(border=True):
            modus, speicher_text = zeige_technikbereich()
    with repertoire_spalte:
        with st.container(border=True):
            repertoire_eintraege = zeige_repertoirebereich(student, stundenende)

    transfer_spalte, lob_spalte = st.columns([1, 1])
    with transfer_spalte:
        with st.container(border=True):
            neue_hausaufgabe, neue_besprechung = zeige_transferbereich()
    with lob_spalte:
        with st.container(border=True):
            (
                lob_vergeben,
                grund,
                auf_taskcards,
                aufgabe_1,
                aufgabe_2,
                neue_lehrer_aufgabe,
            ) = zeige_lobbereich()

    entwurf = {
        "Sch\u00FCler": str(student),
        "Datum": unterrichtsdatum.strftime("%Y-%m-%d"),
        "Dauer_Minuten": int(dauer_minuten),
        "Technik_Bereich": modus,
        "Technik_Details": speicher_text,
        "Repertoire": repertoire_eintraege,
        "Hausaufgabe": neue_hausaufgabe.strip(),
        "Bis_zur_n\u00E4chsten_Stunde": neue_besprechung.strip(),
        "Lobk\u00E4rtchen_Erhalten": "Ja" if lob_vergeben else "Nein",
        "Lob_Grund": grund.strip(),
        "F\u00FCr_TaskCards": "Ja" if auf_taskcards else "Nein",
        "Noten_vorbereiten": "Ja" if aufgabe_1 else "Nein",
        "TaskCards_Board_aktualisieren": "Ja" if aufgabe_2 else "Nein",
        "Weitere_Lehreraufgabe": neue_lehrer_aufgabe.strip(),
    }
    zwischenstand_dauerhaft = speichere_zwischenstand(entwurf)
    zwischenstand_zeit = st.session_state.get("zwischenstand_zeit", jetzt)

    with st.container(key="save_bar"):
        speichern_geklickt = st.button(
            "Unterrichtseintrag speichern",
            type="primary",
            use_container_width=True,
            key="unterrichtseintrag_speichern",
        )
        speicherort = "Google Sheets" if zwischenstand_dauerhaft else "dieser Sitzung"
        st.markdown(
            f'<div class="autosave-status">Zwischenstand automatisch um '
            f'{zwischenstand_zeit.strftime("%H:%M:%S")} Uhr in {speicherort} gesichert</div>',
            unsafe_allow_html=True,
        )

    if speichern_geklickt:
        unvollstaendige_stuecke = [
            eintrag
            for eintrag in repertoire_eintraege
            if not eintrag["Titel"] and (eintrag["Komponist"] or eintrag["Cloud-Link"])
        ]
        if unvollstaendige_stuecke:
            st.error("Bitte erg\u00E4nze bei jedem ausgef\u00FCllten St\u00FCck noch den Titel.")
        else:
            repertoire_zum_speichern = [
                eintrag for eintrag in repertoire_eintraege if eintrag["Titel"]
            ]
            archiv_zeile = {
                "Sch\u00FCler": str(student),
                "Datum": unterrichtsdatum.strftime("%Y-%m-%d"),
                "Status": "Abgeschlossen",
                "Dauer_Minuten": int(dauer_minuten),
                "Technik_Bereich": modus,
                "Technik_Details": speicher_text,
                "St\u00FCcke": " \u00B7 ".join(
                    eintrag["Titel"] for eintrag in repertoire_zum_speichern
                ),
                "Hausaufgabe": neue_hausaufgabe.strip(),
                "Bis_zur_n\u00E4chsten_Stunde": neue_besprechung.strip(),
                "Lobk\u00E4rtchen_Erhalten": "Ja" if lob_vergeben else "Nein",
                "Lob_Grund": grund.strip(),
                "F\u00FCr_TaskCards": "Ja" if auf_taskcards else "Nein",
                "Noten_vorbereiten": "Ja" if aufgabe_1 else "Nein",
                "TaskCards_Board_aktualisieren": "Ja" if aufgabe_2 else "Nein",
                "Weitere_Lehreraufgabe": neue_lehrer_aufgabe.strip(),
            }
            dauerhaft_gespeichert = speichere_unterrichtspaket(
                archiv_zeile,
                repertoire_zum_speichern,
            )
            st.success(
                f"Unterrichtseintrag f\u00FCr {student} am "
                f"{unterrichtsdatum.strftime('%d.%m.%Y')} wurde gespeichert."
            )
            if dauerhaft_gespeichert:
                st.caption(
                    "Technik, Aufgaben und Lob wurden in Google Sheets im Blatt "
                    "Unterrichtsarchiv gespeichert; "
                    f"{len(repertoire_zum_speichern)} St\u00FCck(e) wurden mit Cloud-Link, "
                    "Verwendung und Anmeldestatus im Blatt Repertoire gespeichert."
                )
            else:
                st.warning(
                    "Der Eintrag ist im ge\u00F6ffneten Cockpit gesichert, konnte aber nicht "
                    "dauerhaft an Google Sheets \u00FCbertragen werden. Bitte pr\u00FCfe die "
                    "eingerichtete gsheets-Verbindung und das Zusatzpaket streamlit-gsheets."
                )

elif aktive_ansicht == "analyse":
    st.markdown("## Analyse & Fortschritt")
    st.caption(f"Entwicklung und Jahres\u00FCberblick f\u00FCr {student}")

    verlauf_daten = pd.DataFrame(
        {
            "Datum": ["2026-01-10", "2026-03-15", "2026-05-05", "2026-07-20", "2026-08-18"],
            "Tempo": [60, 72, 90, 110, 128],
            "Tonart": ["C-Dur"] * 5,
        }
    )
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Archivierte Eintr\u00E4ge", len(df_archiv[df_archiv["Schueler"] == student]))
    kpi2.metric("Aktuelles Tempo", "128 BPM", "+18 BPM")
    kpi3.metric("Erarbeitete St\u00FCcke", df_archiv[df_archiv["Schueler"] == student]["Stueck"].nunique())
    kpi4.metric("Lobk\u00E4rtchen", len(df_archiv[(df_archiv["Schueler"] == student) & (df_archiv["K\u00E4rtchen_Erhalten"] == "Ja")]))

    abschnitt("Jahresverlauf", "Tempo-Entwicklung", "Die Beispielkurve wird nach der Google-Sheets-Anbindung automatisch aus den Unterrichtseintr\u00E4gen gespeist.")
    fig = px.line(verlauf_daten, x="Datum", y="Tempo", markers=True)
    fig.update_traces(line_color="#b8954b", line_width=3, marker=dict(size=9, color="#17243b"))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,253,248,.7)",
        font=dict(family="DM Sans", color="#263247"),
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title=None,
        yaxis_title="Tempo \u00B7 BPM",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    abschnitt("Archiv", "Alle Unterrichtseintr\u00E4ge", "Durchsuche und kontrolliere die bisher erfassten Daten.")
    st.dataframe(df_archiv, use_container_width=True, hide_index=True)

elif aktive_ansicht == "zertifikate":
    st.markdown("## Zertifikate & TaskCards")
    st.caption(f"Pers\u00F6nlicher Jahresabschluss 2026 f\u00FCr {student}")

    info_col, action_col = st.columns([1.35, 1])
    with info_col:
        abschnitt("Jahreszertifikat", "Fortschritt sichtbar w\u00FCrdigen", "Das Zertifikat b\u00FCndelt erarbeitete St\u00FCcke und besondere Erfolge aus dem Archiv.")
        st.info("Vor der Erstellung kannst du die Eintr\u00E4ge im Analyse-Tab noch einmal kontrollieren.")
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
            whatsapp_text = f"Hallo! Hier ist das Jahres-Zertifikat {aktuelles_jahr} f\u00FCr {student} aus der Klavierstunde."
            whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(whatsapp_text)}"
            st.link_button("\u00DCber WhatsApp teilen", whatsapp_url, use_container_width=True)
