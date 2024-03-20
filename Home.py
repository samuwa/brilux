import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px
import functions as fc
import numpy as np
import plotly.graph_objects as go


st.set_page_config(layout="wide")


# session states

if "df_con" not in st.session_state:
    st.session_state.df_con = None

if "df_sin" not in st.session_state:
    st.session_state.df_sin = None

if "df_cxc" not in st.session_state:
    st.session_state.df_cxc = None

if "df_sin_cxc" not in st.session_state:
    st.session_state.df_sin_cxc = None

if "df_pedidos" not in st.session_state:
    st.session_state.df_pedidos = None

if "df_cxc_combinado" not in st.session_state:
    st.session_state.df_cxc_combinado = None



con_factura = st.sidebar.file_uploader("Montar Excel - **Pedidos CON Factura**")
sin_factura = st.sidebar.file_uploader("Montar Excel - **Pedidos SIN Factura**")
c_x_c = st.sidebar.file_uploader("Montar Excel - **CXC**")





if con_factura != None:
    st.session_state.df_con = pd.read_excel(con_factura)
    st.session_state.df_con = st.session_state.df_con[st.session_state.df_con["SOP Type"] == "Pedido"]
    #st.session_state.df_con = st.session_state.df_con[st.session_state.df_con["SOP Type"] == "Factura"]
    st.session_state.df_con["QTY"] = st.session_state.df_con["QTY"].round(0).astype(int)

if sin_factura != None:
    st.session_state.df_sin = pd.read_excel(sin_factura)
    st.session_state.df_sin_cxc = pd.read_excel(sin_factura)
    st.session_state.df_sin = st.session_state.df_sin[st.session_state.df_sin["SOP Type"] == "Pedido"]
    st.session_state.df_sin = st.session_state.df_sin[~st.session_state.df_sin['SOP Number'].astype(str).str.startswith('P')]
    st.session_state.df_sin_cxc = st.session_state.df_sin_cxc[~st.session_state.df_sin_cxc['SOP Number'].astype(str).str.startswith('P')]
    st.session_state.df_sin_cxc = st.session_state.df_sin_cxc[st.session_state.df_sin_cxc["SOP Type"] == "Pedido"]
    st.session_state.df_sin["QTY"] = st.session_state.df_sin["QTY"].round(0).astype(int)

if c_x_c != None:
    st.session_state.df_cxc = pd.read_excel(c_x_c)
    st.session_state.df_cxc = st.session_state.df_cxc[st.session_state.df_cxc["Current Trx Amount"] > 0]
    st.session_state.df_cxc['Current Trx Amount USD'] = st.session_state.df_cxc['Current Trx Amount'] / st.session_state.df_cxc['Exchange Rate']
    st.session_state.df_cxc['Original Trx Amount USD'] = st.session_state.df_cxc['Original Trx Amount'] / st.session_state.df_cxc['Exchange Rate']

if isinstance(st.session_state.df_sin, pd.DataFrame) and isinstance(st.session_state.df_con, pd.DataFrame):

    st.session_state.df_pedidos = fc.reconcile_products(pd.concat([st.session_state.df_con, st.session_state.df_sin], ignore_index=True))

    df = st.session_state.df_pedidos
    
    #df = df[df["SOP Type"] == "Factura"]
    

    df["Compania"] = df["Compania"].apply(fc.keep_until_first_quote)

    adf = df[df["Exchange Rate"] == 0]

    df = df[df["Exchange Rate"] > 1] # Si es 0, entonces es una diferencia de precio o similar

    #df["Exchange Rate"] = df["Exchange Rate"].replace(0,1)

    df['Venta Producto ($)'] = df['Unit Price'] * df['QTY'] / df['Exchange Rate']

    df['Document Date'] = pd.to_datetime(df['Document Date'])
    #df['Document Date'] = df['Document Date'].dt.date
    df['Salesperson ID'] = df['Salesperson ID'].astype(str)

