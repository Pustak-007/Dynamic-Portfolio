# Adaptive Asset Allocation Across Macroeconomic Regimes
### A Systematic Solution to the Stock-Bond Correlation Breakdown

**Author:** Pustak Poudel  
**Date:** January 2026

---

## 1. Project Overview
This repository contains the complete Python codebase and research framework for the paper **"Adaptive Asset Allocation Across Macroeconomic Regimes."**

The project investigates the failure of the traditional 60/40 (Equity/Bond) portfolio during inflationary regimes ("Stagflation") and proposes a dynamic solution. By classifying the economic environment into four quadrants based on the trends of **Growth** and **Inflation**, the model systematically rotates capital into the asset class best suited for the prevailing "weather."

### The Core Thesis
*   **The Problem:** Modern Portfolio Theory assumes a negative correlation between Stocks and Bonds. Empirical analysis (1971–2024) proves that this correlation flips **Positive** during Inflationary regimes, destroying the diversification benefit.
*   **The Solution:** A "Weather Station" approach that switches assets based on macro signals.
    *   **Goldilocks:** Equities (S&P 500)
    *   **Deflation:** Treasuries (10Y)
    *   **Reflation/Stagflation:** Commodities (PPI/Oil)

---

## 2. Key Findings (1971–2024)
The backtest demonstrates that a regime-aware strategy significantly outperforms static allocation by avoiding the "Correlation Trap."

| Metric | Dynamic Strategy | 60/40 Benchmark | Stocks (S&P 500) |
| :--- | :--- | :--- | :--- |
| **Terminal Wealth** | **$67.85** | $37.05 | $58.49 |
| **CAGR** | **8.64%** | 7.35% | 8.32% |
| **Volatility** | **8.94%** | 10.73% | 17.46% |
| **Sharpe Ratio** | **0.49** | 0.32 | 0.30 |
| **Max Drawdown** | **-27.03%** | -32.95% | -56.70% |

**Key Takeaway:** The strategy achieved Equity-like returns with Bond-like volatility, primarily by switching to **Commodities** during the 1970s and **Treasuries** during the 2008 GFC.

---

## 3. Data Requirements
This project requires access to institutional-grade financial data. It is **not** compatible with standard Yahoo Finance scraping due to the need for 1970s data and total return indices.

### APIs Required:
1.  **WRDS (Wharton Research Data Services):**
    *   **Library:** `crsp`
    *   **Table:** `dsi` (Daily Stock Indices)
    *   **Variable:** `sprtrn` (S&P 500 Value-Weighted Total Return).
2.  **FRED (Federal Reserve Economic Data):**
    *   **Macro:** `CPIAUCSL` (CPI), `INDPRO` (Industrial Production).
    *   **Bonds:** `DGS10` (10-Year Treasury Yield).
    *   **Commodities:** `PPIACO` (PPI All Commodities), `WTISPLC` (WTI Oil).
    *   **Risk-Free:** `DTB3` (3-Month T-Bill).

---

## 4. Repository Structure
The codebase is modularized into **15 sequential steps** to ensure reproducibility and logical flow.

### Phase I: Data Engineering & Benchmarking
*   `01_construct_benchmark.py`: Downloads CRSP/FRED data, synthesizes Bond Price returns from Yields, and constructs the 60/40 Benchmark.
*   `02_visualize_assets.py`: Visualizes the "Growth of $1" for base assets to verify data integrity.

### Phase II: The Macro Model
*   `03_macro_regimes.py`: Downloads Macro data, calculates 3-month trends (Second Derivative), and classifies history into 4 Quadrants (Goldilocks, Reflation, Stagflation, Deflation).
*   `04_construct_alternatives.py`: Constructs the "Inflation Hedge" assets (Commodities/Oil) using monthly data forward-filled to daily.

### Phase III: The Backtest
*   `05_dynamic_backtest.py`: **The Core Engine.** Aligns the Regime Signal (lagged 1 day) with Asset Returns and executes the switching logic.
*   `06_comprehensive_comparison.py`: Merges all equity curves and re-bases them to $1.0 at the common start date (April 1971). Saves the **Master Consolidated Dataset**.

### Phase IV: Performance & Risk Analysis
*   `07_construct_risk_free.py`: Downloads T-Bill rates and calculates geometrically compounded Daily Risk-Free Returns.
*   `08_performance_metrics.py`: Calculates CAGR, Volatility, and Sharpe Ratios. Crucially, it performs **Regime Attribution** (calculating metrics *conditional* on the economic state).
*   `09_distributional_analysis.py`: Calculates Skewness/Kurtosis and generates KDE/Histogram plots to visualize "Tail Risk."
*   `10_drawdown_analysis.py`: Generates Drawdown curves and calculates "Underwater Duration" and "Recovery Time."

### Phase V: Mechanism & Robustness
*   `11_correlation_analysis.py`: Calculates the Rolling 24-Month Stock-Bond Correlation overlaid with Regime shading. **(The Proof of Concept).**
*   `12_yearly_analysis.py`: Generates the "Heatmap" of calendar year returns.
*   `13_turnover_analysis.py`: Calculates Portfolio Turnover and Friction Costs (Net CAGR).
*   `14_create_dashboard.py`: Aggregates all key charts and tables into a single High-Res "Tear Sheet."
*   `15_inspect_period.py`: Allows focused analysis of specific time windows to examine performance and behavior across different macroeconomic regimes.



---

## 5. Directory Structure
The scripts automatically generate the following folder structure:
*   `/raw_data/`: Direct downloads from WRDS/FRED.
*   `/modified_data/`: Processed, aligned, and rebased datasets.
*   `/figures/`: High-resolution charts (.png).
*   `/results/`: Statistical tables (.csv).

---

## 6. How to Run
1.  Ensure you have a valid `wrds` username configured and a `FRED_API_KEY`.
2.  Install dependencies:
    ```bash
    pip install pandas numpy matplotlib seaborn scipy fredapi wrds
    ```
3.  Run the modules in numerical order (01 -> 16).
    *   *Note:* Module 6 generates the `consolidated_portfolio_rebased.csv` which is the input for all subsequent analysis modules.

---

## 7. Disclaimer
*This project is for educational and research purposes only. Past performance is not indicative of future results. The strategy relies on historical economic relationships that may not persist.*