import { useState, useEffect, useContext } from "react";
import { CategoryScale } from "chart.js";
import Chart from "chart.js/auto";
import useFetch from "../hooks/useFetch";
import {BarChart, HorizontalBarChart, Stat, PieChart} from "./charts";


import { SelectedDateContext } from "../context/SelectedDateContext";

Chart.register(CategoryScale);

export function SalesChartSection() {
    const {selectedYear, selectedMonth} = useContext(SelectedDateContext)

    const {data:sales, loading, error} = useFetch(`/api/sales/?year=${selectedYear}&month=${selectedMonth}`);
    const [productDailySalesTotal, setProductDailySalesTotal] = useState(null);
    const [productMonthlySalesTotal, setProductMonthlySalesTotal] = useState(null);
    const [productMonthlySalesQuantity, setProductMonthlySalesQuantity] = useState(null);

    useEffect(() => {
      setProductMonthlySalesTotal({
        labels: sales?.total_product_monthly.map((data) => data?.label),
        datasets: [
          {
            label: "Ingresos por Produto",
            data:sales?.total_product_monthly.map((data) => data?.data), 
            borderColor: "black",
            backgroundColor: sales?.total_product_monthly.map((data) => data?.backgroundColor),
            barThickness: 30,
            borderWidth: 2
          }
        ]
      })

      setProductDailySalesTotal({
        labels: sales?.total_product_daily?.labels || [],
        datasets: sales?.total_product_daily?.datasets || [],
      })

      setProductMonthlySalesQuantity({
        labels: sales?.total_quantity_monthly?.map(data => data?.title),
        datasets: [{
          data: sales?.total_quantity_monthly?.map(data => parseInt(data?.value)) || [],
          label: "Unidades Vendidas" 
        }

        ]
      })

     }, [sales])

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

      if (sales) {
        return (
          <>
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            {sales.total_by_method.map((statData) => (
              <Stat key={statData.title} title={statData.title} amount={statData.metric} footerNote={statData.footer} />
            ))}
          </div>
          <section className="p-4 mb-10 border border-solid border-gray-400 rounded-md ">
            <div className="max-w-5xl mx-auto flex flex-col gap-8">
              <BarChart chartData={productDailySalesTotal} moneyOptions title="Venda Diária por Método de Pagamento" />
              <HorizontalBarChart chartData={productMonthlySalesQuantity} title="Quantidade Mensal Vendida por Produto" />
            </div>
            <div className="max-w-3xl mt-8 mx-auto">
              <PieChart chartData={productMonthlySalesTotal} title="Receitas Mensais por Produto" />
            </div>
          </section>

          </>
        )
      }

}