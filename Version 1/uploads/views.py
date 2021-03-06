from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from uploads.auth_utils import *
from uploads.forms import *
from uploads.models import *


#tempalte d'accueil
def welcome(request):
    
    return render(request, 'uploads/welcome.html', locals())

#dashboard
def dashboard(request):
    if is_student(request.user):
        if request.method == "POST":
            form = themeForm(request.POST, request.FILES)
            if form.is_valid():
                student = Student.objects.get(user = request.user)
                student.theme = form.cleaned_data["theme"]
                student.save()
        else:
            form = themeForm()
        
        return render(request, 'students/dashboard.html', locals())
    
    elif is_teacher(request.user):
        if request.method == "POST":
            form = themeForm(request.POST, request.FILES)
            if form.is_valid():
                teacher = Teacher.objects.get(user = request.user)
                teacher.theme = form.cleaned_data["theme"]
                teacher.save()
        else:
            form = themeForm()
        return render(request, 'teachers/dashboard.html', locals())
    else:
        return redirect('uploads:connexion')

#upload pour un tag
def upload(request, tagId):
    if is_student(request.user):
        form = UploadForm()
        tag = Tag.objects.get(id=tagId)
    
        return render(request, 'students/upload.html', locals())
    else:
        return redirect('uploads:connexion')

#enregistrement de l'image pour un tag donné
def sauver(request, tagId):
    if is_student(request.user):
        if request.method == "POST":
            form = UploadForm(request.POST, request.FILES)
            
            if form.is_valid():
                    image = Picture()
                    student = Student.objects.get(user=request.user)
                    image.uploader = student
                    image.image = form.cleaned_data["image"]
                    tagValue = Tag.objects.get(id=tagId)
                    image.tag = tagValue
                    image.description = form.cleaned_data["description"]
                    image.contraste = form.cleaned_data["contraste"]
                    image.saturation = form.cleaned_data["saturation"]
                    image.luminosite = form.cleaned_data["luminosite"]
                    image.save()
                    
                    return redirect('uploads:uploaded')
            else:
                
                return redirect('uploads:upload', tagId)
    else:
        return redirect('uploads:connexion')

#images uploadées
def uploaded(request):
    if is_student(request.user):
        student = Student.objects.get(user = request.user)
        images = Picture.objects.all().filter(uploader = student).order_by("date")
        
        return render(request, 'students/images_index.html', locals())
    elif is_teacher(request.user):
        prof = Teacher.objects.get(user=request.user)
        tags = Tag.objects.filter(uploader=prof)
        
        return render(request, 'teachers/tags_index.html', locals())
    else:
        return redirect('uploads:connexion')

#détail d'une image
def detail_uploaded(request, imageId):
    if is_student(request.user):
        image = Picture.objects.get(id=imageId)
        tag = image.tag.value
        form = ModifyForm()
        
        return render(request, 'students/images_detail.html', locals())
        
    elif is_teacher(request.user):
        image = Picture.objects.get(id=imageId)
        tag = image.tag.value
        form = ModifyForm()
        
        return render(request, 'teachers/images_detail.html', locals())
    else:
        return redirect('uploads:connexion')
        
    
#supprimer image
def delete(request, imageId):
    if is_student(request.user):
        if request.method == "POST":
            image = Picture.objects.get(id=imageId)
            image.delete()
            
        return redirect('uploads:uploaded')
    else:
        return redirect('uploads:connexion')
        

#modifier image
def modify(request, imageId):
    if is_student(request.user):
        image = Picture.objects.get(id=imageId)
        if request.method == "POST":
            form = ModifyForm(request.POST, request.FILES)
            
            if form.is_valid():
                image.description = form.cleaned_data["description"]
                image.contraste = form.cleaned_data["contraste"]
                image.saturation = form.cleaned_data["saturation"]
                image.luminosite = form.cleaned_data["luminosite"]
                image.save()
                
        return redirect('uploads:uploaded')
    else:
        return redirect('uploads:connexion')
        
            
#authentification
def connexion(request):
    if request.user.is_authenticated():
        return redirect('uploads:dashboard')
        
    erreur = False
    if request.method == "POST":
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            
            if user:
                login(request, user)
                
                return redirect('uploads:dashboard')
            
            else:
                erreur = True
    else:
        form = LoginForm()
        
    return render(request, "uploads/login.html", locals())
#authentification    
def deconnexion(request):
    logout(request)
    
    return redirect('uploads:connexion')
    
