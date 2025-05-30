import kfp
from kfp.compiler import Compiler
from pipeline_definition import ecommerce_pipeline

Compiler().compile(
    pipeline_func=ecommerce_pipeline,
    package_path='ecommerce_ml_pipeline.yaml'
)

print("✅ Pipeline compiled to ecommerce_ml_pipeline.yaml")
