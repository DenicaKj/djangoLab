from django import forms
from .models import *

class BlogForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(BlogForm, self).__init__(*args, **kwargs)
		for field in self.visible_fields():
			field.field.widget.attrs["class"] = "form-control"
	class Meta:
		model = Blog
		exclude = ("user",)