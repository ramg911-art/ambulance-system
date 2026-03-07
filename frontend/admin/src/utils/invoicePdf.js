import jsPDF from 'jspdf'

const FONT = 'helvetica'
const FONT_BOLD = 'helvetica'
const PRIMARY = [30, 58, 138]   // #1e3a8a
const MUTED = [100, 116, 139]   // #64748b
const BORDER = [226, 232, 240]  // #e2e8f0

/**
 * Generate a modern PDF invoice for a trip.
 * @param {Object} data - Invoice with trip details from GET /billing/invoices/{id}/details
 */
export function generateInvoicePdf(data) {
  const doc = new jsPDF({ unit: 'mm', format: 'a4' })
  const w = doc.internal.pageSize.getWidth()
  let y = 20

  // Header
  doc.setFontSize(24)
  doc.setTextColor(...PRIMARY)
  doc.setFont(FONT, 'bold')
  doc.text('INVOICE', 20, y)
  y += 12

  doc.setFontSize(10)
  doc.setTextColor(...MUTED)
  doc.setFont(FONT, 'normal')
  doc.text(`#${data.invoice_number}`, 20, y)
  doc.text(`Trip #${data.trip_id}`, w - 20, y, { align: 'right' })
  y += 15

  // Divider
  doc.setDrawColor(...BORDER)
  doc.setLineWidth(0.5)
  doc.line(20, y, w - 20, y)
  y += 15

  // Trip details box
  const boxX = 20
  const boxW = w - 40
  const lineH = 7

  const rows = [
    ['Driver', data.driver_name || '—'],
    ['Vehicle', data.vehicle_registration || '—'],
    ['Trip Start', data.start_time ? new Date(data.start_time).toLocaleString('en-IN') : '—'],
    ['Pickup', data.pickup_location || '—'],
    ['Drop', data.drop_location || '—'],
    ['Distance', data.distance_km != null ? `${data.distance_km.toFixed(2)} km` : '—'],
  ]

  doc.setFont(FONT, 'bold')
  doc.setFontSize(11)
  doc.setTextColor(15, 23, 42)
  doc.text('Trip Details', boxX, y)
  y += 10

  doc.setFont(FONT, 'normal')
  doc.setFontSize(10)
  doc.setTextColor(...MUTED)
  for (const [label, value] of rows) {
    doc.setTextColor(...MUTED)
    doc.text(`${label}:`, boxX, y)
    doc.setTextColor(51, 65, 85)
    doc.text(String(value), boxX + 45, y)
    y += lineH
  }
  y += 8

  // Amount box
  doc.setDrawColor(...BORDER)
  doc.setLineWidth(0.3)
  doc.rect(boxX, y, boxW, 28)
  y += 10

  doc.setFont(FONT, 'bold')
  doc.setFontSize(12)
  doc.setTextColor(...PRIMARY)
  doc.text('Total Fare', boxX + 10, y)
  doc.text(`₹${Number(data.amount || data.total_amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`, w - 30, y, { align: 'right' })
  y += 12

  doc.setFont(FONT, 'normal')
  doc.setFontSize(9)
  doc.setTextColor(...MUTED)
  doc.text('Amount includes base fare and any additional charges.', boxX + 10, y)
  y += 20

  // Status badge
  const status = (data.status || 'pending').toLowerCase()
  doc.setFontSize(9)
  if (status === 'paid') {
    doc.setTextColor(22, 101, 52)
    doc.text('✓ PAID', boxX, y)
  } else {
    doc.setTextColor(146, 64, 14)
    doc.text('PENDING', boxX, y)
  }

  // Footer
  y = doc.internal.pageSize.getHeight() - 25
  doc.setDrawColor(...BORDER)
  doc.line(20, y, w - 20, y)
  y += 10
  doc.setFontSize(8)
  doc.setTextColor(...MUTED)
  doc.text('Thank you for your business.', w / 2, y, { align: 'center' })
  doc.text(`Generated on ${new Date().toLocaleString('en-IN')}`, w / 2, y + 5, { align: 'center' })

  doc.save(`Invoice-${data.invoice_number}.pdf`)
}