if isinstance(st.session_state.df_sin_cxc, pd.DataFrame) and isinstance(st.session_state.df_cxc, pd.DataFrame):

    st.session_state.df_sin_cxc = st.session_state.df_sin_cxc[st.session_state.df_sin_cxc["SOP Type"] == "Pedido"]
    st.session_state.df_sin_cxc = st.session_state.df_sin_cxc.drop_duplicates(subset='SOP Number', keep='first')
    # st.session_state.df_cxc_combinado =



# Seleccionar un reporte a visualizar
reporte = st.sidebar.selectbox("Selecciona un reporte", ["Diario - Pedidos", "Mensual - Pedidos", "CXC", "Ventas Estrategia", "Ventas SCI", "Análisis Vendedores"])



if reporte == "Diario - Pedidos":


  # Filtrar por compañia
  compania = st.selectbox("Selecciona una compañía", df["Compania"].unique())

  df = df[df["Compania"] == compania]

  df["Document Date"] = pd.to_datetime(df["Document Date"])
  df = df[df['Document Date'].dt.year == 2024]



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



elif reporte == "Mensual - Pedidos":


  compania = st.selectbox("Selecciona una compañía", df["Compania"].unique())

  df = df[df["Compania"] == compania]



  df = df[df['Document Date'].dt.year == 2024]

  st.subheader("Reporte Mensual - Solo Pedidos")

  col1, col2, col3 = st.columns(3)

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

  filtered_data_2 = filtered_data[filtered_data["Item Description"].apply(fc.filter_prefixes)]
  total_qty = filtered_data_2["QTY"].sum()
  col3.metric("Bultos Vendidos (Papel, Servilletas y Toalla)", f"{total_qty:,.0f}")


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

      if len(adf["SOP Number"]) > 0:
        with st.expander("Pedidos sin 'Exchange Rate'"):
            st.write(adf["SOP Number"].unique())

