"""
Image Captioning Web Interface using BLIP and Gradio.

This script sets up a Gradio web interface that utilizes the Salesforce BLIP 
(Bootstrapped Language-Image Pre-training) model to generate captions for 
uploaded images.
"""
import gradio as gr
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Load model and processor globally to ensure they are loaded only once.
# Using the "base" version of the BLIP model for a balance of speed and accuracy.
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


def caption_image(image: Image.Image) -> str:
    """
    Process a PIL Image to generate a descriptive caption using the BLIP model.

    Args:
        image (PIL.Image.Image): The input image object to be analyzed.

    Returns:
        str: The predicted text caption for the image. Returns an error message 
             string if an exception occurs during processing.
    """
    try:
        inputs = processor(images=image, return_tensors="pt")
        outputs = model.generate(**inputs)
        caption = processor.decode(outputs[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        return f"An error occurred: {e}"


def main() -> None:
    """
    Initializes and launches the Gradio interface for image captioning.
    
    The interface accepts an image file input and outputs the generated text.
    It runs locally on 127.0.0.1 at port 7860.
    """
    iface = gr.Interface(
        fn=caption_image,
        inputs=gr.Image(type="pil"),
        outputs="text",
        title="Image Captioning with BLIP",
        description="Upload an image to generate a caption using the Salesforce BLIP model."
    )

    iface.launch(server_name="127.0.0.1", server_port=7860)


if __name__ == "__main__":
    main()
