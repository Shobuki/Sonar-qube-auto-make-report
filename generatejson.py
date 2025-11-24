import requests
import json

SONAR_URL = "http://localhost:9000"
COMPONENT = "PUT YOUR COMPONENT HERE"


#put cookies here
COOKIE_STRING = (
    "sb-127-auth-token-code-verifier="
    "\"9e6a1008c4b9906c59d54a22e24dc04ec125d97e376f9ad721d73c3ed75a78546bd9b32bb31e3eca4510411e1dbc4ca0f03cd87fa37377fcd\"; "
    "sb-127-auth-token="
    "%7B%22access_token%22%3A%22eyJ%7D; "
    "ajs_user_id=892291cc-b2d6-5930-99bd-537e73b4b3d6; "
    "ajs_anonymous_id=1fceb99f-53b1-428b-8e68-abe69acc5460; "
    "XSRF-TOKEN=bb9edqq7oovng30rnb7ihdn5t; "
    "JWT-SESSION=eyJhbGciOiJIUzI1NiJ9.eyJsYXN0UmVmcmVzaFRpbWUiOjE3NjM5NjQwNjE4OTgsInhzcmZUb2tlbiI6ImJiOWVkcXE3b292bmczMHJuYjdpaGRuNXQiLCJqdGkiOiJmMzQ1YmI3OS1hNzhiLTQyZGItOWM4OC1lZWY5MzgzOGFmYzgiLCJzdWIiOiI0ZWQ3MjFmYy0zMWZkLTQxNWMtYTFmMC0yN2NkYWQwNzQ0OWQiLCJpYXQiOjE3NjM5NTY5OTEsImV4cCI6MTc2NDIyMzI2MX0.HSZ7sk55Yg2b9YE6esL0cgWQDAZQKj0yuW5JCBz-Bqk"
)


XSRF_TOKEN_VALUE = "bb9edqq7oovng30rnb7ihdn5t" 


headers = {
    "Cookie": COOKIE_STRING,
    "X-XSRF-TOKEN": XSRF_TOKEN_VALUE
}

all_issues = []
page = 1
page_size = 500

while True:
    url = f"{SONAR_URL}/api/issues/search?componentKeys={COMPONENT}&ps={page_size}&p={page}"
    print("Fetching page", page)

    r = requests.get(url, headers=headers)
    data = r.json()

    if "issues" not in data:
        print("ERROR:", data)
        break

    issues = data["issues"]
    all_issues.extend(issues)

    if len(issues) < page_size:
        break

    page += 1

print("Total collected:", len(all_issues))

with open("sonar_issues.json", "w", encoding="utf-8") as f:
    json.dump({"issues": all_issues}, f, indent=2)

print("Saved to sonar_issues.json")