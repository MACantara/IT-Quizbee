# IT-Quizbee Data Reorganization

## Overview
This document describes the reorganization of quiz data to support multiple game modes.

## New Structure

### Before Reorganization
```
data/
  topic_name/
    index.json
    subtopic1.json
    subtopic2.json
    ...
```

### After Reorganization
```
data/
  topic_name/
    index.json
    subtopic1/
      elimination/
        subtopic1.json (with mode: "elimination")
      finals/
        easy/
          subtopic1.json (with mode: "finals", difficulty: "easy")
        average/
          subtopic1.json (with mode: "finals", difficulty: "average")
        difficult/
          subtopic1.json (with mode: "finals", difficulty: "difficult")
    subtopic2/
      elimination/
        subtopic2.json (with mode: "elimination")
      finals/
        easy/
          subtopic2.json (with mode: "finals", difficulty: "easy")
        average/
          subtopic2.json (with mode: "finals", difficulty: "average")
        difficult/
          subtopic2.json (with mode: "finals", difficulty: "difficult")
    ...
```

## Game Modes

### 1. Elimination Mode
- Contains the original quiz questions
- Each question file has `"mode": "elimination"` field
- Questions are designed for competitive elimination gameplay

### 2. Finals Mode
- Contains placeholder questions (to be filled later)
- Each question file has `"mode": "finals"` field
- Organized by difficulty levels:
  - **Easy**: Introductory finals questions
  - **Average**: Moderate difficulty finals questions
  - **Difficult**: Advanced/challenging finals questions
- Questions will be designed for finals/championship rounds
- Currently contains 10 placeholder questions per difficulty level per subtopic

## JSON Structure

### Elimination Mode File Example
```json
{
  "subtopic_id": "oop_basics",
  "subtopic_name": "OOP Basics",
  "mode": "elimination",
  "questions": [
    {
      "question": "What is OOP?",
      "options": ["...", "...", "...", "..."],
      "correct": 0,
      "explanation": "..."
    }
  ]
}
```

### Finals Mode File Example (Placeholder)
```json
{
  "subtopic_id": "oop_basics",
  "subtopic_name": "OOP Basics",
  "mode": "finals",
  "difficulty": "easy",
  "questions": [
    {
      "question": "OOP Basics - Finals Question 1 (easy): Sample finals question about this topic?",
      "options": [
        "Option A for question 1",
        "Option B for question 1",
        "Option C for question 1",
        "Option D for question 1"
      ],
      "correct": 1,
      "explanation": "This is the explanation for finals question 1 in OOP Basics. The correct answer provides the best solution."
    }
  ]
}
```

**Note:** Finals files include a `"difficulty"` field with values: "easy", "average", or "difficult".

## Topics Included
1. computer_architecture (10 subtopics)
2. data_science (10 subtopics)
3. dbms (10 subtopics)
4. ecommerce_web (10 subtopics)
5. it_basics (10 subtopics)
6. logic (10 subtopics)
7. networks (10 subtopics)
8. oop (10 subtopics)
9. operating_systems (10 subtopics)
10. software_engineering (10 subtopics)

**Total: 100 subtopics**

## Files Created
- **100 elimination mode files** (migrated from original files)
- **300 finals mode placeholder files** (new)
  - 100 easy difficulty files
  - 100 average difficulty files
  - 100 difficult difficulty files
- **Total: 400 quiz files**

## Scripts

### preview_reorganization.py
- Shows what will happen without making changes
- Displays file counts and structure preview
- Run before executing reorganization

### reorganize_quiz_data.py
- Main reorganization script
- Adds "mode" field to existing files
- Creates new folder structure
- Generates finals mode placeholders
- **⚠️ WARNING: This script will delete original files after migration**

## Running the Reorganization

1. **Preview first:**
   ```bash
   python preview_reorganization.py
   ```

2. **Execute reorganization:**
   ```bash
   python reorganize_quiz_data.py
   ```
   - Type "yes" when prompted to confirm
   - The script will process all topics
   - Original files will be deleted after successful migration

3. **Verify results:**
   - Check that elimination/ and finals/ folders exist in each subtopic
   - Verify that finals/ folder contains easy/, average/, and difficult/ subfolders
   - Confirm that JSON files have the correct "mode" and "difficulty" fields

## Next Steps

### For Finals Mode
1. Review the placeholder questions in finals/{easy,average,difficult}/ folders
2. Replace placeholder questions with actual finals-level questions
3. Ensure finals questions are:
   - **Easy**: Accessible but still finals-worthy questions
   - **Average**: Moderately challenging questions
   - **Difficult**: Expert-level, highly challenging questions
   - Progressively more difficult across the three levels
   - Suitable for championship rounds

### Application Updates
Update the application code to:
1. Read from the new folder structure
2. Support mode selection (elimination vs finals)
3. Support difficulty selection for finals mode (easy/average/difficult)
4. Load questions based on selected mode, difficulty, and subtopic
5. Handle the nested folder structure

## Reverting Changes

If you need to revert to the original structure:
1. Copy files from `subtopic_name/elimination/subtopic_name.json`
2. Remove the "mode" field
3. Move files back to the topic root directory
4. Delete subtopic_name/ folders

**Note:** It's recommended to backup your data before running the reorganization script.

## Statistics
- **Topics:** 10
- **Subtopics per topic:** ~10
- **Total subtopics:** 100
- **Questions per subtopic (elimination):** 10
- **Questions per difficulty level (finals):** 10 (placeholder)
- **Total elimination questions:** ~1,000
- **Total finals placeholder questions:** 3,000 (1,000 per difficulty level)
- **Grand total questions (after finals completion):** ~4,000

## Contact
For questions or issues, refer to the main IT-Quizbee documentation or repository.
