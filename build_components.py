from kfp.components import create_component_from_func
from components.web_scraping import web_scraping_component
from components.data_processing import data_processing_component
from components.ml_training import ml_training_component
from components.top_k_selection import top_k_selection_component

scraping_op = create_component_from_func(
    web_scraping_component,
    base_image='python:3.9',
    packages_to_install=['mysql-connector-python', 'beautifulsoup4', 'requests', 'pandas']
)

processing_op = create_component_from_func(
    data_processing_component,
    base_image='python:3.9',
    packages_to_install=['pandas', 'mysql-connector-python', 'scikit-learn']
)

training_op = create_component_from_func(
    ml_training_component,
    base_image='python:3.9',
    packages_to_install=['pandas', 'scikit-learn']
)

top_k_op = create_component_from_func(
    top_k_selection_component,
    base_image='python:3.9',
    packages_to_install=['pandas', 'scikit-learn']
)