#authentification    
def register(request):
    if request.method == "POST":
        registerform = RegisterForm(data=request.POST)
        
        if registerform.is_valid():
            username = registerform.cleaned_data["username"]
            password = registerform.cleaned_data["password"]
            mail = registerform.cleaned_data["mail"]
            
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                account_model = None # Modèle à instancier pour créer le compte
                
                if registerform.cleaned_data["account_type"] == "student":
                    account_model = Student # Le modèle à utiliser est Student
                    group_name = "students"
                    
                elif registerform.cleaned_data["account_type"] == "teacher":
                    account_model = Teacher # Le modèle à utiliser est Teacher
                    group_name = "teachers"
                    
                user = User.objects.create_user(username, mail, password)
                try:
                    group = Group.objects.get(name=group_name)
                except:
                    group = Group.objects.create(name=group_name)
                
                user.groups.add(group)
                user.save()
                    
                account = account_model() # Instanciation du modèle
                account.user = user # Liaison au compte user
                account.save()
                
                return redirect('uploads:connexion')
            except Exception as e:
                return HttpResponse("Erreur non gérée : {}".format(str(e)))

    else:
        registerform = RegisterForm()
        
    return render(request, "uploads/register.html", {'registerform' : registerform})

#index de tags
def tags_index(request):
    if is_student(request.user):
        eleve = Student.objects.get(user=request.user)
        classes = eleve.classes.all()
        tags = []
        for classe in classes:
            tags += Tag.objects.filter(classes=classe)
        return render(request, "students/tags_index.html", locals())
    
    elif is_teacher(request.user):
        prof = Teacher.objects.get(user=request.user)
        classes = Classe.objects.filter(teacher=prof)
        form = tagForm()
        form.fields['classes'].queryset = Classe.objects.filter(teacher=prof)
        return render(request, "teachers/tags_creator.html", locals())
    
    else:
        return redirect('uploads:connexion')
        

#création tag
def create(request):
    if is_teacher(request.user):
        if request.method == "POST":
            form = tagForm(request.POST, request.FILES)
            try:
                tag = Tag.objects.get(value=form.cleaned_data["value"])
            except:    
                if form.is_valid():
                    prof = Teacher.objects.get(user=request.user)
                    tag = Tag()
                    tag.uploader = prof
                    tag.value = form.cleaned_data["value"]
                    tag.consigne = form.cleaned_data["consigne"]
                    tag.consigneImg = form.cleaned_data["consigneImg"]
                    tag.reponse = form.cleaned_data["reponse"]
                    tag.reponseImg = form.cleaned_data["reponseImg"]
                    tag.save()
                    
                    for classesName in form.cleaned_data['classes']:
                        classe = Classe.objects.get(name=classesName)
                        tag.classes.add(classe)
    
                    tag.save()
                    
        return redirect ('uploads:tags_index')
    else:
        return redirect('uploads:connexion')
        
def classes_index(request):
    if is_teacher(request.user):
        prof = Teacher.objects.get(user = request.user)
        classes = Classe.objects.filter(teacher = prof)
        form = classeForm()

        return render(request, "teachers/classes_index.html", locals())
    
    elif is_student(request.user):
        student = Student.objects.get(user = request.user)
        classes = student.classes.all()
        allClasses = Classe.objects.all()
        
        return render(request, "students/classes_index.html", locals())
    
    else:
        return redirect('uploads:connexion')

def create_classe(request):
    if is_teacher(request.user):
        if request.method == "POST":
            form = classeForm(request.POST, request.FILES)
            if form.is_valid():
                groupName = form.cleaned_data["name"]
                prof = Teacher.objects.get(user = request.user)
                try:
                    classe = Classe.objects.get(name=groupName)
                except:
                    classe = Classe()
                    classe.name = groupName
                    classe.teacher = prof
                    classe.branche = form.cleaned_data["branche"]
                    classe.save()
                
        return redirect('uploads:classes_index')
    else:
        return redirect('uploads:connexion')
        

def classes_detail(request, classeId):
    classe = Classe.objects.get(id=classeId)
    eleves = Student.objects.filter(classes=classe).order_by("user")
    prof = classe.teacher
    allEleves = Student.objects.exclude(classes=classe)
    
    if is_teacher(request.user):
        if Teacher.objects.get(user = request.user) == classe.teacher:
            return render(request, "teachers/classes_detail.html", locals())
        else:
            return render(request, "teachers/classes_detail_2.html", locals())
    
    elif is_student(request.user):
        vous = Student.objects.get(user = request.user)
        return render(request, "students/classes_detail.html", locals())
        
    else:
        return redirect('uploads:connexion')
        
def add_student(request, classeId, studentId):
    classe = Classe.objects.get(id=classeId)
    eleve = Student.objects.get(id=studentId)
    if Teacher.objects.get(user = request.user) == classe.teacher:
        eleve.classes.add(classe)
        eleve.save()
        
    url = '/uploads/classe/' + classeId
    
    return redirect(url)
    
        
def remove_student(request, classeId, studentId):
    classe = Classe.objects.get(id=classeId)
    eleve = Student.objects.get(id=studentId)
    if Teacher.objects.get(user = request.user) == classe.teacher:
        eleve.classes.remove(classe)
        eleve.save()
    
    url = '/uploads/classe/' + classeId
        
    return redirect(url)