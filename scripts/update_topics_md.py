"""
Script to automatically update TOPICS.md based on current data structure
Scans all topic folders and subtopics to generate comprehensive documentation
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Base directory - go up one level from scripts folder
DATA_DIR = Path(__file__).parent.parent / "data"
TOPICS_FILE = Path(__file__).parent.parent / "docs/TOPICS.md"

import json
from pathlib import Path
from datetime import datetime

# Base directory
DATA_DIR = Path(__file__).parent / "data"
TOPICS_FILE = Path(__file__).parent / "docs/TOPICS.md"

# Topic display names mapping
TOPIC_NAMES = {
    "computer_architecture": "Computer Architecture & IT Security",
    "data_science": "Data Science & Analytics",
    "dbms": "Database Management System",
    "ecommerce_web": "E-commerce & Web Design",
    "it_basics": "Basic Computer Concepts & IT",
    "logic": "Logic Formulation",
    "networks": "Computer Networks & Telecommunication",
    "oop": "Object Oriented Programming",
    "operating_systems": "Operating Systems",
    "software_engineering": "Software Engineering"
}

# Topic descriptions
TOPIC_DESCRIPTIONS = {
    "computer_architecture": "Computer organization, architecture concepts, and security fundamentals",
    "data_science": "Data analysis, machine learning, and statistical methods",
    "dbms": "Database design, SQL, and database management concepts",
    "ecommerce_web": "Web development, e-commerce platforms, and online business",
    "it_basics": "Fundamental concepts about computer systems and general information technology",
    "logic": "Logical reasoning, propositions, and mathematical logic",
    "networks": "Network protocols, architectures, and telecommunication systems",
    "oop": "OOP concepts, principles, and design patterns",
    "operating_systems": "OS concepts, processes, memory management, and scheduling",
    "software_engineering": "Software development processes, methodologies, and best practices"
}


def read_json(file_path):
    """Read JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def count_questions_in_file(file_path):
    """Count questions in a JSON file"""
    try:
        data = read_json(file_path)
        return len(data.get("questions", []))
    except:
        return 0


def scan_topic(topic_path):
    """Scan a topic folder and gather subtopic information"""
    index_path = topic_path / "index.json"
    
    if not index_path.exists():
        return None
    
    index_data = read_json(index_path)
    topic_id = index_data.get("topic_id")
    topic_name = index_data.get("topic_name")
    subtopics = index_data.get("subtopics", [])
    
    # Gather subtopic details
    subtopic_details = []
    for subtopic in subtopics:
        subtopic_id = subtopic["id"]
        subtopic_name = subtopic["name"]
        
        # Count questions in different modes
        subtopic_dir = topic_path / subtopic_id
        
        elimination_count = 0
        finals_easy_count = 0
        finals_average_count = 0
        finals_difficult_count = 0
        
        # Check elimination questions
        elim_file = subtopic_dir / "elimination" / f"{subtopic_id}.json"
        if elim_file.exists():
            elimination_count = count_questions_in_file(elim_file)
        
        # Check finals questions (all difficulty levels)
        finals_easy_file = subtopic_dir / "finals" / "easy" / f"{subtopic_id}.json"
        finals_avg_file = subtopic_dir / "finals" / "average" / f"{subtopic_id}.json"
        finals_diff_file = subtopic_dir / "finals" / "difficult" / f"{subtopic_id}.json"
        
        if finals_easy_file.exists():
            finals_easy_count = count_questions_in_file(finals_easy_file)
        if finals_avg_file.exists():
            finals_average_count = count_questions_in_file(finals_avg_file)
        if finals_diff_file.exists():
            finals_difficult_count = count_questions_in_file(finals_diff_file)
        
        total_finals = finals_easy_count + finals_average_count + finals_difficult_count
        total_questions = elimination_count + total_finals
        
        subtopic_details.append({
            "id": subtopic_id,
            "name": subtopic_name,
            "description": subtopic.get("description", ""),
            "elimination": elimination_count,
            "finals_easy": finals_easy_count,
            "finals_average": finals_average_count,
            "finals_difficult": finals_difficult_count,
            "total_finals": total_finals,
            "total": total_questions
        })
    
    return {
        "id": topic_id,
        "name": topic_name,
        "subtopics": subtopic_details
    }


