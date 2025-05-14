import pandas as pd
import streamlit as st
import altair as alt
from data_processing import finalize_data
from navigation import make_sidebar


# Setting page title and favicon
st.set_page_config(page_title='Result Summary', page_icon='📊')

make_sidebar()

# Adding logo and header to the sidebar and main page
st.logo('kognisi_logo.png')

# Main title and description
st.markdown('''  
# 📊 Result Summary
''')

# Retrieve data from data_processing
df_sap, df_merged, df_combined_au_capture, df_creds = finalize_data()

# Sidebar filters with multiselect
st.sidebar.header("Filter Options")

df_filtered = df_merged

# Add platform filter to the sidebar using multiselect with default as empty list
selected_platform = st.sidebar.multiselect(
    "Select Platform",
    options=df_filtered['platform'].unique(),
    default=[]  # Default is an empty list, no selection initially
)

# Apply platform filter if layers are selected
if selected_platform:
    df_filtered = df_filtered[df_filtered['platform'].isin(selected_platform)]

# Add status filter to the sidebar using multiselect with default as empty list
selected_status = st.sidebar.multiselect(
    "Select Internal/External",
    options=df_filtered['status_learner'].unique(),
    default=[]  # Default is an empty list, no selection initially
)

# Apply status filter if layers are selected
if selected_status:
    df_filtered = df_filtered[df_filtered['status_learner'].isin(selected_status)]

# Add unit filter to the sidebar using multiselect with default as empty list
selected_units = st.sidebar.multiselect(
    "Select Unit",
    options=df_filtered['unit'].unique(),
    default=[]  # Default is an empty list, no selection initially
)

# Apply unit filter if units are selected
if selected_units:
    df_filtered = df_filtered[df_filtered['unit'].isin(selected_units)]

# Add subunit filter to the sidebar using multiselect with default as empty list
selected_subunits = st.sidebar.multiselect(
    "Select Subunit",
    options=df_filtered['subunit'].unique(),
    default=[]  # Default is an empty list, no selection initially
)

# Apply subunit filter if subunits are selected
if selected_subunits:
    df_filtered = df_filtered[df_filtered['subunit'].isin(selected_subunits)]

# Add layer filter to the sidebar using multiselect with default as empty list
selected_layers = st.sidebar.multiselect(
    "Select Layer",
    options=df_filtered['layer'].unique(),
    default=[]  # Default is an empty list, no selection initially
)

# Apply layer filter if layers are selected
if selected_layers:
    df_filtered = df_filtered[df_filtered['layer'].isin(selected_layers)]

# Add years (tenure) filter to the sidebar using multiselect with default as empty list
selected_years = st.sidebar.multiselect(
    "Select Years (Tenure)",
    options=df_filtered['tenure'].unique(),
    default=[]  # Default is an empty list, no selection initially
)

# Apply tenure filter if years are selected
if selected_years:
    df_filtered = df_filtered[df_filtered['tenure'].isin(selected_years)]

# Add institution filter to the sidebar using multiselect with default as empty list
selected_institution = st.sidebar.multiselect(
    "Select Institution",
    options=df_filtered['institution'].unique(),
    default=[]  # Default is an empty list, no selection initially
)

# Apply intitution filter if years are selected
if selected_institution:
    df_filtered = df_filtered[df_filtered['institution'].isin(selected_institution)]

# Active learners by bundle
bundle_names = ['GI', 'LEAN', 'ELITE', 'Genuine', 'Astaka']

# Create filtered dataframe for active learners
df_active_learners = df_filtered.groupby(['email', 'last_updated', 'title']).size().reset_index(name='test_count')

# Count active learners per bundle
bundle_counts = {bundle: df_active_learners[df_active_learners['title'] == bundle]['email'].nunique() for bundle in bundle_names}

# Display active learners counts
st.header('Active Learners', divider='gray')
col1, col2, col3, col4, col5 = st.columns(5)

for i, bundle in enumerate(bundle_names):
    with eval(f'col{i + 1}'):
        st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>{bundle}: <span style='color: red;'>{bundle_counts[bundle]:,}</span></strong></p>", unsafe_allow_html=True)


# 1. Get the latest test results for each email and Test Name
latest_test_results = df_filtered.loc[df_filtered.groupby(['email', 'Test Name'])['last_updated'].idxmax()]

