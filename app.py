from flask import Flask, render_template, jsonify, request
import json
import os
import random

app = Flask(__name__)

# Get data directory path
def get_data_dir():
    return os.path.join(os.path.dirname(__file__), 'data')

# Load topic index
def load_topic_index(topic_id):
    """Load the index.json file for a topic"""
    data_dir = get_data_dir()
    index_path = os.path.join(data_dir, topic_id, 'index.json')
    
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# Load subtopic questions
def load_subtopic_questions(topic_id, subtopic_id):
    """Load questions from a subtopic file"""
    data_dir = get_data_dir()
    subtopic_path = os.path.join(data_dir, topic_id, f'{subtopic_id}.json')
    
    if os.path.exists(subtopic_path):
        with open(subtopic_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# Get all available topics
def get_all_topics():
    """Get list of all topics from directory structure"""
    data_dir = get_data_dir()
    topics = []
    
    # Check each subdirectory in data folder
    if os.path.exists(data_dir):
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            if os.path.isdir(item_path):
                index_data = load_topic_index(item)
                if index_data:
                    topics.append(index_data)
    
    return topics

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/topics', methods=['GET'])
def get_topics_api():
    """Get all available quiz topics with their subtopic counts"""
    topics = get_all_topics()
    
    response_topics = []
    for topic_data in topics:
        response_topics.append({
            'id': topic_data['topic_id'],
            'name': topic_data['topic_name'],
            'description': topic_data.get('description', ''),
            'subtopic_count': len(topic_data.get('subtopics', []))
        })
    
    return jsonify(response_topics)

@app.route('/api/topics/<topic_id>/subtopics', methods=['GET'])
def get_subtopics(topic_id):
    """Get all subtopics for a specific topic"""
    topic_data = load_topic_index(topic_id)
    
    if not topic_data:
        return jsonify({'error': 'Topic not found'}), 404
    
    return jsonify({
        'topic_id': topic_data['topic_id'],
        'topic_name': topic_data['topic_name'],
        'description': topic_data.get('description', ''),
        'subtopics': topic_data.get('subtopics', [])
    })

@app.route('/api/quiz/<topic_id>/<subtopic_id>', methods=['GET'])
def get_quiz(topic_id, subtopic_id):
    """Get quiz questions for a specific subtopic"""
    subtopic_data = load_subtopic_questions(topic_id, subtopic_id)
    
    if not subtopic_data:
        return jsonify({'error': 'Subtopic not found'}), 404
    
    questions = subtopic_data.get('questions', [])
    
    # Optionally limit number of questions
    limit = request.args.get('limit', type=int)
    if limit and limit < len(questions):
        questions = random.sample(questions, limit)
    
    return jsonify({
        'topic_id': topic_id,
        'subtopic_id': subtopic_id,
        'subtopic_name': subtopic_data.get('subtopic_name', ''),
        'questions': questions
    })

@app.route('/api/submit', methods=['POST'])
def submit_quiz():
    """Submit quiz answers and get results"""
    data = request.json
    topic_id = data.get('topic_id')
    subtopic_id = data.get('subtopic_id')
    answers = data.get('answers', {})
    
    # Load the subtopic questions
    subtopic_data = load_subtopic_questions(topic_id, subtopic_id)
    
    if not subtopic_data:
        return jsonify({'error': 'Subtopic not found'}), 404
    
    questions = subtopic_data.get('questions', [])
    
    # Calculate score
    correct = 0
    total = len(questions)
    results = []
    
    for i, question in enumerate(questions):
        question_id = str(i)
        user_answer = answers.get(question_id)
        correct_answer = question.get('correct')
        
        is_correct = user_answer == correct_answer
        if is_correct:
            correct += 1
        
        results.append({
            'question': question.get('question'),
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': question.get('explanation', '')
        })
    
    score_percentage = (correct / total * 100) if total > 0 else 0
    
    return jsonify({
        'correct': correct,
        'total': total,
        'percentage': round(score_percentage, 2),
        'results': results
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
