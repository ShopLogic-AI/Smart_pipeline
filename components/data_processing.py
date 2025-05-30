from typing import NamedTuple

def data_processing_component(
    db_host: str,
    db_user: str,
    db_password: str,
    db_name: str
) -> NamedTuple('Outputs', [('processed_data_path', str), ('data_statistics', str)]):
    import pandas as pd
    import mysql.connector
    import pickle
    import os
    from sklearn.preprocessing import MinMaxScaler
    import json

    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

    df = pd.read_sql("SELECT * FROM shopify_products_variants", conn)
    conn.close()

    initial_count = len(df)
    df = df.dropna(subset=['price', 'available', 'grams'])
    df = df[df['price'] > 0]
    cleaned_count = len(df)

    features = ['price', 'available', 'grams']
    df_features = df[features].copy()

    scaler = MinMaxScaler()
    normalized_features = scaler.fit_transform(df_features)
    df_normalized = pd.DataFrame(normalized_features, columns=features)

    weights = {'price': 0.4, 'available': 0.3, 'grams': 0.3}
    df_normalized['score'] = (
        df_normalized['price'] * weights['price'] +
        df_normalized['available'] * weights['available'] +
        df_normalized['grams'] * weights['grams']
    )

    df['score'] = df_normalized['score']

    df_sorted = df.sort_values(by='score', ascending=False)
    df_unique = df_sorted.drop_duplicates(subset=['title'], keep='first').reset_index(drop=True)

    os.makedirs('/tmp/data', exist_ok=True)
    processed_path = '/tmp/data/processed_data.pkl'
    scaler_path = '/tmp/data/scaler.pkl'

    with open(processed_path, 'wb') as f:
        pickle.dump(df_unique, f)

    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)

    stats = {
        'initial_records': int(initial_count),
        'cleaned_records': int(cleaned_count),
        'unique_products': int(len(df_unique)),
        'average_score': float(df_unique['score'].mean()),
        'price_stats': {
            'mean': float(df_unique['price'].mean()),
            'min': float(df_unique['price'].min()),
            'max': float(df_unique['price'].max()),
            'std': float(df_unique['price'].std())
        },
        'vendors_count': int(df_unique['vendor'].nunique()),
        'top_vendors': df_unique['vendor'].value_counts().head(5).to_dict()
    }

    from collections import namedtuple
    output = namedtuple('Outputs', ['processed_data_path', 'data_statistics'])
    return output(processed_path, json.dumps(stats, indent=2))