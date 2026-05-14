"""
Handicap Scraper App
"""
import streamlit as st
import pandas as pd
import io
from datetime import datetime
from utils.handicap_scraper import test_login, scrape_handicap_pw
from utils.handicap_calculator import load_course_data, render_course_tee_selector, calculate_course_handicap

def run(logged_in, credentials, course_df):
    st.header("Handicap Scraper & Calculator")

    if logged_in:
        st.success("✅ Login successful! Connected to Handicaps.co.za.")

        tab1, tab2, tab3 = st.tabs(["Single Player", "Batch Processing", "Handicap Calculator"])

        # --------- Single Player ---------
        with tab1:
            st.header("Single Player Lookup")

            course, tee, tee_data = render_course_tee_selector(course_df, "single")

            member = st.text_input("Membership Number", key="single_member")

            if st.button("Search Player"):
                with st.spinner("Scraping..."):
                    result = scrape_handicap_pw(credentials["username"], credentials["password"], member)

                if result["status"] == "cached":
                    st.info("⚡ Loaded from cache")

                if result["status"] == "error":
                    st.error(result["error"])
                else:
                    st.success("Player found!")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Membership", result["membership"])
                    col2.metric("Name", result["name"])
                    col3.metric("Handicap Index", result["handicap_index"])

                    if tee_data is not None:
                        course_hcp = calculate_course_handicap(
                            result["handicap_index"],
                            tee_data["Slope Rating"],
                            tee_data["Course Rating"],
                            tee_data["Par"],
                        )
                        st.metric("Course Handicap", int(round(course_hcp)))

        # --------- Batch Processing ---------
        with tab2:
            st.header("Batch Processing")

            course, tee, tee_data = render_course_tee_selector(course_df, "batch")

            uploaded = st.file_uploader("Upload player_ids.xlsx", type=["xlsx"])

            if uploaded and st.button("Process All"):
                df_input = pd.read_excel(uploaded)

                membership_col = next((c for c in df_input.columns if "member" in c.lower()), None)
                cap_col = next((c for c in df_input.columns if "cap" in c.lower()), None)
                name_col = next((c for c in df_input.columns if "name" in c.lower()), None)

                members = df_input[membership_col].astype(str).str.replace(r"\.0$", "", regex=True)
                caps = df_input[cap_col]
                names = df_input[name_col] if name_col else [None] * len(members)

                results = []
                progress = st.progress(0)
                status_text = st.empty()

                for i, (mem, cap, fallback) in enumerate(zip(members, caps, names)):
                    status_text.write(f"Searching member: {mem}")

                    result = scrape_handicap_pw(credentials["username"], credentials["password"], mem, fallback)

                    scraped = result.get("handicap_index")
                    if scraped:
                        try:
                            scraped_f = float(scraped)
                            final_index = cap if scraped_f > cap else scraped_f
                        except:
                            final_index = cap
                    else:
                        final_index = cap

                    result["cap"] = cap

                    if tee_data is not None:
                        course_hcp = calculate_course_handicap(
                            final_index,
                            tee_data["Slope Rating"],
                            tee_data["Course Rating"],
                            tee_data["Par"],
                        )
                        result["course_handicap"] = int(round(course_hcp)) if course_hcp is not None else None
                    else:
                        result["course_handicap"] = None

                    results.append(result)
                    progress.progress((i + 1) / len(members))

                status_text.write("Done")

                df_out = pd.DataFrame(results)
                df_out = df_out.drop(columns=["status"])
                df_out = df_out.rename(columns={"cap": "status"})

                output = io.BytesIO()
                df_out.to_excel(output, index=False)
                output.seek(0)

                st.download_button(
                    "Download Results",
                    data=output.getvalue(),
                    file_name=f"GOAM_HI_{datetime.now().strftime('%Y%m')}_PW.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

                st.dataframe(df_out)

        # --------- Handicap Calculator ---------
        with tab3:
            st.header("Handicap Calculator")

            index = st.number_input("Handicap Index", min_value=0.0, max_value=54.0, step=0.1)

            course, tee, tee_data = render_course_tee_selector(course_df, "calc")

            if tee_data is not None:
                hcp = calculate_course_handicap(
                    index,
                    tee_data["Slope Rating"],
                    tee_data["Course Rating"],
                    tee_data["Par"],
                )
                st.metric("Course Handicap", int(round(hcp)))

    else:
        st.warning("👈 Please log in using the sidebar to access the Handicap Scraper.")
