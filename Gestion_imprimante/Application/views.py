from datetime import datetime
import os
import logging.config
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string
from .models import Commande, Designation, LogEntry, Option, Facture, Devis, BonLivraison
from .forms import CommandeForm
from django.db.models import Q
from django.contrib import messages 
from weasyprint import HTML, CSS
from decimal import Decimal
from django.templatetags.static import static
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

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

def log_action(user, action, commande=None, facture=None, devis=None, bon_livraison=None):
    LogEntry.objects.create(
        user=user,
        action=action,
        commande=commande,
        facture=facture,
        devis=devis,
        bon_livraison=bon_livraison
    )

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
        commandes = Commande.objects.filter(
            Q(order_status='completed') & (
                Q(company_reference_number__icontains=query) |
                Q(client_name__icontains=query) |
                Q(devis_numero__icontains=query)
            )
        )
    else:
        commandes = Commande.objects.filter(order_status='completed').order_by('-date_time')
    
    is_assistant = request.user.groups.filter(name='Assistants').exists()
    return render(request, 'Application/liste_devis.html', {'devis_list': commandes, 'is_assistant': is_assistant})

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

def create_situation_client_pdf(output_path, client_name, client_ref, factures, background_image_url, second_background_image_url):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Define custom styles
    large_bold_font = ParagraphStyle('LargeBoldFont', parent=styles['Normal'], fontSize=14, fontName="Helvetica-Bold")
    normal_font = ParagraphStyle('NormalFont', parent=styles['Normal'], fontName="Helvetica", alignment=1)
    bold_font = ParagraphStyle('BoldFont', parent=styles['Normal'], fontName="Helvetica-Bold", alignment=1)
    table_header_font = ParagraphStyle('TableHeaderFont', parent=styles['Normal'], fontSize=12, fontName="Helvetica-Bold", alignment=1)

    width, height = A4

    # Header information
    header = [
        ["", f"Rabat, le {datetime.now().strftime('%d/%m/%y')}"],
    ]
    table_header = Table(header, colWidths=[14 * cm, 5 * cm])
    table_header.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 14),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(Spacer(1, 5 * cm))  # Move the content down by 5 cm from the top
    elements.append(table_header)
    elements.append(Spacer(1, 12))

    # Info section
    info = [
        f"Situation du client: {client_name} (Réf: {client_ref})",
    ]
    for line in info:
        elements.append(Paragraph(line, large_bold_font))
    elements.append(Spacer(1, 24))

    # Prepare data for the table
    data = [
        [Paragraph("Facture N°", table_header_font), 
         Paragraph("Date", table_header_font), 
         Paragraph("Montant TTC", table_header_font)]
    ]

    for facture in factures:
        data.append([
            str(facture.facture_numero),
            facture.facture_date.strftime('%d/%m/%Y'),
            f"{facture.total_ttc:.2f}"
        ])

    # Create the main table
    table = Table(data, colWidths=[4 * cm, 4 * cm, 6 * cm], repeatRows=1)
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEADING', (0, 0), (-1, -1), 20),  # Increase row height
    ])
    table.setStyle(style)

    elements.append(table)
    elements.append(Spacer(1, 1 * cm))

    def on_first_page(canvas, doc):
        draw_background(canvas, background_image_url, *A4)
    
    def on_later_pages(canvas, doc):
        draw_background(canvas, second_background_image_url, *A4)
        canvas.saveState()
        canvas.translate(0, -5 * cm)  # Move content up by 5 cm
        canvas.restoreState()

    # Build the PDF
    doc.build(elements, onFirstPage=on_first_page, onLaterPages=on_later_pages)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def generer_situation_client(request):
    client_ref = request.GET.get('client_ref')
    factures = Commande.objects.filter(company_reference_number=client_ref, facture_status='facture_termine', remarque='non payé')
    client_name = factures.first().client_name if factures.exists() else "Client"

    # Fetch total_ttc for each facture from the Option table
    for facture in factures:
        options = Option.objects.filter(designation__commande=facture)
        facture.total_ttc = sum(option.total_ttc for option in options)
        print(f"Commande ID: {facture.order_id}, Total TTC: {facture.total_ttc}")  # Debugging print statement

    if request.method == 'POST':
        selected_factures_ids = request.POST.getlist('facture_ids')
        selected_factures = [facture for facture in factures if str(facture.order_id) in selected_factures_ids]

        # Generate the PDF using ReportLab
        output_path = os.path.join(settings.MEDIA_ROOT, f"situation_client_{client_ref}.pdf")
        background_image_url = os.path.join(settings.STATIC_ROOT, 'images/devis.png')
        second_background_image_url = os.path.join(settings.STATIC_ROOT, 'images/fa.jpg')
        create_situation_client_pdf(output_path, client_name, client_ref, selected_factures, background_image_url, second_background_image_url)

        # Serve the PDF to the user
        with open(output_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="situation_client_{client_ref}.pdf"'

        # Automatically open the PDF on Windows
        if os.name == 'nt':
            os.startfile(output_path)

        return redirect('situation_client')

    context = {
        'factures': factures,
        'client_ref': client_ref,
        'client_name': client_name,

    }
    return render(request, 'Application/generer_situation_client.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def situation_client(request):
    query = request.GET.get('q')
    if query:
        factures = Commande.objects.filter(company_reference_number=query, facture_status='facture_termine', remarque='non payé')
        # Debugging: Print each facture to verify filtering
        print(f"Query: {query}")
        print(f"Number of factures found: {factures.count()}")
        for facture in factures:
            print(f"Facture: {facture.order_id}, Client: {facture.client_name}, Status: {facture.facture_status}, Remark: {facture.remarque}")
    else:
        factures = Commande.objects.none()

    context = {
        'query': query,
        'factures': factures,
    }
    return render(request, 'Application/situation_client.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Assistants').exists())
def ajouter_commande(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save(commit=False)
            commande.order_status = 'draft'
            commande.save()
            log_action(request.user, 'add', commande)
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
        if 'permanent' in request.POST:
            facture.delete()
        else:
            facture.facture_numero = None
            facture.facture_status = 'no_facture'
            facture.remarque = 'non payé'
            facture.save()
        return redirect('liste_factures')
    return render(request, 'Application/supprimer_facture.html', {'facture': facture})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def supprimer_devis(request, pk):
    devis = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        if 'permanent' in request.POST:
            devis.delete()
        else:
            devis.devis_numero = None
            devis.devis_status = 'no_devis'
            devis.save()
        return redirect('liste_devis')
    return render(request, 'Application/supprimer_devis.html', {'devis': devis})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def supprimer_bl(request, pk):
    bon_livraison = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        if 'permanent' in request.POST:
            bon_livraison.delete()
        else:
            bon_livraison.bl_numero = None
            bon_livraison.bl_status = 'no_bl'
            bon_livraison.save()
        return redirect('liste_bon_livraison')
    return render(request, 'Application/supprimer_bl.html', {'bon_livraison': bon_livraison})

@login_required
def modifier_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    log_action(request.user, 'modify', commande)
    return redirect('designation_commande', pk=commande.pk)


def draw_background(c, image_path, width, height):
    c.drawImage(image_path, 0, 0, width=width, height=height)

def create_devis_pdf(output_path, commande, date, total_ht, tva_20, total_ttc, background_image_url, second_background_image_url):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Define custom styles
    large_bold_font = ParagraphStyle('LargeBoldFont', parent=styles['Normal'], fontSize=14, fontName="Helvetica-Bold")
    normal_font = ParagraphStyle('NormalFont', parent=styles['Normal'], fontName="Helvetica", alignment=1)
    bold_font = ParagraphStyle('BoldFont', parent=styles['Normal'], fontName="Helvetica-Bold", alignment=1)
    table_header_font = ParagraphStyle('TableHeaderFont', parent=styles['Normal'], fontSize=12, fontName="Helvetica-Bold", alignment=1)

    width, height = A4

    # Header information
    header = [
        ["", f"Rabat, le {date}"],
    ]
    table_header = Table(header, colWidths=[14 * cm, 5 * cm])
    table_header.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 14),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(Spacer(1, 5 * cm))  # Move the content down by 5 cm from the top
    elements.append(table_header)
    elements.append(Spacer(1, 12))

    # Info section
    info = [
        f"Devis N°{commande.devis_numero}/{date[-2:]}",
        f"{commande.client_name}",
        f"{commande.ice}"
    ]
    elements.append(Paragraph(info[0], large_bold_font))
    elements.append(Spacer(1, 2))

    # Separator exactly under "Devis"
    separator = Table([[""]], colWidths=[5 * cm])
    separator.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black)
    ]))
    elements.append(separator)
    elements.append(Spacer(1, 12))

    for line in info[1:]:
        elements.append(Paragraph(line, large_bold_font))

    elements.append(Spacer(1, 12))

    # Prepare data for the table
    data = [
        [Paragraph("Article", table_header_font), 
         Paragraph("Designations", table_header_font), 
         Paragraph("QTE", table_header_font), 
         Paragraph("P.U H.T", table_header_font), 
         Paragraph("P.T H.T", table_header_font)]
    ]
    article_counter = 1

    for designation in commande.designations.all():
        for option in designation.options.all():
            characteristics = []
            if option.format:
                characteristics.append(option.format)
            if option.paper_type:
                characteristics.append(option.paper_type)
            if option.paragraph:
                characteristics.append(option.paragraph)
            if option.grammage:
                characteristics.append(option.grammage)
            if option.recto_verso:
                characteristics.append(option.recto_verso)
            if option.pelliculage_mat:
                characteristics.append("Pelliculage Mat")
            if option.pelliculage_brillant:
                characteristics.append("Pelliculage Brillant")
            if option.spiral:
                characteristics.append("Spiral")
            if option.piquage:
                characteristics.append("Piquage")
            if option.collage:
                characteristics.append("Collage")
            if option.cousu:
                characteristics.append("Cousu")
            characteristics_str = " * ".join(characteristics)
            data.append([
                str(article_counter),
                Paragraph(f"* {option.option_name} * {characteristics_str}", normal_font),
                option.quantity,
                f"{option.unit_price:.2f}",
                f"{(option.unit_price * option.quantity):.2f}"
            ])
            article_counter += 1

    # Create the main table
    table = Table(data, colWidths=[2.5 * cm, 9 * cm, 2 * cm, 2.5 * cm, 2.5 * cm], repeatRows=1)
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEADING', (0, 0), (-1, -1), 35),  # Increase row height
    ])
    table.setStyle(style)

    # Center the table with 4 cm on the right side
    elements.append(Spacer(1, 1 * cm))
    elements.append(table)
    elements.append(Spacer(1, 1 * cm))

    # Table for TOTAL HT, TVA, TOTAL TTC
    summary_data = [
        [Paragraph("TOTAL HT", bold_font), Paragraph("TVA 20%", bold_font), Paragraph("TOTAL TTC", bold_font)],
        [f"{total_ht:.2f}", f"{tva_20:.2f}", f"{total_ttc:.2f}"]
    ]
    summary_table = Table(summary_data, colWidths=[6.33 * cm, 6.33 * cm, 6.33 * cm])
    summary_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    summary_table.setStyle(summary_style)

    elements.append(summary_table)

    def on_first_page(canvas, doc):
        draw_background(canvas, background_image_url, *A4)

    def on_later_pages(canvas, doc):
        draw_background(canvas, second_background_image_url, *A4)
        canvas.saveState()
        canvas.translate(0, -5 * cm)  # Move content up by 4 cm
        canvas.restoreState()

    # Build the PDF
    doc.build(elements, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def generer_devis(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    date = datetime.now().strftime('%d/%m/%y')

    if request.method == 'POST':
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')
        print(quantities, unit_prices)  # Ajoutez cette ligne pour vérifier les valeurs
        total_prices = []
        

        if not commande.devis_numero:
            last_devis = Commande.objects.exclude(devis_numero=None).order_by('-devis_numero').first()
            if last_devis:
                commande.devis_numero = last_devis.devis_numero + 1
            else:
                commande.devis_numero = 1

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

        commande.devis_status = 'devis_termine'
        commande.devis_date = datetime.now()  # Set the devis date
        commande.save()

       

        output_path = os.path.join(settings.MEDIA_ROOT, f"devis_{commande.devis_numero}.pdf")
        background_image_url = os.path.join(settings.STATIC_ROOT, 'images/devis.png')
        second_background_image_url = os.path.join(settings.STATIC_ROOT, 'images/fa.jpg')
        create_devis_pdf(output_path, commande, date, total_ht, tva_20, total_ttc, background_image_url, second_background_image_url)

        # Serve the PDF to the user
        with open(output_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="devis_{commande.devis_numero}.pdf"'

        # Automatically open the PDF on Windows
        if os.name == 'nt':
            os.startfile(output_path)


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
@login_required
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

def create_dossier_travail_pdf(output_path, html_content):
    HTML(string=html_content).write_pdf(output_path)

def designation_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    date = datetime.now().strftime('%d/%m/%y')

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
        article_counter = 1
        logo_url = request.build_absolute_uri(static('images/logo.png'))
        output_path = os.path.join(settings.MEDIA_ROOT, f"dossier_travail_{commande.order_id}.pdf")
        html_content = render_to_string('Application/dossier_travail_template.html', {'commande': commande, 'date': date, 'logo_url': logo_url, 'article_counter': article_counter})
        create_dossier_travail_pdf(output_path, html_content)

        # Serve the PDF to the user
        with open(output_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="dossier_travail_{commande.order_id}.pdf"'

        # Automatically open the PDF on Windows
        if os.name == 'nt':
            os.startfile(output_path)

        return redirect('liste_commandes')

    return render(request, 'Application/designation_commande.html', {'commande': commande})

def create_facture_pdf(output_path, commande, date, total_ht, tva_20, total_ttc, bc_number, date_bc, background_image_url, second_background_image_url):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Define custom styles
    large_bold_font = ParagraphStyle('LargeBoldFont', parent=styles['Normal'], fontSize=14, fontName="Helvetica-Bold")
    normal_font = ParagraphStyle('NormalFont', parent=styles['Normal'], fontName="Helvetica", alignment=1)
    bold_font = ParagraphStyle('BoldFont', parent=styles['Normal'], fontName="Helvetica-Bold", alignment=1)
    table_header_font = ParagraphStyle('TableHeaderFont', parent=styles['Normal'], fontSize=12, fontName="Helvetica-Bold", alignment=1)

    width, height = A4

    # Header information
    header = [
        ["", f"Rabat, le {date}"],
    ]
    table_header = Table(header, colWidths=[14 * cm, 5 * cm])
    table_header.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 14),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(Spacer(1, 5 * cm))  # Move the content down by 5 cm from the top
    elements.append(table_header)
    elements.append(Spacer(1, 12))

    info = [
        f"Facture N°{commande.facture_numero}/{date[-2:]}",  # Utilisation de l'année sur deux chiffres
        f"{commande.client_name}",
        f"{commande.ice}",
        f"BC N° : {bc_number}",
        f"Date BC : {date_bc}"
    ]
    elements.append(Paragraph(info[0], large_bold_font))
    elements.append(Spacer(1, 2))

    # Separator exactly under "Facture"
    separator = Table([[""]], colWidths=[5 * cm])
    separator.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black)
    ]))
    elements.append(separator)
    elements.append(Spacer(1, 12))

    for line in info[1:]:
        elements.append(Paragraph(line, large_bold_font))

    elements.append(Spacer(1, 12))

    # Prepare data for the table
    data = [
        [Paragraph("Article", table_header_font), 
         Paragraph("Designations", table_header_font), 
         Paragraph("QTE", table_header_font), 
         Paragraph("P.U H.T", table_header_font), 
         Paragraph("P.T H.T", table_header_font)]
    ]
    article_counter = 1

    for designation in commande.designations.all():
        for option in designation.options.all():
            characteristics = []
            if option.format:
                characteristics.append(option.format)
            if option.paper_type:
                characteristics.append(option.paper_type)
            if option.paragraph:
                characteristics.append(option.paragraph)
            if option.grammage:
                characteristics.append(option.grammage)
            if option.recto_verso:
                characteristics.append(option.recto_verso)
            if option.pelliculage_mat:
                characteristics.append("Pelliculage Mat")
            if option.pelliculage_brillant:
                characteristics.append("Pelliculage Brillant")
            if option.spiral:
                characteristics.append("Spiral")
            if option.piquage:
                characteristics.append("Piquage")
            if option.collage:
                characteristics.append("Collage")
            if option.cousu:
                characteristics.append("Cousu")
            characteristics_str = " * ".join(characteristics)
            data.append([
                str(article_counter),
                Paragraph(f"* {option.option_name} * {characteristics_str}", normal_font),
                option.quantity,
                f"{option.unit_price:.2f}",
                f"{(option.unit_price * option.quantity):.2f}"
            ])
            article_counter += 1

    # Create the main table
    table = Table(data, colWidths=[2.5 * cm, 9 * cm, 2 * cm, 2.5 * cm, 2.5 * cm], repeatRows=1)
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEADING', (0, 0), (-1, -1), 35),  # Increase row height
    ])
    table.setStyle(style)

    # Center the table with 4 cm on the right side
    elements.append(Spacer(1, 1 * cm))
    elements.append(table)
    elements.append(Spacer(1, 1 * cm))

    # Table for TOTAL HT, TVA, TOTAL TTC
    summary_data = [
        [Paragraph("TOTAL HT", bold_font), Paragraph("TVA 20%", bold_font), Paragraph("TOTAL TTC", bold_font)],
        [f"{total_ht:.2f}", f"{tva_20:.2f}", f"{total_ttc:.2f}"]
    ]
    summary_table = Table(summary_data, colWidths=[6.33 * cm, 6.33 * cm, 6.33 * cm])
    summary_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    summary_table.setStyle(summary_style)

    elements.append(summary_table)

    def on_first_page(canvas, doc):
        draw_background(canvas, background_image_url, *A4)

    def on_later_pages(canvas, doc):
        draw_background(canvas, second_background_image_url, *A4)
        canvas.saveState()
        canvas.translate(0, -5 * cm)  # Move content up by 4 cm
        canvas.restoreState()

    # Build the PDF
    doc.build(elements, onFirstPage=on_first_page, onLaterPages=on_later_pages)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def generer_facture(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    date = datetime.now().strftime('%d/%m/%y')

    if request.method == 'POST':
        quantities = request.POST.getlist('quantity[]')
        bc_number = request.POST.get('bc_number')
        date_bc = request.POST.get('date_bc')

    # Automatically assign a facture number if not already assigned
    if not commande.facture_numero:
        last_facture = Commande.objects.exclude(facture_numero=None).order_by('-facture_numero').first()
        if last_facture:
            commande.facture_numero = last_facture.facture_numero + 1
        else:
            commande.facture_numero = 1
    
    total_ht = Decimal('0.00')  # Initialize total_ht
    for designation in commande.designations.all():
        for option in designation.options.all():
            if option.unit_price is not None:
                total_ht += option.unit_price * option.quantity

    tva_20 = total_ht * Decimal('0.20')
    total_ttc = total_ht + tva_20

    if request.method == 'POST':
        commande.facture_status = 'facture_termine'
        commande.facture_date = datetime.now()  # Set the facture date
        commande.bc_number = bc_number
        commande.date_bc = date_bc
        commande.save()

        # Generate the PDF using ReportLab
        output_path = os.path.join(settings.MEDIA_ROOT, f"facture_{commande.facture_numero}.pdf")
        background_image_url = os.path.join(settings.STATIC_ROOT, 'images/devis.png')
        second_background_image_url = os.path.join(settings.STATIC_ROOT, 'images/fa.jpg')
        create_facture_pdf(output_path, commande, date, total_ht, tva_20, total_ttc, bc_number, date_bc, background_image_url, second_background_image_url)

        # Serve the PDF to the user
        with open(output_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="facture_{commande.facture_numero}.pdf"'

        # Automatically open the PDF on Windows
        if os.name == 'nt':
            os.startfile(output_path)

        return redirect('liste_factures')

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

def create_bon_livraison_pdf(output_path, commande, date, background_image_url, second_background_image_url, selected_options):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Define custom styles
    large_bold_font = ParagraphStyle('LargeBoldFont', parent=styles['Normal'], fontSize=14, fontName="Helvetica-Bold")
    normal_font = ParagraphStyle('NormalFont', parent=styles['Normal'], fontName="Helvetica", alignment=1)
    bold_font = ParagraphStyle('BoldFont', parent=styles['Normal'], fontName="Helvetica-Bold", alignment=1)
    table_header_font = ParagraphStyle('TableHeaderFont', parent=styles['Normal'], fontSize=12, fontName="Helvetica-Bold", alignment=1)

    width, height = A4

    # Header information
    header = [
        ["", f"Rabat, le {date}"],
    ]
    table_header = Table(header, colWidths=[14 * cm, 5 * cm])
    table_header.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 14),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(Spacer(1, 5 * cm))  # Move the content down by 5 cm from the top
    elements.append(table_header)
    elements.append(Spacer(1, 12))

    # Info section
    info = [
        f"Bon de Livraison N°{commande.bl_numero}/{date[-2:]}",
        f"{commande.client_name}",
        f"{commande.ice}"
    ]
    elements.append(Paragraph(info[0], large_bold_font))
    elements.append(Spacer(1, 2))

    # Separator exactly under "Bon de Livraison"
    separator = Table([[""]], colWidths=[5 * cm])
    separator.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black)
    ]))
    elements.append(separator)
    elements.append(Spacer(1, 12))

    for line in info[1:]:
        elements.append(Paragraph(line, large_bold_font))

    elements.append(Spacer(1, 12))

    # Prepare data for the table
    data = [
        [Paragraph("Article", table_header_font), 
         Paragraph("Designations", table_header_font), 
         Paragraph("QTE", table_header_font)]
    ]
    article_counter = 1

    for option in selected_options:
        characteristics = []
        if option.format:
            characteristics.append(option.format)
        if option.paper_type:
            characteristics.append(option.paper_type)
        if option.paragraph:
            characteristics.append(option.paragraph)
        if option.grammage:
            characteristics.append(option.grammage)
        if option.recto_verso:
            characteristics.append(option.recto_verso)
        if option.pelliculage_mat:
            characteristics.append("Pelliculage Mat")
        if option.pelliculage_brillant:
            characteristics.append("Pelliculage Brillant")
        if option.spiral:
            characteristics.append("Spiral")
        if option.piquage:
            characteristics.append("Piquage")
        if option.collage:
            characteristics.append("Collage")
        if option.cousu:
            characteristics.append("Cousu")
        characteristics_str = " * ".join(characteristics)
        data.append([
            str(article_counter),
            Paragraph(f"* {option.option_name} * {characteristics_str}", normal_font),
            option.quantity
        ])
        article_counter += 1

    # Create the main table
    table = Table(data, colWidths=[2.5 * cm, 9 * cm, 2 * cm], repeatRows=1)
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEADING', (0, 0), (-1, -1), 35),  # Increase row height
    ])
    table.setStyle(style)

    elements.append(Spacer(1, 1 * cm))
    elements.append(table)
    elements.append(Spacer(1, 1 * cm))

    def on_first_page(canvas, doc):
        draw_background(canvas, background_image_url, *A4)

    def on_later_pages(canvas, doc):
        draw_background(canvas, second_background_image_url, *A4)
        canvas.saveState()
        canvas.translate(0, -5 * cm)  # Move content up by 5 cm
        canvas.restoreState()

    # Build the PDF
    doc.build(elements, onFirstPage=on_first_page, onLaterPages=on_later_pages)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def generer_bon_livraison(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    date = datetime.now().strftime('%d/%m/%y')
    selected_options = []

    if request.method == 'POST':
        quantities = request.POST.getlist('quantity[]')

        selected_commandes_ids = request.POST.getlist('selected_commandes')
        if selected_commandes_ids:
            selected_options = Option.objects.filter(id__in=selected_commandes_ids)

        # Automatically assign a BL number if not already assigned
        if not commande.bl_numero:
            last_bl = Commande.objects.exclude(bl_numero=None).order_by('-bl_numero').first()
            new_bl_numero = last_bl.bl_numero + 1 if last_bl else 1
            commande.bl_numero = new_bl_numero
        else:
            new_bl_numero = commande.bl_numero

        commande.bl_status = 'bl_termine'
        commande.bl_date = datetime.now()  # Set the BL date
        commande.save()

        # Generate the PDF using ReportLab
        output_path = os.path.join(settings.MEDIA_ROOT, f"bon_livraison_{commande.bl_numero}.pdf")
        background_image_url = os.path.join(settings.STATIC_ROOT, 'images/devis.png')
        second_background_image_url = os.path.join(settings.STATIC_ROOT, 'images/fa.jpg')
        create_bon_livraison_pdf(output_path, commande, date, background_image_url, second_background_image_url, selected_options)

        # Serve the PDF to the user
        with open(output_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="bon_livraison_{commande.bl_numero}.pdf"'

        # Automatically open the PDF on Windows
        if os.name == 'nt':
            os.startfile(output_path)

        return redirect('liste_bon_livraison')

    return render(request, 'Application/generer_bon_livraison.html', {
        'commande': commande,
        'selected_commandes': selected_options
    })

@login_required
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
def log_view(request):
    logs = LogEntry.objects.all().order_by('-timestamp')
    context = {
        'logs': logs
    }
    return render(request, 'Application/log_view.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Directeurs').exists())
def clear_log(request):
    if request.method == 'POST':
        LogEntry.objects.all().delete()
    return redirect('log_view')
