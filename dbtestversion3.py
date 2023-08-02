import pandas as pd
import streamlit as st

# Main function for the Streamlit application
def main():
    st.title("Excel Table Viewer")
    df = pd.read_excel("Test_Database.xlsx", engine="openpyxl")

    # Remove "Product" from selectable columns
    selectable_columns = df.columns.tolist()
    selectable_columns.remove("Product")

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

    # Include "Product" as the leftmost column
    selected_columns = ["Product"] + selected_columns

    # Add an expander for setting weights
    weights_expander = st.expander("Set Weights")

    # Create sliders for weights in a 3-column format
    weights = []
    num_weight_columns = 3
    weight_col1, weight_col2, weight_col3 = weights_expander.columns(num_weight_columns)

    for i, column in enumerate(selected_columns[1:]):
        if i % num_weight_columns == 0:
            target_column = weight_col1
        elif i % num_weight_columns == 1:
            target_column = weight_col2
        else:
            target_column = weight_col3

        weight = target_column.slider(f"Weight for {column}", min_value=1, max_value=10, value=5, step=1)
        weights.append(weight)

    # Filter the DataFrame based on selected columns
    filtered_df = df[selected_columns]

    # Normalize the selected columns using Min-Max scaling
    normalized_df = (filtered_df.iloc[:, 1:] - filtered_df.iloc[:, 1:].min()) / (
        filtered_df.iloc[:, 1:].max() - filtered_df.iloc[:, 1:].min()
    )

    # Calculate the weighted average
    weighted_average = 0

    for i, column in enumerate(selected_columns[1:]):
        if column == "Cost of Production":  # "bad" column
            weighted_average -= normalized_df[column] * weights[i]
        else:  # "good" column
            weighted_average += normalized_df[column] * weights[i]

    weighted_average /= sum(weights)  # Divide by the sum of weights

    # Scale the weighted score to the range of 0 to 10
    weighted_score_min = 0  # Minimum value for weighted score
    weighted_score_max = 10  # Maximum value for weighted score
    scaled_score = weighted_score_min + weighted_average * (weighted_score_max - weighted_score_min)  # Scale to the desired range

    # Round the score to 2 decimal places
    rounded_score = scaled_score.round(2)

    # Add the rounded score as a new column
    filtered_df["Score"] = rounded_score

    # Remove unticked columns from the sort by dropdown options
    selectable_sort_by = [column for column in selected_columns[1:-1] if column != "Product"] + ["Score"]
    sort_by = st.selectbox("Sort By", [None] + selectable_sort_by, key="sort_by")

    # Sort the DataFrame based on the selected column
    if sort_by is not None:
        sort_order = st.radio("Sort Order", ["Descending", "Ascending"], index=0, key="sort_order")
        if sort_by == "Score":
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=(sort_order == "Ascending"))
        else:
            ascending = True if sort_order == "Ascending" else False
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)

    # Reset the index to start from 1
    filtered_df.index = range(1, len(filtered_df) + 1)

    # Display the filtered DataFrame
    st.table(filtered_df)

if __name__ == "__main__":
    main()
