import frappe  # type: ignore[import]
from frappe.utils import getdate, nowdate

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def _locales():
	opts = frappe.get_meta("Caja Diaria").get_field("local").options or ""
	return [o.strip() for o in opts.split("\n") if o.strip()]


def execute(filters=None):
	filters = filters or {}
	year = int(filters.get("year") or getdate(nowdate()).year)
	metric = filters.get("metric") or "Ventas"
	return get_columns(), get_data(year, metric)


def get_columns():
	cols = [{"label": "Local", "fieldname": "local", "fieldtype": "Data", "width": 150}]
	for i, m in enumerate(MESES, start=1):
		cols.append({"label": m, "fieldname": f"m{i}", "fieldtype": "Currency", "width": 95})
	cols.append({"label": "Total", "fieldname": "total", "fieldtype": "Currency", "width": 130})
	return cols


def get_data(year, metric):
	campo = "total_ventas" if metric == "Ventas" else "saldo_final"
	rows = frappe.db.sql(
		f"""
		SELECT local, MONTH(fecha) AS mes, SUM(COALESCE({campo}, 0)) AS valor
		FROM `tabCaja Diaria`
		WHERE docstatus < 2 AND YEAR(fecha) = %(year)s
		GROUP BY local, MONTH(fecha)
		""",
		{"year": year},
		as_dict=True,
	)

	pivot = {}
	for l in _locales():
		pivot[l] = {"local": l, "total": 0}
		for i in range(1, 13):
			pivot[l][f"m{i}"] = 0

	for r in rows:
		if r.local in pivot:
			pivot[r.local][f"m{r.mes}"] = r.valor
			pivot[r.local]["total"] += r.valor

	return list(pivot.values())
