"""
Script to save the trained Prophet model to JSON format
Run this ONCE after training your model in model.ipynb
"""
import json
import pandas as pd
from prophet import Prophet

# Load your data
df = pd.read_csv('DATASETS/new_dataset.csv', parse_dates=['date'])

# Prepare data for Prophet (must have 'ds' and 'y' columns)
prophet_df = df[['date', 'price']].rename(columns={'date': 'ds', 'price': 'y'})

# Create and train model
model = Prophet(
    interval_width=0.95,
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False
)

print("Training Prophet model...")
model.fit(prophet_df)

# Save the trained model to JSON format
print("Saving model...")
model_data = {
    'params': {
        'interval_width': 0.95,
        'yearly_seasonality': True,
        'weekly_seasonality': False,
        'daily_seasonality': False,
    },
    'training_data': prophet_df.to_dict(orient='records'),
}

with open('prophet_model.json', 'w') as f:
    json.dump(model_data, f, indent=4, default=str)

# Save metadata
metadata = {
    'interval_width': 0.95,
    'yearly_seasonality': True,
    'weekly_seasonality': False,
    'daily_seasonality': False,
    'training_rows': len(prophet_df),
    'last_date': str(prophet_df['ds'].max())
}

with open('model_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=4)

print("✓ Model saved as 'prophet_model.json'")
print("✓ Metadata saved as 'model_metadata.json'")
