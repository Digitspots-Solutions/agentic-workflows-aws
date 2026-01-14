# 📊 LAUTECH Data Management Guide

**How to add and manage real university data**

---

## 🚀 Quick Start

### Step 1: Import Pre-made Data (20 courses, 20 fees, 35 events, 8 hostels)

```bash
cd strands_agents/lautech

# Import everything
python3 import_data.py --all

# Or import specific tables
python3 import_data.py --courses
python3 import_data.py --fees
python3 import_data.py --calendar
python3 import_data.py --hostels
```

**Output:**
```
✅ Imported 20 courses
✅ Imported 20 fees
✅ Imported 35 calendar events
✅ Imported 8 hostels
```

### Step 2: Verify Data

```bash
# Show statistics
python3 import_data.py --stats

# Or check database directly
sqlite3 lautech_data.db "SELECT COUNT(*) FROM courses;"
```

### Step 3: Deploy to AgentCore

```bash
# Deploy with new data
agentcore launch

# Test it
agentcore invoke '{"prompt": "What Computer Science courses are available?"}'
```

---

## 📁 Data Files

All data is in CSV format for easy editing:

```
data/
├── courses.csv    # 20 courses across departments
├── fees.csv       # 20 fee types and amounts
├── calendar.csv   # 35 academic events
└── hostels.csv    # 8 hostel facilities
```

---

## ✏️ Adding Your Own Data

### Method 1: Edit CSV Files (Easiest)

**1. Open in Excel/Google Sheets:**

```bash
# On Mac
open data/courses.csv

# Or use any text editor
code data/courses.csv
```

**2. Add rows following the format:**

**courses.csv:**
```csv
code,name,credits,prerequisites,description,semester,lecturer,department
CSC501,Cloud Computing,4,CSC401,AWS Azure GCP,First Semester,Dr. Ajayi,Computer Science
```

**fees.csv:**
```csv
level,amount,fee_type,session
400 Level Lab,12000,Laboratory,2024/2025
```

**calendar.csv:**
```csv
event_type,event_date,semester,session,description
Convocation,2025-03-15,Both,2024/2025,Graduation ceremony
```

**hostels.csv:**
```csv
name,gender,capacity,status,facilities
New Hall,Male,500,Available,AC rooms | 24/7 power | WiFi
```

**3. Re-import:**

```bash
python3 import_data.py --all --clear
```

---

### Method 2: Direct SQL (Advanced)

```bash
sqlite3 lautech_data.db

-- Add a course
INSERT INTO courses VALUES (
    'CSC601',
    'Advanced Machine Learning',
    4,
    'CSC402',
    'Deep learning and AI applications',
    'First Semester',
    'Prof. Okonkwo',
    'Computer Science'
);

-- Add a fee
INSERT INTO fees (level, amount, fee_type, session) VALUES
('PG Diploma', 120000, 'Tuition', '2024/2025');

-- View data
SELECT * FROM courses WHERE department = 'Computer Science';

.quit
```

---

### Method 3: Python Script (Bulk Operations)

```python
import sqlite3

conn = sqlite3.connect('lautech_data.db')
cursor = conn.cursor()

# Add multiple courses
courses = [
    ('CSC502', 'Blockchain', 3, 'CSC401', '...', 'First Semester', 'Dr. X', 'CS'),
    ('CSC503', 'IoT Systems', 3, 'CSC403', '...', 'Second Semester', 'Dr. Y', 'CS'),
]

cursor.executemany("""
    INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", courses)

conn.commit()
conn.close()
```

---

## 🔍 Viewing Data

### Quick Stats

```bash
python3 import_data.py --stats
```

### SQL Queries

```bash
sqlite3 lautech_data.db

-- All courses
SELECT code, name, semester FROM courses;

-- Courses by department
SELECT * FROM courses WHERE department = 'Computer Science';

-- Upcoming events
SELECT event_type, event_date FROM academic_calendar
WHERE event_date >= date('now')
ORDER BY event_date;

-- Total fees by type
SELECT fee_type, SUM(amount) FROM fees GROUP BY fee_type;

.quit
```

### Export to CSV

```bash
sqlite3 lautech_data.db

.mode csv
.output courses_backup.csv
SELECT * FROM courses;
.output stdout

.quit
```

---

## 📋 CSV Format Reference

### courses.csv

| Field | Type | Required | Example |
|-------|------|----------|---------|
| code | TEXT | Yes | CSC301 |
| name | TEXT | Yes | Database Systems |
| credits | INTEGER | Yes | 3 |
| prerequisites | TEXT | No | CSC201 |
| description | TEXT | Yes | Database design... |
| semester | TEXT | Yes | First Semester |
| lecturer | TEXT | Yes | Prof. Ibrahim |
| department | TEXT | Yes | Computer Science |

