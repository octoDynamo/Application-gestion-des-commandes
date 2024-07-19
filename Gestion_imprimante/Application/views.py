from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Commande
from .forms import CommandeForm
from django.http import JsonResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import os

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
@user_passes_test(lambda u: u.groups.filter(name='Assistants').exists())
def ajouter_commande(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save()
            return JsonResponse({'commande_id': commande.id})
    else:
        form = CommandeForm()
    return render(request, 'Application/ajouter_commande.html', {'form': form})

@login_required
def supprimer_commande(request, pk):
    if not request.user.groups.filter(name='Directeurs').exists() and not request.user.groups.filter(name='Assistants').exists():
        return redirect('liste_commandes')
    commande = Commande.objects.get(pk=pk)
    commande.delete()
    return redirect('liste_commandes')

@login_required
def modifier_commande(request, pk):
    if not request.user.groups.filter(name='Directeurs').exists() and not request.user.groups.filter(name='Assistants').exists():
        return redirect('liste_commandes')
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
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def generer_devis(request, pk):
    commande = Commande.objects.get(pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="devis.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    p.drawString(100, 750, f"Devis pour Commande: {commande.order_id}")
    p.drawString(100, 735, f"Date et Heure: {commande.date_time}")
    p.drawString(100, 720, f"Company Reference Number: {commande.company_reference_number}")
    p.drawString(100, 705, f"Order Status: {commande.order_status}")
    # Ajoutez plus de détails ici
    p.showPage()
    p.save()

    response.flush()
    os.startfile(response, 'open')  # Ouvre automatiquement le PDF sur Windows

    return response

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def designation_commande(request, pk):
    commande = Commande.objects.get(pk=pk)
    if request.method == 'POST':
        # Récupérer et traiter les options sélectionnées
        designation = request.POST.get('designation')
        # Traitement de la désignation de la commande
        return redirect('liste_commandes')
    return render(request, 'Application/designation_commande.html', {'commande': commande})
