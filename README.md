# IT Quizbee - Interactive IT Quiz Reviewer

A comprehensive web-based quiz application built with Flask, featuring 10 essential IT topics, each with 10 subtopics, totaling 100 subtopics with 10 questions each (1000 questions total).

## Features

- 🎯 **10 IT Topics**: Extensive coverage of IT concepts
  - **Basic Computer Concepts & IT**
  - **Logic Formulation**
  - **Operating Systems**
  - **Software Engineering**
  - **Object Oriented Programming**
  - **Computer Networks & Telecommunication**
  - **Computer Architecture & IT Security**
  - **Database Management System**
  - **Data Science & Analytics**
  - **E-commerce & Web Design**

See topics breakdown in [TOPICS.md](TOPICS.md)

- ✨ **Interactive UI**: Built with Tailwind CSS and Bootstrap Icons
- 📊 **Instant Results**: Get immediate feedback with detailed explanations
- 📱 **Responsive Design**: Works on all devices
- 🎓 **Educational**: Learn from detailed answer explanations
- 🔄 **Hierarchical Navigation**: Topic → Subtopic → Quiz flow

## Technologies Used

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Tailwind CSS (via CDN)
- **Icons**: Bootstrap Icons
- **Data**: JSON format

## Installation

1. **Clone or navigate to the project directory**:
```bash
cd IT-Quizbee
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

## Running the Application

1. **Start the Flask server**:
```bash
python app.py
```

2. **Open your browser** and navigate to:
```
http://localhost:5000
```

## Project Structure

```
IT-Quizbee/
│
├── app.py                          # Flask application with API routes
├── requirements.txt                # Python dependencies
├── generate_subtopics.py           # Script to generate subtopic files
│
├── templates/
│   └── index.html                  # Main HTML template
│
├── static/
│   └── script.js                   # Frontend JavaScript
│
└── data/                           # Hierarchical quiz data structure
    ├── it_basics/
    │   ├── index.json              # Topic metadata and subtopic list
    │   ├── hardware_basics.json    # 10 questions
    │   ├── software_fundamentals.json
    │   ├── input_output_devices.json
    │   ├── memory_storage.json
    │   ├── number_systems.json
    │   ├── computer_basics.json
    │   ├── internet_basics.json
    │   ├── file_management.json
    │   ├── computer_history.json
    │   └── it_terminology.json
    │
    ├── logic/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── operating_systems/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── software_engineering/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── oop/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── networks/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── computer_architecture/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── dbms/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── data_science/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    └── ecommerce_web/
        ├── index.json
        └── [10 subtopic files]
```

## API Endpoints

- `GET /` - Main application page
- `GET /api/topics` - Get all available topics with subtopic counts
- `GET /api/topics/<topic_id>/subtopics` - Get all subtopics for a specific topic
- `GET /api/quiz/<topic_id>/<subtopic_id>` - Get quiz questions for a specific subtopic
- `POST /api/submit` - Submit quiz answers and get results

## Usage

1. Click **Start Quiz** on the welcome page
2. Select a main topic from the 10 available options
3. Choose a subtopic from the 10 subtopics within that topic
4. Answer each question (10 questions per subtopic)
5. Navigate through questions using Previous/Next buttons
6. Submit the quiz when complete
7. Review your results with detailed explanations
8. Retake the same quiz or go back to choose another subtopic

## Data Structure

### Topic Index File (`index.json`)
Each topic folder contains an `index.json` with metadata:
```json
{
  "topic_id": "it_basics",
  "topic_name": "Basic Computer Concepts & IT",
  "description": "Fundamental concepts...",
  "subtopics": [
    {
      "id": "hardware_basics",
      "name": "Hardware Basics",
      "description": "Computer hardware components..."
    }
  ]
}
```

### Subtopic File (`subtopic_id.json`)
Each subtopic file contains 10 questions:
```json
{
  "subtopic_id": "hardware_basics",
  "subtopic_name": "Hardware Basics",
  "questions": [
    {
      "question": "Your question here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct": 0,
      "explanation": "Explanation of the correct answer"
    }
  ]
}
```

## Customization

### Adding New Questions

1. Navigate to the appropriate subtopic file in `data/<topic_id>/<subtopic_id>.json`
2. Add your question following the format above
3. The correct answer index starts at 0 (0 = first option, 1 = second option, etc.)

### Adding New Subtopics

1. Add the subtopic to the topic's `index.json` file
2. Create a new JSON file with the subtopic questions
3. Follow the naming convention: `<subtopic_id>.json`

### Adding New Topics

1. Create a new folder in `data/`
2. Create an `index.json` file with topic metadata
3. Create 10 subtopic JSON files
4. Restart the Flask server to detect the new topic

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Author

- Michael Angelo R. Cantara — https://github.com/MACantara

Created with ❤️ for IT learners everywhere!
