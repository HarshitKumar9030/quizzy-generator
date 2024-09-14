import requests
import json

url = 'http://localhost:5000/generate-quiz'

files = {'image': open(r'C:\Users\kei\Downloads\1715080221522.jpg', 'rb')} # Your image path
data = {
    'difficulty': 'easy',
    'time_range': '30',
    'num_questions': '10'
}

with requests.post(url, files=files, data=data, stream=True) as response:
    response.raise_for_status()
    content = ''
    for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
        if chunk:
            content += chunk
    # JSON response
    quiz_data = json.loads(content)
    print(json.dumps(quiz_data, indent=2))
