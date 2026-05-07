import streamlit as st
import pandas as pd
import plotly.express as px

# Set Page Config
st.set_page_config(page_title="Workforce Strategy Dashboard", layout="wide")

st.title("📊 Global Workforce Strategic Insights")
st.markdown("Focused analysis for the Senior Associate Pre-work.")

# Load and Clean Data
@st.cache_data
def load_data():
    # Load your file
    df = pd.read_csv('Refined_Employee_Database.csv')
    
    # 1. Clean Salary Column
    if df['Annual Salary'].dtype == 'O':
        df['Annual Salary'] = df['Annual Salary'].str.replace('[\$,]', '', regex=True).astype(float)
    
    # 2. Clean Bonus Column (handles 15% vs 0.15)
    if df['Bonus %'].dtype == 'O':
        df['Bonus %'] = df['Bonus %'].str.replace('%', '', regex=True).astype(float).fillna(0)
        # Check if values are > 1 (like 15) and convert to decimal
        df['Bonus %'] = df['Bonus %'].apply(lambda x: x/100 if x > 1 else x)
        
    # 3. Standardize Attrition Flag
    df['is_exited'] = df['is_exited'].str.upper().fillna('NO')
    
    # 4. Define Job Levels for Insight 5
    def get_job_level(title):
        title = str(title).lower()
        if 'vice president' in title or 'vp' in title: return 'Executive (VP)'
        elif 'director' in title: return 'Director'
        elif 'manager' in title or 'manger' in title or 'architect' in title: return 'Manager'
        elif 'sr.' in title or 'senior' in title: return 'Senior Professional'
        else: return 'Professional/Analyst'
    
    df['Job_Level'] = df['Job Title'].apply(get_job_level)
    
    # 5. Create Age Groups (Updated bins to be more inclusive)
    df['Age_Group'] = pd.cut(df['Age'], bins=[0, 30, 40, 50, 100], labels=['<30', '31-40', '41-50', '51+'])
    
    return df

try:
    df = load_data()
    
    # Create Tabs for the 5 Insights
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Attrition Hotspots", 
        "Gender Pay Gap", 
        "Resource Allocation", 
        "Geographic Optimization", 
        "Promotion Bottleneck"
    ])

    with tab1:
        st.subheader("1. Attrition Hotspots by Business Unit")
        attrition_data = df.groupby('Business Unit')['is_exited'].apply(lambda x: (x == 'YES').mean() * 100).reset_index()
        attrition_data.columns = ['Business Unit', 'Attrition Rate (%)']
        fig1 = px.bar(attrition_data.sort_values('Attrition Rate (%)'), 
                      x='Attrition Rate (%)', y='Business Unit', orientation='h',
                      color='Attrition Rate (%)', color_continuous_scale='Reds')
        st.plotly_chart(fig1, use_container_width=True)
        st.info("R&D and Manufacturing show the highest attrition risk[cite: 16].")

    with tab2:
        st.subheader("2. Gender Pay Gap Analysis")
        gender_pay = df.groupby('Gender')['Annual Salary'].mean().reset_index()
        fig2 = px.bar(gender_pay, x='Gender', y='Annual Salary', 
                      color='Gender', color_discrete_sequence=['#FF69B4', '#1E90FF'])
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.subheader("3. Departmental Headcount Allocation")
        dept_counts = df['Department'].value_counts().reset_index()
        fig3 = px.pie(dept_counts, values='count', names='Department', hole=0.4)
        st.plotly_chart(fig3, use_container_width=True)
        st.info("IT accounts for nearly 25% of the workforce share.")

    with tab4:
        st.subheader("4. Geographic Labor Cost Variance")
        geo_pay = df.groupby('Country')['Annual Salary'].mean().reset_index().sort_values('Annual Salary')
        fig4 = px.bar(geo_pay, x='Country', y='Annual Salary', color='Annual Salary', color_continuous_scale='Viridis')
        st.plotly_chart(fig4, use_container_width=True)

    with tab5:
        st.subheader("5. Talent Pipeline: The Promotion Bottleneck")
        # Creating a robust crosstab
        bottleneck = pd.crosstab(df['Age_Group'], df['Job_Level'], normalize='index') * 100
        bottleneck = bottleneck.reset_index().melt(id_vars='Age_Group')
        
        fig5 = px.bar(bottleneck, x='Age_Group', y='value', color='Job_Level',
                     labels={'value': 'Percentage %', 'Age_Group': 'Age Bracket'},
                     barmode='stack', color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig5, use_container_width=True)
        st.warning("Note the stagnation of mid-career employees in Manager/Professional roles.")

except Exception as e:
    st.error(f"Error loading data: {e}. Ensure 'Refined_Employee_Database.csv' is in the root folder.")

# Recommendations Sidebar
st.sidebar.title("Strategic Actions")
st.sidebar.markdown("""
* **Retention:** Focus on R&D Leads.
* **Equity:** Pay parity audit.
* **Efficiency:** IT Department review.
* **Mobility:** Clearer tracks for mid-career talent[cite: 54].
""")
