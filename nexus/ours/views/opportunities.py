from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

import json
from dal import autocomplete

from core.views import restrict_to_http_methods, restrict_to_groups

from ..models import (
    Opportunity,
    MinGPARestriction,
    MajorRestriction,
    CitizenshipRestriction,
    StudyLevelRestriction,
    Keyword,
    Location,
)

from ..forms.opportunity import CreateOpportunityForm, SimpleSearchForm

# Fields of the opportunity form that take typed-in tags: (form field, model, name field)
TAG_FIELDS = (
    ('keywords', Keyword, 'keyword'),
    ('locations', Location, 'name'),
)

def split_tag_values(model, values):
    """Split a tag field's submitted values into ids of existing rows and newly typed names."""
    ids, names = [], []
    for value in values:
        # An existing choice is submitted as its plain pk; "01003" or "²" can only have been typed
        is_pk = value.isascii() and value.isdigit() and str(int(value)) == value
        if is_pk and model.objects.filter(id=int(value)).exists():
            ids.append(value)
            continue
        name = ' '.join(value.split())
        if name:
            names.append(name)
    return ids, names

def bind_opportunity_form(post, **form_kwargs):
    """
    Bind CreateOpportunityForm to the POST data. Keywords and locations that were
    typed in rather than picked are only created once the rest of the form is valid.
    """
    post = post.copy()
    typed = {}
    for field, model, name_field in TAG_FIELDS:
        ids, typed[field] = split_tag_values(model, post.getlist(field))
        post.setlist(field, ids)
    form = CreateOpportunityForm(post, **form_kwargs)
    form.is_valid()
    for field, model, name_field in TAG_FIELDS:
        max_length = model._meta.get_field(name_field).max_length
        for name in typed[field]:
            if len(name) > max_length:
                form.add_error(field, f'"{name[:50]}..." is longer than {max_length} characters.')
    if form.errors or not any(typed.values()):
        return form
    for field, model, name_field in TAG_FIELDS:
        ids = post.getlist(field)
        for name in typed[field]:
            # Case-insensitive, so "boston, ma" reuses "Boston, MA" instead of duplicating it
            obj = model.objects.filter(**{f'{name_field}__iexact': name}).first()
            if obj is None:
                obj = model.objects.create(**{name_field: name})
            if str(obj.id) not in ids:
                ids.append(str(obj.id))
        post.setlist(field, ids)
    return CreateOpportunityForm(post, **form_kwargs)

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def opportunities_list(request):
    if request.method == 'POST':
        search = request.POST.get('search').strip()
        if len(search) == 0:
            opportunities = Opportunity.objects.all()
        else:
            opportunities = Opportunity.objects.basic_search(search)
        context = {
            'opportunities': opportunities.values_list('id', flat=True),
        }
        return render(request, 'opportunities_simple_search_result.html', context)
    opportunities = Opportunity.objects.all().values_list('id', flat=True)
    context = {
        'opportunities': opportunities,
        'form': SimpleSearchForm(),
    }
    return render(request, 'opportunities_list.html', context)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def get_opportunity_row(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    context = {'opportunity': opportunity}
    return render(request, 'opportunity_row.html', context)

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def update_opportunity(request, opp_id, check_opportunity=False):
    try:
        opportunity = Opportunity.objects.get(id=opp_id)
    except Opportunity.DoesNotExist:
        messages.error(request, 'Opportunity not found.')
        context = {'success': False, 'opportunity': None}
        response = render(request, 'update_opportunity.html' if not check_opportunity else 'check_opp_update.html', context)
        response['HX-Trigger-After-Settle'] = json.dumps({"formScroll": "#update-opportunity-message"})
        return response
    if request.method == 'POST':
        form = bind_opportunity_form(request.POST, instance=opportunity)
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
                mr = MajorRestriction.objects.update_or_create(opportunity=opp, defaults={'must_be_all_majors': require_all_majors})[0]
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
        response = render(request, 'update_opportunity.html' if not check_opportunity else 'check_opp_update.html', context)
        response['HX-Trigger-After-Settle'] = json.dumps({"formScroll": "#update-opportunity-message"})
        return response
    context = {'success':False, 'opportunity': opportunity}
    response = render(request, 'update_opportunity.html' if not check_opportunity else 'check_opp_update.html', context)
    response["HX-Trigger-After-Settle"] = json.dumps({"updateClicked": f"ot-{opportunity.id}"})
    return response

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def update_opportunity_form(request, opp_id, check_opportunity=False):
    opportunity = Opportunity.objects.get(id=opp_id)
    form = CreateOpportunityForm(instance=opportunity, check_opportunity=check_opportunity)
    context = {'form': form}
    return render(request, 'just_form.html', context)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
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
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def view_opportunity_full_page(request, opp_id):
    return view_opportunity(request, opp_id, full_page=True)

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def create_opportunity_form(request):
    if request.method == 'POST':
        form = bind_opportunity_form(request.POST)
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
                mr = MajorRestriction.objects.update_or_create(opportunity=opp, defaults={'must_be_all_majors': require_all_majors})[0]
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

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def delete_opportunity(request, opp_id):
    opportunity = Opportunity.objects.get(id=opp_id)
    opportunity.delete()
    return HttpResponse('')

class OpportunityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Opportunity.objects.all()
        if self.q:
            qs = Opportunity.objects.basic_search(self.q)
        return qs

class KeywordAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Keyword.objects.all()
        if self.q:
            qs = Keyword.objects.filter(keyword__icontains=self.q)
        return qs

class LocationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Location.objects.all()
        if self.q:
            qs = Location.objects.filter(name__icontains=self.q)
        return qs