elif reporte == "CXC":

    cxc = st.session_state.df_cxc
    pedidos = st.session_state.df_sin_cxc
    cxc_clean = cxc.dropna(subset=['Exchange Rate', 'Current Trx Amount', 'Original Trx Amount'])
    cxc_clean = cxc_clean[cxc_clean['Exchange Rate'] != 0]



    pedidos_filtered = pedidos[pedidos['SOP Type'] == 'Pedido']
    cxc_clean = cxc_clean[cxc_clean["SOP Type"] == "Factura"]


    # Step 3: Conversion
    cxc_clean['Current Trx Amount USD'] = cxc_clean['Current Trx Amount'] / cxc_clean['Exchange Rate']
    cxc_clean['Original Trx Amount USD'] = cxc_clean['Original Trx Amount'] / cxc_clean['Exchange Rate']
    cxc_clean = cxc_clean[cxc_clean['Current Trx Amount USD'] != 0]

    # Limpieza pedidos



    # Remove duplicates based on SOP Number, keeping the first instance
    pedidos_unique = pedidos_filtered.drop_duplicates(subset=['SOP Number'], keep='first')

    # Convert the 'Subtotal' to USD and rename the column to 'Current Trx Amount USD'
    pedidos_unique['Current Trx Amount USD'] = pedidos_unique['Subtotal'] / pedidos_unique['Exchange Rate']

    # Create 'Original Trx Amount USD' with the same values as 'Current Trx Amount USD'
    pedidos_unique['Original Trx Amount USD'] = pedidos_unique['Current Trx Amount USD']

    # Unir dfs



    pedidos_unique['Due Date'] = np.nan

    # Select columns in cxc_clean that are also in pedidos_unique (and 'Due Date')
    pedidos_unique = pedidos_unique.rename(columns={"SOP Number":"Document Number"})
    common_columns = list(set(pedidos_unique.columns) & set(cxc_clean.columns)) # + ['Due Date']
    # Prepare DataFrames for concatenation by selecting only the common columns
    cxc_prepared = cxc_clean[common_columns]
    pedidos_prepared = pedidos_unique[common_columns]

    # Concatenate the DataFrames
    combined_df = pd.concat([cxc_prepared, pedidos_prepared], ignore_index=True)

    combined_df["Document Date"] = combined_df["Document Date"].dt.date

    compania = st.selectbox("Seleccionar Compañía", combined_df["Compania"].unique())

    combined_df = combined_df[combined_df["Compania"] == compania]

    # print(combined_df)
    # Group by la deuda

    grouped_combined = combined_df.groupby('Customer Name').agg(
        Total_Original_Amount_USD=('Original Trx Amount USD', 'sum'),
        Total_Current_Amount_USD=('Current Trx Amount USD', 'sum')
    ).reset_index()

    # Calculate the percentage of the Original Amount that has been paid
    grouped_combined['Percentage Paid'] = (1 - (grouped_combined['Total_Current_Amount_USD'] / grouped_combined['Total_Original_Amount_USD'])) * 100
    grouped_combined['Percentage Paid'] = grouped_combined['Percentage Paid'].round(0)
    # Sort the results in descending order by 'Current Trx Amount USD'
    grouped_combined_sorted = grouped_combined.sort_values(by='Total_Current_Amount_USD', ascending=False)


    total_current = grouped_combined_sorted["Total_Current_Amount_USD"].sum()
    #st.metric("Total CXC", f"${total_current:,.2f}")

    st.subheader("Resumen de CXC por Cliente")
    grouped_combined_sorted["Total_Original_Amount_USD"] = grouped_combined_sorted["Total_Original_Amount_USD"].round(2)
    grouped_combined_sorted["Total_Current_Amount_USD"] = grouped_combined_sorted["Total_Current_Amount_USD"].round(2)
    
    st.dataframe(grouped_combined_sorted, use_container_width=True)

    #
    # print(grouped_combined_sorted)


    # print(combined_df.columns)

    # Customer detail
    # s
    #print(combined_df)
    #


    today = pd.to_datetime('today')

    difference = today - combined_df['Due Date']



    combined_df['days past due'] = np.where(combined_df['Due Date'].isna(), None, difference.dt.days)





    # Detalles de cliente



    st.subheader("Detalles por Cliente")
    customer_name = st.selectbox("Selecciona un Cliente", combined_df["Customer Name"].unique())
    customer_accounts = combined_df[combined_df["Customer Name"] == customer_name]

    customer_accounts["Current Trx Amount USD"] = customer_accounts["Current Trx Amount USD"].round(2)
    customer_accounts["Original Trx Amount USD"] = customer_accounts["Original Trx Amount USD"].round(2)
    customer_accounts["Document Number"] = customer_accounts["Document Number"].astype(str)


    st.write(f"Deuda acumulada: ${customer_accounts['Current Trx Amount USD'].sum():,.2f}")
    
    
    st.dataframe(customer_accounts[["SOP Type","Document Number","Original Trx Amount USD", "Current Trx Amount USD", "Due Date", "days past due"]], use_container_width=True)


    conditions = [
    (combined_df['days past due'] <= 0) | pd.isnull(combined_df['Due Date']),
    combined_df['days past due'].between(1, 30),
    combined_df['days past due'] > 30
]

    # Names for the categories in Spanish
    categories = ['Vigentes', 'Vencidas', 'Sobre-Vencidas']

    # Assigning category based on conditions
    combined_df['Categoría de Vencimiento'] = np.select(conditions, categories, default='Desconocido')

    # Step 2: Calculate the sum of 'Current Trx Amount USD' for each bucket
    due_sums = combined_df.groupby('Categoría de Vencimiento')['Current Trx Amount USD'].sum().reindex(categories)

    # Step 3: Create a bar chart
    colors = ['green', 'orange', 'red']  # Color for each category

    fig = go.Figure(data=[
        go.Bar(
            x=due_sums.index,
            y=due_sums.values,
            marker_color=colors
        )
    ])

    fig.update_layout(
        title='Suma de Monto de Transacción Actual USD por Categoría de Vencimiento',
        xaxis_title='Categoría de Vencimiento',
        yaxis_title='Suma de Monto de Transacción Actual USD',
        plot_bgcolor='white'
    )

    st.subheader("Resumen de Cuentas por Categoría")
    st.plotly_chart(fig)

    categoria = st.selectbox("Selecciona una categoría", combined_df["Categoría de Vencimiento"].unique())

    combined_df["Document Number"] = combined_df["Document Number"].astype(str)
    combined_df["Original Trx Amount USD"] = combined_df["Original Trx Amount USD"].round(2)
    combined_df["Current Trx Amount USD"] = combined_df["Current Trx Amount USD"].round(2)

    st.dataframe(combined_df[combined_df["Categoría de Vencimiento"] == categoria][["Customer Name", "Document Number", "Original Trx Amount USD", "Current Trx Amount USD","Due Date", "days past due"]], use_container_width=True)
    #[["Customer Name", "Original Trx Amount USD", "Current Trx Amount","Due Date", "days past due"]]

    st.subheader("Todas las cuentas")

    st.dataframe(combined_df[["Customer Name", "Document Number", "Original Trx Amount USD", "Current Trx Amount USD","Due Date", "days past due"]].sort_values("Due Date", ascending=False), use_container_width=True)


