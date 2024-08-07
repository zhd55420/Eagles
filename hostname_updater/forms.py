from django import forms

class HostnameUpdateForm(forms.Form):
    single_ip_address = forms.GenericIPAddressField(label="Single IP Address", required=False)
    single_new_hostname = forms.CharField(max_length=100, label="Single New Hostname", required=False)
    bulk_input = forms.CharField(widget=forms.Textarea, label="Bulk Input (Format: IP, New Hostname)", required=False)
