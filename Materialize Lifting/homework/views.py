from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group

from homework.auth_utils import *
from homework.models import *
from homework.forms import *

def accueil(request):
    return render(request, "homework/accueil.html")
    
def inscription(request):
    if request.user.is_authenticated():
        return redirect("homework:bureau")
    else:
        if request.method == "POST":
            inscriptionForm = InscriptionForm(request.POST, request.FILES)
            
            if inscriptionForm.is_valid():
                username = inscriptionForm.cleaned_data["pseudo"]
                password = inscriptionForm.cleaned_data["motDePasse"]
                first_name = inscriptionForm.cleaned_data["prenom"]
                last_name = inscriptionForm.cleaned_data["nom"]
                eMail = inscriptionForm.cleaned_data["courriel"]
                
                try:
                    User.objects.get(username=username)
                
                except User.DoesNotExist:
                    modeleCompte = None
                    
                    if inscriptionForm.cleaned_data["modeleCompte"] == "etudiant":
                        modeleCompte = Etudiant()
                        group_name = "étudiants"
                        
                    elif inscriptionForm.cleaned_data["modeleCompte"] == "professeur":
                        modeleCompte = Professeur()
                        group_name = "professeurs"
                        
                    user = User.objects.create_user(username, eMail, password)
                    user.first_name = first_name
                    user.last_name = last_name
                    
                    try:
                        groupe = Group.objects.get(name=group_name)
                    
                    except:
                        groupe = Group.objects.create(name=group_name)
                    
                    user.groups.add(groupe)
                    user.save()
                        
                    compte = modeleCompte
                    compte.user = user
                    compte.save()
                    
                    return redirect("homework:connexion")
    
        else:
            inscriptionForm = InscriptionForm()
            
        return render(request, "homework/inscription.html", locals())

def connexion(request):
    if request.user.is_authenticated():
        return redirect("homework:bureau")
    else:    
        erreur = False
        
        if request.method == "POST":
            connexionForm = ConnexionForm(request.POST, request.FILES)
            
            if connexionForm.is_valid():
                username = connexionForm.cleaned_data["pseudo"]
                password = connexionForm.cleaned_data["motDePasse"]
                user = authenticate(username=username, password=password)
                
                if user:
                    login(request, user)
                    
                    return redirect("homework:bureau")
                else:
                    erreur = True
        else:
            connexionForm = ConnexionForm()
            
        return render(request, "homework/connexion.html", locals())
        #return render(request, "material/connexion.html", locals())
        
def deconnexion(request):
    logout(request)
    
    return redirect("homework:accueil")
    
def bureau(request):
    if estEtudiant(request.user):
        etudiant = Etudiant.objects.get(user=request.user)
        classes = etudiant.classe.all()
        images = Image.objects.filter(etudiant=etudiant)
        
        devoirs = Devoir.objects.all().filter(classe=classes).distinct().order_by("-dateReddition")
        
        dejaFait = []
        devoirsAFaire = []
        
        for devoir in devoirs:
            for image in images:
                if image.devoir == devoir:
                    dejaFait.append(devoir)
        
        for devoir in devoirs:
            if devoir not in dejaFait:
                devoirsAFaire.append(devoir)
                
        return render(request, "etudiant/bureau.html", locals())
    
    elif estProfesseur(request.user):
        professeur = Professeur.objects.get(user=request.user)
        classes = Classe.objects.filter(professeur=professeur)
        eleves = []
        
        for classe in classes:
            elevesAAjouter = Etudiant.objects.filter(classe=classe)
            for eleveAAjouter in elevesAAjouter:
                eleves.append(eleveAAjouter)
        
        images = Image.objects.all().order_by("-date")
        
        imagesAMontrer = []
        
        while len(imagesAMontrer) < 5:
            for image in images:
                if image.etudiant in eleves and image not in imagesAMontrer:
                    imagesAMontrer.append(image)
            if len(images) == len(imagesAMontrer):
                break
        if len(imagesAMontrer) == 0:
            imageAucune = True
        else:
            imageAucune = False
        return render(request, "professeur/bureau.html", locals())
    
    else:
        return redirect("homework:connexion")

