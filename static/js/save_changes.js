import { getEditedData, resetEditedData } from './track_changes.js';

export function sendUpdate(tableName) {
    const editedData = getEditedData();

    if (Object.keys(editedData).length === 0) {
        alert("No changes to save.");
        return;
    }

    const updates = Object.entries(editedData).map(([rowId, changes]) => {
        return fetch("/update_table", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                table: tableName,
                row_id: rowId,
                updates: changes
            })
        })
        .then(res => res.json())
        .then(result => {
            if (!result.success) {
                console.error(`Update failed for row ${rowId}: ${result.error}`);
            } else {
                console.log(`Row ${rowId} updated successfully.`);
            }
        })
        .catch(error => {
            console.error(`Error updating row ${rowId}:`, error);
        });
    });

    Promise.all(updates).then(() => {
        alert("All updates sent successfully.");
        resetEditedData();
    });
}