elif reporte == "Ventas Estrategia":

    # df1 = pd.read_excel(docs)
    # df2 = pd.read_excel(bdoc)
    #
    # dfs = [df1, df2]
    #
    # df = clean_sales_data(df1, df2)
    #
    # #df = pd.concat(dfs, ignore_index=True)
    #
    # df = reconcile_products(df)
    #
    #
    # df =df[df["SOP Type"] == "Pedido"]
    # df['Compania'] = df['Compania'].apply(keep_until_first_quote)

  # Filtrar por compañia
    compania = st.selectbox("Selecciona una compañía", df["Compania"].unique())

    df = df[df["Compania"] == compania]



    df = df[df["Exchange Rate"] > 0]


  # Fila total = QTY * Precio / Exchange Rate

    df['Venta Producto ($)'] = df['Unit Price'] * df['QTY'] / df['Exchange Rate']

  # Mismo analisis
    df['Document Date'] = pd.to_datetime(df['Document Date'])

    df['Salesperson ID'] = df['Salesperson ID'].astype(str)

    st.subheader('Estrategia de ventas semanal')
    df['Document Date'] = pd.to_datetime(df['Document Date'])

    customer_names = df['Customer Name'].unique()
    selected_customer = st.selectbox("Select a Customer:", customer_names)

    customer_data = df[df['Customer Name'] == selected_customer]

    # Display current month purchases
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_month_purchases = customer_data[(customer_data['Document Date'].dt.month == current_month) &
                                                (customer_data['Document Date'].dt.year == current_year)]

    if not current_month_purchases.empty:
        st.write(f"Current Month Purchases for {selected_customer}:")
        #st.dataframe(current_month_purchases)
        st.dataframe(current_month_purchases[["SOP Number", "Document Date", "Salesperson ID", "Item Description", "Unit Price $", "QTY"]], hide_index=True)
    else:
        st.write("No purchases found for the current month.")

        # Generate and display recommendations
    recommendations = fc.recommend_sales(customer_data, current_month, current_year)
    if not recommendations.empty:
        st.write("Recommended Sales based on Previous Purchases:")
        st.dataframe(recommendations[recommendations["Purchase Instances"] >= 2], hide_index=True)
    else:
        st.write("No recommendations available based on previous purchases.")

elif reporte == "Ventas SCI":

    col1, col2 = st.columns(2)

    now = datetime.now()

    first_day_of_current_month = datetime(now.year, now.month, 1)

    inicio = col1.date_input("Fecha de Inicio", value=first_day_of_current_month)
    cierre = col2.date_input("Fecha de Cierre", value=datetime.today())
    df_viz = fc.preprocess_data(df.copy(), inicio, cierre)

    df_filtered = df_viz[df_viz['Salesperson ID'].str.contains("SCI", na=False)]

    matching_rows = df_viz[~df_viz['Salesperson ID'].str.contains("SCI", na=False)]
    matching_rows = matching_rows[matching_rows["Customer Name"].isin(df_filtered["Customer Name"])]

