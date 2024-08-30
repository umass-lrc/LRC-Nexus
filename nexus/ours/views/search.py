from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from elasticsearch_dsl.query import MultiMatch, Match, MatchPhrase
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

def divide_query(search_query):
    search_query = search_query.strip()
    search_query_list = []
    i = 0
    while i < len(search_query):
        if search_query[i] == '"':
            start = i
            i += 1
            while i < len(search_query) and search_query[i] != '"':
                i += 1
            query = search_query[start + 1:i].strip()
            if len(query) > 0:
                search_query_list.append((2, search_query[start + 1:i]))
            i += 1
        elif search_query[i] == ' ':
            i += 1
        else:
            start = i
            while i < len(search_query) and search_query[i] != ' ':
                i += 1
            query = search_query[start:i]
            search_query_list.append((1 if query in ["AND", "OR"] else 0, query))
    
    return search_query_list

def interval_query_per_field(query_list, field_name):
    return Q('intervals', **{field_name: {'all_of': {'ordered': 'true', 'intervals': [{'fuzzy': {'term': query}} for query in query_list]}}})

def make_query_from_list(search_query_list):
    es_query = None
    new_query = None
    opp = 'AND'
    i = 0
    while i < len(search_query_list):
        print(i)
        type, query = search_query_list[i]
        if type == 0:
            query_list = [query]
            i += 1
            while i < len(search_query_list) and search_query_list[i][0] == 0:
                query_list.append(search_query_list[i][1])
                i += 1
            new_query = None
            if len(query_list) == 1:
                new_query = Q('bool', should = [Q(MultiMatch(
                    query=query_list[0],
                    type="most_fields", 
                    fields=[
                        'title^5',
                        'short_description^3',
                        'description^2',
                        'website_data',
                        'additional_information',
                        'location^5'
                    ],
                    fuzziness='AUTO'
                    )), Q(
                        'nested',
                        path='keywords',
                        query=Match(keyword=query_list[0])
                    )],
                    minimum_should_match=1,
                    boost=100
                )
            else:
                # 1st priority: If the exact phrase is found
                query_for_phrase = " ".join(query_list)
                phrase_query = Q('bool', should = [Q(MultiMatch(
                    query=query_for_phrase, 
                    type="phrase", 
                    fields=[
                        'title^5',
                        'short_description^3',
                        'description^2',
                        'website_data',
                        'additional_information',
                        'location^5'
                    ]
                    )), Q(
                        'nested',
                        path='keywords',
                        query=MatchPhrase(keyword=query_for_phrase)
                    )],
                    minimum_should_match=1,
                    boost=100
                )
                
                # 2nd priority: If the words are found in same order with gap between them
                interval_query = Q('bool', should =[
                        interval_query_per_field(query_list, 'title'),
                        interval_query_per_field(query_list, 'short_description'),
                        interval_query_per_field(query_list, 'description'),
                        interval_query_per_field(query_list, 'website_data'),
                        interval_query_per_field(query_list, 'additional_information'),
                        interval_query_per_field(query_list, 'location')
                    ],
                    minimum_should_match=1,
                    boost=50
                )
                
                # 3rd priority: If the words are found in any order
                words_query = Q('bool', must=[
                        MultiMatch(
                            query=_query,
                            type="most_fields",
                            fields=[
                                'title^5',
                                'short_description^3',
                                'description^2',
                                'website_data',
                                'additional_information',
                                'location^5'
                            ],
                            fuzziness='AUTO'
                        ) for _query in query_list
                    ],
                )
                
                new_query = Q('bool', should=[phrase_query, interval_query, words_query], minimum_should_match=1)
            i -= 1
        elif type == 1:
            opp = query
            i += 1
            continue
        elif type == 2:
            new_query = Q('bool', should=[MultiMatch(
                    query=query, 
                    type="phrase", 
                    fields=[
                        'title^5',
                        'short_description^3',
                        'description^2',
                        'website_data',
                        'additional_information',
                        'location^5'
                    ]
                ), Q(
                    'nested', 
                    path='keywords', 
                    query=MatchPhrase(keyword=query)
                )], 
                minimum_should_match=1, 
                boost=100
            )
        
        if es_query is None:
            es_query = new_query
        else:
            es_query = es_query & new_query if opp == 'AND' else es_query | new_query
        
        i += 1
    return es_query

def es_opportunity_search(search_query, ours_website=False):
    search_query_list = divide_query(search_query)
    if len(search_query_list) == 0:
        return []
    
    filter_query = Q(Match(active=True))
    if ours_website:
        filter_query = filter_query & \
            Q(Match(show_on_website=True)) & \
            Q('range', show_on_website_start_date={'lte': datetime.datetime.now()}) & \
            Q('range', show_on_website_end_date={'gte': datetime.datetime.now()})
    
    query = make_query_from_list(search_query_list)
    result_opp = OpportunityDocument.search().extra(size=1000).filter(filter_query).query(query).execute()
    
    result_opp = [opp.meta.id for opp in result_opp]
    return result_opp

@login_required
@restrict_to_http_methods('GET', 'POST')
def opportunity_search(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '')
        if len(search_query) == 0:
            return redirect('search_no_result')
        result_opp = es_opportunity_search(search_query)
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