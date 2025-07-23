// Fetch and build the expense table for a specific category
import { trackTableChanges } from './track_changes.js';

export async function buildExpenseTable(categoryName, container) {
    const isChildTab = categoryName === '__child__';
    const endpoint = isChildTab ? '/view_child_expenses' : '/view_category_expenses';

    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: isChildTab ? null : JSON.stringify({ category: categoryName })
    });

    const data = await response.json();

    if (!data.success) {
        container.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        return;
    }

    buildExpenseTableFromData(data, container, categoryName);
}

// Set up filter buttons for each category tab
export function setupFilters() {
    document.querySelectorAll('.apply-filter-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const tab = e.target.closest('.tab-content');
            const container = tab.querySelector('.table-container');
            const category = tab.dataset.category;

            const col = tab.querySelector('.filter-col').value;
            const op = tab.querySelector('.filter-op').value;
            const val = parseFloat(tab.querySelector('.filter-val').value);

            if (!isNaN(val)) {
                try {
                    const res = await fetch('/view_category_expenses', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ category: category })
                    });

                    const data = await res.json();

                    if (!data.success) {
                        container.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                        return;
                    }

                    const filtered = data.table_data.filter(row => {
                        const targetVal = parseFloat(row[col]);
                        if (isNaN(targetVal)) return false;
                        if (op === 'lt') return targetVal < val;
                        if (op === 'gt') return targetVal > val;
                        if (op === 'eq') return targetVal === val;
                        return false;
                    });

                    data.table_data = filtered;
                    buildExpenseTableFromData(data, container, category);
                } catch (err) {
                    container.innerHTML = `<p style="color: red;">Fetch failed: ${err.message}</p>`;
                    console.error(err);
                }
            } else {
                alert("Please enter a valid number to filter by.");
            }
        });
    });
}

// Render a table with expense data
function buildExpenseTableFromData(data, container, categoryName) {
    const userRole = document.body.dataset.role;
    const isParent = userRole === 'parent';

    const table = document.createElement('table');
    table.setAttribute("data-editable", "true"); 
    table.border = '1';
    table.style.margin = '40px auto';
    table.style.borderCollapse = 'collapse';
    table.style.width = '85%';
    table.style.fontSize = '17px';
    table.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.1)';
    table.style.border = '1px solid #ccc';
    table.style.textAlign = 'center';

    const thead = table.createTHead();
    const headerRow = thead.insertRow();
    data.column_names.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        styleHeaderCell(th);
        headerRow.appendChild(th);
    });

    if (isParent) {
        const th = document.createElement('th');
        th.textContent = 'Actions';
        styleHeaderCell(th);
        headerRow.appendChild(th);
    }

    const tbody = table.createTBody();
    data.table_data.forEach(row => {
        const tr = tbody.insertRow();
        tr.dataset.rowId = row.id;

        data.column_names.forEach(col => {
            const td = tr.insertCell();
            let val = row[col];
            if (col.toLowerCase().includes('date') && val) {
                const d = new Date(val);
                val = !isNaN(d) ? d.toLocaleDateString('en-US') : val;
            }

            td.textContent = val ?? '';
            td.style.textAlign = 'center';
            td.style.padding = '10px 14px';
            td.style.borderBottom = '1px solid #ccc';

            if (isParent && col !== "id") {
                td.setAttribute("contenteditable", "true");
                td.setAttribute("data-column-name", col);
                td.setAttribute("data-original-value", val);
            }
        });

        if (isParent) {
            const td = tr.insertCell();
            td.innerHTML = `<button class="delete-expense-btn" data-id="${row.id}">🗑️</button>`;
            td.style.padding = '10px';
        }
    });

    container.innerHTML = '';
    container.appendChild(table);

    if (isParent) {
        setupDeleteButtons();
        ensureSaveButtonExists();
        trackTableChanges(); // Only track changes for editable tables
    }
}

function styleHeaderCell(th) {
    th.style.padding = '12px 16px';
    th.style.backgroundColor = '#2e8b57'; // dark green
    th.style.color = '#fff';
    th.style.fontWeight = 'bold';
    th.style.borderBottom = '2px solid #555';
}

function setupDeleteButtons() {
    document.querySelectorAll('.delete-expense-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.dataset.id;
            const confirmDelete = confirm("Are you sure you want to delete this expense?");
            if (!confirmDelete) return;

            const resp = await fetch('/delete_expense', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id })
            });

            const result = await resp.json();
            if (result.success) {
                const tab = btn.closest('.tab-content');
                const category = tab.dataset.category;
                const container = tab.querySelector('.table-container');
                buildExpenseTable(category, container);
            } else {
                alert("Error deleting: " + result.error);
            }
        });
    });
}

function ensureSaveButtonExists() {
    if (!document.querySelector('#saveChanges')) {
        const saveBtn = document.createElement('button');
        saveBtn.id = 'saveChanges';
        saveBtn.dataset.table = 'expenses';
        saveBtn.textContent = '💾 Save All Edits';
        saveBtn.style.margin = '20px auto';
        saveBtn.style.display = 'block';
        saveBtn.className = 'px-6 py-3 bg-green-700 text-white rounded-lg shadow hover:bg-green-800 transition';
        saveBtn.addEventListener('click', () => {
            import('./save_changes.js').then(module => {
                module.sendUpdate('expenses');
            });
        });
        document.body.appendChild(saveBtn);
    }
}

export { buildExpenseTableFromData };