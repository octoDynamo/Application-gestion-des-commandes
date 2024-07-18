from django.shortcuts import render, get_object_or_404, redirect
from .models import Commande
from .forms import CommandeForm

def liste_commandes(request):
    commandes = Commande.objects.all()
    return render(request, 'Application/liste_commandes.html', {'commandes': commandes})

def ajouter_commande(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_commandes')
    else:
        form = CommandeForm()
    return render(request, 'Application/ajouter_commande.html', {'form': form})
