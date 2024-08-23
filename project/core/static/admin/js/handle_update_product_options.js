document.addEventListener('DOMContentLoaded', () => {
    const productSelect = document.querySelector('[data-trigger="handle_update_product_options"]')
    const sacoId = productSelect.options[productSelect.selectedIndex].value;
    
    if (!sacoId) {
        handleUpdate(sacoId)
    }
})

document.addEventListener('update_product_inline_options', (e) => {
    const productSelect = e.target 
    const sacoId = productSelect.options[productSelect.selectedIndex].value;
    handleUpdate(sacoId)
})

// if there is an "saco" selected try to load data 
// if there is not id or is not valid populates product select with empty option
// if success populates select with "tipo_guarana" related "products"  
async function handleUpdate(sacoId) {
    const produccionProductosSelects = document.querySelectorAll('[data-target="recive_update_product_options"]')
    if (sacoId === "") {
        populateSelect(produccionProductosSelects)
    } else {
        const options = await updateProductInlineOptions(sacoId)
        if (options) {
            populateSelect(produccionProductosSelects, options)
        } else {
            populateSelect(produccionProductosSelects)
        }
    }
}

async function updateProductInlineOptions(sacoId) {
    try {
        const resp = await fetch('/admin/core/saco/update_product_options/?saco=' + sacoId)
        const options = await resp.text()
        return options
    } catch(err) {
        return null
    }
}

function populateSelect(selectCollection, options=null) {
    selectCollection.forEach((select) => {
        if(options) {
            select.innerHTML = options
        } else {
            select.innerHTML =  '<option value="" selected="">Precisa selecionar um saco</option>'
        }
    })
}