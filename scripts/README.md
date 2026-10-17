# IT Quizbee - Utility Scripts

This folder contains utility scripts for managing and maintaining the IT Quizbee application.

## Storage

IT Quizbee persists data to JSON files via `JsonStore` (see `app/repositories/json_store.py`):

- `attempts.json` - quiz submission results (`QuizAttempt`)
- `reports.json` - user-reported question issues (`QuestionReport`)

Files live in `instance/` by default, or in the directory given by the
`QUIZBEE_STORE_DIR` environment variable. The store files are created
automatically on first write — there is no separate database to initialize.
Quiz sessions are not persisted; they live in the user's Flask session.

## Sample Data Scripts

### `insert_sample_data.py`
Generates realistic sample quiz data for testing the admin dashboard.

```bash
python scripts/insert_sample_data.py
```

**Creates:**
- 60-80 Elimination Mode attempts
- 40-60 Finals Mode attempts
- 20-30 Review Mode attempts
- 10-25 sample question reports
- Realistic score distributions
- Data spread over last 30 days

**Details:**
- Sample attempts use `session_id` values starting with `sample-`
- Sample reports use `id` values starting with `sample-`
- Idempotent: if sample data already exists, offers to remove and recreate it
- Loads real questions from `data/` so analytics look realistic
- No running app or database needed — writes directly to the JSON store

**Use cases:**
- Testing admin dashboard
- Demo presentations
- Development and debugging

### `remove_sample_data.py`
Safely removes all sample quiz data from the store.

```bash
python scripts/remove_sample_data.py
```

**Features:**
- Only removes sample data (`session_id` / `id` starting with `sample-`)
- Confirmation prompt required
- Preserves real user data
- Optional `--all` flag to empty both store files (use with caution)

### `verify_sample_data.py`
Quick verification script to check sample data status.

```bash
python scripts/verify_sample_data.py
```

**Displays:**
- Total attempts and question reports count
- Sample data breakdown by mode
- Report status/type breakdown
- Score statistics (avg, min, max)
- Date range of sample data
- Warning if real data exists

---

## Content Management Scripts

### `add_new_subtopic.py`
Interactive script to add a new subtopic to an existing topic.

```bash
python scripts/add_new_subtopic.py
```

**Features:**
- Lists all available topics
- Creates subtopic directory structure
- Generates placeholder questions
- Updates topic index file
- Auto-generates question IDs

**Creates:**
- `elimination/questions.json` - 100 placeholder questions
- `finals/easy.json` - 10 easy questions
- `finals/average.json` - 10 average questions
- `finals/difficult.json` - 10 difficult questions

### `update_topics_md.py`
Automatically generates/updates TOPICS.md documentation.

```bash
python scripts/update_topics_md.py
```

**Features:**
- Scans all topic folders
- Counts questions per subtopic
- Generates comprehensive topic list
- Updates statistics (topics, subtopics, questions)
- Creates formatted markdown documentation

---

## Quick Reference

### Sample Data Workflow
```bash
# 1. Add sample data for testing
python scripts/insert_sample_data.py

# 2. Verify sample data
python scripts/verify_sample_data.py

# 3. Remove it when done
python scripts/remove_sample_data.py
```

### Adding New Content
```bash
# 1. Create new subtopic
python scripts/add_new_subtopic.py

# 2. Edit the generated JSON files in data/[topic]/[subtopic]/

# 3. Update documentation
python scripts/update_topics_md.py
```

### Testing & Cleanup
```bash
# Add test data
python scripts/insert_sample_data.py

# View in browser: http://localhost:5000/admin

# Remove test data
python scripts/remove_sample_data.py
```

---

## Script Dependencies

All scripts require:
- Python 3.8+
- python-dotenv (only used to load `QUIZBEE_STORE_DIR` etc. from `.env`)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Environment Configuration

Scripts read from `.env` file:
```env
QUIZBEE_STORE_DIR=instance   # optional; defaults to <repo>/instance
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password
```

## Error Handling

Common issues and solutions:

**Store write errors:**
- Verify `QUIZBEE_STORE_DIR` points to a writable directory
- Check file permissions on the `instance/` folder

**Import errors:**
- Run from project root directory
- Ensure all dependencies installed
- Activate virtual environment if used

**No topics found:**
- Check that the `data/` folder contains topic question files

---

## Best Practices

1. **Always backup** `instance/` before wiping data with `--all`
2. **Test with sample data** before using real data
3. **Update documentation** after adding subtopics
4. **Verify changes** after running scripts
5. **Use version control** to track changes

## Related Documentation

- [Main README](../README.md) - Application overview
- [SAMPLE_DATA_README.md](../docs/SAMPLE_DATA_README.md) - Sample data usage
- [ADD_SUBTOPIC_README.md](../docs/ADD_SUBTOPIC_README.md) - Subtopic creation guide
