document.addEventListener("DOMContentLoaded", () => {
    hideExtraButtonsOnSmallScreens()
    window.addEventListener('resize', hideExtraButtonsOnSmallScreens)

    createAndAddCopyValueButtonFromTotal() // only one button
    
    const [header, fieldset]  = getPriceHeaderAndFieldset()
    addEventHeaderTooglePriceVisibility(header, fieldset)
    header.click()
})

// return the fieldset header in which are the price inputs 
const getPriceHeaderAndFieldset = () => {
    const td = document.querySelector('[data-label="Precio"]')
    const fieldset = td.closest('fieldset')
    const header = fieldset.querySelector('h2')
    return [header, fieldset]
}

// toggle visibility of price for product item inline
function addEventHeaderTooglePriceVisibility(header, fieldset) {
    header.classList.add('cursor-pointer')
    header.innerText = header.innerText + " (faza click para mostrar os preços)" 
    header.onclick = () => {
        fieldset.querySelectorAll('[data-label="Precio"]').forEach((priceTd) => {
            priceTd.classList.toggle('hidden')
            priceTd.querySelector('input').classList.toggle('hidden')
        })
    }
}
     
// copies value from total to first item
function createAndAddCopyValueButtonFromTotal() {
    const button = helperCreateCopyButton()
    helperAddCopyButtonToPage(button)
}

const helperCreateCopyButton = () => {
    const button = document.createElement('button');
    button.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
    <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75" />
  </svg>`;
    button.className="related-widget-wrapper-link change-related bg-white border cursor-pointer flex items-center h-9.5 justify-center ml-2 rounded shadow-sm shrink-0 text-gray-400 text-sm w-9.5 hover:text-gray-700 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-500 dark:hover:text-gray-200";
    button.type = "button";
    button.style.padding = "8px";
    return button
}

const helperAddCopyButtonToPage = (button) => {
    const total_input = document.getElementById("id_total");
    const container = document.querySelector('[data-label="Monto"]')

    // create container with custom styles and reorder elements
    const newContainer = document.createElement('div')
    newContainer.className = "flex gap-1 w-full"
    const input = container.querySelector('input')
    container.insertBefore(newContainer, container.children[0]);
    newContainer.appendChild(input)
    newContainer.appendChild(button)

    button.addEventListener("click", () => {
        input.value = total_input.value
    })
}



// get elements for toggle visibilite and calls executeHideExtraButtonsOnSmallScreens
function hideExtraButtonsOnSmallScreens() {
    const metodosPago = document.querySelectorAll('[data-model-ref="Metodo de Pago"]')
    const producto = document.querySelectorAll('[data-model-ref="producto"]')
    
    executeHideExtraButtonsOnSmallScreens(metodosPago)
    executeHideExtraButtonsOnSmallScreens(producto)

}

// toggles visibility of extra buttons for inline items
const executeHideExtraButtonsOnSmallScreens = (div) => {
    if(window.innerWidth < 800) {
        div.forEach((metodoPago) => {
            metodoPago.querySelectorAll('a').forEach((anchorTag) => {
                anchorTag.classList.add('hidden')
            })
        })
    } else {
        div.forEach((metodoPago) => {
            metodoPago.querySelectorAll('a').forEach((anchorTag) => {
                anchorTag.classList.remove('hidden')
            })
        })
    }
}