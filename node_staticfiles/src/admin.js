import Trix from "trix"
import axios from 'axios'

const myAxios = axios.create({
    baseURL: process.env.API_ENDPOINT, // Ajusta esto según tu configuración
    withCredentials: true, // Esto asegura que se envíen las cookies con cada solicitud
    xsrfCookieName: 'csrftoken',
    xsrfHeaderName: "X-CSRFTOKEN",
    headers: {
        'Content-Type': 'multipart/form-data',
      }

});

// SETTING ENDPOINT FOR UPLOAD/DELETE IMAGES
let upload_enpoint;
let delete_enponit;
let id_principal_form;
document.addEventListener('DOMContentLoaded', () => {
    // const endpoint =  JSON.parse(document.querySelector('#curso_endpoint').textContent)
    // /admin/core/curso/my_view/
    const imageRemovedField = document.getElementById('id_image_removed');
    const enpoints =  JSON.parse(document.querySelector('#urls_upload_delete_image').textContent)
    upload_enpoint = enpoints.upload
    delete_enponit = (enpoints.delete).replace(/0\/$/, "")
    id_principal_form = enpoints.principal_form
})

    

// MAIN UPLOAD IMAGE FUNCTION
const uploadFileAttachment = async (attachment) => {
  const setProgress = (progress) => attachment.setUploadProgress(progress);
  const setAttributes = (attributes) => attachment.setAttributes(attributes);

  const response = await uploadFile(attachment.file, setProgress);
  if (response) {
    setAttributes({ url: response.url, href: response.url, id:response.id });
  }
};

// UPLOAD IMAGE HANDELER
const uploadFile = async (file, progressCallback) => {
    const formData = new FormData();
    formData.append('image', file);
    try {
        const resp = await myAxios.post(upload_enpoint, formData, {
            onUploadProgress: (event) => {
                const progress = (event.loaded / event.total) * 100;
                progressCallback(progress);
            }
        });
        return resp.data;
    } catch (error) {
        console.error("Error uploading file:", error);
    }
    return null;
};

    
// CALL MAIN UPLOAD IMAGE FUNCTION
window.addEventListener("trix-attachment-add", (event) => {
    if (event.attachment.file) {
    uploadFileAttachment(event.attachment);
    }
});

// DISABLING THE INLINES
// this is usefull in the image related model in in inlines for avoid inconsistencies in save
function disable_inlines(message) {
    // create mask with custom message
    const div = document.createElement("div")
        div.innerHTML = message
        div.style = "padding:20px; text-aling:center; font-size:1.5rem; display:grid; place-content: center; position:absolute;top:0;left:0;width:100%; height:100%; border-radius: 20px; background-color:rgba(255,255,255,0.6); backdrop-filter: blur(8px);"
        document.querySelectorAll('.inline-group').forEach(inline => {
            inline.style = "position:relative;"
            inline.appendChild(div)
            // disabiling checkboxes for delete
            inline.querySelectorAll("input[type=checkbox]").forEach(checkbox => {
                checkbox.disabled = true;
            })
        })
    // create input for avoid save inline forms in backend
document.getElementById("id_disable_inlines").value = true;
}

// DELETE IMAGE FUNCTION
window.addEventListener("trix-attachment-remove", async(event) => {
    const image_id = event.attachment.attachment.attributes.values.id
    try {
        const resp = await myAxios.delete(delete_enponit + image_id)
        if (resp.data.disable_inlines) {
            disable_inlines(resp.data.disable_inlines)
        }
    } catch (error) {
        console.error("Error deleting file:", error);
    }
})

// TOOLBAR CONFIG CONFIG 
Trix.config.blockAttributes.heading2 = {
    tagName: "h2",
    breakOnReturn: true,
    group: false,
    terminal: true
}

Trix.config.blockAttributes.heading3 = {
    tagName: "h3",
    breakOnReturn: true,
    group: false,
    terminal: true
}

Trix.config.blockAttributes.heading4 = {
    tagName: "h4",
    breakOnReturn: true,
    group: false,
    terminal: true
}

Trix.config.blockAttributes.p = {
    tagName: "p",
    breakOnReturn: true,
    terminal: true
}

Trix.config.textAttributes.underlined = {
    tagName: "u",
    inheritable: true,
    parser(element) {
        const style = window.getComputedStyle(element);
        return style.textDecoration === "underline";
    },
}

// LOADING TOOLBAR
document.addEventListener("trix-before-initialize", () => {
    Trix.config.toolbar.getDefaultHTML = () => document.getElementById("custom-trix-toolbar").innerHTML
})