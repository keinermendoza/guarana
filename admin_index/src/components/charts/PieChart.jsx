import { Pie } from "react-chartjs-2";

export function PieChart({ chartData, title=null }) {
  return (
      <Pie
        data={chartData}
        options={{
          plugins: {
            title: {
              display: title,
              text: title
            },
            legend: {
              display: true,
              position: "left",
            },
            tooltip: {
              callbacks: {
                  label: function (context) {
                      return `R$ ${context.raw?.toLocaleString("pt-BR")}`;
                  },
              },
            },
          }
        }}
      />
  );
}