### fees.csv

| Field | Type | Required | Example |
|-------|------|----------|---------|
| level | TEXT | Yes | 200 Level |
| amount | INTEGER | Yes | 75000 |
| fee_type | TEXT | Yes | Tuition |
| session | TEXT | Yes | 2024/2025 |

### calendar.csv

| Field | Type | Required | Example |
|-------|------|----------|---------|
| event_type | TEXT | Yes | Registration Start |
| event_date | TEXT | Yes | 2024-09-01 |
| semester | TEXT | Yes | First Semester |
| session | TEXT | Yes | 2024/2025 |
| description | TEXT | Yes | Online registration opens |

### hostels.csv

| Field | Type | Required | Example |
|-------|------|----------|---------|
| name | TEXT | Yes | Ajose Hall |
| gender | TEXT | Yes | Male |
| capacity | INTEGER | Yes | 400 |
| status | TEXT | Yes | Available |
| facilities | TEXT | Yes | Power Water Security |

---

## 🔄 Update Workflow

### Regular Updates

```bash
# 1. Edit CSV files
code data/courses.csv

# 2. Import with --clear to replace old data
python3 import_data.py --courses --clear

# 3. Verify
python3 import_data.py --stats

# 4. Deploy
agentcore launch

# 5. Test
agentcore invoke '{"prompt": "List all courses"}'
```

### Incremental Updates

```bash
# Add new data without clearing existing
python3 import_data.py --courses

# This will add/update courses but keep existing ones
```

---

## 🎯 Real LAUTECH Data Checklist

Add your actual university data:

### Courses
- [ ] Add all Computer Science courses
- [ ] Add Mathematics courses
- [ ] Add Engineering courses
- [ ] Add Science courses
- [ ] Add Arts courses
- [ ] Update lecturers with real names
- [ ] Verify prerequisites are accurate

### Fees
- [ ] Update with current 2024/2025 fees
- [ ] Add departmental fees
- [ ] Add faculty-specific fees
- [ ] Add PG program fees
- [ ] Add other charges

### Calendar
- [ ] Add 2024/2025 first semester dates
- [ ] Add 2024/2025 second semester dates
- [ ] Add exam dates
- [ ] Add registration periods
- [ ] Add important deadlines
- [ ] Add public holidays

### Hostels
- [ ] Add all male hostels
- [ ] Add all female hostels
- [ ] Update capacities
- [ ] Update facilities
- [ ] Update availability status

---

## 🚨 Troubleshooting

### "File not found"

```bash
# Make sure you're in the right directory
cd strands_agents/lautech

# Check if data folder exists
ls data/
```

### "Import failed"

```bash
# Check CSV format
head -5 data/courses.csv

# Look for errors in the CSV (extra commas, missing fields)
```

### "Database locked"

```bash
# Close any open database connections
# Then try again
python3 import_data.py --all
```

### "Permission denied"

```bash
# Make script executable
chmod +x import_data.py

# Run with python3
python3 import_data.py --all
```

---

## 📊 Sample Data Overview

**Current sample data includes:**

### Courses (20)
- Computer Science: CSC201-CSC501
- Mathematics: MTH201-MTH401
- English: ENG201, ENG301
- Other: PHY201, CHM201, BIO301, STA301

### Fees (20)
- Tuition for all levels (100-500, PG)
- Administrative fees
- Laboratory fees
- Other charges

### Calendar (35)
- Both semesters fully mapped
- Registration periods
- Exam schedules
- Deadlines and breaks

### Hostels (8)
- 4 Male hostels
- 4 Female hostels
- Capacities and facilities

---

## 🎓 Production Best Practices

### 1. Backup Before Changes

```bash
# Backup database
cp lautech_data.db lautech_data.db.backup

# Backup CSV files
cp -r data/ data_backup/
```

### 2. Validate Data

```bash
# Check for duplicates
sqlite3 lautech_data.db "SELECT code, COUNT(*) FROM courses GROUP BY code HAVING COUNT(*) > 1;"

# Check for missing prerequisites
sqlite3 lautech_data.db "SELECT code, prerequisites FROM courses WHERE prerequisites != '';"
```

### 3. Test Before Deploy

```bash
# Always test locally first
agentcore launch -l
agentcore invoke --local '{"prompt": "test query"}'

# Then deploy
agentcore launch
```

---

## 🔗 Next Steps

After adding data:

1. **Test locally** - Verify queries work
2. **Deploy to AgentCore** - Push to production
3. **Build web dashboard** (Part C) - User interface
4. **Create admin panel** (Part D) - Staff management
5. **Add monitoring** (Part E) - Track usage

---

**Ready to add data!** Start with editing the CSV files, then import. 🚀
