let itemCount = 0;

function fmt(n) {
  return '$' + Math.round(n).toLocaleString('es-CO');
}

function agregarItem() {
  itemCount++;
  const id = itemCount;
  const div = document.createElement('div');
  div.className = 'item-row';
  div.id = `item-${id}`;
  div.innerHTML = `
    <div class="field">
      <label>Descripción</label>
      <input type="text" placeholder="Ej: Desarrollo módulo ventas" oninput="actualizarTotales()" data-field="desc" />
    </div>
    <div class="field">
      <label>Cant.</label>
      <input type="number" value="1" min="1" step="0.01" oninput="actualizarSubtotal(${id}); actualizarTotales()" data-field="cant" />
    </div>
    <div class="field">
      <label>Precio unitario</label>
      <input type="number" value="" min="0" placeholder="0" oninput="actualizarSubtotal(${id}); actualizarTotales()" data-field="precio" />
    </div>
    <div class="field">
      <label>Desc. %</label>
      <input type="number" value="0" min="0" max="100" placeholder="0" oninput="actualizarSubtotal(${id}); actualizarTotales()" data-field="desc_pct" />
    </div>
    <div class="subtotal-display" id="sub-${id}">$0</div>
    <button type="button" class="btn-remove" onclick="eliminarItem(${id})" title="Eliminar">✕</button>
  `;
  document.getElementById('items-container').appendChild(div);
  div.querySelector('[data-field="desc"]').focus();
  actualizarTotales();
}

function eliminarItem(id) {
  const el = document.getElementById(`item-${id}`);
  if (el) { 
      el.style.opacity = '0'; 
      el.style.transform = 'translateY(-8px)'; 
      el.style.transition = 'all .2s'; 
      setTimeout(() => el.remove(), 200); 
  }
  setTimeout(actualizarTotales, 210);
}

function getItemData(row) {
  return {
    descripcion: row.querySelector('[data-field="desc"]').value.trim(),
    cantidad:    parseFloat(row.querySelector('[data-field="cant"]').value)    || 0,
    precio_unit: parseFloat(row.querySelector('[data-field="precio"]').value)  || 0,
    descuento:   parseFloat(row.querySelector('[data-field="desc_pct"]').value)|| 0,
  };
}

function actualizarSubtotal(id) {
  const row = document.getElementById(`item-${id}`);
  if (!row) return;
  const d = getItemData(row);
  const bruto = d.cantidad * d.precio_unit;
  const neto  = bruto * (1 - d.descuento / 100);
  document.getElementById(`sub-${id}`).textContent = fmt(neto);
}

function actualizarTotales() {
  let subtotal = 0, descuentos = 0;
  document.querySelectorAll('.item-row').forEach(row => {
    const d = getItemData(row);
    const bruto = d.cantidad * d.precio_unit;
    subtotal   += bruto;
    descuentos += bruto * d.descuento / 100;
  });
  const base = subtotal - descuentos;
  const iva   = base * 0.19;
  const total = base + iva;
  document.getElementById('prev-subtotal').textContent  = fmt(subtotal);
  document.getElementById('prev-descuentos').textContent= '-' + fmt(descuentos);
  document.getElementById('prev-iva').textContent        = fmt(iva);
  document.getElementById('prev-total').textContent     = fmt(total);
}

function showToast(msg, tipo = 'success') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `show ${tipo}`;
  setTimeout(() => t.className = '', 3500);
}

function setLoading(btn, on, textoOn, textoOff, spinnerId, btnTextId) {
  document.getElementById(spinnerId).style.display = on ? 'block' : 'none';
  document.getElementById(btnTextId).textContent   = on ? textoOn : textoOff;
  document.getElementById(btn).disabled = on;
}

function buildPayload() {
  const items = [];
  document.querySelectorAll('.item-row').forEach(row => {
    const d = getItemData(row);
    if (d.descripcion && d.precio_unit > 0) items.push(d);
  });
  return {
    numero_factura: document.getElementById('numero_factura').value.trim(),
    fecha:          document.getElementById('fecha').value.trim() || null,
    cliente: {
      nombre:    document.getElementById('cliente_nombre').value.trim(),
      nit:       document.getElementById('cliente_nit').value.trim(),
      email:     document.getElementById('cliente_email').value.trim(),
      direccion: document.getElementById('cliente_direccion').value.trim(),
    },
    items,
    notas: document.getElementById('notas').value.trim(),
  };
}

// Inicialización
(function() {
  const hoy = new Date();
  const dd = String(hoy.getDate()).padStart(2,'0');
  const mm = String(hoy.getMonth()+1).padStart(2,'0');
  const yyyy = hoy.getFullYear();
  document.getElementById('fecha').value = `${dd}/${mm}/${yyyy}`;
  document.getElementById('numero_factura').value = `FAC-${yyyy}-001`;
  agregarItem();
})();

// Descargar PDF
document.getElementById('form-factura').addEventListener('submit', async function(e) {
  e.preventDefault();
  const payload = buildPayload();

  if (payload.items.length === 0) {
    showToast('Agrega al menos un ítem con descripción y precio.', 'error');
    return;
  }

  setLoading('btn-submit', true,  'Generando…', '⬇ Descargar PDF', 'spinner', 'btn-text');

  try {
    const res = await fetch('/factura', {
      method:  'POST',
      headers: {'Content-Type': 'application/json'},
      body:    JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `Error ${res.status}`);
    }

    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `${payload.numero_factura}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('✓ Factura descargada', 'success');

  } catch (err) {
    showToast('✗ ' + err.message, 'error');
  } finally {
    setLoading('btn-submit', false, '', '⬇ Descargar PDF', 'spinner', 'btn-text');
  }
});

// Enviar por correo
async function enviarPorCorreo() {
  const payload = buildPayload();

  if (payload.items.length === 0) {
    showToast('Agrega al menos un ítem con descripción y precio.', 'error');
    return;
  }
  if (!payload.cliente.email) {
    showToast('Ingresa el correo del cliente para poder enviar.', 'error');
    document.getElementById('cliente_email').focus();
    return;
  }

  setLoading('btn-enviar', true, 'Enviando…', '✉ Enviar por correo', 'spinner-email', 'btn-email-text');

  try {
    const res = await fetch('/enviar-factura', {
      method:  'POST',
      headers: {'Content-Type': 'application/json'},
      body:    JSON.stringify(payload),
    });

    const json = await res.json();
    if (!res.ok) throw new Error(json.error || `Error ${res.status}`);

    showToast(`✓ ${json.mensaje}`, 'success');

  } catch (err) {
    showToast('✗ ' + err.message, 'error');
  } finally {
    setLoading('btn-enviar', false, '', '✉ Enviar por correo', 'spinner-email', 'btn-email-text');
  }
}