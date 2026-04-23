import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df_demand = pd.read_excel("PGCB_date_power_demand.xlsx")
df_weather = pd.read_excel("weather_data.xlsx")
df_economic = pd.read_csv("economic_full_1.csv")

# print("demand shape: ", df_demand.shape)
# print("weather shape: ", df_weather.shape)
# print("economic shape: ", df_economic.shape)

# Quick peek at each dataset
# print("=== DEMAND DATA ===")
# print(df_demand.head())
# print(df_demand.dtypes)

# print("\n=== WEATHER DATA ===")
# print(df_weather.head())

# Fix weather loading - skip the metadata rows
df_weather = pd.read_excel("weather_data.xlsx", skiprows=2, header=1)

# print("\n=== WEATHER DATA ===")
# print(df_weather.head(3))
# print(df_weather.columns.tolist())

# print("\n=== ECONOMIC DATA ===")
# print(df_economic.head(3))

# Sort by datetime first - always do this with time series data
df_demand = df_demand.sort_values('datetime').reset_index(drop=True)

# Plot demand over time
# plt.figure(figsize=(15, 5))
# plt.plot(df_demand['datetime'], df_demand['demand_mw'], linewidth=0.5)
# plt.title('Electricity Demand Over Time')
# plt.xlabel('Date')
# plt.ylabel('Demand (MW)')
# plt.tight_layout()
# plt.savefig('demand_overview.png')
# print("Plot saved as demand_overview.png")

# # Check duplicate timestamps
# duplicates = df_demand.duplicated(subset=['datetime']).sum()
# print(f"Duplicate timestamps: {duplicates}")

# # Check missing values
# print("\nMissing values in demand data:")
# print(df_demand.isnull().sum())

# # Check weather data missing values
# print("Missing values in weather data:")
# print(df_weather.isnull().sum())

# print(df_economic.columns.tolist())

# print(df_demand['demand_mw'].describe())

import numpy as np

upper_limit = df_demand['demand_mw'].quantile(0.99)
lower_limit = df_demand['demand_mw'].quantile(0.01)

# print("99th percentile:", upper_limit)
# print("1st percentile:", lower_limit)

# clipping
upper_limit = df_demand['demand_mw'].quantile(0.99)

df_demand['demand_mw_clipped'] = df_demand['demand_mw'].clip(upper=upper_limit)

# plt.figure(figsize=(15,5))
# plt.plot(df_demand['datetime'], df_demand['demand_mw'], label='Original', alpha=0.5)
# plt.plot(df_demand['datetime'], df_demand['demand_mw_clipped'], label='Clipped', linewidth=1)
# plt.legend()
# plt.title("Before vs After Clipping")
# plt.savefig('demand_overview_clipped.png')
# print("Plot saved as demand_overview_clipped.png")
# plt.show()

# affected = (df_demand['demand_mw'] > upper_limit).sum()
# print("Number of clipped points:", affected)

# lower_limit = df_demand['demand_mw'].quantile(0.01)

# df_demand['demand_mw_clean'] = df_demand['demand_mw_clipped'].clip(lower=lower_limit)

# plt.figure(figsize=(15,5))
# plt.plot(df_demand['datetime'], df_demand['demand_mw_clean'], linewidth=0.7)
# plt.title("Final Cleaned Demand")
# plt.savefig('demand_overview_final.png')
# print("Plot saved as demand_overview_final.png")
# plt.show()

# rolling median
is_anomaly = (df_demand['demand_mw'] > upper_limit) | (df_demand['demand_mw'] < lower_limit)

rolling_median = df_demand['demand_mw'].rolling(window=5, center=True).median()

df_demand['demand_mw_clean'] = df_demand['demand_mw']
df_demand.loc[is_anomaly, 'demand_mw_clean'] = rolling_median

# plt.figure(figsize=(15,5))
# plt.plot(df_demand['datetime'], df_demand['demand_mw_clean'], linewidth=0.7)
# plt.title("Final Cleaned Demand")
# plt.savefig('demand_overview_rolling.png')
# print("Plot saved as demand_overview_rolling.png")
# plt.show()

df_weather.rename(columns={'time': 'datetime'}, inplace=True)

# print(df_demand.columns)
# print(df_weather.columns)

df_demand['datetime'] = pd.to_datetime(df_demand['datetime'])
df_weather['datetime'] = pd.to_datetime(df_weather['datetime'])

