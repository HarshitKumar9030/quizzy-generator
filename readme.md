# Quizzy Quiz Generator

An application that generates quizzes from images using OCR and GPT technology. This project supports both single and multiple images, extracting text from the images and generating quizzes based on the content.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Single Image](#single-image)
  - [Multiple Images](#multiple-images)
- [Test Files](#test-files)
- [Contributing](#contributing)
- [License](#license)
- [Authors](#authors)

---

## Features

- Extract text from images using OCR (Tesseract)
- Generate quizzes using GPT models
- Support for both single and multiple image inputs
- Customizable quiz parameters (difficulty, time range, number of questions)
- Returns quizzes in JSON format
- Shuffle questions to cover a broad range of topics when data is extensive

---

## Requirements

- Python 3.6+
- Required Python packages (see `requirements.txt`)
- Tesseract OCR installed on your system
- Access to GPT models via `g4f` library

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/quizzy.git
   cd quizzy
   ```

2. **Install required Python packages:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR:**

   - **Windows:** Download and install from [here](https://github.com/tesseract-ocr/tesseract)
   - **macOS:** Install via Homebrew:
     ```bash
     brew install tesseract
     ```
   - **Linux:** Install via package manager:
     ```bash
     sudo apt-get install tesseract-ocr
     ```

## Usage

### Single Image

- **Code Location:** `./main.py`

#### Running the Application

```bash
python main.py
```

This will start the server on `http://0.0.0.0:5000`.

#### API Endpoint

- **URL:** `http://localhost:5000/generate-quiz`
- **Method:** `POST`
- **Form Data:**
  - `image`: The image file to upload.
  - `difficulty` (optional): Quiz difficulty level (easy, medium, hard). Default is easy.
  - `time_range` (optional): Time range in minutes. Default is 30.
  - `num_questions` (optional): Number of questions. Default is 10.

#### Example Request

```python
import requests

url = 'http://localhost:5000/generate-quiz'
files = {'image': open('path/to/your/image.jpg', 'rb')}
data = {
    'difficulty': 'easy',
    'time_range': '30',
    'num_questions': '10'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### Multiple Images

- **Code Location:** `./scripts/multi_image.py`

#### Running the Application

```bash
python scripts/multi_image.py
```

This will start the server on `http://0.0.0.0:5000`.

#### API Endpoint

- **URL:** `http://localhost:5000/generate-quiz`
- **Method:** `POST`
- **Form Data:**
  - `images`: The image files to upload (multiple files).
  - `difficulty` (optional): Quiz difficulty level (easy, medium, hard, ultra hard). Default is easy.
  - `time_range` (optional): Time range in minutes. Default is 30.
  - `num_questions` (optional): Number of questions. Default is 10.

#### Example Request

```python
import requests

url = 'http://localhost:5000/generate-quiz'
image_paths = ['path/to/your/image1.jpg', 'path/to/your/image2.jpg']
files = []
for image_path in image_paths:
    files.append(('images', (image_path, open(image_path, 'rb'), 'image/jpeg')))
data = {
    'difficulty': 'easy',
    'time_range': '30',
    'num_questions': '10'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## Test Files

Test files are located in the `./tests` directory. These doesn't include sample images, only the scripts to test the API endpoints.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License.

## Authors

- Harshit - [leoncyriac.me](https://leoncyriac.me)

*Note: This project was made for Quizzy.*
