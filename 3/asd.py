import pandas as pd

# Sample data
data = {
    'Category': ['A', 'A', 'B', 'B', 'C', 'C'],
    'Subcategory': ['X', 'Y', 'X', 'Y', 'X', 'Y'],
    'Values': [10, 20, 30, 40, 50, 60]
}

df = pd.DataFrame(data)

# Create a pivot table
pivot_table = pd.pivot_table(
    df,
    values='Values',
    index='Category',
    columns='Subcategory',
    aggfunc='sum'
)

# Calculate subtotals for each category
subtotals = pivot_table.sum(axis=1).rename('Subtotal')

# Append the subtotals to the pivot table
pivot_table = pivot_table.join(subtotals)

# Optionally, add a grand total row
grand_total = pivot_table.sum().rename('Grand Total')
approw = df[['Views','Impressions']].sum().rename('Grand Total')
pd.concat([df, approw.to_frame().T]).fillna('')

print(pivot_table)