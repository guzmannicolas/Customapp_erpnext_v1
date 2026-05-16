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


def _get_week_range():
	today = datetime.now().date()
	monday = today - timedelta(days=today.weekday())
	sunday = monday + timedelta(days=6)
	return monday, sunday


def _get_cajas_semana():
	monday, sunday = _get_week_range()
	return frappe.get_list(
		"Caja Diaria",
		fields=["total_ventas", "total_egresos", "saldo_final"],
		filters=[["fecha", ">=", monday], ["fecha", "<=", sunday]],
	)


@frappe.whitelist()
def get_ventas_semanales():
	cajas = _get_cajas_semana()
	return {"value": sum(c.get("total_ventas", 0) for c in cajas), "fieldtype": "Currency"}


@frappe.whitelist()
def get_egresos_semanales():
	cajas = _get_cajas_semana()
	return {"value": sum(c.get("total_egresos", 0) for c in cajas), "fieldtype": "Currency"}


@frappe.whitelist()
def get_saldo_semanal():
	cajas = _get_cajas_semana()
	ventas = sum(c.get("total_ventas", 0) for c in cajas)
	egresos = sum(c.get("total_egresos", 0) for c in cajas)
	return {"value": ventas - egresos, "fieldtype": "Currency"}


@frappe.whitelist()
def get_weekly_summary():
	cajas = _get_cajas_semana()
	monday, sunday = _get_week_range()
	total_ventas = sum(c.get("total_ventas", 0) for c in cajas)
	total_egresos = sum(c.get("total_egresos", 0) for c in cajas)
	return {
		"total_ventas": total_ventas,
		"total_egresos": total_egresos,
		"saldo_neto": total_ventas - total_egresos,
		"fecha_inicio": monday.strftime("%d/%m"),
		"fecha_fin": sunday.strftime("%d/%m"),
		"dias_registrados": len(cajas),
	}
