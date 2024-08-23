document.addEventListener('update-price', (e) => {
        const productSelect = e.target
        const selectedOption = productSelect.options[productSelect.selectedIndex];
        const rowElement = productSelect.closest('tr')
        const precioInput = rowElement.querySelector('[data-label="Precio"] input')
        const precio = selectedOption.dataset.precio
        precioInput.value = precio || 0

        rowElement.querySelector('[data-label="Cantidad"] input').focus()
        const calculate = new Event('calculate')
        document.dispatchEvent(calculate)



        
})
