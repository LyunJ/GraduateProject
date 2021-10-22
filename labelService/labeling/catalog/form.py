from django import forms

class LabelingForm(forms.Form):
    label_radio = forms.ChoiceField(choices=[("one",1), ("two",2), ("three",3)],widget=forms.RadioSelect())

    
    def __init__(self,label1=None,label2=None,label3=None):
        super(forms.Form,self).__init__()
        self.fields['label_radio'] = forms.ChoiceField(choices=[(label1,label1), (label2,label2), (label3,label3)],widget=forms.RadioSelect())
