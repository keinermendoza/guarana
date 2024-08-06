from django.shortcuts import get_object_or_404
from django.urls import path, reverse_lazy
from unfold.contrib.forms.widgets import ArrayWidget, WYSIWYG_CLASSES
from django.http import JsonResponse
from django import forms
from unfold.admin import ModelAdmin


class WysiwygWidget(forms.Widget):
    template_name = "admin/forms/wysiwyg.html"

    class Media:
        css = {"all": ("unfold/forms/css/trix.css",)}
        js = ["js/admin.js"]


    def __init__(self, attrs=None) -> None:
        super().__init__(attrs)

        self.attrs.update(
            {
                "class": " ".join(WYSIWYG_CLASSES),
            }
        )


class RichTextEditorAdmin(ModelAdmin):
    """
    *form_required_fields: form.ModelForm with minimun required fields, example:
    
    class Post(model.Model):
        title = models.CharField(max_lenght=100)
        body = models.TextField()

    class PostForm(forms.ModelForm):
        class Meta:
            model = Post
            fields = ['title']

    
    *form: form.ModelForm must to include a WysiwygWidget field, and also and hidden input called 'disabled_inlines', example:
    
    class PostAdminForm(forms.ModelForm):
        disable_inlines = forms.CharField(widget=forms.HiddenInput, required=False)
        class Meta:
            model = Post
            fields = '__all__'
            widgets = {
                'body':WysiwygWidget
            }        
    
    *model_image_related: model.Model of related Image example:
    
    class PostImage(model.Model):
        post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images_post")
        image = models.ImageField(upload_to="posts_images")

    
    *form_related_image: form.ModelForm for Image related model example:
    
    class PostImageForm(forms.ModelForm):
        class Meta:
            model = PostImage
            fields = ["image"]


    *name_image_field: model.ImageField in Image model (default: 'image')
    *rel_image_to_model: model.ForeingKey field in Image to Primary Model (example: 'post') 


    *disable_inlines_on_delete_image: bool (default: True) 
    *disable_inlines_message: str (example: "Para usar esta seccion debe guardar")
   
    """
    change_form_template = "admin/change_form_trix_handle_images.html"
    disable_inlines_on_delete_image = True
    name_image_field = "image"

    
    def get_form(self, request, obj=None, **kwargs):
        """
        setup the minimal form for add_view
        this is necessary beacuse instance must to exist in database
        before be able to create related Image instances
        """
        if obj is None:
            kwargs['form'] = self.form_required_fields
        return super().get_form(request, obj, **kwargs)

    def add_view(self, request, form_url='', extra_context=None):
        """
        lives only the 'save and continue editing' button   
        """
        context = extra_context or {}
        context.update({
            "show_save": False,
            "show_save_and_add_another" : False
        })
        return super().add_view(request=request, form_url="", extra_context=context)
    
    def change_view(self, request, object_id, form_url="", extra_context=None):
        """
        adds the endpoints for handle upload/delete related images to context
        in the custom 'change_form_template' 
        this scripts are loadded by 'js/admin.js'
        """
        instance = self.model.objects.get(pk=object_id)
        extra_context = extra_context or {}
        extra_context.update({
            "urls_upload_delete_image": {
                "upload":reverse_lazy('admin:wysiwyg_upload_image', args=[object_id]),
                "delete":reverse_lazy('admin:wysiwyg_delete_image', args=[object_id, 0]),
            }
        })
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )
            
    def get_urls(self):
        """
        adds customs urls and views for handeling upload/delete related images
        """
        urls = super().get_urls()
        my_urls = [
            path("<int:pk>/wysiwyg_upload_image/", self.admin_site.admin_view(self.wysiwyg_upload_image), name='wysiwyg_upload_image'),
            path("<int:pk>/wysiwyg_delete_image/<int:image_id>/", self.admin_site.admin_view(self.wysiwyg_delete_image), name='wysiwyg_delete_image'),
        ]
        return my_urls + urls


    def wysiwyg_upload_image(self, request, *args, **kwargs):
        """
        custom view for handeling upload realted images
        """
        instance = get_object_or_404(self.model, pk=kwargs.get('pk'))
        form = self.form_related_image(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            setattr(image, self.rel_image_to_model, instance)
            image.save()
            
            return  JsonResponse({"url": getattr(image, self.name_image_field).url, "id":image.id}, status=200)
        return JsonResponse({"errors":form.errors.as_json()}, status=400)
    
    def wysiwyg_delete_image(self, request, *args, **kwargs):
        """
        custom view for handeling delete realted images
        """
        instance = get_object_or_404(self.model, pk=kwargs.get('pk'))
        related_field_name = getattr(self, 'rel_image_to_model')
        
        # checking the image instance exists and belongs to the primary instance
        image = get_object_or_404(
            self.model_image_related,
            pk=kwargs.get('image_id'),
             **{related_field_name: instance}
        )
        image.delete()

        # change input value 
        if self.disable_inlines_on_delete_image:
            return JsonResponse({'disable_inlines': self.disable_inlines_message}, status=200)
        return JsonResponse({'message': 'Eliminado con exito'}, status=200)
    
    def get_inlines(self, request, obj):
        """
        returning and empty list for avoid evaluate the inlines 
        when disable_inlines_on_delete_image is True
        or when is in the add_view
        """
        if request.POST.get('disable_inlines') == 'true' or obj is None:
            return []
        return self.inlines
    
class BaseWysiwygCustomForm(forms.ModelForm):
    disable_inlines = forms.CharField(widget=forms.HiddenInput, required=False)
    class Meta:
        fields = '__all__'
