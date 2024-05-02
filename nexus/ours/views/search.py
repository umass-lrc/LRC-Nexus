from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import json

from core.views import restrict_to_http_methods, restrict_to_groups

from ..models import (
    Opportunity,
    MinGPARestriction,
    MajorRestriction,
    CitizenshipRestriction,
    StudyLevelRestriction,
)

@login_required
@restrict_to_http_methods('GET', 'POST')
def opportunity_search(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '')
        if len(search_query) == 0:
            return redirect('search_no_result')
        result_opp = Opportunity.objects.filter(title__icontains=search_query).values_list('id', flat=True)
        if result_opp.count() == 0:
            return redirect('search_no_result')
        context = {
            'search_query': search_query,
            'num_results': result_opp.count(),
            'result_opp': result_opp,
        }
        return render(request, 'search_result.html', context)
    return render(request, 'search_base.html')

@login_required
@restrict_to_http_methods('GET')
def search_no_result(request):
    response = render(request, 'search_no_result.html')
    response['HX-Trigger-After-Settle'] = json.dumps({"noResult": ""})
    return response

@login_required
@restrict_to_http_methods('GET')
def opportunity_card(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    context = {'opportunity': opportunity}
    return render(request, 'opportunity_card.html', context)