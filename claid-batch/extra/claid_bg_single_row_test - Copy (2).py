import pandas as pd
import requests

API_KEY = "1cae86451bd243579fdaa2a410a6c959"

INPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12       Spiky\hamburger bros\claid-batch\hamburgerPros product images -AI workflow with Claid Ai - Cleaned.xlsx"
OUTPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12\Spiky\hamburger bros\claid-batch\hamburgerPros BG TEST - OUTPUT  2.xlsx"

IMAGE_COL = "Image Src"
OUTPUT_COL = "claid_bg_v2"

TARGET_EXCEL_ROW = 11  # Excel row number (including header)

def call_claid_ai_background(image_url):
    url = "https://api.claid.ai/v1/ai-background/generate"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "object": {
            "image_url": image_url
        },
        "scene": {
            "model": "v2",
            "prompt": (
                "Professional lifestyle product photo. "
                "Modern living room interior, light wooden floor, "
                "neutral beige walls, soft natural daylight, "
                "minimalistic furniture, premium furniture catalog style."
            ),
            "negative_prompt": (
                "text, watermark, logo, brand, man, woman, child, "
                "cartoon, illustration, pixelated, low quality"
            ),
            "aspect_ratio": "4:5",
            "preference": "optimal"
        },
        "output": {
            "number_of_images": 1
        }
    }

    response = requests.post(url, json=payload, headers=headers, timeout=120)
    response.raise_for_status()
    data = response.json()

    try:
        return data["data"]["output"]["images"][0]["tmp_url"]
    except Exception:
        print("Unexpected API response:")
        print(data)
        return None


def main():
    df = pd.read_excel(INPUT_FILE)

    if OUTPUT_COL not in df.columns:
        df[OUTPUT_COL] = ""

    idx = TARGET_EXCEL_ROW - 2
    image_url = str(df.iloc[idx][IMAGE_COL]).strip()

    print("Testing Excel row:", TARGET_EXCEL_ROW)
    print("Image URL:")
    print(image_url)

    result = call_claid_ai_background(image_url)

    if result:
        print("✅ SUCCESS")
        print(result)
        df.at[idx, OUTPUT_COL] = result
    else:
        print("❌ FAILED – no output image")

    df.to_excel(OUTPUT_FILE, index=False)
    print("Saved output file:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
