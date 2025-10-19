from flask import Flask, render_template, jsonify, request, session
import json
import os
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

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
def load_subtopic_questions(topic_id, subtopic_id, mode='elimination', difficulty=None):
    """Load questions from a subtopic file based on mode and difficulty"""
    data_dir = get_data_dir()
    
    # Build path based on mode and difficulty
    if mode == 'elimination':
        subtopic_path = os.path.join(data_dir, topic_id, subtopic_id, 'elimination', f'{subtopic_id}.json')
    elif mode == 'finals':
        if not difficulty:
            difficulty = 'easy'  # Default to easy if not specified
        subtopic_path = os.path.join(data_dir, topic_id, subtopic_id, 'finals', difficulty, f'{subtopic_id}.json')
    else:
        return None
    
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
    """Index page with mode selection"""
    return render_template('index.html')

@app.route('/elimination')
def elimination_mode():
    """Elimination mode - 100 random questions from all topics, 60 minutes"""
    all_topics = get_all_topics()
    all_questions = []
    
    # Collect all elimination questions from all topics
    for topic_data in all_topics:
        topic_id = topic_data['topic_id']
        for subtopic in topic_data.get('subtopics', []):
            subtopic_id = subtopic['id']
            questions_data = load_subtopic_questions(topic_id, subtopic_id, 'elimination')
            if questions_data:
                questions = questions_data.get('questions', [])
                # Add topic and subtopic info to each question
                for q in questions:
                    q['topic_id'] = topic_id
                    q['topic_name'] = topic_data['topic_name']
                    q['subtopic_id'] = subtopic_id
                    q['subtopic_name'] = subtopic['name']
                all_questions.extend(questions)
    
    # Randomly select 100 questions
    if len(all_questions) > 100:
        selected_questions = random.sample(all_questions, 100)
    else:
        selected_questions = all_questions
    
    # Shuffle the questions
    random.shuffle(selected_questions)
    
    # Store questions in session for grading
    session['elimination_questions'] = selected_questions
    
    return render_template('elimination_mode.html', questions=selected_questions)

@app.route('/finals')
def finals_mode():
    """Finals mode - 10 easy, 10 average, 10 difficult identification questions with timers"""
    all_topics = get_all_topics()
    
    # Collect identification questions by difficulty
    easy_questions = []
    average_questions = []
    difficult_questions = []
    
    for topic_data in all_topics:
        topic_id = topic_data['topic_id']
        for subtopic in topic_data.get('subtopics', []):
            subtopic_id = subtopic['id']
            
            # Load easy questions
            easy_data = load_subtopic_questions(topic_id, subtopic_id, 'finals', 'easy')
            if easy_data:
                for q in easy_data.get('questions', []):
                    q['difficulty'] = 'easy'
                    q['topic_name'] = topic_data['topic_name']
                    q['subtopic_name'] = subtopic['name']
                easy_questions.extend(easy_data.get('questions', []))
            
            # Load average questions
            average_data = load_subtopic_questions(topic_id, subtopic_id, 'finals', 'average')
            if average_data:
                for q in average_data.get('questions', []):
                    q['difficulty'] = 'average'
                    q['topic_name'] = topic_data['topic_name']
                    q['subtopic_name'] = subtopic['name']
                average_questions.extend(average_data.get('questions', []))
            
            # Load difficult questions
            difficult_data = load_subtopic_questions(topic_id, subtopic_id, 'finals', 'difficult')
            if difficult_data:
                for q in difficult_data.get('questions', []):
                    q['difficulty'] = 'difficult'
                    q['topic_name'] = topic_data['topic_name']
                    q['subtopic_name'] = subtopic['name']
                difficult_questions.extend(difficult_data.get('questions', []))
    
    # Select 10 from each difficulty
    selected_easy = random.sample(easy_questions, min(10, len(easy_questions)))
    selected_average = random.sample(average_questions, min(10, len(average_questions)))
    selected_difficult = random.sample(difficult_questions, min(10, len(difficult_questions)))
    
    # Combine all questions
    all_selected = selected_easy + selected_average + selected_difficult
    
    # Store questions in session for grading
    session['finals_questions'] = all_selected
    
    # Convert to JSON for JavaScript
    questions_json = json.dumps(all_selected)
    
    return render_template('finals_mode.html', questions_json=questions_json)

@app.route('/topics')
def topics():
    """Display all available topics"""
    topics_list = get_all_topics()
    
    response_topics = []
    for topic_data in topics_list:
        response_topics.append({
            'topic_id': topic_data['topic_id'],
            'topic_name': topic_data['topic_name'],
            'description': topic_data.get('description', ''),
            'subtopic_count': len(topic_data.get('subtopics', []))
        })
    
    return render_template('topics.html', topics=response_topics)

