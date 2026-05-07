import streamlit as st
import pandas as pd
import plotly.express as px

# Set Page Config
st.set_page_config(page_title="Workforce Strategy Dashboard", layout="wide")

# Title and Description
st.title("📊 Global Workforce Strategic Insights")
st.markdown("""
This dashboard presents 5 high-value insights derived from the Employee Database, 
focusing on attrition, equity, resource allocation, and talent pipeline health.
""")

# Load and Clean Data
@st.cache_data
def load_data():
    # Load file
    df = pd.read_csv('Refined_Employee_Database.csv')
    
    # 1. Clean Salary Column: Force string -> remove characters -> force float
    df['Annual Salary'] = df['Annual Salary'].astype(str).str.replace(r'[\$,]', '', regex=True)
    df['Annual Salary'] = pd.to_numeric(df['Annual Salary'], errors='coerce')
    
    # 2. Clean Bonus Column
    df['Bonus %'] = df['Bonus %'].astype(str).str.replace(r'%', '', regex=True)
    df['Bonus %'] = pd.to_numeric(df['Bonus %'], errors='coerce') / 100
        
    # 3. Standardize Attrition Flag
    df['is_exited'] = df['is_exited'].astype(str).str.upper()
    
    # 4. Define Job Levels for Insight 5
    def get_job_level(title):
        title = str(title).lower()
        if 'vice president' in title or 'vp' in title: return 'Executive (VP)'
        elif 'director' in title: return 'Director'
        elif 'manager' in title or 'manger' in title or 'architect' in title: return 'Manager'
        elif 'sr.' in title or 'senior' in title: return 'Senior Professional'
        else: return 'Professional/Analyst'
    
    df['Job_Level'] = df['Job Title'].apply(get_job_level)
    
    # 5. Create Age Groups
    df['Age_Group'] = pd.cut(df['Age'], bins=[20, 30, 40, 50, 65], labels=['20-30', '31-40', '41-50', '51+'])
    
    return df

df = load_data()

# --- INSIGHT 1 & 3: ATTRITION & HEADCOUNT ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Attrition Hotspots by Business Unit")
    attrition_data = df.groupby('Business Unit')['is_exited'].apply(lambda x: (x == 'YES').mean() * 100).reset_index()
    attrition_data.columns = ['Business Unit', 'Attrition Rate (%)']
    fig1 = px.bar(attrition_data.sort_values('Attrition Rate (%)'), 
                  x='Attrition Rate (%)', y='Business Unit', orientation='h',
                  color='Attrition Rate (%)', color_continuous_scale='Reds')
    st.plotly_chart(fig1, width="stretch")
    st.info("R&D and Manufacturing show the highest attrition risk.")

with col2:
    st.subheader("3. Departmental Headcount Allocation")
    dept_counts = df['Department'].value_counts().reset_index()
    fig3 = px.pie(dept_counts, values='count', names='Department', hole=0.4,
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig3, width="stretch")
    st.info("IT accounts for the largest share of organizational overhead.")

st.divider()

# --- INSIGHT 2 & 4: PAY GAP & GEOGRAPHY ---
col3, col4 = st.columns(2)

with col3:
    st.subheader("2. Gender Pay Gap Analysis")
    gender_pay = df.groupby('Gender')['Annual Salary'].mean().reset_index()
    fig2 = px.bar(gender_pay, x='Gender', y='Annual Salary', 
                  color='Gender', color_discrete_sequence=['#FF69B4', '#1E90FF'])
    st.plotly_chart(fig2, width="stretch")
    st.info("Average salary comparison highlights a potential equity gap.")

with col4:
    st.subheader("4. Geographic Labor Cost Variance")
    geo_pay = df.groupby('Country')['Annual Salary'].mean().reset_index().sort_values('Annual Salary')
    fig4 = px.bar(geo_pay, x='Country', y='Annual Salary', color='Annual Salary',
                  color_continuous_scale='Viridis')
    st.plotly_chart(fig4, width="stretch")
    st.info("Disparity in labor costs suggests opportunities for regional optimization.")

st.divider()

# --- INSIGHT 5: PROMOTION BOTTLENECK ---
st.subheader("5. Talent Pipeline: The Promotion Bottleneck")
# Distribution of Job Levels across Age Groups
bottleneck_data = pd.crosstab(df['Age_Group'], df['Job_Level'], normalize='index') * 100
bottleneck_data = bottleneck_data.reset_index().melt(id_vars='Age_Group')

fig5 = px.bar(bottleneck_data, x='Age_Group', y='value', color='Job_Level',
             title="Representation % by Age Group",
             labels={'value': 'Percentage of Age Group', 'Age_Group': 'Age Category'},
             barmode='stack', color_discrete_sequence=px.colors.qualitative.Safe)

st.plotly_chart(fig5, width="stretch")
st.warning("Note: A high percentage of the 31-40 and 41-50 age groups remain in 'Manager' or 'Professional' tiers, indicating a lack of upward mobility into Director/VP roles.")

# Summary Note
st.sidebar.title("Key Recommendations")
st.sidebar.markdown("""
- **Retention:** Launch a retention program for R&D Technical Leads.
- **Equity:** Conduct a formal pay-parity audit.
- **Scaling:** Evaluate moving back-office IT roles to Brazil or China.
- **Mobility:** Create 'Expert Tracks' for tenured mid-career staff.
""")
