from kfp.dsl import OutputPath

def load_data(output_csv: OutputPath(str)):
    import pandas as pd
    df = pd.read_csv("data/products_data.csv")
    df.to_csv(output_csv, index=False)