import { useState } from "react";

export default function HelpModal({ label = "More information", title, children }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button type="button" className="help-icon" aria-label={label} onClick={() => setOpen(true)}>
        ?
      </button>
      {open && (
        <div className="modal-backdrop" onClick={() => setOpen(false)}>
          <div className="modal" onClick={(event) => event.stopPropagation()}>
            <h3>{title}</h3>
            {children}
            <button type="button" className="close-button" onClick={() => setOpen(false)}>
              Close
            </button>
          </div>
        </div>
      )}
    </>
  );
}
