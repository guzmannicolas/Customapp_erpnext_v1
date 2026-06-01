import frappe


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": "Fecha", "fieldname": "fecha", "fieldtype": "Date", "width": 100},
		{"label": "Local", "fieldname": "local", "fieldtype": "Data", "width": 130},
		{"label": "Concepto", "fieldname": "concepto", "fieldtype": "Data", "width": 170},
		{"label": "Subconcepto", "fieldname": "subconcepto", "fieldtype": "Data", "width": 150},
		{"label": "Detalle", "fieldname": "detalle", "fieldtype": "Data", "width": 180},
		{"label": "Medio de Pago", "fieldname": "medio_pago", "fieldtype": "Data", "width": 120},
		{"label": "Monto", "fieldname": "monto", "fieldtype": "Currency", "width": 130},
	]


def get_data(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " AND c.fecha >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND c.fecha <= %(to_date)s"
	if filters.get("local"):
		conditions += " AND c.local = %(local)s"
	if filters.get("concepto"):
		conditions += " AND e.concepto = %(concepto)s"

	rows = frappe.db.sql(
		f"""
		SELECT c.fecha, c.local, e.concepto,
			e.tipo_gasto, e.tipo_arca, e.detalle_municipio,
			e.detalle_referencia, e.medio_pago, e.monto
		FROM `tabDetalle Egresos Caja` e
		JOIN `tabCaja Diaria` c ON c.name = e.parent
		WHERE c.docstatus < 2 {conditions}
		ORDER BY c.fecha, e.concepto
		""",
		filters,
		as_dict=True,
	)

	data = []
	for r in rows:
		# subconcepto = el campo de subconcepto que corresponda al concepto
		subconcepto = r.tipo_gasto or r.tipo_arca or r.detalle_municipio or ""
		data.append({
			"fecha": r.fecha,
			"local": r.local,
			"concepto": r.concepto,
			"subconcepto": subconcepto,
			"detalle": r.detalle_referencia,
			"medio_pago": r.medio_pago,
			"monto": r.monto,
		})
	return data
