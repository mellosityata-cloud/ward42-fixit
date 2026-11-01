async function loadSummary() {
  const errorBox = document.getElementById("dashboard-error");

  try {
    // Request report summary data from the API
    const response = await fetch("/api/reports/summary");

    // Check whether the request was successful
    if (!response.ok) {
      throw new Error("Unable to load dashboard data. Please try again.");
    }

    // Convert the JSON response into JavaScript data
    const data = await response.json();

    // Display the total number of reports
    document.getElementById("total").textContent = data.total;

    // Get the category table body
    const categoryBody = document.getElementById("category-body");

    // Display reports grouped by category
    for (const [category, count] of Object.entries(data.by_category)) {
      const row = document.createElement("tr");

      const categoryCell = document.createElement("td");
      categoryCell.textContent = category;

      const countCell = document.createElement("td");
      countCell.textContent = count;

      row.appendChild(categoryCell);
      row.appendChild(countCell);

      categoryBody.appendChild(row);
    }

    // Get the status table body
    const statusBody = document.getElementById("status-body");

    // Display reports grouped by status
    for (const [status, count] of Object.entries(data.by_status)) {
      const row = document.createElement("tr");

      const statusCell = document.createElement("td");
      statusCell.textContent = status;

      const countCell = document.createElement("td");
      countCell.textContent = count;

      row.appendChild(statusCell);
      row.appendChild(countCell);

      statusBody.appendChild(row);
    }
  } catch (error) {
    // Display an error message if the request fails
    errorBox.textContent = error.message;
    errorBox.classList.remove("d-none");
  }
}

// Load the dashboard data
loadSummary();
