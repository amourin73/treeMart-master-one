from django import forms

from trees.models import Tree


class TreeForm(forms.ModelForm):
    class Meta:
        model = Tree
        fields = '__all__'
