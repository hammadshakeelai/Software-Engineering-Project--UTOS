# UTOS Bulk Data Import Guide

## Document Version: 1.0
## Date: May 2026
## Access Level: ADMINISTRATORS ONLY

---

## Overview

This document provides the complete specification for bulk data import into the University Timetable Optimization System (UTOS). The system supports bulk import via Excel (.xlsx) or CSV files for:

1. **Student Data** - Importing students into sections
2. **Course Enrollments** - Linking students to courses
3. **Master Data** - Teachers, Rooms, Courses, Sections

> **NOTE:** This feature is restricted to **Timetable Administrators** only. Students and teachers cannot access bulk import functionality.

---

## 1. Student Import Format

> **Access:** Admin only

### 1.1 File Structure

**Filename Convention:**
- Students: `students_import.xlsx` or `students_import.csv`
- Must follow the structure below

**Column Structure:**

| Column | Field Name | Data Type | Required | Description |
|--------|-----------|----------|----------|--------------|
| A | student_id | String | YES | Unique student ID (e.g., REG-2024-001) |
| B | first_name | String | YES | Student's first name |
| C | last_name | String | YES | Student's last name |
| D | email | String | YES | Student's email address |
| E | phone | String | NO | Contact phone number |
| F | section_code | String | YES | Section code (e.g., CS-1st-Year-A) |
| G | batch_code | String | YES | Batch code (e.g., BATCH-2024) |
| H | department_code | String | YES | Department code (e.g., CS) |
| I | faculty_code | String | YES | Faculty code (e.g., ENGINEERING) |
| J | status | String | NO | ACTIVE (default) or INACTIVE |

### 1.2 Data Types Specification

| Field | Type | Format | Examples |
|-------|------|--------|----------|
| student_id | String | Alphanumeric | REG-2024-001, STD2024001, CS2024001 |
| first_name | String | Text | John, Mary, Ali |
| last_name | String | Text | Smith, Khan, Ahmed |
| email | String | Email format | john.smith@university.edu |
| phone | String | Digits + symbols | +1234567890, 03001234567 |
| section_code | String | Alphanumeric | CS-1st-Year-A, SE-2K26-A |
| batch_code | String | Alphanumeric | BATCH-2024, 2024 |
| department_code | String | 2-10 chars | CS, SE, EE |
| faculty_code | String | 2-10 chars | ENGINEERING, SCIENCE |
| status | String | ACTIVE/INACTIVE | ACTIVE |

### 1.3 Example - Student Import

#### Excel View:

| | A | B | C | D | E | F | G | H | I | J |
|--|---|---|---|---|---|---|---|---|---|---|
| 1 | student_id | first_name | last_name | email | phone | section_code | batch_code | department_code | faculty_code | status |
| 2 | REG-2024-001 | Ahmed | Khan | ahmed.khan@edu.com | 03001234567 | CS-1st-Year-A | BATCH-2024 | CS | ENGINEERING | ACTIVE |
| 3 | REG-2024-002 | Sara | Ali | sara.ali@edu.com | 03001234568 | CS-1st-Year-A | BATCH-2024 | CS | ENGINEERING | ACTIVE |
| 4 | REG-2024-003 | Omar | Hussain | omar.h@edu.com | 03001234569 | EE-1st-Year-A | BATCH-2024 | EE | ENGINEERING | ACTIVE |
| 5 | REG-2024-004 | Fatima | Zahra | fatima.z@edu.com | 03001234570 | SE-1st-Year-A | BATCH-2024 | SE | ENGINEERING | ACTIVE |

