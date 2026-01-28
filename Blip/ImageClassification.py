"""
Gradio Image Classification Interface.

This script sets up a web interface using Gradio for image classification.
It uses a pre-trained ResNet-18 model from PyTorch to classify images uploaded
by the user into one of 1000 ImageNet categories.

Usage:
    Run the script to launch a local web server. Upload an image via the UI
    to view the top 3 classification predictions.
"""
import torch
import requests
from PIL import Image
from torchvision import transforms
import gradio as gr

# Load pre-trained ResNet-18 model and set to evaluation mode.
model = torch.hub.load('pytorch/vision:v0.6.0', 'resnet18', pretrained=True).eval()

# Download human-readable labels for ImageNet classes.
response = requests.get("https://git.io/JJkYN")
labels = response.text.split("\n")

def predict(inp):
    """Predicts the class probabilities of an input image.

    Args:
        inp (PIL.Image.Image): The input image to be classified.

    Returns:
        dict: A dictionary mapping all 1000 ImageNet labels to their 
              corresponding confidence probabilities.
    """
    inp = transforms.ToTensor()(inp).unsqueeze(0)
    with torch.no_grad():
        prediction = torch.nn.functional.softmax(model(inp)[0], dim=0)
        confidences = {labels[i]: float(prediction[i]) for i in range(1000)}
        return confidences

def main():
    """Configures and launches the Gradio interface."""
    
    # Create the Gradio interface.
    # Inputs: Image upload (type="pil" ensures compatibility with transforms).
    # Outputs: Label display showing the top 3 most likely classes.
    interface = gr.Interface(
        fn=predict,
        inputs=gr.Image(type="pil"),
        outputs=gr.Label(num_top_classes=3),
        title="Image Classification with BLIP",
        examples=["bird.jpg", "house.jpg"]
    )
    
    # Launch the interface.
    interface.launch()

if __name__ == "__main__":
    main()
