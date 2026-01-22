import xlsxwriter
import datetime

# Create the workbook
workbook = xlsxwriter.Workbook('Student_Planner_Modern.xlsx')

# ==========================================
# MODERN COLOR PALETTE (Deep Teal 2026 Trend)
# ==========================================
colors = {
    'primary': '#1a7a7a',        # Deep Teal
    'primary_light': '#2a9a9a',  # Teal
    'accent': '#e85d75',         # Coral Red (complementary)
    'success': '#2ecc71',        # Green (completion)
    'warning': '#f39c12',        # Amber (urgent)
    'danger': '#e74c3c',         # Red (overdue)
    'neutral_bg': '#f8f9fa',     # Light gray background
    'neutral_text': '#2c3e50',   # Dark text
    'border': '#bdc3c7',         # Light border
    'white': '#ffffff'
}

# ==========================================
# FORMAT DEFINITIONS (Modern & Clean)
# ==========================================

# Title Formats
title_fmt = workbook.add_format({
    'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter',
    'font_color': colors['white'], 'bg_color': colors['primary'],
    'border': 0, 'font_name': 'Calibri'
})

subtitle_fmt = workbook.add_format({
    'bold': True, 'font_size': 14, 'align': 'left',
    'font_color': colors['primary'], 'font_name': 'Calibri'
})

# Header Formats
header_fmt = workbook.add_format({
    'bold': True, 'align': 'center', 'valign': 'vcenter',
    'font_color': colors['white'], 'bg_color': colors['primary'],
    'border': 1, 'border_color': colors['border'],
    'font_size': 11, 'font_name': 'Calibri'
})

header_secondary_fmt = workbook.add_format({
    'bold': True, 'align': 'center', 'valign': 'vcenter',
    'font_color': colors['primary'], 'bg_color': colors['neutral_bg'],
    'border': 1, 'border_color': colors['border'],
    'font_size': 10, 'font_name': 'Calibri'
})

# Data Formats
data_fmt = workbook.add_format({
    'align': 'left', 'valign': 'vcenter',
    'border': 1, 'border_color': colors['border'],
    'font_name': 'Calibri', 'font_size': 10
})

date_fmt = workbook.add_format({
    'num_format': 'yyyy-mm-dd', 'align': 'center',
    'border': 1, 'border_color': colors['border'],
    'font_name': 'Calibri'
})

percent_fmt = workbook.add_format({
    'num_format': '0%', 'align': 'center',
    'border': 1, 'border_color': colors['border'],
    'font_name': 'Calibri'
})

center_fmt = workbook.add_format({
    'align': 'center', 'valign': 'vcenter',
    'border': 1, 'border_color': colors['border'],
    'font_name': 'Calibri'
})

# Status Formats
status_pending_fmt = workbook.add_format({
    'align': 'center', 'valign': 'vcenter', 'bold': True,
    'bg_color': '#fff3cd', 'font_color': '#856404',
    'border': 1, 'border_color': colors['border'],
    'font_name': 'Calibri'
})

status_inprogress_fmt = workbook.add_format({
    'align': 'center', 'valign': 'vcenter', 'bold': True,
    'bg_color': '#cfe2ff', 'font_color': '#084298',
    'border': 1, 'border_color': colors['border'],
    'font_name': 'Calibri'
})

status_done_fmt = workbook.add_format({
    'align': 'center', 'valign': 'vcenter', 'bold': True,
    'bg_color': '#d1e7dd', 'font_color': '#0a3622',
    'border': 1, 'border_color': colors['border'],
    'font_name': 'Calibri'
})

# Alert Formats
overdue_fmt = workbook.add_format({
    'bg_color': colors['danger'], 'font_color': colors['white'],
    'bold': True, 'align': 'center',
    'border': 1, 'border_color': colors['danger'],
    'font_name': 'Calibri'
})

