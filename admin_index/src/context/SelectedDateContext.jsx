import { useState, createContext, useContext } from "react";

export const SelectedDateContext = createContext({})

export default function SelectedDateContextProvider ({children}) {
    const [selectedYear, setSelectetdYear] = useState(new Date().getFullYear());
    const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
    
    return (
        <SelectedDateContext.Provider value={{selectedYear, setSelectetdYear, selectedMonth, setSelectedMonth}}>
            {children}
        </SelectedDateContext.Provider>
    )
}