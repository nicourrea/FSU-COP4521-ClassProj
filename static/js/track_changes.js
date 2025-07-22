// static/js/track_changes.js

let editedData = {};  // Format: { rowId: { colName: newValue, ... } }

export function trackTableChanges() {
    editedData = {};  // reset if re-initialized

    const tables = document.querySelectorAll('table[data-editable="true"]');

    tables.forEach(table => {
        table.querySelectorAll("td[contenteditable='true']").forEach(cell => {
            // Capture value on blur (when user leaves the cell)
            cell.addEventListener("blur", () => {
                const row = cell.closest("tr");
                const rowId = row?.dataset.rowId;
                const columnName = cell.getAttribute("data-column-name");
                const newValue = cell.textContent.trim();

                if (rowId && columnName) {
                    if (!editedData[rowId]) editedData[rowId] = {};
                    editedData[rowId][columnName] = newValue;
                    console.log(`📝 Cell updated (row ${rowId}, column ${columnName}):`, newValue);
                }
            });
        });
    });
}

export function getEditedData() {
    return editedData;
}

export function resetEditedData() {
    editedData = {};
}