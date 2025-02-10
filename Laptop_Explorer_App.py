import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from utils.data_managers import load_data
from utils.filters import make_dropdown, make_numeric_slider, remove_outliers


def main():
    st.title("Filtered Laptops")
    
    # LOAD DATA
    full_df = load_data()    

    # CREATE SIDEBAR FILTERS THEN FILTER THE DATAFRAME
    with st.sidebar:
       
        # Key Specs
        st.title("General")
        selected_brands = make_dropdown(full_df, 'brand', "Brand(s)")
        selected_os = make_dropdown(full_df, 'operating_system', "OS")
        selected_windows_ai = make_dropdown(full_df, 'windows_ai', "Windows AI")
        two_in_one_filter = st.radio("Two-in-One", options=['All', 'Only True', 'Only False'], index=0)
        refurbished_filter = st.radio("Refurbished", options=['All', 'Only True', 'Only False'], index=0)
        year_of_release_range = make_numeric_slider(full_df, 'year_of_release', "Year of Release", 'int', False)
        battery_life_range = make_numeric_slider(full_df, 'battery_life_hrs', "Reported Battery Life (hrs)", 'int', True)
        price_range = make_numeric_slider(full_df, 'price', "Price", 'float', True)

        st.title("Chippys")
        selected_cpus = make_dropdown(full_df, 'processor_model', "CPU Series")
        selected_gpus = make_dropdown(full_df, 'graphics', "GPU")
        selected_ssd_interfaces = make_dropdown(full_df, 'solid_state_drive_interface', "SSD Interface")
        selected_ram_type = make_dropdown(full_df, 'type_of_memory_ram', "RAM Type")
        selected_storage_type = make_dropdown(full_df, 'storage_type', "Storage Type")
        ram_range = make_numeric_slider(full_df, 'system_memory_ram_gb', "RAM (GB)", 'int', True)
        storage_range = make_numeric_slider(full_df, 'total_storage_capacity_gb', "Storage (GB)", 'int', True)
        
        st.title("Physical Specs")
        selected_materials = make_dropdown(full_df, 'casing_material', "Casing Material")
        weight_range = make_numeric_slider(full_df, 'product_weight_lbs', "Laptop Weight (lbs)", 'float', True)

        st.title("Display")
        touchscreen_filter = st.radio("Touch Screen", options=['All', 'True', 'False'], index=0)
        selected_resolutions = make_dropdown(full_df, 'screen_resolution', "Screen Resolution")
        screen_size_range = make_numeric_slider(full_df,'screen_size_inches', "Screen Size (inches)", 'int', True)
        refresh_rate_range = make_numeric_slider(full_df, 'refresh_rate_hz', "Refresh Rate (hz)", 'int', True)
        brightness_range = make_numeric_slider(full_df, 'brightness', "Brightness (nits)", 'int', True)

    
        # APPLY FILTERS TO full_df
        filtered_full_df = full_df[
            (full_df['battery_life_hrs'].between(battery_life_range[0], battery_life_range[1], inclusive='both')) &
            ((full_df['brand'].isin(selected_brands)) | (full_df['brand'].isna())) &
            (full_df['brightness'].between(brightness_range[0], brightness_range[1], inclusive='both')) &
            ((full_df['casing_material'].isin(selected_materials)) | (full_df['casing_material'].isna())) & 
            ((full_df['graphics'].isin(selected_gpus)) | (full_df['graphics'].isna())) &
            ((full_df['operating_system'].isin(selected_os)) | (full_df['operating_system'].isna())) &
            ((full_df['price'].between(price_range[0], price_range[1], inclusive='both'))) &
            ((full_df['processor_model'].isin(selected_cpus)) | (full_df['processor_model'].isna())) &
            (full_df['product_weight_lbs'].between(weight_range[0], weight_range[1], inclusive='both')) &
            (full_df['refresh_rate_hz'].between(refresh_rate_range[0], refresh_rate_range[1], inclusive='both')) &
            ((full_df['screen_resolution'].isin(selected_resolutions)) | (full_df['screen_resolution'].isna())) &
            (full_df['screen_size_inches'].between(screen_size_range[0], screen_size_range[1], inclusive='both')) &
            ((full_df['solid_state_drive_interface'].isin(selected_ssd_interfaces)) | (full_df['solid_state_drive_interface'].isna())) &
            ((full_df['storage_type'].isin(selected_storage_type)) | (full_df['storage_type'].isna())) &
            (full_df['system_memory_ram_gb'].between(ram_range[0], ram_range[1], inclusive='both')) &
            (full_df['total_storage_capacity_gb'].between(storage_range[0], storage_range[1], inclusive='both')) &
            ((full_df['type_of_memory_ram'].isin(selected_ram_type)) | (full_df['type_of_memory_ram'].isna())) & 
            ((full_df['windows_ai'].isin(selected_windows_ai)) | (full_df['windows_ai'].isna())) &
            (full_df['year_of_release'].between(year_of_release_range[0], year_of_release_range[1], inclusive='both')) &
            (np.logical_or(touchscreen_filter == "All", full_df["touch_screen"] == (touchscreen_filter == "Yes"))) &
            (np.logical_or(two_in_one_filter == "All", full_df["two_in_one_design"] == (two_in_one_filter == "Yes"))) &
            (np.logical_or(refurbished_filter == "All", full_df["product_name"].str.contains("refurb", case=False, na=False) == (refurbished_filter == "True")))
        ]
        # Clean
        filtered_full_df.loc[:, 'battery_life_hrs'] = remove_outliers(filtered_full_df, 'battery_life_hrs')
        filtered_full_df.loc[:, "date"] = pd.to_datetime(filtered_full_df["timestamp"]).dt.date



    # --------------------------------------------------------------------
    # CREATE THE LATEST, UNIQUE, AND FILTERED DF FOR DISPLAY
    # --------------------------------------------------------------------
    most_recent_date = filtered_full_df['timestamp'].max().date()
    latest_df = filtered_full_df[filtered_full_df['timestamp'].dt.date == most_recent_date]
    latest_df = (latest_df.sort_values('timestamp').groupby('upc', as_index=False).tail(1))
    latest_df['year_of_release'] = latest_df['year_of_release'].astype(int).astype(str)
    organized_columns = ['battery_life_hrs', 'price', 'discount_percentage', 'product_name', 
                         'processor_model', 'processor_model_number', 
                         'graphics', 'graphics_type',
                         'system_memory_ram_gb', 'type_of_memory_ram',
                         'storage_type', 'solid_state_drive_interface', 'total_storage_capacity_gb',
                         'screen_size_inches','screen_resolution','refresh_rate_hz','screen_type','display_type','brightness',
                         'year_of_release', 'product_weight_lbs', 'casing_material',
                        'link', 'upc']
    latest_df = latest_df[organized_columns]

    
    # SORT OPTIONS
    col1, col2 = st.columns([1, 2])
    with col1:
        sort_option = st.selectbox(
            "Sort by:",
            options=[
                "Price: Low to High",
                "Price: High to Low",
                "Discount: High to Low",
            ],
            index=0
        )
        if sort_option == "Price: Low to High":
            sorted_df = latest_df.sort_values("price", ascending=True)
        elif sort_option == "Price: High to Low":
            sorted_df = latest_df.sort_values("price", ascending=False)
        elif sort_option == "Discount: High to Low":
            sorted_df = latest_df.sort_values("discount_percentage", ascending=False)
        else:
            sorted_df = latest_df
    with col2:
        # Display the result count, right-aligned
        st.markdown(f"<h5 style='text-align: right;'>\n{len(sorted_df)} Results</h5>", unsafe_allow_html=True)

    # DISPLAY
    edited_df = st.data_editor(
        sorted_df.head(100),
        column_config={
            "link": st.column_config.LinkColumn("link"),
        },
        hide_index=True,
        width=None,  # Let it auto-size
    )

        
    st.markdown(
        '<div style="height: 6px; background-color: #404040; margin: 10px -50px;"></div>',
        unsafe_allow_html=True
    )



    # ----------------------------------------------------------------
    # CREATE PLOTS
    # ----------------------------------------------------------------

    # MOST RECENT DATA
    st.subheader("Current Relationships")
    col1, col2, col3 = st.columns(3)
    with col1:
        y_option = st.selectbox(
            "y-axis",
            options=[
                'price',
                'discount_percentage'
            ],
            index=0
        )
    with col2:
        x_option = st.selectbox(
            'x-axis',
            options=[
                'processor_model', 
                'processor_model_number',
                'brand',
                'graphics',
                'system_memory_ram_gb',
                'total_storage_capacity_gb',
                'display_type',
                'year_of_release',
                'casing_material',
                'product_weight_lbs',
                'battery_life_hrs',
                'screen_size_inches'
            ],
            index=0
        )
    with col3:
        color_option = st.selectbox(
            "color",
            options=[
                'brand',
                'processor_model', 
                'processor_model_number',
                'graphics',
                'system_memory_ram_gb',
                'total_storage_capacity_gb',
                'display_type',
                'year_of_release',
                'casing_material',
                'product_weight_lbs',
                'battery_life_hrs',
                'screen_size_inches'

            ],
            index=0
        )

    fig_scatter = px.scatter(
        filtered_full_df,
        x=x_option,
        y=y_option,
        color=color_option,
        hover_data=['price',
                    "processor_model",
                    "battery_life_hrs",
                    'total_storage_capacity_gb',
                    'system_memory_ram_gb',
                    'product_name'],
        color_continuous_scale=px.colors.diverging.RdBu

    )
    fig_scatter.update_layout(
        xaxis_title=f"{x_option}",
        yaxis_title=f"{y_option}"
    )
    st.plotly_chart(fig_scatter, use_container_width=False)

    st.markdown(
        '<div style="height: 3px; background-color: #404040; margin: 10px -50px;"></div>',
        unsafe_allow_html=True
    )


    # HISTORICAL DATA
    st.subheader("Historical Price Trends")
    df_historical = filtered_full_df.copy()

    col_measure, col_thresh, col_spec = st.columns(3)
    with col_measure:
        measure_choice = st.selectbox(
            "Measure",
            options=["Number of Laptops Discounted", "Average Discount", "Average Price"],
            index=0
        )
    with col_thresh:
        if measure_choice == "Number of Laptops Discounted":
            discount_threshold = st.selectbox(
                "Discount Threshold",
                options=list(range(0, 101, 5)),
                index=2,  # default e.g., 10%
                format_func=lambda x: f"{x}%"
            )
        else:
            st.markdown("<div style='opacity: 0.5;'>Discount Threshold (disabled)</div>", unsafe_allow_html=True)
            discount_threshold = None
    with col_spec:
        spec = st.selectbox(
            "Spec",
            options=[
                'brand',
                'processor_model', 
                'processor_model_number',
                'graphics',
                'system_memory_ram_gb',
                'total_storage_capacity_gb',
                'display_type',
                'year_of_release',
                'casing_material',
                'product_weight_lbs',
                'battery_life_hrs',
                'screen_size_inches'
            ],
            index=0
        )

    if measure_choice == "Number of Laptops Discounted":
        df_filtered = df_historical[df_historical["discount_percentage"] >= discount_threshold]
        agg_df = df_filtered.groupby(["date", spec], as_index=False).agg(Count=("upc", "count"))
        fig = px.line(
            agg_df,
            x="date",
            y="Count",
            color=spec,
            markers=True,
            title=f"Number of Laptops with Discount >= {discount_threshold}%"
        )
        y_axis_title = "Count"
    elif measure_choice == "Average Discount":
        agg_df = df_historical.groupby(["date", spec], as_index=False).agg(AvgDiscount=("discount_percentage", "mean"))
        fig = px.line(
            agg_df,
            x="date",
            y="AvgDiscount",
            color=spec,
            markers=True,
            title="Average Discount Percentage"
        )
        y_axis_title = "Average Discount (%)"
    else:
        agg_df = df_historical.groupby(["date", spec], as_index=False).agg(AvgPrice=("price", "mean"))
        fig = px.line(
            agg_df,
            x="date",
            y="AvgPrice",
            color=spec,
            markers=True,
            title="Average Price"
        )
        y_axis_title = "Average Price ($)"
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=y_axis_title,
    )
    st.plotly_chart(fig, use_container_width=True)

#TODO:  API to cpu benchmark???

if __name__ == "__main__":
    main()
