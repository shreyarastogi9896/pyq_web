import os
import fitz  # PyMuPDF
from flask import Flask, request, render_template_string
from langchainfile import Chain
import json
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

# Extract text from each PDF page
def extract_text_per_page(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return [page.get_text() for page in doc]



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
        metadata =chain.extract_metadata(text)
        results.append({"page": i + 1, "metadata": metadata})

    return render_template_string(HTML_TEMPLATE, results=results)

if __name__ == '__main__':
    app.run(debug=True)