# 2. Count participants based on bundle_name
participant_counts = df_filtered.groupby('title')['email'].nunique().reset_index()
participant_counts.columns = ['title', 'jumlah_partisipan']

# 3. Count users based on typology from the latest results
typology_user_counts = latest_test_results.groupby('typology')['email'].nunique().reset_index()
typology_user_counts.columns = ['typology', 'jumlah']

# 4. Get unique Test Name for each bundle_name
test_names = df_filtered[['title', 'Test Name']].drop_duplicates()

# 5. Get all unique typology results for each Test Name
typology_results = latest_test_results.groupby(['Test Name', 'typology'])['email'].nunique().reset_index()
typology_results.columns = ['Test Name', 'typology', 'jumlah']

# 6. Calculate percentages for each typology per Test Name
total_users_per_test = typology_results.groupby('Test Name')['jumlah'].transform('sum')
typology_results['persentase'] = (typology_results['jumlah'] / total_users_per_test * 100).round(2)

# 7. Combine results into one DataFrame
result_df = pd.merge(participant_counts, test_names, on='title', how='left')
result_df = pd.merge(result_df, typology_results, on='Test Name', how='left')

# 8. Add rows for Overall ELITE based on filtered results
final_results_elite = latest_test_results[latest_test_results['title'] == 'ELITE'].groupby('final_result')['email'].nunique().reset_index()
overall_elite_rows = [{
    'title': 'ELITE',
    'jumlah_partisipan': participant_counts.loc[participant_counts['title'] == 'ELITE', 'jumlah_partisipan'].values[0],
    'Test Name': 'Overall ELITE',
    'typology': row['final_result'],
    'jumlah': row['email'],
    'persentase': (row['email'] / participant_counts.loc[participant_counts['title'] == 'ELITE', 'jumlah_partisipan'].values[0] * 100).round(2)
} for _, row in final_results_elite.iterrows()]

overall_elite_df = pd.DataFrame(overall_elite_rows)

# 9. Add rows for Overall LEAN based on filtered results
final_results_lean = latest_test_results[latest_test_results['title'] == 'LEAN'].groupby('final_result')['email'].nunique().reset_index()
overall_lean_rows = [{
    'title': 'LEAN',
    'jumlah_partisipan': participant_counts.loc[participant_counts['title'] == 'LEAN', 'jumlah_partisipan'].values[0],
    'Test Name': 'Overall LEAN',
    'typology': row['final_result'],
    'jumlah': row['email'],
    'persentase': (row['email'] / participant_counts.loc[participant_counts['title'] == 'LEAN', 'jumlah_partisipan'].values[0] * 100).round(2)
} for _, row in final_results_lean.iterrows()]

overall_lean_df = pd.DataFrame(overall_lean_rows)

# 10. Combine result_df with overall_elite_df and overall_lean_df
result_df = pd.concat([result_df, overall_elite_df, overall_lean_df], ignore_index=True)

# 11. Filter for desired bundles: GI, ELITE, LEAN
filtered_bundles = ['GI', 'ELITE', 'LEAN']
result_df = result_df[result_df['title'].isin(filtered_bundles)]

# 12. Set categorical order and sort
result_df['title'] = pd.Categorical(result_df['title'], categories=filtered_bundles, ordered=True)
result_df = result_df.sort_values(['title', 'Test Name']).reset_index(drop=True)

# 13. Combine number of users with result_df without additional calculations
combined_result_df = pd.merge(result_df, typology_user_counts[['typology']], on='typology', how='left')

# 14. Create a custom sort order for 'Test Name'
def custom_sort_order(test_name):
    if test_name in ["Mindset", "Overall ELITE", "Overall LEAN"]:
        return 0
    return 1

combined_result_df['sort_order'] = combined_result_df['Test Name'].apply(custom_sort_order)

# Sort by bundle_name and custom sort order
combined_result_df = combined_result_df.sort_values(['title', 'sort_order', 'Test Name']).reset_index(drop=True)

# Typology Summary 
st.header('Typology Summary', divider='gray')

# Replace bundle filter with dropdown on the main page to show table and chart per test

selected_bundle = st.selectbox(
    "Choose Bundle",
    options=["GI", "LEAN", "ELITE", "Genuine", "Astaka"],
    index=0  # Optional: set the default selected option
)

