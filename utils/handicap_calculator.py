"""
Handicap Calculator Module - Handles handicap calculations
"""
import pandas as pd
import streamlit as st
import os

# ================================================================================
# CACHE COURSE DATA
# ================================================================================
@st.cache_data
def load_course_data(uploaded_file=None):
    """Load course data from Excel or CSV file"""
    try:
        if uploaded_file:
            if uploaded_file.name.endswith('.csv'):
                try:
                    return pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    return pd.read_csv(uploaded_file, encoding='latin-1')
            else:
                return pd.read_excel(uploaded_file)
        
        # Try loading from data folder
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        
        # Try Excel first
        excel_path = os.path.join(data_dir, "Course_Information.xlsx")
        if os.path.exists(excel_path):
            return pd.read_excel(excel_path)
        
        # Try CSV with different encodings
        csv_path = os.path.join(data_dir, "Course_Information.csv")
        if os.path.exists(csv_path):
            try:
                return pd.read_csv(csv_path, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    return pd.read_csv(csv_path, encoding='latin-1')
                except UnicodeDecodeError:
                    return pd.read_csv(csv_path, encoding='cp1252')
        
        st.warning("Course_Information file not found. Please upload it in the sidebar.")
        return None
    except Exception as e:
        st.error(f"Error loading course data: {e}")
        return None

# ================================================================================
# CALCULATE COURSE HANDICAP
# ================================================================================
def calculate_course_handicap(handicap_index, slope_rating, course_rating, par):
    """Calculate course handicap from index and course data"""
    try:
        index = float(handicap_index)
        slope = float(slope_rating)
        rating = float(course_rating)
        par_val = float(par)
        return index * (slope / 113.0) + (rating - par_val)
    except:
        return None

# ================================================================================
# COURSE SELECTOR
# ================================================================================
def render_course_tee_selector(course_df, key_prefix):
    """Render course and tee selectors"""
    if course_df is None:
        st.error("Course data not loaded.")
        return None, None, None

    col1, col2 = st.columns(2)

    with col1:
        course_names = course_df["Course Name"].unique().tolist()
        selected_course = st.selectbox("Select Course", course_names, key=f"{key_prefix}_course")

    with col2:
        tees = course_df[course_df["Course Name"] == selected_course]
        tee_names = tees["Tee Name"].tolist()
        selected_tee = st.selectbox("Select Tee", tee_names, key=f"{key_prefix}_tee")

    tee_data = tees[tees["Tee Name"] == selected_tee].iloc[0]

    st.info(
        f"Course: **{selected_course}** | Tee: **{selected_tee}** | "
        f"Slope: {tee_data['Slope Rating']} | Rating: {tee_data['Course Rating']} | Par: {int(tee_data['Par'])}"
    )

    return selected_course, selected_tee, tee_data
