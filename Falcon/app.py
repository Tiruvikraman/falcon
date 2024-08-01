from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from student_functions import extract_text_from_pdf,generate_ai_response,generate_project_idea,generate_project_idea_questions,generate_quiz,generate_response_from_pdf,generate_step_by_step_explanation,perform_ocr,study_plan,ConversationBufferMemory,get_first_youtube_video_link
from teacher_function import convert_from_path,evaluate,extract_text_from_image,extract_text_from_pdf,generate_questions_from_text,generate_student_report,generate_timetable_module

# Firebase setup
cred = credentials.Certificate(r'Falcon\\falcon-50f06-firebase-adminsdk-no87w-d32c464aa6.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
AI71_API_KEY = "api71-api-df260d58-62e0-46c9-b549-62daa9c409be"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS =  {'pdf', 'jpg', 'jpeg', 'png'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
memory = ConversationBufferMemory()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

@app.route('/student_pdfqa', methods=['GET', 'POST'])
def student_pdfqa():
    if request.method == 'POST':
        file = request.files.get('pdf-file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            pdf_text = extract_text_from_pdf(file_path)
            return jsonify({'message': f'PDF uploaded and processed. You can now ask questions.', 'pdf_text': pdf_text})
        else:
            return jsonify({'message': 'Invalid file type. Please upload a PDF.'}), 400

    return render_template('student_pdfqa.html')

@app.route('/ask_pdf_question', methods=['POST'])
def ask_pdf_question():
    data = request.json
    query = data['query']
    pdf_text = data['pdf_text']
    
    response = generate_response_from_pdf(query, pdf_text)[:-6]
    return jsonify({'response': response})

@app.route('/student_aitutor')
def student_aitutor():
    return render_template('student_aitutor.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data['message']
    response = generate_ai_response(query)
    return jsonify({'response': response})

@app.route('/upload_image_for_ocr', methods=['POST'])
def upload_image_for_ocr():
    if 'image-file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image-file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        extracted_text = perform_ocr(file_path)
        ai_response = generate_ai_response(extracted_text)
        
        return jsonify({'ai_response': ai_response})
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/student_projectideas')
def student_projectideas():
    return render_template('student_projectideas.html')

@app.route('/student_quiz')
def student_quiz():
    return render_template('student_quiz.html')



@app.route('/student_reward_points')
def student_reward_points():
    return render_template('student_reward_points.html')

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz_route():
    data = request.json
    subject = data['subject']
    topic = data['topic']
    count = int(data['num-questions'])
    difficulty = data['difficulty']
    
    quiz = generate_quiz(subject, topic, count, difficulty)
    return jsonify({'quiz': quiz})

@app.route('/generate_project_idea', methods=['POST'])
def generate_project_idea_route():
    data = request.json
    subject = data['subject']
    topic = data['topic']
    plan = data['plan']
    
    project_idea = generate_project_idea(subject, topic, plan)
    return jsonify({'project_idea': project_idea})

@app.route('/homework')
def homework():
    return render_template('homework.html')

@app.route('/student_courses')
def student_courses():
    return render_template('student_courses.html')

@app.route('/search_youtube', methods=['POST'])
def search_youtube():
    data = request.json
    query = data['query']
    
    try:
        video_link, video_title = get_first_youtube_video_link(query)
        video_id = video_link.split('v=')[1]
        return jsonify({
            'videoId': video_id,
            'videoTitle': video_title
        })
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/ask_followup', methods=['POST'])
def ask_followup_route():
    data = request.json
    project_idea = data['project_idea']
    query = data['query']
    
    response = generate_project_idea_questions(project_idea, query)
    return jsonify({'response': response})

@app.route('/student_studyplans')
def student_studyplans():
    return render_template('student_studyplans.html')

@app.route('/generate_study_plan', methods=['POST'])
def generate_study_plan_route():
    data = request.json
    subjects = data['subjects']
    hours = data['hours']
    area_lag = data['areaLag']  # Ensure the key matches
    goal = data['goal']
    learning_style = data['learningStyle']

    study_plan_text = study_plan(subjects, hours, area_lag, goal)
    return jsonify({'study_plan': study_plan_text})


@app.route('/student_stepexplanation')
def student_stepexplanation():
    return render_template('student_stepexplanation.html')


@app.route('/generate_step_by_step_explanation', methods=['POST'])
def generate_step_by_step_explanation_route():
    data = request.get_json()
    question = data['question']
    answer = generate_step_by_step_explanation(question)
    return jsonify({'answer': answer})

@app.route('/speak')
def speak():
    return render_template('student_speakai.html')

@app.route('/generate-timetable', methods=['POST'])
def generate_timetable():
    data = request.json
    hours_per_day = data.get('hours_per_day')
    days_per_week = data.get('days_per_week')
    semester_end_date = data.get('semester_end_date')
    subjects = data.get('subjects', [])

    # Input validation
    if not hours_per_day or not days_per_week or not semester_end_date or not subjects:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        timetable=generate_timetable_module(data,hours_per_day,days_per_week,semester_end_date,subjects)
        
        return jsonify({"timetable": timetable})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/generate-paper', methods=['GET', 'POST'])
def generate_paper():
    if request.method == 'POST':
        no_of_questions = int(request.form['no_of_questions'])
        total_marks = int(request.form['total_marks'])
        no_of_parts = int(request.form['no_of_parts'])
        marks_per_part = int(request.form['marks_per_part'])
        test_duration = request.form['test_duration']
        pdf_file = request.files['pdf_file']

        if pdf_file:
            # Secure the file name and save the file to the upload folder
            filename = secure_filename(pdf_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pdf_file.save(file_path)

            # Extract text from the curriculum PDF
            curriculum_text = extract_text_from_pdf(file_path)

            # Generate questions
            questions = generate_questions_from_text(curriculum_text, no_of_questions, marks_per_part, no_of_parts)

            # Optionally, remove the saved file after use
            os.remove(file_path)

            return render_template('teacher_paper_gen.html', questions=questions)

    return render_template('teacher_paper_gen.html')


@app.route('/eval', methods=['GET', 'POST'])
def eval():
    if request.method == 'POST':
        input_type = request.form['input_type']
        question_text = ""
        answer_text = ""
        max_marks = request.form['max_marks']

        if input_type == 'file':
            question_file = request.files['question_file']
            answer_file = request.files['answer_file']

            if question_file and answer_file:
                question_path = os.path.join(app.config['UPLOAD_FOLDER'], question_file.filename)
                answer_path = os.path.join(app.config['UPLOAD_FOLDER'], answer_file.filename)

                question_file.save(question_path)
                answer_file.save(answer_path)

                if question_path.endswith('.pdf'):
                    question_text = extract_text_from_pdf(question_path)
                else:
                    question_text = extract_text_from_image(question_path)

                if answer_path.endswith('.pdf'):
                    answer_text = extract_text_from_pdf(answer_path)
                else:
                    answer_text = extract_text_from_image(answer_path)

        elif input_type == 'text':
            question_text = request.form['question_text']
            answer_text = request.form['answer_text']

        evaluation_result = evaluate(question_text, answer_text, max_marks)
        print(f"Question Text: {question_text}")  # Debugging line
        print(f"Answer Text: {answer_text}")  # Debugging line
        print(f"Evaluation Result: {evaluation_result}")  # Debugging line

        return render_template('teacher_result.html', result=evaluation_result)

    return render_template('teacher_eval.html')

@app.route('/get_students')
def get_students():
    # Retrieve data from Firestore
    students_ref = db.collection('students')
    docs = students_ref.stream()
    students = [doc.to_dict() for doc in docs]
    return jsonify(students)


@app.route('/generate_report', methods=['POST'])
def generate_report():
    student_data = request.json
    report = generate_student_report(
        student_data['name'],
        student_data['age'],
        student_data['cgpa'],
        student_data['course_pursuing'],
        student_data['assigned_test_score'],
        student_data['ai_test_score'],
        student_data['interests'],
        student_data['difficulty_in'],
        student_data['courses_taken']
    )
    return jsonify({'report': report})



if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)

