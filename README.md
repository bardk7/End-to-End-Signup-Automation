# End-to-End Signup Automation with Python Playwright and Mailinator OTP Retrieval

Fully automated end-to-end signup for [authorized-partner.vercel.app](https://authorized-partner.vercel.app) using **Python** and **Playwright (Chromium)**.

Zero manual intervention — the script fills every form field, fetches the OTP from Mailinator, and completes all registration steps automatically.

---

## What It Does

| Step   | Description                                                                                |
| ------ | ------------------------------------------------------------------------------------------ |
| **0**  | Accepts Terms & Conditions                                                                 |
| **1**  | Fills Account Setup (name, email, phone, password)                                         |
| **1b** | Fetches OTP from Mailinator inbox and verifies email (with auto-retry on expiry)           |
| **2**  | Fills Agency Details (name, role, email, website, address, region)                         |
| **3**  | Fills Professional Experience (years, students, focus area, services)                      |
| **4**  | Fills Verification & Preferences (documents, countries, institution types, certifications) |

All form data is **randomly generated** on every run — names, passwords, agency details, regions, countries, and services are all unique each time.

Dropdown and checkbox options are **dynamically discovered** from the live form, so the script adapts automatically if options change on the website.

---

## Prerequisites

- **Python 3.10+** — [Download here](https://www.python.org/downloads/)
- **pip** — comes bundled with Python
- **Internet connection** — required for browser automation and Mailinator OTP retrieval

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/bardk7/vrit-qa-intern-assignment.git
cd vrit-qa-intern-assignment
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows:**

```bash
.venv\Scripts\activate
```

**Mac/Linux:**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Install Playwright browser

```bash
playwright install chromium
```

---

## Usage

```bash
python signup_automation.py
```

A Chromium browser window will open and the script will run through all signup steps automatically. The terminal displays real-time progress:

```
================================================================
  STEP 1  --  ACCOUNT SETUP
================================================================
  [ OK ]             firstName = Hiroshi
  [ OK ]              lastName = Quinn
  [ OK ]                 email = autobot1770654045@mailinator.com
  [ OK ]              password = omYm8L@A1$KTdS
  [ OK ]  Account form submitted — waiting for OTP screen …
```

The browser stays open for 7 seconds after completion so you can inspect the result.

---

## Dependencies

| Package           | Purpose                                                            |
| ----------------- | ------------------------------------------------------------------ |
| **playwright**    | Controls the Chromium browser — clicking, typing, navigating pages |
| greenlet          | Lightweight coroutine switching (used internally by Playwright)    |
| pyee              | Event emitter for browser events (used internally by Playwright)   |
| typing_extensions | Type hint support (used internally by Playwright)                  |

> Only `playwright` is a direct dependency. The others are installed automatically as sub-dependencies.

---

## Randomly Generated Fields

Every run produces unique data for:

| Field               | Example                                                 |
| ------------------- | ------------------------------------------------------- |
| First Name          | Hiroshi, Elena, Kumar, Zara...                          |
| Last Name           | Quinn, Sharma, Chen, Patel...                           |
| Password            | 14-char random (uppercase + lowercase + digit + symbol) |
| Agency Name         | "Apex Edu Solutions 1770654045"                         |
| Role                | Managing Director, Founder, Partner...                  |
| Agency Website      | www.globaleduhub42.com                                  |
| Agency Address      | Random Nepal street + city                              |
| Regions             | Dynamically picked from website options                 |
| Years of Experience | Dynamically picked from website dropdown                |
| Students Per Year   | Random 20–500                                           |
| Focus Area          | Random from 7 education consulting areas                |
| Success Metric      | Random 70–99%                                           |
| Services            | Dynamically picked from website checkboxes              |
| Preferred Countries | Dynamically picked from website options                 |
| Institution Types   | Dynamically picked from website checkboxes              |
| Certifications      | 2–4 random from ICEF, PIER, QEAC, etc.                  |

---

## Troubleshooting

| Issue                          | Solution                                                        |
| ------------------------------ | --------------------------------------------------------------- |
| `playwright` command not found | Make sure the virtual environment is activated                  |
| Browser fails to launch        | Run `playwright install chromium` again                         |
| OTP expired error              | The script auto-retries up to 3 times with resend               |
| Timeout on a form step         | Check your internet connection; the website may be slow or down |
| `python` not recognized        | Use `python3` instead, or add Python to your system PATH        |
