# Required packages:
# pip install Flask requests

import os
from flask import Flask, request, send_file, jsonify, render_template_string
import requests # For making requests to the external LaTeX API
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
LATEX_API_URL = "https://api.latex2pdf.com/compile" # Hypothetical API
TEX_FILENAME = "resume.tex"
PDF_FILENAME = "resume.pdf"
EDITOR_HTML_FILENAME = "editor.html"

# --- Helper Functions ---
def read_file_content(filename, default_content=""):
    """Reads the content of a file, returning default_content if not found."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.info(f"{filename} not found, will use default or try to create.")
        # For resume.tex, we ensure it's created at startup if not found.
        # For editor.html, it should exist.
        if filename == TEX_FILENAME and default_content:
             write_file_content(filename, default_content)
             return default_content
        return default_content if filename != EDITOR_HTML_FILENAME else "<p>Error: editor.html not found.</p>"


def write_file_content(filename, content):
    """Writes content to a file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Successfully wrote to {filename}")
    except IOError as e:
        logger.error(f"Error writing to {filename}: {e}")

# --- Flask Routes ---
@app.route('/')
def index():
    """Serves the main editor page."""
    if not os.path.exists(TEX_FILENAME):
        logger.info(f"{TEX_FILENAME} not found. Creating a default one.")
        default_latex = (
            "\\documentclass{article}\n"
            "\\usepackage[utf8]{inputenc}\n"
            "\\title{My Resume}\n"
            "\\author{Your Name}\n"
            "\\date{\\today}\n\n"
            "\\begin{document}\n\n"
            "\\maketitle\n\n"
            "Hello! This is a placeholder for your resume.tex. \n"
            "Edit this content and click 'Save Changes', then 'Compile to PDF'.\n\n"
            "\\section*{Experience}\n"
            "Your experience here...\n\n"
            "\\end{document}"
        )
        write_file_content(TEX_FILENAME, default_latex)

    tex_content = read_file_content(TEX_FILENAME)
    editor_html_content = read_file_content(EDITOR_HTML_FILENAME, "<p>Error: Main editor HTML file is missing.</p>")

    return render_template_string(editor_html_content, latex_content=tex_content)

@app.route('/edit', methods=['POST'])
def edit_tex_route():
    """Handles saving LaTeX content from the editor."""
    data = request.get_json()
    if data and 'latex_content' in data:
        latex_code = data['latex_content']
        write_file_content(TEX_FILENAME, latex_code)
        logger.info(f"Updated {TEX_FILENAME} from editor.")
        return jsonify({"message": f"{TEX_FILENAME} saved successfully."}), 200
    logger.warning("/edit endpoint called without latex_content.")
    return jsonify({"error": "No latex_content provided."}), 400

@app.route('/compile', methods=['POST'])
def compile_latex_route():
    """
    Reads resume.tex, sends it to the external LaTeX API,
    and saves the resulting PDF.
    """
    if not os.path.exists(TEX_FILENAME):
        logger.error(f"{TEX_FILENAME} not found for compilation.")
        return jsonify({"error": f"{TEX_FILENAME} not found. Cannot compile."}), 404

    tex_content = read_file_content(TEX_FILENAME)
    logger.info(f"Attempting to compile {TEX_FILENAME} using API: {LATEX_API_URL}")

    try:
        api_payload = {"latex_code": tex_content, "engine": "pdflatex", "filename": "resume"}
        # Some APIs might prefer form data, others JSON. Assuming JSON for this hypothetical API.
        headers = {'Content-Type': 'application/json'}
        response = requests.post(LATEX_API_URL, json=api_payload, headers=headers, timeout=90) # 90s timeout

        if response.status_code == 200 and response.headers.get('Content-Type') == 'application/pdf':
            with open(PDF_FILENAME, 'wb') as f:
                f.write(response.content)
            logger.info(f"Successfully compiled and saved {PDF_FILENAME}.")
            return jsonify({"message": f"Successfully compiled to {PDF_FILENAME}. Download link should be active."}), 200
        else:
            error_detail = response.text
            try:
                # If API returns JSON error, try to parse it for better logging
                json_error = response.json()
                error_detail = json_error.get('message') or json_error.get('error') or str(json_error)
            except ValueError: # Not JSON
                pass # Keep response.text

            logger.error(f"LaTeX API Error. Status: {response.status_code}. Response: {error_detail[:500]}")
            return jsonify({
                "error": "Failed to compile LaTeX via external API.",
                "api_status_code": response.status_code,
                "api_response": error_detail[:500] # Truncate long API error messages
            }), 500

    except requests.exceptions.Timeout:
        logger.error(f"Timeout connecting to LaTeX API: {LATEX_API_URL}")
        return jsonify({"error": "LaTeX compilation service timed out."}), 504 # Gateway Timeout
    except requests.exceptions.RequestException as e:
        logger.error(f"Error contacting LaTeX API: {e}")
        return jsonify({"error": "Failed to connect to LaTeX compilation service.", "details": str(e)}), 503 # Service Unavailable

@app.route('/download')
def download_pdf_route():
    """Serves the generated PDF file for download."""
    if os.path.exists(PDF_FILENAME):
        logger.info(f"Serving {PDF_FILENAME} for download.")
        return send_file(PDF_FILENAME, as_attachment=True, download_name=PDF_FILENAME)
    logger.warning(f"{PDF_FILENAME} requested for download but not found.")
    return jsonify({"error": f"{PDF_FILENAME} not found. Please compile the LaTeX document first."}), 404

if __name__ == '__main__':
    # Ensure resume.tex exists on startup (or create a default one)
    if not os.path.exists(TEX_FILENAME):
        logger.info(f"{TEX_FILENAME} not found at startup. Creating a default version.")
        default_latex = (
            "\\documentclass{article}\n"
            "\\usepackage[utf8]{inputenc}\n"
            "\\title{My Default Resume}\n"
            "\\author{Your Name Here}\n"
            "\\date{\\today}\n\n"
            "\\begin{document}\n\n"
            "\\maketitle\n\n"
            "This is a default resume.tex file. \n"
            "Please edit the content using the editor.\n\n"
            "\\section*{Introduction}\n"
            "Replace this with your actual resume content.\n\n"
            "\\end{document}"
        )
        write_file_content(TEX_FILENAME, default_latex)

    # Check if editor.html exists, as it's crucial.
    if not os.path.exists(EDITOR_HTML_FILENAME):
        logger.critical(f"{EDITOR_HTML_FILENAME} is missing! The application cannot start properly.")
        # In a real app, you might exit or have a fallback.
        # For this environment, we'll proceed, but it will fail at the '/' route.

    logger.info("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=8080)
