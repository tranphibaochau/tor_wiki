import pandas as pd
import numpy as np
pd.set_option('display.max_rows', 500)

df = pd.read_csv("/Users/nevermoar/Documents/tor_wiki/tor_wikipedia_edits-20180218.tsv", sep="\t")
df['datetime'] = pd.to_datetime(df['datetime'])
mask = (df['datetime'] >= '2014-07-27') & (df['datetime'] < '2014-08-24')
print(df.loc[mask])