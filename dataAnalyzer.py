import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Auto-EDA Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("Data Analyzer")
st.caption("This application generates a graph of your choice on the given data.")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    st.sidebar.header("Categorical Filters")
    
    for col in categorical_cols:
        if df[col].nunique() < 30:
            unique_options = df[col].dropna().unique()

            selected_options = st.sidebar.multiselect(
                f"Filter by {col}",
                options = unique_options,
                default = unique_options
            )
            df = df[df[col].isin(selected_options)]
    st.sidebar.markdown("---")
    st.sidebar.header("Numerical Range Filters")

    for col in numeric_cols:
        min_val = float(df[col].min())
        max_val = float(df[col].max())
        
        if min_val < max_val:
            st.sidebar.markdown(f"**{col}**")
            
            input_mode = st.sidebar.radio(
                "Input Mode", 
                options=["Slider", "Manual Input"], 
                key=f"mode_{col}", 
                horizontal=True,
                label_visibility="collapsed"
            )
            
            if input_mode == "Slider":
                selected_range = st.sidebar.slider(
                    f"Select range for {col}",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                    key=f"slider_{col}",
                    label_visibility="collapsed"
                )
            else:
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    min_input = st.number_input(
                        f"Min {col}",
                        value=min_val,
                        key=f"min_{col}"
                    )
                with col2:
                    max_input = st.number_input(
                        f"Max {col}",
                        value=max_val,
                        key=f"max_{col}"
                    )
                selected_range = (min_input, max_input)
            
            df = df[
                (df[col] >= selected_range[0]) & 
                (df[col] <= selected_range[1])
            ]
    st.write(f"Filtered Dataset Rows: {len(df)}")
    st.subheader("📊 Dynamic Data Visualizer")

    if len(numeric_cols)>0:
        selected_metric_col = st.selectbox("Choose a column to summarize:", options=numeric_cols)
        
        with st.container(border=True):
            st.subheader("📈 Quick Overview")
            col1, col2 = st.columns(2)
            col1.metric(label=f"Average {selected_metric_col}", value=round(df[selected_metric_col].mean(), 2))
            col2.metric(label="Total Rows Matching Filters", value=len(df))
        st.markdown("---")

        st.write("-> Display Chart")
        col_x = st.selectbox("Choose X axis", options=df.columns)
        col_y = st.selectbox("Choose y axis (Numerical)", options=numeric_cols)

        chart_choice = st.radio("Select Chart Type:", ["Line Chart", "Bar Chart", "Scatter Chart"], horizontal=True)
        if chart_choice == "Line Chart" or chart_choice == "Bar Chart":
            chart_data = df.groupby(col_x, as_index=False)[col_y].mean()
        
            if chart_choice == "Line Chart":
                st.line_chart(data=chart_data, x=col_x, y=col_y)
            else:
                st.bar_chart(data=chart_data, x=col_x, y=col_y)
            
        else:
            st.scatter_chart(data=df, x=col_x, y=col_y)

        with st.expander("📈 View Dataset Summary Statistics"):
            st.write(df.describe())
    else:
        st.warning("⚠️ The uploaded dataset doesn't contain any numerical columns to build charts or metrics.")
else:
    st.info("👆 Please upload a CSV file to get started!")

