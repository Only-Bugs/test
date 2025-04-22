#!/usr/bin/env python3
import os, sys, uuid, base64, json, argparse
import requests

def make_request(image_path, url):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode('utf8')
    payload = {
        "id": str(uuid.uuid4()),
        "image": img_b64
    }
    r = requests.post(url, json=payload)
    try:
        data = r.json()
    except ValueError:
        data = r.text
    print(f"\n=== {os.path.basename(image_path)} ===")
    print(f"Status: {r.status_code}")
    print(json.dumps(data, indent=2))

def main():
    parser = argparse.ArgumentParser(
        description="Smoke‑test CloudPose API (/predict)"
    )
    parser.add_argument(
        "images", nargs="+",
        help="Path(s) to one or more JPG/PNG files"
    )
    parser.add_argument(
        "--url", default="http://localhost:8000/predict",
        help="Full URL of the predict endpoint"
    )
    args = parser.parse_args()

    for img in args.images:
        if not os.path.isfile(img):
            print(f"❌ File not found: {img}")
            continue
        make_request(img, args.url)

if __name__ == "__main__":
    main()
