import google.generativeai as genai
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
# Set your API key for Google Generative AI
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Initialize the model
model = genai.GenerativeModel("models/gemini-pro")
# app
app = Flask(__name__)
# Store chats in memory (or use a database for persistence in production)
chats = [{'name': 'New Chat', 'id': 1, 'messages': []}]  # Default first chat
# Route to render the main page

def AIResponse(prompt, chat_history=None):

    # If there is any chat history, append it to the current prompt
    if chat_history:
        context = "\n".join(
            [f"User: {msg['text']}" if msg['text'].startswith('User') else f"AI: {msg['text']}" for msg in
             chat_history])
        prompt = f"{context}\nUser: {prompt}\nAI:"

    # Generate the AI response
    response = model.generate_content(prompt)

    # Return only the new AI response
    return response.text



@app.route('/')
def index():
    return render_template('index.html')

@app.route("/get_chats",methods=['GET'])
def get_chats():
    return jsonify({'chats':chats})

@app.route("/get_chat_history",methods=['GET'])
def get_chat_history():
    chat_id = int(request.args.get('chat_id'))
    chat = next((chat for chat in chats if chat['id']==chat_id),None)
    if chat:
        return jsonify({'messages': chat['messages']})
    return jsonify({'messages':[]})

# Updated route for generating AI responses
@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    user_input = data.get('input')
    chat_id = data.get('chat_id')

    # Find the relevant chat and get the chat history
    chat = next((chat for chat in chats if chat['id'] == chat_id), None)
    chat_history = chat['messages'] if chat else []

    # Generate the AI response with context
    response = AIResponse(user_input, chat_history)

    # Append user input and AI response to the chat history
    if chat:
        chat['messages'].append({'text': f'User: {user_input}'})
        chat['messages'].append({'text': f'AI: {response}'})

    return jsonify({'response': response})




# Route to create a new chat
@app.route('/new_chat', methods=['POST'])
def new_chat():
    data = request.get_json()
    chat_name = data.get('chat_name')
    new_chat_id = len(chats) + 1
    new_chat = {'name': chat_name, 'id': new_chat_id, 'messages': []}
    chats.append(new_chat)
    return jsonify({'status': 'Chat created successfully', 'chat_id': new_chat_id})

# Route to delete a chat
@app.route('/delete_chat', methods=['POST'])
def delete_chat():
    data = request.get_json()
    chat_id = data.get('chat_id')
    global chats
    chats = [chat for chat in chats if chat['id'] != chat_id]
    return jsonify({'status': f'Chat {chat_id} deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)