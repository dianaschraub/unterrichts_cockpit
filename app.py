
def hole_programm_uebersicht(student):
    """Liest die schuelerbezogene Programmauswahl fuer die obere Cockpit-Zeile."""
    keys = repertoire_status_keys(student)
    tabelle = st.session_state.get(keys["tabelle"], leere_repertoire_tabelle(2))
    if not isinstance(tabelle, pd.DataFrame):
        tabelle = leere_repertoire_tabelle(2)

    titel_nach_index = {}
    for index, zeile in tabelle.iterrows():
        titel = "" if pd.isna(zeile.get("Titel", "")) else str(zeile.get("Titel", "")).strip()
        if titel:
            titel_nach_index[int(index)] = titel

    def ausgewaehlte_titel(key):
        return [
            titel_nach_index[index]
            for index in st.session_state.get(key, [])
            if index in titel_nach_index
        ]

    return {
        "unterricht": list(titel_nach_index.values()),
        "konzert_aktiv": bool(st.session_state.get(keys["konzert_aktiv"], False)),
        "konzert_stuecke": ausgewaehlte_titel(keys["konzert_stuecke"]),
        "konzert_datum": st.session_state.get(keys["konzert_datum"]),
        "konzert_angemeldet": bool(st.session_state.get(keys["konzert_angemeldet"], False)),
        "wettbewerb_aktiv": bool(st.session_state.get(keys["wettbewerb_aktiv"], False)),
        "wettbewerb_stuecke": ausgewaehlte_titel(keys["wettbewerb_stuecke"]),
        "wettbewerb_datum": st.session_state.get(keys["wettbewerb_datum"]),
        "wettbewerb_angemeldet": bool(st.session_state.get(keys["wettbewerb_angemeldet"], False)),
    }

def zeige_repertoirebereich(student, stundenende):
    kompakt_titel("02 \u00B7 Repertoire", "Unterrichtsprogramm und besondere Ziele")
    keys = repertoire_status_keys(student)
    if keys["anzahl"] not in st.session_state:
        st.session_state[keys["anzahl"]] = 2
    if keys["tabelle"] not in st.session_state:
        st.session_state[keys["tabelle"]] = leere_repertoire_tabelle(2)

    anzahl = st.session_state[keys["anzahl"]]
    tabelle = st.session_state[keys["tabelle"]].iloc[:anzahl].copy()
    while len(tabelle) < anzahl:
        tabelle = pd.concat(
            [tabelle, leere_repertoire_tabelle(1, startnummer=len(tabelle) + 1)],
            ignore_index=True,
        )
    tabelle["Nr."] = range(1, len(tabelle) + 1)

    st.caption(
        "Unterrichtsprogramm \u00B7 diese Liste gilt f\u00FCr die laufende Arbeit."
    )

    bearbeitet = st.data_editor(
        tabelle,
        hide_index=True,
        use_container_width=True,
        height=min(315, 72 + anzahl * 35),
        disabled=["Nr."],
        key=f"repertoire_editor_{repertoire_schluessel(student)}_{anzahl}",
        column_config={
            "Nr.": st.column_config.NumberColumn("Nr.", width="small"),
            "Titel": st.column_config.TextColumn("Titel", width="medium"),
            "Komponist": st.column_config.TextColumn("Komponist", width="small"),
            "Cloud-Link": st.column_config.TextColumn(
                "Cloud-Link",
                width="medium",
