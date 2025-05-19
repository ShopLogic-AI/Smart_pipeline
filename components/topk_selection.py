from kfp.dsl import InputPath, OutputPath

def select_top_k(input_csv: InputPath(str), output_csv: OutputPath(str), k: int = 10):
    import pandas as pd
    df = pd.read_csv(input_csv)
    top_k = df.sort_values(by='score', ascending=False).head(k)
    top_k.to_csv(output_csv, index=False)