df = pd.merge(df_demand, df_weather, on='datetime', how='left')

df['demand_mw_clean'].fillna(method='bfill', inplace=True)

# print(df.isnull().sum())
# print(df.shape)
# print(df.head())

cols_to_drop = ['wind', 'india_adani', 'nepal', 'remarks']

df.drop(columns=cols_to_drop, inplace=True)

# df.fillna(method='ffill', inplace=True)
# df.fillna(method='bfill', inplace=True)

df.ffill(inplace=True)
df.bfill(inplace=True)

# print(df.isnull().sum())

df['year'] = df['datetime'].dt.year
# print(df_economic.head())
# print(df_economic.columns)

selected_cols = [
    'year',
    'GDP (current US$)',
    'Population, total',
    'Access to electricity (% of population)',
    'Urban population (% of total)',
    'Industry (including construction), value added (% of GDP)',
    'Electric power transmission and distribution losses (% of output)'
]

# df_economic = df_economic[selected_cols]

# df = pd.merge(df, df_economic, on='year', how='left')

# print(df.shape)
# print(df.head())

indicators = [
    'Access to electricity (% of population)',
    'Urban population',
    'Rural population',
    'Industry (including construction), value added (% of GDP)',
    'Electric power transmission and distribution losses (% of output)',
    'GDP per unit of energy use (PPP $ per kg of oil equivalent)',
]

df_economic = df_economic[df_economic['Indicator Name'].isin(indicators)]

year_cols = [col for col in df_economic.columns if col.isdigit()]

df_economic = df_economic.melt(
    id_vars=['Indicator Name'],
    value_vars=year_cols,
    var_name='year',
    value_name='value'
)

df_economic = df_economic.pivot(
    index='year',
    columns='Indicator Name',
    values='value'
).reset_index()

df_economic['year'] = df_economic['year'].astype(int)

df = pd.merge(df, df_economic, on='year', how='left')

# df.ffill(inplace=True)
# df.bfill(inplace=True)

# print(df_economic.head())
# print(df_economic.shape)

df.ffill(inplace=True)
df.bfill(inplace=True)

# print(df.isnull().sum())
# print(df.shape)

df['hour'] = df['datetime'].dt.hour
df['day_of_week'] = df['datetime'].dt.dayofweek
df['month'] = df['datetime'].dt.month
df['is_weekend'] = df['day_of_week'].isin([5,6]).astype(int)

df['lag1'] = df['demand_mw_clean'].shift(1)
df['lag24'] = df['demand_mw_clean'].shift(24)
df['lag168'] = df['demand_mw_clean'].shift(168)

# df = df.dropna()

df['rolling_mean_3'] = df['demand_mw_clean'].rolling(3).mean()
df['rolling_mean_24'] = df['demand_mw_clean'].rolling(24).mean()
df['std_24'] = df['demand_mw_clean'].rolling(24).std()

df = df.dropna()

# print(df.shape)

df['target'] = df['demand_mw_clean'].shift(-1)

import re

def clean_column_names(df):
    df.columns = [
        re.sub(r'[^A-Za-z0-9_]+', '_', col)
        for col in df.columns
    ]
    return df

df = clean_column_names(df)

train = df[df['year'] < 2023]
test  = df[df['year'] == 2023]

# print(df.columns.tolist())

X_train = train.drop(columns=['target', 'datetime', 'demand_mw', 'demand_mw_clipped'])
y_train = train['target']

X_test = test.drop(columns=['target', 'datetime', 'demand_mw', 'demand_mw_clipped'])
y_test = test['target']


import lightgbm as lgb

model = lgb.LGBMRegressor(
    n_estimators=100,
    learning_rate=0.1,
    random_state=42
)

model.fit(X_train, y_train)

y_pred_lgb = model.predict(X_test)

from sklearn.metrics import mean_absolute_percentage_error

mape_lgb = mean_absolute_percentage_error(y_test, y_pred_lgb)

print("LightGBM MAPE:", mape_lgb)


lgb.plot_importance(model, max_num_features=15)
plt.show()

import xgboost as xgb

model_xgb = xgb.XGBRegressor(
    n_estimators=100,
    learning_rate=0.1,
    random_state=42
)

model_xgb.fit(X_train, y_train)

y_pred_xgb = model_xgb.predict(X_test)

mape_xgb = mean_absolute_percentage_error(y_test, y_pred_xgb)

print("XGBoost MAPE:", mape_xgb)

