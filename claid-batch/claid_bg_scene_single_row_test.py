import pandas as pd
import requests
import json  # just for pretty-printing debug

API_KEY = "1cae86451bd243579fdaa2a410a6c959"

INPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12       Spiky\hamburger bros\claid-batch\hamburgerPros product images -AI workflow with Claid Ai - Cleaned.xlsx"
OUTPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12       Spiky\hamburger bros\claid-batch\hamburgerPros BG Scene TEST - OUTPUT.xlsx"

IMAGE_COL = "Image Src"
OUTPUT_COL = "claid_bg_styled"
TARGET_EXCEL_ROW = 11   # ✅ רק שורה 11


def call_claid_add_styled_background(image_url):
    url = "https://api.claid.ai/v1/scene/create"

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
            # 👇 ניסוח חזק יותר שמכריח סצנה ולא רק רקע לבן
            "prompt": (
                "Replace the plain white studio background with a full interior scene. "
                "The product stands in a modern living room. Light wooden floor, "
                "warm beige walls, a soft fabric sofa and a coffee table in the background, "
                "soft natural daylight from the left, premium lifestyle interior photo "
                "for a high-end e-commerce catalog."
            ),
            "negative_prompt": (
                "plain white background, studio background, solid color background, "
                "text, watermark, logo, people, man, woman, child, "
                "cartoon, illustration, pixelated, low quality"
            ),
            "aspect_ratio": "4:5",
            "preference": "optimal",
        },
        "output": {
            "number_of_images": 1
        }
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    print("Status:", resp.status_code)

    if resp.status_code != 200:
        print("Response text:", resp.text)

    resp.raise_for_status()
    data = resp.json()

    # ניסיון להוציא tmp_url מכל המבנים האפשריים
    try:
        d = data.get("data", {})
        output = d.get("output")

        # 1) output הוא list – כמו בסקרינשוט שקיבלת מה-image/edit
        if isinstance(output, list) and output:
            first = output[0]
            if isinstance(first, dict) and "tmp_url" in first:
                return first["tmp_url"]

        # 2) output dict עם tmp_url ישיר
        if isinstance(output, dict):
            if "tmp_url" in output:
                return output["tmp_url"]

            # 3) output["images"][0]["tmp_url"]
            images = output.get("images")
            if isinstance(images, list) and images:
                first_img = images[0]
                if isinstance(first_img, dict) and "tmp_url" in first_img:
                    return first_img["tmp_url"]

        print("Unexpected API response structure:")
        print(json.dumps(data, indent=2))
        return None

    except Exception as e:
        print("Error while parsing API response:", e)
        print(json.dumps(data, indent=2))
        return None


def main():
    df = pd.read_excel(INPUT_FILE)

    if OUTPUT_COL not in df.columns:
        df[OUTPUT_COL] = ""

    idx = TARGET_EXCEL_ROW - 2  # שורה 11 באקסל -> אינדקס 9
    image_url = str(df.iloc[idx][IMAGE_COL]).strip()

    print("Testing Excel row:", TARGET_EXCEL_ROW)
    print("Image URL:")
    print(image_url)

    result_url = call_claid_add_styled_background(image_url)

    if result_url:
        print("✅ SUCCESS")
        print("Result image URL:", result_url)
        df.at[idx, OUTPUT_COL] = result_url
    else:
        print("❌ FAILED – no output image")

    df.to_excel(OUTPUT_FILE, index=False)
    print("Saved output file:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
