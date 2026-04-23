## Electricity Demand Forecasting

This project demanded an ml model that predicts next-hour electricity demand using historical demand data along with weather and economic indicators.

The objective is to capture both (1) time-based patterns and (2) external influences to build an accurate and interpretable forecasting model.

---

## Data Cleaning:

### (1) Handling Anomalies

* Extreme demand spikes were identified using the 1st and 99th percentiles
* Initially,attempted clipping, but it flattened the data
* Finally used rolling median

  * Replaced anomalous values using nearby values
  * Preserved natural trends in the data

---

### (2) Handling Missing Values

* Weather data contained missing values, which were filled using:
  * **Forward fill (ffill)**
  * **Backward fill (bfill)**

**Why?:**
Weather changes gradually, so nearby values seem to be the best suits to fill the gaps, which also preserves natural trends to some extent

---

## Feature Engineering:

### (1) Temporal Features

Capture time-based patterns:

* `hour`,
       why? -> captures daily cycles
* `day_of_week`,`is_weekend`
       why? -> to compare weekday vs weekend behavior
* `month`
       why? -> to capture somewhat seasonal variation

---

### (2) External Features

* Weather variables (temperature, humidity, etc.)
  why?
  - because weather even in real life, somewhat directly impacts power consumption and demand
* Economic indicators (expanded from yearly to hourly)
  why?
  - because prosperous and wealthier regions tend to consume more power while power consumption and demand is genrally low in areas of less economic prosperity

---

## Evaluation

Metric used: **MAPE (Mean Absolute Percentage Error)**

| Model    | MAPE      |
| -------- | --------- |
| LightGBM | **2.11%** |
| XGBoost  | 2.19%     |

The mape values for both the models seem to be quite competitive (~2%). 

---

## Feature Importance & Insights

### Key Observations:

* **Hour of the day** was the most important feature
  - Indicates strong daily usage patterns

* **Lag24 (previous day same hour)** was highly influential
  - Shows demand repeats daily

* **Current demand (`demand_mw_clean`)**
  - Captures short-term continuity

---

### Interpretation:

* Electricity demand is primarily driven by:

  1. **Time-based patterns (daily cycles)**
  2. **Recent historical demand**

* Weather has a **secondary influence**

* Weekly lag (`lag168`) was less important due to redundancy with other features like lag24

---

## Conclusion

This project employs classical models to develop a machine learning pipeline which predicts hourly power demand.

---
