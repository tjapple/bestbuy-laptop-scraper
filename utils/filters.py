import streamlit as st
import pandas as pd


def make_numeric_slider(df, spec, label, numeric_type, fill_na):
    series = pd.to_numeric(df[spec], errors='coerce')
    series = series.fillna(0) if fill_na else series.dropna()
    df[spec] = df[spec].fillna(0) if fill_na else df[spec].dropna()

    if numeric_type == 'int':
        series = series.astype(int)
    elif numeric_type == 'float':
        series = series.astype(float)
    
    min_value = series.min()
    max_value = series.max()
  
    range = st.slider(label, min_value=min_value, max_value=max_value, value=(min_value, max_value))
    return range

def make_dropdown(df, spec, label):
    options = sorted(df[spec].fillna('N/A').unique())
    selected_options = []
    with st.expander(label):
        col1, col2 = st.columns(2)
        if col1.button("Select All", key=f"select_all_{spec}"):
            for op in options:
                st.session_state[f"{spec}_{op}"] = True
        if col2.button("Deselect All", key=f"deselect_all_{spec}"):
            for op in options:
                st.session_state[f"{spec}_{op}"] = False

        for op in options:
            check = st.checkbox(op, value=True, key=f'{spec}_{op}')
            if check: 
                selected_options.append(op)
    return selected_options

def remove_outliers(df, spec):
    """
    Returns a Series from df[spec] with values outside the IQR bounds replaced by NaN.
    This preserves the original index so you can assign it back to the DataFrame.
    """
    q1 = df[spec].quantile(0.25)
    q3 = df[spec].quantile(0.75)
    IQR = q3 - q1
    lower_bound = q1 - 1.5 * IQR
    upper_bound = q3 + 1.5 * IQR
    # Replace outliers with NaN while preserving the original index
    return df[spec].where((df[spec] >= lower_bound) & (df[spec] <= upper_bound))
