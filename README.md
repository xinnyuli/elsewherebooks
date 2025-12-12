## 🚀 Key Update Summary (v5.0 - Final Logic & Stability Patch)

This submission represents a major engineering upgrade and business logic correction for the book price calculator, aiming for a more stable, aesthetically modern (Modern UI/UX), and functionally accurate pricing tool.

### 1. Architecture and Engineering Improvements (Stability & Best Practice)

The underlying codebase has been thoroughly refactured to adhere to robust software engineering principles:

* **🛡️ Critical Stability Patching**:
    * Introduced the **`RuntimeFixer`** module to specifically **address the `AttributeError` crashes in `CTkSwitch` and `CTkOptionMenu`** that occurred during widget destruction or initialization interruptions. This resolves random application failures under rapid operation or forced exit.
    * Fixed a `KeyError: 'TEXT_SUB'` in the configuration to ensure the application's stability and correct color rendering across themes.
* **🧩 MVC Architectural Separation**:
    * **Logic Decoupling**: All complex pricing formulas are strictly contained within the **`PricingEngine`** static class. This complete separation from the UI layer significantly simplifies future maintenance and unit testing.
    * **Configuration Centralization**: All variables (e.g., margins, API URLs, colors) are defined in the **`AppConfig`** class, enhancing maintainability.
* **🌍 Thread Safety & Performance**: The `ExchangeRateService` utilizes `threading.Lock()` and asynchronous fetching to ensure data integrity and prevent the GUI from freezing .

### 2. Modern UI/UX Implementation (Design & Experience)

The application transitions from native Tkinter to CustomTkinter, adopting modern design standards:

* **Visual Consistency**: Utilizes **Dark Mode** with rounded, card-style layouts, providing a clean and professional aesthetic.
* **Information Hierarchy**: The bottom **`DashboardView`** highlights the Member Price (large, primary color) while displaying the Standard Price in a muted, smaller font, prioritizing key user information.
* **Interaction Refinement**: Buttons and input fields feature modern design touches and the status bar provides real-time feedback on synchronization status.

### 3. Finalized Business Logic (Accurate Pricing Model)

The `PricingEngine` has been definitively updated to correctly execute the final, complex pricing policy agreed upon:

| Pricing Scenario | Member Price Formula (Final AUD) | Standard (Non-Member) Price Formula (Final AUD) |
| :--- | :--- | :--- |
| **Standard Book** | `(Price + 15%)` $\rightarrow$ **AUD** | `(Price + 15%)` $\rightarrow$ **CNY $\times$ 0.3** $\rightarrow$ **AUD** |
| **Manager Recommend** | **Base Member Price $\times$ 0.9** (Extra 10% off) | **Base Member Price** (Non-member gets member pricing) |
| **Used Book** | Input Price $\rightarrow$ **AUD** | Input Price $\rightarrow$ **AUD** |

---
