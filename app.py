import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Basic Setup
st.set_page_config(page_title="Workforce Strategy", layout="wide")
st.title("📊 Global Workforce Strategic Insights")
st.markdown("This is the Safe Mode Dashboard to ensure charts render correctly.")

try:
    # 2. Safest Data Loading (No Cache)
    df = pd.read_csv('Refined_Employee_Database.csv')
    df.columns = df.columns.str.strip() # Strip invisible spaces
    
    # Aggressively rename columns to catch typos
    for col in df.columns:
        if 'salary' in str(col).lower(): df.rename(columns={col: 'Annual Salary'}, inplace=True)
        if 'exited' in str(col).lower(): df.rename(columns={col: 'is_exited'}, inplace=True)
        if 'bonus' in str(col).lower(): df.rename(columns={col: 'Bonus %'}, inplace=True)

    # Clean the numbers strictly (strip everything except numbers and decimals)
    if 'Annual Salary' in df.columns:
        df['Annual Salary'] = pd.to_numeric(df['Annual Salary'].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce')

    # Tell us it worked
    st.success("✅ Data successfully loaded! Drawing charts below...")

    # 3. CHART 1: Attrition (No custom colors)
    st.subheader("1. Attrition Hotspots")
    if 'is_exited' in df.columns and 'Business Unit' in df.columns:
        df['attrition_num'] = df['is_exited'].astype(str).str.upper().eq('YES').astype(int)
        attr_data = df.groupby('Business Unit')['attrition_num'].mean().reset_index()
        attr_data['attrition_num'] *= 100
        
        fig1 = px.bar(attr_data, x='attrition_num', y='Business Unit', orientation='h', title="Attrition % by Unit")
        st.plotly_chart(fig1)

    # 4. CHART 2: Headcount (No custom colors)
    st.subheader("2. Department Headcount")
    if 'Department' in df.columns:
        dept_counts = df['Department'].value_counts().reset_index()
        fig2 = px.pie(dept_counts, values='count', names='Department', title="Employees per Department")
        st.plotly_chart(fig2)

    # 5. CHART 3: Gender Pay (No custom colors)
    st.subheader("3. Gender Pay Gap")
    if 'Gender' in df.columns and 'Annual Salary' in df.columns:
        gender_pay = df.groupby('Gender')['Annual Salary'].mean().reset_index()
        fig3 = px.bar(gender_pay, x='Gender', y='Annual Salary', title="Average Salary by Gender")
        st.plotly_chart(fig3)

    # 6. CHART 4: Geography (No custom colors)
    st.subheader("4. Geographic Labor Costs")
    if 'Country' in df.columns and 'Annual Salary' in df.columns:
        geo_pay = df.groupby('Country')['Annual Salary'].mean().reset_index()
        fig4 = px.bar(geo_pay, x='Country', y='Annual Salary', title="Average Salary by Country")
        st.plotly_chart(fig4)

except Exception as e:
    # If it fails, print the exact error in red
    st.error(f"🚨 Python Error: {e}")
    
