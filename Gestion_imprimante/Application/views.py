from datetime import datetime
import os
import logging
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string
from .models import Commande, CommandeLog, Designation, Option, Prix
from .forms import CommandeForm
from django.db.models import Q
from django.contrib import messages
from weasyprint import HTML
from decimal import Decimal
from django.templatetags.static import static


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name='Directeurs').exists():
                return redirect('welcome_director')
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
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def welcome_director(request):
    return render(request, 'Application/welcome_director.html')


@login_required
def liste_commandes(request):
    query = request.GET.get('q')
    if query:
        commandes = Commande.objects.filter(
            Q(order_id__icontains=query) |
            Q(client_name__icontains=query)  
        )
    else:
        commandes = Commande.objects.filter(order_status__in=['draft', 'completed'])
    is_assistant = request.user.groups.filter(name='Assistants').exists()
    is_director = request.user.groups.filter(name='Directeurs').exists()    
    return render(request, 'Application/liste_commandes.html', {'commandes': commandes, 'is_director': is_director})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def liste_devis(request):
    commandes = Commande.objects.all()
    return render(request, 'Application/liste_devis.html', {'commandes': commandes})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def liste_factures(request):
    query = request.GET.get('q')
    if query:
        factures = Commande.objects.filter(
            Q(order_status='completed') & (
                Q(order_id__icontains=query) |
                Q(company_reference_number__icontains=query) |
                Q(client_name__icontains=query) |
                Q(facture_numero__icontains=query)
            )
        )
    else:
        factures = Commande.objects.filter(order_status='completed').order_by('-date_time')
    return render(request, 'Application/liste_factures.html', {'factures': factures})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def liste_bon_livraison(request):
    commandes = Commande.objects.all()
    return render(request, 'Application/liste_bon_livraison.html', {'commandes': commandes})