# Step 3: Append rows
# Append the filtered rows from df1 to df2
    df_filtered = pd.concat([df_filtered, matching_rows], ignore_index=True)

    # Display overall sales metrics based on filtered data
    #st.header("Overall Sales Metrics (Filtered by SCI)")
    ventas_totales = df_filtered['Venta Producto ($)'].sum()
    st.metric("Ventas Totales por SCI", f"${ventas_totales:,.0f}")

    # Group by Salesperson ID (filtered)

    col1, col2 = st.columns([2,4.5])

    col1.subheader("Ventas por vendedor")
    ventas_por_salesperson = df_filtered.groupby('Salesperson ID')['Venta Producto ($)'].sum().reset_index().sort_values(by='Venta Producto ($)', ascending=False)
    ventas_por_salesperson['Venta Producto ($)'] = ventas_por_salesperson['Venta Producto ($)'].apply(lambda x: f"{x:,.0f}")

# Rename 'Venta Producto ($)' to 'Ventas por Vendedor'
    ventas_por_salesperson.rename(columns={'Venta Producto ($)': 'Ventas por Vendedor ($)'}, inplace=True)

# Display the DataFrame
    col1.dataframe(ventas_por_salesperson, hide_index=True)

    # col1.write("El **75%** de las ventas SCI consisten de:")
    # col1.write(" 1. Automercados Plaza")
    # col1.write(" 2. Comercializadora Monti Sin Límites")
    # col1.write(" 3. Redvital")
    # col1.write(" 4. Comercializadora Centro de Guarenas (NUEVO)")
    # col1.write(" 5. Automercados Luz")

    # Group by Customer Name (filtered)
    col2.subheader("Ventas por cliente (por SCI)")
    ventas_por_customer = df_filtered.groupby('Customer Name')['Venta Producto ($)'].sum().reset_index().sort_values(by='Venta Producto ($)', ascending=False)
    ventas_por_customer['Venta Producto ($)'] = ventas_por_customer['Venta Producto ($)'].apply(lambda x: f"{x:,.0f}")

    # Rename 'Venta Producto ($)' to 'Ventas por Vendedor'
    ventas_por_customer.rename(columns={'Venta Producto ($)': 'Ventas por Cliente ($)'}, inplace=True)

    # Display the DataFrame

    df_sorted = df.sort_values(by=['Customer Name', 'Document Date'])

    # Step 2: Determine the first salesperson for each customer
    first_salesperson_per_customer = df_sorted.groupby('Customer Name').first()['Salesperson ID']

    # Step 3: Check if the first salesperson for each customer contains 'SCI'
    customer_discovered_by_sci = first_salesperson_per_customer.str.contains("SCI").reset_index()
    customer_discovered_by_sci.rename(columns={'Salesperson ID': 'Discovered by SCI'}, inplace=True)

    # Step 4: Merge this information back into your 'ventas_por_customer' DataFrame
    # Ensure ventas_por_customer is calculated before this step
    ventas_por_customer = ventas_por_customer.merge(customer_discovered_by_sci, on='Customer Name', how='left')

    # Step 5: Convert the boolean 'Discovered by SCI' column to a more readable format if desired
    ventas_por_customer['Discovered by SCI'] = ventas_por_customer['Discovered by SCI'].map({True: 'Yes', False: 'No'})
    col2.dataframe(ventas_por_customer, hide_index=True, height=900)

    customers_discovered_by_sci_count = ventas_por_customer[ventas_por_customer['Discovered by SCI'] == 'Yes'].shape[0]

    # Calculate the total sales from customers discovered by SCI
    # Ensure that 'Venta Producto ($)' column is in a numeric format for accurate summation

    ventas_por_customer['Ventas por Cliente ($)'] = pd.to_numeric(ventas_por_customer['Ventas por Cliente ($)'].str.replace(',', ''), errors='coerce')
    sales_from_customers_discovered_by_sci_sum = ventas_por_customer[ventas_por_customer['Discovered by SCI'] == 'Yes']['Ventas por Cliente ($)'].sum()

    # Display metrics in Streamlit
    col1.markdown("##")
    col1.metric("Clientes descubiertos por SCI", customers_discovered_by_sci_count)
    col1.metric("Ventas a clientes descubiertos por SCI ($)", f"${sales_from_customers_discovered_by_sci_sum:,.0f}")

