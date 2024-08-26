GitHub Repository: Job Matching Web Application
Overview
This repository contains a Python-based web application that helps users upload their resumes and find matching jobs an APIs, from Adzuna. The application allows users to search for job opportunities by specifying job titles, locations, and salary preferences. The application also ranks the job matches based on the similarity between the job description and the uploaded resume. The results are automatically exported to an excel spreadsheet to the desired path that you configure.

Features
Resume Upload: Users can upload their resume in .docx format.
Job Search: Search jobs on Adzuna based on job titles and locations.
Job Ranking: The application ranks the jobs based on the similarity between the job descriptions and the uploaded resume.
Downloadable Results: Users can download the matched job results as an Excel file with clickable links to the job postings.

Installation
Clone the Repository
bash
git clone https://github.com/cdbarry53/job-matching-app.git
cd job-matching-app

Install the Required Packages Ensure you have Python installed. Then install the required packages by running:
bash
pip install -r requirements.txt

Create Uploads Directory Create a directory named uploads in the project root to store uploaded resumes.
bash
mkdir uploads

Set Up API Keys
Obtain your API key for Adzuna.
Replace the placeholder keys in the app.py script with your own API keys. This is found on lines 93 and 94.

Set up your directory path
On line 166 complete the desired output path of the excel spreadsheet.

Run the Application Start the Flask application by running:
bash
python app.py

Access the Application Open your web browser and navigate to http://127.0.0.1:5000/.

How to Use
Upload Your Resume: On the main page, upload your resume in .docx format.
Enter Job Details: Enter the desired job title(s), location, and minimum salary. You can also specify whether you want to search for remote jobs only.
View and Download Results: After submission, you’ll be redirected to the results page where you can view matched jobs. You can also download the results as an Excel file.
Directory Structure
plaintext
Copy code
job-matching-app/
│
├── app.py                # Main application script
├── requirements.txt      # Python dependencies
├── uploads/              # Directory for storing uploaded resumes
├── templates/            # HTML templates for the web pages
│   ├── index.html        # Main page template
│   ├── results.html      # Results page template
│
└── static/               # Static files (e.g., CSS, JavaScript)
API Integration
Adzuna API: Used to fetch job listings based on the job title, location, and salary. The API responses are processed to retrieve relevant job details.
Issues and Troubleshooting
API Rate Limits: If you hit rate limits, the application includes a retry mechanism that waits and retries the request.
No Results Found: If the application returns no results, ensure that your API keys are correct, and that the job title and location are valid.
Contribution
Feel free to fork this repository, submit pull requests, or open issues if you find any bugs or have suggestions for improvements.

This documentation provides a comprehensive overview of how to set up and use the job-matching web application, ensuring that users can easily get started and contribute to the project.
