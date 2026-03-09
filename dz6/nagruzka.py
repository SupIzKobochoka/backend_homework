import random
import string
import time
import threading
import requests

BASE_URL = "http://localhost:8003"


def rand_str(n=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def generate_valid_ad():
    return {
        "seller_id": random.randint(1, 10000),
        "is_verified_seller": random.choice([True, False]),
        "item_id": random.randint(1, 100000),
        "name": rand_str(15),
        "description": rand_str(50),
        "category": random.randint(0, 20),
        "images_qty": random.randint(0, 10),
    }


def generate_invalid_ad():
    ad = generate_valid_ad()

    error_type = random.choice([
        "wrong_type",
        "missing_field",
        "bad_range",
    ])

    if error_type == "wrong_type":
        ad["seller_id"] = "INVALID"
    elif error_type == "missing_field":
        ad.pop(random.choice(list(ad.keys())))
    elif error_type == "bad_range":
        ad["images_qty"] = 999

    return ad


def call_predict_one():
    url = f"{BASE_URL}/predict_one"
    payload = generate_valid_ad() if random.random() < 0.8 else generate_invalid_ad()
    r = requests.post(url, json=payload, timeout=3)
    print(f"POST /predict_one -> {r.status_code}")


def call_simple_predict():
    url = f"{BASE_URL}/simple_predict"
    params = {
        "item_id": random.randint(1, 100000)
    }
    r = requests.post(url, params=params, timeout=3)
    print(f"POST /simple_predict -> {r.status_code}")


def call_async_predict():
    url = f"{BASE_URL}/async_predict"
    params = {
        "item_id": random.randint(1, 100000)
    }
    r = requests.post(url, params=params, timeout=3)
    print(f"POST /async_predict -> {r.status_code}")


def worker():
    handlers = [
        call_predict_one,
        call_simple_predict,
        call_async_predict,
    ]

    while True:
        try:
            handler = random.choices(
                handlers,
                weights=[0.5, 0.3, 0.2],
                k=1
            )[0]
            handler()
        except Exception as e:
            print("error:", e)

        time.sleep(random.uniform(0.01, 0.2))


def main():
    threads = 3

    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    while True:
        time.sleep(0.5)


if __name__ == "__main__":
    main()