due_soon_fmt = workbook.add_format({
    'bg_color': colors['warning'], 'font_color': colors['white'],
    'bold': True, 'align': 'center',
    'border': 1, 'border_color': colors['warning'],
    'font_name': 'Calibri'
})

# Summary Stats Format
stat_fmt = workbook.add_format({
    'bold': True, 'font_size': 12,
    'align': 'center', 'valign': 'vcenter',
    'bg_color': colors['primary_light'],
    'font_color': colors['white'],
    'border': 1, 'border_color': colors['primary'],
    'num_format': '0.0',
    'font_name': 'Calibri'
})

# ==========================================
# 1. Setup Sheet
# ==========================================
ws_setup = workbook.add_worksheet('Setup')
ws_setup.set_column('A:A', 20)
ws_setup.set_column('B:F', 18)

ws_setup.merge_range('A1:F1', '📋 Student Planner Configuration', title_fmt)
ws_setup.set_row(0, 25)

# Setup Information
ws_setup.write('A3', 'Semester Start', subtitle_fmt)
ws_setup.write('B3', datetime.date(2026, 1, 10), date_fmt)

ws_setup.write('A4', 'Semester Name', subtitle_fmt)
ws_setup.write('B4', 'Spring 2026', data_fmt)

ws_setup.write('A5', 'Institution', subtitle_fmt)
ws_setup.write('B5', 'IIT Kanpur', data_fmt)

# Navigation Section
ws_setup.write('A8', 'QUICK NAVIGATION', subtitle_fmt)
links = [
    ('📊 Dashboard', 'Dashboard!A1'),
    ('📚 Courses', 'Courses!A1'),
    ('✅ Assignments', 'Assignments!A1'),
    ('📅 Calendar', 'Calendar!A1'),
    ('📖 Books', 'Books!A1'),
    ('🎯 Habits', 'Habits!A1')
]
for i, (name, loc) in enumerate(links):
    ws_setup.write_url(8 + i, 0, f"internal:'{loc}'", string=name)

# Instructions
ws_setup.write('A16', 'INSTRUCTIONS', subtitle_fmt)
instructions = [
    '1. Update "Courses" sheet with your courses and schedule',
    '2. Add assignments in "Assignments" sheet',
    '3. Track daily habits in "Habits" sheet',
    '4. View overview in "Dashboard" sheet',
    '5. All formulas update automatically'
]
for i, instr in enumerate(instructions):
    ws_setup.write(15 + i, 0, instr, data_fmt)

# ==========================================
# 2. Courses Sheet
# ==========================================
ws_courses = workbook.add_worksheet('Courses')
ws_courses.set_column('A:G', 15)

ws_courses.merge_range('A1:G1', '📚 Courses', title_fmt)
ws_courses.set_row(0, 25)

courses_headers = ['Code', 'Name', 'Credits', 'Current', 'Target', 'Days', 'Times']
ws_courses.write_row('A2', courses_headers, header_fmt)
ws_courses.set_row(1, 20)

courses_data = [
    ['CE612', 'Fluid Mechanics', 4, 85, 90, 'Mon,Wed,Fri', '09:00'],
    ['CE613', 'Computational Methods', 4, 78, 85, 'Tue,Thu', '10:00'],
    ['CE614', 'Water Resources', 3, 88, 92, 'Mon,Wed', '14:00'],
]
for row_idx, row_data in enumerate(courses_data, start=2):
    for col_idx, val in enumerate(row_data):
        if col_idx in [3, 4]:  # Current & Target grades
            ws_courses.write(row_idx, col_idx, val, center_fmt)
        else:
            ws_courses.write(row_idx, col_idx, val, data_fmt)

# Create Table
ws_courses.add_table('A2:G50', {
    'name': 'CoursesTable',
    'columns': [{'header': h} for h in courses_headers],
    'style': 'Table Style Light 9'
})

