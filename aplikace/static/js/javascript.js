document.addEventListener('DOMContentLoaded', function() {
            const searchInput = document.getElementById('stock-search');
            const suggestionsList = document.getElementById('suggestions-list');

            searchInput.addEventListener('input', function() {
                const query = searchInput.value.trim();

                if (query.length > 0) {
                    fetch(`/stock_suggestions/?q=${query}`)
                        .then(response => response.json())
                        .then(data => {
                            suggestionsList.innerHTML = '';
                            if (data.length > 0) {
                                data.forEach(stock => {
                                    const li = document.createElement('li');
                                    li.classList.add('dropdown-item');
                                    li.innerHTML = `${stock.ticker} - ${stock.name}`;
                                    li.addEventListener('click', function() {
                                        window.location.href = `/stock/${stock.ticker}`; // Redirect to the stock detail page
                                    });
                                    suggestionsList.appendChild(li);
                                });
                                suggestionsList.style.display = 'block';
                            } else {
                                suggestionsList.style.display = 'none';
                            }
                        })
                        .catch(error => {
                            console.error('Error fetching stock suggestions:', error);
                        });
                } else {
                    suggestionsList.style.display = 'none';
                }
            });

            // Close the suggestions list when clicking outside the search bar
            document.addEventListener('click', function(event) {
                if (!searchInput.contains(event.target) && !suggestionsList.contains(event.target)) {
                    suggestionsList.style.display = 'none';
                }
            });
        });

        // Function to toggle sidebar visibility
        function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');

    // Toggle classes for sidebar and main content
    sidebar.classList.toggle('sidebar-hidden');
    mainContent.classList.toggle('sidebar-hidden');

    // Toggle between full version and icon-only version of the sidebar
    sidebar.classList.toggle('icon-only');

}