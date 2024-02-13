import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px

docs = st.sidebar.file_uploader("Montar Excel - **Pedidos**", accept_multiple_files=True)
adoc = st.sidebar.file_uploader("Montar Excel - **CXC**")

reporte = st.sidebar.selectbox("Selecciona un reporte", ["Diario - Pedidos", "Mensual - Pedidos", "CXC"])

if docs != [] and reporte == "Diario - Pedidos":

  dfs = []

  for doc in docs:
    if doc is not None:
      df = pd.read_excel(doc)
      dfs.append(df)

  df = pd.concat(dfs, ignore_index=True)

  df =df[df["SOP Type"] == "Pedido"]
  
  # Fila total = QTY * Precio / Exchange Rate
  
  df['Venta Producto ($)'] = df['Unit Price'] * df['QTY'] / df['Exchange Rate']
  
  # Mismo analisis
  df['Document Date'] = pd.to_datetime(df['Document Date'])

  df['Salesperson ID'] = df['Salesperson ID'].astype(str)
  
  st.subheader("Reporte del día - Solo Pedidos")
  
  col1, col2 = st.columns(2)
  
  selected_date = col1.date_input("Selecciona un día", value=pd.to_datetime('today'))
  
  filtered_data = df[df['Document Date'].dt.date == selected_date]
  
  # Adapted: Ventas Totales using "Venta Producto ($)"
  total_sales = filtered_data['Venta Producto ($)'].sum()
  col2.metric(label="Ventas Totales", value=f"$ {total_sales:,.0f}")
  
  # Unidades por producto (remains the same)
  st.write("**Unidades Vendidas por Producto**")
  product_qty = filtered_data.groupby('Item Description')['QTY'].sum().reset_index()
  product_qty = product_qty.sort_values("QTY", ascending=False)
  st.table(product_qty)
  
  # Adapted: Ventas por vendedor using "Venta Producto ($)"
  st.write("**Ventas por Vendedor**")
  sales_by_salesperson = filtered_data.groupby('Salesperson ID')['Venta Producto ($)'].sum().reset_index(name='Total Sales Value ($)')
  sales_by_salesperson = sales_by_salesperson.sort_values("Total Sales Value ($)", ascending=False).style.format({'Total Sales Value ($)': '{:,.2f}'})
  st.table(sales_by_salesperson)
  
  # Adapted: Ventas por cliente using "Venta Producto ($)"
  st.write("**Ventas por cliente**")
  sales_by_customer = filtered_data.groupby('Customer Name')['Venta Producto ($)'].sum().reset_index(name='Total Sales Value ($)')
  sales_by_customer = sales_by_customer.sort_values("Total Sales Value ($)", ascending=False).style.format({'Total Sales Value ($)': '{:,.2f}'})
  st.table(sales_by_customer)
  
  # Detalles cliente (remains focused on QTY for product details)
  customer_list = filtered_data["Customer Name"].unique()
  selected_customer = st.selectbox("Selecciona un Cliente", customer_list)
  
  customer_data = filtered_data[filtered_data['Customer Name'] == selected_customer]
  
  salesperson_ids = customer_data['Salesperson ID'].unique()
  salesperson_ids_str = ', '.join(salesperson_ids)
  
  col1, col2 = st.columns([1,5])
  col1.metric(label="Salesperson ID", value=salesperson_ids_str)
  
  # Table of Units Purchased (remains the same)
  product_details = customer_data.groupby('Item Description')['QTY'].sum().reset_index()
  col2.table(product_details.sort_values("QTY", ascending=False))
  


