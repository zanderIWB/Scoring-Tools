import pandas as pd
import streamlit as st

# Main function for the Streamlit application
def main():
    st.title("Excel Table Viewer")
    df = pd.read_excel("Test_Database.xlsx", engine="openpyxl")

    # Remove "Product" from selectable columns
    selectable_columns = df.columns.tolist()
    selectable_columns.remove("Product")

    # Create tickboxes for column selection in three columns
    num_columns = 3
    col1, col2, col3 = st.columns(num_columns)

    selected_columns = []
    selected_column_keys = []  # To store unique keys for selected columns
    for i, column in enumerate(selectable_columns):
        if i % num_columns == 0:
            target_column = col1
        elif i % num_columns == 1:
            target_column = col2
        else:
            target_column = col3

        key = f"checkbox_{column}"  # Unique key for each checkbox
        checkbox = target_column.checkbox(column, value=True, key=key)
        if checkbox:
            selected_columns.append(column)
            selected_column_keys.append(key)

    # Include "Product" as the leftmost column
    selected_columns = ["Product"] + selected_columns

    # Filter the DataFrame based on selected columns
    filtered_df = df[selected_columns]

    # Remove unticked columns from the sort by dropdown options
    selectable_sort_by = [column for column in selected_columns if column != "Product"]
    sort_by = st.selectbox("Sort By", [None] + selectable_sort_by, key="sort_by")

    # Sort the DataFrame based on the selected column
    if sort_by is not None:
        sort_order = st.radio("Sort Order", ["Descending", "Ascending"], index=0, key="sort_order")
        ascending = True if sort_order == "Ascending" else False
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)

    # Reset the index to start from 1
    filtered_df.index = range(1, len(filtered_df) + 1)

    st.table(filtered_df)

if __name__ == "__main__":
    main()






