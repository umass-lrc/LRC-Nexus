from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from urllib.parse import parse_qs

from elasticsearch_dsl.query import MultiMatch, Match
from elasticsearch_dsl import Q

import json
from random import randint

from core.views import restrict_to_http_methods, restrict_to_groups

from ours.models import (
    Opportunity,
    MinGPARestriction,
    MajorRestriction,
    CitizenshipRestriction,
    StudyLevelRestriction,
    Keyword,
)

from ours.documents import OpportunityDocument

@csrf_exempt
@restrict_to_http_methods('GET', 'POST')
def opportunity_search(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        if len(body_unicode) < 13:
            return search_no_result(request, search_query, 0)
        body = parse_qs(body_unicode, strict_parsing=True)
        search_query = body['search_query'][0] if 'search_query' in body else ""
        result_opp = OpportunityDocument.search().extra(size=1000).query(
            (Q(MultiMatch(query=search_query)) |
            Q('nested', path='keywords', query=MultiMatch(query=search_query, fields=['keywords.keyword'], fuzziness='AUTO'))) &
            Q(Match(active=True)) & (Q(Match(show_on_website=True)) & Q('range', show_on_website_start_date={'lte': 'now/d'}) & Q('range', show_on_website_end_date={'gte': 'now/d'}))
        ).execute()
        result_opp = [(opp.meta.id, opp.meta.score) for opp in result_opp]
        sorted_result_opp = sorted(result_opp, key=lambda x: x[1], reverse=True)
        result_opp = [opp[0] for opp in sorted_result_opp]
        num_results = len(result_opp)
        if num_results == 0:
            return search_no_result(request, search_query, num_results)
        context = {
            'query': search_query,
            'num_results': num_results,
            'result_opp': result_opp,
        }
        return render(request, 'api_search_results.html', context)
    return render(request, 'api_search_base.html')

@csrf_exempt
@restrict_to_http_methods('GET', 'POST')
def search_no_result(request, query="", num_results=0):
    count = Keyword.objects.count()
    random_ints = [randint(0, count - 1) for _ in range(10)]
    keywords = Keyword.objects.filter(id__in=random_ints)[:5]
    context = {
        'keywords': keywords,
        'query': query,
        'num_results': num_results,
    }
    return render(request, 'search_no_result.html', context)

@restrict_to_http_methods('GET')
def opportunity_card(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    context = {'opportunity': opportunity}
    return render(request, 'api_opportunity_card.html', context)

@restrict_to_http_methods('GET')
def opportunity_details(request, opp_id):
    print("Opportunity details")
    opportunity = Opportunity.objects.get(id=opp_id)
    keywords = [obj.keyword for obj in opportunity.keywords.all()]
    rtm = [obj.major for obj in opportunity.related_to_major.all()]
    rtt = [obj.track for obj in opportunity.related_to_track.all()]
    restrictions = {}
    min_gpa = MinGPARestriction.objects.filter(opportunity=opportunity).first()
    if min_gpa and min_gpa.gpa is not None:
        restrictions['min_gpa'] = min_gpa.gpa
    major_restriction = MajorRestriction.objects.filter(opportunity=opportunity).first()
    if major_restriction and major_restriction.majors.count() > 0:
        restrictions['restricted_majors'] = ', '.join([obj.major for obj in major_restriction.majors.all()])
        restrictions['require_all_majors'] = major_restriction.must_be_all_majors
    citizenship_restriction = CitizenshipRestriction.objects.filter(opportunity=opportunity).first()
    if citizenship_restriction and citizenship_restriction.citizenship_status.count() > 0:
        restrictions['restricted_to_citizenship_status'] = ', '.join([obj.citizenship_status for obj in citizenship_restriction.citizenship_status.all()])
    study_level_restriction = StudyLevelRestriction.objects.filter(opportunity=opportunity).first()
    if study_level_restriction and study_level_restriction.study_level.count() > 0:
        restrictions['restricted_to_study_level'] = ', '.join([obj.study_level for obj in study_level_restriction.study_level.all()])
    context = {'opportunity': opportunity, 'keywords': keywords, 'rtm': rtm, 'rtt': rtt, 'restrictions': restrictions}
    response = render(request, 'api_opportunity_details.html', context)
    response["HX-Trigger-After-Settle"] = json.dumps({"viewClicked": f"ot-{opportunity.id}"})
    return response