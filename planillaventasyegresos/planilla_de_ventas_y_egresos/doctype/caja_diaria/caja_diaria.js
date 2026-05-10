frappe.ui.form.on("Caja Diaria", {
	efectivo: calcular_totales,
	mercado_pago: calcular_totales,
	tarjetas: calcular_totales,
});

frappe.ui.form.on("Detalle Egresos Caja", {
	monto: calcular_totales,
	egresos_remove: calcular_totales,
});

function calcular_totales(frm) {
	let total_ventas = (frm.doc.efectivo || 0) + (frm.doc.mercado_pago || 0) + (frm.doc.tarjetas || 0);
	let total_egresos = (frm.doc.egresos || []).reduce((sum, row) => sum + (row.monto || 0), 0);

	frm.set_value("total_ventas", total_ventas);
	frm.set_value("total_egresos", total_egresos);
	frm.set_value("saldo_final", total_ventas - total_egresos);
}
