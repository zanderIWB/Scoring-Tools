import pandas as pd
import streamlit as st
import math

# Main function for the Streamlit application
def main():
    # Set the title of the application
    st.title("VCT Database")
    st.subheader("Introduction")
    st.write("Welcome to the VCT Database tool! This application allows investors to discover a selection of Venture Capital Trusts (VCTs) and explore their features."
		" You can customize the table by selecting parameters of interest and set the importance of your selected parameters to calculate a revelationary Score."
		" The Score will help you identify VCTs that best suit your client's investment needs.")

    st.subheader("Parameters")
    
    # Read the data from the specified Excel file and sheet using pandas
    df = pd.read_excel("Albion Valuation Manipulation.xlsm", sheet_name="Streamlit", engine="openpyxl")

    # Define some column lists to manage the selection and display of data
    no_tickbox_columns = ["VCT"]
    non_numeric_columns = ["VCT", "Management Group", "AIC Sector", "TIDM", "Date of last results"]
    bad_columns = ["Discount", "Charge (no perf fee)", "Charge (w/ perf fee)", "Net Cash", "Top 5 Weight"]
    date_columns = ["Date of last results"]
    performance_columns = ["NAV tr 1 yr", "NAV tr 5 yr", "NAV tr 10 yr"]
    no_of_operational = len(non_numeric_columns) - 1
    no_of_performance = len(performance_columns)
    no_of_analytics = 7

    # Initialize the list of selected columns with the default non-tickbox columns
    selected_columns = no_tickbox_columns.copy()

    # Create a new vector of columns for the "Column Selection" section
    tickbox_columns = [col for col in df.columns if col not in no_tickbox_columns]

    # Create an expander for column selection
    column_expander = st.expander("Parameter Selection")

    column_expander.write("Select the parameters you want to include in the table:")
    # Add checkboxes for "Operational" columns
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

    # Add checkboxes for "Performance" columns
    column_expander.write("Performance")
    num_columns = 3
    num_rows = math.ceil(no_of_performance / num_columns)
    columns_per_row = num_columns

    cols = []
    for _ in range(num_rows):
        cols.append(column_expander.columns(columns_per_row))

    for i, column in enumerate(tickbox_columns[no_of_operational:(no_of_operational + no_of_performance)]):
        row = i // columns_per_row
        col = i % columns_per_row
        checkbox = cols[row][col].checkbox(column, value=True, key=f"checkbox_{column}")
        if checkbox:
            selected_columns.append(column)

    # Add checkboxes for "Analytics" columns
    column_expander.write("Analytics")
    num_columns = 3
    num_rows = math.ceil(no_of_analytics / num_columns)
    columns_per_row = num_columns

    cols = []
    for _ in range(num_rows):
        cols.append(column_expander.columns(columns_per_row))

    for i, column in enumerate(tickbox_columns[(no_of_operational + no_of_performance):]):
        row = i // columns_per_row
        col = i % columns_per_row
        checkbox = cols[row][col].checkbox(column, value=True, key=f"checkbox_{column}")
        if checkbox:
            selected_columns.append(column)

    # Create a new DataFrame with the selected columns only
    filtered_df = df[selected_columns]

    # Function to check if two vectors contain any similar elements
    def contains_similar_element(vector_1, vector_2):
        for element in vector_2:
            if element in vector_1:
                return True
        return False

    # If any performance columns are selected, calculate the "Performance Score"
    if contains_similar_element(performance_columns, selected_columns):
        common_columns = list(set(performance_columns) & set(selected_columns))
        normalized_common = pd.DataFrame()
        for i, col in enumerate(common_columns):
            normalized_common[i] = (filtered_df[col] - filtered_df[col].min()) / (
                filtered_df[col].max() - filtered_df[col].min())
        perf_scores = normalized_common.mean(axis=1)
        for i, col in enumerate(selected_columns):
            if col in performance_columns:
                performance_column_index = i
        filtered_df.insert(performance_column_index + 1, "Performance Score", perf_scores.round(2))

        score_columns = ["Performance Score"] + [col for col in selected_columns if col not in non_numeric_columns and col not in performance_columns]
    else:
        score_columns = [col for col in selected_columns if col not in non_numeric_columns]

    # Convert date columns to day-month-year format
    for col in date_columns:
        if col in filtered_df.columns:
            filtered_df[col] = filtered_df[col].dt.strftime("%d-%m-%Y")

    st.subheader("Score Weightings")
    # Add an expander for setting weights
    weights_expander = st.expander("Set Weights")

    weights_expander.write("Set the importance of each parameter by assigning each a level from 1 to 10"
    	" (10 being 'highly important). The Score calculated takes your importance assigned to each parameter into account."
    	" The Performance parameters are combined:")
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

        weight = target_column.slider(f"{column}", min_value=1, max_value=10, value=5, step=1)

        weights.append(weight)
        weight_counter += 1

    # Calculate the weighted average score based on the selected weights
    if len(score_columns) == 1:
        select_column = score_columns[0]
        normalized_column = (filtered_df[select_column] - filtered_df[select_column].min()) / (
            filtered_df[select_column].max() - filtered_df[select_column].min()
        )

        if select_column in bad_columns:
            weighted_average = (1 - normalized_column)
        else:
            weighted_average = normalized_column

        # Scale the weighted average to the range of 0 to 10
        scaled_score = 0 + weighted_average * (10 - 0)

        # Round the score to 2 decimal places
        rounded_score = round(scaled_score, 2)

        # Display the score
        filtered_df["Score"] = rounded_score

    else:
        # Calculate the weighted sum and total weight for multiple numerical datapoints
        weighted_sum = 0
        total_weight = 0

        for i, column in enumerate(score_columns):
            normalized_column = (filtered_df[column] - filtered_df[column].min()) / (
                filtered_df[column].max() - filtered_df[column].min()
            )

            if column in bad_columns:
                weighted_sum += (1 - normalized_column) * weights[i]
            else:
                weighted_sum += normalized_column * weights[i]

            total_weight += abs(weights[i])

        # Calculate the weighted average score
        weighted_average = weighted_sum / total_weight

        # Scale the weighted average to the range of 0 to 10
        scaled_score = 0 + weighted_average * (10 - 0)

        # Round the score to 2 decimal places
        rounded_score = round(scaled_score, 2)

        # Display the score
        filtered_df["Score"] = rounded_score

    # Determine the columns to consider for sorting based on the selected data
    if contains_similar_element(performance_columns, selected_columns):
        condition_columns = list(set(performance_columns) & set(selected_columns)) + score_columns + ["Score"]
    else:
        condition_columns = [col for col in selected_columns if col not in non_numeric_columns] + ["Score"]

    # Add a section for Sorting the Results
    st.subheader("Sort VCTs by Specific Criteria")
    st.write("You can sort the displayed VCTs based on specific criteria. Select a column to sort by and choose the sort order."
    	" Sorting the VCTs can help you identify top performers or find VCTs that align better with your client's preferences.")

    # Remove unticked columns from the sort by dropdown options
    selectable_sort_by = condition_columns
    sort_by = st.selectbox("Sort", [None] + selectable_sort_by, key="sort_by")

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

    # Format numerical values to remove trailing zeros
    for col in condition_columns:
        filtered_df[col] = filtered_df[col].apply(lambda x: str(x).rstrip("0").rstrip(".") if isinstance(x, float) else x)

    # Display the filtered DataFrame in a table format
    st.subheader("Table")
    st.write("View the table in full by selecting the arrows in the top right corner:")
    st.table(filtered_df)
    
    with st.expander("Disclaimers"):
    	st.write(" ")

if __name__ == "__main__":
    main()
