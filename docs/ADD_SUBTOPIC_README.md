# Add New Subtopic Script

## Overview
The `add_new_subtopic.py` script allows you to easily add new subtopics to any existing topic in the IT-Quizbee quiz system. It automatically creates all necessary files and folder structures.

## What It Creates

For each new subtopic, the script creates:

1. **Elimination Mode** (1 file)
   - 10 placeholder questions
   - File: `topic/subtopic_id/elimination/subtopic_id.json`

2. **Finals Mode - Easy** (1 file)
   - 10 placeholder questions
   - File: `topic/subtopic_id/finals/easy/subtopic_id.json`

3. **Finals Mode - Average** (1 file)
   - 10 placeholder questions
   - File: `topic/subtopic_id/finals/average/subtopic_id.json`

4. **Finals Mode - Difficult** (1 file)
   - 10 placeholder questions
   - File: `topic/subtopic_id/finals/difficult/subtopic_id.json`

**Total: 4 files with 40 placeholder questions (10 + 10 + 10 + 10)**

## Usage

### Step 1: Run the Script
```bash
python scripts/add_new_subtopic.py
```

### Step 2: Select a Topic
The script will display all 10 available topics:
```
1. Computer Architecture & IT Security (computer_architecture)
2. Data Science & Analytics (data_science)
3. Database Management System (dbms)
4. E-commerce & Web Design (ecommerce_web)
5. Basic Computer Concepts & IT (it_basics)
6. Logic Formulation (logic)
7. Computer Networks & Telecommunication (networks)
8. Object Oriented Programming (oop)
9. Operating Systems (operating_systems)
10. Software Engineering (software_engineering)
```

Enter the number of your chosen topic (1-10) or 'q' to quit.

### Step 3: Enter Subtopic Information

**Subtopic ID:**
- Use lowercase with underscores
- Example: `cloud_computing`, `machine_learning`, `api_design`
- The script automatically converts spaces to underscores

**Subtopic Name:**
- Human-readable display name
- Example: `Cloud Computing`, `Machine Learning`, `API Design`

**Description (Optional):**
- Brief description of the subtopic
- If left empty, defaults to "Questions about [Subtopic Name]"

### Step 4: Confirm Creation
The script shows a summary and asks for confirmation:
```
Topic: Data Science & Analytics
Subtopic ID: machine_learning_advanced
Subtopic Name: Advanced Machine Learning
Description: Deep learning and neural networks

Files to be created:
  • data_science/machine_learning_advanced/elimination/machine_learning_advanced.json
  • data_science/machine_learning_advanced/finals/easy/machine_learning_advanced.json
  • data_science/machine_learning_advanced/finals/average/machine_learning_advanced.json
  • data_science/machine_learning_advanced/finals/difficult/machine_learning_advanced.json

Proceed with creation? (yes/no):
```

Type `yes` to proceed.

### Step 5: Update Documentation
After successful creation, update the TOPICS.md file:
```bash
python scripts/update_topics_md.py
```

## Example Session

```bash
$ python scripts/add_new_subtopic.py

======================================================================
IT-QUIZBEE: ADD NEW SUBTOPIC
======================================================================

Enter topic number (1-10): 2

✅ Selected topic: Data Science & Analytics

Enter subtopic ID: deep_learning
Enter subtopic name: Deep Learning
Enter subtopic description: Neural networks and deep learning concepts

Proceed with creation? (yes/no): yes

🚀 Creating subtopic files...

📁 Created directory: data_science/deep_learning
  ✅ Created: elimination/deep_learning.json (10 questions)
  ✅ Created: finals/easy/deep_learning.json (10 questions)
  ✅ Created: finals/average/deep_learning.json (10 questions)
  ✅ Created: finals/difficult/deep_learning.json (10 questions)

✨ Total files created: 4
✨ Total questions created: 40

✅ Updated index.json - added 'Deep Learning'
   Total subtopics in Data Science & Analytics: 11

✅ SUBTOPIC SUCCESSFULLY CREATED!
```

## JSON Structure

### Elimination Mode Example
```json
{
  "subtopic_id": "deep_learning",
  "subtopic_name": "Deep Learning",
  "mode": "elimination",
  "questions": [
    {
      "question": "Deep Learning - Elimination Question 1: [Placeholder question]",
      "options": [
        "[Option A for question 1]",
        "[Option B for question 1]",
        "[Option C for question 1]",
        "[Option D for question 1]"
      ],
      "correct": 1,
      "explanation": "[Explanation for elimination question 1]",
      "id": "deep_learn_deep_learn_elim_000"
    }
    // ... 9 more questions
  ]
}
```

### Finals Mode Example (with Difficulty)
```json
{
  "subtopic_id": "deep_learning",
  "subtopic_name": "Deep Learning",
  "mode": "finals",
  "difficulty": "difficult",
  "questions": [
    {
      "question": "Deep Learning - Finals (Difficult) Question 1: [Placeholder question]",
      "answer": "[Correct answer for question 1]",
      "alternatives": [],
      "explanation": "[Explanation for finals - difficult question 1]",
      "id": "deep_learn_deep_learn_d_finals_000"
    }
    // ... 9 more questions
  ]
}
```

## Features

✅ **Interactive Interface** - User-friendly prompts guide you through the process
✅ **Automatic Structure** - Creates all folders and files automatically
✅ **Index Update** - Automatically updates the topic's index.json file
✅ **Duplicate Detection** - Warns if subtopic ID already exists
✅ **Validation** - Ensures all required information is provided
✅ **Summary Display** - Shows exactly what will be created before proceeding

## After Creation

Once you've created a new subtopic with placeholder questions:

1. **Replace Placeholder Content**
   - Open each JSON file
   - Replace placeholder questions with actual questions
   - Update options with relevant choices
   - Verify correct answer indices (0-3)
   - Add meaningful explanations

2. **Update Documentation**
   ```bash
   python scripts/update_topics_md.py
   ```
   This updates TOPICS.md with the new subtopic and question counts.

3. **Test the Questions**
   - Verify questions are appropriate for their difficulty level
   - Ensure elimination questions are suitable for competitive rounds
   - Make finals questions progressively harder (easy → average → difficult)

## Tips

- **Subtopic IDs**: Keep them short, descriptive, and use underscores
- **Naming Convention**: Use title case for subtopic names
- **Descriptions**: Be concise but informative
- **Question Quality**: 
  - Elimination: Clear, straightforward questions
  - Finals Easy: Slightly more challenging
  - Finals Average: Requires deeper understanding
  - Finals Difficult: Expert-level, complex scenarios

## Troubleshooting

**Problem: "Topic directory not found"**
- Solution: Ensure you're running the script from the IT-Quizbee root directory

**Problem: "index.json not found"**
- Solution: Create an index.json file in the topic folder with proper structure

**Problem: "Subtopic already exists"**
- Solution: Choose a different subtopic ID or confirm overwrite

## Related Scripts

- `reorganize_quiz_data.py` - Reorganizes existing data structure
- `update_topics_md.py` - Updates TOPICS.md documentation
- `preview_reorganization.py` - Previews reorganization changes

---

**Happy Quiz Building! 🎓✨**
