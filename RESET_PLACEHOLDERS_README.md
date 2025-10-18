# Reset to Placeholders Script

A utility script to reset JSON question files back to placeholder questions for the IT-Quizbee application.

## Overview

This script allows you to reset question files back to their placeholder state, which is useful when:
- Starting fresh with a subtopic
- Creating a template for new questions
- Removing all existing questions and starting over
- Testing the question generation workflow

## Features

- ✅ Resets both **elimination mode** (multiple choice) and **finals mode** (identification) questions
- ✅ Preserves metadata (subtopic_id, subtopic_name, mode, difficulty)
- ✅ Supports resetting individual topics or all topics at once
- ✅ Interactive prompts with safety confirmations
- ✅ Detailed progress reporting
- ✅ Maintains proper JSON formatting

## Usage

### Interactive Mode (Recommended)

Run the script without arguments for an interactive experience:

```bash
python reset_to_placeholders.py
```

The script will:
1. Display available topics
2. Ask you to select which topic to reset (or all topics)
3. Request confirmation (you must type "RESET" to proceed)
4. Reset all selected question files to placeholders
5. Display a summary of files reset

### Safety Features

⚠️ **Important**: This script REPLACES actual questions with placeholders!

- **Confirmation Required**: You must type "RESET" (case-sensitive) to proceed
- **Backup Reminder**: The script warns you to backup before proceeding
- **Reversible via Git**: If using version control, you can revert changes

## What Gets Reset

For each subtopic selected, the script resets:

### 1. Elimination Mode File (Multiple Choice)
- **Location**: `data/topic_id/subtopic_id/elimination/subtopic_id.json`
- **Format**: 10 multiple choice questions with 4 options each
- **Example**:
```json
{
  "subtopic_id": "abstraction",
  "subtopic_name": "Abstraction",
  "mode": "elimination",
  "questions": [
    {
      "question": "Abstraction - Elimination Question 1: [Placeholder question about Abstraction]",
      "options": [
        "[Option A for question 1]",
        "[Option B for question 1]",
        "[Option C for question 1]",
        "[Option D for question 1]"
      ],
      "correct": 1,
      "explanation": "[Explanation for elimination question 1. Replace with actual explanation.]"
    }
    // ... 9 more questions
  ]
}
```

### 2. Finals Mode Files (Identification)
- **Easy**: `data/topic_id/subtopic_id/finals/easy/subtopic_id.json`
- **Average**: `data/topic_id/subtopic_id/finals/average/subtopic_id.json`
- **Difficult**: `data/topic_id/subtopic_id/finals/difficult/subtopic_id.json`
- **Format**: 10 identification questions each
- **Example**:
```json
{
  "subtopic_id": "abstraction",
  "subtopic_name": "Abstraction",
  "mode": "finals",
  "difficulty": "easy",
  "questions": [
    {
      "question": "Abstraction - Finals (Easy) Question 1: [Placeholder identification question about Abstraction]",
      "answer": "[Correct answer for question 1]",
      "alternatives": [],
      "explanation": "[Explanation for finals - easy question 1. Replace with actual explanation.]"
    }
    // ... 9 more questions
  ]
}
```

## Available Topics

1. Computer Architecture & IT Security (`computer_architecture`)
2. Data Science & Analytics (`data_science`)
3. Database Management System (`dbms`)
4. E-commerce & Web Design (`ecommerce_web`)
5. Basic Computer Concepts & IT (`it_basics`)
6. Logic Formulation (`logic`)
7. Computer Networks & Telecommunication (`networks`)
8. Object Oriented Programming (`oop`)
9. Operating Systems (`operating_systems`)
10. Software Engineering (`software_engineering`)
11. **All Topics** (resets everything)

## Example Workflow

### Scenario 1: Reset a Single Topic

