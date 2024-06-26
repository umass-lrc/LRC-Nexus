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
    link_override = opportunity.link_not_working_override
    location_check = opportunity.on_campus or (opportunity.location is not None and len(opportunity.location.strip()) > 0)
    
    context = {
        'opportunity': opportunity,
        'featured': opportunity.featured,
        'short_desc': 'success' if short_desc_check else 'danger',
        'short_desc_len': len(opportunity.short_description.strip().split()),
        'long_desc': ('success' if not long_desc_warning else 'warning') if long_desc_check else 'danger',
        'long_desc_len': len(opportunity.description.strip().split()),
        'link': 'warning' if link_override else 'success' if link_check else 'danger',
        'location': 'success' if location_check else 'danger',
        'keywords': 'success' if opportunity.keywords.count() > 0 else 'danger',
        'keywords_count': opportunity.keywords.count(),
        'majors': 'success' if opportunity.related_to_major.count() > 0 else 'danger',
        'majors_count': opportunity.related_to_major.count(),
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
def check_opportunity_link_with_progress_bar(request, opp_id, max_id):
    try:
        opportunity = Opportunity.objects.get(id=opp_id)
        opportunity.check_link()
    except:
        pass
    if opp_id == max_id:
        return render(request, 'check_opp_check_link_form.html')
    context = {
        'label': f'Checking Opportunity: {opp_id+1}/{max_id+1}',
        'percentage': round((opp_id / max_id) * 100),
        'next_url': 'check_opportunity_link_with_progress_bar',
        'next_index': opp_id + 1,
        'max_id': max_id,
    }
    return render(request, 'check_opp_progress_bar.html', context)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def check_all_opportunity_links(request):
    max_id = Opportunity.objects.latest('id').id
    return redirect('check_opportunity_link_with_progress_bar', opp_id=0, max_id=max_id)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def update_web_data(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    opportunity.link_not_working = True
    opportunity.website_data = ''
    opportunity.save()
    opportunity.check_link()
    return redirect('check_opp_row', opp_id=opp_id)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def update_web_data_with_progress_bar(request, opp_id, max_id):
    try:
        opportunity = Opportunity.objects.get(id=opp_id)
        opportunity.link_not_working = True
        opportunity.website_data = ''
        opportunity.save()
        opportunity.check_link()
    except:
        pass
    if opp_id == max_id:
        return render(request, 'check_opp_update_web_data_form.html')
    context = {
        'label': f'Updating Opportunity: {opp_id+1}/{max_id+1}',
        'percentage': round((opp_id / max_id) * 100),
        'next_url': 'update_web_data_with_progress_bar',
        'next_index': opp_id + 1,
        'max_id': max_id,
    }
    return render(request, 'check_opp_progress_bar.html', context)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def update_all_web_data(request):
    max_id = Opportunity.objects.latest('id').id
    return redirect('update_web_data_with_progress_bar', opp_id=0, max_id=max_id)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def change_link_override(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    opportunity.link_not_working_override = not opportunity.link_not_working_override
    opportunity.save()
    return redirect('check_opp_row', opp_id=opp_id)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def change_featured(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    opportunity.featured = not opportunity.featured
    opportunity.save()
    return redirect('check_opp_row', opp_id=opp_id)