#### CSV Format:
```csv
student_id,first_name,last_name,email,phone,section_code,batch_code,department_code,faculty_code,status
REG-2024-001,Ahmed,Khan,ahmed.khan@edu.com,03001234567,CS-1st-Year-A,BATCH-2024,CS,ENGINEERING,ACTIVE
REG-2024-002,Sara,Ali,sara.ali@edu.com,03001234568,CS-1st-Year-A,BATCH-2024,CS,ENGINEERING,ACTIVE
REG-2024-003,Omar,Hussain,omar.h@edu.com,03001234569,EE-1st-Year-A,BATCH-2024,EE,ENGINEERING,ACTIVE
REG-2024-004,Fatima,Zahra,fatima.z@edu.com,03001234570,SE-1st-Year-A,BATCH-2024,SE,ENGINEERING,ACTIVE
```

---

> **Access:** Admin only

## 2. Course Enrollment Import Format

> **Access:** Admin only

### 2.1 File Structure

**Filename Convention:**
- Enrollments: `enrollments_import.xlsx` or `enrollments_import.csv`

**Column Structure:**

| Column | Field Name | Data Type | Required | Description |
|--------|-----------|----------|----------|--------------|
| A | student_id | String | YES | Links to student (must exist) |
| B | course_code | String | YES | Course code (e.g., CS101) |
| C | section_code | String | YES | Section taking this course |
| D | enrollment_date | Date | NO | Date enrolled (YYYY-MM-DD) |
| E | status | String | NO | ENROLLED (default) or DROPPED |

### 2.2 Data Types Specification

| Field | Type | Format | Examples |
|-------|------|--------|----------|
| student_id | String | Must match existing student | REG-2024-001 |
| course_code | String | Must match existing course | CS101, EE201 |
| section_code | String | Must match existing section | CS-1st-Year-A |
| enrollment_date | Date | YYYY-MM-DD | 2024-01-15 |
| status | String | ENROLLED/DROPPED | ENROLLED |

### 2.3 Example - Course Enrollment Import

#### Excel View:

| | A | B | C | D | E |
|--|---|---|---|---|---|
| 1 | student_id | course_code | section_code | enrollment_date | status |
| 2 | REG-2024-001 | CS101 | CS-1st-Year-A | 2024-01-15 | ENROLLED |
| 3 | REG-2024-001 | CS102 | CS-1st-Year-A | 2024-01-15 | ENROLLED |
| 4 | REG-2024-002 | CS101 | CS-1st-Year-A | 2024-01-15 | ENROLLED |
| 5 | REG-2024-003 | EE101 | EE-1st-Year-A | 2024-01-15 | ENROLLED |

#### CSV Format:
```csv
student_id,course_code,section_code,enrollment_date,status
REG-2024-001,CS101,CS-1st-Year-A,2024-01-15,ENROLLED
REG-2024-001,CS102,CS-1st-Year-A,2024-01-15,ENROLLED
REG-2024-002,CS101,CS-1st-Year-A,2024-01-15,ENROLLED
REG-2024-003,EE101,EE-1st-Year-A,2024-01-15,ENROLLED
```

---

> **Access:** Admin only

## 3. Teacher Import Format

> **Access:** Admin only

### 3.1 File Structure

**Filename Convention:**
- Teachers: `teachers_import.xlsx` or `teachers_import.csv`

**Column Structure:**

| Column | Field Name | Data Type | Required | Description |
|--------|-----------|----------|----------|--------------|
| A | teacher_id | String | YES | Unique teacher ID |
| B | first_name | String | YES | Teacher's first name |
| C | last_name | String | YES | Teacher's last name |
| D | email | String | YES | Teacher's email |
| E | phone | String | NO | Contact number |
| F | department_code | String | YES | Department code |
| G | max_daily_load | Number | NO | Max classes per day (default: 4) |
| H | status | String | NO | ACTIVE (default) or INACTIVE |

### 3.2 Example - Teacher Import

#### Excel View:

