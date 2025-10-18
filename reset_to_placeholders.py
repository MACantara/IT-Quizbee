"""
Script to reset JSON question files back to placeholder questions
Supports both elimination mode (multiple choice) and finals mode (identification)
"""

import json
import os
from pathlib import Path
import argparse


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
    print(f"  ✅ Reset: {file_path.relative_to(DATA_DIR)}")


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
                "explanation": f"[Explanation for {mode} question {i}. Replace with actual explanation.]"
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
                "explanation": f"[Explanation for {mode} - {difficulty} question {i}. Replace with actual explanation.]"
            }
            for i in range(1, 11)
        ]
    
    return data


def reset_file(file_path):
    """Reset a single JSON file to placeholder questions"""
    try:
        # Read existing file to get metadata
        data = read_json(file_path)
        
        subtopic_id = data.get("subtopic_id")
        subtopic_name = data.get("subtopic_name")
        mode = data.get("mode")
        difficulty = data.get("difficulty")
        
        if not all([subtopic_id, subtopic_name, mode]):
            print(f"  ⚠️  Skipping {file_path.name}: Missing required metadata")
            return False
        
        # Create placeholder data
        placeholder_data = create_placeholder_questions(subtopic_id, subtopic_name, mode, difficulty)
        
        # Write back to file
        write_json(file_path, placeholder_data)
        return True
        
    except Exception as e:
        print(f"  ❌ Error resetting {file_path.name}: {str(e)}")
        return False


def reset_subtopic(topic_path, subtopic_id):
    """Reset all question files for a specific subtopic"""
    subtopic_dir = topic_path / subtopic_id
    
    if not subtopic_dir.exists():
        print(f"  ⚠️  Subtopic directory not found: {subtopic_id}")
        return 0
    
    reset_count = 0
    
    # Reset elimination file
    elimination_file = subtopic_dir / "elimination" / f"{subtopic_id}.json"
    if elimination_file.exists():
        if reset_file(elimination_file):
            reset_count += 1
    
    # Reset finals files (all difficulty levels)
    for difficulty in ["easy", "average", "difficult"]:
        finals_file = subtopic_dir / "finals" / difficulty / f"{subtopic_id}.json"
        if finals_file.exists():
            if reset_file(finals_file):
                reset_count += 1
    
    return reset_count


def reset_topic(topic_id):
    """Reset all subtopics in a topic"""
    topic_path = DATA_DIR / topic_id
    
    if not topic_path.exists():
        print(f"❌ Topic directory not found: {topic_id}")
        return 0
    
    # Read index.json to get subtopics
    index_file = topic_path / "index.json"
    if not index_file.exists():
        print(f"❌ index.json not found for topic: {topic_id}")
        return 0
    
    index_data = read_json(index_file)
    subtopics = index_data.get("subtopics", [])
    
    if not subtopics:
        print(f"⚠️  No subtopics found in index.json for: {topic_id}")
        return 0
    
    total_reset = 0
    print(f"\n📁 Processing topic: {index_data.get('topic_name', topic_id)}")
    print(f"   Subtopics to reset: {len(subtopics)}\n")
    
    for subtopic in subtopics:
        subtopic_id = subtopic.get("id")
        if subtopic_id:
            print(f"  🔄 Resetting subtopic: {subtopic.get('name', subtopic_id)}")
            count = reset_subtopic(topic_path, subtopic_id)
            total_reset += count
            if count > 0:
                print(f"     ✨ Reset {count} file(s)\n")
    
    return total_reset


def reset_all_topics():
    """Reset all topics in the data directory"""
    total_reset = 0
    
    for topic_id in [t["id"] for t in TOPICS.values()]:
        count = reset_topic(topic_id)
        total_reset += count
    
    return total_reset


def display_topics():
    """Display available topics"""
    print("\nAvailable Topics:")
    print("-" * 70)
    for key, topic in sorted(TOPICS.items()):
        print(f"  {key}. {topic['name']} ({topic['id']})")
    print(f"  11. All topics")
    print("-" * 70)


def get_user_choice():
    """Get user's choice for what to reset"""
    display_topics()
    
    choice = input("\nSelect topic to reset (1-11, or 'q' to quit): ").strip()
    
    if choice.lower() == 'q':
        return None
    
    if choice == "11":
        return "all"
    
    if choice in TOPICS:
        return TOPICS[choice]["id"]
    
    print("❌ Invalid choice. Please try again.")
    return get_user_choice()


def main():
    """Main execution function"""
    print("=" * 70)
    print("IT-QUIZBEE: RESET QUESTIONS TO PLACEHOLDERS")
    print("=" * 70)
    print("\n⚠️  WARNING: This will replace actual questions with placeholders!")
    print("   Make sure you have a backup before proceeding.\n")
    
    if not DATA_DIR.exists():
        print("❌ Data directory not found!")
        return
    
    # Get user choice
    choice = get_user_choice()
    
    if choice is None:
        print("\n👋 Operation cancelled.")
        return
    
    # Confirm action
    if choice == "all":
        confirm_msg = "ALL TOPICS"
    else:
        topic_name = next((t["name"] for t in TOPICS.values() if t["id"] == choice), choice)
        confirm_msg = topic_name
    
    print(f"\n{'=' * 70}")
    print(f"You are about to reset: {confirm_msg}")
    print(f"{'=' * 70}")
    confirm = input("\nType 'RESET' to confirm (or anything else to cancel): ").strip()
    
    if confirm != "RESET":
        print("\n❌ Operation cancelled.")
        return
    
    # Perform reset
    print("\n🚀 Starting reset process...\n")
    
    if choice == "all":
        total_reset = reset_all_topics()
    else:
        total_reset = reset_topic(choice)
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ RESET COMPLETE!")
    print("=" * 70)
    print(f"Total files reset: {total_reset}")
    print("\nNext steps:")
    print("  1. Replace placeholder questions with actual content")
    print("  2. Verify correct answer indices (elimination mode)")
    print("  3. Add meaningful explanations")
    print("  4. Test the questions in the application")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
