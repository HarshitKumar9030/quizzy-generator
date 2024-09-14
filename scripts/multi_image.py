from quart import Quart, request, jsonify, Response
import pytesseract
from PIL import Image
import io
import asyncio

app = Quart(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Adjust upload limit as needed

# Function to extract text using OCR - Tesseract
def extract_text_from_image(image_data):
    try:
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"Error during text extraction (OCR): {e}")
        return None

# Generator function (synchronous)
def generate_quiz_from_text(extracted_text, difficulty, time_range, num_questions):
    # Updated prompt to instruct GPT to shuffle between the data
    prompt = f"""
Generate a quiz with {num_questions} questions based on the following content:

{extracted_text}

Include questions of types: MCQ, ONEWORD, ASSERTION_REASONING, TRUE_FALSE.
The difficulty level should be {difficulty} and the time range is {time_range} minutes.
Provide clear and concise questions and answers.

If the content is extensive and the number of requested questions is less than what can be created from the content, please shuffle between different parts of the content to create questions that cover a broad range of topics.

Return the quiz in JSON format with the following structure:
{{
  "questions": [
    {{
      "question": "Question text",
      "type": "MCQ/ONEWORD/ASSERTION_REASONING/TRUE_FALSE",
      "options": ["Option1", "Option2", "Option3", "Option4"],  # Include only for MCQ
      "answer": "Correct answer or explanation"
    }},
    ...
  ]
}}
Ensure that the JSON output is valid and parsable. Do not include any explanations or extra text outside the JSON structure.
"""
    try:
        from g4f import ChatCompletion

        # Create the chat completion with streaming
        response = ChatCompletion.create(
            model="gpt-4", #gpt-4= for best experience ifykyk
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            stream=True,
        )

        # Iterate over the response, which yields strings
        for chunk in response:
            if chunk:
                yield chunk

    except Exception as e:
        print(f"Error during quiz generation: {e}")
        yield ""

# Asynchronous generator wrapper
async def async_generator_wrapper(sync_gen):
    for item in sync_gen:
        yield item
        await asyncio.sleep(0)  # Yield control to the event loop

@app.route('/generate-quiz', methods=['POST'])
async def generate_quiz():
    files = await request.files
    form = await request.form

    # Get all uploaded images
    images = files.getlist('images')
    if not images:
        return jsonify({"error": "No images provided"}), 400

    difficulty = form.get('difficulty', 'easy').lower()
    try:
        time_range = int(form.get('time_range', 30))  # Default is 30 minutes
        num_questions = int(form.get('num_questions', 10))  # Default is 10 questions if not specified
    except ValueError:
        return jsonify({"error": "Invalid 'time_range' or 'num_questions' value. They must be integers."}), 400

    # Validate difficulty level
    valid_difficulties = ['easy', 'medium', 'hard', 'ultra hard']
    if difficulty not in valid_difficulties:
        return jsonify({"error": f"Invalid difficulty level. Choose from {valid_difficulties}."}), 400

    # Extract text from each image and combine
    combined_text = ''
    for image in images:
        image_data = image.read()  # Reading the image
        extracted_text = extract_text_from_image(image_data)
        if not extracted_text:
            return jsonify({"error": f"Failed to extract text from image '{image.filename}'."}), 500
        combined_text += extracted_text + '\n'

    async def stream():
        yield '{"quiz":'
        content = ''
        sync_gen = generate_quiz_from_text(combined_text, difficulty, time_range, num_questions)
        gen = async_generator_wrapper(sync_gen)

        async for chunk in gen:
            content += chunk
            yield chunk

        yield '}'

    return Response(stream(), content_type='application/json')

if __name__ == "__main__":
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    app.run(host='0.0.0.0', port=5000)

# May throw some warnings while the request is getting processed, but that is completely fine
# Use this for multi image