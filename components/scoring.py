from kfp.dsl import InputPath, OutputPath

def score_products(input_csv: InputPath(str), output_csv: OutputPath(str)):
    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler

    df = pd.read_csv(input_csv)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['available'] = df['available'].astype(int)
    df['tags'] = df['tags'].fillna('').apply(lambda x: len(str(x).split(',')))
    scaler = MinMaxScaler()
    df['price_norm'] = 1 - scaler.fit_transform(df[['price']])
    df['score'] = 0.5 * df['available'] + 0.3 * df['price_norm'] + 0.2 * df['tags']
    df.to_csv(output_csv, index=False)
