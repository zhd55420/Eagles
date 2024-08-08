from django import forms

class HostnameUpdateForm(forms.Form):
    single_ip_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    single_new_hostname = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    bulk_input = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    zabbix_server = forms.ChoiceField(
        choices=[],  # 这里不需要默认值，动态生成
        widget=forms.Select(attrs={'class': 'form-control'})
    )
