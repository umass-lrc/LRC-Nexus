from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import json

from core.views import restrict_to_http_methods, restrict_to_groups

from ..models import (
    Opportunity,
)

from ..forms.opportunity import CreateOpportunityForm

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor')
def opportunities_list(request):
    opportunities = Opportunity.objects.all().values_list('id', flat=True)
    context = {
        'opportunities': opportunities,
    }
    return render(request, 'opportunities_list.html', context)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor')
def get_opportunity_row(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    context = {'opportunity': opportunity}
    return render(request, 'opportunity_row.html', context)

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'OURS Supervisor')
def update_opportunity(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    if request.method == 'POST':
        form = CreateOpportunityForm(request.POST, instance=opportunity)
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
        else:
            form.save()
            messages.success(request, 'Opportunity updated successfully.')
        context = {'success': True, 'opportunity': opportunity}
        return render(request, 'update_opportunity.html', context)
    context = {'success':False, 'opportunity': opportunity}
    response = render(request, 'update_opportunity.html', context)
    response["HX-Trigger-After-Settle"] = json.dumps({"updateClicked": f"ot-{opportunity.id}"})
    return response

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'SI Supervisor', 'Tutor Supervisor', 'OURS Supervisor')
def update_opportunity_form(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    form = CreateOpportunityForm(instance=opportunity)
    context = {'form': form}
    return render(request, 'just_form_with_media.html', context)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor')
def view_opportunity(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    keywords = ','.join(map( str, opportunity.keywords.all()))
    keywords = 'None' if len(keywords) == 0 else keywords
    rtm = ', '.join(map( str, opportunity.related_to_major.all()))
    rtm = 'None' if len(rtm) == 0 else rtm
    rtt = ', '.join(map( str, opportunity.related_to_track.all()))
    rtt = 'None' if len(rtt) == 0 else rtt
    context = {'opportunity': opportunity, 'keywords': keywords, 'rtm': rtm, 'rtt': rtt}
    response = render(request, 'opportunity_details.html', context)
    response["HX-Trigger-After-Settle"] = json.dumps({"viewClicked": f"ot-{opportunity.id}"})
    return response

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'SI Supervisor', 'Tutor Supervisor', 'OURS Supervisor')
def create_opportunity_form(request):
    if request.method == 'POST':
        form = CreateOpportunityForm(request.POST)
        success = False
        if form.is_valid():
            form.save()
            success = True
            messages.success(request, 'Opportunity created successfully.')
        else:
            messages.error(request, f'Form Errors: {form.errors}')
        context = {'success': success}
        return render(request, 'create_opportunity_message.html', context)
    form = CreateOpportunityForm()
    context = {'form': form}
    return render(request, 'just_form_with_media.html', context)