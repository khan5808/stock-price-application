const searchInput = document.getElementById('search-input');
const suggestionsList = document.getElementById('suggestions-list');
const stockDataContainer = document.getElementById('stock-data');
const chartPanel = document.getElementById('chart-panel');
const predictButton = document.getElementById('predict-button');
const predictionContainer = document.getElementById('prediction');
const predictionPanel = document.querySelector('.prediction-panel');
const timeframeButtons = document.querySelectorAll('.timeframe-button');
const chartCanvas = document.getElementById('price-chart');
const chartWrapper = document.querySelector('.chart-wrapper');

let stockHistory = null;
let currentPeriod = '24h';
let stockChart = null;
let lastValidSymbol = '';
let searchTimeout = null;

function formatNumber(num) {
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toString();
}

searchInput.addEventListener('input', async () => {
    const query = searchInput.value.trim();
    
    // Clear previous timeout
    if (searchTimeout) clearTimeout(searchTimeout);
    
    // Debounce search to avoid too many API calls
    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
            const suggestions = await response.json();
            displaySuggestions(suggestions);
        } catch (error) {
            console.error('Search error:', error);
        }
    }, 300);
});

searchInput.addEventListener('focus', async () => {
    if (searchInput.value.trim().length === 0) {
        try {
            const response = await fetch('/api/search?query=');
            const suggestions = await response.json();
            displaySuggestions(suggestions);
        } catch (error) {
            console.error('Suggestions error:', error);
        }
    }
});

searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const symbol = searchInput.value.trim().toUpperCase();
        if (symbol) {
            suggestionsList.innerHTML = '';
            fetchStockData(symbol);
        }
    }
});

function displaySuggestions(suggestions) {
    suggestionsList.innerHTML = '';

    if (!suggestions || suggestions.length === 0) {
        return;
    }

    suggestions.forEach((item) => {
        const li = document.createElement('li');
        li.className = 'suggestion-item';
        const symbol = typeof item === 'string' ? item : item.symbol;
        const name = typeof item === 'string' ? '' : item.name;
        
        li.innerHTML = `<strong>${symbol}</strong>${name ? ` - ${name}` : ''}`;
        li.addEventListener('click', (e) => {
            e.preventDefault();
            searchInput.value = symbol;
            suggestionsList.innerHTML = '';
            fetchStockData(symbol);
        });
        suggestionsList.appendChild(li);
    });
}

// Hide suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (e.target !== searchInput && !suggestionsList.contains(e.target)) {
        suggestionsList.innerHTML = '';
    }
});

async function fetchStockData(stockSymbol) {
    const trimmedSymbol = stockSymbol.trim().toUpperCase();
    if (!trimmedSymbol) {
        return;
    }

    stockDataContainer.innerHTML = '<p>Loading...</p>';
    stockDataContainer.classList.remove('hidden');
    chartPanel.classList.add('hidden');
    predictionPanel.classList.add('hidden');

    const response = await fetch(`/api/stock_data?symbol=${encodeURIComponent(trimmedSymbol)}`);
    if (!response.ok) {
        stockDataContainer.innerHTML = `<p class="error">Unable to load stock data for ${trimmedSymbol}. Please check the symbol and try again.</p>`;
        return;
    }

    const stockData = await response.json();
    if (!stockData || !stockData.history) {
        stockDataContainer.innerHTML = `<p class="error">No data available for ${trimmedSymbol}.</p>`;
        return;
    }

    lastValidSymbol = trimmedSymbol;
    stockHistory = stockData.history;
    currentPeriod = '24h';
    updateStockDataUI(stockData);
    renderChart(currentPeriod);
}

