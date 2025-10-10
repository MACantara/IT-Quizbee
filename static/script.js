// Global state
let currentTopic = null;
let currentSubtopic = null;
let quizData = null;
let currentQuestion = 0;
let userAnswers = {};
let topics = [];
let subtopics = [];

// DOM Elements
const welcomeSection = document.getElementById('welcomeSection');
const topicSection = document.getElementById('topicSection');
const subtopicSection = document.getElementById('subtopicSection');
const quizSection = document.getElementById('quizSection');
const resultsSection = document.getElementById('resultsSection');
const loadingSpinner = document.getElementById('loadingSpinner');
const homeBtn = document.getElementById('homeBtn');

// Buttons
const startBtn = document.getElementById('startBtn');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const submitBtn = document.getElementById('submitBtn');
const retakeBtn = document.getElementById('retakeBtn');
const newTopicBtn = document.getElementById('newTopicBtn');

// Event Listeners
startBtn.addEventListener('click', loadTopics);
homeBtn.addEventListener('click', showWelcome);
prevBtn.addEventListener('click', previousQuestion);
nextBtn.addEventListener('click', nextQuestion);
submitBtn.addEventListener('click', submitQuiz);
retakeBtn.addEventListener('click', retakeQuiz);
newTopicBtn.addEventListener('click', backToSubtopics);

// Utility Functions
function showLoading() {
    loadingSpinner.classList.remove('hidden');
}

function hideLoading() {
    loadingSpinner.classList.add('hidden');
}

function hideAllSections() {
    welcomeSection.classList.add('hidden');
    topicSection.classList.add('hidden');
    subtopicSection.classList.add('hidden');
    quizSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
}

function showWelcome() {
    hideAllSections();
    welcomeSection.classList.remove('hidden');
    homeBtn.classList.add('hidden');
    currentTopic = null;
    currentSubtopic = null;
    quizData = null;
    currentQuestion = 0;
    userAnswers = {};
}

// Load Topics
async function loadTopics() {
    showLoading();
    try {
        const response = await fetch('/api/topics');
        topics = await response.json();
        displayTopics();
        hideAllSections();
        topicSection.classList.remove('hidden');
        homeBtn.classList.remove('hidden');
    } catch (error) {
        console.error('Error loading topics:', error);
        alert('Failed to load topics. Please try again.');
    } finally {
        hideLoading();
    }
}

