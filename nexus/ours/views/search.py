from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from elasticsearch_dsl.query import MultiMatch

import json

from core.views import restrict_to_http_methods, restrict_to_groups

from ..models import (
    Opportunity,
    MinGPARestriction,
    MajorRestriction,
    CitizenshipRestriction,
    StudyLevelRestriction,
)

from ..documents import OpportunityDocument

@login_required
@restrict_to_http_methods('GET', 'POST')
def opportunity_search(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '')
        if len(search_query) == 0:
            return redirect('search_no_result')
        # result_opp = Opportunity.objects.filter(title__icontains=search_query).values_list('id', flat=True)
        result_opp = OpportunityDocument.search().query(MultiMatch(query=search_query))
        result_opp = [opp.meta.id for opp in result_opp]
        num_results = len(result_opp)
        if num_results == 0:
            return search_no_result(request, search_query, num_results)
        context = {
            'query': search_query,
            'num_results': num_results,
            'result_opp': result_opp,
        }
        return render(request, 'search_result.html', context)
    return render(request, 'search_base.html')

@login_required
@restrict_to_http_methods('GET', 'POST')
def search_no_result(request, query="", num_results=0):
    context = {
        'query': query,
        'num_results': num_results,
    }
    response = render(request, 'search_no_result.html', context)
    response['HX-Trigger-After-Settle'] = json.dumps({"noResult": ""})
    return response

@login_required
@restrict_to_http_methods('GET')
def opportunity_card(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    context = {'opportunity': opportunity}
    return render(request, 'opportunity_card.html', context)