elif docs != [] and reporte == "Mensual - Pedidos":
  dfs = []

  for doc in docs:
    if doc is not None:
      df = pd.read_excel(doc)
      dfs.append(df)

  df = pd.concat(dfs, ignore_index=True)

  df = df[df["SOP Type"] == "Pedido"]
  df['Salesperson ID'] = df['Salesperson ID'].astype(str)

  # Fila total = QTY * Precio / Exchange Rate

  df['Venta Producto ($)'] = df['Unit Price'] * df['QTY'] / df['Exchange Rate']
  
  df['Document Date'] = pd.to_datetime(df['Document Date'])


  st.subheader("Reporte Mensual - Solo Pedidos")
  
  col1, col2 = st.columns(2)
  
  month_to_num = {
      "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
      "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
  }
  selected_month = col1.selectbox("Selecciona un mes", list(month_to_num.keys()))
  selected_month_num = month_to_num[selected_month]
  
  # Filter Data for Selected Month
  filtered_data = df[df['Document Date'].dt.month == selected_month_num]
  
  # Adapted: Ventas Totales using "Venta Producto ($)"
  total_sales = filtered_data['Venta Producto ($)'].sum()
  col2.metric(label="Ventas Totales", value=f"$ {total_sales:,.0f}")
  
  # Unidades por producto (remains the same)
  st.write("**Unidades Vendidas por Producto**")
  product_qty = filtered_data.groupby('Item Description')['QTY'].sum().reset_index()
  product_qty = product_qty.sort_values("QTY", ascending=False)
  st.table(product_qty)
  
  # Adapted: Ventas por vendedor using "Venta Producto ($)"
  st.write("**Ventas por Vendedor**")
  sales_by_salesperson = filtered_data.groupby('Salesperson ID')['Venta Producto ($)'].sum().reset_index(name='Total Sales Value ($)')
  sales_by_salesperson = sales_by_salesperson.sort_values("Total Sales Value ($)", ascending=False).style.format({'Total Sales Value ($)': '{:,.2f}'})
  st.table(sales_by_salesperson)
  
  # Adapted: Ventas por cliente using "Venta Producto ($)"
  st.write("**Ventas por cliente**")
  sales_by_customer = filtered_data.groupby('Customer Name')['Venta Producto ($)'].sum().reset_index(name='Total Sales Value ($)')
  sales_by_customer = sales_by_customer.sort_values("Total Sales Value ($)", ascending=False).style.format({'Total Sales Value ($)': '{:,.2f}'})
  st.table(sales_by_customer)
  
  # Detalles cliente (remains focused on QTY for product details)
  customer_list = filtered_data["Customer Name"].unique()
  selected_customer = st.selectbox("Selecciona un Cliente", customer_list)
  
  customer_data = filtered_data[filtered_data['Customer Name'] == selected_customer]
  
  salesperson_ids = customer_data['Salesperson ID'].unique()
  salesperson_ids_str = ', '.join(salesperson_ids)
  
  col1, col2 = st.columns([1,5])
  col1.metric(label="Salesperson ID", value=salesperson_ids_str)
  
  # Table of Units Purchased (remains the same)
  product_details = customer_data.groupby('Item Description')['QTY'].sum().reset_index()
  col2.table(product_details.sort_values("QTY", ascending=False))

  customer_data['Document Date'] = pd.to_datetime(customer_data['Document Date']).dt.date

  # First, sort the entire DataFrame by 'Document Date' to ensure the dates are in ascending order
  customer_data_sorted = customer_data.sort_values(by='Document Date')
  
  # Then, get unique dates from the sorted DataFrame
  unique_dates = customer_data_sorted['Document Date'].unique()
  
  for date in unique_dates:
      # Filter data for each specific day from the sorted DataFrame
      daily_data = customer_data_sorted[customer_data_sorted['Document Date'] == date]
      
      # Group by 'Item Description' and calculate sum of 'QTY' and 'Venta Producto ($)'
      daily_summary = daily_data.groupby('Item Description').agg({'QTY': 'sum', 'Venta Producto ($)': 'sum'}).reset_index()
      
      # Append a TOTAL row
      total_sales = daily_summary['Venta Producto ($)'].sum()
      total_row = pd.DataFrame([['TOTAL', daily_summary['QTY'].sum(), total_sales]], columns=['Item Description', 'QTY', 'Venta Producto ($)'])
      daily_summary = pd.concat([daily_summary, total_row], ignore_index=True)
      
      # Format the 'Venta Producto ($)' column
      daily_summary['Venta Producto ($)'] = daily_summary.apply(lambda x: f"$ {x['Venta Producto ($)']:,.2f}" if x['Item Description'] == 'TOTAL' else int(x['Venta Producto ($)']), axis=1)
      
      # Ensure 'QTY' column is integer for all but the TOTAL row
      daily_summary['QTY'] = daily_summary['QTY'].astype(int, errors='ignore')
      
      # Display the date and the table
      st.write(f"**{date}**")
      st.table(daily_summary)

