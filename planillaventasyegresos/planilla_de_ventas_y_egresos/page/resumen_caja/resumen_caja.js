frappe.pages["resumen-caja"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Resumen de Caja",
		single_column: true,
	});

	// --- Filtros en la barra de la página ---
	const rango_field = page.add_field({
		label: __("Rango"),
		fieldtype: "Select",
		fieldname: "rango",
		options: [
			{ label: __("Hoy"), value: "hoy" },
			{ label: __("Esta semana"), value: "semana" },
			{ label: __("Este mes"), value: "mes" },
		],
		default: "semana",
		change: () => load(),
	});

	const local_field = page.add_field({
		label: __("Sucursal"),
		fieldtype: "Select",
		fieldname: "local",
		options: [
			"Todas",
			"CENTRAL",
			"GRAND BOURG",
			"JOSE C. PAZ",
			"SAN MIGUEL",
			"PILAR",
			"DEPÓSITO",
		],
		default: "Todas",
		change: () => load(),
	});

	// --- Cuerpo: 3 números grandes ---
	$(page.main).html(`
		<div id="resumen-caja-block" style="
			padding: 24px;
			background: var(--card-bg, #f8f9fa);
			border-radius: 8px;
			margin-bottom: 20px;
		">
			<div style="text-align: center; margin-bottom: 24px;">
				<small style="color: var(--text-muted, #999);" id="rc-rango">—</small>
			</div>
			<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
				<div style="text-align: center;">
					<div style="font-size: 30px; font-weight: bold; color: #27ae60; margin-bottom: 5px;" id="rc-ventas">$0</div>
					<div style="font-size: 12px; color: var(--text-muted, #666); text-transform: uppercase; letter-spacing: 0.5px;">Ventas</div>
				</div>
				<div style="text-align: center;">
					<div style="font-size: 30px; font-weight: bold; color: #e74c3c; margin-bottom: 5px;" id="rc-egresos">$0</div>
					<div style="font-size: 12px; color: var(--text-muted, #666); text-transform: uppercase; letter-spacing: 0.5px;">Egresos</div>
				</div>
				<div style="text-align: center;">
					<div style="font-size: 30px; font-weight: bold; color: #3498db; margin-bottom: 5px;" id="rc-saldo">$0</div>
					<div style="font-size: 12px; color: var(--text-muted, #666); text-transform: uppercase; letter-spacing: 0.5px;">Saldo</div>
				</div>
			</div>
			<div style="margin-top: 18px; text-align: center;">
				<small style="color: var(--text-muted, #999);" id="rc-dias"></small>
			</div>
		</div>
	`);

	function load() {
		frappe.call({
			method:
				"planillaventasyegresos.planilla_de_ventas_y_egresos.doctype.caja_diaria.caja_diaria.get_resumen",
			args: {
				rango: rango_field.get_value() || "semana",
				local: local_field.get_value() || "Todas",
			},
			callback: (r) => {
				if (!r.message) return;
				const d = r.message;
				const fmt = (v) => format_currency(v, frappe.boot.sysdefaults.currency);
				$(page.main).find("#rc-ventas").text(fmt(d.ventas));
				$(page.main).find("#rc-egresos").text(fmt(d.egresos));
				$(page.main).find("#rc-saldo").text(fmt(d.saldo));
				$(page.main).find("#rc-rango").text(`${d.desde} — ${d.hasta}`);
				$(page.main)
					.find("#rc-dias")
					.text(`${d.dias_registrados} días registrados`);
			},
		});
	}

	load();
};
