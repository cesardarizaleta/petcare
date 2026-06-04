import ExcelJS from 'exceljs';

/**
 * Generates and downloads a beautifully styled Excel report using ExcelJS.
 * @param {Object} data - The JSON report data from the backend.
 * @param {string} period - The analyzed period name.
 */
export async function exportDashboardToExcel(data, period) {
  const workbook = new ExcelJS.Workbook();
  workbook.creator = 'Clinica PetCare';
  workbook.lastModifiedBy = 'PetCare Manager';
  workbook.created = new Date();
  workbook.modified = new Date();

  // Color Palette Constants (Premium Theme)
  const BRAND_COLOR = 'FFC2A769';      // Elegant Gold/Bronze
  const DARK_CHARCOAL = 'FF3D3D3D';    // Charcoal Dark Theme
  const ACCENT_BG = 'FFF9F9FB';        // Light Grey/Blue for zebra
  const BORDER_COLOR = 'FFE0E0E0';     // Subtle border line
  const TEXT_MUTED = 'FF888888';       // Grey text

  // ----------------------------------------------------
  // SHEET 1: RESUMEN DE RENDIMIENTO
  // ----------------------------------------------------
  const sheet1 = workbook.addWorksheet('Resumen de Rendimiento');
  sheet1.views = [{ showGridLines: true }];

  // Title Block
  sheet1.mergeCells('B2:F2');
  const titleCell = sheet1.getCell('B2');
  titleCell.value = 'REPORTE DE RENDIMIENTO GERENCIAL';
  titleCell.font = { name: 'Segoe UI', size: 16, bold: true, color: { argb: BRAND_COLOR } };
  titleCell.alignment = { vertical: 'middle', horizontal: 'left' };
  sheet1.getRow(2).height = 30;

  // Metadata Info
  sheet1.getCell('B3').value = 'Periodo:';
  sheet1.getCell('B3').font = { name: 'Segoe UI', size: 10, bold: true, color: { argb: DARK_CHARCOAL } };
  sheet1.getCell('C3').value = `${data.report_metadata.from} al ${data.report_metadata.to} (${period.replace('_', ' ').toUpperCase()})`;
  sheet1.getCell('C3').font = { name: 'Segoe UI', size: 10 };

  sheet1.getCell('B4').value = 'Generado el:';
  sheet1.getCell('B4').font = { name: 'Segoe UI', size: 10, bold: true, color: { argb: DARK_CHARCOAL } };
  sheet1.getCell('C4').value = new Date(data.report_metadata.generated_at).toLocaleString();
  sheet1.getCell('C4').font = { name: 'Segoe UI', size: 10 };

  // Divider Line
  for (let col = 2; col <= 6; col++) {
    sheet1.getCell(5, col).border = { bottom: { style: 'medium', color: { argb: BRAND_COLOR } } };
  }

  // KPIs Header
  sheet1.getCell('B7').value = 'INDICADORES CLAVE DE RENDIMIENTO (KPIs)';
  sheet1.getCell('B7').font = { name: 'Segoe UI', size: 12, bold: true, color: { argb: DARK_CHARCOAL } };
  
  // KPI Table Headers
  sheet1.getCell('B9').value = 'Indicador';
  sheet1.getCell('C9').value = 'Valor';
  
  const kpiHeaderCells = [sheet1.getCell('B9'), sheet1.getCell('C9')];
  kpiHeaderCells.forEach(cell => {
    cell.font = { name: 'Segoe UI', size: 11, bold: true, color: { argb: 'FFFFFFFF' } };
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: BRAND_COLOR } };
    cell.alignment = { vertical: 'middle', horizontal: 'center' };
  });
  sheet1.getRow(9).height = 24;

  let currentKpiRow = 10;
  (data.kpis || []).forEach((kpi, idx) => {
    const cellName = sheet1.getCell(`B${currentKpiRow}`);
    const cellValue = sheet1.getCell(`C${currentKpiRow}`);
    
    cellName.value = kpi.title;
    cellValue.value = kpi.value;

    cellName.font = { name: 'Segoe UI', size: 11 };
    cellValue.font = { name: 'Segoe UI', size: 11, bold: true };
    
    cellName.alignment = { vertical: 'middle', horizontal: 'left' };
    cellValue.alignment = { vertical: 'middle', horizontal: 'center' };

    const cells = [cellName, cellValue];
    cells.forEach(cell => {
      cell.border = {
        top: { style: 'thin', color: { argb: BORDER_COLOR } },
        bottom: { style: 'thin', color: { argb: BORDER_COLOR } },
        left: { style: 'thin', color: { argb: BORDER_COLOR } },
        right: { style: 'thin', color: { argb: BORDER_COLOR } }
      };
      if (idx % 2 === 1) {
        cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: ACCENT_BG } };
      }
    });
    sheet1.getRow(currentKpiRow).height = 22;
    currentKpiRow++;
  });

  // Adjust Column Widths for Sheet 1
  sheet1.getColumn('B').width = 45;
  sheet1.getColumn('C').width = 25;


  // ----------------------------------------------------
  // SHEET 2: DETALLE DE CONSULTAS
  // ----------------------------------------------------
  const sheet2 = workbook.addWorksheet('Detalle de Consultas');
  sheet2.views = [{ showGridLines: true }];

  // Sheet Header
  sheet2.getCell('A1').value = 'DETALLE DE CONSULTAS Y CITAS MÉDICAS';
  sheet2.getCell('A1').font = { name: 'Segoe UI', size: 14, bold: true, color: { argb: DARK_CHARCOAL } };
  sheet2.getRow(1).height = 26;

  const consultationHeaders = ['ID Cita', 'Fecha', 'Paciente', 'Propietario', 'Motivo de Visita', 'Estado'];
  
  // Set Column Headers
  consultationHeaders.forEach((h, idx) => {
    const cell = sheet2.getCell(3, idx + 1);
    cell.value = h;
    cell.font = { name: 'Segoe UI', size: 11, bold: true, color: { argb: 'FFFFFFFF' } };
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: DARK_CHARCOAL } };
    cell.alignment = { vertical: 'middle', horizontal: 'center' };
  });
  sheet2.getRow(3).height = 24;

  let currentConsultationRow = 4;
  const appointments = data.appointments || [];

  if (appointments.length === 0) {
    sheet2.mergeCells('A4:F4');
    const emptyCell = sheet2.getCell('A4');
    emptyCell.value = 'No se registraron consultas en este período.';
    emptyCell.font = { name: 'Segoe UI', size: 11, italic: true, color: { argb: TEXT_MUTED } };
    emptyCell.alignment = { horizontal: 'center', vertical: 'middle' };
    sheet2.getRow(4).height = 26;
  } else {
    appointments.forEach((appt, idx) => {
      const rowData = [
        appt.id,
        appt.date || '',
        appt.patient_name || '',
        appt.owner_name || '',
        appt.reason || '',
        appt.status === 'completed' ? 'Completada' :
        appt.status === 'confirmed' ? 'Confirmada' :
        appt.status === 'cancelled' ? 'Cancelada' : appt.status
      ];

      rowData.forEach((val, colIdx) => {
        const cell = sheet2.getCell(currentConsultationRow, colIdx + 1);
        cell.value = val;
        cell.font = { name: 'Segoe UI', size: 10 };
        cell.border = {
          top: { style: 'thin', color: { argb: BORDER_COLOR } },
          bottom: { style: 'thin', color: { argb: BORDER_COLOR } },
          left: { style: 'thin', color: { argb: BORDER_COLOR } },
          right: { style: 'thin', color: { argb: BORDER_COLOR } }
        };
        
        // Alignments
        if (colIdx === 0 || colIdx === 1 || colIdx === 5) {
          cell.alignment = { vertical: 'middle', horizontal: 'center' };
        } else {
          cell.alignment = { vertical: 'middle', horizontal: 'left' };
        }

        // Alternating background
        if (idx % 2 === 1) {
          cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: ACCENT_BG } };
        }
      });
      sheet2.getRow(currentConsultationRow).height = 20;
      currentConsultationRow++;
    });
  }

  // Auto-fit Columns for Sheet 2
  sheet2.columns.forEach(col => {
    let maxLen = 0;
    col.eachCell({ includeEmpty: true }, cell => {
      if (cell.value) {
        maxLen = Math.max(maxLen, cell.value.toString().length);
      }
    });
    col.width = Math.min(Math.max(maxLen + 4, 12), 40); // Cap at 40 width
  });


  // ----------------------------------------------------
  // SHEET 3: DETALLE DE REQUISICIONES
  // ----------------------------------------------------
  const sheet3 = workbook.addWorksheet('Detalle de Requisiciones');
  sheet3.views = [{ showGridLines: true }];

  // Sheet Header
  sheet3.getCell('A1').value = 'DETALLE DE REQUISICIONES Y COMPRAS DE ALMACÉN';
  sheet3.getCell('A1').font = { name: 'Segoe UI', size: 14, bold: true, color: { argb: DARK_CHARCOAL } };
  sheet3.getRow(1).height = 26;

  const purchaseHeaders = ['ID Requisición', 'Fecha', 'Proveedor', 'Costo Total', 'Estado'];
  
  // Set Column Headers
  purchaseHeaders.forEach((h, idx) => {
    const cell = sheet3.getCell(3, idx + 1);
    cell.value = h;
    cell.font = { name: 'Segoe UI', size: 11, bold: true, color: { argb: 'FFFFFFFF' } };
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: DARK_CHARCOAL } };
    cell.alignment = { vertical: 'middle', horizontal: 'center' };
  });
  sheet3.getRow(3).height = 24;

  let currentPurchaseRow = 4;
  const purchases = data.purchase_orders || [];

  if (purchases.length === 0) {
    sheet3.mergeCells('A4:E4');
    const emptyCell = sheet3.getCell('A4');
    emptyCell.value = 'No se registraron requisiciones en este período.';
    emptyCell.font = { name: 'Segoe UI', size: 11, italic: true, color: { argb: TEXT_MUTED } };
    emptyCell.alignment = { horizontal: 'center', vertical: 'middle' };
    sheet3.getRow(4).height = 26;
  } else {
    purchases.forEach((po, idx) => {
      const rowData = [
        po.id,
        po.date || '',
        po.supplier_name || '',
        Number(po.total_cost || 0),
        po.status === 'REQUESTED' ? 'Pendiente' :
        po.status === 'APPROVED' ? 'Aprobada' :
        po.status === 'RECEIVED' ? 'Recibida' :
        po.status === 'CANCELLED' ? 'Cancelada' : po.status
      ];

      rowData.forEach((val, colIdx) => {
        const cell = sheet3.getCell(currentPurchaseRow, colIdx + 1);
        cell.value = val;
        cell.font = { name: 'Segoe UI', size: 10 };
        cell.border = {
          top: { style: 'thin', color: { argb: BORDER_COLOR } },
          bottom: { style: 'thin', color: { argb: BORDER_COLOR } },
          left: { style: 'thin', color: { argb: BORDER_COLOR } },
          right: { style: 'thin', color: { argb: BORDER_COLOR } }
        };
        
        // Alignments and Number Formats
        if (colIdx === 3) {
          cell.alignment = { vertical: 'middle', horizontal: 'right' };
          cell.numFmt = '"$"#,##0.00';
        } else if (colIdx === 0 || colIdx === 1 || colIdx === 4) {
          cell.alignment = { vertical: 'middle', horizontal: 'center' };
        } else {
          cell.alignment = { vertical: 'middle', horizontal: 'left' };
        }

        // Alternating background
        if (idx % 2 === 1) {
          cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: ACCENT_BG } };
        }
      });
      sheet3.getRow(currentPurchaseRow).height = 20;
      currentPurchaseRow++;
    });

    // Add Sum Row
    const sumRowIdx = currentPurchaseRow;
    sheet3.getCell(`C${sumRowIdx}`).value = 'TOTAL COMPRAS:';
    sheet3.getCell(`C${sumRowIdx}`).font = { name: 'Segoe UI', size: 11, bold: true, color: { argb: DARK_CHARCOAL } };
    sheet3.getCell(`C${sumRowIdx}`).alignment = { vertical: 'middle', horizontal: 'right' };

    const totalCostCell = sheet3.getCell(`D${sumRowIdx}`);
    totalCostCell.value = { formula: `=SUM(D4:D${sumRowIdx - 1})` };
    totalCostCell.font = { name: 'Segoe UI', size: 11, bold: true };
    totalCostCell.alignment = { vertical: 'middle', horizontal: 'right' };
    totalCostCell.numFmt = '"$"#,##0.00';

    const summaryCells = [
      sheet3.getCell(`A${sumRowIdx}`),
      sheet3.getCell(`B${sumRowIdx}`),
      sheet3.getCell(`C${sumRowIdx}`),
      sheet3.getCell(`D${sumRowIdx}`),
      sheet3.getCell(`E${sumRowIdx}`)
    ];

    summaryCells.forEach(cell => {
      cell.border = {
        top: { style: 'thin', color: { argb: 'FF000000' } },
        bottom: { style: 'double', color: { argb: 'FF000000' } }
      };
    });
    sheet3.getRow(sumRowIdx).height = 24;
  }

  // Auto-fit Columns for Sheet 3
  sheet3.columns.forEach(col => {
    let maxLen = 0;
    col.eachCell({ includeEmpty: true }, cell => {
      // Don't count formula structures for length auto-calculation
      if (cell.value && typeof cell.value !== 'object') {
        maxLen = Math.max(maxLen, cell.value.toString().length);
      }
    });
    col.width = Math.min(Math.max(maxLen + 4, 12), 40);
  });


  // ----------------------------------------------------
  // TRIGGER BROWSER DOWNLOAD
  // ----------------------------------------------------
  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  
  const fromDate = data.report_metadata.from;
  const toDate = data.report_metadata.to;
  link.setAttribute('download', `reporte_general_petcare_${period}_${fromDate}_al_${toDate}.xlsx`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
