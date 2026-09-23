import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { jsPDF } from 'jspdf';
import { fetchSaleReceipt } from '../../services/api';

const money = (value) => '$ ' + Number(value || 0).toLocaleString('es-CO', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const formatDate = (value) => new Date(value).toLocaleString('es-CO', {
  dateStyle: 'medium',
  timeStyle: 'short',
});

const customer = (receipt) => (typeof receipt.cliente === 'string'
  ? { nombre: receipt.cliente, nit: receipt.cliente_nit || '', cedula: '', telefono: '' }
  : receipt.cliente || { nombre: '', nit: '', cedula: '', telefono: '' });

const ITEMS_PER_PAGE = 15;
const splitItems = (items = []) => Array.from(
  { length: Math.max(1, Math.ceil(items.length / ITEMS_PER_PAGE)) },
  (_, index) => items.slice(index * ITEMS_PER_PAGE, (index + 1) * ITEMS_PER_PAGE),
);

export default function SaleReceipt() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [receipt, setReceipt] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSaleReceipt(id).then(setReceipt).catch((err) => {
      setError(err.response?.data?.error || 'No se pudo cargar el recibo de caja.');
    });
  }, [id]);

  const downloadPdf = () => {
    if (!receipt) return;
    const doc = new jsPDF({ unit: 'pt', format: 'a4' });
    const width = doc.internal.pageSize.getWidth();
    const client = customer(receipt);
    const pages = splitItems(receipt.items);
    pages.forEach((items, pageIndex) => {
      if (pageIndex > 0) doc.addPage();
      const pageNumber = pageIndex + 1;
      const pageCount = pages.length;
      doc.setFillColor(15, 23, 42);
      doc.rect(0, 0, width, 70, 'F');
      doc.setTextColor(255, 255, 255);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(18);
      doc.text('Multivariedades Ricaurte', 42, 30);
      doc.setFontSize(10);
      doc.text('NIT 1010085627-1', 42, 50);
      doc.text(`Recibo de Caja No. ${receipt.numero_comprobante}`, width - 250, 38);
      doc.text(`Hoja ${pageNumber} de ${pageCount}`, width - 110, 57);
      doc.setTextColor(17, 24, 39);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(11);
      let y = 105;
      doc.text(`Fecha: ${formatDate(receipt.fecha)}`, 42, y);
      doc.text(`Vendedor: ${receipt.vendedor}`, 42, y + 20);
      doc.text(`Cliente: ${client.nombre || 'Consumidor final'}`, 300, y);
      doc.text(`NIT: ${client.nit || '-'}`, 300, y + 20);
      doc.text(`Pago: ${receipt.medio_pago}`, 300, y + 40);
      y += 60;
      doc.setFont('helvetica', 'bold');
      doc.text('Producto', 42, y);
      doc.text('Cantidad', 300, y);
      doc.text('Subtotal', 450, y);
      doc.line(42, y + 7, width - 42, y + 7);
      doc.setFont('helvetica', 'normal');
      items.forEach((item, index) => {
        const rowY = y + 30 + index * 22;
        doc.text(String(item.producto), 42, rowY, { maxWidth: 220 });
        doc.text(String(item.cantidad), 300, rowY);
        doc.text(money(item.subtotal), 450, rowY);
      });
      if (pageIndex === pageCount - 1) {
        const totalY = y + 42 + items.length * 22;
        doc.setFont('helvetica', 'bold');
        doc.text('TOTAL', 370, totalY);
        doc.text(money(receipt.total), 450, totalY);
      }
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.text(`Recibo de Caja ${receipt.numero_comprobante} | Hoja ${pageNumber} de ${pageCount}`, 42, doc.internal.pageSize.getHeight() - 28);
    });
    doc.save(`recibo-caja-${receipt.numero_comprobante}.pdf`);
  };

  if (error) return <div className="container py-5"><div className="alert alert-danger">{error}</div><button className="btn btn-secondary" onClick={() => navigate('/ventas')}>Volver</button></div>;
  if (!receipt) return <div className="container py-5 text-center">Cargando recibo de caja...</div>;

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-end gap-2 mb-3 d-print-none">
        <button type="button" className="btn btn-outline-secondary" onClick={() => window.print()}><i className="bi bi-printer me-1" />Imprimir</button>
        <button type="button" className="btn btn-primary" onClick={downloadPdf}><i className="bi bi-filetype-pdf me-1" />PDF</button>
      </div>
      {splitItems(receipt.items).map((items, pageIndex, pages) => (
        <article className="data-table p-4 receipt-page" key={pageIndex}>
          <header className="d-flex justify-content-between border-bottom pb-3 mb-4">
            <div><h2 className="mb-1">Multivariedades Ricaurte</h2><div>NIT 1010085627-1</div></div>
            <div className="text-end"><h3 className="mb-0">Recibo de Caja No. {receipt.numero_comprobante}</h3><small>Hoja {pageIndex + 1} de {pages.length}</small></div>
          </header>
          <div className="row g-3 mb-4">
            <div className="col-md-3"><strong>Fecha</strong><div>{formatDate(receipt.fecha)}</div></div>
            <div className="col-md-3"><strong>Vendedor</strong><div>{receipt.vendedor}</div></div>
            <div className="col-md-3"><strong>Cliente</strong><div>{customer(receipt).nombre || 'Consumidor final'}</div></div>
            <div className="col-md-3"><strong>NIT del comprador</strong><div>{customer(receipt).nit || '-'}</div></div>
            <div className="col-md-3"><strong>Pago</strong><div>{receipt.medio_pago}</div></div>
          </div>
          <div className="table-responsive">
            <table className="table align-middle">
              <thead><tr><th>Producto</th><th className="text-end">Cantidad</th><th className="text-end">Precio unitario</th><th className="text-end">Subtotal</th></tr></thead>
              <tbody>{items.map((item) => <tr key={item.producto_id}><td>{item.producto}</td><td className="text-end">{item.cantidad}</td><td className="text-end">{money(item.precio_unitario)}</td><td className="text-end">{money(item.subtotal)}</td></tr>)}</tbody>
              {pageIndex === pages.length - 1 && <tfoot><tr><th colSpan="3" className="text-end">TOTAL</th><th className="text-end fs-5">{money(receipt.total)}</th></tr></tfoot>}
            </table>
          </div>
          <footer className="receipt-page-footer">Hoja {pageIndex + 1} de {pages.length}</footer>
        </article>
      ))}
    </div>
  );
}
