import pandas as pd
import requests
import time

# ========= הגדרות =========
API_KEY = "1cae86451bd243579fdaa2a410a6c959"  # לכאן להדביק את ה-API KEY החדש שלך
INPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12       Spiky\hamburger bros\claid-batch\hamburgerPros product images -AI workflow with Claid Ai - Cleaned.xlsx"
OUTPUT_FILE = r"OUTPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12       Spiky\hamburger bros\claid-batch\hamburgerPros product images -AI workflow with Claid Ai - OUTPUT.xlsx"


SHEET_NAME = 0  # אם יש רק גיליון אחד באקסל, להשאיר 0. אם יש כמה גיליונות – אפשר לשים את השם במרכאות.

INPUT_URL_COLUMN = "Image Src"           # שם העמודה עם כתובת התמונה (AF אצלך)
NEEDS_STD_COLUMN = "needs_standardization"  # העמודה עם YES/NO (AK אצלך)
OUTPUT_URL_COLUMN = "claid_standard_white_url"  # עמודה חדשה שניצור


def call_claid_standard_white(image_url: str) -> str | None:
    """
    שולח את התמונה ל-Claid כדי לנקות/לאחד אותה על רקע לבן
    ומחזיר tmp_url של התמונה המעובדת.
    אם יש תקלה – מחזיר None.
    """
    endpoint = "https://api.claid.ai/v1/image/edit"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "*/*",
    }

    payload = {
        "input": image_url,
        "operations": {
            "restorations": {
                "upscale": {
                    "mode": "smart_enhance"
                },
                "decompress": {
                    "mode": "auto"
                },
                "polish": False
            },
            "background": {
                "remove": {
                    "category": "products"
                },
                "color": "#ffffff"
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

    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["data"]["output"]["tmp_url"]
    except Exception as e:
        print(f"❌ שגיאה בכתובת: {image_url}")
        print(f"   {e}")
        return None


def main():
    print("📥 קורא את קובץ האקסל...")
    df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)

    # אם אין את העמודה – נוסיף אותה ריקה
    if OUTPUT_URL_COLUMN not in df.columns:
        df[OUTPUT_URL_COLUMN] = ""

    total_rows = len(df)
    print(f"נמצאו {total_rows} שורות בגיליון.")

    for idx, row in df.iterrows():
        needs_std = str(row.get(NEEDS_STD_COLUMN, "")).strip().upper()
        image_url = str(row.get(INPUT_URL_COLUMN, "")).strip()

        # מדלגים על שורות שלא צריכים סטנדרטיזציה או שאין בהן URL
        if needs_std != "YES" or not image_url:
            continue

        print(f"\n🔄 שורה {idx + 2} (אקסל) – שולח ל-Claid...")
        print(f"URL: {image_url}")

        result_url = call_claid_standard_white(image_url)

        if result_url:
            df.at[idx, OUTPUT_URL_COLUMN] = result_url
            print(f"✅ הצלחה. כתובת פלט: {result_url}")
        else:
            print("⚠️ לא נשמר URL (תקלה בבקשה).")

        # הפסקה קטנה בין קריאות – לא להציף את ה-API
        time.sleep(1)

    print("\n💾 שומר קובץ חדש עם תוצאות...")
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"סיימנו! הקובץ נשמר כ:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
