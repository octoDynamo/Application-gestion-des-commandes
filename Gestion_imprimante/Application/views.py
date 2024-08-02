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
from .models import Commande, CommandeLog, Designation, Option
from .forms import CommandeForm
from django.db.models import Q
from django.contrib import messages
from weasyprint import HTML, CSS
from decimal import Decimal
from django.templatetags.static import static
from django.db.models import Max


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
    return render(request, 'Application/liste_commandes.html', {'commandes': commandes, 'is_assistant': is_assistant})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def liste_devis(request):
    query = request.GET.get('q')
    if query:
        devis = Commande.objects.filter(
            Q(order_status='completed') & (
            Q(company_reference_number__icontains=query) |
            Q(client_name__icontains=query) |
            Q(devis_numero__icontains=query)
            )
        )
    else:
        devis = Commande.objects.filter(order_status='completed').order_by('-date_time')
    is_assistant = request.user.groups.filter(name='Assistants').exists()
    return render(request, 'Application/liste_devis.html', {'devis': devis, 'is_assistant': is_assistant})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def liste_factures(request):
    query = request.GET.get('q')
    if query:
        factures = Commande.objects.filter(
            Q(order_status='completed') & (
                Q(company_reference_number__icontains=query) |
                Q(client_name__icontains=query) |
                Q(facture_numero__icontains=query)
            )
        )
    else:
        factures = Commande.objects.filter(order_status='completed').order_by('-date_time')
    is_assistant = request.user.groups.filter(name='Assistants').exists()    
    return render(request, 'Application/liste_factures.html', {'factures': factures, 'is_assistant' : is_assistant})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def liste_bon_livraison(request):
    query = request.GET.get('q')
    if query:
        bon_livraison = Commande.objects.filter(
            Q(order_status='completed') & (
                Q(company_reference_number__icontains=query) |
                Q(client_name__icontains=query) |
                Q(bl_numero__icontains=query)
            )
        )
    else:
        bon_livraison = Commande.objects.filter(order_status='completed').order_by('-date_time')
    is_assistant = request.user.groups.filter(name='Assistants').exists()    
    return render(request, 'Application/liste_bon_livraison.html', {'bon_livraison': bon_livraison, 'is_assistant' : is_assistant})


