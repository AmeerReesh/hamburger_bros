# file: claid_single_edit.py
import requests
import json

API_KEY = "1cae86451bd243579fdaa2a410a6c959"  # שים כאן את המפתח שלך

URL = "https://api.claid.ai/v1-beta1/image/edit"

payload = {
    "input": "https://claid.ai/doc-samples/bag.jpeg",  # תחליף ל-Shopify URL שלך
    "operations": {
        "resizing": {
            "width": 800,
            "height": 800,
            "fit": "crop"
        },
        "adjustments": {
            "hdr": 60,
            "sharpness": 40
        }
    },
    "output": {
        "format": {
            "type": "jpeg",
            "quality": 90
        }
    }
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def main():
    try:
        resp = requests.post(URL, headers=headers, json=payload, timeout=120)
        print("Status:", resp.status_code)
        resp.raise_for_status()

        data = resp.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # כתובת התמונה החדשה
        tmp_url = data["data"]["output"]["tmp_url"]
        print("\nResult image URL:")
        print(tmp_url)

    except requests.exceptions.HTTPError as e:
        print("HTTP error:", e)
        print("Response body:", resp.text)
    except Exception as e:
        print("Unexpected error:", e)

if __name__ == "__main__":
    main()
