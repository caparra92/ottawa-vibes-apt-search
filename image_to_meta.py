import os
import base64
import json
import glob
import requests
from pathlib import Path

# === Configuration ===
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Use a vision-capable GPT-4o model that supports Structured Outputs
MODEL = 'gpt-4o-2024-11-20'

# === JSON Schema for Room Photo Description ===
ROOM_SCHEMA = {
    "name": "room_photo_description",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "room_type": {
            "type": "string",
            "enum": [
                "kitchen", "bathroom", "bedroom", "living room",
                "dining room", "home office", "entryway", "laundry room",
                "garage", "basement", "attic", "balcony", "patio", "other"
            ]
            },
            "room_style": {
            "type": "string"
            },
            "dimensions": {
            "type": "object",
            "properties": {
                "width_m":  { "type": "number" },
                "length_m": { "type": "number" },
                "height_m": { "type": "number" }
            },
            "required": ["width_m", "length_m", "height_m"],
            "additionalProperties": False
            },
            "lighting": {
            "type": "object",
            "properties": {
                "natural_light":  { "type": "boolean" },
                "light_sources": {
                "type": "array",
                "items": { "type": "string" }
                },
                "lighting_mood": { "type": "string" }
            },
            "required": ["natural_light", "light_sources", "lighting_mood"],
            "additionalProperties": False
            },
            "flooring":   { "type": "string" },
            "wall_color": { "type": "string" },
            "features": {
            "type": "array",
            "items": { "type": "string" }
            },
            "furniture": {
            "type": "array",
            "items": { "type": "string" }
            },
            "appliances": {
            "type": "array",
            "items": { "type": "string" }
            },
            "decor": {
            "type": "array",
            "items": { "type": "string" }
            },
            "cleanliness": {
            "type": "string",
            "enum": ["spotless", "clean", "average", "cluttered", "messy"]
            },
            "overall_impression": { "type": "string" }
        },
        "required": [
            "room_type",
            "room_style",
            "dimensions",
            "lighting",
            "flooring",
            "wall_color",
            "features",
            "furniture",
            "appliances",
            "decor",
            "cleanliness",
            "overall_impression"
        ],
        "additionalProperties": False
        }


}

# === Helper to encode image to Base64 ===
def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# === Build payload with Structured Outputs ===
def create_payload(base64_image: str) -> dict:
    return {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Describe this apartment listing image in detail, "
                            "focusing on the room shown, its features, condition, "
                            "and any notable elements visible."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000,
        "response_format": {
            "type": "json_schema",
            "json_schema": ROOM_SCHEMA
        }
    }

# === Send to OpenAI and parse structured output ===
def get_image_description(image_path: str) -> dict:
    base64_image = encode_image_to_base64(image_path)
    payload = create_payload(base64_image)
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        json=payload,
        headers=headers
    )
    # Robust error handling
    if resp.status_code != 200:
        raise RuntimeError(f"OpenAI API error {resp.status_code}: {resp.text}")

    # Parse the JSON-structured response
    content = resp.json()["choices"][0]["message"]["content"]
    return json.loads(content)

def process_apartment_images():
    apartment_dirs = glob.glob("apartment_*")
    for apartment_dir in apartment_dirs:
        print(f"Processing images in {apartment_dir}...")
        image_files = []
        for ext in ('*.jpg', '*.jpeg', '*.png'):
            image_files.extend(glob.glob(os.path.join(apartment_dir, ext)))
            image_files.extend(glob.glob(os.path.join(apartment_dir, ext.upper())))

        for image_path in image_files:
            json_path = Path(image_path).with_suffix('.json')
            if json_path.exists():
                print(f"Skipping {image_path} - JSON already exists")
                continue

            print(f"Processing {image_path}...")
            try:
                description_data = get_image_description(image_path)
                # Save structured data directly
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(description_data, f, indent=2, ensure_ascii=False)
                print(f"Saved description to {json_path}")
            except Exception as e:
                print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    process_apartment_images()
