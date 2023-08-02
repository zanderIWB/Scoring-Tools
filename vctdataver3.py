import pandas as pd
import streamlit as st
import math

# Main function for the Streamlit application
def main():
    st.title("Excel Table Viewer")
    df = pd.read_excel("Albion Valuation Manipulation.xlsm", sheet_name="Streamlit", engine="openpyxl")

    no_tickbox_columns = ["VCT"]
    non_numeric_columns = ["VCT", "Management Group", "AIC Sector", "Financial Year End", "Date of last results"]
    bad_columns = ["Discount", "Ongoing Charge (no perf fee)", "Ongoing Charge (w/ perf fee)", "Top 5 Weight"]
    date_columns = ["Date of last results"]
    no_of_operational = 4
    no_of_performance = 3
    no_of_analytics = 7
	
    selected_columns = no_tickbox_columns.copy()

    # Create a new vector of columns for the "Column Selection" section
    tickbox_columns = [col for col in df.columns if col not in no_tickbox_columns]

    # Create an expander for column selection
    column_expander = st.expander("Column Selection")
    
    column_expander.write("Operational")
    num_columns = 3
    num_rows = math.ceil(no_of_operational / num_columns)
    columns_per_row = num_columns
    
    cols = []
    for _ in range(num_rows):
    	cols.append(column_expander.columns(columns_per_row))
    
    for i, column in enumerate(tickbox_columns[:no_of_operational]):
    	row = i // columns_per_row
    	col = i % columns_per_row
    	checkbox = cols[row][col].checkbox(column, value=True, key=f"checkbox_{column}")
    	if checkbox:
    		selected_columns.append(column)

    
    column_expander.write("Performance")
    num_columns = 3
    num_rows = math.ceil(no_of_performance / num_columns)
    columns_per_row = num_columns
    
    cols = []
    for _ in range(num_rows):
    	cols.append(column_expander.columns(columns_per_row))
    
    for i, column in enumerate(tickbox_columns[no_of_operational:(no_of_operational+no_of_performance)]):
    	row = i // columns_per_row
    	col = i % columns_per_row
    	checkbox = cols[row][col].checkbox(column, value=True, key=f"checkbox_{column}")
    	if checkbox:
    		selected_columns.append(column)

    column_expander.write("Analytics")
    num_columns = 3
    num_rows = math.ceil(no_of_analytics / num_columns)
    columns_per_row = num_columns
    
    cols = []
    for _ in range(num_rows):
    	cols.append(column_expander.columns(columns_per_row))
    
    for i, column in enumerate(tickbox_columns[(no_of_operational+no_of_performance):]):
    	row = i // columns_per_row
    	col = i % columns_per_row
    	checkbox = cols[row][col].checkbox(column, value=True, key=f"checkbox_{column}")
    	if checkbox:
    		selected_columns.append(column)
    
    score_columns = [col for col in selected_columns if col not in non_numeric_columns]

    # Add an expander for setting weights
    weights_expander = st.expander("Set Weights")

    # Create sliders for weights in a 3-column format
    weights = []
    num_weight_columns = 3
    weight_col1, weight_col2, weight_col3 = weights_expander.columns(num_weight_columns)

    weight_counter = 0
    for i, column in enumerate(score_columns):
        if weight_counter % num_columns == 0:
            target_column = weight_col1
        elif weight_counter % num_columns == 1:
            target_column = weight_col2
        else:
            target_column = weight_col3

        if column in bad_columns:
            weight = target_column.slider(f"Weight for {column}", min_value=1, max_value=10, value=5, step=1)
        else:
            weight = target_column.slider(f"Weight for {column}", min_value=1, max_value=10, value=5, step=1)

        weights.append(weight)
        weight_counter += 1

    # Filter the DataFrame based on selected columns
    filtered_df = df[selected_columns]
    
    # Convert date columns to day-month-year format
    for col in date_columns:
    	if col in filtered_df.columns:
    		filtered_df[col] = filtered_df[col].dt.strftime("%d-%m-%Y")
    		
    # Calculate the weighted sum
    weighted_sum = 0
    total_weight = 0

    for i, column in enumerate(score_columns):
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

    # Ensure the score is not less than 0
    scaled_score = scaled_score.apply(lambda x: max(x, 0))

    # Round the score to 2 decimal places
    rounded_score = round(scaled_score, 2)

    # Display the score with 2 decimal places without trailing zeros
    filtered_df["Score"] = rounded_score.round(2)
    for col in score_columns + ["Score"]:
    	filtered_df[col] = filtered_df[col].apply(
        	lambda x: str(x).rstrip("0").rstrip(".") if isinstance(x, float) else x)
    
    # Remove unticked columns from the sort by dropdown options
    selectable_sort_by = score_columns + ["Score"]
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
