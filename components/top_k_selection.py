from typing import NamedTuple

def top_k_selection_component(
    clustered_data_path: str,
    model_path: str,
    k: int = 10
) -> NamedTuple('Outputs', [('top_k_results', str), ('evaluation_report', str)]):
    import pandas as pd
    import pickle
    import json
    from sklearn.metrics import mean_absolute_error

    with open(clustered_data_path, 'rb') as f:
        df_unique = pickle.load(f)

    with open(model_path, 'rb') as f:
        rf_model = pickle.load(f)

    top_k_products = df_unique.head(k)

    features = ['price', 'available', 'grams', 'cluster']
    X_top_k = top_k_products[features]
    predicted_scores = rf_model.predict(X_top_k)

    top_k_results = top_k_products.copy()
    top_k_results['predicted_score'] = predicted_scores
    top_k_results['score_difference'] = top_k_results['score'] - top_k_results['predicted_score']

    mae = mean_absolute_error(top_k_results['score'], predicted_scores)

    top_k_summary = {
        'top_k_count': int(k),
        'selected_products': [
            {
                'title': row['title'],
                'vendor': row['vendor'],
                'price': float(row['price']),
                'score': float(row['score']),
                'predicted_score': float(row['predicted_score']),
                'cluster': int(row['cluster'])
            }
            for _, row in top_k_results.iterrows()
        ],
        'summary_stats': {
            'average_price': float(top_k_results['price'].mean()),
            'price_range': [float(top_k_results['price'].min()), float(top_k_results['price'].max())],
            'vendor_distribution': top_k_results['vendor'].value_counts().to_dict(),
            'cluster_distribution': top_k_results['cluster'].value_counts().to_dict(),
            'average_score': float(top_k_results['score'].mean())
        }
    }

    evaluation_report = {
        'model_performance': {
            'mean_absolute_error': float(mae),
            'score_correlation': float(top_k_results[['score', 'predicted_score']].corr().iloc[0, 1])
        },
        'business_recommendations': {
            'best_performing_cluster': int(top_k_results.groupby('cluster')['score'].mean().idxmax()),
            'most_represented_vendor': top_k_results['vendor'].mode().iloc[0],
            'optimal_price_range': [
                float(top_k_results[top_k_results['score'] >= top_k_results['score'].quantile(0.8)]['price'].min()),
                float(top_k_results[top_k_results['score'] >= top_k_results['score'].quantile(0.8)]['price'].max())
            ]
        }
    }

    from collections import namedtuple
    output = namedtuple('Outputs', ['top_k_results', 'evaluation_report'])
    return output(json.dumps(top_k_summary, indent=2), json.dumps(evaluation_report, indent=2))