# Prepare filtered data based on dropdown selection
selected_layers_title = ', '.join(selected_layers) if selected_layers else 'All Layers'
selected_units_title = ', '.join(selected_units) if selected_units else 'All Units'

# --- GI / ELITE / LEAN (Stacked Chart Section) ---
if selected_bundle in ["GI", "LEAN", "ELITE"]:
    df_bundle = combined_result_df[combined_result_df['title'] == selected_bundle].copy()

    if selected_bundle == 'LEAN':
        df_bundle = df_bundle[~df_bundle['typology'].isin(['The Olympian', 'The Spectator'])]
    elif selected_bundle == 'ELITE':
        df_bundle = df_bundle[~df_bundle['typology'].isin(['Citizen', 'Governor'])]

    total_users_per_test = df_bundle.groupby('Test Name')['jumlah'].transform('sum')
    df_bundle['persentase'] = (df_bundle['jumlah'] / total_users_per_test * 100).round(2)

    chart = alt.Chart(df_bundle).mark_bar().encode(
        x=alt.X('persentase:Q', title='Persentase Active Learners'),
        y=alt.Y('Test Name:N', title='Test Name', sort='-x'),
        color=alt.Color('typology:N', title='Typology', scale=alt.Scale(scheme='category10')),
        tooltip=['Test Name:N', 'jumlah:Q', 'typology:N', 'persentase:Q']
    ).properties(
        width=600,
        height=400
    ).configure_axis(labelFontSize=12, titleFontSize=14)

    st.altair_chart(chart, use_container_width=True)
    with st.expander('View Summary Data'):
        st.dataframe(df_bundle.drop(columns=['sort_order']))


# --- Genuine Section ---
if selected_bundle == "Genuine":

    # Filter for 'Genuine' bundle
    genuine_filtered = df_filtered[df_filtered['title'] == 'Genuine']
    highest_scores = genuine_filtered.loc[genuine_filtered.groupby(['email', 'last_updated', 'Test Name'])['total_score'].idxmax()]

    # Prepare the data with necessary columns
    genuine_active_learners_data = highest_scores[['name', 'email', 'Customer ID', 'title', 'last_updated', 'Test Name', 'total_score', 'final_result']].copy()

    # Rank the learners by total_score
    genuine_active_learners_data['rank'] = genuine_active_learners_data.groupby(['Customer ID', 'last_updated'])['total_score'].rank(ascending=False, method='first').astype(int)
    
    # Filter out ranks above 9
    genuine_active_learners_data = genuine_active_learners_data[genuine_active_learners_data['rank'] <= 9]

    # Rank selection dropdown
    selected_rank = st.selectbox("Select Rank for Genuine", options=range(1, 10), index=0)
    
    # Filter data by selected rank
    filtered_data_by_rank = genuine_active_learners_data[genuine_active_learners_data['rank'] == selected_rank]
    
    # Get the latest test results per email
    latest_results = filtered_data_by_rank.loc[filtered_data_by_rank.groupby('email')['last_updated'].idxmax()]
    total_participants = latest_results['email'].nunique()

    # Create summary data for display
    summary_data = (
        latest_results
        .groupby(['title', 'Test Name'])  # Group by title and Test Name
        .agg(
            jumlah_partisipan=('email', 'nunique'),  # Count unique email
            jumlah=('email', 'count')  # Count total entries for each Test Name
        )
        .reset_index()
    )

    # Add total participants and calculate percentage
    summary_data['jumlah_partisipan'] = total_participants
    summary_data['persentase'] = (summary_data['jumlah'] / summary_data['jumlah_partisipan'] * 100).round(2)

    # Reorder columns for display
    summary_data = summary_data[['title', 'jumlah_partisipan', 'Test Name', 'jumlah', 'persentase']]


    # Visualization: Create a bar chart for the data
    bar_chart = alt.Chart(summary_data).mark_bar().encode(
        x=alt.X('Test Name:O', title='Test Name'),
        y=alt.Y('jumlah:Q', title='Jumlah'),
        tooltip=['Test Name', 'jumlah', 'persentase']
    ).properties(
        title=f'Genuine Top {selected_rank}'
    )
    # Display the bar chart
    st.altair_chart(bar_chart, use_container_width=True)

    # Display the summary data
    with st.expander('View Summary Data'):
        st.dataframe(summary_data)

