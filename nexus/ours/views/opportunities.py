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
    Keyword,
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
        updated_post = request.POST.copy()
        keywords = request.POST.getlist('keywords')
        for i, keyword in enumerate(keywords):
            if keyword.isnumeric() and Keyword.objects.filter(id=int(keyword)).exists():
                continue
            key = Keyword.objects.create(keyword=keyword)
            keywords[i] = str(key.id)
        updated_post.setlist('keywords', keywords)
        form = CreateOpportunityForm(updated_post, instance=opportunity)
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
        else:
            data = form.cleaned_data
            min_gpa = data.pop('min_gpa')
            restricted_majors = data.pop('restricted_majors')
            require_all_majors = data.pop('require_all_majors')
            restricted_to_citizenship_status = data.pop('restricted_to_citizenship_status')
            restricted_to_study_level = data.pop('restricted_to_study_level')
            opp = form.save()
            
            if min_gpa:
                MinGPARestriction.objects.update_or_create(opportunity=opp, defaults={'gpa': min_gpa})
            else:
                MinGPARestriction.objects.filter(opportunity=opp).delete()
            
            if restricted_majors:
                mr = MajorRestriction.objects.update_or_create(opportunity=opp, defaults={'must_be_all_majors': require_all_majors})
                mr.majors.set(restricted_majors)
                mr.save()
            else:
                MajorRestriction.objects.filter(opportunity=opp).delete()
            
            if restricted_to_citizenship_status:
                rc = CitizenshipRestriction.objects.get_or_create(opportunity=opp)[0]
                rc.citizenship_status.set(restricted_to_citizenship_status)
                rc.save()
            else:
                CitizenshipRestriction.objects.filter(opportunity=opp).delete()
            
            if restricted_to_study_level:
                sl = StudyLevelRestriction.objects.get_or_create(opportunity=opp)[0]
                sl.study_level.set(restricted_to_study_level)
                sl.save()
            else:
                StudyLevelRestriction.objects.filter(opportunity=opp).delete()
            
            messages.success(request, 'Opportunity updated successfully.')
        context = {'success': True, 'opportunity': opportunity}
        response = render(request, 'update_opportunity.html', context)
        response['HX-Trigger-After-Settle'] = json.dumps({"formScroll": "#update-opportunity-message"})
        return response
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
    return render(request, 'just_form.html', context)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor')
def view_opportunity(request, opp_id, full_page=False):
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
    if full_page:
        return render(request, 'opportunity_details_full_page.html', context)
    response = render(request, 'opportunity_details.html', context)
    response["HX-Trigger-After-Settle"] = json.dumps({"viewClicked": f"ot-{opportunity.id}"})
    return response



@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor')
def view_opportunity_full_page(request, opp_id):
    return view_opportunity(request, opp_id, full_page=True)

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'SI Supervisor', 'Tutor Supervisor', 'OURS Supervisor')
def create_opportunity_form(request):
    if request.method == 'POST':
        updated_post = request.POST.copy()
        keywords = request.POST.getlist('keywords')
        for i, keyword in enumerate(keywords):
            if keyword.isnumeric() and Keyword.objects.filter(id=int(keyword)).exists():
                continue
            key = Keyword.objects.create(keyword=keyword)
            keywords[i] = str(key.id)
        updated_post.setlist('keywords', keywords)
        form = CreateOpportunityForm(updated_post)
        success = False
        if form.is_valid():
            data = form.cleaned_data
            min_gpa = data.pop('min_gpa')
            restricted_majors = data.pop('restricted_majors')
            require_all_majors = data.pop('require_all_majors')
            restricted_to_citizenship_status = data.pop('restricted_to_citizenship_status')
            restricted_to_study_level = data.pop('restricted_to_study_level')
            opp = form.save()
            
            if min_gpa:
                MinGPARestriction.objects.update_or_create(opportunity=opp, defaults={'gpa': min_gpa})
            if restricted_majors:
                mr = MajorRestriction.objects.update_or_create(opportunity=opp, defaults={'must_be_all_majors': require_all_majors})
                mr.majors.set(restricted_majors)
                mr.save()
            if restricted_to_citizenship_status:
                rc = CitizenshipRestriction.objects.get_or_create(opportunity=opp)[0]
                rc.citizenship_status.set(restricted_to_citizenship_status)
                rc.save()
            if restricted_to_study_level:
                sl = StudyLevelRestriction.objects.get_or_create(opportunity=opp)[0]
                sl.study_level.set(restricted_to_study_level)
                sl.save()
            
            success = True
            messages.success(request, 'Opportunity created successfully.')
        else:
            messages.error(request, f'Form Errors: {form.errors}')
        context = {'success': success}
        response = render(request, 'create_opportunity_message.html', context)
        response['HX-Trigger-After-Settle'] = json.dumps({"formScroll": "#create-opportunity-message"})
        return response
    form = CreateOpportunityForm()
    context = {'form': form}
    return render(request, 'just_form.html', context)