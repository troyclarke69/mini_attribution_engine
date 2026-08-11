import { useMemo, useState } from "react";

export default function RawTable({ rows = [], count = 0, pageSize = 25, page = 0, onPageChange, activeTab, onRowSelect }) {
  const [selectedRow, setSelectedRow] = useState(null);
  const columns = useMemo(() => {
    if (!rows.length) return [];
    return Object.keys(rows[0]);
  }, [rows]);

  const handleSelect = (row) => {
    setSelectedRow(row);
    if (onRowSelect) onRowSelect(row);
  };

  return (
    <>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column}>{column}</th>
              ))}
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={columns.length + 1}>No rows available for the current filters.</td>
              </tr>
            ) : (
              rows.map((row, index) => (
                <tr key={`${activeTab}-${index}`}>
                  {columns.map((column) => (
                    <td key={`${activeTab}-${column}-${index}`}>{String(row[column] ?? "")}</td>
                  ))}
                  <td><button className="inline-button" onClick={() => handleSelect(row)}>View details</button></td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <span>{count} total rows</span>
        <div>
          <button disabled={page === 0} onClick={() => onPageChange(Math.max(0, page - 1))}>Previous</button>
          <button disabled={(page + 1) * pageSize >= count} onClick={() => onPageChange(page + 1)}>Next</button>
        </div>
      </div>

      {selectedRow && (
        <div className="modal-backdrop" onClick={() => setSelectedRow(null)}>
          <div className="modal" onClick={(event) => event.stopPropagation()}>
            <h3>Row details</h3>
            <dl>
              {Object.entries(selectedRow).map(([key, value]) => (
                <div key={key} className="detail-row">
                  <dt>{key}</dt>
                  <dd>{String(value ?? "")}</dd>
                </div>
              ))}
            </dl>
            <button className="close-button" onClick={() => setSelectedRow(null)}>Close</button>
          </div>
        </div>
      )}
    </>
  );
}