| | A | B | C | D | E | F | G | H |
|--|---|---|---|---|---|---|---|---|
| 1 | teacher_id | first_name | last_name | email | phone | department_code | max_daily_load | status |
| 2 | T-CH-001 | Dr. Ahmad | Khan | ahmad.khan@edu.com | 03001234567 | CS | 4 | ACTIVE |
| 3 | T-CH-002 | Dr. Sara | Ali | sara.ali@edu.com | 03001234568 | CS | 3 | ACTIVE |
| 4 | T-EE-001 | Dr. Omar | Hussain | omar.h@edu.com | 03001234569 | EE | 4 | ACTIVE |

#### CSV Format:
```csv
teacher_id,first_name,last_name,email,phone,department_code,max_daily_load,status
T-CH-001,Dr. Ahmad,Khan,ahmad.khan@edu.com,03001234567,CS,4,ACTIVE
T-CH-002,Dr. Sara,Ali,sara.ali@edu.com,03001234568,CS,3,ACTIVE
T-EE-001,Dr. Omar,Hussain,omar.h@edu.com,03001234569,EE,4,ACTIVE
```

---

> **Access:** Admin only

## 4. Room Import Format

> **Access:** Admin only

### 4.1 File Structure

**Filename Convention:**
- Rooms: `rooms_import.xlsx` or `rooms_import.csv`

**Column Structure:**

| Column | Field Name | Data Type | Required | Description |
|--------|-----------|----------|----------|--------------|
| A | room_code | String | YES | Unique room ID (e.g., R-101) |
| B | building | String | YES | Building name |
| C | floor | Number | YES | Floor number (0, 1, 2, ...) |
| D | capacity | Number | YES | Seating capacity |
| E | room_type | String | YES | CLASSROOM, LAB, CONFERENCE, GROUP_STUDY |
| F | facilities | String | NO | Comma-separated features |
| G | status | String | NO | ACTIVE (default) or INACTIVE |

### 4.2 Example - Room Import

#### Excel View:

| | A | B | C | D | E | F | G |
|--|---|---|---|---|---|---|---|
| 1 | room_code | building | floor | capacity | room_type | facilities | status |
| 2 | R-101 | Main Building | 1 | 30 | CLASSROOM | Projector,Whiteboard | ACTIVE |
| 3 | R-102 | Main Building | 1 | 30 | CLASSROOM | Projector,Whiteboard | ACTIVE |
| 4 | LAB-001 | Engineering | 2 | 20 | LAB | Computers,Projector | ACTIVE |
| 5 | CONF-001 | Admin Block | 3 | 15 | CONFERENCE | TV,Video Call | ACTIVE |

---

> **Access:** Admin only

## 5. Course Import Format

> **Access:** Admin only

### 5.1 File Structure

**Filename Convention:**
- Courses: `courses_import.xlsx` or `courses_import.csv`

**Column Structure:**

| Column | Field Name | Data Type | Required | Description |
|--------|-----------|----------|----------|--------------|
| A | course_code | String | YES | Unique course code (e.g., CS101) |
| B | course_title | String | YES | Full course name |
| C | teacher_id | String | YES | Assigned teacher ID |
| D | section_code | String | YES | Section offering this course |
| E | weekly_sessions | Number | YES | Sessions per week (1-5) |
| F | duration | String | YES | 1h, 1.5h, or 2h |
| G | required_room_type | String | YES | CLASSROOM or LAB |
| H | department_code | String | YES | Department code |

### 5.2 Example - Course Import

#### Excel View:

| | A | B | C | D | E | F | G | H |
|--|---|---|---|---|---|---|---|---|
| 1 | course_code | course_title | teacher_id | section_code | weekly_sessions | duration | required_room_type | department_code |
| 2 | CS101 | Introduction to Programming | T-CH-001 | CS-1st-Year-A | 3 | 1.5h | LAB | CS |
| 3 | CS102 | Data Structures | T-CH-002 | CS-1st-Year-A | 2 | 1h | LAB | CS |
| 4 | EE101 | Electrical Basics | T-EE-001 | EE-1st-Year-A | 2 | 2h | LAB | EE |

---

> **Access:** Admin only

## 6. Section Import Format

> **Access:** Admin only

