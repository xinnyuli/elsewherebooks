# Integra Book Price Calculator 📚

**Author:** XINYULI (KELLY)  
**Version:** 3.0

A simple Python tool designed to calculate book prices (Member vs. Standard) based on real-time exchange rates.

## ⚡ Features

* **Auto Exchange Rates:** Fetches real-time rates (Base: AUD).
* **Quick Calculation:** Supports JPY, SGD, MYR, HKD, TWD, CNY, and AUD.
* **Smart Pricing:** Automatically calculates:
    * **Member Price:** Discounted rate.
    * **Standard Price:** Adjusted market rate.
* **Used Books:** One-click shortcuts for $5 / $10 used books.

## 🚀 How to Run

1.  **Install the library:**
    ```bash
    pip install requests
    ```

2.  **Run the script:**
    ```bash
    python main.py
    ```

## 🧮 Pricing Logic

* **Base Margin:** +15% on original price.
* **Member Price:** Converted cost (minus 10% if "Recommended").
* **Standard Price:** Benchmarked against CNY rates.

---
*Created for personal use.*
