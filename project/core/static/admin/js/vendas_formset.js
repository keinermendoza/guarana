const CALCULATOR_SVG =`<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 15.75V18m-7.5-6.75h.008v.008H8.25v-.008Zm0 2.25h.008v.008H8.25V13.5Zm0 2.25h.008v.008H8.25v-.008Zm0 2.25h.008v.008H8.25V18Zm2.498-6.75h.007v.008h-.007v-.008Zm0 2.25h.007v.008h-.007V13.5Zm0 2.25h.007v.008h-.007v-.008Zm0 2.25h.007v.008h-.007V18Zm2.504-6.75h.008v.008h-.008v-.008Zm0 2.25h.008v.008h-.008V13.5Zm0 2.25h.008v.008h-.008v-.008Zm0 2.25h.008v.008h-.008V18Zm2.498-6.75h.008v.008h-.008v-.008Zm0 2.25h.008v.008h-.008V13.5ZM8.25 6h7.5v2.25h-7.5V6ZM12 2.25c-1.892 0-3.758.11-5.593.322C5.307 2.7 4.5 3.65 4.5 4.757V19.5a2.25 2.25 0 0 0 2.25 2.25h10.5a2.25 2.25 0 0 0 2.25-2.25V4.757c0-1.108-.806-2.057-1.907-2.185A48.507 48.507 0 0 0 12 2.25Z" />
</svg>`

const COPY_SVG = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
    <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75" />
  </svg>`

document.addEventListener("DOMContentLoaded", () => {
    const calculateTotalButton = helperCreateButton(CALCULATOR_SVG)
    helperAddCalculateButton(calculateTotalButton)
    
    const copyTotalButton = helperCreateButton(COPY_SVG)
    helperAddAllowEditPriceButton(copyTotalButton)


})

// copy the total for first metodo monto 
document.addEventListener('reload_copy', () => {
    const container = document.querySelector('[data-label="Monto"]')
    const total_input = document.getElementById("id_total");
    const input = container.querySelector('input')
    input.value = total_input.value
})
     

const helperCreateButton = (svg) => {
    const button = document.createElement('button');
    button.innerHTML = svg;
    button.className="related-widget-wrapper-link change-related bg-white border cursor-pointer flex items-center h-9.5 justify-center ml-2 rounded shadow-sm shrink-0 text-gray-400 text-sm w-9.5 hover:text-gray-700 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-500 dark:hover:text-gray-200";
    button.type = "button";
    button.style.padding = "8px";
    return button
}

const helperAddCalculateButton = (button) => {
    const total_input = document.getElementById("id_total");
    createContainerAndReorderItems(total_input.parentElement, button)

    const calculate = () => {
        let totalMontoItems = 0
        let totalMontoVidros = 0

        // plus total items
        document.querySelectorAll('[data-target="item_precio_calculate_total"]').forEach((precioInput) => {
            const cantidadInput = precioInput.parentElement.parentElement.querySelector('[data-target="item_cantidad_calculate_total"]')
            const totalItem = cantidadInput.value * precioInput.value
            totalMontoItems += totalItem ? totalItem : 0
        })
        // substarct total vidros
        document.querySelectorAll('[data-target="compravidros_precio_calculate_total"]').forEach((precioInput) => {
            const cantidadInput = precioInput.parentElement.parentElement.querySelector('[data-target="compravidros_cantidad_calculate_total"]')
            const totalVidrios = cantidadInput.value * precioInput.value
            totalMontoVidros += totalVidrios ? totalVidrios : 0
        })
        
        total_input.value = totalMontoItems - totalMontoVidros 
        const reload = new Event('reload_copy')
        document.dispatchEvent(reload)
    }

    document.addEventListener('calculate', calculate)
    button.addEventListener('click', calculate)
}

const helperAddAllowEditPriceButton = (button) => {
    const container = document.querySelector('.main-form__total-price')
    button.addEventListener("click", () => {
        document.querySelectorAll('[data-target="item_precio_calculate_total"]').forEach((inputPrice) => {
            inputPrice.classList.toggle('pointer-events-none')
        })
        button.classList.toggle('bg-primary-600')
    })
    console.log(container)
    container.appendChild(button)
}

const createContainerAndReorderItems = (acutalContainer, button) => {
    const newContainer = document.createElement('div')
    newContainer.className = "main-form__total-price flex gap-1 w-full"
    const input = acutalContainer.querySelector('input')
    acutalContainer.insertBefore(newContainer, acutalContainer.children[0]);
    newContainer.appendChild(input)
    newContainer.appendChild(button)
}