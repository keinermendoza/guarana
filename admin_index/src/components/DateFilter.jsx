import { useState, useEffect, useContext } from "react"
import useFetch from "../hooks/useFetch";
import { SelectedDateContext } from "../context/SelectedDateContext";
import { ToogleButton, CardWrapper } from "../ui";


function MessageError () {
  return (
    <div className="bg-red-300 text-red-600 p-3 rounded-md">Teve um error...</div>
  )
}

function MessageLoading () {
  return (
    <div className="bg-green-300 text-green-600 p-3 rounded-md">Carregando...</div>
  )
}
export function DateFilter() {
    const { data: availableYears, error: yearError, loading: yearLoading } = useFetch('/api/available-years/');
    const {selectedYear, setSelectetdYear, selectedMonth, setSelectedMonth} = useContext(SelectedDateContext)

    const { data: availableMonths, error: monthError, loading: monthLoading } = useFetch(`/api/available-months/?year=${selectedYear}`);

    if (yearError) {
        return <MessageError />;
    }
    if (yearLoading) {
        return <MessageLoading />;
    }

    return (
        <div>
            {/* Year Selectors */}
            <CardWrapper>
                <p className="mb-2">Selecione o Ano</p>
                <div className="flex gap-4">
                {availableYears?.years?.map((year) => (
                    <ToogleButton
                    key={year}
                    data-holder={year}
                    isActive={year === selectedYear}
                    handleClick={() => setSelectetdYear(year)}
                    >
                        {year}
                    </ToogleButton>
                ))}
                </div>
            </CardWrapper>
            {/* Month Selectors */}
            
            {monthError && <MessageError />}
            {monthLoading && <MessageLoading />}
            {!monthError && !monthLoading && (
                <CardWrapper>
                    <p className="mb-2">Selecione o Mês</p>
                    <div className="flex gap-4">
                        {availableMonths?.months?.map((month) => (
                            <ToogleButton
                                key={month}
                                data-holder={month}
                                isActive={month === selectedMonth}
                                handleClick={() => setSelectedMonth(month)}
                            >
                                {month}
                            </ToogleButton>
                        ))}
                    </div>
                </CardWrapper>
            )}

        </div>
  );
}