def generate_topics_md():
    """Generate the complete TOPICS.md content"""
    print("Scanning data directory...")
    
    if not DATA_DIR.exists():
        print("❌ Data directory not found!")
        return None
    
    # Scan all topics
    all_topics = []
    total_subtopics = 0
    total_elimination_questions = 0
    total_finals_questions = 0
    
    for topic_dir in sorted(DATA_DIR.iterdir()):
        if topic_dir.is_dir():
            topic_data = scan_topic(topic_dir)
            if topic_data:
                all_topics.append(topic_data)
                total_subtopics += len(topic_data["subtopics"])
                
                for subtopic in topic_data["subtopics"]:
                    total_elimination_questions += subtopic["elimination"]
                    total_finals_questions += subtopic["total_finals"]
    
    # Generate markdown content
    md_content = []
    md_content.append("# IT Quizbee - Complete Topic and Subtopic List\n")
    md_content.append("## Overview")
    md_content.append(f"IT Quizbee contains **{len(all_topics)} main topics** with a total of **{total_subtopics} subtopics**.")
    md_content.append(f"The quiz system supports **two game modes**: Elimination and Finals.\n")
    md_content.append("### Game Modes")
    md_content.append("- **Elimination Mode**: Competitive preliminary rounds")
    md_content.append("- **Finals Mode**: Championship rounds with three difficulty levels (Easy, Average, Difficult)\n")
    md_content.append("---\n")
    
    # Generate each topic section
    for idx, topic in enumerate(all_topics, 1):
        topic_id = topic["id"]
        topic_name = TOPIC_NAMES.get(topic_id, topic["name"])
        topic_desc = TOPIC_DESCRIPTIONS.get(topic_id, "")
        
        md_content.append(f"## {idx}. {topic_name} ({topic_id})")
        if topic_desc:
            md_content.append(f"{topic_desc}\n")
        
        md_content.append("### Subtopics:")
        
        for sub_idx, subtopic in enumerate(topic["subtopics"], 1):
            name = subtopic["name"]
            desc = subtopic["description"]
            elim = subtopic["elimination"]
            finals_total = subtopic["total_finals"]
            total = subtopic["total"]
            
            # Build question count info
            question_info = []
            if elim > 0:
                question_info.append(f"{elim} elimination")
            if finals_total > 0:
                finals_breakdown = []
                if subtopic["finals_easy"] > 0:
                    finals_breakdown.append(f"{subtopic['finals_easy']} easy")
                if subtopic["finals_average"] > 0:
                    finals_breakdown.append(f"{subtopic['finals_average']} average")
                if subtopic["finals_difficult"] > 0:
                    finals_breakdown.append(f"{subtopic['finals_difficult']} difficult")
                
                finals_str = f"{finals_total} finals ({', '.join(finals_breakdown)})"
                question_info.append(finals_str)
            
            question_count_str = f" [{', '.join(question_info)}]" if question_info else ""
            
            md_content.append(f"{sub_idx}. **{name}**{question_count_str} - {desc}")
        
        md_content.append("\n---\n")
    
    # Statistics section
    md_content.append("## Statistics\n")
    md_content.append(f"- **Total Topics**: {len(all_topics)}")
    md_content.append(f"- **Total Subtopics**: {total_subtopics}")
    md_content.append(f"- **Total Elimination Questions**: {total_elimination_questions}")
    md_content.append(f"- **Total Finals Questions**: {total_finals_questions}")
    md_content.append(f"  - Easy: {sum(s['finals_easy'] for t in all_topics for s in t['subtopics'])}")
    md_content.append(f"  - Average: {sum(s['finals_average'] for t in all_topics for s in t['subtopics'])}")
    md_content.append(f"  - Difficult: {sum(s['finals_difficult'] for t in all_topics for s in t['subtopics'])}")
    md_content.append(f"- **Grand Total Questions**: {total_elimination_questions + total_finals_questions}\n")
    
    # File organization section
    md_content.append("---\n")
    md_content.append("## File Organization\n")
    md_content.append("```")
    md_content.append("data/")
    md_content.append("├── [topic_id]/")
    md_content.append("│   ├── index.json                      (Topic metadata)")
    md_content.append("│   ├── [subtopic_id]/")
    md_content.append("│   │   ├── elimination/")
    md_content.append("│   │   │   └── [subtopic_id].json     (Elimination mode questions)")
    md_content.append("│   │   └── finals/")
    md_content.append("│   │       ├── easy/")
    md_content.append("│   │       │   └── [subtopic_id].json (Finals easy questions)")
    md_content.append("│   │       ├── average/")
    md_content.append("│   │       │   └── [subtopic_id].json (Finals average questions)")
    md_content.append("│   │       └── difficult/")
    md_content.append("│   │           └── [subtopic_id].json (Finals difficult questions)")
    md_content.append("```\n")
    
    # Notes section
    md_content.append("## Notes\n")
    md_content.append("### Question Structure")
    md_content.append("Each question JSON file contains:")
    md_content.append("- `subtopic_id`: Unique identifier for the subtopic")
    md_content.append("- `subtopic_name`: Display name of the subtopic")
    md_content.append("- `mode`: Game mode (\"elimination\" or \"finals\")")
    md_content.append("- `difficulty`: Difficulty level (only for finals: \"easy\", \"average\", or \"difficult\")")
    md_content.append("- `questions`: Array of question objects\n")
    md_content.append("### Question Object")
    md_content.append("Each question contains:")
    md_content.append("- `question`: The question text")
    md_content.append("- `options`: Array of 4 answer options")
    md_content.append("- `correct`: Index of the correct answer (0-3)")
    md_content.append("- `explanation`: Explanation of the correct answer\n")
    
    # Footer
    md_content.append("---\n")
    md_content.append(f"*Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*")
    md_content.append(f"\n*Generated automatically by `update_topics_md.py`*\n")
    
    return "\n".join(md_content)


def main():
    """Main execution function"""
    print("="*60)
    print("IT-QUIZBEE TOPICS.MD UPDATE SCRIPT")
    print("="*60)
    print()
    
    # Generate new content
    new_content = generate_topics_md()
    
    if new_content is None:
        print("\n❌ Failed to generate TOPICS.md content")
        return
    
    # Write to file
    try:
        with open(TOPICS_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("\n✅ TOPICS.md has been successfully updated!")
        print(f"   Location: {TOPICS_FILE}")
        print("\nSummary:")
        
        # Count lines for summary
        lines = new_content.split('\n')
        print(f"   - Total lines: {len(lines)}")
        print(f"   - File size: {len(new_content)} characters")
        
    except Exception as e:
        print(f"\n❌ Error writing TOPICS.md: {e}")


if __name__ == "__main__":
    main()
