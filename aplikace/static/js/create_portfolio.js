let currentPage = 1;

    function loadStocks(page) {
        fetch(`/load_stocks/?page=${page}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                const stockList = document.getElementById('stock_list');

                data.stocks.forEach(stock => {
                    const column = document.createElement('div');
                    column.classList.add('column', 'is-one-quarter', 'stock-item');

                    const box = document.createElement('div');
                    box.classList.add('box');
                    box.style.borderTop = '4px solid #6a0dad';

                    box.innerHTML = `
                        <h2 class="subtitle" style="color: #6a0dad;">${stock.name}</h2>
                        <p><strong>P/E Ratio:</strong> ${stock.pe_ratio || 'N/A'}</p>
                        <p><strong>ROE (%):</strong> ${stock.roe || 'N/A'}</p>
                        <p><strong>Debt to Equity Ratio:</strong> ${stock.debt_to_equity || 'N/A'}</p>
                        <p><strong>Ticker:</strong> ${stock.ticker}</p>
                        <p><strong>Market Cap:</strong> ${stock.market_cap || 'N/A'}</p>
                        <p><strong>ROA (%):</strong> ${stock.roa || 'N/A'}</p>
                        <form method="post" action="{% url 'add_stock_to_portfolio' %}">
                            {% csrf_token %}
                            <input type="hidden" name="ticker" value="${stock.ticker}">
                            <div class="field">
                                <div class="control">
                                    <div class="select">
                                        <select name="portfolio_id" required>
                                            {% for portfolio in user.portfolios.all %}
                                                <option value="{{ portfolio.id }}">{{ portfolio.name }}</option>
                                            {% endfor %}
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="control" style="text-align: center; margin-top: 10px;">
                                <button type="submit" class="button is-link is-light">Add to Portfolio</button>
                            </div>
                        </form>
                    `;

                    column.appendChild(box);
                    stockList.appendChild(column);
                });

                // Hide "Load More Stocks" button if no more pages
                if (!data.has_next) {
                    document.getElementById('load_more').style.display = 'none';
                }
            })
            .catch(error => {
                console.error('There has been a problem with your fetch operation:', error);
            });
    }

    document.getElementById('load_more').addEventListener('click', function() {
        currentPage += 1;
        loadStocks(currentPage);
    });

    // Load the first page of stocks on initial page load
    loadStocks(currentPage);

    document.getElementById('stock_search').addEventListener('input', function() {
        const query = this.value.trim();
        if (query.length > 1) {
            fetch(`/stock_suggestions/?q=${encodeURIComponent(query)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log(data); // Debug: Podívej se na odpověď serveru v konzoli prohlížeče
                    const suggestions = document.getElementById('suggestions');
                    suggestions.innerHTML = '';

                    if (data.length === 0) {
                        const li = document.createElement('li');
                        li.textContent = 'No stocks found.';
                        li.classList.add('box', 'mt-2', 'p-2');
                        suggestions.appendChild(li);
                    } else {
                        data.forEach(stock => {
                            const li = document.createElement('li');
                            li.innerHTML = `
                                ${stock.ticker} - ${stock.name}
                                <form method="post" action="{% url 'add_stock_to_portfolio' %}" style="display:inline;">
                                    {% csrf_token %}
                                    <input type="hidden" name="ticker" value="${stock.ticker}">
                                    <div class="select" style="display:inline;">
                                        <select name="portfolio_id" required>
                                            {% for portfolio in user.portfolios.all %}
                                                <option value="{{ portfolio.id }}">{{ portfolio.name }}</option>
                                            {% endfor %}
                                        </select>
                                    </div>
                                    <button type="submit" class="button is-link is-light" style="margin-left: 10px;">Add to Portfolio</button>
                                </form>
                            `;
                            li.classList.add('box', 'mt-2', 'p-2');
                            li.style.cursor = 'pointer';
                            suggestions.appendChild(li);
                        });
                    }
                })
                .catch(error => {
                    console.error('There has been a problem with your fetch operation:', error);
                });
        } else {
            document.getElementById('suggestions').innerHTML = '';
        }
    });