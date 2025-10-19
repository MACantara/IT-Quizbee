"""
Script to add a new subtopic with placeholder questions to an existing topic
Creates elimination and finals (easy, average, difficult) question files
"""

import json
import os
from pathlib import Path

# Base directory
DATA_DIR = Path(__file__).parent / "data"

# Available topics
TOPICS = {
    "1": {"id": "computer_architecture", "name": "Computer Architecture & IT Security"},
    "2": {"id": "data_science", "name": "Data Science & Analytics"},
    "3": {"id": "dbms", "name": "Database Management System"},
    "4": {"id": "ecommerce_web", "name": "E-commerce & Web Design"},
    "5": {"id": "it_basics", "name": "Basic Computer Concepts & IT"},
    "6": {"id": "logic", "name": "Logic Formulation"},
    "7": {"id": "networks", "name": "Computer Networks & Telecommunication"},
    "8": {"id": "oop", "name": "Object Oriented Programming"},
    "9": {"id": "operating_systems", "name": "Operating Systems"},
    "10": {"id": "software_engineering", "name": "Software Engineering"}
}


def read_json(file_path):
    """Read JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(file_path, data):
    """Write JSON file with proper formatting"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_abbreviation(text):
    """Convert topic/subtopic name to 3-4 character abbreviation"""
    words = text.lower().split()
    if len(words) == 1:
        # Single word: take first 4 characters
        return text[:4].lower()
    else:
        # Multiple words: take first character of each word, up to 4 chars
        abbr = ''.join(word[0] for word in words)[:4]
        return abbr


def generate_question_id(topic_id, subtopic_id, mode, difficulty=None, index=0):
    """Generate unique question ID"""
    topic_abbr = get_abbreviation(topic_id)
    subtopic_abbr = get_abbreviation(subtopic_id)
    
    if mode == "elimination":
        return f"{topic_abbr}_{subtopic_abbr}_elim_{index:03d}"
    else:  # finals mode
        difficulty_char = difficulty[0].lower() if difficulty else "e"
        return f"{topic_abbr}_{subtopic_abbr}_{difficulty_char}_finals_{index:03d}"


def create_placeholder_questions(subtopic_id, subtopic_name, mode, difficulty=None):
    """Create placeholder questions for a given mode and difficulty"""
    data = {
        "subtopic_id": subtopic_id,
        "subtopic_name": subtopic_name,
        "mode": mode
    }
    
    # Add difficulty field for finals mode
    if difficulty:
        data["difficulty"] = difficulty
        question_prefix = f"{subtopic_name} - {mode.capitalize()} ({difficulty.capitalize()}) Question"
    else:
        question_prefix = f"{subtopic_name} - {mode.capitalize()} Question"
    
    # Create questions based on mode
    if mode == "elimination":
        # Multiple choice for elimination mode
        data["questions"] = [
            {
                "question": f"{question_prefix} {i}: [Placeholder question about {subtopic_name}]",
                "options": [
                    f"[Option A for question {i}]",
                    f"[Option B for question {i}]",
                    f"[Option C for question {i}]",
                    f"[Option D for question {i}]"
                ],
                "correct": i % 4,
                "explanation": f"[Explanation for {mode} question {i}. Replace with actual explanation.]",
                "id": generate_question_id(subtopic_id, subtopic_id, mode, None, i)
            }
            for i in range(1, 11)
        ]
    else:
        # Identification (type-in) for finals mode
        data["questions"] = [
            {
                "question": f"{question_prefix} {i}: [Placeholder identification question about {subtopic_name}]",
                "answer": f"[Correct answer for question {i}]",
                "alternatives": [],  # Add alternative acceptable answers here
                "explanation": f"[Explanation for {mode} - {difficulty} question {i}. Replace with actual explanation.]",
                "id": generate_question_id(subtopic_id, subtopic_id, mode, difficulty, i)
            }
            for i in range(1, 11)
        ]
    
    return data


def display_topics():
    """Display available topics"""
    print("\n" + "="*70)
    print("AVAILABLE TOPICS")
    print("="*70)
    for key, topic in sorted(TOPICS.items()):
        print(f"  {key}. {topic['name']} ({topic['id']})")
    print("="*70)


def get_topic_choice():
    """Get user's topic choice"""
    while True:
        choice = input("\nEnter topic number (1-10) or 'q' to quit: ").strip()
        
        if choice.lower() == 'q':
            return None
        
        if choice in TOPICS:
            return TOPICS[choice]
        
        print("❌ Invalid choice. Please enter a number between 1 and 10.")


def get_subtopic_info():
    """Get subtopic information from user"""
    print("\n" + "="*70)
    print("SUBTOPIC INFORMATION")
    print("="*70)
    
    # Get subtopic ID
    while True:
        subtopic_id = input("\nEnter subtopic ID (e.g., 'new_concept'): ").strip().lower()
        if subtopic_id:
            # Replace spaces with underscores
            subtopic_id = subtopic_id.replace(" ", "_")
            break
        print("❌ Subtopic ID cannot be empty.")
    
    # Get subtopic name
    while True:
        subtopic_name = input("Enter subtopic name (e.g., 'New Concept'): ").strip()
        if subtopic_name:
            break
        print("❌ Subtopic name cannot be empty.")
    
    # Get subtopic description
    subtopic_desc = input("Enter subtopic description (optional): ").strip()
    if not subtopic_desc:
        subtopic_desc = f"Questions about {subtopic_name}"
    
    return {
        "id": subtopic_id,
        "name": subtopic_name,
        "description": subtopic_desc
    }


