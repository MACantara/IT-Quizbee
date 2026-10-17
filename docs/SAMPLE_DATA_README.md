# Sample Data Scripts

Quick reference for testing the app with sample quiz attempts.

## Insert Sample Data

Creates ~120-170 realistic quiz attempts over the last 30 days.

```bash
python scripts/insert_sample_data.py
```

**What it creates:**
- 60-80 Elimination Mode attempts
- 40-60 Finals Mode attempts
- 20-30 Review Mode attempts
- Realistic score distributions showing learning curves
- Random timestamps throughout each day

## Remove Sample Data

Safely removes all sample quiz data.

```bash
python scripts/remove_sample_data.py
```

Type `DELETE` when prompted to confirm.

**Safety:** Only removes data with IDs starting with `sample-` (created by the insert script).

## Verify Sample Data

Check what sample data exists without opening the browser:

```bash
python scripts/verify_sample_data.py
```

Shows:
- Total sessions and attempts in the JSON store
- Sample data count by mode
- Score statistics (avg, min, max)
- Date range of sample data
- Warning if real (non-sample) data exists

## View Results

After inserting sample data:
- **Verify**: `python scripts/verify_sample_data.py`
- **Review an attempt**: http://localhost:5000/quiz/review/&lt;attempt_id&gt;

## Complete Documentation

See [docs/SAMPLE_DATA.md](docs/SAMPLE_DATA.md) for:
- Detailed usage instructions
- Testing scenarios
- Troubleshooting guide
- Best practices
- Sample data structure

## Quick Test Flow

```bash
# 1. Insert sample data
python scripts/insert_sample_data.py

# 2. Verify it was created
python scripts/verify_sample_data.py

# 3. Start the app
python run.py

# 4. Review a sample attempt
# Open http://localhost:5000/quiz/review/<attempt_id> in browser

# 5. Clean up
python scripts/remove_sample_data.py
# Type DELETE when prompted
```

## Advanced Usage

### Remove ALL data (including real attempts)
```bash
python scripts/remove_sample_data.py --all
```
⚠️ **WARNING:** This removes EVERYTHING! Use with extreme caution.

Requires double confirmation:
1. Type `YES`
2. Type `DELETE ALL DATA`

## Features

✅ **Sample data is isolated** - Can be removed without affecting real data
✅ **Realistic patterns** - Shows learning curves and score distributions
✅ **Multiple game modes** - Covers elimination, finals, and review modes
✅ **Date range** - Spreads data over 30 days
✅ **Safe operations** - Confirmation prompts prevent accidents

## Troubleshooting

If sample data doesn't appear:
1. Verify `instance/attempts.json` exists and is writable
2. Run `python scripts/verify_sample_data.py` to check the store
3. Restart Flask application

For more help, see [docs/SAMPLE_DATA.md](docs/SAMPLE_DATA.md)