# Grade Progress Column
ws_courses.write('H2', 'Progress', header_fmt)
ws_courses.write_formula('H3', '=[@[Current]]-[@[Target]]', center_fmt)

# ==========================================
# 3. Assignments Sheet (Core Tracker)
# ==========================================
ws_assign = workbook.add_worksheet('Assignments')
ws_assign.set_column('A:H', 16)

ws_assign.merge_range('A1:H1', '✅ Assignment Tracker', title_fmt)
ws_assign.set_row(0, 25)

assign_headers = ['Assignment', 'Course', 'Type', 'Due Date', 'Status', 'Grade', 'Days Left', 'Notes']
ws_assign.write_row('A2', assign_headers, header_fmt)
ws_assign.set_row(1, 20)

assign_data = [
    ['Hydraulics Lab Report', 'CE612', 'Lab', datetime.date(2026, 1, 22), 'In Progress', None, '', 'Complete analysis section'],
    ['CFD Project Proposal', 'CE613', 'Project', datetime.date(2026, 1, 25), 'Pending', None, '', 'Needs team approval'],
    ['Water Quality Assessment', 'CE614', 'Assignment', datetime.date(2026, 1, 18), 'In Progress', None, '', 'Fieldwork completed'],
    ['Computational Quiz', 'CE613', 'Quiz', datetime.date(2026, 1, 15), 'Pending', None, '', 'Study notes ready'],
]

for r, row in enumerate(assign_data, start=2):
    ws_assign.write(r, 0, row[0], data_fmt)
    ws_assign.write(r, 1, row[1], data_fmt)
    ws_assign.write(r, 2, row[2], center_fmt)
    ws_assign.write(r, 3, row[3], date_fmt)
    ws_assign.write(r, 4, row[4], status_inprogress_fmt if row[4] == 'In Progress' else status_pending_fmt)
    ws_assign.write(r, 5, '', center_fmt)
    ws_assign.write_formula(r, 6, f'=IF(D{r+1}="","",D{r+1}-TODAY())', center_fmt)
    ws_assign.write(r, 7, row[7], data_fmt)

# Create Table
ws_assign.add_table('A2:H100', {
    'name': 'AssignTable',
    'columns': [{'header': h} for h in assign_headers],
    'style': 'Table Style Light 9'
})

# Data Validation
ws_assign.data_validation('C3:C100', {'validate': 'list', 'source': ['Quiz', 'Exam', 'Homework', 'Lab', 'Project', 'Assignment']})
ws_assign.data_validation('E3:E100', {'validate': 'list', 'source': ['Pending', 'In Progress', 'Done']})

# Conditional Formatting
red_fmt = workbook.add_format({'bg_color': colors['danger'], 'font_color': colors['white'], 'bold': True})
yellow_fmt = workbook.add_format({'bg_color': colors['warning'], 'font_color': colors['white']})

# Overdue highlight
ws_assign.conditional_format('D3:D100', {
    'type': 'formula',
    'criteria': '=AND(D3<>"", D3<TODAY())',
    'format': red_fmt
})

# Due within 3 days
ws_assign.conditional_format('G3:G100', {
    'type': 'formula',
    'criteria': '=AND(G3<>"", G3<=3, G3>=0)',
    'format': yellow_fmt
})

# ==========================================
# 4. Habits Sheet
# ==========================================
ws_habits = workbook.add_worksheet('Habits')
ws_habits.set_column('A:AF', 5)

ws_habits.merge_range('A1:AF1', '🎯 Habit Tracker - 31 Day Month', title_fmt)
ws_habits.set_row(0, 25)

habits = ['Study 2hrs', 'Gym/Exercise', 'Read 30min', 'Sleep 8hrs', 'Meditation', 'Code Practice']
ws_habits.write_column('A2', habits, header_secondary_fmt)