### 6.1 File Structure

**Filename Convention:**
- Sections: `sections_import.xlsx` or `sections_import.csv`

**Column Structure:**

| Column | Field Name | Data Type | Required | Description |
|--------|-----------|----------|----------|--------------|
| A | section_code | String | YES | Unique section ID |
| B | section_name | String | YES | Full section name |
| C | department_code | String | YES | Department code |
| D | batch_code | String | YES | Batch code |
| E | expected_size | Number | YES | Expected number of students |
| F | starting_year | Number | YES | Year section started |

### 6.2 Example - Section Import

#### Excel View:

| | A | B | C | D | E | F |
|--|---|---|---|---|---|---|
| 1 | section_code | section_name | department_code | batch_code | expected_size | starting_year |
| 2 | CS-1st-Year-A | Computer Science Year 1 | CS | BATCH-2024 | 30 | 2024 |
| 3 | CS-2nd-Year-A | Computer Science Year 2 | CS | BATCH-2023 | 25 | 2023 |
| 4 | EE-1st-Year-A | Electrical Eng Year 1 | EE | BATCH-2024 | 20 | 2024 |

---

> **Access:** Admin only

## 7. Combined Master Data Import (All-in-One)

> **Access:** Admin only

### 7.1 File for One-Time Setup

For initial setup, you can import all master data using multiple sheets:

**Filename:** `master_data_import.xlsx`

#### Sheet 1: Teachers
| teacher_id | first_name | last_name | email | department_code |
|------------|-----------|-----------|-------|----------------|
| T-CH-001 | Dr. Ahmad | Khan | ahmad.khan@edu.com | CS |
| T-CH-002 | Dr. Sara | Ali | sara.ali@edu.com | CS |

#### Sheet 2: Rooms
| room_code | building | floor | capacity | room_type |
|-----------|---------|-------|----------|-----------|
| R-101 | Main | 1 | 30 | CLASSROOM |
| LAB-001 | Eng | 2 | 20 | LAB |

#### Sheet 3: Sections
| section_code | section_name | department_code | batch_code |
|-------------|-------------|---------------|-----------|
| CS-1st-Year-A | CS Year 1 | CS | BATCH-2024 |

#### Sheet 4: Courses
| course_code | course_title | teacher_id | section_code | weekly_sessions | duration |
|------------|-------------|-----------|------------|----------------|----------|
| CS101 | Intro to Programming | T-CH-001 | CS-1st-Year-A | 3 | 1.5h |

#### Sheet 5: Students
| student_id | first_name | last_name | email | section_code |
|------------|-----------|-----------|-------|--------------|
| REG-2024-001 | Ahmed | Khan | ahmed@edu.com | CS-1st-Year-A |
| REG-2024-002 | Sara | Ali | sara@edu.com | CS-1st-Year-A |

---

## 8. Validation Rules

### 8.1 Required Fields

- **Student Import:** student_id, first_name, last_name, email, section_code, department_code, faculty_code
- **Teacher Import:** teacher_id, first_name, last_name, email, department_code
- **Room Import:** room_code, building, floor, capacity, room_type
- **Course Import:** course_code, course_title, teacher_id, section_code, duration
- **Section Import:** section_code, section_name, department_code

### 8.2 Validation Checks

| Check | Rule | Error Message |
|-------|------|-------------|
| Duplicate ID | student_id must be unique | "Duplicate student_id: {id}" |
| Email Format | Must be valid email | "Invalid email format: {email}" |
| Section Exists | section_code must exist in system | "Section not found: {code}" |
| Department Exists | department_code must exist | "Department not found: {code}" |
| Teacher Exists | teacher_id must exist | "Teacher not found: {id}" |
| Room Type | Must be CLASSROOM, LAB, CONFERENCE, GROUP_STUDY | "Invalid room type: {type}" |
| Capacity | Must be positive number | "Invalid capacity: {value}" |
| Duration | Must be 1h, 1.5h, or 2h | "Invalid duration: {value}" |

