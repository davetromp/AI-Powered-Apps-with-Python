# Import required libraries for natural language processing tasks
from transformers import AutoTokenizer, AutoModelForCausalLM

def main():
    # Set default model name to "unsloth/Llama-3.2-1B-Instruct" which was used in one run (initialization and reference local installation)
    model_name = "unsloth/Llama-3.2-1B-Instruct"

    # Load pre-trained model and tokenizer for sequence-to-sequence task using the specified model
    # Use pre-trained tokenizer to utilize saved weights
    # The `from_pretrained` method is used twice to download the model on first run and reference local installation for subsequent runs
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Initialize an empty list to store messages, which keeps track of message history
    messages = []

    while True:
        try:
            # Get the input data from the user
            input_text = input("> ")

            message = {"role": "user", "content": input_text}
            messages.append(message)

            # Tokenize the messages
            inputs = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(model.device)

            # Generate the response from the model
            outputs = model.generate(**inputs, max_new_tokens=4096)

            # Decode the response
            response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:]).replace("<|eot_id|>", "")

            print(response)

            # Add response to messages
            messages.append({"role" : "chatbot", "content" : response})

        except KeyboardInterrupt:
            # Handle Ctrl+C
            print("\nExiting due to keyboard interrupt.")
            break

# Run main function when script is executed directly
if __name__ == "__main__":
    main()