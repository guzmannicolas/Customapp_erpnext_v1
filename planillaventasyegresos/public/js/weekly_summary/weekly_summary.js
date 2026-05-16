frappe.ui.form.ControlWeeklySummary = frappe.ui.form.Control.extend({
	html: `<div id="weekly-summary-block" style="
		padding: 20px;
		background: #f8f9fa;
		border-radius: 8px;
		margin-bottom: 20px;
	">
		<div style="text-align: center; margin-bottom: 20px;">
			<h5 style="margin: 0; color: #666; font-size: 14px;">RESUMEN DE LA SEMANA</h5>
			<small style="color: #999;" id="week-range"></small>
		</div>
		<div style="
			display: grid;
			grid-template-columns: repeat(3, 1fr);
			gap: 20px;
		">
			<div style="text-align: center;">
				<div style="font-size: 28px; font-weight: bold; color: #27ae60; margin-bottom: 5px;" id="ventas-total">$0</div>
				<div style="font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;">Ventas</div>
			</div>
			<div style="text-align: center;">
				<div style="font-size: 28px; font-weight: bold; color: #e74c3c; margin-bottom: 5px;" id="egresos-total">$0</div>
				<div style="font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;">Egresos</div>
			</div>
			<div style="text-align: center;">
				<div style="font-size: 28px; font-weight: bold; color: #3498db; margin-bottom: 5px;" id="saldo-neto">$0</div>
				<div style="font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;">Saldo Neto</div>
			</div>
		</div>
		<div style="margin-top: 15px; text-align: center;">
			<small style="color: #999;" id="dias-info"></small>
		</div>
	</div>`,

	make_input: function() {
		this.$wrapper.html(this.html);
		this.loadData();
		this.refresh();
	},

	loadData: function() {
		frappe.call({
			method: 'planillaventasyegresos.planilla_de_ventas_y_egresos.doctype.caja_diaria.caja_diaria.get_weekly_summary',
			callback: (r) => {
				if (r.message) {
					const data = r.message;

					document.getElementById('ventas-total').textContent =
						frappe.format(data.total_ventas, { fieldtype: 'Currency' });
					document.getElementById('egresos-total').textContent =
						frappe.format(data.total_egresos, { fieldtype: 'Currency' });
					document.getElementById('saldo-neto').textContent =
						frappe.format(data.saldo_neto, { fieldtype: 'Currency' });

					document.getElementById('week-range').textContent =
						`${data.fecha_inicio} - ${data.fecha_fin}`;
					document.getElementById('dias-info').textContent =
						`${data.dias_registrados} días registrados`;
				}
			}
		});
	},

	refresh: function() {
		// Recargar datos cada vez que se refresca
		this.loadData();
	}
});
