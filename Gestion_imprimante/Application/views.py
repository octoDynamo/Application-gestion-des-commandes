from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Commande
from .forms import CommandeForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error_message = 'Invalid credentials'
            return render(request, 'Application/login.html', {'error_message': error_message})
    return render(request, 'Application/login.html')

@login_required
def dashboard(request):
    return redirect('liste_commandes')

@login_required
def liste_commandes(request):
    user_role = 'directeur' if request.user.groups.filter(name='Directeurs').exists() else 'assistant'
    commandes = Commande.objects.all()
    return render(request, 'Application/liste_commandes.html', {'commandes': commandes, 'user_role': user_role})

@login_required
def ajouter_commande(request):
    if not request.user.groups.filter(name='Assistants').exists():
        return redirect('liste_commandes')
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_commandes')
    else:
        form = CommandeForm()
    return render(request, 'Application/ajouter_commande.html', {'form': form})

@login_required
def supprimer_commande(request, pk):
    commande = Commande.objects.get(pk=pk)
    commande.delete()
    return redirect('liste_commandes')

@login_required
def modifier_commande(request, pk):
    commande = Commande.objects.get(pk=pk)
    if request.method == 'POST':
        form = CommandeForm(request.POST, instance=commande)
        if form.is_valid():
            form.save()
            return redirect('liste_commandes')
    else:
        form = CommandeForm(instance=commande)
    return render(request, 'Application/modifier_commande.html', {'form': form})

@login_required
def generer_devis(request, pk):
    if not request.user.groups.filter(name='Directeurs').exists():
        return redirect('liste_commandes')
    commande = Commande.objects.get(pk=pk)
    # Logique pour générer le devis (PDF, etc.)
    return render(request, 'Application/generer_devis.html', {'commande': commande})

def logout_view(request):
    logout(request)
    return redirect('login')
