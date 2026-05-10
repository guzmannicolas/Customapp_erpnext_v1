import frappe

SUCURSALES = ["Sucursal 1", "Sucursal 2", "Sucursal 3", "Sucursal 4", "Sucursal 5", "Sucursal 6"]


def execute(filters=None):
	filters = filters or {}
	metric = filters.get("metric") or "Saldo Final"
	columns = get_columns(metric)
	data = get_data(filters)
	chart = get_chart_data(data, metric)
	return columns, data, None, chart


def get_columns(metric):
	show_ventas = metric == "Ventas"
	suffix = "_ventas" if show_ventas else "_saldo"
	label_tipo = "Ventas" if show_ventas else "Saldo"

	columns = [{"label": "Fecha", "fieldname": "fecha", "fieldtype": "Date", "width": 110}]
	for s in SUCURSALES:
		key = s.lower().replace(" ", "_")
		columns.append({
			"label": f"{s} - {label_tipo}",
			"fieldname": f"{key}{suffix}",
			"fieldtype": "Currency",
			"width": 140,
		})
	columns.append({
		"label": f"Total {label_tipo}",
		"fieldname": "total_ventas" if show_ventas else "total_saldo",
		"fieldtype": "Currency",
		"width": 140,
	})
	return columns


def get_data(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " AND fecha >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND fecha <= %(to_date)s"

	rows = frappe.db.sql(
		f"""
		SELECT
			fecha, local,
			COALESCE(total_ventas, 0) AS ventas,
			COALESCE(saldo_final, 0)  AS saldo
		FROM `tabCaja Diaria`
		WHERE docstatus < 2 {conditions}
		ORDER BY fecha
		""",
		filters,
		as_dict=True,
	)

	pivot = {}
	for row in rows:
		fecha = str(row.fecha)
		if fecha not in pivot:
			pivot[fecha] = {"fecha": row.fecha}
			for s in SUCURSALES:
				key = s.lower().replace(" ", "_")
				pivot[fecha][f"{key}_ventas"] = 0
				pivot[fecha][f"{key}_saldo"] = 0
		key = row.local.lower().replace(" ", "_")
		pivot[fecha][f"{key}_ventas"] += row.ventas
		pivot[fecha][f"{key}_saldo"] += row.saldo

	data = []
	for _, row in sorted(pivot.items()):
		row["total_ventas"] = sum(row.get(f"{s.lower().replace(' ', '_')}_ventas", 0) for s in SUCURSALES)
		row["total_saldo"] = sum(row.get(f"{s.lower().replace(' ', '_')}_saldo", 0) for s in SUCURSALES)
		data.append(row)

	return data


def get_chart_data(data, metric):
	if not data:
		return None

	suffix = "_ventas" if metric == "Ventas" else "_saldo"
	labels = [str(row["fecha"]) for row in data]
	datasets = [
		{
			"name": s,
			"values": [row.get(f"{s.lower().replace(' ', '_')}{suffix}", 0) for row in data],
		}
		for s in SUCURSALES
	]

	return {
		"data": {"labels": labels, "datasets": datasets},
		"type": "bar",
		"fieldtype": "Currency",
	}
