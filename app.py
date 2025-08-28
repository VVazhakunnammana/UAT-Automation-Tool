from flask import Flask, request, jsonify, render_template_string, send_file, abort
from flask_cors import CORS
import os
import subprocess
import pandas as pd
import time
from datetime import datetime
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload and output directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs('tests', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main HTML page"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "index.html not found. Please ensure the file exists in the same directory.", 404

@app.route('/styles.css')
def styles():
    """Serve the CSS file"""
    try:
        with open('styles.css', 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/css'}
    except FileNotFoundError:
        return "styles.css not found", 404

@app.route('/script.js')
def script():
    """Serve the JavaScript file"""
    try:
        with open('script.js', 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "script.js not found", 404

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only .xlsx and .xls files are allowed'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Try to read and validate the Excel file
        try:
            df = pd.read_excel(filepath)
            preview = {
                'filename': filename,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist()[:10],  # First 10 columns
                'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
            }
        except Exception as e:
            # Clean up uploaded file if it can't be read
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Invalid Excel file: {str(e)}'}), 400
        
        # Store the current file path for testing
        with open('current_file.txt', 'w') as f:
            f.write(filepath)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'filepath': filepath,
            'preview': preview
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/run-tests', methods=['POST'])
def run_tests():
    """Run pytest scripts"""
    try:
        # Check if a file has been uploaded
        if not os.path.exists('current_file.txt'):
            return jsonify({'error': 'No file uploaded. Please upload a file first.'}), 400
        
        with open('current_file.txt', 'r') as f:
            current_file = f.read().strip()
        
        if not os.path.exists(current_file):
            return jsonify({'error': 'Uploaded file not found. Please upload a file again.'}), 400
        
        # Create a simple test file if it doesn't exist
        test_file = 'tests/test_grading.py'
        if not os.path.exists(test_file):
            create_sample_test_file(test_file, current_file)
        
        # Record start time
        start_time = time.time()
        
        # Run pytest
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', test_file, '-v', '--tb=short', '-n=auto'],
                capture_output=True,
                text=True,
                timeout=3600  # 60 minute timeout
            )
            
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            
            # Parse test results
            success = result.returncode == 0
            
            # Generate summary
            test_summary = generate_test_summary(result.stdout, result.stderr, success)
            
            return jsonify({
                'success': success,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': duration,
                'test_summary': test_summary,
                'file_tested': current_file
            }), 200
            
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Test execution timed out (60s limit)'}), 500
        except FileNotFoundError:
            return jsonify({'error': 'pytest not found. Please install pytest: pip install pytest'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Test execution failed: {str(e)}'}), 500

def create_sample_test_file(test_file, excel_file):
    """Create a sample pytest file for testing Excel files"""
    test_content = f'''
import pytest
import pandas as pd
import os

EXCEL_FILE = r"{excel_file}"

class TestExcelFile:
    """Test cases for the uploaded Excel file"""
    
    def test_file_exists(self):
        """Test that the Excel file exists"""
        assert os.path.exists(EXCEL_FILE), f"Excel file does not exist: {{EXCEL_FILE}}"
    
    def test_file_readable(self):
        """Test that the Excel file can be read"""
        try:
            df = pd.read_excel(EXCEL_FILE)
            assert df is not None, "Failed to read Excel file"
        except Exception as e:
            pytest.fail(f"Could not read Excel file: {{e}}")
    
    def test_file_not_empty(self):
        """Test that the Excel file is not empty"""
        df = pd.read_excel(EXCEL_FILE)
        assert len(df) > 0, "Excel file is empty (no data rows)"
        assert len(df.columns) > 0, "Excel file has no columns"
    
    def test_data_integrity(self):
        """Test basic data integrity"""
        df = pd.read_excel(EXCEL_FILE)
        
        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        
        # Check for completely empty rows
        empty_rows = df.isnull().all(axis=1).sum()
        
        # Log findings (these are warnings, not failures)
        if duplicate_count > 0:
            print(f"Warning: Found {{duplicate_count}} duplicate rows")
        
        if empty_rows > 0:
            print(f"Warning: Found {{empty_rows}} completely empty rows")
        
        # This test passes but logs warnings
        assert True, f"Data integrity check completed. Duplicates: {{duplicate_count}}, Empty rows: {{empty_rows}}"
    
    def test_column_headers(self):
        """Test that columns have proper headers"""
        df = pd.read_excel(EXCEL_FILE)
        
        # Check for unnamed columns
        unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed:')]
        
        if unnamed_cols:
            print(f"Warning: Found unnamed columns: {{unnamed_cols}}")
        
        # Test passes if we have at least one properly named column
        named_cols = [col for col in df.columns if not str(col).startswith('Unnamed:')]
        assert len(named_cols) > 0, "No properly named columns found"
    
    def test_data_types(self):
        """Test data types in the Excel file"""
        df = pd.read_excel(EXCEL_FILE)
        
        # Get info about data types
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        
        print(f"Numeric columns: {{len(numeric_cols)}}")
        print(f"Text columns: {{len(text_cols)}}")
        print(f"Date columns: {{len(date_cols)}}")
        
        # Test passes if we have any recognizable data types
        total_typed_cols = len(numeric_cols) + len(text_cols) + len(date_cols)
        assert total_typed_cols > 0, "No recognizable data types found"

def test_file_summary():
    """Generate a summary of the Excel file"""
    df = pd.read_excel(EXCEL_FILE)
    
    print("\\n" + "="*50)
    print("EXCEL FILE SUMMARY")
    print("="*50)
    print(f"File: {{os.path.basename(EXCEL_FILE)}}")
    print(f"Rows: {{len(df)}}")
    print(f"Columns: {{len(df.columns)}}")
    print(f"Size: {{df.shape}}")
    print("\\nColumn Names:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {{i}}. {{col}}")
    
    if len(df) > 0:
        print("\\nFirst few rows:")
        print(df.head(3).to_string())
    
    print("="*50)
'''
    
    with open(test_file, 'w') as f:
        f.write(test_content)

def generate_test_summary(stdout, stderr, success):
    """Generate a human-readable test summary"""
    summary = []
    
    if success:
        summary.append("✅ All tests passed successfully!")
    else:
        summary.append("❌ Some tests failed.")
    
    # Extract test results from stdout
    lines = stdout.split('\n')
    test_results = []
    
    for line in lines:
        if '::' in line and ('PASSED' in line or 'FAILED' in line):
            test_results.append(line.strip())
    
    if test_results:
        summary.append("\nTest Results:")
        for result in test_results:
            summary.append(f"  {result}")
    
    # Count passed/failed
    passed_count = stdout.count('PASSED')
    failed_count = stdout.count('FAILED')
    
    summary.append(f"\nTotal: {passed_count + failed_count} tests")
    summary.append(f"Passed: {passed_count}")
    summary.append(f"Failed: {failed_count}")
    
    return '\n'.join(summary)

@app.route('/list-output-files', methods=['GET'])
def list_output_files():
    """List all files in the output directory"""
    try:
        output_dir = app.config['OUTPUT_FOLDER']
        if not os.path.exists(output_dir):
            return jsonify({'files': []}), 200
        
        files = []
        for filename in os.listdir(output_dir):
            if filename.lower().endswith(('.xlsx', '.xls', '.csv', '.txt', '.json', '.xml')):
                filepath = os.path.join(output_dir, filename)
                file_stat = os.stat(filepath)
                files.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'download_url': f'/download-output/{filename}'
                })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to list output files: {str(e)}'}), 500

@app.route('/download-output/<filename>', methods=['GET'])
def download_output_file(filename):
    """Download a file from the output directory"""
    try:
        # Secure the filename to prevent directory traversal
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            abort(404, description="File not found")
        
        # Check if it's actually a file (not a directory)
        if not os.path.isfile(filepath):
            abort(404, description="File not found")
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        abort(500, description=f"Download failed: {str(e)}")

# @app.route('/create-sample-output', methods=['POST'])
# def create_sample_output():
#     """Create a sample output file for demonstration"""
#     try:
#         # Get the current uploaded file info
#         if not os.path.exists('current_file.txt'):
#             return jsonify({'error': 'No file uploaded. Please upload a file first.'}), 400
        
#         with open('current_file.txt', 'r') as f:
#             current_file = f.read().strip()
        
#         if not os.path.exists(current_file):
#             return jsonify({'error': 'Uploaded file not found.'}), 400
        
#         # Read the uploaded Excel file
#         df = pd.read_excel(current_file)
        
#         # Create a processed version with some analysis
#         analysis_data = {
#             'File Analysis': [
#                 f'Original filename: {os.path.basename(current_file)}',
#                 f'Total rows: {len(df)}',
#                 f'Total columns: {len(df.columns)}',
#                 f'Analysis date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
#             ],
#             'Column Summary': [
#                 f'Numeric columns: {len(df.select_dtypes(include=["number"]).columns)}',
#                 f'Text columns: {len(df.select_dtypes(include=["object"]).columns)}',
#                 f'Date columns: {len(df.select_dtypes(include=["datetime"]).columns)}',
#                 f'Total data points: {df.size}'
#             ],
#             'Data Quality': [
#                 f'Missing values: {df.isnull().sum().sum()}',
#                 f'Duplicate rows: {df.duplicated().sum()}',
#                 f'Empty rows: {df.isnull().all(axis=1).sum()}',
#                 f'Completeness: {((df.size - df.isnull().sum().sum()) / df.size * 100):.1f}%'
#             ]
#         }
        
#         # Create analysis DataFrame
#         analysis_df = pd.DataFrame.from_dict(analysis_data, orient='index').T
        
#         # Generate output filename
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         output_filename = f"analysis_result_{timestamp}.xlsx"
#         output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
#         # Create Excel file with multiple sheets
#         with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
#             # Analysis summary sheet
#             analysis_df.to_excel(writer, sheet_name='Analysis_Summary', index=False)
            
#             # Original data (first 1000 rows to avoid large files)
#             df_sample = df.head(1000) if len(df) > 1000 else df
#             df_sample.to_excel(writer, sheet_name='Data_Sample', index=False)
            
#             # Column information
#             col_info = pd.DataFrame({
#                 'Column_Name': df.columns,
#                 'Data_Type': df.dtypes.astype(str),
#                 'Non_Null_Count': df.count(),
#                 'Null_Count': df.isnull().sum(),
#                 'Unique_Values': df.nunique()
#             })
#             col_info.to_excel(writer, sheet_name='Column_Info', index=False)
        
#         return jsonify({
#             'message': 'Sample output file created successfully',
#             'filename': output_filename,
#             'download_url': f'/download-output/{output_filename}',
#             'size': os.path.getsize(output_path)
#         }), 200
        
#     except Exception as e:
#         return jsonify({'error': f'Failed to create sample output: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Excel Upload & Test Runner Server...")
    print("Server will be available at: http://localhost:5000")
    print("Make sure you have the required packages installed:")
    print("  pip install flask flask-cors pandas openpyxl pytest")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
