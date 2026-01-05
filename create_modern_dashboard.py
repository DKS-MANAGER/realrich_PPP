import pandas as pd
import xlsxwriter
from datetime import datetime, time
import os

# 1. Load and Clean Data
# Use absolute paths to avoid CWD confusion
base_dir = r'C:\Users\DKS\Desktop\VSC\Dec25\python'
file_path = os.path.join(base_dir, 'IITK_Timetable_Dashboard_v3_FIXED.xlsx')
output_file = os.path.join(base_dir, 'IITK_Modern_Dashboard.xlsx')

print(f"Reading from: {file_path}")
meetings = pd.read_excel(file_path, sheet_name='MasterMeetings')
courses = pd.read_excel(file_path, sheet_name='MasterCourses')

# Clean MasterCourses: Keep only relevant columns
# Ensure columns exist before selecting
print("Cleaning Courses...")
courses_clean = courses[['CourseCode', 'CourseTitle', 'DisplayCourse', 'Instructor']].drop_duplicates()

# Clean MasterMeetings: Convert Time strings to Python Time objects
def clean_time(t):
    if isinstance(t, str):
        try:
            # Handle potential whitespace
            t = t.strip()
            return datetime.strptime(t, "%H:%M").time()
        except ValueError:
            return None
    return t

print("Cleaning Meetings...")
meetings['StartTime'] = meetings['StartTime'].apply(clean_time)
meetings['EndTime'] = meetings['EndTime'].apply(clean_time)

# 2. Create New Excel File with "Modern" Layout
print(f"Creating {output_file}...")
writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
workbook = writer.book

# Formats
fmt_header = workbook.add_format({'bold': True, 'font_name': 'Segoe UI', 'font_size': 12, 'bg_color': '#2C3E50', 'font_color': 'white', 'border': 1})
fmt_cell = workbook.add_format({'font_name': 'Segoe UI', 'font_size': 10, 'border': 1})
fmt_time = workbook.add_format({'num_format': 'hh:mm AM/PM', 'font_name': 'Segoe UI', 'font_size': 10, 'border': 1})
fmt_dashboard_bg = workbook.add_format({'bg_color': '#F4F6F7'}) # Light grey background for app-feel
fmt_card = workbook.add_format({'bg_color': 'white', 'border': 1, 'border_color': '#D5D8DC'}) # "Card" look
fmt_input = workbook.add_format({'bg_color': '#FEF9E7', 'border': 2, 'border_color': '#F1C40F', 'font_name': 'Segoe UI', 'bold': True})

# --- Write Data Sheets ---
courses_clean.to_excel(writer, sheet_name='Data_Courses', index=False)
meetings.to_excel(writer, sheet_name='Data_Meetings', index=False)

# Format Data Sheets (Auto-width)
for sheet in ['Data_Courses', 'Data_Meetings']:
    worksheet = writer.sheets[sheet]
    worksheet.set_column('A:Z', 15)

# --- Build Dashboard Sheet ---
ws_dash = workbook.add_worksheet('Dashboard')
writer.sheets['Dashboard'] = ws_dash

# remove gridlines for clean look
ws_dash.hide_gridlines(2) 
ws_dash.set_column('A:A', 2) # Spacer
ws_dash.set_column('B:B', 15) # Time Col
ws_dash.set_column('C:G', 20) # Mon-Fri Cols

# Title
title_fmt = workbook.add_format({'font_name': 'Segoe UI', 'bold': True, 'font_size': 24, 'font_color': '#2C3E50'})
ws_dash.write('B2', "IITK Student Timetable", title_fmt)
ws_dash.write('B3', "Select your courses below to populate the schedule.", workbook.add_format({'font_name': 'Segoe UI', 'font_color': '#7F8C8D'}))

# Input Section (Course Selectors)
ws_dash.write('B5', "Select Courses:", workbook.add_format({'font_name': 'Segoe UI', 'bold': True}))

# Create Dropdowns (Data Validation)
# Note: Data_Courses sheet has headers in row 1. Data starts at row 2.
# len(courses_clean) gives number of rows. So range is A2 : A(len+1).
course_list_formula = '=Data_Courses!$A$2:$A$' + str(len(courses_clean) + 1)
input_cells = ['C5', 'D5', 'E5', 'F5', 'G5', 'C6']

for cell in input_cells:
    ws_dash.write(cell, "", fmt_input) # Empty cell with formatting
    ws_dash.data_validation(cell, {'validate': 'list', 'source': course_list_formula})

ws_dash.write('C5', "Select Course ->", fmt_input) # Hint text in first cell

# Schedule Grid Header
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
for idx, day in enumerate(days):
    ws_dash.write(9, 2 + idx, day, fmt_header)

ws_dash.write(9, 1, "Time", fmt_header)

# Schedule Grid Rows (08:00 to 18:00)
row = 10
for hour in range(8, 19):
    time_str = f"{hour:02d}:00"
    # Write time string, apply time format? 
    # If we write string "08:00", excel might treat as text unless we convert.
    # But fmt_time has num_format 'hh:mm AM/PM'.
    # Better to write a number (fraction of day) or string.
    # xlsxwriter handles datetime objects.
    # Let's use datetime.time
    t_obj = time(hour, 0)
    ws_dash.write_datetime(row, 1, t_obj, fmt_time)
    
    for col in range(2, 7):
        # Apply a formula to lookup course (This is a complex array formula placeholder)
        # For this script, we just format the grid cleanly
        ws_dash.write(row, col, "", fmt_cell)
    row += 1

writer.close()
print(f"File saved as: {output_file}")