@app.route('/topics/<topic_id>/subtopics')
def subtopics(topic_id):
    """Display subtopics for a specific topic"""
    topic_data = load_topic_index(topic_id)
    
    if not topic_data:
        return "Topic not found", 404
    
    return render_template('subtopics.html', 
                         topic=topic_data,
                         subtopics=topic_data.get('subtopics', []))

@app.route('/topics/<topic_id>/subtopics/<subtopic_id>/mode')
def mode_selection(topic_id, subtopic_id):
    """Display mode selection for a subtopic"""
    topic_data = load_topic_index(topic_id)
    
    if not topic_data:
        return "Topic not found", 404
    
    # Find subtopic name
    subtopic_name = subtopic_id
    for subtopic in topic_data.get('subtopics', []):
        if subtopic['id'] == subtopic_id:
            subtopic_name = subtopic['name']
            break
    
    return render_template('mode_selection.html',
                         topic_id=topic_id,
                         subtopic_id=subtopic_id,
                         subtopic_name=subtopic_name)

@app.route('/quiz/<topic_id>/<subtopic_id>')
def quiz(topic_id, subtopic_id):
    """Display quiz questions"""
    mode = request.args.get('mode', 'elimination')
    difficulty = request.args.get('difficulty', 'easy')
    
    # Load questions based on mode and difficulty
    subtopic_data = load_subtopic_questions(topic_id, subtopic_id, mode, difficulty)
    
    if not subtopic_data:
        return "Quiz not found", 404
    
    return render_template('quiz.html',
                         quiz_data={
                             'topic_id': topic_id,
                             'subtopic_id': subtopic_id,
                             'subtopic_name': subtopic_data.get('subtopic_name', ''),
                             'mode': mode,
                             'difficulty': difficulty if mode == 'finals' else None,
                             'questions': subtopic_data.get('questions', [])
                         })

@app.route('/elimination/submit', methods=['POST'])
def submit_elimination():
    """Submit elimination mode answers and display results"""
    # Get questions from session
    questions = session.get('elimination_questions', [])
    
    if not questions:
        return "No quiz data found. Please start the quiz again.", 404
    
    # Calculate score
    correct = 0
    total = len(questions)
    results = []
    
    for i, question in enumerate(questions):
        user_answer_raw = request.form.get(f'answer_{i}')
        
        # Multiple choice - compare index
        user_answer = int(user_answer_raw) if user_answer_raw else None
        correct_answer = question.get('correct')
        is_correct = user_answer == correct_answer
        
        if is_correct:
            correct += 1
        
        # Store result with options for display
        results.append({
            'question': question.get('question'),
            'options': question.get('options', []),
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': question.get('explanation', ''),
            'topic_name': question.get('topic_name', ''),
            'subtopic_name': question.get('subtopic_name', '')
        })
    
    score_percentage = (correct / total * 100) if total > 0 else 0
    
    # Clear session data
    session.pop('elimination_questions', None)
    
    return render_template('results.html',
                         results={
                             'correct': correct,
                             'total': total,
                             'percentage': round(score_percentage, 2),
                             'results': results
                         },
                         mode='elimination_full',
                         topic_id=None,
                         subtopic_id=None)

@app.route('/finals/submit', methods=['POST'])
def submit_finals():
    """Submit finals mode answers and display results"""
    # Get questions from session
    questions = session.get('finals_questions', [])
    
    if not questions:
        return "No quiz data found. Please start the quiz again.", 404
    
    # Calculate score
    correct = 0
    total = len(questions)
    results = []
    
    for i, question in enumerate(questions):
        user_answer_raw = request.form.get(f'answer_{i}')
        
        # Identification - compare text (case-insensitive)
        user_answer = user_answer_raw.strip() if user_answer_raw else ""
        correct_answer = question.get('answer', '').strip()
        alternatives = question.get('alternatives', [])
        
        # Check if answer matches (case-insensitive)
        user_answer_lower = user_answer.lower()
        correct_answer_lower = correct_answer.lower()
        
        is_correct = user_answer_lower == correct_answer_lower
        
        # Check alternatives if not correct
        if not is_correct and alternatives:
            for alt in alternatives:
                if user_answer_lower == alt.lower().strip():
                    is_correct = True
                    break
        
        if is_correct:
            correct += 1
        
        results.append({
            'question': question.get('question'),
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': question.get('explanation', ''),
            'difficulty': question.get('difficulty', ''),
            'topic_name': question.get('topic_name', ''),
            'subtopic_name': question.get('subtopic_name', '')
        })
    
    score_percentage = (correct / total * 100) if total > 0 else 0
    
    # Clear session data
    session.pop('finals_questions', None)
    
    return render_template('results.html',
                         results={
                             'correct': correct,
                             'total': total,
                             'percentage': round(score_percentage, 2),
                             'results': results
                         },
                         mode='finals_full',
                         topic_id=None,
                         subtopic_id=None)

