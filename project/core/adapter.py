from django.contrib.sites.models import Site
from  allauth.account.adapter import DefaultAccountAdapter
from django.template.loader import render_to_string
from .task import  async_render_and_send

class AccountAdapterEmailAsync(DefaultAccountAdapter):
    """
    Reimplementation of send mail for use celery worker 
    see original code in https://github.com/pennersr/django-allauth/blob/main/allauth/account/adapter.py
    """
    def send_mail(self, template_prefix, email, context):
        ctx = {
            "email": email,
            "current_site": Site.objects.get_current().id, # Site instance will be recover using the id
            "from_email": self.get_from_email(), # this was originally called from render_mail
        }
        
        # the request obj is  not serializable
        if "request" in context:
            context.pop("request")

        # user instance will be recover using the id
        if "user" in context:
            context.update({
                "user": context["user"].id    
            })

        ctx.update(context)

        # this was originally called from render_mail
        subject = render_to_string("{0}_subject.txt".format(template_prefix), ctx)
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)
        ctx.update({"subject": subject})

        # calling 
        async_render_and_send.delay(template_prefix, email, ctx)
      