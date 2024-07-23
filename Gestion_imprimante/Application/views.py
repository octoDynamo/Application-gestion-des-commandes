import os
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Commande, CommandeLog, Designation, Option
from .forms import CommandeForm
from django.db.models import Q

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

def log_action(user, action, commande):
    CommandeLog.objects.create(user=user, action=action, commande=commande)

@login_required
def dashboard(request):
    return redirect('liste_commandes')

@login_required
def liste_commandes(request):
    query = request.GET.get('q')
    if query:
        commandes = Commande.objects.filter(
            Q(order_id__icontains=query) |
            Q(company_reference_number__icontains=query) |
            Q(order_status__icontains=query)
        )
    else:
        commandes = Commande.objects.all()
    user_role = 'directeur' if request.user.groups.filter(name='Directeurs').exists() else 'assistant'
    return render(request, 'Application/liste_commandes.html', {'commandes': commandes, 'user_role': user_role})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Assistants').exists())
def ajouter_commande(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save()
            log_action(request.user, 'add', commande)
            return redirect('designation_commande', pk=commande.id)
    else:
        form = CommandeForm()
    return render(request, 'Application/ajouter_commande.html', {'form': form})

@login_required
def supprimer_commande(request, pk):
    if not request.user.groups.filter(name='Directeurs').exists() and not request.user.groups.filter(name='Assistants').exists():
        return redirect('liste_commandes')
    commande = get_object_or_404(Commande, pk=pk)
    log_action(request.user, 'delete', commande)
    commande.delete()
    return redirect('liste_commandes')

@login_required
def modifier_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    log_action(request.user, 'modify', commande)
    return redirect('designation_commande', pk=commande.pk)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def generer_devis(request, pk):
    commande = get_object_or_404(Commande, pk=pk)

    if request.method == 'POST':
        quantities = request.POST.getlist('quantity[]')
        designations = request.POST.getlist('designation[]')
        options = request.POST.getlist('option[]')
        formats = request.POST.getlist('format[]')
        paper_types = request.POST.getlist('paper_type[]')
        unit_prices = request.POST.getlist('unit_price[]')
        total_prices = request.POST.getlist('total_price[]')

        # Generate the PDF
        response = HttpResponse(content_type='application/pdf')
        filename = f"devis_{commande.order_id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        p = canvas.Canvas(response, pagesize=letter)
        p.drawString(100, 750, f"Devis pour Commande: {commande.order_id}")
        p.drawString(100, 735, f"Date et Heure: {commande.date_time}")
        p.drawString(100, 720, f"Company Reference Number: {commande.company_reference_number}")
        p.drawString(100, 705, f"Order Status: {commande.order_status}")

        y = 680
        p.drawString(100, y, "Quantité")
        p.drawString(200, y, "Désignation")
        p.drawString(300, y, "Option")
        p.drawString(400, y, "Format")
        p.drawString(500, y, "Type de Papier")
        p.drawString(600, y, "Prix Unitaire HT")
        p.drawString(700, y, "Prix Total HT")
        y -= 20

        for qty, des, opt, fmt, pt, up, tp in zip(quantities, designations, options, formats, paper_types, unit_prices, total_prices):
            p.drawString(100, y, str(qty))
            p.drawString(200, y, des)
            p.drawString(300, y, opt)
            p.drawString(400, y, fmt)
            p.drawString(500, y, pt)
            p.drawString(600, y, str(up))
            p.drawString(700, y, str(tp))
            y -= 20

        p.showPage()
        p.save()

        # Save the PDF to a file and serve it
        pdf_path = os.path.join(settings.MEDIA_ROOT, filename)
        with open(pdf_path, 'wb') as f:
            f.write(response.content)

        # Automatically open the PDF on Windows
        os.startfile(pdf_path)

        return redirect('liste_commandes')

    return render(request, 'Application/generer_devis.html', {'commande': commande})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def designation_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        designations = request.POST.getlist('designations[]')

        commande.designations.all().delete()

        for designation_name in designations:
            designation = Designation.objects.create(name=designation_name, commande=commande)
            for i in range(1, 33):
                if request.POST.get(f'option{i}'):
                    Option.objects.create(
                        designation=designation,
                        option_name=request.POST.get(f'option{i}'),
                        format=request.POST.get(f'format{i}'),
                        quantity=request.POST.get(f'quantity{i}'),
                        paper_type=request.POST.get(f'paper_type{i}')
                    )

        # Generate the PDF
        response = HttpResponse(content_type='application/pdf')
        filename = f"fiche_travail_{commande.order_id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        p = canvas.Canvas(response, pagesize=letter)
        p.drawString(100, 750, f"Numéro de dossier: {commande.order_id}")
        p.drawString(100, 735, f"Date: {commande.date_time}")
        p.drawString(100, 720, f"Nom du client: {commande.company_reference_number}")
        p.drawString(100, 705, f"Désignation: {', '.join(designations)}")
        
        y = 690
        for designation in commande.designations.all():
            for option in designation.options.all():
                p.drawString(100, y, f"Option: {option.option_name}, Format: {option.format}, Quantité: {option.quantity}, Type de Papier: {option.paper_type}")
                y -= 15
        
        p.showPage()
        p.save()

        # Save the PDF to a file and serve it
        pdf_path = os.path.join(settings.MEDIA_ROOT, filename)
        with open(pdf_path, 'wb') as f:
            f.write(response.content)

        # Automatically open the PDF on Windows (ensure the path is correct)
        os.startfile(pdf_path)

        return redirect('liste_commandes')

    return render(request, 'Application/designation_commande.html', {'commande': commande})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def log_view(request):
    logs = CommandeLog.objects.all().order_by('-timestamp')
    return render(request, 'Application/log_view.html', {'logs': logs})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def clear_log(request):
    if request.method == 'POST':
        CommandeLog.objects.all().delete()
    return redirect('log_view')
