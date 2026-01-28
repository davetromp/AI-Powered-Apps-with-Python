import os
import glob
from typing import List
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration


def load_model() -> tuple[BlipProcessor, BlipForConditionalGeneration]:
    """
    Load the pretrained BLIP processor and model for image captioning.
    
    Returns:
        tuple: The processor and model instances.
    """
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model


def get_image_paths(directory: str, extensions: List[str]) -> List[str]:
    """
    Get all image file paths from a directory matching the given extensions.
    
    Args:
        directory: The directory to search for images.
        extensions: List of image file extensions to include.
        
    Returns:
        List[str]: List of image file paths.
    """
    image_paths = []
    for ext in extensions:
        image_paths.extend(glob.glob(os.path.join(directory, f"*.{ext}")))
    return image_paths


def generate_caption(
    image: Image.Image,
    processor: BlipProcessor,
    model: BlipForConditionalGeneration,
    max_new_tokens: int = 50
) -> str:
    """
    Generate a caption for the given image using the BLIP model.
    
    Args:
        image: The input PIL Image.
        processor: The BLIP processor instance.
        model: The BLIP model instance.
        max_new_tokens: Maximum number of tokens to generate.
        
    Returns:
        str: The generated image caption.
    """
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=max_new_tokens)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption


def process_images(
    image_dir: str,
    output_file: str,
    extensions: List[str] = ["jpg", "jpeg", "png"]
) -> None:
    """
    Process all images in a directory, generate captions, and write to file.
    
    Args:
        image_dir: Directory containing the images to process.
        output_file: Path to the output file for captions.
        extensions: List of image file extensions to process.
    """
    processor, model = load_model()
    image_paths = get_image_paths(image_dir, extensions)
    
    with open(output_file, "w") as caption_file:
        for img_path in image_paths:
            try:
                raw_image = Image.open(img_path).convert("RGB")
                caption = generate_caption(raw_image, processor, model)
                caption_file.write(f"{os.path.basename(img_path)}: {caption}\n")
                print(f"Processed: {os.path.basename(img_path)}")
            except Exception as e:
                print(f"Error processing {img_path}: {e}")


def main() -> None:
    """Main entry point for the image captioning script."""
    image_dir = "/home/dave/Documents/CODE/AI_Powered_Python_Apps/Blip"
    output_file = "localcaptions.txt"
    
    process_images(image_dir, output_file)
    print(f"Captions saved to {output_file}")


if __name__ == "__main__":
    main()
