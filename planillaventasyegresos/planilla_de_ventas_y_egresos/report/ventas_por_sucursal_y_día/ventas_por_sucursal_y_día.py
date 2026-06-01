import frappe  # type: ignore[import]
import re
from datetime import date, timedelta

# métrica -> (sufijo de fieldname, etiqueta a mostrar)
METRICAS = {
	"Ventas": ("_ventas", "Ventas"),
	"Egresos": ("_egresos", "Egresos"),
	"Saldo Final": ("_saldo", "Saldo"),
}


def _locales():
	"""Locales reales desde las opciones del campo `local` (robusto a renombres)."""
	opts = frappe.get_meta("Caja Diaria").get_field("local").options or ""
	return [o.strip() for o in opts.split("\n") if o.strip()]


def _key(nombre):
	"""fieldname seguro a partir del nombre del local."""
	return re.sub(r"[^a-z0-9]+", "_", (nombre or "").lower()).strip("_")


def _resolve_periodo(filters):
	"""Rellena from_date/to_date según el campo periodo (salvo Personalizado)."""
	periodo = filters.get("periodo") or "Este Mes"
	if periodo == "Personalizado":
		return
	hoy = date.today()
	if periodo == "Hoy":
		filters["from_date"] = filters["to_date"] = hoy
	elif periodo == "Ayer":
		ayer = hoy - timedelta(days=1)
		filters["from_date"] = filters["to_date"] = ayer
	elif periodo == "Esta Semana":
		filters["from_date"] = hoy - timedelta(days=hoy.weekday())
		filters["to_date"] = hoy
	elif periodo == "Este Mes":
		filters["from_date"] = hoy.replace(day=1)
		filters["to_date"] = hoy
	elif periodo == "Mes Pasado":
		primer_dia = hoy.replace(day=1)
		ultimo_mes = primer_dia - timedelta(days=1)
		filters["from_date"] = ultimo_mes.replace(day=1)
		filters["to_date"] = ultimo_mes
	elif periodo == "Este Año":
		filters["from_date"] = hoy.replace(month=1, day=1)
		filters["to_date"] = hoy


def execute(filters=None):
	filters = filters or {}
	_resolve_periodo(filters)
	metric = filters.get("metric") or "Saldo Final"
	locales = _locales()
	return get_columns(metric, locales), get_data(filters, locales)


def get_columns(metric, locales):
	suffix, label_tipo = METRICAS.get(metric, METRICAS["Saldo Final"])

	columns = [{"label": "Fecha", "fieldname": "fecha", "fieldtype": "Date", "width": 110}]
	for s in locales:
		columns.append({
			"label": f"{s} - {label_tipo}",
			"fieldname": f"{_key(s)}{suffix}",
			"fieldtype": "Currency",
			"width": 140,
		})
	columns.append({
		"label": f"Total {label_tipo}",
		"fieldname": f"total{suffix}",
		"fieldtype": "Currency",
		"width": 140,
	})
	return columns


def get_data(filters, locales):
	# condiciones de fecha (separadas para la caja y para el detalle de egresos)
	date_caja = ""
	date_eg = ""
	if filters.get("from_date"):
		date_caja += " AND fecha >= %(from_date)s"
		date_eg += " AND c.fecha >= %(from_date)s"
	if filters.get("to_date"):
		date_caja += " AND fecha <= %(to_date)s"
		date_eg += " AND c.fecha <= %(to_date)s"

	# ventas: soporta subfiltro por medio de pago
	medio = filters.get("medio_pago_venta")
	if medio == "Efectivo":
		ventas_col = "COALESCE(efectivo, 0)"
	elif medio == "Mercado Pago":
		ventas_col = "COALESCE(mercado_pago, 0)"
	elif medio == "Tarjeta de Crédito":
		ventas_col = "COALESCE(tarjeta_credito, 0)"
	elif medio == "Tarjeta de Débito":
		ventas_col = "COALESCE(tarjeta_debito, 0)"
	else:
		ventas_col = "COALESCE(total_ventas, 0)"

	cajas = frappe.db.sql(
		f"""
		SELECT fecha, local,
			{ventas_col}              AS ventas,
			COALESCE(saldo_final, 0)  AS saldo
		FROM `tabCaja Diaria`
		WHERE docstatus < 2 {date_caja}
		""",
		filters,
		as_dict=True,
	)

	# egresos: del detalle, con filtros OPCIONALES por concepto y subconcepto.
	# Los subfiltros son campos YA EXISTENTES del detalle; solo se aplica el que venga seteado.
	eg_cond = ""
	if filters.get("concepto"):
		eg_cond += " AND e.concepto = %(concepto)s"
	for fn in ("tipo_gasto", "tipo_arca", "detalle_municipio", "estado_cheque",
			"local_egreso", "persona", "banco", "nro_patente", "concepto_aporte", "nro_partida"):
		if filters.get(fn):
			eg_cond += f" AND e.{fn} = %({fn})s"

	egresos = frappe.db.sql(
		f"""
		SELECT c.fecha AS fecha, c.local AS local, SUM(COALESCE(e.monto, 0)) AS egresos
		FROM `tabDetalle Egresos Caja` e
		JOIN `tabCaja Diaria` c ON c.name = e.parent
		WHERE c.docstatus < 2 {date_eg} {eg_cond}
		GROUP BY c.fecha, c.local
		""",
		filters,
		as_dict=True,
	)

	keys = {s: _key(s) for s in locales}

	def _ensure(fecha_obj):
		f = str(fecha_obj)
		if f not in pivot:
			pivot[f] = {"fecha": fecha_obj}
			for s in locales:
				pivot[f][f"{keys[s]}_ventas"] = 0
				pivot[f][f"{keys[s]}_egresos"] = 0
				pivot[f][f"{keys[s]}_saldo"] = 0
		return pivot[f]

	pivot = {}
	for r in cajas:
		row = _ensure(r.fecha)
		k = _key(r.local)
		if f"{k}_ventas" in row:
			row[f"{k}_ventas"] += r.ventas
			row[f"{k}_saldo"] += r.saldo
	for r in egresos:
		row = _ensure(r.fecha)
		k = _key(r.local)
		if f"{k}_egresos" in row:
			row[f"{k}_egresos"] += r.egresos

	data = []
	for _, row in sorted(pivot.items()):
		row["total_ventas"] = sum(row.get(f"{keys[s]}_ventas", 0) for s in locales)
		row["total_egresos"] = sum(row.get(f"{keys[s]}_egresos", 0) for s in locales)
		row["total_saldo"] = sum(row.get(f"{keys[s]}_saldo", 0) for s in locales)
		data.append(row)
	return data