@app.route('/quiz/submit', methods=['POST'])
def submit_quiz():
    """Submit quiz answers and display results (Review mode)"""
    topic_id = request.form.get('topic_id')
    subtopic_id = request.form.get('subtopic_id')
    mode = request.form.get('mode', 'elimination')
    difficulty = request.form.get('difficulty', 'easy')
    
    # Load the subtopic questions
    subtopic_data = load_subtopic_questions(topic_id, subtopic_id, mode, difficulty)
    
    if not subtopic_data:
        return "Quiz not found", 404
    
    questions = subtopic_data.get('questions', [])
    
    # Calculate score
    correct = 0
    total = len(questions)
    results = []
    
    for i, question in enumerate(questions):
        user_answer_raw = request.form.get(f'answer_{i}')
        
        if mode == 'elimination':
            # Multiple choice - compare index
            user_answer = int(user_answer_raw) if user_answer_raw else None
            correct_answer = question.get('correct')
            is_correct = user_answer == correct_answer
            
            results.append({
                'question': question.get('question'),
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question.get('explanation', ''),
                'mode': 'elimination'
            })
        else:
            # Identification - compare text (case-insensitive)
            user_answer = user_answer_raw.strip() if user_answer_raw else ""
            correct_answer = question.get('answer', '').strip()
            alternatives = question.get('alternatives', [])
            
            # Check if answer matches (case-insensitive)
            user_answer_lower = user_answer.lower()
            correct_answer_lower = correct_answer.lower()
            
            is_correct = user_answer_lower == correct_answer_lower
            
            # Check alternatives if not correct
            if not is_correct and alternatives:
                for alt in alternatives:
                    if user_answer_lower == alt.lower().strip():
                        is_correct = True
                        break
            
            results.append({
                'question': question.get('question'),
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question.get('explanation', ''),
                'mode': 'finals'
            })
        
        if is_correct:
            correct += 1
    
    score_percentage = (correct / total * 100) if total > 0 else 0
    
    return render_template('results.html',
                         results={
                             'correct': correct,
                             'total': total,
                             'percentage': round(score_percentage, 2),
                             'results': results
                         },
                         questions=questions,
                         topic_id=topic_id,
                         subtopic_id=subtopic_id,
                         mode=mode,
                         difficulty=difficulty)

@app.route('/api/topics', methods=['GET'])
def get_topics_api():
    """Get all available quiz topics with their subtopic counts (API)"""
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
    """Get quiz questions for a specific subtopic with mode and difficulty"""
    mode = request.args.get('mode', 'elimination')
    difficulty = request.args.get('difficulty', 'easy')
    
    # Load questions based on mode and difficulty
    subtopic_data = load_subtopic_questions(topic_id, subtopic_id, mode, difficulty)
    
    if not subtopic_data:
        return jsonify({'error': 'Quiz not found'}), 404
    
    questions = subtopic_data.get('questions', [])
    
    # Optionally limit number of questions
    limit = request.args.get('limit', type=int)
    if limit and limit < len(questions):
        questions = random.sample(questions, limit)
    
    return jsonify({
        'topic_id': topic_id,
        'subtopic_id': subtopic_id,
        'subtopic_name': subtopic_data.get('subtopic_name', ''),
        'mode': mode,
        'difficulty': difficulty if mode == 'finals' else None,
        'questions': questions
    })

@app.route('/api/submit', methods=['POST'])
def submit_quiz_api():
    """Submit quiz answers and get results (API endpoint)"""
    data = request.json
    topic_id = data.get('topic_id')
    subtopic_id = data.get('subtopic_id')
    mode = data.get('mode', 'elimination')
    difficulty = data.get('difficulty', 'easy')
    answers = data.get('answers', {})
    
    # Load the subtopic questions
    subtopic_data = load_subtopic_questions(topic_id, subtopic_id, mode, difficulty)
    
    if not subtopic_data:
        return jsonify({'error': 'Quiz not found'}), 404
    
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
