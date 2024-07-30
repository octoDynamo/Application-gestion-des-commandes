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
from django.contrib import messages
from weasyprint import HTML
from django.template.loader import render_to_string  # Add this import

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Mot de passe ou username oublié')
            return render(request, 'Application/login.html')
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
            Q(client_name__icontains=query) |
            Q(order_status__icontains=query)
        )
    else:
        commandes = Commande.objects.all()
    is_director = request.user.groups.filter(name='Directeurs').exists()
    return render(request, 'Application/liste_commandes.html', {'commandes': commandes, 'is_director': is_director})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Assistants').exists())
def ajouter_commande(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save(commit=False)
            # Additional fields not in the form
            commande.order_status = 'draft'
            commande.save()
            return redirect('designation_commande', pk=commande.order_id)
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
        total_prices = []

        # Calculate total prices
        for unit_price, quantity in zip(unit_prices, quantities):
            try:
                unit_price = float(unit_price)
                quantity = int(quantity)
                total_prices.append(unit_price * quantity)
            except ValueError:
                total_prices.append(0)  # Default to 0 if parsing fails

        # Generate the PDF using WeasyPrint
        html_string = render_to_string('Application/devis_template.html', {
            'commande': commande,
            'quantities': quantities,
            'designations': designations,
            'options': options,
            'formats': formats,
            'paper_types': paper_types,
            'unit_prices': unit_prices,
            'total_prices': total_prices
        })
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="devis_{commande.order_id}.pdf"'

        # Save the PDF to a file and serve it
        pdf_path = os.path.join(settings.MEDIA_ROOT, f"devis_{commande.order_id}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(pdf)

        # Automatically open the PDF on Windows
        os.startfile(pdf_path)

        return redirect('liste_commandes')

    return render(request, 'Application/generer_devis.html', {'commande': commande})

def logout_view(request):
    logout(request)
    return redirect('login')

def designation_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        # Supprimer les désignations existantes
        commande.designations.all().delete()

        # Ajouter les nouvelles désignations et options
        designations = request.POST.getlist('designations[]')
        print("Designations:", designations)  # Debug

        for designation_id, designation_name in enumerate(designations):
            designation = Designation.objects.create(name=designation_name, commande=commande)
            option_names = request.POST.getlist(f'options[{designation_id}][]')
            formats = request.POST.getlist(f'formats[{designation_id}][]')
            quantities = request.POST.getlist(f'quantities[{designation_id}][]')
            paper_types = request.POST.getlist(f'paper_types[{designation_id}][]')
            
            print(f"Options for {designation_name}: {option_names}")  # Debug

            for i in range(len(option_names)):
                if option_names[i]:
                    quantity = quantities[i] if quantities[i] else 0
                    Option.objects.create(
                        designation=designation,
                        option_name=option_names[i],
                        format=formats[i],
                        quantity=int(quantity),
                        paper_type=paper_types[i]
                    )

        commande.order_status = 'completed'
        commande.save()

        # Générer le PDF using WeasyPrint
        html_string = render_to_string('Application/fiche_template.html', {
            'commande': commande
        })
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="fiche_travail_{commande.order_id}.pdf"'

        # Save the PDF to a file and serve it
        pdf_path = os.path.join(settings.MEDIA_ROOT, f"fiche_travail_{commande.order_id}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(pdf)

        # Automatically open the PDF on Windows
        if os.name == 'nt':  # Check if the OS is Windows
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
