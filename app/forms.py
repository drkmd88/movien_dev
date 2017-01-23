from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, BooleanField, HiddenField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length
from app.models import User, Movie_gr


class LoginForm(FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    use_openid = BooleanField('use_openid', default=False)
    openid = StringField('openid')
    remember_me = BooleanField('remember_me', default=False)


class SignupForm(FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    repassword = PasswordField('repassword', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])


    def validate(self):
        validation = True
        if not FlaskForm.validate(self):
            validation = False
        if not self.nickname.data.find(' ') == -1:
            self.nickname.errors.append('Nickname can not contain space (\' \')')
            validation = False
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if not (user is None):
            self.nickname.errors.append('Nickname exists, please change another one')
            validation = False
        if self.email.data.find('@') == -1:
            self.email.errors.append('Please use a valid email address')
            validation = False
        if not self.password.data == self.repassword.data:
            self.repassword.errors.append('Passwords are not match')
            validation = False
        return validation



class EditForm(FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])


    def __init__(self, original_nickname, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname


    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True


class PostForm(FlaskForm):
    post = TextAreaField('post', validators=[DataRequired()])
    private = SelectField('private', choices=[('0', 'Public'), ('1', 'Myself')])


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])


class RecommandForm(FlaskForm):
    avgrating = BooleanField(default="checked")
    genres = SelectField('genres', choices=[('none', 'None'), ('comedy', 'Comedy'), ('thriller', 'Thriller'), ('action', 'Action'), ('romance','Romance'), ('adventure', 'Adventure'), ('crime', 'Crime'), ('fantasy', 'Fantasy'), ('animation', 'Animation'), ('scifi', 'Scifi')], default='none')
    adv = BooleanField()
    prod = BooleanField()
    budget = BooleanField()
    profit = BooleanField()
    year = SelectField('year', choices=[("none", "None"), ('lt1990', 'Before 1990'), ('lt2000', '1990-1999'), ('lt2010', '2000-2010'), ('gt2010', 'After 2010')], default='none')
