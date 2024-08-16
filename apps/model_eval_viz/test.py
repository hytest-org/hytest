import pandas as pd
streamgages_path = "./data/streamflow_gages_v1_n5390.csv"
df = pd.read_csv(streamgages_path)
print("shape df", df.shape)
print(df.columns)
filt_df = df.loc[df.swim == 1]
print("shape filt_df", filt_df.shape)
