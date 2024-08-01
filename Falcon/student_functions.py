from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import easyocr
from pypdf import PdfReader
from ai71 import AI71
AI71_API_KEY = "api71-api-df260d58-62e0-46c9-b549-62daa9c409be"

def extract_text_from_pdf(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    print(text)
    return text

def generate_response_from_pdf(query, pdf_text):
    response = ''
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a project building assistant."},
            {"role": "user", "content": f'''Answer the querry based on the given content.Content:{pdf_text},query:{query}'''},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            response += chunk.choices[0].delta.content
    return response[:-6]

def generate_quiz(subject, topic, count, difficult):
    quiz_output = ""
    
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a teaching assistant."},
            {"role": "user", "content": f'''Generate {count} multiple-choice questions in the subject of {subject} for the topic {topic} for students at a {difficult} level. Ensure the questions are well-diversified and cover various aspects of the topic. Format the questions as follows:
Question: [Question text] [specific concept in a question] 
<<o>> [Option1] 
<<o>> [Option2] 
<<o>> [Option3] 
<<o>> [Option4], 
Answer: [Option number]'''},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            quiz_output += chunk.choices[0].delta.content
    print("Quiz generated")
    return quiz_output

def perform_ocr(image_path):
    reader = easyocr.Reader(['en'])
    try:
        result = reader.readtext(image_path)
        extracted_text = ''
        for (bbox, text, prob) in result:
            extracted_text += text + ' '
        return extracted_text.strip()
    except Exception as e:
        print(f"Error during OCR: {e}")
        return ''

def generate_ai_response(query):
    ai_response = ''
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a teaching assistant."},
            {"role": "user", "content": f'Assist the user clearly for his questions: {query}.'},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            ai_response += chunk.choices[0].delta.content
    return ai_response


def generate_project_idea(subject, topic, overview):
    string = ''
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a project building assistant."},
            {"role": "user", "content": f'''Give the different project ideas to build project in {subject} specifically in {topic} for school students. {overview}.'''},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            string += chunk.choices[0].delta.content
    return string

def generate_project_idea_questions(project_idea, query):
    project_idea_answer = ''
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a project building assistant."},
            {"role": "user", "content": f'''Assist me clearly for the following question for the given idea. Idea: {project_idea}. Question: {query}'''},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            project_idea_answer += chunk.choices[0].delta.content
    return project_idea_answer
def generate_step_by_step_explanation(query):
    explanation = ''
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are the best teaching assistant."},
            {"role": "user", "content": f'''Provide me the clear step by step explanation answer for the following question. Question: {query}'''},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            explanation += chunk.choices[0].delta.content
    return explanation


def study_plan(subjects,hours,arealag,goal):
  plan=''
  for chunk in AI71(AI71_API_KEY).chat.completions.create(
      model="tiiuae/falcon-180b-chat",
      messages=[
          {"role": "system", "content": "You are the best teaching assistant."},
          {"role": "user", "content":f'''Provide me the clear personalised study plan for the subjects {subjects} i lag in areas like {arealag}, im available for {hours} hours per day and my study goal is to {goal}.Provide me like a timetable like day1,day2 for 5 days with concepts,also suggest some books'''},
      ],
      stream=True,
          ):
      if chunk.choices[0].delta.content:
                   plan+= chunk.choices[0].delta.content
  return plan.replace('\n','<br>')




class ConversationBufferMemory:
    def __init__(self, memory_key="chat_history"):
        self.memory_key = memory_key
        self.buffer = []

    def add_to_memory(self, interaction):
        self.buffer.append(interaction)

    def get_memory(self):
        return "\n".join([f"Human: {entry['user']}\nAssistant: {entry['assistant']}" for entry in self.buffer])

def spk_msg(user_input, memory):
    chat_history = memory.get_memory()
    msg = ''

    # Construct the message for the API request
    messages = [
        {"role": "system", "content": "You are a nice speaker having a conversation with a human.You ask the question the user choose the topic and let user answer.Provide the response only within 2 sentence"},
        {"role": "user", "content": f"Previous conversation:\n{chat_history}\n\nNew human question: {user_input}\nResponse:"}
    ]

    try:
        for chunk in AI71(AI71_API_KEY).chat.completions.create(
            model="tiiuae/falcon-180b-chat",
            messages=messages,
            stream=True,
        ):
            if chunk.choices[0].delta.content:
                msg += chunk.choices[0].delta.content
    except Exception as e:
        print(f"An error occurred: {e}")

    return msg


def get_first_youtube_video_link(query):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get('https://www.youtube.com')
        search_box = driver.find_element(By.NAME, 'search_query')
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a#video-title')))
        first_video = driver.find_element(By.CSS_SELECTOR, 'a#video-title')
        first_video_link = first_video.get_attribute('href')
        video_title = first_video.get_attribute('title')
        return first_video_link, video_title
    finally:
        driver.quit()