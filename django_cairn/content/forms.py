from django import forms

from django_cairn.content.models import DjangoTag


class SelectedDjangoTagForm(forms.Form):
    selected_versions = forms.ModelMultipleChoiceField(
        queryset=DjangoTag.objects.order_by("-version")
    )