# --- Astaka Section ---
if selected_bundle == "Astaka":

    astaka_filtered = df_filtered[df_filtered['title'] == 'Astaka']
    highest_scores = astaka_filtered.loc[astaka_filtered.groupby(['email', 'last_updated', 'Test Name'])['total_score'].idxmax()]
    astaka_active_learners_data = highest_scores[['name', 'email', 'Customer ID', 'title', 'last_updated', 'Test Name', 'total_score', 'final_result']].copy()

    astaka_active_learners_data['rank'] = astaka_active_learners_data.groupby(['Customer ID', 'last_updated'])['total_score'].rank(ascending=False, method='first').astype(int)
    astaka_active_learners_data = astaka_active_learners_data[astaka_active_learners_data['rank'] <= 6]

    selected_rank = st.selectbox("Select Rank for Astaka", options=range(1, 7), index=0)
    filtered_data_by_rank = astaka_active_learners_data[astaka_active_learners_data['rank'] == selected_rank]
    latest_results = filtered_data_by_rank.loc[filtered_data_by_rank.groupby('email')['last_updated'].idxmax()]
    total_participants = latest_results['email'].nunique()

    summary_data = (
        latest_results
        .groupby(['title', 'Test Name'])
        .agg(
            jumlah_partisipan=('email', 'nunique'),
            jumlah=('email', 'count')
        )
        .reset_index()
    )
    summary_data['jumlah_partisipan'] = total_participants
    summary_data['persentase'] = (summary_data['jumlah'] / summary_data['jumlah_partisipan'] * 100).round(2)
    summary_data = summary_data[['title', 'jumlah_partisipan', 'Test Name', 'jumlah', 'persentase']]

    bar_chart = alt.Chart(summary_data).mark_bar().encode(
        x=alt.X('Test Name:O', title='Test Name'),
        y=alt.Y('jumlah:Q', title='Jumlah'),
        tooltip=['Test Name', 'jumlah', 'persentase']
    ).properties(title=f'Astaka Top {selected_rank}')

    # Display chart & table
    st.altair_chart(bar_chart, use_container_width=True)
    with st.expander('View Summary Data'):
        st.dataframe(summary_data)

# --- Demographic Comparison Section ---
st.header('Demographic Comparison', divider='gray')

# Step 1: Bundle selection
selected_demo_bundle = selected_bundle

# Step 2: Filter the latest test results for that bundle
demo_filtered = latest_test_results[latest_test_results['title'] == selected_demo_bundle]

# Step 3: Get available tests for this bundle
available_tests = demo_filtered['Test Name'].unique()
selected_demo_test = st.selectbox("Select Test", options=available_tests)

# Step 4: Choose demographic variable
demographic_options = ['status_learner', 'unit', 'subunit', 'gender', 'generation', 'layer', 'tenure']
selected_demo_variable = st.selectbox("Select Demographic Variable", options=demographic_options)

# Step 5: Filter by test
df_demo = demo_filtered[demo_filtered['Test Name'] == selected_demo_test]

# Step 6: Group and calculate typology distribution
demo_grouped = (
    df_demo.groupby([selected_demo_variable, 'typology'])['email']
    .nunique()
    .reset_index(name='jumlah')
)

# Step 7: Calculate total per demographic group
total_per_group = demo_grouped.groupby(selected_demo_variable)['jumlah'].transform('sum')
demo_grouped['persentase'] = (demo_grouped['jumlah'] / total_per_group * 100).round(2)

# Step 8: Visualization
chart = alt.Chart(demo_grouped).mark_bar().encode(
    x=alt.X('persentase:Q', title='Percentage'),
    y=alt.Y(f'{selected_demo_variable}:N', title=selected_demo_variable.replace('_', ' ').title()),
    color=alt.Color('typology:N', title='Typology'),
    tooltip=[selected_demo_variable, 'typology', 'jumlah', 'persentase']
).properties(
    width=700,
    height=400,
)

st.altair_chart(chart, use_container_width=True)

# Optional: Show raw data
with st.expander("View Raw Data Table"):
    st.dataframe(demo_grouped)
