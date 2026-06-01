frappe.query_reports["Ventas por Sucursal y Día"] = {
	filters: [
		{
			fieldname: "periodo",
			label: __("Período"),
			fieldtype: "Select",
			options: ["Este Mes", "Hoy", "Ayer", "Esta Semana", "Mes Pasado", "Este Año", "Personalizado"].join("\n"),
			default: "Este Mes",
			on_change: function(report) {
				let p = report.get_filter_value("periodo");
				let today = frappe.datetime.get_today();
				if (p === "Hoy") {
					report.set_filter_value("from_date", today);
					report.set_filter_value("to_date", today);
				} else if (p === "Ayer") {
					let ayer = frappe.datetime.add_days(today, -1);
					report.set_filter_value("from_date", ayer);
					report.set_filter_value("to_date", ayer);
				} else if (p === "Esta Semana") {
					report.set_filter_value("from_date", frappe.datetime.week_start());
					report.set_filter_value("to_date", frappe.datetime.week_end());
				} else if (p === "Este Mes") {
					report.set_filter_value("from_date", frappe.datetime.month_start());
					report.set_filter_value("to_date", frappe.datetime.month_end());
				} else if (p === "Mes Pasado") {
					let d = frappe.datetime.str_to_obj(today);
					d.setDate(1); d.setMonth(d.getMonth() - 1);
					let ini = frappe.datetime.obj_to_str(d);
					d.setMonth(d.getMonth() + 1); d.setDate(0);
					let fin = frappe.datetime.obj_to_str(d);
					report.set_filter_value("from_date", ini);
					report.set_filter_value("to_date", fin);
				} else if (p === "Este Año") {
					let year = frappe.datetime.str_to_obj(today).getFullYear();
					report.set_filter_value("from_date", year + "-01-01");
					report.set_filter_value("to_date", today);
				}
			},
		},
		{
			fieldname: "from_date",
			label: __("Desde"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1,
			depends_on: "eval:doc.periodo=='Personalizado'",
		},
		{
			fieldname: "to_date",
			label: __("Hasta"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd: 1,
			depends_on: "eval:doc.periodo=='Personalizado'",
		},
		{
			fieldname: "metric",
			label: __("Métrica"),
			fieldtype: "Select",
			options: "Ventas\nEgresos\nSaldo Final",
			default: "Saldo Final",
		},
		{
			fieldname: "medio_pago_venta",
			label: __("Medio de Pago"),
			fieldtype: "Select",
			options: ["", "Efectivo", "Mercado Pago", "Tarjeta de Crédito", "Tarjeta de Débito"].join("\n"),
			depends_on: "eval:doc.metric=='Ventas'",
		},
		{
			fieldname: "concepto",
			label: __("Concepto"),
			fieldtype: "Select",
			options: [
				"",
				"Gastos Generales",
				"Sueldos",
				"Aportes Obra Social",
				"Pagos ARCA",
				"Cuotas de ARCA",
				"Cuotas de ARBA",
				"Cuotas de Municipio",
				"Patentes de Autos",
				"Pagos Alquileres",
				"Pagos Cheques Bco",
				"Gastos Bancarios",
				"Pago Cuotas Préstamos Bco",
				"Retiros",
				"Imp. Provincial",
			].join("\n"),
			depends_on: "eval:doc.metric=='Egresos'",
		},
		{
			fieldname: "tipo_gasto",
			label: __("Tipo de Gasto"),
			fieldtype: "Select",
			options: ["", "Servicios", "Alquiler", "Nafta", "Comida", "Papelería", "Extras"].join("\n"),
			depends_on: "eval:doc.metric=='Egresos' && doc.concepto=='Gastos Generales'",
		},
		{
			fieldname: "tipo_arca",
			label: __("Tipo"),
			fieldtype: "Select",
			options: ["", "IVA", "Ganancias", "IIBB", "Monotributo", "Autónomos", "Otros"].join("\n"),
			depends_on: "eval:doc.metric=='Egresos' && doc.concepto=='Pagos ARCA'",
		},
		{
			fieldname: "detalle_municipio",
			label: __("Detalle"),
			fieldtype: "Select",
			options: ["", "Aportes Seg. e Higiene", "Cuota municipal", "P. Propaganda"].join("\n"),
			depends_on: "eval:doc.metric=='Egresos' && doc.concepto=='Cuotas de Municipio'",
		},
		{
			fieldname: "estado_cheque",
			label: __("Estado"),
			fieldtype: "Select",
			options: ["", "A pagar", "Pagado"].join("\n"),
			depends_on: "eval:doc.metric=='Egresos' && doc.concepto=='Pagos Cheques Bco'",
		},
		{
			fieldname: "local_egreso",
			label: __("Local"),
			fieldtype: "Select",
			options: ["", "CENTRAL", "GRAND BOURG", "JOSE C. PAZ", "SAN MIGUEL", "PILAR", "DEPÓSITO"].join("\n"),
			depends_on: "eval:doc.metric=='Egresos' && doc.concepto=='Pagos Alquileres'",
		},
		{
			fieldname: "nro_patente",
			label: __("Nº Patente"),
			fieldtype: "Data",
			depends_on: "eval:doc.metric=='Egresos' && doc.concepto=='Patentes de Autos'",
		},
		{
			fieldname: "persona",
			label: __("Persona / Nombre"),
			fieldtype: "Data",
			depends_on: "eval:doc.metric=='Egresos' && ['Sueldos','Retiros'].includes(doc.concepto)",
		},
		{
			fieldname: "banco",
			label: __("Banco"),
			fieldtype: "Data",
			depends_on: "eval:doc.metric=='Egresos' && ['Gastos Bancarios','Pago Cuotas Préstamos Bco'].includes(doc.concepto)",
		},
		{
			fieldname: "concepto_aporte",
			label: __("Concepto"),
			fieldtype: "Data",
			depends_on: "eval:doc.metric=='Egresos' && doc.concepto=='Aportes Obra Social'",
		},
		{
			fieldname: "nro_partida",
			label: __("Nº de Partida"),
			fieldtype: "Data",
			depends_on: "eval:doc.metric=='Egresos' && doc.concepto=='Imp. Provincial'",
		},
	],
};