def classeIndex(request):
    if estProfesseur(request.user):
        erreur = False
        professeur = Professeur.objects.get(user=request.user)
        classes = Classe.objects.filter(professeur=professeur)
        
        if request.method == "POST":
            creerClasseForm = CreerClasseForm(request.POST, request.FILES)
            if creerClasseForm.is_valid():
                classeNom = creerClasseForm.cleaned_data["nom"]
                try:
                    classe = Classe.objects.get(nom=classeNom)
                    erreur = True
                except:
                    classe = Classe()
                    classe.nom = classeNom
                    classe.branche = creerClasseForm.cleaned_data["branche"]
                    classe.professeur = professeur
                    classe.save()
                    creerClasseForm = CreerClasseForm()
        else:
            creerClasseForm = CreerClasseForm()
        
        branches = [("Allemand"),
                    ("Anglais"),
                    ("Arts Visuels"),
                    ("Biologie"),
                    ("Chimie"),
                    ("Français"),
                    ("Histoire"),
                    ("Maths"),
                    ("Musique"),
                    ("Philosophie"),
                    ("Physique"),
                    ("Sport")]
                    
        return render(request, "professeur/classeIndex.html", locals())
    
    elif estEtudiant(request.user):
        etudiant = Etudiant.objects.get(user=request.user)
        classes = etudiant.classe.all()
        
        return render(request, "etudiant/classeIndex.html", locals())
        
    else:
        return redirect("homework:connexion")

def classeEdition(request, classeNom):
    if estProfesseur(request.user) or estEtudiant(request.user):
        classe = Classe.objects.get(nom=classeNom)
        classeEtudiants = Etudiant.objects.filter(classe=classe)
        classeProfesseur = classe.professeur
        etudiantsTous = Etudiant.objects.exclude(classe=classe)
        
        if estProfesseur(request.user):
            professeurConnecte = Professeur.objects.get(user=request.user)
            if professeurConnecte == classeProfesseur:
                if request.method == "POST":
                    if 'etudiantSuppr' in request.POST:
                        etudiantSupprForm = EtudiantSupprForm(request.POST, request.FILES)              
                        if etudiantSupprForm.is_valid():                                                
                            for etudiant in etudiantSupprForm.cleaned_data["etudiants"]:                
                                etudiant.classe.remove(classe)                             
                                etudiant.save()
                                
                                etudiantSupprForm = EtudiantSupprForm()
                                etudiantAjoutForm = EtudiantAjoutForm()
                                etudiantSupprForm.fields['etudiants'].queryset = Etudiant.objects.filter(classe=classe)
                                etudiantAjoutForm.fields['etudiants'].queryset = Etudiant.objects.exclude(classe=classe)
        
                    elif 'etudiantAjout' in request.POST:
                        etudiantAjoutForm = EtudiantAjoutForm(request.POST, request.FILES)
                        if etudiantAjoutForm.is_valid():
                            for etudiant in etudiantAjoutForm.cleaned_data["etudiants"]:
                                etudiant.classe.add(classe)
                                etudiant.save()
                                
                                etudiantSupprForm = EtudiantSupprForm()
                                etudiantAjoutForm = EtudiantAjoutForm()
                                etudiantSupprForm.fields['etudiants'].queryset = Etudiant.objects.filter(classe=classe)
                                etudiantAjoutForm.fields['etudiants'].queryset = Etudiant.objects.exclude(classe=classe)
                else:
                    etudiantSupprForm = EtudiantSupprForm()
                    etudiantAjoutForm = EtudiantAjoutForm()
                    etudiantSupprForm.fields['etudiants'].queryset = Etudiant.objects.filter(classe=classe)
                    etudiantAjoutForm.fields['etudiants'].queryset = Etudiant.objects.exclude(classe=classe)
                
                return render(request, "professeur/classeEditionPropre.html", locals())
            else:
                return render(request, "professeur/classeEditionAutre.html", locals())
        
        elif estEtudiant(request.user):
            etudiantConnecte = Etudiant.objects.get(user=request.user)
            classeEtudiants = Etudiant.objects.exclude(user=request.user)
            erreur = False
            if request.method == "POST":
                if 'quitterClasse' in request.POST:
                    quitterClasseForm = QuitterClasseForm(request.POST, request.FILES)              
                    if quitterClasseForm.is_valid():                                                
                        if quitterClasseForm.cleaned_data["nomClasse"] == classe.nom:                
                            etudiantConnecte.classe.remove(classe)                             
                            etudiantConnecte.save()
                            
                            return redirect("homework:connexion")
                        else:
                            erreur = True
            else:
                quitterClasseForm = QuitterClasseForm()        
            return render(request, "etudiant/classeEdition.html", locals())
    
    else:
        return redirect("homework:connexion")

