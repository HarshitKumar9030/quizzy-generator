import requests
import json

# Endpoint
url = 'http://localhost:5000/generate-quiz'

# Paths to the images you want to upload
image_paths = [
    r'C:\path\to\your\image1.jpg',
    r'C:\path\to\your\image2.jpg',
    # Add more image paths as needed
]

# Prepare the files for uploading
files = []
for image_path in image_paths:
    files.append(('images', (image_path, open(image_path, 'rb'), 'image/jpeg')))

# Prepare form data
data = {
    'difficulty': 'easy',
    'time_range': '30',
    'num_questions': '10'
}

# Send the POST request with streaming enabled
with requests.post(url, files=files, data=data, stream=True) as response:
    if response.status_code == 200:
        content = ''
        for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
            if chunk:
                content += chunk
        # Remove the wrapper to parse the JSON content
        json_content = content.strip()
        quiz_data = json.loads(json_content)
        print(json.dumps(quiz_data, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
