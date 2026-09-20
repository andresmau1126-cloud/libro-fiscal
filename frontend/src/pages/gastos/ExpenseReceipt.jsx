import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { jsPDF } from 'jspdf';
import { fetchExpenseReceipt } from '../../services/api';

const money = (value) =>
  new Intl.NumberFormat('es-GT', {
    style: 'currency',
    currency: 'GTQ',
    minimumFractionDigits: 2,
  }).format(Number(value || 0));

export default function ExpenseReceipt() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [receipt, setReceipt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadReceipt = async () => {
      try {
        setLoading(true);
        const data = await fetchExpenseReceipt(id);
        setReceipt(data);
      } catch (err) {
        setError(err.response?.data?.error || 'No se pudo cargar el comprobante.');
      } finally {
        setLoading(false);
      }
    };

    if (id) loadReceipt();
  }, [id]);

  const handleDownloadPdf = () => {
    if (!receipt) return;

    const doc = new jsPDF({ unit: 'pt', format: 'a4' });
    const pageWidth = doc.internal.pageSize.getWidth();
    let y = 40;

    doc.setFillColor(15, 23, 42);
    doc.rect(0, 0, pageWidth, 54, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.text('AGENTS WEST', 42, 26);
    doc.setFontSize(10);
    doc.text('NIT: 1010085627', 42, 42);
    doc.text('COMPROBANTE DE EGRESO', pageWidth - 170, 26);
    doc.text(`N° ${receipt.numero_comprobante}`, pageWidth - 170, 42);

    y = 90;
    doc.setTextColor(17, 24, 39);
    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    doc.text(`Fecha: ${receipt.fecha}`, 42, y);
    doc.text(`Proveedor: ${receipt.proveedor.nombre}`, 250, y);
    doc.text(`NIT: ${receipt.proveedor.nit}`, 250, y + 18);
    doc.text(`Concepto: ${receipt.concepto}`, 42, y + 36);
    doc.text(`Registrado por: ${receipt.usuario_registro.nombre}`, 42, y + 54);

    y += 92;
    doc.setDrawColor(200, 200, 200);
    doc.line(42, y, pageWidth - 42, y);
    doc.setFont('helvetica', 'bold');
    doc.text('Cantidad', 42, y + 18);
    doc.text('Detalle', 150, y + 18);
    doc.text('Valor unitario', 365, y + 18);
    doc.text('Total', 490, y + 18);
    doc.line(42, y + 24, pageWidth - 42, y + 24);

    doc.setFont('helvetica', 'normal');
    receipt.detalle.forEach((item, index) => {
      const rowY = y + 42 + index * 22;
      doc.text(String(item.cantidad), 42, rowY);
      doc.text(String(item.descripcion || 'Detalle'), 150, rowY, { maxWidth: 180 });
      doc.text(money(item.valor_unitario), 365, rowY);
      doc.text(money(item.total), 490, rowY);
    });

    const totalY = y + 42 + receipt.detalle.length * 22 + 22;
    doc.setFont('helvetica', 'bold');
    doc.text('TOTAL', 370, totalY);
    doc.text(money(receipt.total_pagado), 490, totalY);

    doc.setFont('helvetica', 'normal');
    doc.text(`Forma de pago: ${receipt.forma_pago}`, 42, totalY + 24);
    doc.text(`Observaciones: ${receipt.observaciones}`, 42, totalY + 42, { maxWidth: 500 });

    doc.line(42, totalY + 80, 220, totalY + 80);
    doc.text('Quien entrega', 42, totalY + 96);
    doc.line(270, totalY + 80, 470, totalY + 80);
    doc.text('Quien recibe', 270, totalY + 96);

    doc.save(`comprobante-egreso-${receipt.numero_comprobante}.pdf`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <div className="rounded-xl border border-slate-200 bg-white px-6 py-5 shadow-sm">
          <div className="flex items-center gap-3 text-slate-700">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-sky-600" />
            Cargando comprobante...
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100 p-6">
        <div className="max-w-md rounded-2xl border border-red-200 bg-white p-6 text-center shadow-sm">
          <p className="text-lg font-semibold text-red-600">No se pudo cargar el comprobante</p>
          <p className="mt-2 text-sm text-slate-600">{error}</p>
          <button
            type="button"
            onClick={() => navigate('/egresos')}
            className="mt-4 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-700"
          >
            Volver a egresos
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 p-4 text-slate-900 print:bg-white print:p-0">
      <div className="mx-auto max-w-5xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm print:shadow-none print:border-0">
        <div className="flex items-start justify-between border-b border-slate-200 pb-5">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-slate-900 text-lg font-black text-white">
              AW
            </div>
            <div>
              <p className="text-xl font-black uppercase tracking-wide">AGENTS WEST</p>
              <p className="text-sm text-slate-500">NIT: 1010085627</p>
            </div>
          </div>

          <div className="text-right">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Comprobante</p>
            <p className="mt-2 text-2xl font-black text-slate-900">{receipt.numero_comprobante}</p>
          </div>
        </div>

        <div className="mt-7 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-sky-700">Documento de egreso</p>
          <h1 className="mt-2 text-3xl font-black uppercase tracking-tight text-slate-900">Comprobante de egreso</h1>
        </div>

        <div className="mt-8 grid gap-4 border border-slate-200 bg-slate-50 p-4 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Fecha</p>
            <p className="mt-2 font-semibold text-slate-900">{receipt.fecha}</p>
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Proveedor</p>
            <p className="mt-2 font-semibold text-slate-900">{receipt.proveedor.nombre}</p>
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">NIT</p>
            <p className="mt-2 font-semibold text-slate-900">{receipt.proveedor.nit}</p>
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Registrado por</p>
            <p className="mt-2 font-semibold text-slate-900">{receipt.usuario_registro.nombre}</p>
          </div>
        </div>

        <div className="mt-8">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Concepto</p>
          <p className="mt-2 text-lg font-semibold text-slate-900">{receipt.concepto}</p>
        </div>

        <div className="mt-8 overflow-hidden rounded-xl border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200 text-left">
            <thead className="bg-slate-900 text-white">
              <tr>
                <th className="px-4 py-3 text-xs font-bold uppercase tracking-[0.18em]">Cantidad</th>
                <th className="px-4 py-3 text-xs font-bold uppercase tracking-[0.18em]">Detalle</th>
                <th className="px-4 py-3 text-xs font-bold uppercase tracking-[0.18em]">Valor unitario</th>
                <th className="px-4 py-3 text-xs font-bold uppercase tracking-[0.18em] text-right">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {receipt.detalle.map((item, index) => (
                <tr key={`${receipt.id}-${index}`}>
                  <td className="px-4 py-3 text-sm text-slate-700">{item.cantidad}</td>
                  <td className="px-4 py-3 text-sm text-slate-700">{item.descripcion}</td>
                  <td className="px-4 py-3 text-sm text-slate-700">{money(item.valor_unitario)}</td>
                  <td className="px-4 py-3 text-right text-sm font-semibold text-slate-900">{money(item.total)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-8 grid gap-6 md:grid-cols-[1.3fr_0.7fr]">
          <div className="space-y-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Forma de pago</p>
              <p className="mt-2 font-semibold text-slate-900">{receipt.forma_pago}</p>
            </div>
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Observaciones</p>
              <p className="mt-2 text-sm text-slate-700">{receipt.observaciones}</p>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-900 p-4 text-white">
            <div className="flex items-center justify-between border-b border-white/15 pb-3">
              <span className="text-sm uppercase tracking-[0.18em] text-slate-300">Total</span>
              <span className="text-2xl font-black">{money(receipt.total_pagado)}</span>
            </div>
            <div className="mt-4 text-sm text-slate-300">
              <p>Empresa: AGENTS WEST</p>
              <p className="mt-1">NIT: 1010085627</p>
            </div>
          </div>
        </div>

        <div className="mt-10 grid gap-8 md:grid-cols-2">
          <div>
            <div className="h-24 border-b border-slate-300" />
            <p className="mt-3 text-center text-sm font-semibold uppercase tracking-[0.18em] text-slate-600">Quien entrega</p>
          </div>
          <div>
            <div className="h-24 border-b border-slate-300" />
            <p className="mt-3 text-center text-sm font-semibold uppercase tracking-[0.18em] text-slate-600">Quien recibe</p>
          </div>
        </div>

        <div className="mt-8 flex justify-end gap-3 print:hidden">
          <button
            type="button"
            onClick={() => window.print()}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-800 transition hover:bg-slate-100"
          >
            Imprimir
          </button>
          <button
            type="button"
            onClick={handleDownloadPdf}
            className="rounded-lg bg-sky-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-800"
          >
            Descargar PDF
          </button>
        </div>
      </div>
    </div>
  );
}
