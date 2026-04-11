import { useState, useEffect, useRef, useCallback } from 'react';
import {
  fetchLibros, createLibro, updateLibro, deleteLibro,
  fetchEntries, createEntry, updateEntry, deleteEntry,
  fetchResumenAnual, fetchExportBlob,
} from '../../services/api';

const MES_ES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
const fmt = (n) => '$ ' + (n < 0 ? '-' : '') + Math.abs(Number(n || 0)).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const ITEMS_PER_PAGE = 12;

export default function LibrosPage() {
  /* ── Libros state ── */
  const [libros, setLibros] = useState([]);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [libroForm, setLibroForm] = useState({ nombre: '', nit: '', anio: new Date().getFullYear() });
  const [libroError, setLibroError] = useState('');
  const [savingLibro, setSavingLibro] = useState(false);
  const [editingLibroId, setEditingLibroId] = useState(null);

  /* ── Selected libro ── */
  const [selectedLibro, setSelectedLibro] = useState(null);

  /* ── Month picker ── */
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);

  /* ── Entries state ── */
  const [entries, setEntries] = useState([]);
  const [totals, setTotals] = useState({ ingresos: 0, egresos: 0, saldo: 0 });
  const [loadingEntries, setLoadingEntries] = useState(false);

  /* ── KPIs ── */
  const [kpis, setKpis] = useState({ ingresos: 0, egresos: 0, saldo: 0, count: 0 });

  /* ── Resumen ── */
  const [resumen, setResumen] = useState(null);

  /* ── Inline editing state ── */
  const [inlineEdit, setInlineEdit] = useState(null); // { id, field, value }

  /* ── Modal form state ── */
  const [editingId, setEditingId] = useState(null);
  const [modalForm, setModalForm] = useState({ descripcion: '', tipo: 'ingreso', monto: '', dia: '1' });
  const [modalError, setModalError] = useState('');
  const [savingEntry, setSavingEntry] = useState(false);
  const modalRef = useRef(null);
  const bsModalRef = useRef(null);
  const inlineInputRef = useRef(null);

  /* ── Flash message ── */
  const [flash, setFlash] = useState(null);

  const showFlash = useCallback((msg, ok = true) => {
    setFlash({ msg, ok });
    setTimeout(() => setFlash(null), 2500);
  }, []);

  /* ═══════ Load libros ═══════ */
  const loadLibros = useCallback(() => {
    fetchLibros().then(setLibros).catch(() => {});
  }, []);

  useEffect(() => {
    loadLibros();
    const saved = sessionStorage.getItem('selectedLibro');
    if (saved) {
      try {
        const libro = JSON.parse(saved);
        setSelectedLibro(libro);
        setYear(libro.anio);
      } catch {}
    }
  }, [loadLibros]);

  /* ═══════ Load entries when libro/month changes ═══════ */
  useEffect(() => {
    if (!selectedLibro) return;
    setLoadingEntries(true);
    fetchEntries(selectedLibro.id, year, month)
      .then((data) => {
        const rows = data.rows || [];
        const tot = data.totals || { ingresos: 0, egresos: 0, saldo: 0 };
        setEntries(rows);
        setTotals(tot);
        setKpis({ ingresos: tot.ingresos, egresos: tot.egresos, saldo: tot.saldo, count: rows.length });
      })
      .catch(() => {
        setEntries([]);
        setTotals({ ingresos: 0, egresos: 0, saldo: 0 });
        setKpis({ ingresos: 0, egresos: 0, saldo: 0, count: 0 });
      })
      .finally(() => setLoadingEntries(false));
  }, [selectedLibro, year, month]);

  /* ═══════ Load resumen when libro/year changes ═══════ */
  useEffect(() => {
    if (!selectedLibro) return;
    fetchResumenAnual(selectedLibro.id, year)
      .then(setResumen)
      .catch(() => setResumen(null));
  }, [selectedLibro, year]);

  /* ═══════ Bootstrap modal init ═══════ */
  useEffect(() => {
    if (modalRef.current && window.bootstrap) {
      bsModalRef.current = new window.bootstrap.Modal(modalRef.current);
    }
  }, []);

  /* ═══════ Filtered & paginated libros ═══════ */
  const filtered = libros.filter(l => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return l.nombre.toLowerCase().includes(q) || l.nit.toLowerCase().includes(q) || String(l.anio).includes(q);
  });
  const totalPages = Math.max(1, Math.ceil(filtered.length / ITEMS_PER_PAGE));
  const paginated = filtered.slice((page - 1) * ITEMS_PER_PAGE, page * ITEMS_PER_PAGE);

  /* ═══════ Handlers: Libros ═══════ */
  const handleCreateLibro = async (e) => {
    e.preventDefault();
    setLibroError('');
    setSavingLibro(true);
    try {
      const payload = { nombre: libroForm.nombre.trim(), nit: libroForm.nit.trim(), anio: Number(libroForm.anio) };
      if (editingLibroId) {
        const updated = await updateLibro(editingLibroId, payload);
        if (selectedLibro?.id === editingLibroId) {
          setSelectedLibro(updated);
          sessionStorage.setItem('selectedLibro', JSON.stringify(updated));
        }
        showFlash('Libro actualizado correctamente');
      } else {
        await createLibro(payload);
        showFlash('Libro creado correctamente');
      }
      setLibroForm({ nombre: '', nit: '', anio: new Date().getFullYear() });
      setEditingLibroId(null);
      setShowForm(false);
      loadLibros();
    } catch (err) {
      setLibroError(err.response?.data?.error || 'Error al guardar');
    } finally {
      setSavingLibro(false);
    }
  };

  const handleEditLibro = (e, libro) => {
    e.stopPropagation();
    setEditingLibroId(libro.id);
    setLibroForm({ nombre: libro.nombre, nit: libro.nit, anio: libro.anio });
    setLibroError('');
    setShowForm(true);
  };

  const handleCancelLibroForm = () => {
    setShowForm(false);
    setEditingLibroId(null);
    setLibroForm({ nombre: '', nit: '', anio: new Date().getFullYear() });
    setLibroError('');
  };

  const handleDeleteLibro = async (e, id, nombre) => {
    e.stopPropagation();
    if (!window.confirm(`¿Eliminar "${nombre}" y todos sus movimientos?`)) return;
    try {
      await deleteLibro(id);
      if (selectedLibro?.id === id) {
        setSelectedLibro(null);
        sessionStorage.removeItem('selectedLibro');
      }
      loadLibros();
      showFlash('Libro eliminado');
    } catch (err) {
      showFlash(err.response?.data?.error || 'Error al eliminar', false);
    }
  };

  const selectLibro = (libro) => {
    setSelectedLibro(libro);
    setYear(libro.anio);
    setMonth(new Date().getMonth() + 1);
    sessionStorage.setItem('selectedLibro', JSON.stringify(libro));
  };

  /* ═══════ Month navigation ═══════ */
  const prevMonth = () => {
    if (month === 1) { setMonth(12); setYear(y => y - 1); }
    else setMonth(m => m - 1);
  };
  const nextMonth = () => {
    if (month === 12) { setMonth(1); setYear(y => y + 1); }
    else setMonth(m => m + 1);
  };

  /* ═══════ Days in selected month ═══════ */
  const daysInMonth = new Date(year, month, 0).getDate();

  /* ═══════ Modal: open/close ═══════ */
  const openAddModal = () => {
    setEditingId(null);
    setModalForm({ descripcion: '', tipo: 'ingreso', monto: '', dia: '1' });
    setModalError('');
    bsModalRef.current?.show();
  };

  const openEditModal = (entry) => {
    setEditingId(entry.id);
    const isIngreso = Number(entry.ingresos) > 0;
    setModalForm({
      descripcion: entry.descripcion,
      tipo: isIngreso ? 'ingreso' : 'egreso',
      monto: String(isIngreso ? entry.ingresos : entry.egresos),
      dia: String(entry.dia || new Date(entry.fecha).getDate()),
    });
    setModalError('');
    bsModalRef.current?.show();
  };

  /* ═══════ Modal: save ═══════ */
  const handleSaveEntry = async (e) => {
    e.preventDefault();
    setModalError('');
    setSavingEntry(true);
    try {
      const monto = Number(modalForm.monto) || 0;
      const dia = Number(modalForm.dia) || 1;
      const fecha = `${year}-${String(month).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
      const payload = {
        fecha,
        descripcion: modalForm.descripcion.trim(),
        ingresos: modalForm.tipo === 'ingreso' ? monto : 0,
        egresos: modalForm.tipo === 'egreso' ? monto : 0,
      };

      if (editingId) {
        await updateEntry(editingId, payload);
        showFlash('Movimiento actualizado');
      } else {
        payload.libro_id = selectedLibro.id;
        await createEntry(payload);
        showFlash('Movimiento creado');
      }
      bsModalRef.current?.hide();
      // Re-fetch
      setLoadingEntries(true);
      const data = await fetchEntries(selectedLibro.id, year, month);
      const rows = data.rows || [];
      const tot = data.totals || { ingresos: 0, egresos: 0, saldo: 0 };
      setEntries(rows);
      setTotals(tot);
      setKpis({ ingresos: tot.ingresos, egresos: tot.egresos, saldo: tot.saldo, count: rows.length });
      setLoadingEntries(false);
      fetchResumenAnual(selectedLibro.id, year).then(setResumen).catch(() => {});
    } catch (err) {
      setModalError(err.response?.data?.error || 'Error al guardar');
    } finally {
      setSavingEntry(false);
    }
  };

  /* ═══════ Delete entry ═══════ */
  const handleDeleteEntry = async (id) => {
    if (!window.confirm('¿Eliminar este movimiento?')) return;
    try {
      await deleteEntry(id);
      showFlash('Movimiento eliminado');
      const data = await fetchEntries(selectedLibro.id, year, month);
      const rows = data.rows || [];
      const tot = data.totals || { ingresos: 0, egresos: 0, saldo: 0 };
      setEntries(rows);
      setTotals(tot);
      setKpis({ ingresos: tot.ingresos, egresos: tot.egresos, saldo: tot.saldo, count: rows.length });
      fetchResumenAnual(selectedLibro.id, year).then(setResumen).catch(() => {});
    } catch (err) {
      showFlash(err.response?.data?.error || 'Error al eliminar', false);
    }
  };

  /* ═══════ Inline edit: double-click to edit a cell ═══════ */
  const startInlineEdit = (entry, field) => {
    let value;
    if (field === 'descripcion') value = entry.descripcion;
    else if (field === 'ingresos') value = String(Number(entry.ingresos) || '');
    else if (field === 'egresos') value = String(Number(entry.egresos) || '');
    else if (field === 'dia') value = String(entry.dia);
    setInlineEdit({ id: entry.id, field, value });
    setTimeout(() => inlineInputRef.current?.focus(), 0);
  };

  const commitInlineEdit = async () => {
    if (!inlineEdit) return;
    const entry = entries.find(e => e.id === inlineEdit.id);
    if (!entry) { setInlineEdit(null); return; }

    const payload = {
      fecha: entry.fecha,
      descripcion: entry.descripcion,
      ingresos: Number(entry.ingresos) || 0,
      egresos: Number(entry.egresos) || 0,
    };

    if (inlineEdit.field === 'descripcion') {
      payload.descripcion = inlineEdit.value.trim() || entry.descripcion;
    } else if (inlineEdit.field === 'dia') {
      const dia = Math.max(1, Math.min(daysInMonth, Number(inlineEdit.value) || 1));
      payload.fecha = `${year}-${String(month).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
    } else if (inlineEdit.field === 'ingresos') {
      payload.ingresos = Math.max(0, Number(inlineEdit.value) || 0);
      if (payload.ingresos > 0) payload.egresos = 0;
    } else if (inlineEdit.field === 'egresos') {
      payload.egresos = Math.max(0, Number(inlineEdit.value) || 0);
      if (payload.egresos > 0) payload.ingresos = 0;
    }

    setInlineEdit(null);
    try {
      await updateEntry(entry.id, payload);
      const data = await fetchEntries(selectedLibro.id, year, month);
      const rows = data.rows || [];
      const tot = data.totals || { ingresos: 0, egresos: 0, saldo: 0 };
      setEntries(rows);
      setTotals(tot);
      setKpis({ ingresos: tot.ingresos, egresos: tot.egresos, saldo: tot.saldo, count: rows.length });
      fetchResumenAnual(selectedLibro.id, year).then(setResumen).catch(() => {});
      showFlash('Actualizado');
    } catch (err) {
      showFlash(err.response?.data?.error || 'Error al actualizar', false);
    }
  };

  const handleInlineKeyDown = (e) => {
    if (e.key === 'Enter') { e.preventDefault(); commitInlineEdit(); }
    else if (e.key === 'Escape') setInlineEdit(null);
  };

  /* ═══════ Quick Add: inline row at bottom ═══════ */
  const [quickAdd, setQuickAdd] = useState({ descripcion: '', tipo: 'ingreso', monto: '', dia: String(new Date().getDate()) });
  const [savingQuick, setSavingQuick] = useState(false);

  const handleQuickAdd = async (e) => {
    e.preventDefault();
    const monto = Number(quickAdd.monto);
    if (!quickAdd.descripcion.trim() || !monto || monto <= 0) return;
    setSavingQuick(true);
    try {
      const dia = Number(quickAdd.dia) || 1;
      const fecha = `${year}-${String(month).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
      await createEntry({
        libro_id: selectedLibro.id,
        fecha,
        descripcion: quickAdd.descripcion.trim(),
        ingresos: quickAdd.tipo === 'ingreso' ? monto : 0,
        egresos: quickAdd.tipo === 'egreso' ? monto : 0,
      });
      setQuickAdd({ descripcion: '', tipo: 'ingreso', monto: '', dia: String(new Date().getDate()) });
      showFlash('Movimiento creado');
      const data = await fetchEntries(selectedLibro.id, year, month);
      const rows = data.rows || [];
      const tot = data.totals || { ingresos: 0, egresos: 0, saldo: 0 };
      setEntries(rows);
      setTotals(tot);
      setKpis({ ingresos: tot.ingresos, egresos: tot.egresos, saldo: tot.saldo, count: rows.length });
      fetchResumenAnual(selectedLibro.id, year).then(setResumen).catch(() => {});
    } catch (err) {
      showFlash(err.response?.data?.error || 'Error al crear', false);
    } finally {
      setSavingQuick(false);
    }
  };

  /* ═══════ Export ═══════ */
  const handleExport = async () => {
    try {
      const blob = await fetchExportBlob(selectedLibro.id, year, month);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'libro_fiscal.xlsx';
      a.click();
      URL.revokeObjectURL(url);
      showFlash('Excel exportado');
    } catch {
      showFlash('Error al exportar', false);
    }
  };

  /* ═══════ Resumen: max for bar widths ═══════ */
  const resumenMax = resumen?.meses?.reduce((mx, m) => Math.max(mx, Number(m.ingresos) || 0, Number(m.egresos) || 0), 0) || 1;

  /* ═══════════════════════════════
     RENDER
     ═══════════════════════════════ */
  return (
    <div className="container-fluid p-4">
      {/* Flash */}
      {flash && (
        <div id="flash" className="position-fixed top-0 start-50 translate-middle-x mt-3" style={{ zIndex: 1100, minWidth: 320, animation: 'flashSlideDown .35s cubic-bezier(.4,0,.2,1)' }}>
          <div className={`alert ${flash.ok ? 'alert-success' : 'alert-danger'} alert-dismissible fade show shadow-lg`} style={{ borderRadius: 14, borderLeft: `5px solid ${flash.ok ? '#059669' : '#dc2626'}` }}>
            <i className={`bi ${flash.ok ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'} me-2`} style={{ fontSize: '1.1rem' }} />
            <strong>{flash.msg}</strong>
          </div>
        </div>
      )}

      {/* ═══════ SECTION: Libro selector ═══════ */}
      <section className="mb-4">
        {/* Search bar + New button */}
        <div className="libro-selector-bar mb-3">
          <div className="libro-selector-search">
            <i className="bi bi-search libro-search-icon" />
            <input
              type="text"
              className="libro-search-input"
              placeholder="Buscar libro por nombre, NIT o año..."
              autoComplete="off"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            />
          </div>
          <button className="action-btn action-btn-new-libro" onClick={() => { if (showForm) { handleCancelLibroForm(); } else { setEditingLibroId(null); setLibroForm({ nombre: '', nit: '', anio: new Date().getFullYear() }); setShowForm(true); } }}>
            <i className={`bi ${showForm ? 'bi-x-lg' : 'bi-plus-circle-fill'}`} />
            <span>{showForm ? 'Cancelar' : 'Nuevo Libro'}</span>
          </button>
        </div>

        {/* Libro card grid */}
        <div className="libro-grid">
          {paginated.map(l => (
            <div
              key={l.id}
              className={`libro-card${selectedLibro?.id === l.id ? ' libro-card-active' : ''}`}
              onClick={() => selectLibro(l)}
            >
              <div className="libro-card-year">{l.anio}</div>
              <div className="libro-card-body">
                <div className="libro-card-name" title={l.nombre}>{l.nombre}</div>
                <div className="libro-card-nit"><i className="bi bi-hash" />{l.nit}</div>
              </div>
              <div className="libro-card-actions">
                <button className="libro-card-btn libro-card-btn-open" title="Abrir" onClick={(e) => { e.stopPropagation(); selectLibro(l); }}>
                  <i className="bi bi-folder2-open" />
                </button>
                <button className="libro-card-btn libro-card-btn-open" title="Editar" onClick={(e) => handleEditLibro(e, l)}>
                  <i className="bi bi-pencil-fill" />
                </button>
                <button className="libro-card-btn libro-card-btn-del" title="Eliminar" onClick={(e) => handleDeleteLibro(e, l.id, l.nombre)}>
                  <i className="bi bi-trash3" />
                </button>
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="libro-empty">
              <i className="bi bi-journal-bookmark" style={{ fontSize: '2rem', display: 'block', marginBottom: 8 }} />
              {libros.length === 0 ? 'No hay libros registrados. Cree uno nuevo.' : 'No se encontraron libros que coincidan.'}
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="libro-pagination">
            <button className="libro-page-btn" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
              <i className="bi bi-chevron-left" />
            </button>
            {Array.from({ length: totalPages }, (_, i) => (
              <button key={i + 1} className={`libro-page-btn${page === i + 1 ? ' active' : ''}`} onClick={() => setPage(i + 1)}>
                {i + 1}
              </button>
            ))}
            <button className="libro-page-btn" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>
              <i className="bi bi-chevron-right" />
            </button>
          </div>
        )}

        {/* New libro form (hidden by default) */}
        {showForm && (
          <div className="card card-fiscal shadow-sm libro-form-card">
            <div className="card-header py-3 d-flex align-items-center justify-content-between">
              <h6 className="mb-0"><i className={`bi ${editingLibroId ? 'bi-pencil-square' : 'bi-plus-circle'} me-2`} />{editingLibroId ? 'Editar Libro Fiscal' : 'Crear Nuevo Libro Fiscal'}</h6>
              <button className="btn btn-sm btn-outline-secondary" onClick={handleCancelLibroForm} title="Cancelar">
                <i className="bi bi-x-lg" />
              </button>
            </div>
            <div className="card-body">
              {libroError && <div className="alert alert-danger">{libroError}</div>}
              <form onSubmit={handleCreateLibro}>
                <div className="row g-3">
                  <div className="col-12 col-md-5">
                    <label className="form-label fw-semibold"><i className="bi bi-person me-1 text-primary" />Nombre del contribuyente</label>
                    <input className="form-control form-control-lg" placeholder="Ej: Juan Pérez" value={libroForm.nombre} onChange={e => setLibroForm({ ...libroForm, nombre: e.target.value })} required maxLength={200} />
                  </div>
                  <div className="col-12 col-md-3">
                    <label className="form-label fw-semibold"><i className="bi bi-hash me-1 text-primary" />NIT</label>
                    <input className="form-control form-control-lg" placeholder="Ej: 1010085627-1" value={libroForm.nit} onChange={e => setLibroForm({ ...libroForm, nit: e.target.value })} required maxLength={50} />
                  </div>
                  <div className="col-6 col-md-2">
                    <label className="form-label fw-semibold"><i className="bi bi-calendar3 me-1 text-primary" />Año</label>
                    <input type="number" className="form-control form-control-lg" placeholder="YYYY" min={1990} max={2099} value={libroForm.anio} onChange={e => setLibroForm({ ...libroForm, anio: e.target.value })} required />
                  </div>
                  <div className="col-12 col-md-2 d-flex align-items-end">
                    <button type="submit" className="btn btn-primary btn-lg w-100" disabled={savingLibro}>
                      <i className="bi bi-check-lg me-1" />{savingLibro ? 'Guardando...' : (editingLibroId ? 'Guardar' : 'Crear')}
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        )}
      </section>

      {/* ═══════ SECTIONS VISIBLE WHEN LIBRO SELECTED ═══════ */}
      {selectedLibro && (
        <>
          {/* KPIs */}
          <section className="mb-4">
            <div className="row g-3">
              <div className="col-6 col-md-3">
                <div className="card kpi-card border-0 shadow-sm text-center">
                  <div className="card-body py-3">
                    <div className="text-uppercase small text-muted">Ingresos</div>
                    <div className="h5 mb-0 text-success fw-bold">{fmt(kpis.ingresos)}</div>
                  </div>
                </div>
              </div>
              <div className="col-6 col-md-3">
                <div className="card kpi-card border-0 shadow-sm text-center">
                  <div className="card-body py-3">
                    <div className="text-uppercase small text-muted">Egresos</div>
                    <div className="h5 mb-0 text-danger fw-bold">{fmt(kpis.egresos)}</div>
                  </div>
                </div>
              </div>
              <div className="col-6 col-md-3">
                <div className="card kpi-card border-0 shadow-sm text-center">
                  <div className="card-body py-3">
                    <div className="text-uppercase small text-muted">Saldo</div>
                    <div className={`h5 mb-0 fw-bold ${kpis.saldo >= 0 ? 'text-success' : 'text-danger'}`}>{fmt(kpis.saldo)}</div>
                  </div>
                </div>
              </div>
              <div className="col-6 col-md-3">
                <div className="card kpi-card border-0 shadow-sm text-center">
                  <div className="card-body py-3">
                    <div className="text-uppercase small text-muted">Registros</div>
                    <div className="h5 mb-0 fw-bold text-info">{kpis.count}</div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Month Picker + Table */}
          <section className="mb-4">
            <div className="month-picker-bar mb-3">
              <button className="month-picker-arrow" onClick={prevMonth} title="Mes anterior">
                <i className="bi bi-chevron-left" />
              </button>
              <div className="month-picker-display">
                <span className="month-picker-month">{MES_ES[month]}</span>
                <span className="month-picker-year">{year}</span>
              </div>
              <button className="month-picker-arrow" onClick={nextMonth} title="Mes siguiente">
                <i className="bi bi-chevron-right" />
              </button>
            </div>

            <div className="action-toolbar mb-3">
              <button className="action-btn action-btn-add" onClick={openAddModal}>
                <i className="bi bi-plus-circle-fill" /><span>Nueva Operación</span>
              </button>
              <button className="action-btn action-btn-export" onClick={handleExport}>
                <i className="bi bi-file-earmark-excel-fill" /><span>Exportar Excel</span>
              </button>
            </div>

            <div className="card card-fiscal shadow-sm">
              <div className="card-body p-0">
                <div className="table-responsive">
                  <table className="table table-hover align-middle mb-0 movements-table">
                    <thead>
                      <tr>
                        <th style={{ width: 60 }} className="text-center">Día</th>
                        <th>Descripción</th>
                        <th className="text-end" style={{ width: 130 }}>Ingresos</th>
                        <th className="text-end" style={{ width: 130 }}>Egresos</th>
                        <th className="text-end" style={{ width: 120 }}>Saldo</th>
                        <th style={{ width: 90 }} className="text-center">Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {loadingEntries ? (
                        <tr>
                          <td colSpan={6} className="text-center py-4">
                            <div className="spinner-border spinner-border-sm text-primary me-2" />Cargando datos...
                          </td>
                        </tr>
                      ) : entries.length === 0 && !selectedLibro ? (
                        <tr><td colSpan={6} className="text-center text-muted py-4">Sin movimientos para este mes</td></tr>
                      ) : (
                        <>
                          {entries.map(e => (
                            <tr key={e.id} className="entry-row-anim">
                              <td className="text-center editable-cell" onDoubleClick={() => startInlineEdit(e, 'dia')}>
                                {inlineEdit?.id === e.id && inlineEdit.field === 'dia' ? (
                                  <input ref={inlineInputRef} type="number" min={1} max={daysInMonth} className="inline-edit-input text-center" style={{ width: 50 }}
                                    value={inlineEdit.value} onChange={ev => setInlineEdit({ ...inlineEdit, value: ev.target.value })}
                                    onBlur={commitInlineEdit} onKeyDown={handleInlineKeyDown} />
                                ) : e.dia}
                              </td>
                              <td className="editable-cell" onDoubleClick={() => startInlineEdit(e, 'descripcion')}>
                                {inlineEdit?.id === e.id && inlineEdit.field === 'descripcion' ? (
                                  <input ref={inlineInputRef} type="text" className="inline-edit-input" style={{ width: '100%' }}
                                    value={inlineEdit.value} onChange={ev => setInlineEdit({ ...inlineEdit, value: ev.target.value })}
                                    onBlur={commitInlineEdit} onKeyDown={handleInlineKeyDown} />
                                ) : e.descripcion}
                              </td>
                              <td className="text-end editable-cell" onDoubleClick={() => startInlineEdit(e, 'ingresos')}>
                                {inlineEdit?.id === e.id && inlineEdit.field === 'ingresos' ? (
                                  <input ref={inlineInputRef} type="number" step="0.01" min="0" className="inline-edit-input text-end" style={{ width: 110 }}
                                    value={inlineEdit.value} onChange={ev => setInlineEdit({ ...inlineEdit, value: ev.target.value })}
                                    onBlur={commitInlineEdit} onKeyDown={handleInlineKeyDown} />
                                ) : Number(e.ingresos) > 0 ? <span className="text-success">{fmt(e.ingresos)}</span> : ''}
                              </td>
                              <td className="text-end editable-cell" onDoubleClick={() => startInlineEdit(e, 'egresos')}>
                                {inlineEdit?.id === e.id && inlineEdit.field === 'egresos' ? (
                                  <input ref={inlineInputRef} type="number" step="0.01" min="0" className="inline-edit-input text-end" style={{ width: 110 }}
                                    value={inlineEdit.value} onChange={ev => setInlineEdit({ ...inlineEdit, value: ev.target.value })}
                                    onBlur={commitInlineEdit} onKeyDown={handleInlineKeyDown} />
                                ) : Number(e.egresos) > 0 ? <span className="text-danger">{fmt(e.egresos)}</span> : ''}
                              </td>
                              <td className="text-end fw-semibold">{fmt(e.saldo)}</td>
                              <td className="text-center">
                                <div className="row-actions row-actions-visible">
                                  <button className="row-action-btn row-action-edit" title="Editar" onClick={() => openEditModal(e)}>
                                    <i className="bi bi-pencil-fill" />
                                  </button>
                                  <button className="row-action-btn row-action-del" title="Eliminar" onClick={() => handleDeleteEntry(e.id)}>
                                    <i className="bi bi-trash-fill" />
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                          {/* ── Quick Add Row ── */}
                          <tr className="quick-add-row">
                            <td className="text-center">
                              <select className="quick-add-input text-center" style={{ width: 55 }} value={quickAdd.dia} onChange={ev => setQuickAdd({ ...quickAdd, dia: ev.target.value })}>
                                {Array.from({ length: daysInMonth }, (_, i) => (
                                  <option key={i + 1} value={i + 1}>{i + 1}</option>
                                ))}
                              </select>
                            </td>
                            <td>
                              <input type="text" className="quick-add-input" placeholder="Descripción..." style={{ width: '100%' }}
                                value={quickAdd.descripcion} onChange={ev => setQuickAdd({ ...quickAdd, descripcion: ev.target.value })}
                                onKeyDown={ev => { if (ev.key === 'Enter') handleQuickAdd(ev); }} />
                            </td>
                            <td className="text-end" colSpan={2}>
                              <div className="d-flex align-items-center gap-2 justify-content-end">
                                <select className="quick-add-input" style={{ width: 110 }} value={quickAdd.tipo} onChange={ev => setQuickAdd({ ...quickAdd, tipo: ev.target.value })}>
                                  <option value="ingreso">💰 Ingreso</option>
                                  <option value="egreso">💸 Egreso</option>
                                </select>
                                <input type="number" step="0.01" min="0.01" className="quick-add-input text-end" style={{ width: 110 }}
                                  placeholder="Monto" value={quickAdd.monto} onChange={ev => setQuickAdd({ ...quickAdd, monto: ev.target.value })}
                                  onKeyDown={ev => { if (ev.key === 'Enter') handleQuickAdd(ev); }} />
                              </div>
                            </td>
                            <td className="text-center" colSpan={2}>
                              <button className="quick-add-btn" onClick={handleQuickAdd} disabled={savingQuick || !quickAdd.descripcion.trim() || !quickAdd.monto}>
                                <i className="bi bi-plus-lg me-1" />{savingQuick ? '...' : 'Agregar'}
                              </button>
                            </td>
                          </tr>
                        </>
                      )}
                    </tbody>
                    {entries.length > 0 && (
                      <tfoot>
                        <tr className="movements-total">
                          <th className="text-end" colSpan={2}>TOTAL</th>
                          <th className="text-end">{fmt(totals.ingresos)}</th>
                          <th className="text-end">{fmt(totals.egresos)}</th>
                          <th className="text-end">{fmt(totals.saldo)}</th>
                          <th />
                        </tr>
                      </tfoot>
                    )}
                  </table>
                </div>
              </div>
            </div>
          </section>

          {/* ═══════ Resumen Anual ═══════ */}
          <section className="mb-4">
            <div className="card card-fiscal shadow-sm">
              <div className="card-header py-3 d-flex align-items-center justify-content-between">
                <h6 className="mb-0">
                  <i className="bi bi-bar-chart-line me-2" />Resumen Anual
                  <span className="badge bg-primary ms-2">{year}</span>
                </h6>
                <div className="d-flex gap-3 small fw-semibold">
                  <span className="text-success"><i className="bi bi-circle-fill me-1" style={{ fontSize: '.5rem', verticalAlign: 'middle' }} />Ingresos</span>
                  <span className="text-danger"><i className="bi bi-circle-fill me-1" style={{ fontSize: '.5rem', verticalAlign: 'middle' }} />Egresos</span>
                </div>
              </div>
              <div className="card-body p-3">
                <div className="row g-3">
                  {MES_ES.slice(1).map((mesNombre, i) => {
                    const m = resumen?.meses?.find(x => x.mes === i + 1);
                    const ing = Number(m?.ingresos) || 0;
                    const egr = Number(m?.egresos) || 0;
                    const hasData = ing > 0 || egr > 0;
                    const balance = ing - egr;
                    return (
                      <div key={i} className="col-6 col-md-4 col-lg-3">
                        <div
                          className={`resumen-month-card${hasData ? ' has-data' : ''}`}
                          onClick={hasData ? () => setMonth(i + 1) : undefined}
                        >
                          <div className="resumen-month-name">{mesNombre}</div>
                          <div className="resumen-bars">
                            <div className="resumen-bar-row">
                              <span className="resumen-bar-label">📈</span>
                              <div className="resumen-bar-track">
                                <div className="resumen-bar-fill" style={{ width: `${(ing / resumenMax * 100) || 0}%`, background: '#10b981' }} />
                              </div>
                              <span className="resumen-bar-val">{fmt(ing)}</span>
                            </div>
                            <div className="resumen-bar-row">
                              <span className="resumen-bar-label">📉</span>
                              <div className="resumen-bar-track">
                                <div className="resumen-bar-fill" style={{ width: `${(egr / resumenMax * 100) || 0}%`, background: '#ef4444' }} />
                              </div>
                              <span className="resumen-bar-val">{fmt(egr)}</span>
                            </div>
                          </div>
                          <div className="resumen-month-balance" style={{ color: balance >= 0 ? '#059669' : '#dc2626' }}>
                            {fmt(balance)}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
              {resumen?.totales && (
                <div className="card-footer bg-white border-top py-3">
                  <div className="row text-center fw-bold">
                    <div className="col-4">
                      <span className="text-muted small d-block">Total Ingresos</span>
                      <span className="text-success h6 mb-0">{fmt(resumen.totales.ingresos)}</span>
                    </div>
                    <div className="col-4">
                      <span className="text-muted small d-block">Total Egresos</span>
                      <span className="text-danger h6 mb-0">{fmt(resumen.totales.egresos)}</span>
                    </div>
                    <div className="col-4">
                      <span className="text-muted small d-block">Balance</span>
                      <span className={`h6 mb-0 ${(resumen.totales.saldo || 0) >= 0 ? 'text-success' : 'text-danger'}`}>{fmt(resumen.totales.saldo)}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </section>
        </>
      )}

      {/* ═══════ MODAL: Movimiento ═══════ */}
      <div className="modal fade" ref={modalRef} tabIndex={-1} aria-hidden="true">
        <div className="modal-dialog modal-lg">
          <div className="modal-content">
            <form onSubmit={handleSaveEntry}>
              <div className="modal-header modal-header-gradient">
                <h5 className="modal-title">
                  <i className="bi bi-pencil-square me-2" />
                  {editingId ? 'Editar operación' : 'Nueva operación'}
                </h5>
                <button type="button" className="btn-close btn-close-white" data-bs-dismiss="modal" />
              </div>
              <div className="modal-body px-4 py-4">
                {modalError && <div className="alert alert-danger">{modalError}</div>}
                <div className="row g-3">
                  <div className="col-12 col-md-6">
                    <label className="form-label fw-semibold"><i className="bi bi-card-text me-1 text-primary" />Descripción</label>
                    <input
                      type="text"
                      className="form-control form-control-lg"
                      required
                      maxLength={255}
                      placeholder="Ej: Pago servicios públicos"
                      value={modalForm.descripcion}
                      onChange={e => setModalForm({ ...modalForm, descripcion: e.target.value })}
                    />
                  </div>
                  <div className="col-6 col-md-3">
                    <label className="form-label fw-semibold"><i className="bi bi-arrow-left-right me-1 text-primary" />Tipo</label>
                    <select
                      className="form-select form-select-lg"
                      value={modalForm.tipo}
                      onChange={e => setModalForm({ ...modalForm, tipo: e.target.value })}
                    >
                      <option value="ingreso">💰 Ingreso</option>
                      <option value="egreso">💸 Egreso</option>
                    </select>
                  </div>
                  <div className="col-6 col-md-3">
                    <label className="form-label fw-semibold"><i className="bi bi-currency-dollar me-1 text-primary" />Monto</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0.01"
                      className="form-control form-control-lg"
                      required
                      placeholder="0.00"
                      value={modalForm.monto}
                      onChange={e => setModalForm({ ...modalForm, monto: e.target.value })}
                    />
                  </div>
                  <div className="col-12">
                    <label className="form-label fw-semibold"><i className="bi bi-calendar-event me-1 text-primary" />Fecha</label>
                    <div className="d-flex align-items-center gap-2">
                      <select
                        className="form-select"
                        style={{ width: 100 }}
                        value={modalForm.dia}
                        onChange={e => setModalForm({ ...modalForm, dia: e.target.value })}
                      >
                        {Array.from({ length: daysInMonth }, (_, i) => (
                          <option key={i + 1} value={i + 1}>{i + 1}</option>
                        ))}
                      </select>
                      <div className="form-control bg-light text-center flex-grow-1" style={{ cursor: 'default' }}>
                        {MES_ES[month]} {year}
                      </div>
                    </div>
                    <small className="text-muted mt-1 d-block">Solo puede seleccionar el día. Mes y año fijos según el filtro actual.</small>
                  </div>
                </div>
              </div>
              <div className="modal-footer border-0 px-4 pb-4">
                <button type="button" className="btn btn-light px-4" data-bs-dismiss="modal">Cancelar</button>
                <button type="submit" className="btn btn-primary btn-lg px-4" disabled={savingEntry}>
                  <i className="bi bi-check-lg me-1" />{savingEntry ? 'Guardando...' : 'Guardar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
