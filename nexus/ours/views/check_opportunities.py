from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

import json
from dal import autocomplete
import requests
from urllib.parse import urlparse

from core.views import restrict_to_http_methods, restrict_to_groups

from ..models import (
    Opportunity,
    MinGPARestriction,
    MajorRestriction,
    CitizenshipRestriction,
    StudyLevelRestriction,
    Keyword,
)

from .opportunities import (
    update_opportunity,
    update_opportunity_form,
)

from ..forms.opportunity import CreateOpportunityForm, SimpleSearchForm

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def check_opp_main(request):
    opportunities = Opportunity.objects.all()
    opp_id = opportunities.values_list('id', flat=True)
    context = {
        'opportunities': opp_id,
        'form': SimpleSearchForm(),
    }
    return render(request, 'check_opp_main.html', context)

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def check_opp_row(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    
    short_desc_check = len(opportunity.short_description.strip()) > 0
    long_desc_check = len(opportunity.description.strip()) > 0
    long_desc_warning = len(opportunity.description.strip()) <= len(opportunity.short_description.strip())
    link_check = not opportunity.link_not_working
    location_check = opportunity.on_campus or (opportunity.location is not None and len(opportunity.location.strip()) > 0)
    
    context = {
        'opportunity': opportunity,
        'short_desc': 'success' if short_desc_check else 'danger',
        'long_desc': ('success' if not long_desc_warning else 'warning') if long_desc_check else 'danger',
        'link': 'success' if link_check else 'danger',
        'location': 'success' if location_check else 'danger',
    }
    return render(request, 'check_opp_row.html', context)

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def check_opp_update_opportunity(request, opp_id):
    return update_opportunity(request, opp_id, check_opportunity=True)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def check_opp_update_opportunity_form(request, opp_id):
    return update_opportunity_form(request, opp_id, check_opportunity=True)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def check_opportunity_link(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    opportunity.check_link()
    return redirect('check_opp_row', opp_id=opp_id)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def check_all_opportunity_links(request):
    opportunities = Opportunity.objects.all()
    for i, opportunity in enumerate(opportunities):
        opportunity.check_link()
    return redirect('check_opp_main')

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def update_web_data(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    netloc = urlparse(opportunity.link).netloc
    status = netloc not in ['lrcstaff.umass.edu', 'localhost:8000', '127.0.0.1:8000']
    req = requests.get(opportunity.link) if status else None
    status = status and req.status_code == 200
    if status:
        opportunity.link_not_working = False
        opportunity.website_data = '\n'.join([line for line in req.text.split('\n') if line.strip() != ''])
    if not status:
        opportunity.link_not_working = True
        opportunity.website_data = ''
    opportunity.save()
    return redirect('check_opp_row', opp_id=opp_id)