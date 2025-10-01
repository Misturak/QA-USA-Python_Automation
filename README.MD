# Project 8: Selenium Automated Testing (Urban Routes)

This project implements **end-to-end automated UI tests** for the Urban Routes app using **Selenium**, **pytest**, and the **Page Object Model (POM)** design pattern.  

The tests cover the full taxi-ordering flow, including:

1. Setting pickup and destination addresses  
2. Selecting the **Supportive** tariff  
3. Filling and confirming a phone number (via SMS code retrieved from performance logs)  
4. Adding a credit card  
5. Writing a comment for the driver  
6. Ordering a blanket and handkerchiefs  
7. Ordering 2 ice creams  
8. Placing the order and verifying that the **car search modal** appears  

---

## 📂 Project Structure

```
QA-USA-Python_Automation/
│
├── data.py                      # Test data (addresses, phone, card info, messages, APP_URL)
├── helpers.py                   # Utility functions (retrieve_phone_code, is_url_reachable)
├── pages.py                     # Page Object Model class (UrbanRoutesPage)
├── main.py                      # Full test suite (pytest class)
├── test_project8_supportive_flow.py  # Alternate pytest test suite
├── requirements.txt             # Python dependencies
└── README.md                    # Instructions (this file)
```

---

## ⚙️ Setup Instructions

### 1. Create & activate a virtual environment
```bash
# from project root
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `selenium==4.25.0`
- `pytest==8.3.3`
- `webdriver-manager`

---

## ▶️ Running Tests

Run all tests (recommended):
```bash
python -m pytest -vv
```

Run the `main.py` test suite explicitly:
```bash
python -m pytest -vv main.py
```

Run the alternate flow-based test file:
```bash
python -m pytest -vv test_project8_supportive_flow.py
```

Run a single test (example):
```bash
python -m pytest -vv test_project8_supportive_flow.py::TestProject8SupportiveFlow::test_03_fill_phone_and_confirm
```

---

## 📝 Notes

- Tests use **Page Object Model** (`pages.py`) for maintainability.  
- **Phone confirmation** relies on Selenium performance logs and the helper `retrieve_phone_code(driver)`.  
- **Card modal** may require a `TAB` key press to enable the **Link** button (handled in code).  
- **Artifacts** (screenshots and HTML) are saved in `/artifacts/` on failure.  
- Ensure you are online when running tests — the app URL (`APP_URL` in `data.py`) must be reachable.  