def devoirIndex(request):
    if estProfesseur(request.user):
        erreur = False
        professeur = Professeur.objects.get(user=request.user)
        classes = Classe.objects.filter(professeur=professeur)
        devoirs = Devoir.objects.filter(professeur=professeur)
        
        if request.method == "POST":
            creerDevoirForm = CreerDevoirForm(request.POST, request.FILES)
            if creerDevoirForm.is_valid():
                try:
                    devoir = Devoir.objects.get(titre=creerDevoirForm.cleaned_data["titre"])
                    erreur = True
                except:
                    devoir = Devoir()
                    devoir.professeur = Professeur.objects.get(user=request.user)
                    devoir.titre = creerDevoirForm.cleaned_data["titre"]
                    devoir.consigne = creerDevoirForm.cleaned_data["consigne"]
                    devoir.consigneImg = creerDevoirForm.cleaned_data["consigneImg"]
                    devoir.reponse = creerDevoirForm.cleaned_data["reponse"]
                    devoir.reponseImg = creerDevoirForm.cleaned_data["reponseImg"]
                    devoir.dateReddition = creerDevoirForm.cleaned_data["dateReddition"]
                    devoir.save()
                    
                    for classeNom in creerDevoirForm.cleaned_data['classe']:
                        devoir.classe.add(classeNom)
                        devoir.save()
        else:
            creerDevoirForm = CreerDevoirForm()
        
        creerDevoirForm.fields['classe'].queryset = Classe.objects.filter(professeur=professeur)
        
        return render(request, "professeur/devoirIndex.html", locals())
    
    elif estEtudiant(request.user):
        etudiant = Etudiant.objects.get(user=request.user)
        classes = etudiant.classe.all()
        images = Image.objects.filter(etudiant=etudiant)
        
        devoirs = Devoir.objects.all().filter(classe=classes).order_by("-dateReddition")
        
        dejaFait = []
        pasFait = []
        
        for devoir in devoirs:
            for image in images:
                if image.devoir == devoir:
                    dejaFait.append(devoir)
        
        for devoir in devoirs:
            if devoir not in dejaFait:
                pasFait.append(devoir)
        
        return render(request, "etudiant/devoirIndex.html", locals())
    
    else:
        return redirect("homework:connexion")

def devoirEdition(request, devoirTitre):
    devoir = Devoir.objects.get(titre=devoirTitre)
    if estProfesseur(request.user):
        professeurConnecte = Professeur.objects.get(user=request.user)
        devoirProfesseur = devoir.professeur
        autorise = True
        if professeurConnecte == devoirProfesseur:
            if request.method == "POST":
                if 'devoirCons' in request.POST:
                    devoirConsForm = DevoirConsForm(request.POST, request.FILES)
                    if devoirConsForm.is_valid():
                        devoir.consigne = devoirConsForm.cleaned_data["consigne"]
                        devoir.save()
                elif 'devoirConsImg' in request.POST:
                    devoirConsImgForm = DevoirConsImgForm(request.POST, request.FILES)
                    if devoirConsImgForm.is_valid():
                        devoir.consigneImg = devoirConsImgForm.cleaned_data["consigneImg"]
                        devoir.save()
                elif 'devoirRep' in request.POST:
                    devoirRepForm = DevoirRepForm(request.POST, request.FILES)
                    if devoirRepForm.is_valid():
                        devoir.reponse = devoirRepForm.cleaned_data["reponse"]
                        devoir.save()        
                elif 'devoirRepImg' in request.POST:
                    devoirRepImgForm = DevoirRepImgForm(request.POST, request.FILES)
                    if devoirRepImgForm.is_valid():
                        devoir.reponseImg = devoirRepImgForm.cleaned_data["reponseImg"]
                        devoir.save()    
                elif 'devoirDate' in request.POST:
                    devoirDateForm = DevoirDateForm(request.POST, request.FILES)
                    if devoirDateForm.is_valid():
                        devoir.dateReddition = devoirDateForm.cleaned_data["dateReddition"]
                        devoir.save()
            
            devoirConsForm = DevoirConsForm()
            devoirConsImgForm = DevoirConsImgForm()
            devoirRepForm = DevoirRepForm()
            devoirRepImgForm = DevoirRepImgForm()
            devoirDateForm = DevoirDateForm()
            
            return render(request, "professeur/devoirEdition.html", locals())
        else:
            autorise=False
    
    else:
        return redirect("homework:connexion")

