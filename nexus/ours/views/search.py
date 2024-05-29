from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from elasticsearch_dsl.query import MultiMatch, Match
from elasticsearch_dsl import Q

import json
from random import randint
import requests
from bs4 import BeautifulSoup

from core.views import restrict_to_http_methods, restrict_to_groups

from ..models import (
    Opportunity,
    MinGPARestriction,
    MajorRestriction,
    CitizenshipRestriction,
    StudyLevelRestriction,
    Keyword,
)

import datetime

from ..documents import OpportunityDocument, KeywordDocument

@login_required
@restrict_to_http_methods('GET', 'POST')
def opportunity_search(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '')
        if len(search_query) == 0:
            return redirect('search_no_result')
        # result_opp = Opportunity.objects.filter(title__icontains=search_query).values_list('id', flat=True)
        # result_opp = OpportunityDocument.search().query(MultiMatch(query=search_query))
        result_opp = OpportunityDocument.search().extra(size=1000).query(
            (Q(MultiMatch(query=search_query, fuzziness='AUTO')) |
            Q('nested', path='keywords', query=MultiMatch(query=search_query, fields=['keywords.keyword'], fuzziness='AUTO'))) &
            Q(Match(active=True))
        ).execute()
        result_opp = [(opp.meta.id, opp.meta.score) for opp in result_opp]
        sorted_result_opp = sorted(result_opp, key=lambda x: x[1], reverse=True)
        print(sorted_result_opp[0][1], sorted_result_opp[-1][1])
        result_opp = [opp[0] for opp in sorted_result_opp if opp[1] > 0]
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
    # keywords = [keyword.meta.id for keyword in KeywordDocument.search().query(MultiMatch(query=query)).scan()]
    count = Keyword.objects.count()
    random_ints = [randint(0, count - 1) for _ in range(10)]
    keywords = Keyword.objects.filter(id__in=random_ints)[:5]
    context = {
        'query': query,
        'num_results': num_results,
        'keywords': keywords,
    }
    response = render(request, 'search_no_result.html', context)
    response['HX-Trigger-After-Settle'] = json.dumps({"noResult": ""})
    return response

@login_required
@restrict_to_http_methods('GET')
def opportunity_card(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    opportunity.check_link()
    context = {'opportunity': opportunity}
    return render(request, 'opportunity_card.html', context)