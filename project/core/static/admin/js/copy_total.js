document.addEventListener("DOMContentLoaded", () =>{
    const button = document.createElement('button');
    button.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
    <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75" />
  </svg>`;
    button.className="related-widget-wrapper-link change-related bg-white border cursor-pointer flex items-center h-9.5 justify-center ml-2 rounded shadow-sm shrink-0 text-gray-400 text-sm w-9.5 hover:text-gray-700 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-500 dark:hover:text-gray-200";
    button.type = "button";
    button.style.padding = "8px";

    const total_input = document.getElementById("id_total");

    document.querySelectorAll('[data-label="Monto"]').forEach((td) => {
        const clonedButton = button.cloneNode(true)
        td.appendChild(clonedButton);

        clonedButton.addEventListener("click", () => {
            const input = td.querySelector('input')
            input.value = total_input.value
        })    
        
    })
})