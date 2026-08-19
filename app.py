    
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
