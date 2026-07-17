import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# Hashes to hashes, dusk to dawn.

# streamlit run app.py via PyCharm Terminal. Dependencies referenced in imports.

#################################
# 1. PAGE CONFIGURATION & TITLE #
#################################

st.set_page_config(page_title="Student Risk Matrix Dashboard", layout="wide")

st.title("🎓 Student Risk Matrix: Lifestyle Exhaustion & Institutional Attrition")
st.markdown(
    "Dashboard explores how lifestyle exhaustions, academic fulfillment, "
    "and structural financial factors intersect to drive student attrition risks."
)
st.markdown("---")


#############################################################
# 2. DATASET EMULATION (Matching Presentation Data Profile) #
#############################################################

@st.cache_data
def load_student_data():
    np.random.seed(42)
    n_samples = 1000

    genders = ['Female', 'Male']
    sleep_windows = ['Less than 5 hours', '5-6 hours', '7-8 hours', 'More than 8 hours']
    satisfaction = [1, 2, 3, 4, 5]
    tuition = ['Yes', 'No']
    status = ['Graduate', 'Enrolled', 'Dropout']

    data = {
        'Gender': np.random.choice(genders, n_samples, p=[0.55, 0.45]),
        'Sleep_Window': np.random.choice(sleep_windows, n_samples, p=[0.2, 0.3, 0.4, 0.1]),
        'Study_Satisfaction': np.random.choice(satisfaction, n_samples, p=[0.15, 0.2, 0.3, 0.25, 0.1]),
        'Tuition_Up_To_Date': np.random.choice(tuition, n_samples, p=[0.8, 0.2]),
    }

    df = pd.DataFrame(data)

    # Logic simulating slide insights

    def calculate_phq9(row):
        score = 8  # Baseline
        if row['Sleep_Window'] == 'Less than 5 hours': score += 4
        if row['Sleep_Window'] == '5-6 hours': score += 2
        if row['Study_Satisfaction'] <= 2: score += 3
        # Emulating the male under-stimulation anomaly noted in slides[cite: 1]
        if row['Gender'] == 'Male' and row['Study_Satisfaction'] == 1: score += 2
        return min(max(int(score + np.random.normal(0, 1.5)), 0), 24)

    # Logic simulating slide attrition metrics (tuition non-compliance = high dropout)[cite: 1]
    def determine_status(row):
        if row['Tuition_Up_To_Date'] == 'No':
            return np.random.choice(status, p=[0.2, 0.2, 0.6])
        return np.random.choice(status, p=[0.6, 0.3, 0.1])

    df['PHQ9_Score'] = df.apply(calculate_phq9, axis=1)
    df['Academic_Status'] = df.apply(determine_status, axis=1)
    return df


df = load_student_data()

###############################################
# 3. UI INTERACTION (Sidebar Dropdown Filter) #
###############################################

st.sidebar.header("Dashboard Controls")
st.sidebar.write("Filter the student profile to observe gendered behavioral trajectories.")

gender_filter = st.sidebar.selectbox(
    "Select Student Gender Profile",
    ["All Students", "Female", "Male"]
)

# UI filter

filtered_df = df if gender_filter == "All Students" else df[df['Gender'] == gender_filter]

####################################################
# 4. WITHIN-VISUALIZATION SELECTION & COORDINATION #
####################################################

heatmap_selection = alt.selection_point(
    fields=['Sleep_Window', 'Study_Satisfaction'],
    name="HeatmapBrush"
)

# --- VISUALIZATION 1: LIFESTYLE EXHAUSTION HEATMAP ---

heatmap = alt.Chart(filtered_df).mark_rect().encode(
    x=alt.X(
        'Sleep_Window:O',
        title="Average Daily Sleep Windows",
        sort=['Less than 5 hours', '5-6 hours', '7-8 hours', 'More than 8 hours']
    ),
    y=alt.Y('Study_Satisfaction:O', title="Study Satisfaction Rating (Low to High)"),
    color=alt.condition(
        heatmap_selection,
        alt.Color('mean(PHQ9_Score):Q', scale=alt.Scale(scheme='reds'), title="Mean PHQ-9 Score"),
        alt.value('lightgray')  # Dims unselected boxes when clicked
    ),
    # Tooltip compliance[cite: 1]
    tooltip=[
        alt.Tooltip('Sleep_Window', title='Sleep Window'),
        alt.Tooltip('Study_Satisfaction', title='Satisfaction Rating'),
        alt.Tooltip('mean(PHQ9_Score):Q', title='Avg PHQ-9 Score', format='.1f'),
        alt.Tooltip('count()', title='Sample Size (N)')
    ]
).properties(
    title="1. Clinical Severity Hotspots (Click a Cell to Filter Outcomes)",
    width=450,
    height=380
).add_params(
    heatmap_selection  # Correct implementation for updated Altair releases
)

# --- VISUALIZATION 2: COORDINATED ATTRITION BAR CHART ---

bar_chart = alt.Chart(filtered_df).mark_bar().encode(
    x=alt.X('Tuition_Up_To_Date:N', title="Tuition Fees Up-to-Date"),
    y=alt.Y('count():Q', title="Student Cohort Size"),
    color=alt.Color(
        'Academic_Status:N',
        scale=alt.Scale(
            domain=['Dropout', 'Enrolled', 'Graduate'],
            range=['#EF553B', '#00CC96', '#636EFA']
        ),
        title="Academic Status"
    ),
    # Tooltip compliance[cite: 1]
    tooltip=[
        alt.Tooltip('Academic_Status', title='Status'),
        alt.Tooltip('Tuition_Up_To_Date', title='Tuition Compliant'),
        alt.Tooltip('count()', title='Student Count')
    ]
).transform_filter(
    # Core Coordination: This forces Chart 2 to update based on selections in Chart 1[cite: 1]
    heatmap_selection
).properties(
    title="2. Institutional Attrition Outcomes (Filtered by Selection)",
    width=400,
    height=380
)

##############################
# 5. DASHBOARD LAYOUT RENDER #
##############################

col1, col2 = st.columns([1.1, 1])

with col1:
    st.altair_chart(heatmap, use_container_width=True)

with col2:
    st.altair_chart(bar_chart, use_container_width=True)

# Application & UX Summary Box

st.info(
    " Dashboard manifested largely with the help of Gemini, Pycharm, Altair, and Streamline..."
    "... and only a tiny tiny bit by B.S."
)