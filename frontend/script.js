const API_BASE = "http://127.0.0.1:5000";

let chart;

async function getStockData() {
    const ticker = document.getElementById("ticker").value;

    const response = await fetch(`${API_BASE}/stock/${ticker}`);
    const data = await response.json();

    const labels = data.map(item => item.Date);
    const prices = data.map(item => item.Close);

    renderChart(labels, prices);
}

async function predictPrice() {
    const ticker = document.getElementById("ticker").value;

    const response = await fetch(`${API_BASE}/predict/${ticker}`);
    const data = await response.json();

    document.getElementById("prediction").innerText =
        `Predicted Price: $${data.predicted_price.toFixed(2)}`;
}

function renderChart(labels, prices) {
    const ctx = document.getElementById("stockChart").getContext("2d");

    if (chart) {
        chart.destroy();
    }

    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Stock Price",
                data: prices,
                borderWidth: 2,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            interaction: {
                mode: "index",
                intersect: false
            },
            plugins: {
                tooltip: {
                    enabled: true
                }
            },
            scales: {
                x: {
                    ticks: {
                        maxTicksLimit: 10
                    }
                }
            }
        }
    });
}

async function getStockData() {
    const ticker = document.getElementById("ticker").value;
    const timeframe = document.getElementById("timeframe").value;

    let interval = "1d";

    if (timeframe === "1d") interval = "5m";
    if (timeframe === "1w") interval = "1h";

    const response = await fetch(
        `${API_BASE}/stock/${ticker}?period=${timeframe}&interval=${interval}`
    );

    const data = await response.json();

    const labels = data.map(d => d.Datetime || d.Date);
    const prices = data.map(d => d.Close);

    renderChart(labels, prices);
}

async function getCurrentPrice() {
    const ticker = document.getElementById("ticker").value;

    const res = await fetch(`${API_BASE}/current/${ticker}`);
    const data = await res.json();

    document.getElementById("currentPrice").innerText =
        `Current Price: $${data.price.toFixed(2)}`;
}

async function predictPrice() {
    const ticker = document.getElementById("ticker").value;

    await getCurrentPrice();

    const response = await fetch(`${API_BASE}/predict/${ticker}`);
    const data = await response.json();

    document.getElementById("prediction").innerText =
        `Predicted Price: $${data.predicted_price.toFixed(2)}`;
}