elif adoc!= None and reporte == "CXC":


  df = pd.read_excel(adoc)
  def format_currency(val):
      return "{:,.0f}".format(val)
  
  def categorize_transaction(days_past_due):
      if days_past_due <= 0:
          return 'Babies'
      elif 0 < days_past_due <= 20:
          return 'Ripe'
      elif 20 < days_past_due <= 45:
          return 'Danger Zone'
      else:  # days_past_due > 45
          return 'Bugsy Siegel'
  
  
  df['Document Date'] = pd.to_datetime(df['Document Date'])
  
  # Set the minimum document date as the default for the date picker
  min_document_date = df['Document Date'].min()
  
  # Use columns for layout
  col1, col2 = st.columns(2)
  
  selected_date = col1.date_input("Filter results from this date:", min_document_date)
  
  # Filter the DataFrame based on the selected date
  df_filtered = df[df['Document Date'] >= pd.Timestamp(selected_date)]
  
  # Find rows with 'Exchange Rate' equal to 0 in the filtered DataFrame
  invalid_exchange_rates = df_filtered[df_filtered['Exchange Rate'] == 0]
  
  # Create an informational message with the document numbers excluded
  
  
  # Remove rows with 'Exchange Rate' of 0 from the filtered DataFrame
  df_filtered = df_filtered[df_filtered['Exchange Rate'] != 0]
  
  # Perform the conversion on the filtered DataFrame
  df= df[df["Current Trx Amount"] > 0]
  
  df_filtered['Current Trx Amount USD'] = df_filtered['Current Trx Amount'] / df_filtered['Exchange Rate']
  df_filtered['Original Trx Amount USD'] = df_filtered['Original Trx Amount'] / df_filtered['Exchange Rate']
  
  # Calculate the total USD currently owed using the filtered DataFrame
  total_usd_owed = df_filtered['Current Trx Amount USD'].sum()
  
  # Display the metric in Streamlit
  
  col2.metric(label="Total USD Currently Owed", value=f"${total_usd_owed:,.2f}")
  
  # Display the metric in Streamlit
  
  customer_grouped = df_filtered.groupby('Customer Name').agg(
      Total_Original_Amount_USD=('Original Trx Amount USD', 'sum'),
      Total_Current_Amount_USD=('Current Trx Amount USD', 'sum')
  ).reset_index()
  
  # Sort the grouped data in descending order of 'Total_Current_Amount_USD'
  customer_grouped_sorted = customer_grouped.sort_values(by='Total_Current_Amount_USD', ascending=False)
  
  
  customer_grouped_sorted['Percentage Paid'] = (
      (customer_grouped_sorted['Total_Original_Amount_USD'] - customer_grouped_sorted['Total_Current_Amount_USD']) /
      customer_grouped_sorted['Total_Original_Amount_USD']
  ) * 100
  
  # Format the 'Percentage Paid' column to zero decimals and add the percentage sign
  customer_grouped_sorted['Percentage Paid'] = customer_grouped_sorted['Percentage Paid'].apply(lambda x: "{:.0f}%".format(x))
  
  customer_grouped_sorted['Total_Original_Amount_USD'] = customer_grouped_sorted['Total_Original_Amount_USD'].apply(format_currency)
  customer_grouped_sorted['Total_Current_Amount_USD'] = customer_grouped_sorted['Total_Current_Amount_USD'].apply(format_currency)
  
  
  # Now you can display this DataFrame in your Streamlit app
  st.write("Customer Debt Summary", customer_grouped_sorted)
  
  
  # Create a select box of customers
  customer_names = sorted(df_filtered['Customer Name'].unique())
  selected_customer = st.selectbox('Select a Customer', customer_names)
  
  # Filter the DataFrame for the selected customer
  customer_transactions = df_filtered[df_filtered['Customer Name'] == selected_customer].copy()
  
  # Calculate 'Days Past Due' for each transaction
  customer_transactions['Due Date'] = pd.to_datetime(customer_transactions['Due Date'])
  customer_transactions['Days Past Due'] = (datetime.now() - customer_transactions['Due Date']).dt.days.clip(lower=0)
  
  # Format the date columns to exclude time
  customer_transactions['Document Date'] = customer_transactions['Document Date'].dt.strftime('%Y-%m-%d')
  customer_transactions['Due Date'] = customer_transactions['Due Date'].dt.strftime('%Y-%m-%d')
  
  # Format currency columns
  customer_transactions['Original Trx Amount USD'] = customer_transactions['Original Trx Amount USD'].apply(lambda x: "${:,.0f}".format(x))
  customer_transactions['Current Trx Amount USD'] = customer_transactions['Current Trx Amount USD'].apply(lambda x: "${:,.0f}".format(x))
  
  # Display the detailed table for the selected customer
  st.write(f"Transactions for {selected_customer}", customer_transactions[['Document Number', 'Document Date', 'Due Date', 'Original Trx Amount USD', 'Current Trx Amount USD', 'Days Past Due']])
  
  
  
  df_filtered['Due Date'] = pd.to_datetime(df_filtered['Due Date'])
  df_filtered['Days Past Due'] = (pd.to_datetime('today') - df_filtered['Due Date']).dt.days.apply(lambda x: x if x > 0 else 0)
  
  
  
  df_filtered['Category'] = df_filtered['Days Past Due'].apply(categorize_transaction)
  
  # Now, you can display the DataFrame, grouped by the new 'Category' column, or filter it based on the category
  # For example, to display the count of transactions in each category:
  # st.write(df_filtered['Category'].value_counts().reset_index().rename(columns={'index': 'Bucket', 'Category': 'Count'}))
  #
  # # If you want to allow the user to select a category and view transactions in that category:
  # selected_category = st.selectbox('Select a Category', ['Babies', 'Ripe', 'Danger Zone', 'Bugsy Siegel'])
  # filtered_by_category = df_filtered[df_filtered['Category'] == selected_category]
  #
  # # Display the transactions for the selected category
  # st.write(f"Transactions in the {selected_category} category", filtered_by_category)
  
  
  
  category_sums = df_filtered.groupby('Category')['Current Trx Amount USD'].sum().reset_index()
  
  # Specify the custom order for the categories
  category_order = ['Babies', 'Ripe', 'Danger Zone', 'Bugsy Siegel']

  actual_sums = df_filtered.groupby('Category')['Current Trx Amount USD'].sum().reset_index()

  # Define all categories to ensure they are represented, even if not present in the data
  all_categories = ['Babies', 'Ripe', 'Danger Zone', 'Bugsy Siegel']
  
  # Create a DataFrame with all categories to ensure they are included
  all_categories_df = pd.DataFrame(all_categories, columns=['Category'])
  
  # Merge the actual sums with the all categories DataFrame, ensuring all categories are included
  category_sums = all_categories_df.merge(actual_sums, on='Category', how='left').fillna(0)

  
  # Define the color for each category
  category_colors = {
      'Babies': 'green',
      'Ripe': 'yellow',
      'Danger Zone': 'orange',
      'Bugsy Siegel': 'red',
  }
  
  # Create a bar chart with Plotly Express
  fig = px.bar(category_sums,
               x='Category',
               y='Current Trx Amount USD',
               color='Category',
               color_discrete_map=category_colors,
               title="Current Amount Owed by Category")
  
  # Display the plot in Streamlit
  st.plotly_chart(fig)
  
  st.info("Babies = No ha llegado Due Date | Ripe = Menos de 20 días pasados del due date | Danger Zone = Entre 20 y 45 días pasados del due date | Bugsy = mas de 45 días pasados del due date")
  
  category_options = ['Babies', 'Ripe', 'Danger Zone', 'Bugsy Siegel']
  selected_category = st.selectbox('Select a Category:', category_options)
  
  # Filter transactions based on the selected category
  filtered_transactions = df_filtered[df_filtered['Category'] == selected_category]
  
  # Calculate 'Percentage Paid' for the filtered transactions
  filtered_transactions['Percentage Paid'] = (1 - (filtered_transactions['Current Trx Amount USD'] / filtered_transactions['Original Trx Amount USD'])) * 100
  
  # Select and rename columns for display
  columns_to_display = ['Document Number', 'Document Date', 'Customer Name', 'Original Trx Amount USD', 'Current Trx Amount USD', 'Percentage Paid', 'Due Date', 'Days Past Due']
  filtered_transactions_display = filtered_transactions[columns_to_display]
  
  # Format the DataFrame for nicer display
  filtered_transactions_display['Document Date'] = filtered_transactions_display['Document Date'].dt.strftime('%Y-%m-%d')
  filtered_transactions_display['Due Date'] = filtered_transactions_display['Due Date'].dt.strftime('%Y-%m-%d')
  filtered_transactions_display['Original Trx Amount USD'] = filtered_transactions_display['Original Trx Amount USD'].apply(lambda x: "${:,.2f}".format(x))
  filtered_transactions_display['Current Trx Amount USD'] = filtered_transactions_display['Current Trx Amount USD'].apply(lambda x: "${:,.2f}".format(x))
  filtered_transactions_display['Percentage Paid'] = filtered_transactions_display['Percentage Paid'].apply(lambda x: "{:.0f}%".format(x))
  
  # Display the DataFrame
  st.dataframe(filtered_transactions_display)
  
  
  # Create an informational message with the document numbers excluded
  if not invalid_exchange_rates.empty:
      excluded_documents = invalid_exchange_rates['Document Number'].tolist()
      message = f"The following document numbers had no exchange rate and were excluded from the analysis: {excluded_documents}"
      st.info(message)
  

else:
  pass
