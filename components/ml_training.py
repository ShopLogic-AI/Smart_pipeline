from typing import NamedTuple

def ml_training_component(
    processed_data_path: str,
    n_clusters: int = 3
) -> NamedTuple('Outputs', [('model_path', str), ('clustered_data_path', str), ('training_metrics', str)]):
    import pandas as pd
    import pickle
    import os
    from sklearn.cluster import KMeans
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score, silhouette_score
    from sklearn.preprocessing import MinMaxScaler
    import json

    with open(processed_data_path, 'rb') as f:
        df_unique = pickle.load(f)

    features = ['price', 'available', 'grams']
    scaler = MinMaxScaler()
    normalized_features = scaler.fit_transform(df_unique[features])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df_unique['cluster'] = kmeans.fit_predict(normalized_features)

    silhouette_avg = silhouette_score(normalized_features, df_unique['cluster'])

    X = df_unique[features + ['cluster']]
    y = df_unique['score']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)

    y_pred = rf_model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    feature_importance = dict(zip(features + ['cluster'], rf_model.feature_importances_))

    os.makedirs('/tmp/models', exist_ok=True)
    model_path = '/tmp/models/rf_model.pkl'
    clustered_data_path = '/tmp/models/clustered_data.pkl'
    kmeans_path = '/tmp/models/kmeans_model.pkl'

    with open(model_path, 'wb') as f:
        pickle.dump(rf_model, f)

    with open(clustered_data_path, 'wb') as f:
        pickle.dump(df_unique, f)

    with open(kmeans_path, 'wb') as f:
        pickle.dump(kmeans, f)

    metrics = {
        'clustering_metrics': {
            'silhouette_score': float(silhouette_avg),
            'n_clusters': int(n_clusters),
            'cluster_sizes': df_unique['cluster'].value_counts().to_dict()
        },
        'regression_metrics': {
            'mse': float(mse),
            'r2_score': float(r2),
            'feature_importance': feature_importance
        },
        'data_info': {
            'training_samples': int(len(X_train)),
            'test_samples': int(len(X_test))
        }
    }

    from collections import namedtuple
    output = namedtuple('Outputs', ['model_path', 'clustered_data_path', 'training_metrics'])
    return output(model_path, clustered_data_path, json.dumps(metrics, indent=2))