// Display Topics
function displayTopics() {
    const topicGrid = document.getElementById('topicGrid');
    topicGrid.innerHTML = '';

    const icons = [
        'bi-cpu-fill',
        'bi-diagram-3-fill',
        'bi-gear-fill',
        'bi-code-slash',
        'bi-box-seam',
        'bi-router-fill',
        'bi-hdd-rack-fill',
        'bi-database-fill',
        'bi-graph-up',
        'bi-cart-fill'
    ];

    const colors = [
        'from-blue-500 to-blue-600',
        'from-purple-500 to-purple-600',
        'from-green-500 to-green-600',
        'from-yellow-500 to-yellow-600',
        'from-red-500 to-red-600',
        'from-pink-500 to-pink-600',
        'from-indigo-500 to-indigo-600',
        'from-teal-500 to-teal-600',
        'from-orange-500 to-orange-600',
        'from-cyan-500 to-cyan-600'
    ];

    topics.forEach((topic, index) => {
        const topicCard = document.createElement('div');
        topicCard.className = `bg-gradient-to-br ${colors[index % colors.length]} p-6 rounded-xl shadow-lg cursor-pointer transform hover:scale-105 transition duration-300 text-white`;
        topicCard.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <i class="bi ${icons[index % icons.length]} text-4xl"></i>
                <span class="bg-white text-gray-800 px-3 py-1 rounded-full text-sm font-semibold">${topic.subtopic_count} Topics</span>
            </div>
            <h3 class="text-xl font-bold mb-2">${topic.name}</h3>
            <p class="text-sm opacity-90">${topic.description || 'Click to view subtopics'}</p>
        `;
        topicCard.addEventListener('click', () => loadSubtopics(topic.id));
        topicGrid.appendChild(topicCard);
    });
}

// Load Subtopics
async function loadSubtopics(topicId) {
    showLoading();
    currentTopic = topicId;

    try {
        const response = await fetch(`/api/topics/${topicId}/subtopics`);
        const data = await response.json();
        subtopics = data.subtopics;
        
        displaySubtopics(data);
        hideAllSections();
        subtopicSection.classList.remove('hidden');
    } catch (error) {
        console.error('Error loading subtopics:', error);
        alert('Failed to load subtopics. Please try again.');
    } finally {
        hideLoading();
    }
}

// Display Subtopics
function displaySubtopics(topicData) {
    const subtopicTitle = document.getElementById('subtopicTitle');
    const subtopicDescription = document.getElementById('subtopicDescription');
    const subtopicGrid = document.getElementById('subtopicGrid');
    
    subtopicTitle.textContent = topicData.topic_name;
    subtopicDescription.textContent = topicData.description || '';
    subtopicGrid.innerHTML = '';

    const colors = [
        'border-blue-500 hover:bg-blue-50',
        'border-purple-500 hover:bg-purple-50',
        'border-green-500 hover:bg-green-50',
        'border-yellow-500 hover:bg-yellow-50',
        'border-red-500 hover:bg-red-50',
        'border-pink-500 hover:bg-pink-50',
        'border-indigo-500 hover:bg-indigo-50',
        'border-teal-500 hover:bg-teal-50',
        'border-orange-500 hover:bg-orange-50',
        'border-cyan-500 hover:bg-cyan-50'
    ];

    subtopics.forEach((subtopic, index) => {
        const subtopicCard = document.createElement('div');
        subtopicCard.className = `border-l-4 ${colors[index % colors.length]} p-4 rounded-lg shadow cursor-pointer transform hover:scale-102 transition duration-200 bg-white`;
        subtopicCard.innerHTML = `
            <h3 class="text-lg font-bold text-gray-800 mb-2">${subtopic.name}</h3>
            <p class="text-sm text-gray-600 mb-3">${subtopic.description || ''}</p>
            <div class="flex items-center justify-between">
                <span class="text-sm font-semibold text-gray-500">10 Questions</span>
                <i class="bi bi-arrow-right-circle text-xl text-gray-400"></i>
            </div>
        `;
        subtopicCard.addEventListener('click', () => startQuiz(currentTopic, subtopic.id));
        subtopicGrid.appendChild(subtopicCard);
    });
}

// Start Quiz
async function startQuiz(topicId, subtopicId) {
    showLoading();
    currentTopic = topicId;
    currentSubtopic = subtopicId;
    currentQuestion = 0;
    userAnswers = {};

    try {
        const response = await fetch(`/api/quiz/${topicId}/${subtopicId}`);
        quizData = await response.json();
        
        hideAllSections();
        quizSection.classList.remove('hidden');
        displayQuestion();
    } catch (error) {
        console.error('Error loading quiz:', error);
        alert('Failed to load quiz. Please try again.');
    } finally {
        hideLoading();
    }
}

// Display Question
function displayQuestion() {
    const question = quizData.questions[currentQuestion];
    const questionText = document.getElementById('questionText');
    const optionsContainer = document.getElementById('optionsContainer');
    const progressText = document.getElementById('progressText');
    const progressBar = document.getElementById('progressBar');

    // Update question
    questionText.textContent = `${currentQuestion + 1}. ${question.question}`;

    // Update progress
    progressText.textContent = `${currentQuestion + 1}/${quizData.questions.length}`;
    const progressPercent = ((currentQuestion + 1) / quizData.questions.length) * 100;
    progressBar.style.width = `${progressPercent}%`;

    // Display options
    optionsContainer.innerHTML = '';
    question.options.forEach((option, index) => {
        const optionDiv = document.createElement('div');
        const isSelected = userAnswers[currentQuestion] === index;
        
        optionDiv.className = `p-4 border-2 rounded-lg cursor-pointer transition ${
            isSelected 
                ? 'border-blue-600 bg-blue-50' 
                : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
        }`;
        
        optionDiv.innerHTML = `
            <div class="flex items-center gap-3">
                <div class="w-6 h-6 rounded-full border-2 ${
                    isSelected 
                        ? 'border-blue-600 bg-blue-600' 
                        : 'border-gray-400'
                } flex items-center justify-center">
                    ${isSelected ? '<i class="bi bi-check text-white text-sm"></i>' : ''}
                </div>
                <span class="font-semibold text-gray-700">${String.fromCharCode(65 + index)}.</span>
                <span class="text-gray-800">${option}</span>
            </div>
        `;
        
        optionDiv.addEventListener('click', () => selectAnswer(index));
        optionsContainer.appendChild(optionDiv);
    });

    // Update navigation buttons
    prevBtn.disabled = currentQuestion === 0;
    
    if (currentQuestion === quizData.questions.length - 1) {
        nextBtn.classList.add('hidden');
        submitBtn.classList.remove('hidden');
    } else {
        nextBtn.classList.remove('hidden');
        submitBtn.classList.add('hidden');
    }
}

// Select Answer
function selectAnswer(optionIndex) {
    userAnswers[currentQuestion] = optionIndex;
    displayQuestion();
}

// Navigation
function previousQuestion() {
    if (currentQuestion > 0) {
        currentQuestion--;
        displayQuestion();
    }
}

function nextQuestion() {
    if (currentQuestion < quizData.questions.length - 1) {
        currentQuestion++;
        displayQuestion();
    }
}

// Submit Quiz
async function submitQuiz() {
    // Check if all questions are answered
    const unansweredCount = quizData.questions.length - Object.keys(userAnswers).length;
    if (unansweredCount > 0) {
        const proceed = confirm(`You have ${unansweredCount} unanswered question(s). Do you want to submit anyway?`);
        if (!proceed) return;
    }

    showLoading();
    
    try {
        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic_id: currentTopic,
                subtopic_id: currentSubtopic,
                answers: userAnswers
            })
        });

        const results = await response.json();
        displayResults(results);
        
        hideAllSections();
        resultsSection.classList.remove('hidden');
    } catch (error) {
        console.error('Error submitting quiz:', error);
        alert('Failed to submit quiz. Please try again.');
    } finally {
        hideLoading();
    }
}

// Display Results
function displayResults(results) {
    const scoreIcon = document.getElementById('scoreIcon');
    const scorePercentage = document.getElementById('scorePercentage');
    const scoreText = document.getElementById('scoreText');
    const correctCount = document.getElementById('correctCount');
    const incorrectCount = document.getElementById('incorrectCount');
    const totalCount = document.getElementById('totalCount');
    const detailedResults = document.getElementById('detailedResults');

    // Set score icon based on percentage
    if (results.percentage >= 80) {
        scoreIcon.innerHTML = '🏆';
        scoreIcon.className = 'text-8xl mb-4 animate-bounce';
    } else if (results.percentage >= 60) {
        scoreIcon.innerHTML = '😊';
        scoreIcon.className = 'text-8xl mb-4';
    } else {
        scoreIcon.innerHTML = '📚';
        scoreIcon.className = 'text-8xl mb-4';
    }

    // Set score and message
    scorePercentage.textContent = `${results.percentage}%`;
    scorePercentage.className = `text-6xl font-bold mb-4 ${
        results.percentage >= 80 ? 'text-green-600' :
        results.percentage >= 60 ? 'text-yellow-600' :
        'text-red-600'
    }`;

    if (results.percentage >= 80) {
        scoreText.textContent = 'Excellent! You\'ve mastered this topic! 🎉';
    } else if (results.percentage >= 60) {
        scoreText.textContent = 'Good job! Keep practicing to improve! 💪';
    } else {
        scoreText.textContent = 'Keep studying! You\'ll get better! 📖';
    }

    // Set counts
    correctCount.textContent = results.correct;
    incorrectCount.textContent = results.total - results.correct;
    totalCount.textContent = results.total;

    // Display detailed results
    detailedResults.innerHTML = '';
    results.results.forEach((result, index) => {
        const resultDiv = document.createElement('div');
        const isCorrect = result.is_correct;
        
        resultDiv.className = `p-4 rounded-lg border-2 ${
            isCorrect ? 'border-green-300 bg-green-50' : 'border-red-300 bg-red-50'
        }`;
        
        const userAnswerText = result.user_answer !== undefined && result.user_answer !== null
            ? quizData.questions[index].options[result.user_answer]
            : 'Not answered';
        
        const correctAnswerText = quizData.questions[index].options[result.correct_answer];
        
        resultDiv.innerHTML = `
            <div class="flex items-start gap-3 mb-3">
                <i class="bi ${isCorrect ? 'bi-check-circle-fill text-green-600' : 'bi-x-circle-fill text-red-600'} text-2xl mt-1"></i>
                <div class="flex-1">
                    <h4 class="font-bold text-gray-800 mb-2">${index + 1}. ${result.question}</h4>
                    <div class="space-y-1 text-sm">
                        <p class="text-gray-700">
                            <span class="font-semibold">Your answer:</span> 
                            <span class="${isCorrect ? 'text-green-700' : 'text-red-700'}">${userAnswerText}</span>
                        </p>
                        ${!isCorrect ? `
                            <p class="text-gray-700">
                                <span class="font-semibold">Correct answer:</span> 
                                <span class="text-green-700">${correctAnswerText}</span>
                            </p>
                        ` : ''}
                        ${result.explanation ? `
                            <p class="text-gray-600 mt-2 italic">
                                <i class="bi bi-info-circle mr-1"></i>${result.explanation}
                            </p>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        detailedResults.appendChild(resultDiv);
    });
}

// Retake Quiz
function retakeQuiz() {
    currentQuestion = 0;
    userAnswers = {};
    hideAllSections();
    quizSection.classList.remove('hidden');
    displayQuestion();
}

// Go back to subtopics
function backToSubtopics() {
    if (currentTopic) {
        loadSubtopics(currentTopic);
    } else {
        loadTopics();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    showWelcome();
});
