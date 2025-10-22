# String Analysis API

A RESTful API service built with FastAPI that analyzes strings and stores their computed properties. This service provides comprehensive string analysis including palindrome detection, character frequency mapping, word counting, and more.

## 🚀 Features

- **String Analysis**: Compute various properties of input strings
- **Flexible Querying**: Filter strings by multiple criteria
- **Natural Language Support**: Query strings using natural language
- **SHA256 Hashing**: Unique identification using cryptographic hashing
- **RESTful Design**: Proper HTTP status codes and REST conventions

## 📋 API Endpoints

### 1. Create/Analyze String
- **POST** `/api/v1/strings`
- **Description**: Analyze a string and store its computed properties
- **Request Body**:
  ```json
  {
    "value": "string to analyze"
  }
  ```
- **Success Response**: `201 Created`
- **Error Responses**:
  - `400 Bad Request`: Invalid request body or missing "value" field
  - `409 Conflict`: String already exists in the system
  - `422 Unprocessable Entity`: Invalid data type for "value"

### 2. Get String by Value
- **GET** `/api/v1/strings/{string_value}`
- **Description**: Retrieve stored string analysis by original string value
- **Success Response**: `200 OK`
- **Error Response**: `404 Not Found` if string doesn't exist

### 3. Get All Strings with Filtering
- **GET** `/api/v1/strings`
- **Description**: Retrieve all stored string analyses with optional filters
- **Query Parameters**:
  - `is_palindrome` (boolean): Filter by palindrome status
  - `min_length` (integer): Minimum string length
  - `max_length` (integer): Maximum string length
  - `word_count` (integer): Exact word count
  - `contains_character` (string): Single character to search for
- **Success Response**: `200 OK`
- **Error Response**: `400 Bad Request` for invalid parameters

### 4. Natural Language Filtering
- **GET** `/api/v1/strings/filter-by-natural-language`
- **Description**: Filter strings using natural language queries
- **Query Parameter**: `query` (string)
- **Supported Query Examples**:
  - "all single word palindromic strings" → `word_count=1, is_palindrome=true`
  - "strings longer than 10 characters" → `min_length=11`
  - "palindromic strings that contain the first vowel" → `is_palindrome=true, contains_character=a`
  - "strings containing the letter z" → `contains_character=z`
- **Success Response**: `200 OK`
- **Error Responses**:
  - `400 Bad Request`: Unable to parse natural language query
  - `422 Unprocessable Entity`: Conflicting filters in parsed query

### 5. Delete String
- **DELETE** `/api/v1/strings/{string_value}`
- **Description**: Delete a stored string analysis by original string value
- **Success Response**: `204 No Content` (empty body)
- **Error Response**: `404 Not Found` if string doesn't exist

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### 1. Clone the repository
```bash
git clone https://github.com/Fritz-nvm/HNG-stage-1
cd HNG-stage-1
```

### 2. Create virtual environment
```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
cd app
python3 -m uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## 📊 String Properties Computed

For each analyzed string, the API computes and stores:

- **length**: Number of characters in the string
- **is_palindrome**: Boolean indicating if the string reads the same forwards and backwards (case-insensitive)
- **unique_characters**: Count of distinct characters in the string
- **word_count**: Number of words separated by whitespace
- **sha256_hash**: SHA-256 hash of the string for unique identification
- **character_frequency_map**: Object/dictionary mapping each character to its occurrence count

## 🎯 Usage Examples

### Analyzing a String
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/strings" \
     -H "Content-Type: application/json" \
     -d '{"value": "Hello World"}'
```

### Getting String Analysis
```bash
curl "http://127.0.0.1:8000/api/v1/strings/Hello%20World"
```

### Filtering Strings
```bash
# Get all palindromes
curl "http://127.0.0.1:8000/api/v1/strings?is_palindrome=true"

# Get strings between 5-20 characters
curl "http://127.0.0.1:8000/api/v1/strings?min_length=5&max_length=20"

# Natural language query
curl "http://127.0.0.1:8000/api/v1/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings"
```

### Deleting a String
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/strings/Hello%20World"
```

## 🗂️ Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── api/
│   └── routes.py          # API route definitions
├── application/
│   ├── services.py        # Business logic and string analysis
│   └── natural_language_parser.py  # NLP query processing
└── infrastructure/
    ├── models.py          # Pydantic models and database schemas
    └── database.py        # Database configuration
```

## 🔧 Configuration

The application uses SQLite by default for data storage. The database file (`string_analysis.db`) will be created automatically in the application directory.

To use a different database (PostgreSQL, MySQL), update the connection string in `infrastructure/database.py`.

## 📚 API Documentation

Once the application is running, you can access:

- **Interactive API Docs**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc

## 🧪 Testing

Test the API using the interactive Swagger documentation at `/docs` or using curl commands as shown in the examples above.
   ```

## 🐛 Error Handling

The API provides comprehensive error handling with appropriate HTTP status codes:

- `400 Bad Request`: Invalid input parameters
- `404 Not Found`: Resource not found
- `409 Conflict`: Duplicate resource creation attempt
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server-side issues

## 📄 License

This project is part of the HNG Internship program.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
