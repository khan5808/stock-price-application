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
                fill: false
            }]
        },
        options: {
            responsive: true
        }
    });
}
