import { Bar } from "react-chartjs-2";
import { defaults } from 'chart.js';

defaults.font.family = 'monospace';

export function BarChart({ chartData, moneyOptions=false, options=null, title=null }) {

  const defaultOptions = {
    plugins: {
        title: {
        display: title,
        text: title
        },
  }
}
const moneyChartOptions = {
  responsive: true,
  plugins: {
    title: {
      display: title,
      text: title
      },
      legend: {
          display: true,
          position: "top",
      },
      tooltip: {
          callbacks: {
              label: function (context) {
                  return `R$ ${context.raw?.toLocaleString("pt-BR")}`;
              },
          },
      },
  },
  scales: {
      y: {
          ticks: {
              callback: function (value) {
                  return `R$ ${value.toLocaleString("pt-BR")}`;
              },
          },
      },
  },
};


  const chartOptions = options || moneyOptions && moneyChartOptions || defaultOptions;
    return (
        <Bar
          data={chartData}
          options={chartOptions}
        />
    );
  }