### 8.3 Error Report Format

After import, system generates error report:

| Row | Field | Error |
|-----|-------|------|
| 2 | student_id | Duplicate ID: REG-2024-001 |
| 5 | email | Invalid email format: invalid-email |
| 10 | section_code | Section not found: CS-Year-X |

---

## 9. Import Steps

### Step 1: Prepare Data

> **NOTE:** This feature is restricted to Timetable Administrators only.

1. Create Excel/CSV file following format above
2. Ensure all required fields are filled
3. Verify data accuracy

### Step 2: Upload
1. Navigate to Admin → Bulk Import
2. Select import type (Students/Teachers/Rooms/etc.)
3. Choose file
4. Click "Upload"

### Step 3: Validation
1. System validates all rows
2. If errors → Show error report
3. Fix errors and re-upload

### Step 4: Confirmation
1. If valid → Show preview
2. Review data
3. Click "Confirm Import"

### Step 5: Complete
1. Data imported
2. Success message shown
3. Records added to system

---

## 10. Sample Files

### 10.1 Complete Students CSV
```csv
student_id,first_name,last_name,email,phone,section_code,batch_code,department_code,faculty_code,status
REG-2024-001,Ahmed,Khan,ahmed.khan@edu.com,03001234567,CS-1st-Year-A,BATCH-2024,CS,ENGINEERING,ACTIVE
REG-2024-002,Sara,Ali,sara.ali@edu.com,03001234568,CS-1st-Year-A,BATCH-2024,CS,ENGINEERING,ACTIVE
REG-2024-003,Omar,Hussain,omar.h@edu.com,03001234569,EE-1st-Year-A,BATCH-2024,EE,ENGINEERING,ACTIVE
REG-2024-004,Fatima,Zahra,fatima.z@edu.com,03001234570,SE-1st-Year-A,BATCH-2024,SE,ENGINEERING,ACTIVE
REG-2024-005,Ali,Ahmad,ali.ahmad@edu.com,03001234571,CS-2nd-Year-A,BATCH-2023,CS,ENGINEERING,ACTIVE
```

### 10.2 Complete Enrollment CSV
```csv
student_id,course_code,section_code,enrollment_date,status
REG-2024-001,CS101,CS-1st-Year-A,2024-01-15,ENROLLED
REG-2024-001,CS102,CS-1st-Year-A,2024-01-15,ENROLLED
REG-2024-001,MATH101,CS-1st-Year-A,2024-01-15,ENROLLED
REG-2024-002,CS101,CS-1st-Year-A,2024-01-15,ENROLLED
REG-2024-002,CS102,CS-1st-Year-A,2024-01-15,ENROLLED
REG-2024-003,EE101,EE-1st-Year-A,2024-01-15,ENROLLED
REG-2024-003,EE102,EE-1st-Year-A,2024-01-15,ENROLLED
```

---

## 11. Quick Reference Card

### Field Summary

| Import Type | Required Columns | File Type |
|-----------|--------------|----------|
| Students | student_id, first_name, last_name, email, section_code, department_code, faculty_code | .xlsx, .csv |
| Teachers | teacher_id, first_name, last_name, email, department_code | .xlsx, .csv |
| Rooms | room_code, building, floor, capacity, room_type | .xlsx, .csv |
| Sections | section_code, section_name, department_code, batch_code | .xlsx, .csv |
| Courses | course_code, course_title, teacher_id, section_code, duration | .xlsx, .csv |
| Enrollments | student_id, course_code, section_code | .xlsx, .csv |

### Maximums

| Data Type | Maximum Records |
|----------|--------------|
| Students per file | 10,000 |
| Courses per file | 500 |
| Rooms per file | 200 |

---

*This document is part of the UTOS SRS documentation*
*For support, contact: admin@utos.edu*
*Access Level: Administrators Only - Unauthorized access is prohibited*