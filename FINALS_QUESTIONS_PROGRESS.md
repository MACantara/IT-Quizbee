# Finals Questions Replacement - Progress and Instructions

## Overview
This project involves replacing 3000 placeholder identification questions with actual educational content across 10 IT topics, 100 subtopics, 3 difficulty levels.

## Current Progress
- **Completed**: 60/3000 questions (2%)
- **Subtopics with real questions**: 
  - Computer Architecture > CPU Architecture (30 questions)
  - Computer Architecture > Memory Hierarchy (30 questions)

## Tool: question_generator.py
The `question_generator.py` script handles updating all finals JSON files. It:
1. Reads the QUESTIONS_DB dictionary containing questions for each subtopic
2. Updates all matching JSON files in the data/ directory
3. Reports progress

### Usage
```bash
python3 question_generator.py
```

## Question Format
Each question follows this structure:
```python
{
    "question": "What is...?",
    "answer": "The correct answer",
    "alternatives": ["Alternative 1", "Alternative 2"],
    "explanation": "Detailed explanation of the concept..."
}
```

## How to Add More Questions

### Step 1: Choose a Subtopic
Pick a subtopic from the list of 98 remaining subtopics (see TOPICS.md or issue description)

### Step 2: Research the Topic
Understand the key concepts, terminology, and difficulty progression for that subtopic

### Step 3: Add to QUESTIONS_DB
In `question_generator.py`, add a new entry following this pattern:

```python
QUESTIONS_DB['subtopic_id'] = {
    "easy": [
        # 10 questions for easy difficulty
        {"question": "...", "answer": "...", "alternatives": [...], "explanation": "..."},
        # ... 9 more
    ],
    "average": [
        # 10 questions for average difficulty
    ],
    "difficult": [
        # 10 questions for difficult difficulty  
    ]
}
```

### Step 4: Run the Script
```bash
python3 question_generator.py
```

### Step 5: Verify
Check that the JSON files were updated correctly:
```bash
python3 -c "import json; data = json.load(open('data/TOPIC/SUBTOPIC/finals/easy/SUBTOPIC.json')); print(data['questions'][0])"
```

## Quality Guidelines

### Easy Questions
- Test basic terminology and fundamental concepts
- Answers should be single words or short phrases
- Explanations should define terms clearly

### Average Questions  
- Test understanding of relationships between concepts
- Require knowledge of how things work together
- May involve multiple related concepts

### Difficult Questions
- Test deep technical knowledge
- May involve complex scenarios or edge cases
- Explanations should provide advanced insights

## Subtopics Needing Questions

### Computer Architecture & IT Security (8 remaining)
- instruction_set
- pipelining
- parallel_processing
- cryptography
- security_threats
- authentication
- security_protocols
- cyber_defense

### Data Science & Analytics (10 subtopics)
- data_fundamentals
- statistics
- data_preprocessing
- data_visualization
- ml_basics
- supervised_learning
- unsupervised_learning
- python_data_tools
- big_data
- data_ethics

### Database Management (10 subtopics)
- database_fundamentals
- relational_model
- sql_basics
- sql_advanced
- normalization
- transactions
- indexing
- nosql
- database_design
- database_security

### E-commerce & Web Design (10 subtopics)
- html_basics
- css_styling
- javascript_basics
- responsive_design
- web_frameworks
- ecommerce_platforms
- payment_systems
- seo
- web_security
- digital_marketing

### IT Basics (10 subtopics)
- hardware_basics
- software_fundamentals
- input_output_devices
- memory_storage
- number_systems
- computer_basics
- internet_basics
- file_management
- computer_history
- it_terminology

### Logic Formulation (10 subtopics)
- propositional_logic
- logical_operators
- truth_tables
- logical_equivalence
- implications
- quantifiers
- logical_laws
- arguments
- predicate_logic
- proof_techniques

### Computer Networks (10 subtopics)
- network_fundamentals
- osi_model
- tcp_ip
- network_devices
- ip_addressing
- routing
- wireless_networks
- network_security
- application_protocols
- network_troubleshooting

### Object Oriented Programming (10 subtopics)
- oop_basics
- encapsulation
- inheritance
- polymorphism
- abstraction
- constructors
- design_patterns
- solid_principles
- relationships
- advanced_oop

### Operating Systems (10 subtopics)
- os_fundamentals
- process_management
- cpu_scheduling
- memory_management
- file_systems
- deadlock
- synchronization
- io_systems
- security_protection
- os_types

### Software Engineering (10 subtopics)
- sdlc
- agile_methodologies
- requirements_engineering
- software_design
- testing
- version_control
- code_quality
- devops
- project_management
- maintenance

## Tips for Efficient Question Generation

1. **Batch by Domain**: Work on all subtopics within a topic together to maintain context
2. **Use Existing Resources**: Reference textbooks, documentation, and educational sites
3. **Maintain Consistency**: Follow the established quality and format patterns
4. **Test as You Go**: Run the script after adding each subtopic to verify
5. **Commit Frequently**: Commit after completing each subtopic or small batch

## Estimated Effort
- Per Question: ~2-5 minutes (including research, writing, and review)
- Per Subtopic (30 questions): ~1-2 hours
- Full Completion (100 subtopics): ~100-200 hours of focused work

This is a substantial undertaking best completed incrementally over time or by multiple contributors.
