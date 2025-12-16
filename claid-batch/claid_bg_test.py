# -*- coding: utf-8 -*-
import pandas as pd
import requests

# ================== הגדרות ==================
API_KEY = "1cae86451bd243579fdaa2a410a6c959"

INPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12       Spiky\hamburger bros\claid-batch\hamburgerPros product images -AI workflow with Claid Ai - Cleaned.xlsx"
OUTPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12       Spiky\hamburger bros\claid-batch\hamburgerPros BG TEST - OUTPUT.xlsx"

SHEET_NAME = 0
TARGET_EXCEL_ROW = 11  # שורה 11 באקסל (לא לגעת)

INPUT_URL_COLUMN = "Image Src"
OUTPUT_URL_COLUMN = "claid_lifestyle_bg_url"

# ================== פרומפטים ==================
PROMPT_GUIDELINES = [
    "modern living room",
    "warm natural light",
    "light wooden floor",
    "premium furniture showroom",
    "realistic lifestyle environment",
    "professional product photography"
]

NEGATIVE_PROMPT = [
    "text",
    "watermark",
    "logo",
    "people",
    "hands",
    "cartoon",
    "low quality",
    "blur"
]


def call_claid_lifestyle_background(image_url: str):
    endpoint = "https://api.claid.ai/v1/image/edit"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "*/*",
    }

    payload = {
        "input": image_url,
        "operations": {
            "background": {
                "scene": {
                    "model": "v2",
                    "prompt": {
                        "generate": True,
                        "guidelines": PROMPT_GUIDELINES
                    },
                    "negative_prompt": NEGATIVE_PROMPT,
                    "aspect_ratio": "4:5",
                    "preference": "best"
                }
            }
        },
        "output": {
            "format": {
                "type": "jpeg",
                "quality": 90,
                "progressive": True
            }
        }
    }

    response = requests.post(endpoint, json=payload, headers=headers, timeout=120)

    if response.status_code != 200:
        print("שגיאה מה־API")
        print(response.status_code)
        print(response.text)
        return None

    return response.json()["data"]["output"]["tmp_url"]


def main():
    print("")
    print("מתחיל טסט לייפסטייל על שורה אחת בלבד")
    print("שורה באקסל:", TARGET_EXCEL_ROW)
    print("")

    df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)

    if OUTPUT_URL_COLUMN not in df.columns:
        df[OUTPUT_URL_COLUMN] = ""

    idx = TARGET_EXCEL_ROW - 1  # המרה לאינדקס פייתון
    row = df.loc[idx]

    image_url = str(row.get(INPUT_URL_COLUMN, "")).strip()

    print("URL המקור:")
    print(image_url)
    print("")

    if not image_url:
        print("אין URL בשורה הזו – ביטול")
        return

    print("שולח ל-Claid (AI Background)...")
    result_url = call_claid_lifestyle_background(image_url)

    if result_url:
        df.at[idx, OUTPUT_URL_COLUMN] = result_url
        print("")
        print("הטסט הצליח")
        print("URL תמונת פלט:")
        print(result_url)
    else:
        print("")
        print("הטסט נכשל")

    df.to_excel(OUTPUT_FILE, index=False)
    print("")
    print("הקובץ נשמר:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
