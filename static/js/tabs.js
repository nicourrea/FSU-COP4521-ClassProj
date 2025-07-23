// Import both functions from get_cat_expense.js
import { buildExpenseTable, buildExpenseTableFromData } from "./get_cat_expense.js";

// Fetch child-only expenses and render using the shared table builder
async function fetchChildExpenses(container) {
    const response = await fetch('/view_child_expenses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });

    const data = await response.json();

    if (!data.success) {
        container.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        return;
    }

    buildExpenseTableFromData(data, container);
}

export function setupTabs() {
    const tabs = document.querySelectorAll('.tablink');
    const contents = document.querySelectorAll('.tab-content');

    function showTab(index) {
        tabs.forEach(tab => tab.classList.remove('active'));
        contents.forEach(content => content.style.display = 'none');

        const selectedTab = tabs[index];
        const selectedContent = contents[index];

        if (selectedTab && selectedContent) {
            selectedTab.classList.add('active');
            selectedContent.style.display = 'block';

            const categoryName = selectedContent.dataset.category;
            const container = selectedContent.querySelector('.table-container');
            if (!container) return;

            container.innerHTML = "";

            // Special handling for child tab
            if (categoryName === "__child__") {
                fetchChildExpenses(container);
            } else {
                buildExpenseTable(categoryName, container);
            }
        }
    }

    tabs.forEach((tab, i) => {
        tab.addEventListener('click', () => showTab(i));
    });

    // Show first tab by default
    if (tabs.length > 0) {
        showTab(0);
    }
}