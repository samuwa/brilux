import pandas as pd


def clean_sales_data(df1, df2):
    """
    Cleans sales data by concatenating two DataFrames, standardizing 'Compania' values,
    filtering out rows with 'Exchange Rate' as 0 or NaN, keeping only rows with 'SOP Type' as "Pedido",
    and adjusting 'Unit Price' by the 'Exchange Rate'. The adjusted unit price is stored
    in a new column named "Unit Price $".

    Parameters:
    - df1, df2 (pd.DataFrame): The two DataFrames to be cleaned and merged.

    Returns:
    - pd.DataFrame: The cleaned DataFrame.
    """
    # Concatenate the two DataFrames
    df_combined = pd.concat([df1, df2], ignore_index=True)

    # Standardize 'Compania' values
    df_combined['Compania'] = df_combined['Compania'].apply(keep_until_first_quote)

    # Remove rows where 'Exchange Rate' is 0 or NaN
    df_filtered = df_combined[(df_combined['Exchange Rate'] != 0) & (df_combined['Exchange Rate'].notna())]

    # Filter 'SOP Type' to keep only "Pedido"
    # df_filtered = df_filtered[df_filtered['SOP Type'] == "Pedido"]  || Se elimina esto porque ahora se ven facturas.

    # Ensure 'Unit Price' and 'Exchange Rate' are numeric
    df_filtered['Unit Price'] = pd.to_numeric(df_filtered['Unit Price'], errors='coerce')
    df_filtered['Subtotal'] = pd.to_numeric(df_filtered['Subtotal'], errors='coerce')
    df_filtered['Exchange Rate'] = pd.to_numeric(df_filtered['Exchange Rate'], errors='coerce')

    # Adjust 'Unit Price' by the 'Exchange Rate' and rename to "Unit Price $"
    df_filtered['Unit Price $'] = df_filtered['Unit Price'] / df_filtered['Exchange Rate']
    df_filtered['Subtotal $'] = df_filtered['Subtotal'] / df_filtered['Exchange Rate']

    return df_filtered




# Cambiar productos llamados mal
def reconcile_products(df):
    # Mapping of adapted names to original names and conversion factors
    name_map = {
        'Servilletas BRILUX Disp. Pequeño .200': 'Servilletas BRILUX Disp. Peq. 16X200',
        'Papel Higiénico Cherry 300 H': 'Papel Higiénico Cherry 300 12x4',
        'Papel Higiénico TESSA 800- 200H': 'Papel Higiénico TESSA 800 12x4',
        'Papel Higiénico TESSA 1200- 300H': 'Papel Higiénico TESSA 1200 12x4',
        'Servilletas BRILUX De Mesa 100': 'Servilletas BRILUX De Mesa 12X100',
        'Toalla BRILUX Intercalada Blanca 180': 'Toalla BRILUX Intercalada Blanca 12X180'
    }

    conversion_factors = {
        'Servilletas BRILUX Disp. Pequeño .200': 16,
        'Papel Higiénico Cherry 300 H': 12,
        'Papel Higiénico TESSA 800- 200H': 12,
        'Papel Higiénico TESSA 1200- 300H': 12,
        'Servilletas BRILUX De Mesa 100': 12,
        'Toalla BRILUX Intercalada Blanca 180': 12
    }

    # Iterate over the DataFrame rows
    for index, row in df.iterrows():
        # Use "Item Description" instead of "Product"
        if row['Item Description'] in name_map:
            # Update the item description to the original name
            df.at[index, 'Item Description'] = name_map[row['Item Description']]
            # Adjust the quantity by dividing it by the conversion factor and round to 0 decimals
            df.at[index, 'QTY'] = round(row['QTY'] / conversion_factors[row['Item Description']], 0)
            # Multiply the Unit Price by the conversion factor for the same row
            df.at[index, 'Unit Price'] = round(row['Unit Price'] * conversion_factors[row['Item Description']], 2)

    return df

def keep_until_first_quote(string):
  return string[:string.find("C.A")]

def recommend_sales(customer_data, current_month, current_year):
    past_purchases = customer_data[(customer_data['Document Date'].dt.month != current_month) |
                                   (customer_data['Document Date'].dt.year != current_year)]

    if past_purchases.empty:
        return pd.DataFrame()

    aggregation = {
        'QTY': ['mean', 'count'],
        'Document Date': ['max', lambda x: (pd.Timestamp('now') - max(x)).days,
                          lambda x: (x.max() - x.min()).days / len(x.unique()) if len(x.unique()) > 1 else 0]
    }
    item_metrics = past_purchases.groupby('Item Description').agg(aggregation)
    item_metrics.columns = ['Benchmark Quantity', 'Purchase Instances', 'Last Purchase Date',
                            'Days Since Last Purchase', 'Avg Days Between Purchases']

    current_month_items = customer_data[(customer_data['Document Date'].dt.month == current_month) &
                                        (customer_data['Document Date'].dt.year == current_year)]['Item Description'].unique()
    recommended_items = item_metrics[~item_metrics.index.isin(current_month_items)].reset_index()

    recommended_items = recommended_items[['Item Description', 'Benchmark Quantity', 'Purchase Instances',
                                           'Avg Days Between Purchases', 'Days Since Last Purchase']]

    return recommended_items


def filter_prefixes(description):
    prefixes = ['Papel', 'Servilletas', 'Toalla']
    return any(description.startswith(prefix) for prefix in prefixes)


def preprocess_data(df, inicio, cierre):
    # Convert 'Document Date' to datetime format
    # df['Document Date'] = df.apply(lambda x: x['Order Date'] if x['Order Date'] != pd.Timestamp('1900-01-01') else x['Document Date'], axis=1)
    # df = df[df['SOP Type'] == "Factura"]
    df['Document Date'] = pd.to_datetime(df['Document Date'])
    # df = df[df["Document Date"] >= "20240201"]
    # df = df[df["Document Date"] <= "20240301"]

    inicio = pd.to_datetime(inicio)
    cierre = pd.to_datetime(cierre)
    df = df[df["Document Date"] >= inicio]
    df = df[df["Document Date"] <= cierre]
    # Calculate 'Venta Producto ($)'
    df['Venta Producto ($)'] = df['Unit Price'] * df['QTY'] / df['Exchange Rate']

    # Use a case-insensitive regular expression to replace variations of "AUTOMERCADOS PLAZA'S"
    # This will match "AUTOMERCADOS PLAZA'S" and any characters that follow, replacing it with "Automercados Plaza"
    df['Customer Name'] = df['Customer Name'].str.replace(r"(?i)AUTOMERCADOS PLAZA.*", "Automercados Plaza", regex=True)

    # Filter rows where 'SOP Type' is "Factura"
    

    return df
