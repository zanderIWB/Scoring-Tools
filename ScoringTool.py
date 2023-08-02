#Load packages
import pandas as pd
import streamlit as st
import math

# Set the title and introduction of the application
st.title("VCT Scoring Tool")
st.subheader("Introduction")
st.write("Welcome to the VCT Scoring tool! This application allows you to discover a selection of Venture Capital Trusts (VCTs) and explore their features."
	" Customize the table by selecting parameters of interest and setting their relative importance to you to calculate the VCT scores."
	" The score will help you identify VCTs that best suit your investment needs.")

################ Define column lists - edit here if columns changed in source spreadsheet ##########################################

# Load the data from the specified Excel file and sheet using pandas
df = pd.read_excel("VCT Database.xlsm", sheet_name="Streamlit", engine="openpyxl")

no_tickbox_columns = ["VCT"]

non_numeric_columns = ["VCT", "Management Group", "AIC Sector", "TIDM", "Date of last results"]
performance_columns = ["NAV tr 1 yr", "NAV tr 5 yr", "NAV tr 10 yr"]
consistency_columns = ["0 to 12 m", "12 to 24 m", "24 to 36 m"]
diversification_columns = ["Top 5 Weight", "Top 10 Weight", "Equivalent Equal Sized"]
analytics_columns = ["Net Assets", "Discount", "Dividend Yield", "Charge (w/o perf fee)", "Charge (w/ perf fee)", "Net Cash"]

bad_columns = ["Top 5 Weight", "Top 10 Weight", "Discount", "Charge (w/o perf fee)", "Charge (w/ perf fee)", "Net Cash"]
date_columns = ["Date of last results"]

no_of_basic = len(non_numeric_columns) - 1
no_of_performance = len(performance_columns)
no_of_consistency = len(consistency_columns)
no_of_diversification = len(diversification_columns)
no_of_analytics = len(analytics_columns)

###################################################################################################################################

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
tickboxes("Performance (Items to be included in the Performance Score)", no_of_basic, no_of_performance)
column_expander.write("Performance Consistency")
col1, col2 = column_expander.columns(2)
checkbox = col1.checkbox("5 year Performance Consistency Ranking", value=True)
if checkbox:
	selected_columns.extend(consistency_columns)
tickboxes("Diversification (Items to be included in the Diversification Score)", (no_of_basic + no_of_performance + no_of_consistency), no_of_diversification)
tickboxes("Analytics", (no_of_basic + no_of_performance + no_of_consistency + no_of_diversification), no_of_analytics)

# Create a new DataFrame with the selected columns only
filtered_df = df[selected_columns]

# Function to check if two vectors contain any similar elements
def contains_similar_element(vector_1, vector_2):
	for element in vector_2:
		if element in vector_1:
			return True
	return False
	
# Calculate diversification score if any diversification columns are selected
score_columns = [col for col in selected_columns if col in analytics_columns]

if contains_similar_element(diversification_columns, selected_columns):
	common_columns = list(set(diversification_columns) & set(selected_columns))
	normalized_common = pd.DataFrame()
	for i, col in enumerate(common_columns):
		if col in bad_columns:
			normalized_common[i] = (1-(filtered_df[col] - filtered_df[col].min()) / (
				filtered_df[col].max() - filtered_df[col].min()))
		else:
			normalized_common[i] = (filtered_df[col] - filtered_df[col].min()) / (
				filtered_df[col].max() - filtered_df[col].min())
	div_scores = 10 * normalized_common.mean(axis=1)
	for i, col in enumerate(filtered_df):
		if col in diversification_columns:
			diversification_column_index = i
	filtered_df.insert(diversification_column_index + 1, "Diversification Score", div_scores.round(2))
	
	score_columns = ["Diversification Score"] + score_columns

# Calculate performance consistency rank if any consistency columns are selected
if contains_similar_element(consistency_columns, selected_columns):
	common_columns = list(set(consistency_columns) & set(selected_columns))
	filtered_df[common_columns] = filtered_df[common_columns].round(3)
	rank_df = filtered_df[common_columns].rank(axis=0, method='first', ascending=False)
	for i, col in enumerate(filtered_df):
		if col in consistency_columns:
			consistency_column_index = i
	filtered_df.insert(consistency_column_index + 1, "Performance Consistency Rank", rank_df.mean(axis=1).round(2))
	filtered_df = filtered_df.drop(columns=set(consistency_columns))
	bad_columns = ["Performance Consistency Rank"] + bad_columns
	
	score_columns = ["Performance Consistency Rank"] + score_columns

# Calculate performance score if any performance columns are selected
if contains_similar_element(performance_columns, selected_columns):
	common_columns = list(set(performance_columns) & set(selected_columns))
	normalized_common = pd.DataFrame()
	for i, col in enumerate(common_columns):
		normalized_common[i] = (filtered_df[col] - filtered_df[col].min()) / (
			filtered_df[col].max() - filtered_df[col].min())
	perf_scores = 10 * normalized_common.mean(axis=1)
	for i, col in enumerate(filtered_df):
		if col in performance_columns:
			performance_column_index = i
	filtered_df.insert(performance_column_index + 1, "Performance Score", perf_scores.round(2))

	score_columns = ["Performance Score"] + score_columns
	
# Convert date columns to day-month-year format
for col in date_columns:
	if col in filtered_df.columns:
		filtered_df[col] = filtered_df[col].dt.strftime("%d-%m-%Y")

# Calculate overall score based on the selected weights if any score columns are present
if len(score_columns) != 0:
	st.subheader("Score Weightings")
	# Add an expander for setting weights
	weights_expander = st.expander("Set your desired score weightings here:")
	weights_expander.write("Set the relative importance of each parameter to you by assigning each a level from 1 to 10"
						   " (10 being 'highly important'). The score calculated takes into account the importance you assign to each parameter.")

	# Create sliders for weights in a 3-column format
	weights = []
	num_weight_columns = 3
	weight_col1, weight_col2, weight_col3 = weights_expander.columns(num_weight_columns)

	weight_counter = 0
	for i, column in enumerate(score_columns):
		if weight_counter % num_weight_columns == 0:
			target_column = weight_col1
		elif weight_counter % num_weight_columns == 1:
			target_column = weight_col2
		else:
			target_column = weight_col3

		weight = target_column.slider(f"{column}", min_value=1, max_value=10, value=5, step=1)
		weights.append(weight)
		weight_counter += 1

	# Calculate the weighted average score based on the selected weights

	# Calculate the weighted sum and total weight for multiple numerical datapoints
	weighted_sum = 0
	total_weight = 0

	for i, col in enumerate(score_columns):
		if col in ["Performance Score", "Diversification Score"]:
			weighted_sum += filtered_df[col] / 10 * weights[i]
			total_weight += weights[i]
		else:
			normalized_column = (filtered_df[col] - filtered_df[col].min()) / (
						filtered_df[col].max() - filtered_df[col].min())
			if col in bad_columns:
				weighted_sum += (1 - normalized_column) * weights[i]
			else:
				weighted_sum += normalized_column * weights[i]
			total_weight += weights[i]

	# Calculate the weighted average score
	weighted_average = weighted_sum / total_weight

	# Scale the weighted average to the range of 0 to 10
	scaled_score = 0 + weighted_average * (10 - 0)

	# Round the score to 2 decimal places
	rounded_score = round(scaled_score, 2)

	# Display the score
	filtered_df["Score"] = rounded_score

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
