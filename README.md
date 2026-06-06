# Stock Price Web Application

This project is a stock price web application that allows users to search for stock information and view current data along with predictions for future prices. The application is built with a frontend using HTML, CSS, and JavaScript, and a backend using Python with Flask.

## Project Structure

```
stock-price-web-app
├── frontend
│   ├── index.html       # Main HTML document for the web application
│   ├── styles.css       # CSS styles for the frontend
│   └── script.js        # JavaScript code for handling user interactions
├── backend
│   ├── app.py           # Main entry point for the backend application
│   ├── model.py         # Implementation of the linear regression model
│   └── requirements.txt  # Python dependencies for the backend
└── README.md            # Documentation for the project
```

## Setup Instructions

### Frontend

1. Navigate to the `frontend` directory.
2. Open `index.html` in a web browser to view the application.

### Backend

1. Navigate to the `backend` directory.
2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the backend application:
   ```
   python app.py
   ```

## Usage Guidelines

- Use the search bar on the homepage to enter a stock symbol. As you type, search recommendations will appear.
- Upon submitting a search, the application will display the current stock data and predictions for the next day and week.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.