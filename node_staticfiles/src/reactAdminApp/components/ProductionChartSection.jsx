import React from "react";
import useProductionData from "../hooks/useProductionData"

export function ProductionChartSection() {
    const {titleSection, productionByItem, totalProccecedByCategory} = useProductionData()

    return (
        <div className="bg-red-500">aqui dice algo derrepende</div>
    )
}