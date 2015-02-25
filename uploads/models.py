from django.db import models

class Theme(models.Model):
    value = models.CharField(max_length=1)

class Picture(models.Model):
    #ImageField pour que l'image soit enregistrée comme une image
    image = models.ImageField(upload_to="uploadedImages")
    
    #tag: court énoncé sur l'image si nécessaire, par après sera remplacé par
    #le nom de l'exercice
    tag = models.CharField(max_length=20, null=True)
    
    #description: texte pour décrire l'image et apporter des précisions si nécessaire
    description = models.CharField(max_length=500, null=True)
    
    saturation = models.DecimalField(decimal_places=1, max_digits=2, default=0)
    
    contraste = models.DecimalField(decimal_places=1, max_digits=2, default=0)
    
    luminosite = models.DecimalField(decimal_places=1, max_digits=2, default=0)
    
    #désactivés pour l'instant
    #destinateur, celui qui envoie l'image
    #sender = models.ForeignKey(Student, null=True)
    #destinataire, souvvent le professeur si une image ne passe pas par un
    #exercice mais va directemetn chez le professeur pour une question, par ex.
    #recipient = models.ForeignKey(Teacher, null=True)
    
    #exercices concernés si nécessaire mais ceci sera sûrement ajouté 
    #automatiquement lors de l'appui sur le bouton à la fin d'un exercice
    #exercises = models.ManyToManyField(Exercise, null=True)
    #courses = models.ManyToManyField(Course, null=True)
    
    #date de l'upload
    date = models.DateField(auto_now_add=True)