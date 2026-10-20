from django.shortcuts import redirect, render
from .forms import ContactForm

def contact(request):
    initial = {"subject": "personalization"} if request.GET.get("asunto") == "personalizacion" else None
    form = ContactForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        form.save()
        request.session["contact_message_saved"] = True
        return redirect("contact:contact")
    contact_success = request.session.pop("contact_message_saved", False)
    return render(request, "contact/contact.html", {"form": form, "contact_success": contact_success})
