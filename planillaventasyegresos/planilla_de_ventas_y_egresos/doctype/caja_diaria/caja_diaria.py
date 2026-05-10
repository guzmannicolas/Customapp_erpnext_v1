# Copyright (c) 2026, Zepe and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class CajaDiaria(Document):
	def validate(self):
		self.total_ventas = (
			(self.efectivo or 0) +
			(self.mercado_pago or 0) +
			(self.tarjetas or 0)
		)
		self.total_egresos = sum(row.monto or 0 for row in (self.egresos or []))
		self.saldo_final = self.total_ventas - self.total_egresos
