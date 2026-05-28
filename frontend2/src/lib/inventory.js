export const DEFAULT_INVENTORY_UMBRAL = 10;

export function getInventoryUmbral(item) {
  const raw = item?.umbral;
  if (raw != null && raw !== '' && !Number.isNaN(Number(raw))) {
    return Number(raw);
  }
  return DEFAULT_INVENTORY_UMBRAL;
}

export function normalizeInventoryItem(item) {
  if (!item.batches) {
    item.batches = [];
  }
  item.umbral = getInventoryUmbral(item);
  return item;
}

export function normalizeInventory(inventory) {
  if (!Array.isArray(inventory)) return;
  inventory.forEach(normalizeInventoryItem);
}

function daysUntilExpiration(expirationDate) {
  const today = new Date();
  const expiration = new Date(`${expirationDate}T00:00:00`);
  const diffMs = expiration - today;
  return Math.ceil(diffMs / (1000 * 60 * 60 * 24));
}

/** Alertas de stock y vencimiento de lotes (no confundir con estado de solicitudes de compra). */
export function evaluateProductAlertState(product) {
  let alertClass = 'normal';
  const messages = [];

  const stock = product.quantity || 0;
  const minimum = getInventoryUmbral(product);
  const warningStockLimit = minimum * 1.5;

  if (stock <= minimum) {
    alertClass = 'critical';
    messages.push(`Stock crítico: quedan ${stock} uds. (mínimo: ${minimum})`);
  } else if (stock <= warningStockLimit) {
    alertClass = 'warning';
    messages.push(`Stock bajo: quedan ${stock} uds. (mínimo: ${minimum})`);
  }

  if (product.batches?.length) {
    product.batches.forEach((batch) => {
      const daysRemaining = daysUntilExpiration(batch.expirationDate);

      if (daysRemaining <= 15) {
        alertClass = 'critical';
        messages.push(`Lote #${batch.batch}: vence en ${daysRemaining} días (crítico)`);
      } else if (daysRemaining <= 45) {
        if (alertClass !== 'critical') alertClass = 'warning';
        messages.push(`Lote #${batch.batch}: vence en ${daysRemaining} días`);
      }
    });
  }

  return { alertClass, messages };
}