logger = logging.getLogger(__name__)
@login_required
def situation_client(request):
    query = request.GET.get('q')
    commandes = []

    if query:
        # Debug: Print the raw query
        print(f"Raw query: {query}")
        
        # Filter commandes based on the query
        commandes = Commande.objects.filter(company_reference_number__icontains=query)
        
        # Debug: Print the queryset
        print(f"Filtered commandes: {commandes}")
    else:
        # Debug: Indicate no query was provided
        print("No query provided.")
    
    # Debug: Print if commandes is empty or not
    if not commandes:
        print("No commandes found.")

    return render(request, 'Application/situation_client.html', {'commandes': commandes, 'query': query})


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Assistants').exists())
def ajouter_commande(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save(commit=False)
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
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def supprimer_facture(request, pk):
    facture = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        facture.delete()
        return redirect('liste_factures')
    return render(request, 'Application/confirmer_suppression_facture.html', {'facture': facture})

@login_required
def modifier_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    log_action(request.user, 'modify', commande)
    return redirect('designation_commande', pk=commande.pk)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def generer_devis(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    date = datetime.now().strftime('%B %d, %Y')


    if request.method == 'POST':
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')
        total_prices = []

        for idx, option in enumerate(Option.objects.filter(designation__commande=commande)):
            unit_price = Decimal(unit_prices[idx])
            option.unit_price = unit_price
            option.total_ht = unit_price * option.quantity
            option.tva_20 = option.total_ht * Decimal('0.2')
            option.total_ttc = option.total_ht + option.tva_20
            option.save()
            total_prices.append(option.total_ht)

        total_ht = sum(total_prices)
        tva_20 = total_ht * Decimal('0.2')
        total_ttc = total_ht + tva_20

        # Generate the PDF using WeasyPrint
        html_string = render_to_string('Application/devis_template.html', {
            'commande': commande,
            'date': date,
            'quantities': quantities,
            'unit_prices': unit_prices,
            'total_prices': total_prices,
            'total_ht': total_ht,
            'tva_20': tva_20,
            'total_ttc': total_ttc,
            'image_url': request.build_absolute_uri(static('Application/images/devis.jpg'))

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
        if os.name == 'nt':
            os.startfile(pdf_path)

        return redirect('liste_devis')

    total_ht = sum(option.unit_price * option.quantity if option.unit_price else Decimal('0.00') for designation in commande.designations.all() for option in designation.options.all())
    tva_20 = total_ht * Decimal('0.20')
    total_ttc = total_ht + tva_20

    return render(request, 'Application/generer_devis.html', {
        'commande': commande,
        'total_ht': total_ht,
        'tva_20': tva_20,
        'total_ttc': total_ttc
    })

def logout_view(request):
    logout(request)
    return redirect('login')

def designation_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        commande.designations.all().delete()

        designations = request.POST.getlist('designations[]')
        for designation_id, designation_name in enumerate(designations):
            designation = Designation.objects.create(name=designation_name, commande=commande)
            option_names = request.POST.getlist(f'options[{designation_id}][]')
            formats = request.POST.getlist(f'formats[{designation_id}][]', default=[""] * len(option_names))
            quantities = request.POST.getlist(f'quantities[{designation_id}][]', default=["0"] * len(option_names))
            grammages = request.POST.getlist(f'grammages[{designation_id}][]', default=[""] * len(option_names))
            paper_types = request.POST.getlist(f'paper_types[{designation_id}][]', default=[""] * len(option_names))
            recto_versos = request.POST.getlist(f'recto_verso[{designation_id}][]', default=[""] * len(option_names))

            for i in range(len(option_names)):
                if option_names[i]:
                    quantity = int(quantities[i]) if quantities[i] else 0
                    Option.objects.create(
                        designation=designation,
                        option_name=option_names[i],
                        format=formats[i],
                        quantity=quantity,
                        grammage=grammages[i],
                        paper_type=paper_types[i],
                        recto_verso=recto_versos[i]
                    )

            # Handle the finishing options
            spirals = request.POST.getlist(f'spiral[{designation_id}][]')
            piquages = request.POST.getlist(f'piquage[{designation_id}][]')
            collages = request.POST.getlist(f'collage[{designation_id}][]')
            cousus = request.POST.getlist(f'cousu[{designation_id}][]')
            pelliculage_mats = request.POST.getlist(f'pelliculage_mat[{designation_id}][]')
            pelliculage_brillants = request.POST.getlist(f'pelliculage_brillant[{designation_id}][]')

            for spiral in spirals:
                Option.objects.create(designation=designation, option_name='Spiral', quantity=1 if spiral else 0)
            for piquage in piquages:
                Option.objects.create(designation=designation, option_name='Piquage', quantity=1 if piquage else 0)
            for collage in collages:
                Option.objects.create(designation=designation, option_name='Collage', quantity=1 if collage else 0)
            for cousu in cousus:
                Option.objects.create(designation=designation, option_name='Cousu', quantity=1 if cousu else 0)
            for pelliculage_mat in pelliculage_mats:
                Option.objects.create(designation=designation, option_name=f'Pelliculage Mat {pelliculage_mat}', quantity=1 if pelliculage_mat else 0)
            for pelliculage_brillant in pelliculage_brillants:
                Option.objects.create(designation=designation, option_name=f'Pelliculage Brillant {pelliculage_brillant}', quantity=1 if pelliculage_brillant else 0)

        commande.order_status = 'completed'
        commande.save()

        html_string = render_to_string('Application/fiche_template.html', {
            'commande': commande
        })
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="fiche_travail_{commande.order_id}.pdf"'

        pdf_path = os.path.join(settings.MEDIA_ROOT, f"fiche_travail_{commande.order_id}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(pdf)

        if os.name == 'nt':
            os.startfile(pdf_path)

        return redirect('liste_commandes')

    return render(request, 'Application/designation_commande.html', {'commande': commande})
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def generer_facture(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    date = datetime.now().strftime('%B %d, %Y')

    
    if request.method == 'POST':
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')
        total_prices = []
        bc_number = request.POST.get('bc_number')
        date_bc = request.POST.get('date_bc')


         # Automatically assign a facture number if not already assigned
        if not commande.facture_numero:
            last_facture = Commande.objects.exclude(facture_numero=None).order_by('-facture_numero').first()
            if last_facture:
                commande.facture_numero = last_facture.facture_numero + 1
            else:
                commande.facture_numero = 1



        for idx, option in enumerate(Option.objects.filter(designation__commande=commande)):
            unit_price = Decimal(unit_prices[idx])
            option.unit_price = unit_price
            option.total_ht = unit_price * option.quantity
            option.tva_20 = option.total_ht * Decimal('0.2')
            option.total_ttc = option.total_ht + option.tva_20
            option.save()
            total_prices.append(option.total_ht)


        total_ht = sum(total_prices)
        tva_20 = total_ht * Decimal('0.20')
        total_ttc = total_ht + tva_20
        

        # Save these values to the Commande model
        commande.bc_number = bc_number
        commande.date_bc = date_bc
        commande.facture_status = 'facture_termine'  # Mark facture as complete
        commande.save()

        # Generate the PDF using WeasyPrint
        html_string = render_to_string('Application/facture_template.html', {
            'commande': commande,
            'date': date,
            'bc_number': bc_number,
            'date_bc': date_bc,
            'quantities': quantities,
            'unit_prices': unit_prices,
            'total_prices': total_prices,
            'total_ht': total_ht,
            'tva_20': tva_20,
            'total_ttc': total_ttc,
            'image_url': request.build_absolute_uri(static('Application/images/devis.jpg'))

        })
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{commande.facture_numero}.pdf"'

        pdf_path = os.path.join(settings.MEDIA_ROOT, f"facture_{commande.facture_numero}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(pdf)

        if os.name == 'nt':
            os.startfile(pdf_path)

        return redirect('liste_factures')

    total_ht = sum(option.unit_price * option.quantity if option.unit_price else Decimal('0.00') for designation in commande.designations.all() for option in designation.options.all())
    tva_20 = total_ht * Decimal('0.20')
    total_ttc = total_ht + tva_20


    return render(request, 'Application/generer_facture.html', {
        'commande': commande,
        'total_ht': total_ht,
        'tva_20': tva_20,
        'total_ttc': total_ttc
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def update_facture_status(request, pk):
    facture = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        remarque = request.POST.get('remarque')
        facture.remarque = remarque
        if remarque == 'paye':
            facture.facture_status = 'facture_termine'
        facture.save()
    return redirect('liste_factures')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def generer_bon_livraison(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        quantities = request.POST.getlist('quantity[]')

        # Generate the PDF using WeasyPrint
        html_string = render_to_string('Application/bon_livraison_template.html', {
            'commande': commande,
            'quantities': quantities
        })
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="bon_livraison_{commande.order_id}.pdf"'

        pdf_path = os.path.join(settings.MEDIA_ROOT, f"bon_livraison_{commande.order_id}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(pdf)

        if os.name == 'nt':
            os.startfile(pdf_path)

        return redirect('liste_bon_livraison')

    return render(request, 'Application/generer_bon_livraison.html', {
        'commande': commande
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def situation_client(request):
    if request.method == 'POST':
        client_ref = request.POST.get('client_ref')
        commandes = Commande.objects.filter(company_reference_number=client_ref, order_status='unpaid')
        html_string = render_to_string('Application/situation_client_template.html', {'commandes': commandes, 'client_ref': client_ref})
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="situation_client_{client_ref}.pdf"'

        pdf_path = os.path.join(settings.MEDIA_ROOT, f"situation_client_{client_ref}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(pdf)

        if os.name == 'nt':
            os.startfile(pdf_path)

        return redirect('liste_commandes')

    return render(request, 'Application/situation_client.html')

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