elif reporte == "Análisis Vendedores":

    st.header("Análisis Vendedores")
    col1, col2 = st.columns(2)
    selected_salespersons = col1.multiselect('Select Salesperson ID', df['Salesperson ID'].unique())
    selected_date_range = col2.date_input('Select date range', [])
    df['Month/Year'] = df['Document Date'].dt.to_period('M')
    st.divider()
    
    
    if selected_salespersons and selected_date_range:
    
    
    
        # Convert selected_date_range to datetime64[ns]
        start_date = pd.to_datetime(selected_date_range[0])
        end_date = pd.to_datetime(selected_date_range[1])
    
        for salesperson in selected_salespersons:
            st.subheader(f'{salesperson}')
    
            # Filter data for the current salesperson within the selected date range
            filtered_data = df[(df['Salesperson ID'] == salesperson) &
                               (df['Document Date'].between(start_date, end_date))]
    
            # Calculations for the current salesperson
            ## New Customers
            all_time_customers = df[(df['Salesperson ID'] == salesperson) & (df['Document Date'] < start_date)]['Customer Name'].unique()
            new_customers = filtered_data[~filtered_data['Customer Name'].isin(all_time_customers)]
            new_customers_count = new_customers['Customer Name'].nunique()
    
            ## Who New Customers
            who_new_customers = new_customers[['Customer Name', 'Venta $']].groupby('Customer Name').sum().reset_index()
    
            ## Total Sales
            total_sales = filtered_data['Venta $'].sum()
    
            ## Sales per Customer
            sales_per_customer = filtered_data[['Customer Name', 'Venta $']].groupby('Customer Name').sum().reset_index()
    
    
            # Cartera completa
            salesperson_data = df[df["Salesperson ID"] == salesperson]
            cartera_completa = len(salesperson_data["Customer Name"].unique())
    
            # Venta a nuevos clientes
            vanc = who_new_customers["Venta $"].sum()
    
            # numero de clientes vendidos
    
            ncv = len(sales_per_customer["Customer Name"].unique())
            # Display Results for the current salesperson
    
            # Clientes no vendidos
            cnv = df[~df["Customer Name"].isin(sales_per_customer["Customer Name"])]
    
            col1, col2, col3, col4, col5 = st.columns(5)
            col4.metric(f"Clientes Nuevos", new_customers_count)
            col5.metric("Venta CLientes Nuevos", f"$ {vanc:,.0f}")
            col2.metric("Clientes Vendidos", ncv)
            col3.metric("Ventas Totales", f"$ {total_sales:,.0f}")
            col1.metric("Cartera Completa (clientes)", cartera_completa)
            st.markdown("##")
            col1, col2, col3 = st.columns(3)
            col2.write('Ventas de **nuevos clientes**')
            col2.dataframe(who_new_customers.sort_values("Venta $", ascending=False), hide_index=True)
            col1.write('Ventas de **todos los clientes**')
            col1.dataframe(sales_per_customer.sort_values("Venta $", ascending=False), hide_index=True)
            col3.write("CLientes **no vendidos**")
            col3.dataframe(cnv["Customer Name"], hide_index=True)
    
    
            customer_names = salesperson_data['Customer Name'].unique()
    
            with st.expander("Inspección Cliente"):
                selected_customer = st.selectbox(f'Select a customer for historical behavior (Salesperson {salesperson})', customer_names)
                if selected_customer:
                    st.subheader(f'Historical behavior for {selected_customer}')
    
                    # Line chart of sum(Venta $) by months
                    customer_sales = salesperson_data[salesperson_data['Customer Name'] == selected_customer]
                    monthly_sales = customer_sales.groupby('Month/Year')['Venta $'].sum()
    
                    # Table with item description, month/year, and sum(qty)
                    pivot_table = customer_sales.pivot_table(index='Item Description', columns='Month/Year', values='QTY', aggfunc='sum', fill_value=0)
                    st.table(pivot_table)
    
            st.divider()
    
    else:
        st.write('Please select a Salesperson ID and a date range to view the analysis.')






else:
  pass

