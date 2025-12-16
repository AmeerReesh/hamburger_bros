import pandas as pd
import requests
import json

API_KEY = "1cae86451bd243579fdaa2a410a6c959"

INPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12       Spiky\hamburger bros\claid-batch\hamburgerPros product images -AI workflow with Claid Ai - Cleaned.xlsx"
OUTPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12       Spiky\hamburger bros\claid-batch\hamburgerPros BG Scene TEST - OUTPUT.xlsx"

IMAGE_COL = "Image Src"
OUTPUT_COL = "claid_bg_styled"
TARGET_EXCEL_ROW = 11  # Row number 11


def call_claid_remove_background(image_url: str):
    """
    Step 1: Remove the background using the selective method (keep product).
    """
    url = "https://api.claid.ai/v1/image/edit"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "input": image_url,
        "operations": {
            "background": {
                "remove": {
                    "selective": {
                        "object_to_keep": "product"  # Specify what to keep (the product)
                    }
                }
            },
            "resizing": {
                "width": "auto",
                "height": "auto",
                "fit": "crop"
            }
        },
        "output": {
            "format": {
                "type": "jpeg",
                "quality": 90
            }
        }
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    print("Status:", resp.status_code)

    if resp.status_code != 200:
        print("Response text:", resp.text)

    resp.raise_for_status()
    data = resp.json()

    try:
        d = data.get("data", {})
        output = d.get("output")

        if isinstance(output, list) and output:
            first = output[0]
            if isinstance(first, dict) and "tmp_url" in first:
                return first["tmp_url"]

        if isinstance(output, dict) and "tmp_url" in output:
            return output["tmp_url"]

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


def call_claid_add_styled_background(image_url: str):
    """
    Step 2: After background removal, create the scene with the image.
    """
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
            "prompt": (
                "Professional lifestyle furniture scene. "
                "Modern living room interior, soft natural daylight, "
                "light wooden floor, warm neutral walls, "
                "minimalistic premium interior styling, "
                "high-end e-commerce catalog photo."
            ),
            "negative_prompt": (
                "text, watermark, logo, people, man, woman, child, "
                "cartoon, illustration, pixelated, low quality"
            ),
            "aspect_ratio": "4:5",
            "preference": "optimal"
        },
        "output": {
            "number_of_images": 1
        }
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    print("Status:", resp.status_code)

    if resp.status_code != 200:
        print("Response Text:", resp.text)

    resp.raise_for_status()
    data = resp.json()

    try:
        d = data.get("data", {})
        output = d.get("output")

        if isinstance(output, list) and output:
            first = output[0]
            if isinstance(first, dict) and "tmp_url" in first:
                return first["tmp_url"]

        if isinstance(output, dict) and "tmp_url" in output:
            return output["tmp_url"]

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

    idx = TARGET_EXCEL_ROW - 2
    image_url = str(df.iloc[idx][IMAGE_COL]).strip()

    print("Testing Excel row:", TARGET_EXCEL_ROW)
    print("Image URL:")
    print(image_url)

    # Step 1: Remove background
    no_bg_url = call_claid_remove_background(image_url)

    if no_bg_url:
        print(" Background removed successfully.")
        print("Background removed image URL:", no_bg_url)

        # Step 2: Add scene with the processed image
        result_url = call_claid_add_styled_background(no_bg_url)

        if result_url:
            print(" Scene created successfully.")
            print("Result image URL:", result_url)
            df.at[idx, OUTPUT_COL] = result_url
        else:
            print(" FAILED. Scene creation failed.")
    else:
        print(" FAILED. Background removal failed.")

    # Save the output Excel file
    df.to_excel(OUTPUT_FILE, index=False)
    print("Saved output file:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