```bash
$ python reset_to_placeholders.py

Available Topics:
----------------------------------------------------------------------
  1. Computer Architecture & IT Security (computer_architecture)
  2. Data Science & Analytics (data_science)
  ...
  8. Object Oriented Programming (oop)
  ...
----------------------------------------------------------------------

Select topic to reset (1-11, or 'q' to quit): 8

======================================================================
You are about to reset: Object Oriented Programming
======================================================================

Type 'RESET' to confirm (or anything else to cancel): RESET

🚀 Starting reset process...

📁 Processing topic: Object Oriented Programming
   Subtopics to reset: 10

  🔄 Resetting subtopic: Abstraction
    ✅ Reset: oop/abstraction/elimination/abstraction.json
    ✅ Reset: oop/abstraction/finals/easy/abstraction.json
    ✅ Reset: oop/abstraction/finals/average/abstraction.json
    ✅ Reset: oop/abstraction/finals/difficult/abstraction.json
     ✨ Reset 4 file(s)

  ...

======================================================================
✅ RESET COMPLETE!
======================================================================
Total files reset: 40
```

### Scenario 2: Reset All Topics

```bash
$ python reset_to_placeholders.py

Select topic to reset (1-11, or 'q' to quit): 11

======================================================================
You are about to reset: ALL TOPICS
======================================================================

Type 'RESET' to confirm (or anything else to cancel): RESET

🚀 Starting reset process...
...
Total files reset: 400
```

## After Resetting

Once you've reset questions to placeholders:

1. **Replace Placeholder Content**
   - Open each JSON file
   - Replace placeholder questions with actual questions
   - Update options (for elimination) or answers (for finals)
   - Verify correct answer indices (0-3 for elimination mode)
   - Add meaningful explanations

2. **Update Documentation**
   ```bash
   python update_topics_md.py
   ```
   This updates `TOPICS.md` with current question counts.

3. **Test the Questions**
   - Run the Flask application
   - Navigate to the reset subtopic
   - Verify questions display correctly
   - Test both elimination and finals modes

## Question Format Details

### Elimination Mode (Multiple Choice)
- **Questions**: 10 per file
- **Options**: 4 choices per question
- **Correct Answer**: Index (0-3) indicating the correct option
- **Explanation**: Detailed explanation of the answer

### Finals Mode (Identification)
- **Questions**: 10 per difficulty level (30 total per subtopic)
- **Answer**: Short text answer (exact match)
- **Alternatives**: Array of acceptable alternative answers
- **Explanation**: Detailed explanation of the answer

## Troubleshooting

**Problem: "Data directory not found"**
- **Solution**: Ensure you're running the script from the IT-Quizbee root directory

**Problem: "index.json not found"**
- **Solution**: Verify the topic directory has a valid `index.json` file

**Problem: "Subtopic directory not found"**
- **Solution**: Check that the subtopic folder exists in the topic directory

**Problem: Questions not displaying after reset**
- **Solution**: Restart the Flask application to reload the question data

**Problem: Want to undo the reset**
- **Solution**: Use `git restore` to revert changes if using version control:
  ```bash
  git restore data/
  ```

## Technical Details

### File Structure
The script maintains the existing directory structure:
```
data/
├── topic_id/
│   ├── index.json
│   └── subtopic_id/
│       ├── elimination/
│       │   └── subtopic_id.json
│       └── finals/
│           ├── easy/
│           │   └── subtopic_id.json
│           ├── average/
│           │   └── subtopic_id.json
│           └── difficult/
│               └── subtopic_id.json
```

### Metadata Preservation
The script reads and preserves:
- `subtopic_id`: Unique identifier
- `subtopic_name`: Display name
- `mode`: "elimination" or "finals"
- `difficulty`: "easy", "average", or "difficult" (finals only)

### Error Handling
- Missing files are skipped with warnings
- Invalid JSON is reported
- Keyboard interrupts are handled gracefully
- All errors include descriptive messages

## Related Scripts

- **`add_new_subtopic.py`**: Create new subtopics with placeholder questions
- **`update_topics_md.py`**: Update TOPICS.md documentation with question counts
- **`question_generator.py`**: Generate questions using AI
- **`additional_questions.py`**: Add questions to existing subtopics

## License

This script is part of the IT-Quizbee project and follows the same MIT License.

## Author

Michael Angelo R. Cantara — https://github.com/MACantara

---

**Remember**: Always backup your questions before resetting! 💾