function updateStockDataUI(stockData) {
    const changeColor = stockData.change >= 0 ? '#27ae60' : '#d32f2f';
    const changeSign = stockData.change >= 0 ? '+' : '';
    let html = `
        <h2>${stockData.symbol} - ${stockData.name}</h2>
        <p>Current Price: <strong>$${stockData.currentPrice}</strong></p>
        <p style="color: ${changeColor};">Change: ${changeSign}${stockData.change} (${changeSign}${stockData.changePercent}%)</p>
    `;

    if (stockData.keyStats) {
        html += '<h3>Key Stats</h3><table class="key-stats-table">';
        const stats = stockData.keyStats;
        html += `<tr><td>Open</td><td>${stats.open ? '$' + stats.open.toFixed(2) : 'N/A'}</td></tr>`;
        html += `<tr><td>Day High</td><td>${stats.dayHigh ? '$' + stats.dayHigh.toFixed(2) : 'N/A'}</td></tr>`;
        html += `<tr><td>Day Low</td><td>${stats.dayLow ? '$' + stats.dayLow.toFixed(2) : 'N/A'}</td></tr>`;
        html += `<tr><td>Prev Close</td><td>${stats.prevClose ? '$' + stats.prevClose.toFixed(2) : 'N/A'}</td></tr>`;
        html += `<tr><td>52 Week High</td><td>${stats.fiftyTwoWeekHigh ? '$' + stats.fiftyTwoWeekHigh.toFixed(2) : 'N/A'}</td></tr>`;
        html += `<tr><td>52 Week High Date</td><td>${stats.fiftyTwoWeekHighDate || 'N/A'}</td></tr>`;
        html += `<tr><td>52 Week Low</td><td>${stats.fiftyTwoWeekLow ? '$' + stats.fiftyTwoWeekLow.toFixed(2) : 'N/A'}</td></tr>`;
        html += `<tr><td>52 Week Low Date</td><td>${stats.fiftyTwoWeekLowDate || 'N/A'}</td></tr>`;
        html += `<tr><td>Market Cap</td><td>${stats.marketCap ? formatNumber(stats.marketCap) : 'N/A'}</td></tr>`;
        html += `<tr><td>Shares Out</td><td>${stats.sharesOut ? formatNumber(stats.sharesOut) : 'N/A'}</td></tr>`;
        html += `<tr><td>10 Day Average Volume</td><td>${stats.avgVolume10d ? formatNumber(stats.avgVolume10d) : 'N/A'}</td></tr>`;
        html += `<tr><td>Dividend</td><td>${stats.dividend ? '$' + stats.dividend.toFixed(2) : 'N/A'}</td></tr>`;
        html += `<tr><td>Dividend Yield</td><td>${stats.dividendYield ? (stats.dividendYield * 100).toFixed(2) + '%' : 'N/A'}</td></tr>`;
        html += `<tr><td>Beta</td><td>${stats.beta ? stats.beta.toFixed(2) : 'N/A'}</td></tr>`;
        html += '</table>';
    }

    stockDataContainer.innerHTML = html;
    stockDataContainer.classList.remove('hidden');
    chartPanel.classList.remove('hidden');
    predictionPanel.classList.remove('hidden');
    if (stockData.prediction) {
        displayPrediction(stockData.prediction);
    }
    setActiveButton(currentPeriod);
}

function setActiveButton(period) {
    timeframeButtons.forEach((button) => {
        button.classList.toggle('active', button.dataset.period === period);
    });
}

function renderChart(period) {
    if (!stockHistory || !stockHistory[period]) {
        return;
    }

    const labels = stockHistory[period].labels;
    const data = stockHistory[period].prices;
    const dataset = {
        labels,
        datasets: [
            {
                label: 'Price (USD)',
                data,
                borderColor: '#35424a',
                backgroundColor: 'rgba(53, 66, 74, 0.12)',
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#35424a',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                tension: 0.25,
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        plugins: {
            legend: {
                display: true,
                position: 'top',
            },
            tooltip: {
                enabled: true,
                callbacks: {
                    title(context) {
                        return context[0]?.label || '';
                    },
                    label(context) {
                        return `Price: $${Number(context.formattedValue).toFixed(2)}`;
                    },
                },
            },
        },
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: period === '24h' ? 'Hour' : 'Date',
                },
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'Price (USD)',
                },
            },
        },
    };

    if (stockChart) {
        stockChart.data = dataset;
        stockChart.options = options;
        stockChart.update();
        return;
    }

    stockChart = new Chart(chartCanvas, {
        type: 'line',
        data: dataset,
        options,
    });
}

predictButton.addEventListener('click', async () => {
    const stockSymbol = lastValidSymbol || searchInput.value.trim().toUpperCase();
    if (!stockSymbol) {
        predictionContainer.innerHTML = '<p class="error">Please search for a stock first.</p>';
        return;
    }

    predictionContainer.innerHTML = '<p>Predicting...</p>';
    const response = await fetch(`/api/predict/${encodeURIComponent(stockSymbol)}`);
    if (!response.ok) {
        predictionContainer.innerHTML = '<p class="error">Unable to generate prediction for this stock.</p>';
        return;
    }

    const prediction = await response.json();
    if (prediction) {
        displayPrediction(prediction);
    }
});

function displayPrediction(prediction) {
    const trendEmoji = prediction.trend === 'up' ? '📈' : '📉';
    predictionContainer.innerHTML = `
        <h3>Prediction for ${prediction.symbol}</h3>
        <p>Predicted Price: <strong>$${prediction.predictedPrice}</strong></p>
        <p>Trend: ${trendEmoji} <strong>${prediction.trend.toUpperCase()}</strong></p>
    `;
}

timeframeButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const period = button.dataset.period;
        if (period === currentPeriod) {
            return;
        }
        currentPeriod = period;
        setActiveButton(period);
        renderChart(period);
    });
});
