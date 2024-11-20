import { useState } from "react";
import { ProductionChartSection, SalesChartSection, DateFilter } from "./components";
import { ToogleButton, CardWrapper } from "./ui";

const sectionOptions = {
  production: 'production',
  sales: 'sales'
}

export default function App() {
  const [sectionSwitcher, setSectionSwitcher] = useState(sectionOptions.sales)
  return (
    <div className="App">
      <DateFilter />
      
      <CardWrapper>
        <p className="mb-2">Selecione a Categoria a Visualizar</p>
        <div className="flex gap-4">
          <ToogleButton
            isActive={sectionSwitcher === sectionOptions.sales}
            handleClick={() => setSectionSwitcher(sectionOptions.sales)}
          >
            Vendas
          </ToogleButton>
          <ToogleButton
            isActive={sectionSwitcher === sectionOptions.production}
            handleClick={() => setSectionSwitcher(sectionOptions.production)}
          >
            Produção
          </ToogleButton>
        </div>

      </CardWrapper>

      {sectionSwitcher === sectionOptions.sales && <SalesChartSection />}
      {sectionSwitcher === sectionOptions.production && <ProductionChartSection />}
      
    </div>
  );
}