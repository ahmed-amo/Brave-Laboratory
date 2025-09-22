from django.contrib.auth.models import Group


from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def is_client(user):
    client_group = Group.objects.get(name='client')
    return client_group in user.groups.all()

def is_nurse(user):
    nurse_group = Group.objects.get(name='nurse')
    return nurse_group in user.groups.all()

def is_receptionist(user):
    receptionist_group = Group.objects.get(name='receptionist')
    return receptionist_group in user.groups.all()

def is_auditor(user):
    auditor_group = Group.objects.get(name='auditor')
    return auditor_group in user.groups.all()

def is_admin_user(user):
    admin_user_group = Group.objects.get(name='admin_user')
    return admin_user_group in user.groups.all()




