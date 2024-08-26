from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
import re
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, numbers
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import time

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to extract text from a .docx resume
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Function to rank jobs based on resume match
def rank_jobs_by_resume(jobs, resume_text):
    job_descriptions = [job.get('description', '') for job in jobs]
    documents = [resume_text] + job_descriptions
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    ranked_jobs = sorted(zip(jobs, cosine_similarities[0]), key=lambda x: x[1], reverse=True)
    return [job for job, score in ranked_jobs]

# Function to send a GET request with retries
def get_with_retries(url, params, retries=3, delay=5):
    for attempt in range(retries):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response
        elif response.status_code == 503:
            time.sleep(delay)
        else:
            response.raise_for_status()
    raise Exception("Failed to retrieve data after multiple attempts.")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        if 'resume' not in request.files:
            return redirect(request.url)
        
        resume = request.files['resume']
        if resume.filename == '':
            return redirect(request.url)
        
        if resume:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resume.docx')
            resume.save(file_path)
            
            # Collect form data
            form_data = {
                'salary_min': request.form.get('salary_min', '90000'),
                'location': request.form.get('location', ''),
                'job_title': request.form.get('job_title', ''),
                'remote': request.form.get('remote', 'true')
            }
            
            # Redirect to results with form data in query string
            return redirect(url_for('results', **form_data))
    
    return render_template('index.html')

@app.route('/results', methods=['GET'])
def results():
    # Extract query parameters
    salary_min = request.args.get('salary_min', 90000) #specify the minimum salary
    location = request.args.get('location', '')
    job_title = request.args.get('job_title', '')
    is_remote = request.args.get('remote', 'true') == 'true'
    
    # Extract resume text
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resume.docx')
    resume_text = extract_text_from_docx(file_path)
    
    # Define API parameters
    app_id = ''
    app_key = ''
    endpoint = 'https://api.adzuna.com/v1/api/jobs/us/search/1'
    params = {
        'app_id': '', #Get your api id from https://developer.adzuna.com/admin/access_details
        'app_key': '',# Get your api key from https://developer.adzuna.com/admin/access_details
        'results_per_page': 500,
        'what': job_title,
        'where': location,
        'salary_min': salary_min,
        'full_time': 1,
        'content-type': 'application/json'
    }
    
    # Fetch jobs and rank
    total_results_needed = 500 # Specify the amount of jobs you would like in the output - the higher the number the longer it will take
    current_page = 1
    all_jobs = []
    
    while len(all_jobs) < total_results_needed:
        endpoint = f'https://api.adzuna.com/v1/api/jobs/us/search/{current_page}'
        response = get_with_retries(endpoint, params)
        data = response.json()
        jobs = data.get('results', [])
        if not jobs:
            break
        
        for job in jobs:
            title = job.get('title', '')
            description = job.get('description', '')
            location = job.get('location', {}).get('display_name', '')
            is_remote_job = any([
                'remote' in title.lower(),
                'remote' in description.lower(),
                'remote' in location.lower(),
                job.get('remote', False)
            ])
            
            if is_remote and not is_remote_job:
                continue
            
            salary_min = job.get('salary_min')
            salary_max = job.get('salary_max')
            if salary_min and salary_max:
                salary_avg = (salary_min + salary_max) / 2
            else:
                salary_avg = salary_min or salary_max or None
            
            direct_url = None
            url_pattern = re.compile(r'(https?://[^\s]+)')
            urls_in_description = url_pattern.findall(description)
            if urls_in_description:
                direct_url = urls_in_description[0]
            
            job_info = {
                'Title': title,
                'Company': job.get('company', {}).get('display_name', 'N/A'),
                'Location': location if location else 'N/A',
                'Salary Min': salary_min if salary_min else 'N/A',
                'Salary Max': salary_max if salary_max else 'N/A',
                'Salary Average': salary_avg if salary_avg else 'N/A',
                'Description': description,
                'URL': direct_url if direct_url else job.get('redirect_url', 'N/A')
            }
            all_jobs.append(job_info)
        
        current_page += 1
    
    ranked_jobs = rank_jobs_by_resume(all_jobs, resume_text)
    
    # Automatically save the results to an Excel file
    save_jobs_to_excel(ranked_jobs)
    
    return render_template('results.html', jobs=ranked_jobs)

def save_jobs_to_excel(jobs):
    # Define the file path below
    file_dir = r'C:\Users\'  
    file_name = 'Jobfinderoutput.xlsx'
    file_path = os.path.join(file_dir, file_name)

    # Ensure the directory exists
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    # Convert job data to DataFrame
    df = pd.DataFrame(jobs)

    # Write the DataFrame to an Excel file
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Jobs')
        workbook = writer.book
        worksheet = writer.sheets['Jobs']

        url_column = 'G'
        for row_idx in range(2, len(df) + 2):
            cell = worksheet[f'{url_column}{row_idx}']
            url = cell.value
            if url and isinstance(url, str):
                cell.hyperlink = url
                cell.value = "Click Here"
                cell.style = "Hyperlink"

        for col_letter in ['D', 'E', 'F']:
            for row_idx in range(2, len(df) + 2):
                cell = worksheet[f'{col_letter}{row_idx}']
                if isinstance(cell.value, (int, float)):
                    cell.number_format = numbers.FORMAT_CURRENCY_USD_SIMPLE

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.run(host='0.0.0.0', port=5000, debug=True)