logger = logging.getLogger(__name__)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def situation_client(request):
    query = request.GET.get('q')
    print(f"Search Query: {query}")  # Debugging line
    if query:
        commandes = Commande.objects.filter(company_reference_number__icontains=query)
        print(f"Commandes found: {[commande.company_reference_number for commande in commandes]}")  # Debugging line
    else:
        commandes = Commande.objects.all()
        print("No query provided or no specific results found, showing all commandes")  # Debugging line

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
    return render(request, 'Application/supprimer_facture.html', {'facture': facture})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def supprimer_devis(request, pk):
    devis = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        devis.delete()
        return redirect('liste_devis')
    return render(request, 'Application/supprimer_devis.html', {'devis': devis})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def supprimer_bl(request, pk):
    bon_livraison = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        bon_livraison.delete()
        return redirect('liste_bon_livraison')
    return render(request, 'Application/supprimer_bl.html', {'bon_livraison': bon_livraison})

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

        # Generate a unique devis_numero if it doesn't exist
        if not commande.devis_numero:
            max_devis_numero = Commande.objects.aggregate(Max('devis_numero'))['devis_numero__max']
            if max_devis_numero is None:
                max_devis_numero = 0

        for idx, option in enumerate(Option.objects.filter(designation__commande=commande)):
            try:
                    unit_price = Decimal(unit_prices[idx])
            except (IndexError, ValueError):
                    unit_price = Decimal('0.00')            
            option.unit_price = unit_price 
            option.total_ht = unit_price * option.quantity 
            option.tva_20 = option.total_ht * Decimal('0.2')
            option.total_ttc = option.total_ht + option.tva_20
            option.save()
            total_prices.append(option.total_ht)

        total_ht = sum(total_prices)
        tva_20 = total_ht * Decimal('0.2')
        total_ttc = total_ht + tva_20

        commande.devis_numero = max_devis_numero + 1
        commande.devis_status = 'devis_termine'
        commande.save()
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
        response['Content-Disposition'] = f'attachment; filename="devis_{commande.devis_numero}.pdf"'

        # Save the PDF to a file and serve it
        pdf_path = os.path.join(settings.MEDIA_ROOT, f"devis_{commande.devis_numero}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(pdf)

        # Automatically open the PDF on Windows
        if os.name == 'nt':
            os.startfile(pdf_path)

        return redirect('liste_devis')

    total_ht = sum(option.unit_price * option.quantity if option.unit_price else Decimal('0.00') for designation in commande.designations.all() for option in designation.options.all())
    tva_20 = total_ht * Decimal('0.20')
    total_ttc = total_ht + tva_20
    commande.devis_status = 'devis_termine'  # Mark facture as complete
    commande.save()
    return render(request, 'Application/generer_devis.html', {
        'commande': commande,
        'total_ht': total_ht,
        'tva_20': tva_20,
        'total_ttc': total_ttc
    })

login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def update_devis_status(request, pk):
    devis = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        devis_status = request.POST.get('devis_status')
        devis.devis_status = devis_status
        devis.save()
    return redirect('liste_devis')

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
            categories = request.POST.getlist(f'categories[{designation_id}][]')
            
            for i, category in enumerate(categories):
                if category:
                    quantity_str = request.POST.getlist(f'quantities[{designation_id}][]')
                    quantity = int(quantity_str[i]) if quantity_str and i < len(quantity_str) and quantity_str[i].isdigit() else 0

                    if designation_name in ['IMPRESSION OFFSET', 'IMPRESSION PETIT FORMAT (NUMÉRIQUE)']:
                        option = Option.objects.create(
                            designation=designation,
                            option_name=category,
                            format=request.POST.getlist(f'formats[{designation_id}][]')[i] if request.POST.getlist(f'formats[{designation_id}][]') else "",
                            quantity=quantity,
                            grammage=request.POST.getlist(f'grammages[{designation_id}][]')[i] if request.POST.getlist(f'grammages[{designation_id}][]') else "",
                            paper_type=request.POST.getlist(f'paper_types[{designation_id}][]')[i] if request.POST.getlist(f'paper_types[{designation_id}][]') else "",
                            recto_verso=request.POST.getlist(f'recto_versos[{designation_id}][]')[i] if request.POST.getlist(f'recto_versos[{designation_id}][]') else "",
                            pelliculage_mat=request.POST.get(f'pelliculage_mat[{designation_id}][]') is not None,
                            pelliculage_brillant=request.POST.get(f'pelliculage_brillant[{designation_id}][]') is not None,
                            spiral=request.POST.get(f'spiral[{designation_id}][]') is not None,
                            piquage=request.POST.get(f'piquage[{designation_id}][]') is not None,
                            collage=request.POST.get(f'collage[{designation_id}][]') is not None,
                            cousu=request.POST.get(f'cousu[{designation_id}][]') is not None
                        )
                    else:
                        option = Option.objects.create(
                            designation=designation,
                            option_name=category,
                            quantity=quantity,
                            paragraph=request.POST.getlist(f'paragraphs[{designation_id}][]')[i] if request.POST.getlist(f'paragraphs[{designation_id}][]') else ""
                        )

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
            'image_url_first_page': request.build_absolute_uri(static('Application/images/fa.jpg')),
            'image_url_other_pages': request.build_absolute_uri(static('Application/images/fa.jpg'))
        })
        html = HTML(string=html_string)
  
        css_string = f"""
        @page {{
            size: A4;
            margin: 3cm 1cm 3cm 1cm;
        }}
        @page :first {{
            margin-top: 5cm;
            background: url('{request.build_absolute_uri(static('Application/images/fa.jpg'))}') no-repeat center center;
            background-size: cover;
        }}
        @page {{
            background: url('{request.build_absolute_uri(static('Application/images/fa.jpg'))}') no-repeat center center;
            background-size: cover;
            margin-top: 3cm;
            margin-bottom: 3cm;
        }}
        body {{
            margin: 0;
            padding: 0;
            background: white;
            box-sizing: border-box;
        }}
        .content {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;

        }}
        .header {{
            margin-top: 5cm; /* Adjust if needed */
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 5px;
            text-align: left;
            border: 1px solid black;
        }}
        .total {{
            font-weight: bold;
        }}
        .right-align {{
            text-align: right;
        }}
        """
        css = CSS(string=css_string)

        pdf = html.write_pdf(stylesheets=[css])

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
    date = datetime.now().strftime('%B %d, %Y')

    if request.method == 'POST':
        quantities = request.POST.getlist('quantity[]')

        if not commande.bl_numero:
            max_bl_numero = Commande.objects.aggregate(Max('bl_numero'))['bl_numero__max']
            if max_bl_numero is None:
                max_bl_numero = 0
            commande.bl_numero = max_bl_numero + 1

        commande.bl_status = 'bl_termine'
        commande.save()

        # Generate the PDF using WeasyPrint
        html_string = render_to_string('Application/bon_livraison_template.html', {
            'commande': commande,
            'date': date,
            'quantities': quantities,
            'image_url': request.build_absolute_uri(static('Application/images/devis.jpg'))
        })
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="bon_livraison_{commande.bl_numero}.pdf"'

        pdf_path = os.path.join(settings.MEDIA_ROOT, f"bon_livraison_{commande.bl_numero}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(pdf)

        if os.name == 'nt':
            os.startfile(pdf_path)

        return redirect('liste_bon_livraison')

    return render(request, 'Application/generer_bon_livraison.html', {
        'commande': commande
    })

login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def update_bl_status(request, pk):
    bon_livraison = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        bl_status = request.POST.get('bl_status')
        bon_livraison.bl_status = bl_status
        bon_livraison.save()
    return redirect('liste_bon_livraison')

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

