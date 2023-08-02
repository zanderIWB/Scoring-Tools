import pandas as pd
import streamlit as st

# Main function for the Streamlit application
def main():
    st.title("Excel Table Viewer")
    df = pd.read_excel("Test_Database.xlsx", engine="openpyxl")

    no_tickbox_columns = ["Product"]
    non_numeric_columns = ["Product"]
    bad_columns = ["Cost of Production"]

    selectable_columns = df.columns.tolist()
    selectable_columns = [col for col in selectable_columns if col not in no_tickbox_columns]

    # Create an expander for column selection
    column_expander = st.expander("Column Selection")

    # Get selected columns using tickboxes
    selected_columns = []
    num_columns = 3
    col1, col2, col3 = column_expander.columns(num_columns)

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

    # Include no_tickbox_columns as the leftmost column
    selected_columns = no_tickbox_columns + selected_columns

    # Add an expander for setting weights
    weights_expander = st.expander("Set Weights")

    # Create sliders for weights in a 3-column format
    weights = []
    num_weight_columns = 3
    weight_col1, weight_col2, weight_col3 = weights_expander.columns(num_weight_columns)

    for i, column in enumerate(selected_columns[1:]):
        if column in non_numeric_columns:
            continue

        if i % num_columns == 0:
            target_column = weight_col1
        elif i % num_columns == 1:
            target_column = weight_col2
        else:
            target_column = weight_col3

        if column in bad_columns:
            weight = target_column.slider(f"Weight for {column}", min_value=1, max_value=10, value=5, step=1)
        else:
            weight = target_column.slider(f"Weight for {column}", min_value=1, max_value=10, value=5, step=1)

        weights.append(weight)

    # Filter the DataFrame based on selected columns
    filtered_df = df[selected_columns]

    # Calculate the weighted sum
    weighted_sum = 0
    total_weight = 0

    for i, column in enumerate(selected_columns[1:]):
        if column in non_numeric_columns:
            continue

        normalized_column = (filtered_df[column] - filtered_df[column].min()) / (
            filtered_df[column].max() - filtered_df[column].min()
        )

        if column in bad_columns:
            weighted_sum -= normalized_column * weights[i]
        else:
            weighted_sum += normalized_column * weights[i]

        total_weight += abs(weights[i])

    # Calculate the weighted average
    weighted_average = weighted_sum / total_weight

    # Scale the weighted average to the range of 0 to 10
    scaled_score = 0 + weighted_average * (10 - 0)

    # Round the score to 2 decimal places
    rounded_score = round(scaled_score, 2)

    # Display the score with 2 decimal places without trailing zeros
    filtered_df["Score"] = rounded_score.round(2)
    filtered_df["Score"] = filtered_df["Score"].apply(
        lambda x: str(x).rstrip("0").rstrip(".") if isinstance(x, float) else x
    )

    # Remove unticked columns from the sort by dropdown options
    selectable_sort_by = [column for column in selected_columns[1:]] + ["Score"]
    sort_by = st.selectbox("Sort By", [None] + selectable_sort_by, key="sort_by")

    # Sort the DataFrame based on the selected column
    if sort_by is not None:
        sort_order = st.radio("Sort Order", ["Descending", "Ascending"], index=0, key="sort_order")
        if sort_by == "Score":
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=(sort_order == "Ascending"), ignore_index=True)
        else:
            ascending = sort_order == "Ascending"
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)

    # Reset the index to start from 1
    filtered_df.index = range(1, len(filtered_df) + 1)

    # Display the filtered DataFrame
    st.table(filtered_df)


if __name__ == "__main__":
    main()
