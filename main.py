from quart import Quart, request, jsonify, Response
import pytesseract
from PIL import Image
import io
import asyncio

app = Quart(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # upload limit / change to your needs

# Function to extract text using OCR - Tesseract
def extract_text_from_image(image_data):
    try:
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image)
        # print(text)
        return text.strip()
    except Exception as e:
        print(f"Error during text generation (OCR): {e}")
        return None

# generator function ( synchronus )
def generate_quiz_from_text(extracted_text, difficulty, time_range, num_questions):
    # customize prompt according to your needs.
    # PS: even this prompt is AI generated lol
    prompt = f"""
Generate a quiz with {num_questions} questions based on the following content:

{extracted_text}

Include questions of types: MCQ, ONEWORD, ASSERTION_REASONING, TRUE_FALSE.
The difficulty level should be {difficulty} and the time range is {time_range} minutes.
Provide clear and concise questions and answers.

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
            model="gpt-4",
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

# gen wrapper
async def async_generator_wrapper(sync_gen):
    for item in sync_gen:
        yield item
        await asyncio.sleep(0)  # Yield control to the event loop

@app.route('/generate-quiz', methods=['POST'])
async def generate_quiz():
    files = await request.files
    form = await request.form

    if 'image' not in files:
        return jsonify({"error": "No image file provided"}), 400

    image = files['image']
    difficulty = form.get('difficulty', 'easy').lower()
    try:
        time_range = int(form.get('time_range', 30)) # default is 30 minutes
        num_questions = int(form.get('num_questions', 10)) # default is 10 questions if not specified
    except ValueError:
        return jsonify({"error": "Invalid 'time_range' or 'num_questions' value. They must be integers."}), 400

    # Validate difficulty level
    valid_difficulties = ['easy', 'medium', 'hard']
    if difficulty not in valid_difficulties:
        return jsonify({"error": f"Invalid difficulty level. Choose from {valid_difficulties}."}), 400

    # Extract text from image using OCR
    image_data = image.read() # Reading the image
    extracted_text = extract_text_from_image(image_data) # Using pytesseract to get text from image, alternaticely you can use any other cloudvision service or API for example google cloudvision or azure vision. 
    if not extracted_text:
        return jsonify({"error": "Failed to extract text from image."}), 500

    async def stream():
        yield '{"quiz":'
        content = ''
        sync_gen = generate_quiz_from_text(extracted_text, difficulty, time_range, num_questions)
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


# supports single_image
