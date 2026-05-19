import pandas as pd

df = pd.read_csv('data/GSE5281_series_matrix.txt', 
                  sep='\t', 
                  comment='!',
                  index_col=0)

# Flip it so patients are rows, genes are columns
df = df.T

# Reset index so sample IDs become a regular column, then drop them
df = df.reset_index(drop=True)

# Convert everything to numeric, drop anything that won't convert
df = df.apply(pd.to_numeric, errors='coerce')
df = df.dropna(axis=1)

# Keep first 500 genes to start
df = df.iloc[:, :500]

print(df.shape)
print(df.dtypes.value_counts())
df.to_csv('data/GSE5281_ready.csv', index=False)
print("Done")