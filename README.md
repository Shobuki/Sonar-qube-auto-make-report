Tentu, ini adalah revisi `README.md` dalam Bahasa Inggris, disusun ulang untuk kejelasan dan profesionalisme yang lebih baik.

-----

## 📘 SonarQube Automatic Report Generator

[](https://github.com/Shobuki/Sonar-qube-auto-make-report)
[](https://www.python.org/downloads/)
[](https://opensource.org/licenses/MIT)

-----

## 📌 Overview

The **SonarQube Automatic Report Generator** is a Python utility designed to automate the process of retrieving **all issues** from a specific SonarQube project and compiling them into structured reports.

This tool is perfect for developers and QA teams who require raw issue data for custom reporting, external dashboards, and automated auditing processes.

### ✨ Key Features

  * **📥 Fetch All Issues:** Retrieves **all issues** from the SonarQube API, including automatic **pagination** handling.
  * **📄 Versatile Output:** Generates a **JSON** file (`sonar_issues.json`) for raw data and a formatted **HTML report** (`sonar_report.html`).
  * **🖨️ PDF Export:** Optional conversion of the HTML report into a printable **PDF report** (`sonar_report.pdf`).
  * **🔐 Automated Token Handling:** Uses **Basic Authentication (Username/Password)** to generate a temporary access token and handles the automatic revocation of old tokens.

-----

## 📂 Project Structure

```
/Sonar-qube-auto-make-report
│
├── generatejson.py     # Main script: Fetches data, generates tokens, and creates reports.
├── sonar_issues.json   # Intermediate JSON file (Raw data output).
├── sonar_report.html   # Generated HTML report (Formatted report output).
└── sonar_report.pdf    # Generated PDF report (Requires wkhtmltopdf).
└── README.md
```

-----

## 📥 Requirements

### 1\. Python Dependencies

  * **Python 3.9** or above.
  * Python libraries (install via `pip`):
    ```bash
    pip install requests pdfkit
    ```

| Library | Purpose |
| :--- | :--- |
| **`requests`** | Used for all HTTP communications with the SonarQube API (token generation and issue fetching). |
| **`pdfkit`** | Python wrapper used for converting the HTML report to PDF. |

### 2\. External Dependency (For PDF Generation Only)

To generate the PDF report (`sonar_report.pdf`), you **must** install the external program **`wkhtmltopdf`**.

  * **Action:** Download and install `wkhtmltopdf` from the [official wkhtmltopdf website](https://wkhtmltopdf.org/).
  * **Configuration:** Ensure the `wkhtmltopdf` executable path inside the `generatejson.py` file is correct for your operating system.
    ```python
    # Example configuration in generatejson.py (must be adjusted)
    config = pdfkit.configuration(
        wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    )
    ```
    *You may need to change this path (e.g., to `/usr/local/bin/wkhtmltopdf` for Linux/macOS).*

### 3\. SonarQube Access

You need the following SonarQube connection details:

| Parameter | Example |
| :--- | :--- |
| **SonarQube URL** | `http://localhost:9000` |
| **Login Username/Password** | `admin`/`password` |
| **Target Project Key** | `your-project` |

-----

## 🔧 How to Use

### 1\. Clone Repository & Install Dependencies

```bash
git clone https://github.com/Shobuki/Sonar-qube-auto-make-report
cd Sonar-qube-auto-make-report
pip install requests pdfkit
# Ensure wkhtmltopdf is installed on your system
```

### 2\. Initial Configuration

You might need to adjust the **`SONAR_URL`** and **`COMPONENT`** (Project Key) variables that are *hardcoded* at the top of the `generatejson.py` file.

### 3\. Run the Script

Execute the main Python script from your terminal:

```bash
python generatejson.py
```

### 4\. Enter Credentials

The script will prompt you for your SonarQube connection details:

```
=== SonarQube Issue Export ===
Masukkan username SonarQube: [Your Username]
Masukkan password SonarQube: [Your Password]
```

### 5\. Output

Upon successful completion, three output files will be generated in the project root directory:

1.  `sonar_issues.json` (Raw issue data, JSON format)
2.  `sonar_report.html` (Formatted issue report, viewable in a browser)
3.  `sonar_report.pdf` (PDF report, if `wkhtmltopdf` is installed)

-----

## 🔍 How It Works (API Flow)

The script interacts with the SonarQube API using Basic Authentication to obtain a Bearer Token, which is then used to fetch the issue data repeatedly. `{SONAR_URL}` represents the base SonarQube URL, and `{TOKEN_NAME}` is hardcoded as `auto-token-for-script`.

| Step | Method | SonarQube API Endpoint | Purpose |
| :--- | :--- | :--- | :--- |
| **1. Token Revocation** | `POST` | `{SONAR_URL}/api/user_tokens/revoke?name={TOKEN_NAME}` | Attempts to revoke an old token with the same name. |
| **2. Token Generation** | `POST` | `{SONAR_URL}/api/user_tokens/generate?name={TOKEN_NAME}` | Generates a new access token using Basic Auth credentials. |
| **3. Issue Search (Paginated)** | `GET` | `{SONAR_URL}/api/issues/search?...` | Retrieves all issues for the specified project, looped until all pages are retrieved. |

### Issue Search Detail (Step 3)

The script must handle **pagination** as the API limits the results per page (the default maximum is 500).

```
GET /api/issues/search?componentKeys={PROJECT_KEY}&ps={PAGE_SIZE}&p={PAGE_NUMBER}
```

| Parameter | Value in Script | Description |
| :--- | :--- | :--- |
| **`componentKeys`** | **`COMPONENT`** | The target project key (e.g., `your-project`). |
| **`ps`** | `500` | Page Size. The maximum number of results to return per page. |
| **`p`** | `1, 2, 3...` | Page Number. Incremented in a loop until the last page is reached. |
The script stops iterating when the number of issues returned in a response is less than the **`ps`** (Page Size).
