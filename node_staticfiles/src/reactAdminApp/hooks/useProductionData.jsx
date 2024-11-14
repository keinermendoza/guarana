import React from "react";
import { useEffect, useState } from "react";

function useProductionData() {
    const [titleSection, setTitleSection] = useState("")
    const [productionByItem, setProductionByItem] = useState([])
    const [totalProccecedByCategory, setTotalProccecedByCategory] = useState([])


    useEffect(() => {
        const fetchProduction = async () => {
            try {
                const resp = await fetch('/api/production/');
                const data = await resp.json();

                setTitleSection(data.main_graphic_bar_title)
                setProductionByItem(data.progress)
                setTotalProccecedByCategory(data.kpi)
                
                console.log(data)

            } catch(err) {
                console.error(err)
            }
        }
        fetchProduction()
    }, [])

    return { titleSection, productionByItem, totalProccecedByCategory };
}

export default {useProductionData}