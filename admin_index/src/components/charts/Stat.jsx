
export function StatLabel ({children}) {
    return (
        <div className="px-2 py-1.5 bg-violet-200 rounded text-violet-800 uppercase font-semibold text-sm">{children}</div>
    )
}

export function Stat({title, month, amount, footerNote}) {
  return (
    <div className="border border-solid  border-gray-400 rounded-md shadow-md shadow-violet-400">
        <div className="p-6 flex flex-col gap-2">
            <div className="flex justify-between items-center">
                <p className="text-lg">{title}</p>
                { month && <StatLabel>{month}</StatLabel>}
            </div>
            <p className="font-bold text-2xl ">{amount}</p> 

        </div>
        <footer className="border-t font-medium text-green-600 border-gray-400 px-6 py-3">
            {footerNote}
        </footer>

    </div>
  )
}
