const renderChart = (canvasId, labels, data, chartLabel, chartTitle) => {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: chartLabel,
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: chartTitle
                }
            }
        }
    });
}

const getChartData = (url, canvasId, dataKey, chartLabel, chartTitle) => {
    fetch(url)
    .then(res => res.json())
    .then((results) => {
        const category_data = results[dataKey];
        const [labels, data] = [Object.keys(category_data), Object.values(category_data)];
        renderChart(canvasId, labels, data, chartLabel, chartTitle);
    })
    .catch(error => {
        console.error('Error fetching chart data:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    getChartData('/expense_category_summary', 'myChart', 'expense_category', 'Last Six Months Expenses', 'Expenses');
});