#!/usr/bin/env python3
"""
Script to add unique question IDs to all questions in the data directory.

This script:
1. Finds all JSON question files in the data directory
2. Generates unique question IDs for each question
3. Adds the ID field to each question
4. Preserves all existing data
5. Provides detailed progress reporting

Question ID format:
- Elimination mode: {topic}_{subtopic}_elim_{index} (e.g., arch_auth_elim_001)
- Finals mode: {topic}_{subtopic}_{difficulty}_finals_{index} (e.g., arch_auth_easy_finals_001)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
import hashlib


def get_abbreviation(text: str) -> str:
    """Convert text to abbreviation (e.g., 'computer_architecture' -> 'comp_arch')"""
    words = text.replace('_', ' ').split()
    if len(words) == 1:
        return text[:4].lower()
    return '_'.join(word[:3].lower() for word in words)


def generate_question_id(
    topic_id: str,
    subtopic_id: str,
    mode: str,
    difficulty: str = None,
    index: int = 0
) -> str:
    """
    Generate a unique question ID.
    
    Args:
        topic_id: Topic identifier (e.g., 'computer_architecture')
        subtopic_id: Subtopic identifier (e.g., 'authentication')
        mode: Quiz mode ('elimination' or 'finals')
        difficulty: Difficulty level for finals mode ('easy', 'average', 'difficult')
        index: Question index (0-based)
    
    Returns:
        Unique question ID string
    """
    topic_abbr = get_abbreviation(topic_id)
    subtopic_abbr = get_abbreviation(subtopic_id)
    
    if mode == 'elimination':
        return f"{topic_abbr}_{subtopic_abbr}_elim_{index:03d}"
    elif mode == 'finals':
        diff_abbr = difficulty[0].lower() if difficulty else 'e'
        return f"{topic_abbr}_{subtopic_abbr}_{diff_abbr}_finals_{index:03d}"
    else:
        return f"{topic_abbr}_{subtopic_abbr}_unk_{index:03d}"


def process_question_file(file_path: Path) -> Tuple[bool, str, int]:
    """
    Process a single question file and add IDs to questions.
    
    Args:
        file_path: Path to the JSON file
    
    Returns:
        Tuple of (success: bool, message: str, questions_updated: int)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'questions' not in data:
            return False, f"No 'questions' key found", 0
        
        # Extract metadata
        topic_id = file_path.parent.parent.parent.name
        subtopic_id = data.get('subtopic_id', file_path.parent.parent.name)
        mode = data.get('mode', 'unknown')
        difficulty = data.get('difficulty', None)
        
        # Add IDs to questions
        questions_updated = 0
        for index, question in enumerate(data['questions']):
            # Skip if ID already exists
            if 'id' in question:
                continue
            
            question_id = generate_question_id(
                topic_id,
                subtopic_id,
                mode,
                difficulty,
                index
            )
            question['id'] = question_id
            questions_updated += 1
        
        # Write back if any questions were updated
        if questions_updated > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True, f"✓ Updated {questions_updated} questions", questions_updated
    
    except json.JSONDecodeError as e:
        return False, f"✗ JSON decode error: {str(e)}", 0
    except Exception as e:
        return False, f"✗ Error: {str(e)}", 0


def main():
    """Main function to process all question files."""
    data_dir = Path(__file__).parent / 'data'
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    print("=" * 70)
    print("Adding Question IDs to All Questions")
    print("=" * 70)
    
    # Find all JSON files in elimination and finals directories
    json_files = []
    
    # Find elimination files
    for elim_file in data_dir.glob('*/*/elimination/*.json'):
        json_files.append(elim_file)
    
    # Find finals files
    for finals_file in data_dir.glob('*/*/finals/*/*.json'):
        json_files.append(finals_file)
    
    if not json_files:
        print("❌ No question files found!")
        return
    
    print(f"\nFound {len(json_files)} question files to process\n")
    
    # Process files
    total_questions_updated = 0
    successful_files = 0
    failed_files = 0
    
    for file_path in sorted(json_files):
        # Build relative path for display
        rel_path = file_path.relative_to(data_dir)
        
        success, message, questions_updated = process_question_file(file_path)
        
        if success:
            successful_files += 1
            total_questions_updated += questions_updated
            print(f"  {rel_path}")
            print(f"    {message}\n")
        else:
            failed_files += 1
            print(f"  {rel_path}")
            print(f"    {message}\n")
    
    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✓ Successful files: {successful_files}")
    print(f"✗ Failed files: {failed_files}")
    print(f"📊 Total questions updated: {total_questions_updated}")
    print("=" * 70)
    
    if failed_files == 0:
        print("\n✅ All files processed successfully!")
    else:
        print(f"\n⚠️  {failed_files} file(s) had errors. Please review above.")


if __name__ == '__main__':
    main()
