from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DetailView, DeleteView, ListView, UpdateView

from braces.views import LoginRequiredMixin

from ..forms import RegistrationForm
from ..models import get_application_model
from account.permissions import perms


class ApplicationOwnerIsUserMixin(LoginRequiredMixin):
    """
    This mixin is used to provide an Application queryset filtered by the current request.user.
    """
    model = get_application_model()

    def get_queryset(self):
        queryset = super(ApplicationOwnerIsUserMixin, self).get_queryset()
        qset = Q(user=self.request.user)
        if self.request.GET.get('q'):
            qset = Q(qset&Q(name__contains=self.request.GET.get('q')))
        return queryset.filter(qset)


class ApplicationRegistration(LoginRequiredMixin, CreateView):
    """
    View used to register a new Application for the request.user
    """
    form_class = RegistrationForm
    template_name = "oauth2/application_registration_form.html"

    def get(self, request, *args, **kwargs):
        if not perms.may_create_application(request.user):
            raise PermissionDenied
        return super(ApplicationRegistration, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not perms.may_create_application(request.user):
            raise PermissionDenied
        return super(ApplicationRegistration, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ApplicationRegistration, self).form_valid(form)


class ApplicationDetail(ApplicationOwnerIsUserMixin, DetailView):
    """
    Detail view for an application instance owned by the request.user
    """
    context_object_name = 'application'
    template_name = "oauth2/application_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ApplicationDetail, self).get_context_data(**kwargs)
        if self.object:
            if self.object.status in [1, 3]:
                context["is_examine"] = True
        return context


class ApplicationList(ApplicationOwnerIsUserMixin, ListView):
    """
    List view for all the applications owned by the request.user
    """
    context_object_name = 'applications'
    template_name = "oauth2/application_list.html"

    def get_context_data(self, **kwargs):
        context_data = super(ApplicationList, self).get_context_data(**kwargs)
        return context_data


class ApplicationDelete(ApplicationOwnerIsUserMixin, DeleteView):
    """
    View used to delete an application owned by the request.user
    """
    context_object_name = 'application'
    success_url = reverse_lazy('oauth2:list')
    template_name = "oauth2/application_confirm_delete.html"


class ApplicationExamine(ApplicationOwnerIsUserMixin, DetailView):
    """
    View used to delete an application owned by the request.user
    """

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        assert object.status in [1, 3]
        object.status = 2
        object.save()
        return HttpResponseRedirect(reverse_lazy('oauth2:detail', kwargs={"pk": kwargs['pk']}))


class ApplicationUpdate(ApplicationOwnerIsUserMixin, UpdateView):
    """
    View used to update an application owned by the request.user
    """
    form_class = RegistrationForm
    context_object_name = 'application'
    template_name = "oauth2/application_form.html"
