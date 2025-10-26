# Testing the Admin Dashboard with Sample Data

## Overview

Two scripts are provided to help you test the admin dashboard functionality with realistic sample data:

1. **`insert_sample_data.py`** - Creates sample quiz attempts
2. **`remove_sample_data.py`** - Removes sample data

## Quick Start

### Insert Sample Data

```bash
python scripts/insert_sample_data.py
```

This creates approximately **120-170 quiz attempts** over the last 30 days with realistic score distributions.

### Remove Sample Data

```bash
python scripts/remove_sample_data.py
```

Type `DELETE` when prompted to confirm removal.

---

## Insert Sample Data Script

### What It Creates

The script generates realistic quiz data across three game modes:

#### 1. Elimination Mode (60-80 attempts)
- 100 questions per attempt
- Score distribution shows learning curve:
  - **20+ days ago**: 40-70% (lower scores)
  - **10-20 days ago**: 60-80% (medium scores)
  - **0-10 days ago**: 70-95% (higher scores)
- Random times throughout the day
- Completion time: 30-60 minutes

#### 2. Finals Mode (40-60 attempts)
- 30 questions per attempt (10 easy, 10 average, 10 difficult)
- Higher scores than elimination:
  - **20+ days ago**: 50-75%
  - **10-20 days ago**: 65-85%
  - **0-10 days ago**: 75-95%
- Random difficulty levels
- Completion time: 15-30 minutes

#### 3. Review Mode (20-30 attempts)
- 10 questions per attempt
- Random topics from all 10 available topics
- Score range: 60-90%
- Completion time: 5-15 minutes

### Sample Data Features

✅ **Realistic timestamps** - Spread over 30 days
✅ **Learning curves** - Scores improve over time
✅ **Random variations** - Different topics, difficulties, times
✅ **Complete attempts** - All sessions marked as completed
✅ **Proper relationships** - Sessions linked to attempts

### Usage

```bash
python scripts/insert_sample_data.py
```

**Interactive prompts:**
- If sample data exists, asks to remove and recreate
- Confirms before proceeding

**Expected output:**
```
======================================================================
IT-QUIZBEE: Insert Sample Data for Admin Dashboard
======================================================================

🚀 Creating sample data...

📝 Creating Elimination Mode attempts...
   ✅ Created 72 elimination attempts
📝 Creating Finals Mode attempts...
   ✅ Created 48 finals attempts
📝 Creating Review Mode attempts...
   ✅ Created 25 review attempts

💾 Saving to database...

======================================================================
✅ SAMPLE DATA SUCCESSFULLY CREATED!
======================================================================

📊 Summary:
   • Total Sessions: 145
   • Total Attempts: 145
   • Elimination Attempts: 72
   • Finals Attempts: 48
   • Review Attempts: 25
   • Date Range: Last 30 days

🌐 View the data:
   • Admin Dashboard: http://localhost:5000/admin
   • API Summary: http://localhost:5000/api/analytics/summary

💡 To remove this sample data, run: python scripts/remove_sample_data.py
======================================================================
```

### Sample Data Identification

All sample data is prefixed with `sample-` in the database:
- Session IDs: `sample-elim-0001`, `sample-finals-0002`, etc.
- This allows easy identification and removal

---

## Remove Sample Data Script

### What It Does

Safely removes all sample data created by `insert_sample_data.py` without affecting real quiz attempts.

### Usage

#### Remove Sample Data Only

```bash
python scripts/remove_sample_data.py
```

**Interactive prompts:**
- Shows count of sample sessions and attempts
- Requires typing `DELETE` to confirm

**Expected output:**
```
======================================================================
IT-QUIZBEE: Remove Sample Data
======================================================================

📊 Found sample data:
   • Sessions: 145
   • Attempts: 145

⚠️  WARNING: This will permanently delete all sample data!
   This action cannot be undone.

Type 'DELETE' to confirm removal: DELETE

🗑️  Removing sample data...

======================================================================
✅ SAMPLE DATA SUCCESSFULLY REMOVED!
======================================================================

📊 Deletion Summary:
   • Sessions Removed: 145
   • Attempts Removed: 145

🌐 Verify removal:
   • Admin Dashboard: http://localhost:5000/admin
   • API Summary: http://localhost:5000/api/analytics/summary

💡 To add sample data again, run: python scripts/insert_sample_data.py
======================================================================
```

#### Remove ALL Data (Dangerous!)

```bash
python scripts/remove_sample_data.py --all
```

⚠️ **WARNING**: This removes ALL quiz data, including real attempts!

**Safety features:**
- Double confirmation required
- Must type `YES` and then `DELETE ALL DATA`
- Clear warnings about permanence

---

## Testing the Admin Dashboard

### Step-by-Step Testing Guide

#### 1. Prepare Database
```bash
# Ensure database is initialized
python scripts/init_db.py
```

#### 2. Insert Sample Data
```bash
python scripts/insert_sample_data.py
```

#### 3. Start Application
```bash
python app.py
```

#### 4. View Dashboard
Open browser to: `http://localhost:5000/admin`

#### 5. Verify Charts and Data

**Summary Cards:**
- [ ] Total Attempts shows ~120-170
- [ ] Average Score shows realistic percentage
- [ ] Popular Mode shows "Elimination"
- [ ] Completed Sessions matches total attempts

**Performance by Mode Chart:**
- [ ] Shows three modes with different heights
- [ ] Elimination has most attempts
- [ ] Finals has fewer attempts
- [ ] Review has fewest attempts

**Performance by Difficulty Chart:**
- [ ] Shows Easy, Average, Difficult
- [ ] Scores should vary by difficulty

