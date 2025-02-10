import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_managers import load_data, load_upc_watchlist, write_upc_watchlist




def manage_watchlist():
    watchlist = load_upc_watchlist()

    # --- Section to Display and Remove UPC Codes ---
    with st.sidebar:
        st.title("Manage Watchlist")
        new_upc = st.text_input("Enter new UPC code to add:")
        if st.button("Add UPC"):
            if new_upc.strip() == "":
                st.error("UPC code cannot be empty.")
            elif not new_upc.strip().isdigit():
                st.error("UPC code must be numeric.")
            elif new_upc.strip() in watchlist:
                st.warning("UPC code is already in the watchlist.")
            else:
                watchlist.append(new_upc.strip())
                write_upc_watchlist(watchlist)
                st.success(f"Added UPC {new_upc.strip()} to the watchlist.")
        if watchlist:
            # Create a simulated table header
            col_header1, col_header2 = st.columns(2)
            col_header1.markdown("**UPC**")
            col_header2.markdown("**Action**")

            # For each UPC, create a row with the UPC and a remove button.
            for upc in watchlist:
                col1, col2 = st.columns(2)
                col1.write(upc)
                if col2.button("Remove", key=f"remove_{upc}"):
                    watchlist.remove(upc)
                    write_upc_watchlist(watchlist)
                    st.success(f"Removed UPC {upc} from the watchlist.")
        else:
            st.info("No UPC codes in the watchlist yet.")




def main():
    st.title("Watchlist")
    st.subheader('Watchlist Historical Prices')

    # Get data
    full_df = load_data() 
    upc_watchlist = load_upc_watchlist()

    df_watch = full_df[full_df['upc'].isin(upc_watchlist)].copy()
    df_watch.loc[:, "date"] = pd.to_datetime(df_watch["timestamp"]).dt.date
    df_watch = df_watch.sort_values(by=["upc", "date"])

    # Plot data
    fig = px.line(
        df_watch,
        x="date",
        y="price",
        color="upc",
        hover_data=['price',
                    'discount_percentage',
                    'screen_size_inches',
                    'product_weight_lbs',
                    "processor_model",
                    'processor_model_number',
                    "battery_life_hrs",
                    'total_storage_capacity_gb',
                    'system_memory_ram_gb',
                    'product_name'],
        markers=True,
        title="Price History of Watchlist Items"
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price",
        title_x=0.5  # Center the title
    )
    st.plotly_chart(fig, use_container_width=True)


    # Create a table mapping upc to product name with clickable link
    st.subheader("Product Links")
    unique_products = df_watch.groupby('upc').first().reset_index()

    table_md = "| UPC | Product Name |\n| --- | --- |\n"
    for _, row in unique_products.iterrows():
        table_md += f"| {row['upc']} | [{row['product_name']}]({row['link']}) |\n"

    st.markdown(table_md, unsafe_allow_html=True)

    manage_watchlist()

if __name__ == "__main__":
    main()
