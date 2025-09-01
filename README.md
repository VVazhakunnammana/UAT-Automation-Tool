# Excel Upload & Pytest Runner

A web application that allows users to upload Excel files and run automated pytest scripts to validate the uploaded data.

## Features

- **Modern Web Interface**: Clean, responsive UI built with HTML, CSS, and JavaScript
- **File Upload**: Drag-and-drop or browse to upload Excel files (.xlsx, .xls)
- **Automated Testing**: Runs pytest scripts automatically on uploaded files
- **Real-time Results**: View test results and status in real-time
- **Data Validation**: Built-in tests for file integrity, data types, and structure

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- Modern web browser

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## Usage

1. **Upload Excel File:**
   - Click "Browse Files" or drag and drop an Excel file (.xlsx or .xls)
   - The application will validate the file format

2. **Upload to Server:**
   - Click "Upload File" to send the file to the server
   - The system will process and validate the Excel file

3. **Run Tests:**
   - Click "Run Tests" to execute the pytest scripts
   - View real-time test results and status

## Test Features

The application automatically creates and runs the following tests:

- **File Existence**: Verifies the uploaded file exists and is accessible
- **File Readability**: Ensures the Excel file can be properly read
- **Data Integrity**: Checks for empty rows, duplicates, and data quality
- **Column Headers**: Validates proper column naming
- **Data Types**: Analyzes numeric, text, and date columns
- **File Summary**: Provides detailed information about the Excel structure

## File Structure

```
ui_uat_test/
├── app.py              # Flask backend server
├── index.html          # Main web interface
├── styles.css          # UI styling
├── script.js           # Frontend JavaScript
├── requirements.txt    # Python dependencies
├── uploads/            # Directory for uploaded files (created automatically)
└── README.md          # This file
```

## API Endpoints

- `GET /` - Serves the main web interface
- `POST /upload` - Handles file uploads
- `POST /run-tests` - Executes pytest scripts
- `GET /styles.css` - Serves CSS file
- `GET /script.js` - Serves JavaScript file

## Customization

### Adding Custom Tests

You can modify the `create_sample_test_file()` function in `app.py` to add your own pytest test cases. The function generates a Python test file that will be executed when users click "Run Tests".

### Modifying UI

- Edit `styles.css` for visual changes
- Modify `script.js` for functionality changes
- Update `index.html` for structure changes

## Error Handling

The application includes comprehensive error handling for:
- Invalid file formats
- Large file sizes (16MB limit)
- Missing dependencies
- Test execution timeouts
- Network errors

## Security Features

- File type validation
- Secure filename handling
- File size limits
- Input sanitization

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Troubleshooting

### Common Issues

1. **"pytest not found" error:**
   ```bash
   pip install pytest
   ```

2. **Module import errors:**
   ```bash
   pip install -r requirements.txt
   ```

3. **File upload fails:**
   - Check file format (.xlsx or .xls only)
   - Ensure file size is under 16MB
   - Verify the uploads directory is writable

4. **Tests don't run:**
   - Ensure you've uploaded a file first
   - Check that all dependencies are installed
   - Verify Python is in your system PATH

## Development

To contribute or modify this application:

1. Fork the repository
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).
