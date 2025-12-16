import pandas as pd
import requests
import time

# ========= הגדרות =========
API_KEY = "1cae86451bd243579fdaa2a410a6c959"  # ה-API KEY שלך
INPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12       Spiky\hamburger bros\claid-batch\hamburgerPros product images -AI workflow with Claid Ai - Cleaned.xlsx"
OUTPUT_FILE = r"C:\Users\Ameer\Desktop\My Projects\12       Spiky\hamburger bros\claid-batch\hamburgerPros product images -AI workflow with Claid Ai - OUTPUT.xlsx"

SHEET_NAME = 0  # אם יש רק גיליון אחד באקסל, להשאיר 0

INPUT_URL_COLUMN = "Image Src"               # העמודה עם כתובת התמונה (AF אצלך)
NEEDS_STD_COLUMN = "needs_standardization"   # העמודה עם YES/NO (AK אצלך)
OUTPUT_URL_COLUMN = "claid_standard_white_url"  # עמודת פלט חדשה

MAX_IMAGES = 10   # ⚠️ כמה תמונות להפעיל בניסוי הראשון


def call_claid_standard_white(image_url: str):
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

    # payload לפי ה-API הרשמי
    payload = {
        "input": image_url,
        "operations": {
            "restorations": {
                "decompress": "auto",          # יכול להיות: null / "moderate" / "strong" / "auto"
                "upscale": "smart_enhance",    # "smart_enhance" / "smart_resize" / "faces" / "digital_art" / "photo"
                "polish": False
            },
            "background": {
                "remove": {
                    "category": "products"     # חשוב לאיקומרס
                },
                "color": "#ffffff"             # רקע לבן
            }
            # ===== מקום ל-PROMPT בעתיד (generative / style_transfer) =====
            # "generative": {
            #     "style_transfer": {
            #         "prompt": "product photo on wooden table, soft daylight",
            #         "style_strength": 0.75,
            #         "denoising_strength": 0.75,
            #         "depth_strength": 1.0
            #     }
            # }
            # ============================================================
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
    except requests.exceptions.HTTPError as e:
        print(f"❌ שגיאת HTTP בכתובת: {image_url}")
        print(f"   Status code: {resp.status_code}")
        try:
            print(f"   Response: {resp.text}")
        except Exception:
            pass
        return None
    except Exception as e:
        print(f"❌ שגיאה כללית בכתובת: {image_url}")
        print(f"   {e}")
        return None


def main():
    print("📥 קורא את קובץ האקסל...")
    df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)

    # אם אין את עמודת הפלט – נוסיף אותה ריקה
    if OUTPUT_URL_COLUMN not in df.columns:
        df[OUTPUT_URL_COLUMN] = ""

    total_rows = len(df)
    print(f"נמצאו {total_rows} שורות בגיליון.")
    print(f"נריץ ניסיון על עד {MAX_IMAGES} תמונות שצריך לסטנדרטיזציה.\n")

    processed = 0

    for idx, row in df.iterrows():
        if processed >= MAX_IMAGES:
            print(f"\nהגענו למגבלת הניסיון ({MAX_IMAGES} תמונות). עוצרים כאן 👍")
            break

        needs_std = str(row.get(NEEDS_STD_COLUMN, "")).strip().upper()
        image_url = str(row.get(INPUT_URL_COLUMN, "")).strip()

        # מדלגים על שורות שלא צריכות סטנדרטיזציה או שאין בהן URL
        if needs_std != "YES" or not image_url:
            continue

        print(f"\n🔄 שורה {idx + 2} (אקסל) – שולח ל-Claid...")
        print(f"URL: {image_url}")

        result_url = call_claid_standard_white(image_url)

        if result_url:
            df.at[idx, OUTPUT_URL_COLUMN] = result_url
            processed += 1
            print(f"✅ הצלחה ({processed}/{MAX_IMAGES}). כתובת פלט: {result_url}")
        else:
            print("⚠️ לא נשמר URL (תקלה בבקשה).")

        # הפסקה קטנה בין קריאות – לא להציף את ה-API
        time.sleep(1)

    print("\n💾 שומר קובץ חדש עם תוצאות...")
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"סיימנו! הקובץ נשמר כ:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
