import json
import os

# Template questions for each subtopic
def generate_questions(subtopic_name, count=10):
    """Generate template questions for a subtopic"""
    questions = []
    for i in range(1, count + 1):
        question = {
            "question": f"{subtopic_name} - Question {i}: Sample question about this topic?",
            "options": [
                f"Option A for question {i}",
                f"Option B for question {i}",
                f"Option C for question {i}",
                f"Option D for question {i}"
            ],
            "correct": (i - 1) % 4,  # Rotate correct answers
            "explanation": f"This is the explanation for question {i} in {subtopic_name}. The correct answer provides the best solution."
        }
        questions.append(question)
    return questions

# All topics with their subtopics (from index files)
topics_subtopics = {
    "it_basics": [
        ("hardware_basics", "Hardware Basics"),
        ("software_fundamentals", "Software Fundamentals"),
        ("input_output_devices", "Input/Output Devices"),
        ("memory_storage", "Memory & Storage"),
        ("number_systems", "Number Systems"),
        ("computer_basics", "Computer Basics"),
        ("internet_basics", "Internet Basics"),
        ("file_management", "File Management"),
        ("computer_history", "Computer History"),
        ("it_terminology", "IT Terminology")
    ],
    "logic": [
        ("propositional_logic", "Propositional Logic"),
        ("logical_operators", "Logical Operators"),
        ("truth_tables", "Truth Tables"),
        ("logical_equivalence", "Logical Equivalence"),
        ("implications", "Implications & Conditionals"),
        ("quantifiers", "Quantifiers"),
        ("logical_laws", "Logical Laws"),
        ("arguments", "Arguments & Validity"),
        ("predicate_logic", "Predicate Logic"),
        ("proof_techniques", "Proof Techniques")
    ],
    "operating_systems": [
        ("os_fundamentals", "OS Fundamentals"),
        ("process_management", "Process Management"),
        ("cpu_scheduling", "CPU Scheduling"),
        ("memory_management", "Memory Management"),
        ("file_systems", "File Systems"),
        ("deadlock", "Deadlock"),
        ("synchronization", "Synchronization"),
        ("io_systems", "I/O Systems"),
        ("security_protection", "Security & Protection"),
        ("os_types", "OS Types")
    ],
    "software_engineering": [
        ("sdlc", "Software Development Life Cycle"),
        ("agile_methodologies", "Agile Methodologies"),
        ("requirements_engineering", "Requirements Engineering"),
        ("software_design", "Software Design"),
        ("testing", "Software Testing"),
        ("version_control", "Version Control"),
        ("code_quality", "Code Quality"),
        ("devops", "DevOps"),
        ("project_management", "Project Management"),
        ("maintenance", "Software Maintenance")
    ],
    "oop": [
        ("oop_basics", "OOP Basics"),
        ("encapsulation", "Encapsulation"),
        ("inheritance", "Inheritance"),
        ("polymorphism", "Polymorphism"),
        ("abstraction", "Abstraction"),
        ("constructors", "Constructors & Destructors"),
        ("design_patterns", "Design Patterns"),
        ("solid_principles", "SOLID Principles"),
        ("relationships", "Object Relationships"),
        ("advanced_oop", "Advanced OOP")
    ],
    "networks": [
        ("network_fundamentals", "Network Fundamentals"),
        ("osi_model", "OSI Model"),
        ("tcp_ip", "TCP/IP Protocol Suite"),
        ("network_devices", "Network Devices"),
        ("ip_addressing", "IP Addressing"),
        ("routing", "Routing Protocols"),
        ("wireless_networks", "Wireless Networks"),
        ("network_security", "Network Security"),
        ("application_protocols", "Application Protocols"),
        ("network_troubleshooting", "Network Troubleshooting")
    ],
    "computer_architecture": [
        ("cpu_architecture", "CPU Architecture"),
        ("memory_hierarchy", "Memory Hierarchy"),
        ("instruction_set", "Instruction Set Architecture"),
        ("pipelining", "Pipelining"),
        ("parallel_processing", "Parallel Processing"),
        ("cryptography", "Cryptography"),
        ("security_threats", "Security Threats"),
        ("authentication", "Authentication"),
        ("security_protocols", "Security Protocols"),
        ("cyber_defense", "Cyber Defense")
    ],
    "dbms": [
        ("database_fundamentals", "Database Fundamentals"),
        ("relational_model", "Relational Model"),
        ("sql_basics", "SQL Basics"),
        ("sql_advanced", "Advanced SQL"),
        ("normalization", "Normalization"),
        ("transactions", "Transactions"),
        ("indexing", "Indexing"),
        ("nosql", "NoSQL Databases"),
        ("database_design", "Database Design"),
        ("database_security", "Database Security")
    ],
    "data_science": [
        ("data_fundamentals", "Data Fundamentals"),
        ("statistics", "Statistics"),
        ("data_preprocessing", "Data Preprocessing"),
        ("data_visualization", "Data Visualization"),
        ("ml_basics", "Machine Learning Basics"),
        ("supervised_learning", "Supervised Learning"),
        ("unsupervised_learning", "Unsupervised Learning"),
        ("python_data_tools", "Python Data Tools"),
        ("big_data", "Big Data"),
        ("data_ethics", "Data Ethics")
    ],
    "ecommerce_web": [
        ("html_basics", "HTML Basics"),
        ("css_styling", "CSS Styling"),
        ("javascript_basics", "JavaScript Basics"),
        ("responsive_design", "Responsive Design"),
        ("web_frameworks", "Web Frameworks"),
        ("ecommerce_platforms", "E-commerce Platforms"),
        ("payment_systems", "Payment Systems"),
        ("seo", "SEO"),
        ("web_security", "Web Security"),
        ("digital_marketing", "Digital Marketing")
    ]
}

# Generate all subtopic files
base_path = "data"
files_created = 0

for topic_id, subtopics in topics_subtopics.items():
    topic_dir = os.path.join(base_path, topic_id)
    
    # Skip if hardware_basics already exists (we created it manually)
    for subtopic_id, subtopic_name in subtopics:
        file_path = os.path.join(topic_dir, f"{subtopic_id}.json")
        
        # Skip if file already exists
        if os.path.exists(file_path):
            print(f"Skipping {file_path} (already exists)")
            continue
        
        # Generate the subtopic data
        subtopic_data = {
            "subtopic_id": subtopic_id,
            "subtopic_name": subtopic_name,
            "questions": generate_questions(subtopic_name, 10)
        }
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(subtopic_data, f, indent=2, ensure_ascii=False)
        
        files_created += 1
        print(f"Created: {file_path}")

print(f"\nTotal files created: {files_created}")
print("Note: These are template questions. You should replace them with actual content.")