# Date headers (B1 to AF1)
for i in range(31):
    col_idx = i + 1  # B is column 1
    cell = xlsxwriter.utility.xl_rowcol_to_cell(0, col_idx)
    ws_habits.write_formula(cell, f'=Setup!$B$3 + {i}', header_fmt)
    ws_habits.set_column(col_idx, col_idx, 5)

# Habit tracking cells (TRUE/FALSE)
ws_habits.data_validation('B2:AF31', {'validate': 'list', 'source': ['✓', '']})

# Summary Column
ws_habits.set_column('AG:AG', 10)
ws_habits.write('AG1', 'Score', header_fmt)
for i, habit in enumerate(habits):
    row_num = i + 2
    ws_habits.write_formula(f'AG{row_num}', f'=COUNTIF(B{row_num}:AF{row_num},"✓")/31', percent_fmt)

# ==========================================
# 5. Books Sheet
# ==========================================
ws_books = workbook.add_worksheet('Books')
ws_books.set_column('A:G', 16)

ws_books.merge_range('A1:G1', '📖 Books Reading List', title_fmt)
ws_books.set_row(0, 25)

books_headers = ['Title', 'Author', 'Status', 'Start Date', 'Finish Date', 'Rating', 'Days Reading']
ws_books.write_row('A2', books_headers, header_fmt)
ws_books.set_row(1, 20)

books_data = [
    ['Fluids in Motion', 'Joseph H. Spurk', 'Reading', datetime.date(2025, 12, 15), None, '', ''],
    ['The Elegant Universe', 'Brian Greene', 'Completed', datetime.date(2025, 10, 1), datetime.date(2025, 12, 10), 5, ''],
]

for r, row in enumerate(books_data, start=2):
    ws_books.write(r, 0, row[0], data_fmt)
    ws_books.write(r, 1, row[1], data_fmt)
    ws_books.write(r, 2, row[2], status_done_fmt if row[2] == 'Completed' else status_inprogress_fmt)
    ws_books.write(r, 3, row[3], date_fmt)
    ws_books.write(r, 4, row[4] if row[4] else '', date_fmt if row[4] else data_fmt)
    ws_books.write(r, 5, row[5], center_fmt)
    ws_books.write_formula(r, 6, f'=IF(D{r+1}="","",IF(E{r+1}<>"",E{r+1}-D{r+1},TODAY()-D{r+1}))', center_fmt)

ws_books.add_table('A2:G50', {
    'name': 'BooksTable',
    'columns': [{'header': h} for h in books_headers],
    'style': 'Table Style Light 9'
})

# ==========================================
# 6. Calendar Sheet
# ==========================================
ws_cal = workbook.add_worksheet('Calendar')
ws_cal.set_column('A:B', 12)
ws_cal.set_column('C:C', 40)

ws_cal.merge_range('A1:C1', '📅 Monthly Calendar', title_fmt)
ws_cal.set_row(0, 25)

ws_cal.write('A2', 'Date', header_fmt)
ws_cal.write('B2', 'Day', header_fmt)
ws_cal.write('C2', 'Events Due', header_fmt)
ws_cal.set_row(1, 20)

for d in range(1, 32):
    row = d + 1
    ws_cal.write(row, 0, d, center_fmt)
    
    # Day name formula
    date_formula = f'=DATE(YEAR(Setup!$B$3), MONTH(Setup!$B$3), A{row})'
    ws_cal.write_formula(row, 1, f'=TEXT({date_formula}, "ddd")', center_fmt)
    
    # Events formula with proper syntax
    ws_cal.write_formula(row, 2, 
        f'=IFERROR(TEXTJOIN(", ",TRUE,IF(DAY(AssignTable[Due Date])=A{row},AssignTable[Assignment]&" ("&AssignTable[Type]&")","")),"")',
        data_fmt)

# ==========================================
# 7. Dashboard Sheet (Executive Summary)
# ==========================================
ws_dash = workbook.add_worksheet('Dashboard')
ws_dash.set_column('A:H', 16)

