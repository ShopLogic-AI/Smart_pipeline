from kfp import dsl
from build_components import scraping_op, processing_op, training_op, top_k_op

@dsl.pipeline(
    name='ecommerce-ml-pipeline',
    description='Pipeline for eCommerce scraping, scoring, and top-k selection'
)

def ecommerce_pipeline(
    db_host: str = 'localhost',
    db_user: str = 'root',
    db_password: str = '',
    db_name: str = 'ecommerce_data',
    domains_json: str = '["rowingblazers.com", "glossier.com"]',
    n_clusters: int = 3,
    k: int = 10
):
    # Étape 1 : Scraping
    scraping = scraping_op(
        domains_json=domains_json,
        db_host=db_host,
        db_user=db_user,
        db_password=db_password,
        db_name=db_name
    ).set_display_name("Web Scraping")

    # Étape 2 : Prétraitement
    processing = processing_op(
        db_host=db_host,
        db_user=db_user,
        db_password=db_password,
        db_name=db_name
    ).set_display_name("Data Processing").after(scraping)

    # Étape 3 : Entraînement
    training = training_op(
        processed_data_path=processing.outputs["processed_data_path"],
        n_clusters=n_clusters
    ).set_display_name("ML Training").after(processing)

    # Étape 4 : Sélection Top-K
    top_k = top_k_op(
        clustered_data_path=training.outputs["clustered_data_path"],
        model_path=training.outputs["model_path"],
        k=k
    ).set_display_name("Top-K Selection").after(training)
