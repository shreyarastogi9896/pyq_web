import os
import fitz  # PyMuPDF
from flask import Flask, request, render_template_string
from langchainfile import Chain
import json
import re
from pdf2image import convert_from_bytes
import pytesseract
app= Flask(__name__)


# HTML Template (with upload form and results)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>PDF Metadata Extractor</title></head>
<body>
  <h2>Upload a PDF File</h2>
  <form action="/upload" method="post" enctype="multipart/form-data">
    <input type="file" name="file" accept="application/pdf" required>
    <input type="submit" value="Upload">
  </form>

  {% if results %}
    <h2>Extracted Metadata</h2>
    <ul>
    {% for item in results %}
      <li><strong>Page {{ item.page }}:</strong>
        <pre>{{ item.metadata | tojson(indent=2) }}</pre>
      </li>
    {% endfor %}
    </ul>
  {% endif %}
</body>
</html>
'''

review_metadata = '''
<!DOCTYPE html>
<html>
<head><title>Review PDF Metadata</title></head>
<body>

<form method="POST" action="/submit">
  {% for item in results %}
    <h3>Page {{ item.page }}</h3>
    Subject: <input name="subject_{{ item.page }}" value="{{ item.metadata.subject }}"><br>
    Course Code: <input name="course_code_{{ item.page }}" value="{{ item.metadata.course_code }}"><br>
    Semester: <input name="semester_{{ item.page }}" value="{{ item.metadata.semester }}"><br>
    Year: <input name="year_{{ item.page }}" value="{{ item.metadata.year }}"><br>
    <hr>
  {% endfor %}
  <input type="submit" value="Save All">
</form>
</body>
</html>
'''


# Extract text from each PDF page
def extract_text_from_scanned_pdf(pdf_bytes):
    
    images = convert_from_bytes(pdf_bytes, dpi=300,poppler_path=r"C:\Users\deeshika & Sherya\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin")
    text_per_page = []

    for img in images:
        text = pytesseract.image_to_string(img)
        text_per_page.append(text)

    return text_per_page



def extract_text_per_page(pdf_bytes):
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text_per_page = [page.get_text().strip() for page in doc]

    # If all pages are empty → fallback to OCR
    if all(not t for t in text_per_page):
        print("No extractable text found — falling back to OCR.")
        text_per_page = extract_text_from_scanned_pdf(pdf_bytes)

    return text_per_page




@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    pdf_bytes = file.read()
    pages = extract_text_per_page(pdf_bytes)
    chain = Chain()
    results = []

    for i, text in enumerate(pages):
        metadata = chain.extract_metadata(text)
        print("Raw metadata:", metadata)
        

        # Attempt to extract the JSON-like part from the text
        match = re.search(r"\{[\s\S]*?\}", metadata)
        if match:
          try:
            parsed = json.loads(match.group())
          except Exception as e:
            print("JSON parsing failed:", e)
            parsed = {}
        else:
          parsed = {}

        
        parsed.setdefault("subject", "")
        parsed.setdefault("course_code", "")
        parsed.setdefault("semester", "")
        parsed.setdefault("year", "")
        try:
            parsed = json.loads(metadata)
        except:
            parsed = {"subject": "", "course_code": "", "semester": "", "year": ""}
        results.append({"page": i + 1, "metadata": parsed})

    return render_template_string(review_metadata, results=results)


if __name__ == '__main__':
    app.run(debug=True)
