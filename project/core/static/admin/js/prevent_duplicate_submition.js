document.addEventListener("DOMContentLoaded", () => {
    let submitions = {
        first: true
    }
    const btnSave = document.querySelector('[name="_save"]')
    if (btnSave) {
        btnSave.onclick = function(e) {
            blockSubmition(submitions, this)
        }
    }

    const btnSaveContinue = document.querySelector('[name="_continue"]')
    if (btnSaveContinue) {
        btnSaveContinue.onclick = function(e) {
            blockSubmition(submitions, this)
        }
    }

    const btnSaveAdd = document.querySelector('[name="_addanother"]')
    if (btnSaveAdd) {
        btnSaveAdd.onclick = function(e) {
            blockSubmition(submitions, this)
        }
    }

})

function blockSubmition(objBool, button) {
    if (objBool.first) {
        objBool.first = false
    } else {
        button.disabled = true
    }
}