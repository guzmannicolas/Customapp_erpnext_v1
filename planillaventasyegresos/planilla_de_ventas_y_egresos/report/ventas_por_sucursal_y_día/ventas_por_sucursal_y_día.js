frappe.query_reports["Ventas por Sucursal y Día"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("Desde"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("Hasta"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "metric",
			label: __("Mostrar en gráfico"),
			fieldtype: "Select",
			options: "Ventas\nSaldo Final",
			default: "Saldo Final",
		},
	],
};
