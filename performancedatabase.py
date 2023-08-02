#Load packages
import pandas as pd
import streamlit as st
import math

# Set the title and introduction of the application
st.title("VCT Performance Database")
st.subheader("Introduction")
st.write("Welcome to the VCT Performance Database tool! Explore the performance of Venture Capital Trusts (VCTs) in greater detail."
	" Customize the table by selecting parameters of interest and identify the VCTs alligning with your client's investment needs.")


################ Define excel sheet and column lists - edit here if columns changed in source spreadsheet #########################

# Read the data from the specified Excel file and sheet using pandas
df = pd.read_excel("VCT Database.xlsm", sheet_name="Streamlit_Performance", engine="openpyxl")

# Define some column lists to manage the selection and display of data
no_tickbox_columns = ["VCT"]
non_numeric_columns = ["VCT", "Management Group", "AIC Sector", "TIDM", "Date of last results"]
date_columns = ["Date of last results"]
no_of_basic = len(non_numeric_columns) - 1
no_of_performance = 14 						#Adding another Performance column: Update this number

###################################################################################################################################


st.subheader("Parameters")

# Initialize the list of selected columns with the default non-tickbox columns
selected_columns = no_tickbox_columns.copy()

# Create a new vector of columns for the "Column Selection" section
tickbox_columns = [col for col in df.columns if col not in no_tickbox_columns]

# Create an expander for column selection
column_expander = st.expander("Select the parameters you wish to include in the table here:")

# Function to create tickboxes for parameter selection
def tickboxes(name, start_column, end_column):
	column_expander.write(name)
	num_columns = 3
	num_rows = math.ceil(end_column / num_columns)
	columns_per_row = num_columns
	
	cols = []
	for _ in range(num_rows):
		cols.append(column_expander.columns(columns_per_row))
		
	for i, column in enumerate(tickbox_columns[start_column:(start_column + end_column)]):
		row = i // columns_per_row
		col = i % columns_per_row
		checkbox = cols[row][col].checkbox(column, value=True, key=f"checkbox_{column}")
		if checkbox:
			selected_columns.append(column)

# Include tickboxes for parameter selection in the application
tickboxes("Basic Information", 0, no_of_basic)
tickboxes("Performance", no_of_basic, no_of_performance)

# Create a new DataFrame with the selected columns only
filtered_df = df[selected_columns]

	
# Convert date columns to day-month-year format
for col in date_columns:
	if col in filtered_df.columns:
		filtered_df[col] = filtered_df[col].dt.strftime("%d-%m-%Y")


score_columns = [col for col in selected_columns if col not in non_numeric_columns]

if score_columns:
	filtered_df["Average Score"] = filtered_df[score_columns].mean(axis=1).round(2)

# Add a section for Sorting the Results
st.subheader("Sort and Filter")
st.write("You can sort the displayed VCTs based on your chosen parameters. Select a column to sort by and choose the sort order."
		 " Sorting by score can help you identify VCTs that align better with your overall preferences.")
			

# Remove unticked columns from the sort by dropdown options

sort_columns = ["Score"] + list(filtered_df.columns[:-1]) if "Score" in filtered_df else list(filtered_df.columns)

sort_by = st.selectbox("Sort By:", sort_columns, key="sort_by")

# Sort the DataFrame based on the selected column
if sort_by in date_columns:
	sort_order = st.radio("Sort Order", ["Earliest first", "Latest first"], index=0, key="sort_order")
	ascending = True if sort_order == "Earliest first" else False
	filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
elif sort_by in non_numeric_columns:
	sort_order = st.radio("Sort Order", ["A - Z", "Z - A"], index=0, key="sort_order")
	ascending = True if sort_order == "A - Z" else False
	filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
else:
	sort_order = st.radio("Sort Order", ["Descending", "Ascending"], index=0, key="sort_order")
	if "Score" in filtered_df and sort_by == "Score":
		filtered_df = filtered_df.sort_values(by=sort_by, ascending=(sort_order == "Ascending"), ignore_index=True)
	else:
		ascending = sort_order == "Ascending"
		filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)

# Format numerical values to remove trailing zeros
for col in sort_columns:
	filtered_df[col] = filtered_df[col].apply(lambda x: str(x).rstrip("0").rstrip(".") if isinstance(x, float) else x)

# Add a filter by AIC Sector option if AIC Sector column is selected
if "AIC Sector" in selected_columns:
	st.write("Filter the results by AIC Sector to remove VCTs that are not relevant to your search.")
	# Get unique AIC Sectors from the DataFrame
	aic_sectors = df["AIC Sector"].unique()
	# Allow users to select multiple AIC Sectors to filter the data
	selected_aic_sectors = st.multiselect("Filter by AIC Sector:", aic_sectors)
	# Filter the DataFrame based on the selected AIC Sectors
	if selected_aic_sectors:
		filtered_df = filtered_df[filtered_df["AIC Sector"].isin(selected_aic_sectors)]

# Reset the index to start from 1
filtered_df.index = range(1, len(filtered_df) + 1)
# Display the filtered DataFrame in a table format
st.subheader("Table")
st.write("View the table in full by selecting the arrows in the top right corner:")

st.table(filtered_df)

