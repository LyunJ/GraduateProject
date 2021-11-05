from django import forms

class LabelingForm(forms.Form):
    label_radio = forms.ChoiceField(choices=[("one",1), ("two",2), ("three",3)],widget=forms.RadioSelect())

    
    def __init__(self,labels=None):
        super(forms.Form,self).__init__()
        self.fields['label_radio'] = forms.ChoiceField(choices=[(x['label'],x['label']) for x in labels],widget=forms.RadioSelect())
