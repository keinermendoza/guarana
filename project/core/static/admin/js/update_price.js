document.addEventListener('update-price', (e) => {
        const productSelect = e.target
        const selectedOption = productSelect.options[productSelect.selectedIndex];
        const precioInput = productSelect.closest('tr').querySelector('[data-label="Precio"] input')
        const precio = selectedOption.dataset.precio
        precioInput.value = precio || 0

        const calculate = new Event('calculate')
        document.dispatchEvent(calculate)
        
})