# Main Title
ws_dash.merge_range('A1:H2', '🎓 Academic Dashboard - At a Glance', title_fmt)
ws_dash.set_row(0, 30)

# Quick Stats Section
ws_dash.write('A4', 'QUICK STATS', subtitle_fmt)

stat_labels = ['Average Grade', 'Assignments Due', 'Completed Habits', 'Books Reading', 'Days Until Deadline']
stat_row = 5

ws_dash.write('A5', stat_labels[0], header_secondary_fmt)
ws_dash.write_formula('B5', '=IFERROR(AVERAGE(CoursesTable[Current]),0)', stat_fmt)

ws_dash.write('A6', stat_labels[1], header_secondary_fmt)
ws_dash.write_formula('B6', '=COUNTIFS(AssignTable[Status],"Pending",AssignTable[Due Date],"<="&TODAY()+7)', stat_fmt)

ws_dash.write('A7', stat_labels[2], header_secondary_fmt)
ws_dash.write_formula('B7', '=IFERROR(AVERAGE(Habits!AG:AG),0)', percent_fmt)

ws_dash.write('A8', stat_labels[3], header_secondary_fmt)
ws_dash.write_formula('B8', '=COUNTIF(Books!C:C,"Reading")', stat_fmt)

# Course Performance Section
ws_dash.write('A11', 'COURSE STATUS', subtitle_fmt)
ws_dash.write_row('A12', ['Course', 'Current', 'Target', 'Gap'], header_fmt)
ws_dash.set_row(11, 20)

ws_dash.write_formula('A13', '=INDEX(CoursesTable[Code],ROW()-12)', data_fmt)
ws_dash.write_formula('B13', '=INDEX(CoursesTable[Current],ROW()-12)', center_fmt)
ws_dash.write_formula('C13', '=INDEX(CoursesTable[Target],ROW()-12)', center_fmt)
ws_dash.write_formula('D13', '=IF(B13="","",B13-C13)', center_fmt)

# Upcoming Assignments Section
ws_dash.write('F4', 'UPCOMING DEADLINES', subtitle_fmt)
ws_dash.write_row('F5', ['Assignment', 'Due In', 'Status'], header_fmt)
ws_dash.write_formula('F6', '=IFERROR(INDEX(AssignTable[Assignment],SMALL(IF(AssignTable[Days Left]>0,ROW(AssignTable[Days Left])-ROW(INDEX(AssignTable,1,1))+1),ROW(A1))),"")', data_fmt)
ws_dash.write_formula('G6', '=IFERROR(INDEX(AssignTable[Days Left],SMALL(IF(AssignTable[Days Left]>0,ROW(AssignTable[Days Left])-ROW(INDEX(AssignTable,1,1))+1),ROW(A1))),"")', center_fmt)
ws_dash.write_formula('H6', '=IFERROR(INDEX(AssignTable[Status],SMALL(IF(AssignTable[Days Left]>0,ROW(AssignTable[Days Left])-ROW(INDEX(AssignTable,1,1))+1),ROW(A1))),"")', center_fmt)

# Add Chart (Pie)
chart_pie = workbook.add_chart({'type': 'pie'})
chart_pie.add_series({
    'name': 'Grade Distribution',
    'categories': '=CoursesTable[Code]',
    'values': '=CoursesTable[Current]',
    'points': [
        {'fill': {'color': colors['primary']}},
        {'fill': {'color': colors['primary_light']}},
        {'fill': {'color': colors['accent']}},
    ],
    'data_labels': {'percentage': True, 'value': True},
})
chart_pie.set_title({'name': 'Current Grades by Course'})
chart_pie.set_legend({'position': 'right'})
chart_pie.set_size({'width': 350, 'height': 250})
ws_dash.insert_chart('F12', chart_pie)

workbook.close()
print("✅ Modern Student Planner created successfully as 'Student_Planner_Modern.xlsx'")
