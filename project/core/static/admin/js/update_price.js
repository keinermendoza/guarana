document.addEventListener('click', (e) => {
    if(e.target.dataset.producto == 'update-price') {
        const productSelect = e.target
        const selectedOption = productSelect.options[productSelect.selectedIndex];
        const price = productSelect.closest('tr').querySelector('[data-label="Precio"] input')
        price.value = selectedOption.dataset.precio
        
    }
})
