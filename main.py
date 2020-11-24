from wtforms import Form, FloatField, validators
from flask import Flask, render_template, request
from bungee import any_bungee_solver

#array (k, l, m, c_1, c_2): All the arguments needed for modeling the jump, see bungee() for details!

class InputForm(Form):
    starting_height = FloatField(label='(m)', default=80,
                validators=[validators.InputRequired()])
    time = FloatField(label='(s)', default=20,
                validators=[validators.InputRequired()])
    k = FloatField(label='(N/m)', default=150,
                validators=[validators.InputRequired()])
    bungee_length = FloatField(label='(m)', default=50,
                validators=[validators.InputRequired()])
    jumper_mass = FloatField(label='(kg)', default=100,
                validators=[validators.InputRequired()])

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():    
    form = InputForm(request.form)
    try: 
        int(form.starting_height.data)
        int(form.time.data)
        int(form.k.data)
        int(form.bungee_length.data)
        int(form.jumper_mass.data)
        if request.method == 'POST' and form.validate():
            bungee_arguments = (form.k.data, form.bungee_length.data, form.jumper_mass.data, 1,1)
            result, out= any_bungee_solver([form.starting_height.data, 0],
                                        form.time.data,
                                        bungee_arguments)
        else:
            result = None
            out = None
        return render_template('bungee.html', form=form, result=result, out=out)
    except:
        result = None
        out = None
        return render_template('bungee.html', form=form, result=result, out=out)
