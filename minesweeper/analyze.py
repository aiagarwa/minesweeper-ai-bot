import seaborn as sns
import pandas as pd

df = pd.read_csv(
    './Statistics.csv')
df['mine_density'] = [a / (b * b) for a, b in zip(df['mines'], df['size'])]
df_new = df[df['win_steps'] != 0]
print(df_new.head())
ax = sns.lmplot(x='mine_density', y='win_rate', hue="type", data=df_new)
ax.set(ylim=(0, 1))
ax.savefig(
    './winrate.png')
ax = sns.lmplot(x='mine_density', y='degree of completion', hue="type", data=df_new)
ax.set(ylim=(0, 1))
ax.savefig(
    './compelet.png')
