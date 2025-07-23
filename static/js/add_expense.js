// static/js/add_expense.js

// Setup form submission for adding expenses
export function setupAddExpense(buildExpenseTable) {
    // Loop through each expense form on the page
    document.querySelectorAll('.input-container form').forEach(form => {
        form.addEventListener('submit', async e => {
            e.preventDefault();

            // Convert form data to a plain object
            const data = Object.fromEntries(new FormData(form).entries());
            console.log("Submitting to /add_expense:", JSON.stringify(data));

            // Parse amount field
            data.amount = parseFloat(data.amount);
            if (isNaN(data.amount)) {
                alert("Enter a valid number for the amount.");
                return;
            }

            // Send POST request to add expense
            const resp = await fetch('/add_expense', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await resp.json();
            if (!result.success) {
                alert("Error adding expense: " + result.error);
                return;
            }

            // Clear form after successful addition
            form.reset();

            // Find the associated category tab
            const pane = form.closest('.tab-content');
            const dept = pane.querySelector('h1')?.textContent.replace(' Expenses', '').trim();
            const container = pane.querySelector('.table-container');

            if (dept && container) {
                buildExpenseTable(dept, container);
            }
        });
    });
}