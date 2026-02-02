# Chatbot

An AI-powered chatbot application using the unsloth/Llama-3.2-1B-Instruct model. Features conversation history tracking for more contextual responses.

## Model Information

- **Model**: unsloth/Llama-3.2-1B-Instruct
- **Size**: ~1GB download on first run
- **Features**: Conversation history, chat formatting support

## Setup

### Prerequisites
Install dependencies:
```bash
pip install -r requirements.txt
```

### Command Line Version

Run the chatbot in your terminal:
```bash
python chatbot.py
```

Type your messages and press Enter. Press Ctrl+C to exit.

### Web Browser Version

Launch the Flask web application:
```bash
cd ./LLM_application_chatbot
flask run
```

Open your browser and navigate to: http://127.0.0.1:5000/

## Usage Examples

### CLI Example
```
> What is Python?
Python is a high-level, interpreted programming language known for its readability and versatility...

> Can you give me an example?
Sure! Here's a simple Python example:
print("Hello, World!")

[Press Ctrl+C to exit]
```

### Web Interface
1. Open http://127.0.0.1:5000/
2. Type your question in the input field
3. Click Send or press Enter
4. View the chatbot's response in the conversation history

## Screenshots

### Command Line Chatbot
![CLI Chatbot](screenshots/Screenshot-chatbot-terminal.png)

### Web Browser Chatbot
![Web Chatbot](screenshots/Screenshot-chatbot.png)

## Credits

Frontend interface reused from: https://github.com/ibm-developer-skills-network/LLM_application_chatbot