def create_subtopic_files(topic_path, subtopic_info):
    """Create all question files for the new subtopic"""
    subtopic_id = subtopic_info["id"]
    subtopic_name = subtopic_info["name"]
    
    # Create subtopic directory
    subtopic_dir = topic_path / subtopic_id
    subtopic_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Created directory: {subtopic_dir.relative_to(DATA_DIR)}")
    
    # Create elimination folder and file
    elimination_dir = subtopic_dir / "elimination"
    elimination_dir.mkdir(exist_ok=True)
    
    elimination_data = create_placeholder_questions(subtopic_id, subtopic_name, "elimination")
    elimination_file = elimination_dir / f"{subtopic_id}.json"
    write_json(elimination_file, elimination_data)
    
    print(f"  ✅ Created: elimination/{subtopic_id}.json (10 questions)")
    
    # Create finals folder structure with difficulty levels
    finals_dir = subtopic_dir / "finals"
    finals_dir.mkdir(exist_ok=True)
    
    difficulties = ["easy", "average", "difficult"]
    for difficulty in difficulties:
        difficulty_dir = finals_dir / difficulty
        difficulty_dir.mkdir(exist_ok=True)
        
        finals_data = create_placeholder_questions(subtopic_id, subtopic_name, "finals", difficulty)
        finals_file = difficulty_dir / f"{subtopic_id}.json"
        write_json(finals_file, finals_data)
        
        print(f"  ✅ Created: finals/{difficulty}/{subtopic_id}.json (10 questions)")
    
    print(f"\n✨ Total files created: 4 (1 elimination + 3 finals)")
    print(f"✨ Total questions created: 40 (10 elimination + 30 finals)")


def update_index_file(topic_path, subtopic_info):
    """Update the topic's index.json file"""
    index_path = topic_path / "index.json"
    
    if not index_path.exists():
        print(f"⚠️  Warning: index.json not found in {topic_path.name}")
        return False
    
    try:
        index_data = read_json(index_path)
        
        # Check if subtopic already exists
        existing_ids = [s["id"] for s in index_data.get("subtopics", [])]
        if subtopic_info["id"] in existing_ids:
            print(f"\n⚠️  Subtopic '{subtopic_info['id']}' already exists in index.json!")
            overwrite = input("Do you want to overwrite it? (yes/no): ").strip().lower()
            if overwrite != "yes":
                print("❌ Subtopic not added to index.json")
                return False
            
            # Remove existing subtopic
            index_data["subtopics"] = [s for s in index_data["subtopics"] if s["id"] != subtopic_info["id"]]
        
        # Add new subtopic to index
        new_subtopic_entry = {
            "id": subtopic_info["id"],
            "name": subtopic_info["name"],
            "description": subtopic_info["description"]
        }
        
        index_data["subtopics"].append(new_subtopic_entry)
        
        # Write updated index
        write_json(index_path, index_data)
        
        print(f"\n✅ Updated index.json - added '{subtopic_info['name']}'")
        print(f"   Total subtopics in {index_data['topic_name']}: {len(index_data['subtopics'])}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error updating index.json: {e}")
        return False


def main():
    """Main execution function"""
    print("="*70)
    print("IT-QUIZBEE: ADD NEW SUBTOPIC")
    print("="*70)
    print("\nThis script will create a new subtopic with placeholder questions:")
    print("  • 1 elimination file (10 questions)")
    print("  • 3 finals files - easy, average, difficult (30 questions total)")
    print("  • Update the topic's index.json file")
    print()
    
    if not DATA_DIR.exists():
        print("❌ Data directory not found!")
        return
    
    # Display and select topic
    display_topics()
    topic = get_topic_choice()
    
    if topic is None:
        print("\n👋 Goodbye!")
        return
    
    topic_path = DATA_DIR / topic["id"]
    
    if not topic_path.exists():
        print(f"\n❌ Topic directory not found: {topic['id']}")
        return
    
    print(f"\n✅ Selected topic: {topic['name']}")
    
    # Get subtopic information
    subtopic_info = get_subtopic_info()
    
    # Show summary and confirm
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Topic: {topic['name']}")
    print(f"Subtopic ID: {subtopic_info['id']}")
    print(f"Subtopic Name: {subtopic_info['name']}")
    print(f"Description: {subtopic_info['description']}")
    print()
    print("Files to be created:")
    print(f"  • {topic['id']}/{subtopic_info['id']}/elimination/{subtopic_info['id']}.json")
    print(f"  • {topic['id']}/{subtopic_info['id']}/finals/easy/{subtopic_info['id']}.json")
    print(f"  • {topic['id']}/{subtopic_info['id']}/finals/average/{subtopic_info['id']}.json")
    print(f"  • {topic['id']}/{subtopic_info['id']}/finals/difficult/{subtopic_info['id']}.json")
    print("="*70)
    
    confirm = input("\nProceed with creation? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("\n❌ Operation cancelled.")
        return
    
    # Create the files
    print("\n🚀 Creating subtopic files...")
    create_subtopic_files(topic_path, subtopic_info)
    
    # Update index.json
    print("\n📝 Updating index.json...")
    update_index_file(topic_path, subtopic_info)
    
    # Final message
    print("\n" + "="*70)
    print("✅ SUBTOPIC SUCCESSFULLY CREATED!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Replace placeholder questions with actual content")
    print("  2. Verify correct answer indices")
    print("  3. Add meaningful explanations")
    print("  4. Run 'python update_topics_md.py' to update documentation")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
