import requests
import json
import getpass
import sys

SONAR_URL = "http://localhost:9000"
COMPONENT = "wfm-dashboardd"  
TOKEN_NAME = "auto-token-for-script"  

def generate_token(username, password):
    """Generate user token. Kalau sudah ada, revoke dulu lalu generate ulang."""
    generate_url = f"{SONAR_URL}/api/user_tokens/generate"
    params = {"name": TOKEN_NAME}

    print("\nMencoba generate token...")
    resp = requests.post(generate_url, params=params, auth=(username, password))

    if resp.status_code == 200:
        data = resp.json()
        token = data.get("token")
        print("✅ Token berhasil dibuat baru.")
        return token

    # Kalau gagal karena token dengan nama itu sudah ada
    try:
        data = resp.json()
    except Exception:
        data = {}

    msg = ""
    if isinstance(data, dict):
        errors = data.get("errors", [])
        if errors:
            msg = errors[0].get("msg", "")

    if "already exists" in msg:
        print("ℹ️  Token dengan nama yang sama sudah ada. Mencoba revoke dulu...")

        revoke_url = f"{SONAR_URL}/api/user_tokens/revoke"
        revoke_resp = requests.post(revoke_url, params={"name": TOKEN_NAME}, auth=(username, password))

        if revoke_resp.status_code != 204:
            print("❌ Gagal revoke token lama.")
            print("Status:", revoke_resp.status_code)
            print("Response:", revoke_resp.text)
            sys.exit(1)

        print("✅ Token lama berhasil di-revoke. Generate token baru lagi...")

        # Coba generate ulang
        resp2 = requests.post(generate_url, params=params, auth=(username, password))
        if resp2.status_code != 200:
            print("❌ Gagal generate token setelah revoke.")
            print("Status:", resp2.status_code)
            print("Response:", resp2.text)
            sys.exit(1)

        data2 = resp2.json()
        token = data2.get("token")
        print("✅ Token baru berhasil dibuat.")
        return token

    # Kalau error lain
    print("❌ Gagal generate token.")
    print("Status:", resp.status_code)
    print("Response:", resp.text)
    sys.exit(1)


def fetch_issues(sonar_token):
    """Ambil semua issues untuk COMPONENT dan simpan ke sonar_issues.json."""
    all_issues = []
    page = 1
    page_size = 500

    while True:
        url = f"{SONAR_URL}/api/issues/search"
        params = {
            "componentKeys": COMPONENT,
            "ps": page_size,
            "p": page
        }

        print(f"Fetching page {page} ...")
        r = requests.get(url, auth=(sonar_token, ""), params=params)

        if r.status_code != 200:
            print("❌ Error saat fetch data:")
            print("Status:", r.status_code)
            print("Response:", r.text)
            break

        try:
            data = r.json()
        except requests.exceptions.JSONDecodeError:
            print("❌ Response bukan JSON.")
            print("Body snippet:")
            print(r.text[:500])
            break

        if "issues" not in data:
            print("❌ Response tidak berisi 'issues':")
            print(data)
            break

        issues = data["issues"]
        all_issues.extend(issues)

        if len(issues) < page_size:
            # halaman terakhir
            break

        page += 1

    print("Total collected:", len(all_issues))

    with open("sonar_issues.json", "w", encoding="utf-8") as f:
        json.dump({"issues": all_issues}, f, indent=2)

    print("✅ Saved to sonar_issues.json")


if __name__ == "__main__":
    print("=== SonarQube Issue Export ===")
    username = input("Masukkan username SonarQube: ")
    password = getpass.getpass("Masukkan password SonarQube: ")

    token = generate_token(username, password)
    # Kalau mau lihat token sekali:
    # print("Token:", token)

    fetch_issues(token)
