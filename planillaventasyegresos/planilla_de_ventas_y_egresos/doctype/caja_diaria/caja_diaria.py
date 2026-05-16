# Copyright (c) 2026, Zepe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta


class CajaDiaria(Document):
	def validate(self):
		self.total_ventas = (
			(self.efectivo or 0) +
			(self.mercado_pago or 0) +
			(self.tarjetas or 0)
		)
		self.total_egresos = sum(row.monto or 0 for row in (self.egresos or []))
		self.saldo_final = self.total_ventas - self.total_egresos


@frappe.whitelist()
def get_weekly_summary():
	today = datetime.now().date()
	weekday = today.weekday()
	monday = today - timedelta(days=weekday)
	sunday = monday + timedelta(days=6)

	cajas = frappe.get_list(
		"Caja Diaria",
		fields=["total_ventas", "total_egresos", "saldo_final"],
		filters=[["fecha", ">=", monday], ["fecha", "<=", sunday]],
		order_by="fecha asc"
	)

	total_ventas = sum(caja.get("total_ventas", 0) for caja in cajas)
	total_egresos = sum(caja.get("total_egresos", 0) for caja in cajas)
	saldo_neto = total_ventas - total_egresos

	return {
		"total_ventas": total_ventas,
		"total_egresos": total_egresos,
		"saldo_neto": saldo_neto,
		"fecha_inicio": monday.strftime("%d/%m"),
		"fecha_fin": sunday.strftime("%d/%m"),
		"dias_registrados": len(cajas)
	}
