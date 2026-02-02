from flask import Flask, request, render_template
from flask_cors import CORS
import json
from transformers import AutoTokenizer, AutoModelForCausalLM

app = Flask(__name__)
CORS(app)

model_name = "unsloth/Llama-3.2-1B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

messages = []

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/chatbot', methods=['POST'])
def handle_prompt():
    data = request.get_data(as_text=True)
    data = json.loads(data)
    input_text = data['prompt']

    message = {"role": "user", "content": input_text}
    messages.append(message)

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)

    # Generate the response from the model
    outputs = model.generate(**inputs, max_new_tokens=4096)

    # Decode the response and clean it up
    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:]).replace("<|eot_id|>", "")

    # Add interaction to messages
    messages.append({"role" : "chatbot", "content" : response})

    return response

if __name__ == '__main__':
    app.run(debug=True)