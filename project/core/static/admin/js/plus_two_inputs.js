function updateTotal(element) {
    const formRow = element.closest('.inline-related');
    const input1 = parseInt(formRow.querySelector('.input1').value) || 0;
    const input2 = parseInt(formRow.querySelector('.input2').value) || 0;
    const total = input1 + input2;
    formRow.querySelector('[data-peso="peso_inicial"]').value = total;
}