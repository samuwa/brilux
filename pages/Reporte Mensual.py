import pandas as pd
import streamlit as st
import Home

# File Uploader

df = pd.read_excel(Home.doc)

df['Document Date'] = pd.to_datetime(df['Document Date'])

st.subheader("Reporte del día")

col1, col2 = st.columns(2)

month_to_num = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
    "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}
selected_month = col1.selectbox("Selecciona un mes", list(month_to_num.keys()))
selected_month_num = month_to_num[selected_month]

# Filter Data for Selected Month
filtered_data = df[df['Document Date'].dt.month == selected_month_num]

# Ventas Totales
total_sales = filtered_data['Unit Price'].multiply(filtered_data['QTY']).sum()
col2.metric(label="Ventas Totales", value=f"Bs. {total_sales:,.0f}")

# Unidades por producto
st.write("**Unidades Vendidas por Producto**")
product_qty = filtered_data.groupby('Item Description')['QTY'].sum().reset_index()
product_qty = product_qty.sort_values("QTY", ascending=False)
st.table(product_qty)

# Ventas por vendedor
st.write("**Ventas por Vendedor**")
sales_by_salesperson = filtered_data.groupby('Salesperson ID').apply(lambda x: (x['Unit Price'] * x['QTY']).sum()).reset_index(name='Total Product Value (Bs)')
sales_by_salesperson = sales_by_salesperson.sort_values("Total Product Value (Bs)", ascending=False).style.format({'Total Product Value (Bs)': '{:,.2f}'})
st.table(sales_by_salesperson)

# Ventas por cliente
st.write("**Ventas por cliente**")
sales_by_customer = filtered_data.groupby('Customer Name').apply(lambda x: (x['Unit Price'] * x['QTY']).sum()).reset_index(name='Total Product Value (BS)')
sales_by_customer = sales_by_customer.sort_values("Total Product Value (BS)", ascending=False).style.format({'Total Product Value (BS)': '{:,.2f}'})
st.table(sales_by_customer)

# Detalles cliente
customer_list = filtered_data["Customer Name"].unique()
selected_customer = st.selectbox("Selecciona un Cliente", customer_list)

customer_data = filtered_data[filtered_data['Customer Name'] == selected_customer]

salesperson_ids = customer_data['Salesperson ID'].unique()
salesperson_ids_str = ', '.join(salesperson_ids)

col1, col2 = st.columns([1,5])
col1.metric(label="Salesperson ID", value=salesperson_ids_str)

# Table of Units Purchased
product_details = customer_data.groupby('Item Description')['QTY'].sum().reset_index()
col2.table(product_details.sort_values("QTY", ascending=False))

