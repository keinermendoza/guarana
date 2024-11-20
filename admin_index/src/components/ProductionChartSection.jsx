import { useState, useEffect, useContext } from "react";
import { CategoryScale } from "chart.js";
import Chart from "chart.js/auto";
import useFetch from "../hooks/useFetch";
import {BarChart, HorizontalBarChart, Stat} from "./charts";
import { SelectedDateContext } from "../context/SelectedDateContext";
import {CardWrapper} from "../ui";
Chart.register(CategoryScale);

export function ProductionChartSection() {
  const {selectedYear, selectedMonth} = useContext(SelectedDateContext)

  const {data:production, loading, error} = useFetch(`/api/production/?year=${selectedYear}&month=${selectedMonth}`);
  const [totalByProductChartData, setTotalByProductChartData] = useState([]);
  
  useEffect(() => {
      setTotalByProductChartData({
        labels: production?.total_by_product?.map((data) => data?.title) || [],
        datasets: [
          {
            label: "Produção Mensal",
            data:production?.total_by_product?.map((data) => data?.value) || [], 
            borderWidth: 2
          }
        ]
      })
  }, [production])


  if (loading) {
    return (
      <div> Cargando... </div>
    )
  }

      if (error) {
        return (
          <div> Algo salió mal</div>
        )
      }

      if (production) {
        return (
          <>
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            {production?.total_by_category?.map((statData) => (
              <Stat key={statData.title} title={statData.title} amount={statData.metric} footerNote={statData.footer} />
            ))}
          </div>
          <CardWrapper>
            <HorizontalBarChart chartData={totalByProductChartData} title="Produtos Produzidos no Mês"  />
          </CardWrapper>

          </>
        )
      }

}