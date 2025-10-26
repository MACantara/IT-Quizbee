# IT Quizbee - Utility Scripts

This folder contains utility scripts for managing and maintaining the IT Quizbee application.

## Database Scripts

### `init_db.py`
Initializes the MySQL database with required tables.

```bash
python scripts/init_db.py
```

**Purpose:**
- Creates `quiz_sessions` table
- Creates `quiz_attempts` table
- Sets up database indexes
- Configures connection pooling

**When to use:**
- First-time setup
- After database schema changes
- When resetting the database

---

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
- Realistic score distributions
- Data spread over last 30 days

**Use cases:**
- Testing admin dashboard
- Demo presentations
- Development and debugging

### `remove_sample_data.py`
Safely removes all sample quiz data from the database.

```bash
python scripts/remove_sample_data.py
```

**Features:**
- Only removes sample data (IDs starting with `sample-`)
- Confirmation prompt required
- Preserves real user data
- Optional `--all` flag to remove ALL data (use with caution)

### `verify_sample_data.py`
Quick verification script to check sample data status.

```bash
python scripts/verify_sample_data.py
```

**Displays:**
- Total sessions and attempts count
- Sample data breakdown by mode
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

### First-Time Setup
```bash
# 1. Initialize database
python scripts/init_db.py

# 2. Add sample data for testing
python scripts/insert_sample_data.py

# 3. Verify sample data
python scripts/verify_sample_data.py
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
- Flask
- Flask-SQLAlchemy
- PyMySQL
- python-dotenv

Install dependencies:
```bash
pip install -r requirements.txt
```

## Environment Configuration

Scripts read from `.env` file:
```env
MYSQL_PUBLIC_URL=mysql://username:password@host:port/database
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password
```

## Error Handling

Common issues and solutions:

**Database connection errors:**
- Ensure MySQL server is running
- Verify MYSQL_PUBLIC_URL in .env
- Check database credentials

**Import errors:**
- Run from project root directory
- Ensure all dependencies installed
- Activate virtual environment if used

**Permission errors:**
- Check database user permissions
- Verify write access to data/ folder

---

## Best Practices

1. **Always backup** before running database scripts
2. **Test with sample data** before using real data
3. **Update documentation** after adding subtopics
4. **Verify changes** after running scripts
5. **Use version control** to track changes

## Related Documentation

- [Main README](../README.md) - Application overview
- [SAMPLE_DATA_README.md](../docs/SAMPLE_DATA_README.md) - Sample data usage
- [ADD_SUBTOPIC_README.md](../docs/ADD_SUBTOPIC_README.md) - Subtopic creation guide
- [MYSQL_SETUP.md](../docs/MYSQL_SETUP.md) - Database setup guide
