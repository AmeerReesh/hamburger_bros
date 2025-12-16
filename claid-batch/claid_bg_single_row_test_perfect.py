import pandas as pd
import requests

API_KEY = "1cae86451bd243579fdaa2a410a6c959"

INPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12       Spiky\hamburger bros\claid-batch\hamburgerPros product images -AI workflow with Claid Ai - Cleaned.xlsx"
OUTPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12       Spiky\hamburger bros\claid-batch\hamburgerPros BG TEST - OUTPUT  2.xlsx"

IMAGE_COL = "Image Src"
OUTPUT_COL = "claid_bg_white"
TARGET_EXCEL_ROW = 33   # <<< השורה שאתה רוצה באקסל


def call_claid_remove_bg_white(image_url):
    """
    שולח את התמונה ל-Claid,
    מוציא את הרקע ושם רקע לבן.
    מחזיר URL חדש לתמונה המעובדת או None אם נכשל.
    """
    url = "https://api.claid.ai/v1-beta1/image/edit"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "input": image_url,
        "operations": {
            "background": {
                # להוציא רקע מסביב למוצר
                "remove": {
                    "category": "products"
                },
                # רקע לבן
                "color": "#ffffff"
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
    resp.raise_for_status()
    data = resp.json()

    try:
        return data["data"]["output"]["tmp_url"]
    except Exception:
        print("Unexpected API response:")
        print(data)
        return None


def main():
    # לקרוא את האקסל
    df = pd.read_excel(INPUT_FILE)

    # אם אין עמודת פלט – להוסיף
    if OUTPUT_COL not in df.columns:
        df[OUTPUT_COL] = ""

    # שורה 33 באקסל = אינדקס 31 (0-based + כותרת)
    idx = TARGET_EXCEL_ROW - 2
    image_url = str(df.iloc[idx][IMAGE_COL]).strip()

    print("Testing Excel row:", TARGET_EXCEL_ROW)
    print("Image URL:")
    print(image_url)

    # קריאה ל-Claid
    result_url = call_claid_remove_bg_white(image_url)

    if result_url:
        print("✅ SUCCESS")
        print("Result image URL:", result_url)
        df.at[idx, OUTPUT_COL] = result_url
    else:
        print("❌ FAILED – no output image")

    # שמירת קובץ פלט
    df.to_excel(OUTPUT_FILE, index=False)
    print("Saved output file:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
