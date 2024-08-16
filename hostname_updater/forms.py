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


class ResourceGroupForm(forms.Form):
    action = forms.ChoiceField(choices=[('add', 'Add'), ('delete', 'Delete')], label='Action')
    group_name = forms.CharField(max_length=100, label='Resource Group Name')

class PRTForm(forms.Form):
    action = forms.ChoiceField(choices=[('add', 'Add'), ('delete', 'Delete')], label='Action')
    group_name = forms.ChoiceField(label='Resource Group Name')
    prt_value = forms.CharField(max_length=100, label='PRT Server ID')

    def __init__(self, *args, **kwargs):
        resource_groups = kwargs.pop('resource_groups', [])
        super().__init__(*args, **kwargs)
        self.fields['group_name'].choices = [(name, name) for name in resource_groups]

class TrackerForm(forms.Form):
    action = forms.ChoiceField(choices=[('add', 'Add'), ('delete', 'Delete')], label='Action')
    group_name = forms.ChoiceField(label='Resource Group Name')
    tracker_value = forms.CharField(max_length=100, label='Tracker Server ID')

    def __init__(self, *args, **kwargs):
        resource_groups = kwargs.pop('resource_groups', [])
        super().__init__(*args, **kwargs)
        self.fields['group_name'].choices = [(name, name) for name in resource_groups]