**Performance Trend Chart:**
- [ ] Line shows data over 30 days
- [ ] Try different intervals (daily/weekly/monthly)
- [ ] Scores should show upward trend (learning curve)

**Performance by Topic Chart:**
- [ ] Shows multiple topics (if review mode data exists)
- [ ] Topics with data appear in pie chart

**Recent Attempts Table:**
- [ ] Shows 20 most recent attempts
- [ ] Dates within last 30 days
- [ ] Scores are color-coded (green/yellow/red)
- [ ] Filter by mode works
- [ ] Filter by date range works

**Statistics Panels:**
- [ ] Mode statistics show breakdown
- [ ] Difficulty statistics show breakdown
- [ ] Numbers match charts

#### 6. Test Filters

**Mode Filter:**
```
1. Select "Elimination Full"
2. Table shows only elimination attempts
3. Select "Finals Full"
4. Table shows only finals attempts
5. Select "All Modes"
6. Table shows all attempts
```

**Date Range Filter:**
```
1. Select "Last 7 Days"
2. Fewer attempts shown
3. Select "Last 30 Days"
4. More attempts shown
```

**Trend Interval:**
```
1. Select "Daily"
2. Chart shows daily data points
3. Select "Weekly"
4. Chart groups by week
5. Select "Monthly"
6. Chart shows single month
```

#### 7. Test API Endpoints

```bash
# Summary
curl http://localhost:5000/api/analytics/summary

# By Mode
curl http://localhost:5000/api/analytics/by-mode

# By Difficulty
curl http://localhost:5000/api/analytics/by-difficulty

# By Topic
curl http://localhost:5000/api/analytics/by-topic

# Recent Attempts
curl "http://localhost:5000/api/analytics/recent-attempts?limit=10&days=7"

# Performance Trend
curl "http://localhost:5000/api/analytics/performance-trend?days=30&interval=day"
```

#### 8. Clean Up
```bash
python scripts/remove_sample_data.py
# Type DELETE when prompted
```

---

## Advanced Testing Scenarios

### Scenario 1: Empty Database
```bash
python scripts/remove_sample_data.py
# Dashboard should show "No quiz attempts yet"
```

### Scenario 2: Small Dataset
Modify `insert_sample_data.py` to create fewer attempts:
- Change `random.randint(60, 80)` to `random.randint(5, 10)`
- Test with minimal data

### Scenario 3: Large Dataset
Modify ranges to create more data:
- Change to `random.randint(100, 200)`
- Test dashboard performance with large dataset

### Scenario 4: Recent Data Only
Modify date range:
- Change `timedelta(days=30)` to `timedelta(days=7)`
- Test trend charts with limited date range

### Scenario 5: Different Score Distributions
Modify score ranges in `generate_sample_answers()`:
- Test with all high scores (80-100)
- Test with all low scores (20-50)
- Test with very random scores

---

## Troubleshooting

### Sample Data Not Showing

**Problem:** Dashboard shows no data after inserting

**Solutions:**
1. Check database connection:
   ```bash
   python scripts/init_db.py
   ```

2. Verify data was inserted:
   ```bash
   curl http://localhost:5000/api/analytics/summary
   ```

3. Check for errors in browser console (F12)

4. Restart Flask application

### Cannot Remove Sample Data

**Problem:** Script says no sample data found

**Solutions:**
1. Check if data was actually inserted
2. Verify database connection
3. Check session IDs start with `sample-`

### Charts Not Loading

**Problem:** Dashboard loads but charts are empty

**Solutions:**
1. Check browser console for JavaScript errors
2. Verify Chart.js CDN is accessible
3. Clear browser cache
4. Check API endpoints return data

### Database Errors

**Problem:** MySQL connection errors

**Solutions:**
1. Ensure MySQL server is running
2. Check `.env` file for correct credentials
3. Verify database exists:
   ```bash
   mysql -u root -p
   SHOW DATABASES;
   ```

---

## Best Practices

### ✅ Do's

- **Always test with sample data first** before using real data
- **Remove sample data** before deploying to production
- **Use version control** before running scripts
- **Backup database** before removing all data
- **Test incrementally** - start small, then increase data

### ❌ Don'ts

- **Don't use `--all` flag** unless absolutely necessary
- **Don't mix sample and real data** in production
- **Don't skip confirmations** - they exist for safety
- **Don't modify sample data manually** in database
- **Don't test in production** environment

---

## Sample Data Structure

### Session Example
```python
{
    'id': 'sample-elim-0001',
    'session_type': 'elimination',
    'created_at': '2025-10-15T14:30:00',
    'expires_at': '2025-10-15T16:30:00',
    'completed': True,
    'questions': [/* 100 sample questions */]
}
```

### Attempt Example
```python
{
    'id': 'auto-generated-uuid',
    'session_id': 'sample-elim-0001',
    'quiz_mode': 'elimination_full',
    'total_questions': 100,
    'correct_answers': 72,
    'score_percentage': 72.0,
    'created_at': '2025-10-15T14:30:00',
    'completed_at': '2025-10-15T15:15:00'
}
```

---

## Integration with CI/CD

### Automated Testing

```bash
# In your test script
python scripts/insert_sample_data.py
python -m pytest tests/test_admin_dashboard.py
python scripts/remove_sample_data.py
```

### Docker Integration

```dockerfile
# In Dockerfile
RUN python scripts/insert_sample_data.py
# Run tests
RUN python scripts/remove_sample_data.py
```

---

## Support

If you encounter issues:

1. Check this documentation
2. Verify database connection
3. Check Flask application logs
4. Inspect browser console
5. Test API endpoints directly

## License

Same as main IT-Quizbee application (MIT License)
