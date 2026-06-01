import frappe  # type: ignore[import]


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": "Fecha", "fieldname": "fecha", "fieldtype": "Date", "width": 100},
		{"label": "Local", "fieldname": "local", "fieldtype": "Data", "width": 130},
		{"label": "Tipo", "fieldname": "tipo", "fieldtype": "Data", "width": 80},
		{"label": "Detalle", "fieldname": "detalle", "fieldtype": "Data", "width": 220},
		{"label": "Ingreso", "fieldname": "ingreso", "fieldtype": "Currency", "width": 120},
		{"label": "Egreso", "fieldname": "egreso", "fieldtype": "Currency", "width": 120},
		{"label": "Saldo", "fieldname": "saldo", "fieldtype": "Currency", "width": 130},
	]


def _cond(filters, fecha_col, local_col):
	c = ""
	if filters.get("from_date"):
		c += f" AND {fecha_col} >= %(from_date)s"
	if filters.get("to_date"):
		c += f" AND {fecha_col} <= %(to_date)s"
	if filters.get("local"):
		c += f" AND {local_col} = %(local)s"
	return c


def get_data(filters):
	ventas = frappe.db.sql(
		f"""
		SELECT fecha, local, COALESCE(total_ventas, 0) AS ventas
		FROM `tabCaja Diaria`
		WHERE docstatus < 2 AND COALESCE(total_ventas, 0) > 0
		{_cond(filters, "fecha", "local")}
		""",
		filters,
		as_dict=True,
	)

	egresos = frappe.db.sql(
		f"""
		SELECT c.fecha, c.local, e.concepto, COALESCE(e.monto, 0) AS monto
		FROM `tabDetalle Egresos Caja` e
		JOIN `tabCaja Diaria` c ON c.name = e.parent
		WHERE c.docstatus < 2 AND COALESCE(e.monto, 0) <> 0
		{_cond(filters, "c.fecha", "c.local")}
		""",
		filters,
		as_dict=True,
	)

	movimientos = []
	for v in ventas:
		movimientos.append({
			"fecha": v.fecha, "local": v.local, "tipo": "Venta",
			"detalle": "Ventas del día", "ingreso": v.ventas, "egreso": 0, "_ord": 0,
		})
	for e in egresos:
		movimientos.append({
			"fecha": e.fecha, "local": e.local, "tipo": "Egreso",
			"detalle": e.concepto or "", "ingreso": 0, "egreso": e.monto, "_ord": 1,
		})

	# ordenar por fecha, y dentro del día primero las ventas
	movimientos.sort(key=lambda m: (str(m["fecha"]), m["_ord"]))

	saldo = 0
	for m in movimientos:
		saldo += (m["ingreso"] or 0) - (m["egreso"] or 0)
		m["saldo"] = saldo
		del m["_ord"]

	return movimientos
