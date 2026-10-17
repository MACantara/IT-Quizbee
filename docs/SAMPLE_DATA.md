# Testing with Sample Data

## Overview

Two scripts are provided to help you test the application with realistic sample quiz attempts:

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
✅ **Complete attempts** - All attempts marked as completed
✅ **Real questions** - Loaded from the `data/` folder

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
IT-QUIZBEE: Insert Sample Data
======================================================================

🚀 Creating sample data...

📝 Creating Elimination Mode attempts...
   ✅ Created 72 elimination attempts
📝 Creating Finals Mode attempts...
   ✅ Created 48 finals attempts
📝 Creating Review Mode attempts...
   ✅ Created 25 review attempts

💾 Saving to JSON store...

======================================================================
✅ SAMPLE DATA SUCCESSFULLY CREATED!
======================================================================

📊 Summary:
   • Total Attempts: 145
   • Elimination Attempts: 72
   • Finals Attempts: 48
   • Review Attempts: 25
   • Date Range: Last 30 days

💡 To remove this sample data, run: python scripts/remove_sample_data.py
======================================================================
```

### Sample Data Identification

All sample data is prefixed with `sample-` in the JSON store:
- Session IDs: `sample-elim-0001`, `sample-finals-0002`, `sample-re-*-0003`, etc.
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
- Shows count of sample attempts
- Requires typing `DELETE` to confirm

**Expected output:**
```
======================================================================
IT-QUIZBEE: Remove Sample Data
======================================================================

📊 Found sample data:
   • Attempts: 145

⚠️  WARNING: This will permanently delete all sample data!
   This action cannot be undone.

Type 'DELETE' to confirm removal: DELETE

🗑️  Removing sample data...

======================================================================
✅ SAMPLE DATA SUCCESSFULLY REMOVED!
======================================================================

📊 Deletion Summary:
   • Attempts Removed: 145

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

## Testing with Sample Data

### Step-by-Step Testing Guide

#### 1. Prepare Storage
No database setup is needed — attempts persist to `instance/attempts.json` automatically on first write.

#### 2. Insert Sample Data
```bash
python scripts/insert_sample_data.py
```

#### 3. Verify Sample Data
```bash
python scripts/verify_sample_data.py
```

Shows:
- Total attempts in the JSON store
- Sample data count by mode
- Score statistics (avg, min, max)
- Date range of sample data
- Warning if real (non-sample) data exists

#### 4. Start Application
```bash
python run.py
```

#### 5. Review an Attempt
Open a sample attempt in the browser:

```
http://localhost:5000/quiz/review/<attempt_id>
```

Use the `id` of any attempt from `instance/attempts.json` (or the output of `verify_sample_data.py`).

#### 6. Clean Up
```bash
python scripts/remove_sample_data.py
# Type DELETE when prompted
```

---

## Advanced Testing Scenarios

### Scenario 1: Empty Store
```bash
python scripts/remove_sample_data.py
# Verify with: python scripts/verify_sample_data.py
```

### Scenario 2: Small Dataset
Modify `insert_sample_data.py` to create fewer attempts:
- Change `random.randint(60, 80)` to `random.randint(5, 10)`
- Test with minimal data

### Scenario 3: Large Dataset
Modify ranges to create more data:
- Change to `random.randint(100, 200)`
- Test the app with a large dataset

### Scenario 4: Recent Data Only
Modify date range:
- Change `timedelta(days=30)` to `timedelta(days=7)`
- Test with a limited date range

### Scenario 5: Different Score Distributions
Modify score ranges in `generate_sample_answers()`:
- Test with all high scores (80-100)
- Test with all low scores (20-50)
- Test with very random scores

---

## Troubleshooting

### Sample Data Not Showing

**Problem:** No sample attempts after inserting

**Solutions:**
1. Check the JSON store exists and is writable:
   ```bash
   ls instance/
   ```

2. Verify data was inserted:
   ```bash
   python scripts/verify_sample_data.py
   ```

3. Restart Flask application

### Cannot Remove Sample Data

**Problem:** Script says no sample data found

**Solutions:**
1. Check if data was actually inserted
2. Verify `instance/attempts.json` is writable
3. Check session IDs start with `sample-`

### Storage Errors

**Problem:** Data not persisted to the JSON store

**Solutions:**
1. Ensure the `instance/` directory exists and is writable
2. Check `QUIZBEE_STORE_DIR` if a custom store location is configured
3. Verify the store files contain valid JSON:
   ```bash
   cat instance/attempts.json
   ```

---

## Best Practices

### ✅ Do's

- **Always test with sample data first** before using real data
- **Remove sample data** before deploying to production
- **Use version control** before running scripts
- **Back up `instance/`** before removing all data
- **Test incrementally** - start small, then increase data

### ❌ Don'ts

- **Don't use `--all` flag** unless absolutely necessary
- **Don't mix sample and real data** in production
- **Don't skip confirmations** - they exist for safety
- **Don't modify sample data manually** in the JSON store files
- **Don't test in production** environment

---

## Sample Data Structure

### Attempt Example
```python
{
    'id': 'auto-generated-uuid',
    'session_id': 'sample-elim-0001',
    'quiz_type': 'elimination',
    'topic': 'all_topics',
    'subtopic': None,
    'difficulty': 'mixed',
    'user_name': 'Sample User',
    'score': 72.0,
    'correct_count': 72,
    'incorrect_count': 28,
    'time_taken': 2700,
    'answers': [/* detailed answer data */],
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
python -m pytest
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
2. Verify `instance/` exists and is writable
3. Check Flask application logs
4. Run `python scripts/verify_sample_data.py`

## License

Same as main IT-Quizbee application (MIT License)
