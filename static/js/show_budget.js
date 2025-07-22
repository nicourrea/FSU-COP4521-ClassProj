import { trackTableChanges } from './track_changes.js';
import { sendUpdate } from './save_changes.js';

document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById('tableContainer');
    const syncUrl = container.dataset.syncUrl;
    const tableName = container.dataset.tableName;

    const userRole = document.body.dataset.role;
    const isParent = userRole === 'parent';

    console.log("🔄 Fetching data from:", syncUrl);
    console.log("📝 Target table name:", tableName);
    console.log("👤 User role:", userRole);

    try {
        const res = await fetch(syncUrl, { method: 'POST' });
        const data = await res.json();

        console.log(" Received data from backend:", data);

        if (!data.success) {
            console.error(" Error from backend:", data.error);
            container.innerHTML = `<p class="text-red-500 font-semibold text-center">${data.error}</p>`;
            return;
        }

        // Build Table
        const table = document.createElement('table');
        table.setAttribute("data-editable", isParent ? "true" : "false");
        table.className = 'min-w-full table-auto border border-gray-300 shadow-md rounded overflow-hidden';

        // Header
        const thead = table.createTHead();
        const headerRow = thead.insertRow();
        data.column_names.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col;
            th.className = 'px-4 py-2 bg-green-700 text-white text-left font-semibold border-b';
            headerRow.appendChild(th);
        });

        // Body
        const tbody = table.createTBody();
        data.table_data.forEach(row => {
            const tr = tbody.insertRow();
            tr.dataset.rowId = row.id;
            tr.className = 'bg-gray-50';

            data.column_names.forEach(col => {
                const td = tr.insertCell();
                td.textContent = row[col];
                td.setAttribute('data-column-name', col);
                td.className = 'px-4 py-2 border text-gray-800';

                // Only parents can edit (except 'id' column)
                td.contentEditable = isParent && col !== 'id';
            });
        });

        container.innerHTML = '';
        container.appendChild(table);
        console.log(" Table built and appended to container");

        // Track changes only for parents
        if (isParent) {
            trackTableChanges();
            console.log(" Table is now being watched for edits");

            // Inject Save Button for Parents
            const saveBtn = document.createElement('button');
            saveBtn.id = 'saveChanges';
            saveBtn.dataset.table = tableName;
            saveBtn.textContent = ' Save Changes';
            saveBtn.className = 'bg-green-700 text-white px-6 py-3 rounded-lg shadow hover:bg-green-800 transition mt-6 block mx-auto';

            container.parentElement.appendChild(saveBtn);

            saveBtn.addEventListener('click', () => {
                console.log(" Save button clicked. Sending updates for:", tableName);
                sendUpdate(tableName);
            });
        }

    } catch (err) {
        container.innerHTML = `<p class="text-red-500 text-center font-semibold">Failed to load table</p>`;
        console.error(" Fetch error:", err);
    }
});