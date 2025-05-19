import kfp
from kfp import dsl

def load_data_op():
    return dsl.ContainerOp(
        name='Load Data',
        image='python:3.9',
        command=['sh', '-c'],
        arguments=[
            "pip install pandas && "
            "python3 -c \"import pandas as pd; df = pd.read_csv('data/products_data.csv'); df.to_csv('/tmp/data.csv', index=False)\""
        ],
        file_outputs={'output': '/tmp/data.csv'}
    )

def scoring_op(input_csv):
    return dsl.ContainerOp(
        name='Score Products',
        image='python:3.9',
        command=['sh', '-c'],
        arguments=[
            "pip install pandas scikit-learn && "
            "python3 -c \""
            "import pandas as pd; from sklearn.preprocessing import MinMaxScaler; "
            f"df = pd.read_csv('{input_csv}'); "
            "df['price'] = pd.to_numeric(df['price'], errors='coerce'); "
            "df['available'] = df['available'].astype(int); "
            "df['tags'] = df['tags'].fillna('').apply(lambda x: len(str(x).split(','))); "
            "df['price_norm'] = 1 - MinMaxScaler().fit_transform(df[['price']]); "
            "df['score'] = 0.5 * df['available'] + 0.3 * df['price_norm'] + 0.2 * df['tags']; "
            "df.to_csv('/tmp/scored.csv', index=False)"
            "\""
        ],
        file_outputs={'output': '/tmp/scored.csv'}
    )

def topk_op(input_csv):
    return dsl.ContainerOp(
        name='Select Top-K',
        image='python:3.9',
        command=['sh', '-c'],
        arguments=[
            "pip install pandas && "
            "python3 -c \""
            f"import pandas as pd; df = pd.read_csv('{input_csv}'); "
            "df.sort_values(by='score', ascending=False).head(10).to_csv('/tmp/topk.csv', index=False)"
            "\""
        ],
        file_outputs={'output': '/tmp/topk.csv'}
    )

@dsl.pipeline(
    name='Top-K Product Selector',
    description='Loads products, scores them, and selects top-K.'
)
def topk_pipeline():
    load = load_data_op()
    score = scoring_op(load.output)
    topk = topk_op(score.output)

# Compile it
if __name__ == '__main__':
    kfp.compiler.Compiler().compile(topk_pipeline, 'topk_pipeline_v1.zip')
