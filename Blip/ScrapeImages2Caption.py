"""
Web scraper and image caption generator using BLIP model.

When executed, this script:
1. Scrapes all images from BASE_URL
2. Uses the BLIP model to generate captions
3. Saves results to OUTPUT_FILE

Constants:
    MODEL_NAME: HuggingFace model for image captioning
    BASE_URL: Target URL to scrape images from
    HEADERS: User agent for HTTP requests
    MIN_IMAGE_PIXELS: Minimum resolution threshold
    OUTPUT_FILE: Path to save generated captions
    TIMEOUT: HTTP request timeout in seconds
"""

import requests
from io import BytesIO
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from PIL import Image
from transformers import AutoProcessor, BlipForConditionalGeneration

# Constants
MODEL_NAME = "Salesforce/blip-image-captioning-base"
BASE_URL = "https://davetromp.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MIN_IMAGE_PIXELS = 200
OUTPUT_FILE = "captions.txt"
TIMEOUT = 10


def load_model():
    """Load the BLIP model and processor."""
    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME)
    return processor, model


def normalize_url(img_url: str) -> str | None:
    """Convert relative URLs to absolute."""
    if img_url.startswith("//"):
        return "https:" + img_url
    if img_url.startswith("/"):
        return urljoin(BASE_URL, img_url)
    if img_url.startswith("http"):
        return img_url
    return None


def should_skip_url(url: str) -> bool:
    """Check if URL should be skipped (SVGs, invalid formats)."""
    return not url or ".svg" in url


def generate_caption(image_url: str, processor, model) -> str | None:
    """Download image and generate caption."""
    try:
        response = requests.get(image_url, timeout=TIMEOUT, headers=HEADERS)
        raw_image = Image.open(BytesIO(response.content))
        
        if raw_image.size[0] * raw_image.size[1] < MIN_IMAGE_PIXELS:
            return None
        
        inputs = processor(images=raw_image.convert("RGB"), 
                          text="the image of", 
                          return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=50)
        return processor.decode(out[0], skip_special_tokens=True)
        
    except (OSError, requests.RequestException):
        return None


def main():
    processor, model = load_model()
    
    response = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for idx, img in enumerate(soup.find_all('img'), start=1):
            img_url = img.attrs.get('data-src') or img.attrs.get('src', '')
            
            if should_skip_url(img_url):
                continue
            
            img_url = normalize_url(img_url)
            if not img_url:
                continue
            
            caption = generate_caption(img_url, processor, model)
            if caption:
                f.write(f"{img_url}: {caption}\n")
                print(f"[{idx}] Caption saved")


if __name__ == "__main__":
    main()