def chargerImage(request, devoirTitre):
    if estProfesseur(request.user):
        return render(request, "professeur/nonAutorise.html", locals())
    
    elif estEtudiant(request.user):
        devoir = Devoir.objects.get(titre=devoirTitre)
        etudiant = Etudiant.objects.get(user=request.user)
        
        dejaFait = False
        images = Image.objects.filter(etudiant=etudiant)
        for image in images:
            if image.devoir == devoir:
                dejaFait = True
                
        if request.method == "POST":
            chargerImageForm = ChargerImageForm(request.POST, request.FILES)
            if chargerImageForm.is_valid():
                image = Image()
                image.etudiant = etudiant
                image.photo = chargerImageForm.cleaned_data["photo"]
                image.devoir = devoir
                image.description = chargerImageForm.cleaned_data["description"]
                image.save()
                dejaFait = True
        else:
            chargerImageForm = ChargerImageForm()
        
        return render(request, "etudiant/chargerImage.html", locals())
    else:
        return redirect("homework:connexion")

def imageIndexEtudiant(request):
    if estProfesseur(request.user):
        return render(request, "professeur/nonAutorise.html", locals())
    elif estEtudiant(request.user):
        etudiant = Etudiant.objects.get(user=request.user)
        imageAucune = False
        images = Image.objects.filter(etudiant=etudiant)
        if len(images) == 0:
            imageAucune = True
            
        return render(request, "etudiant/imageIndex.html", locals())
    else:
        return redirect("homework:connexion")

def imageEditionEtudiant(request, devoirTitre):
    if estProfesseur(request.user):
        return render(request, "professeur/nonAutorise.html", locals())
    elif estEtudiant(request.user):
        etudiant = Etudiant.objects.get(user=request.user)
        imageAucune = False
        try:
            devoir = Devoir.objects.get(titre=devoirTitre)
            image = Image.objects.filter(etudiant=etudiant).get(devoir=devoir)
        except:
            imageAucune = True
        
        return render(request, "etudiant/imageEdition.html", locals())
    else:
        return redirect("homework:connexion")

def imageIndexProfesseur(request, devoirTitre):
    if estEtudiant(request.user):
        return render(request, "etudiant/nonAutorise.html", locals())
    elif estProfesseur(request.user):
        professeur = Professeur.objects.get(user=request.user)
        devoir = Devoir.objects.get(titre=devoirTitre)
        if devoir.professeur == professeur:
            images = Image.objects.filter(devoir=devoir)
            if len(images) == 0:
                imageAucune = True
            else:
                imageAucune = False
            
        
            return render(request, "professeur/imageIndex.html", locals())
        else:
            return render(request, "professeur/nonAutorise.html", locals())
    else:
        return redirect("homework:connexion")

def imageEditionProfesseur(request, imageId):
    if estEtudiant(request.user):
        return render(request, "etudiant/nonAutorise.html", locals())
    elif estProfesseur(request.user):
        image = Image.objects.get(id=imageId)
                
        return render(request, "professeur/imageEdition.html", locals())
    else:
        return redirect("homework:connexion")