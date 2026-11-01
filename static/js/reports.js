const categoryFilter = document.getElementById("filter-category");
const statusFilter = document.getElementById("filter-status");

const rows = document.querySelectorAll(
  "#reports-table tbody tr[data-category]",
);

function applyFilters() {
  const selectedCategory = categoryFilter.value;
  const selectedStatus = statusFilter.value;

  rows.forEach(function (row) {
    const categoryMatches =
      selectedCategory === "" || row.dataset.category === selectedCategory;

    const statusMatches =
      selectedStatus === "" || row.dataset.status === selectedStatus;

    row.hidden = !(categoryMatches && statusMatches);
  });
}

categoryFilter.addEventListener("change", applyFilters);
statusFilter.addEventListener("change", applyFilters);
