frappe.query_reports["Ventas por Local y Mes"] = {
	filters: [
		{
			fieldname: "year",
			label: __("Año"),
			fieldtype: "Int",
			default: new Date().getFullYear(),
			reqd: 1,
		},
		{
			fieldname: "metric",
			label: __("Métrica"),
			fieldtype: "Select",
			options: "Ventas\nSaldo Final",
			default: "Ventas",
		},
	],
};
