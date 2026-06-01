frappe.ui.form.on("Caja Diaria", {
	efectivo: calcular_totales,
	mercado_pago: calcular_totales,
	tarjeta_credito: calcular_totales,
	tarjeta_debito: calcular_totales,
});

frappe.ui.form.on("Detalle Egresos Caja", {
	egresos_add: function(frm, cdt, cdn) {
		setTimeout(function() {
			var row = frm.fields_dict["egresos"].grid.grid_rows_by_docname[cdn];
			if (row) row.toggle_view(true);
		}, 100);
	},
	monto: calcular_totales,
	egresos_remove: calcular_totales,
	serv_agua: sumar_servicios,
	serv_luz: sumar_servicios,
	serv_gas: sumar_servicios,
	serv_internet: sumar_servicios,
});

function calcular_totales(frm) {
	let total_ventas = (frm.doc.efectivo || 0) + (frm.doc.mercado_pago || 0) + (frm.doc.tarjeta_credito || 0) + (frm.doc.tarjeta_debito || 0);
	let total_egresos = (frm.doc.egresos || []).reduce((sum, row) => sum + (row.monto || 0), 0);

	frm.set_value("total_ventas", total_ventas);
	frm.set_value("total_egresos", total_egresos);
	frm.set_value("saldo_final", total_ventas - total_egresos);
}

// Gastos Generales > Servicios: el monto de la fila = suma de los 4 servicios
function sumar_servicios(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.concepto === "Gastos Generales" && row.tipo_gasto === "Servicios") {
		row.monto = (row.serv_agua || 0) + (row.serv_luz || 0) + (row.serv_gas || 0) + (row.serv_internet || 0);
		frm.refresh_field("egresos");
	}
	calcular_totales(frm);
}
