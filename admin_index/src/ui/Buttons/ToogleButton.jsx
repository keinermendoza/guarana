export function ToogleButton ({children, handleClick, isActive}) {
    return (
        <button 
            onClick={handleClick}
            disabled={isActive}
            className={`${isActive ? 'bg-blue-400 text-gray-700' : 'bg-violet-700 text-white shadow-xl shadow-violet-400 hover:scale-110 '} rounded px-4 py-1.5 text-lg font-medium transition-transform duration-250`}>
            {children}
        </button>
    )
}