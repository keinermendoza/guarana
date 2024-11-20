import { Bar } from "react-chartjs-2";
import { defaults } from 'chart.js';

defaults.font.family = 'monospace';
export function HorizontalBarChart({ chartData, title=null }) {
  return (
      <Bar
        data={chartData}
        options={{
            indexAxis: 'y',
            plugins: {
                title: {
                display: title,
                text: title
                },
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true
                },
            },
           
          }
        }}
      />
  );
}