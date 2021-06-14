"""Prepares the raw data for training and uploads it to S3."""

import json
import pandas as pd
import subprocess as sp
import smart_open

dependent_variable = 'quality'
bucket = sp.check_output('pulumi stack output bucket', shell=True).decode().strip()

df = pd.read_csv(f'data/winequality-red.csv')

# y column should come first as SageMaker recognizes the first
# column as the dependent variable
df = df[[dependent_variable] + [c for c in df.columns if c != dependent_variable]]

csv = f's3://{bucket}/training_data/csv/part_c0.csv.gz'
with smart_open.open(csv, 'w') as fp:
    df.to_csv(fp, index=False, header=False)
    print(f'Written {csv}')

schema = f's3://{bucket}/training_data/_schema.json'
with smart_open.open(schema, 'w') as fp:
    json.dump({'columns': [c for c in df.columns]}, fp)
    print(f'Written {schema}')
