from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import google.generativeai as genai
import json
import sqlite3
from sqlite3 import Error
import os
import random
from roadmap import parse_roadmap
# import redis 


app = Flask(__name__)
CORS(app)
load_dotenv() 

# Configure the Gemini API
genai.configure(api_key=os.getenv('key'))

# redis_client = redis.from_url(
#     os.environ.get('REDIS_URL'),
#     ssl=True
# )

def load_prompt():
    with open('prompt.txt', 'r') as file:
        return file.read()

def parse_llm_response(response):
    try:
        cleaned_response = response.strip("```json").strip("```").strip()
        print(f"Cleaned response: {cleaned_response}")
        
        return json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        return {"error": "Failed to parse LLM response as JSON"}


@app.route('/api/learn', methods=['GET'])
def learn_topic():
    topic = request.args.get('topic', '')
    if not topic:
        return jsonify({"error": "No topic provided"}), 400

    try:
        prompt_template = load_prompt()
        full_prompt = (
            topic + prompt_template + 
            "Remember do add edges to the generated json structure"
        )

        # cached_data = redis_client.get(full_prompt)
        # if cached_data:
        #     return jsonify(json.loads(cached_data) )

        attempt = 0
        max_attempts = 4
        model = genai.GenerativeModel('gemini-2.0-flash')
        parsed_response = None
        while attempt < max_attempts:
            print(f"Attempt {attempt}")
            resp = model.generate_content(full_prompt)
            parsed_response = parse_llm_response(resp.text or "")
            print(f"Parsed response: {parsed_response}, Type: {type(parsed_response)}")
            if isinstance(parsed_response, dict) and 'error' not in parsed_response:
                break
            attempt += 1

        if attempt == max_attempts:
            return jsonify({"error": "json not proper"}), 500
        if 'topic' not in parsed_response or 'levels' not in parsed_response:
            return jsonify({"error": "Invalid response structure from LLM"}), 500

        print(parsed_response)
        # redis_client.set(full_prompt, json.dumps(parsed_response) )
        return jsonify(parsed_response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/expand_node', methods=['POST'])
def expand_node():
    print(request.json)
    data = request.get_json(silent=True) or {}
    topic = data.get('topic')
    node_id = data.get('node_id')
    title = data.get('title')
    content = data.get('content')

    if not all([topic, node_id, title, content]):
        return jsonify({"error": "Missing required parameters"}), 400

    text = f"{topic} {node_id} {content}"
    print(title)
    print(text)



    # inputs are already validated above
        
    def get_node_context():
        pass
    

    def generate():
        try:
            
            model = genai.GenerativeModel('gemini-2.0-flash')

            prompt = f"""
            Efficiently explain the following topic in the context of {topic} in markdown:

            Title: {title}
            Brief description: {content}
            markdown format
            Provide a clear and concise explanation that anyone can understand and implement (if relevant). 
            Include key concepts, practical applications, and any important considerations.
            If applicable, provide a simple example or implementation steps.
            leave proper spaces too between paras so its readable
            critical: respond solely in markdown format not anything else
            markdown format
            """
            response = model.generate_content(prompt, stream=True)
            yield json.dumps({"content": content + "\n"}) + "\n" 

            for chunk in response:
                if chunk.text:
                    yield json.dumps({"content": chunk.text}) + "\n"    
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    return Response(stream_with_context(generate()), content_type='application/json')

@app.route('/api/node_question', methods=['POST'])
def node_question():
    data = request.json
    topic = data.get('topic')
    node_id = data.get('node_id')
    question = data.get('question')
    context = data.get('context')

    if not all([topic, node_id, question, context]):
        return jsonify({"error": "Missing required parameters"}), 400


    try:
        
        
        context += f"\nUser: {question}\nAssistant:"

        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(context)
        answer = response.text

        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/roadmap/mermaid', methods=['POST'])
def roadmap_mermaid():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        graph = payload.get('graph') if isinstance(payload, dict) and 'graph' in payload else payload

        # Accept either an object or a JSON string for `graph`
        if isinstance(graph, str):
            try:
                graph = json.loads(graph)
            except Exception:
                return jsonify({"error": "Invalid JSON string provided in 'graph'"}), 400

        if not isinstance(graph, dict):
            return jsonify({"error": "Body must be a JSON object or contain a 'graph' object"}), 400

        mermaid = parse_roadmap({"graph": graph})
        if not mermaid:
            return jsonify({"error": "Failed to generate mermaid"}), 400
        return jsonify({"mermaid": mermaid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
