frappe.query_reports["Libro de Caja"] = {
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
			fieldname: "local",
			label: __("Local"),
			fieldtype: "Select",
			options: ["", "CENTRAL", "GRAND BOURG", "JOSE C. PAZ", "SAN MIGUEL", "PILAR", "DEPÓSITO"].join("\n"),
		},
	],
};
