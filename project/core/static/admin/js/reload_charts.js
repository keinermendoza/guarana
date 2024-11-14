document.addEventListener('reload_charts', (e) => {
    renderChartFromData()
})

function renderChartFromData() {
    const canvas = document.querySelectorAll('canvas').forEach((canva) => {
        // getting data from properties
        const dataValue = canva.getAttribute('data-value');
        const dataType = canva.getAttribute('data-type');

        const chartData = JSON.parse(dataValue);
        canva.style.maxHeight = '400px'; // re settign max height

        // Inicializar o re-renderizar el gráfico
        const ctx = canva.getContext('2d');
        new Chart(ctx, {
            type: dataType, // Aquí debes especificar el tipo de gráfico que estás utilizando
            data: chartData, // Usa la data que has extraído
            options: {
                responsive: true,
                scales: {
                    x: {
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.2)',
                            borderDash: [2, 10] // Define las líneas discontinuas para el eje X
                        }
                    },
                    y: {
                        beginAtZero: true,
                        
                    }
                },
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    // title: {
                    //     display: true,
                    //     text: 'Ventas Diarias por Método de Pago'
                    // },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                // Obtener el valor numérico
                                let value = context.parsed.y;

                                // Formatear como moneda en reales brasileños
                                let formattedValue = new Intl.NumberFormat('pt-BR', {
                                    style: 'currency',
                                    currency: 'BRL'
                                }).format(value);

                                // Devolver el texto del tooltip personalizado
                                return `${context.dataset.label} ${formattedValue}`;
                            }
                        }
                    }
                }
            }
        });
    })
    
}