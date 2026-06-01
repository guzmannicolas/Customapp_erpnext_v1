# Copyright (c) 2026, Zepe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, get_first_day, formatdate
from datetime import datetime, timedelta


class CajaDiaria(Document):
	def validate(self):
		self.total_ventas = (
			(self.efectivo or 0) +
			(self.mercado_pago or 0) +
			(self.tarjeta_credito or 0) +
			(self.tarjeta_debito or 0)
		)
		# Gastos Generales > Servicios: el monto es la suma de los 4 servicios
		for row in (self.egresos or []):
			if row.concepto == "Gastos Generales" and row.tipo_gasto == "Servicios":
				row.monto = (
					(row.serv_agua or 0) + (row.serv_luz or 0) +
					(row.serv_gas or 0) + (row.serv_internet or 0)
				)
		self.total_egresos = sum(row.monto or 0 for row in (self.egresos or []))
		self.saldo_final = self.total_ventas - self.total_egresos


def _get_week_range():
	today = datetime.now().date()
	monday = today - timedelta(days=today.weekday())
	sunday = monday + timedelta(days=6)
	return monday, sunday


def _get_cajas(desde, hasta, local=None):
	"""Cajas en un rango de fechas, opcionalmente filtradas por sucursal."""
	filters = [["fecha", ">=", desde], ["fecha", "<=", hasta]]
	if local:
		filters.append(["local", "=", local])
	return frappe.get_list(
		"Caja Diaria",
		fields=["total_ventas", "total_egresos", "saldo_final"],
		filters=filters,
	)


def _get_cajas_semana():
	monday, sunday = _get_week_range()
	return _get_cajas(monday, sunday)


def _resolve_rango(rango):
	"""Traduce un rango ('hoy' | 'semana' | 'mes') a fechas desde/hasta."""
	today = getdate(nowdate())
	if rango == "hoy":
		return today, today
	if rango == "mes":
		return get_first_day(today), today
	# 'semana' (default): lunes a domingo de la semana actual
	monday = today - timedelta(days=today.weekday())
	return monday, monday + timedelta(days=6)


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


def _get_cajas_hoy():
	desde, hasta = _resolve_rango("hoy")
	return _get_cajas(desde, hasta)


@frappe.whitelist()
def get_ventas_hoy():
	cajas = _get_cajas_hoy()
	return {"value": sum(c.get("total_ventas") or 0 for c in cajas), "fieldtype": "Currency"}


@frappe.whitelist()
def get_egresos_hoy():
	cajas = _get_cajas_hoy()
	return {"value": sum(c.get("total_egresos") or 0 for c in cajas), "fieldtype": "Currency"}


@frappe.whitelist()
def get_saldo_hoy():
	cajas = _get_cajas_hoy()
	ventas = sum(c.get("total_ventas") or 0 for c in cajas)
	egresos = sum(c.get("total_egresos") or 0 for c in cajas)
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


@frappe.whitelist()
def get_resumen(rango="semana", local=None):
	"""Resumen de ventas/egresos/saldo para un rango y sucursal elegibles.

	rango: 'hoy' | 'semana' | 'mes'
	local: 'Sucursal N' o vacío/'Todas' para sumar todas.
	"""
	if local in (None, "", "Todas"):
		local = None
	desde, hasta = _resolve_rango(rango)
	cajas = _get_cajas(desde, hasta, local)
	total_ventas = sum(c.get("total_ventas") or 0 for c in cajas)
	total_egresos = sum(c.get("total_egresos") or 0 for c in cajas)
	return {
		"ventas": total_ventas,
		"egresos": total_egresos,
		"saldo": total_ventas - total_egresos,
		"desde": formatdate(desde, "dd/MM/yyyy"),
		"hasta": formatdate(hasta, "dd/MM/yyyy"),
		"dias_registrados": len(cajas),
	}
