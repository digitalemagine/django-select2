=======================
Django Select2 Examples
=======================

Or how to use Django Select2 - some from the included testapp.


Setup - model field
===================



.. code:: python

    class MyModel(models.Model):

        # some stuff

        field_fk = models.ForeignKey(SomeModel)
        field_choices = models.CharField(choices=SOME_CHOICES)

Simple Select2
--------------

Simply use the Select2Widget in a form

.. code:: python

    class MyForm(forms.ModelForm):

        class Meta:
            model = MyModel

            widgets = {
                'field_fk': Select2Widget,
                'field_choices': Select2Widget,
            }


This is the most straightforward. No settings. All choices and models will be embedded into the page.

Does not work with large choices or referenced models!

Heavy Select2
-------------

Retrieves data from server.

Of course requires creating a view that responds to the ajax request.

Extending Select2View
.....................

A simple way is to extend the included Select2View

.. code:: python

    from django.db.models import Q
    from django_select2 import Select2View, NO_ERR_RESP

    from .models import MyModel

    class MyModelSelect2View(Select2View):

        def check_all_permissions(self, request, *args, **kwargs):
            user = request.user
            if not (user.is_authenticated() and user.has_perms('mymodel.view_mymodel')):
                raise PermissionDenied

        def get_results(self, request, term, page, context):
            qs = Models.objects.filter(
                Q(SOME_FIELD__icontains=term) | Q(SOME_FIELD__icontains=term) | Q(SOME_FIELD__icontains=term))
            res = [ (instance.id, "%s %s" % (instance.WHAT YOU WANT TO FORMAT),)
                for instance in instances ]
            return (NO_ERR_RESP, False, res) # Any error response, Has more results, options list

Then simply use it in the urls

.. code:: python

    ...

Using AutoSelect2Field
......................

If you feel that writing these views are too much of a hassel then you have an alternate option – sub-class AutoSelect2Field field. In your sub-classed field you need to override security_check(self, request, *args, **kwargs) and get_results(self, request, term, page, context) methods. When your field will be instantiated for the first time, it will register its own instance with AutoResponseView. When the related field is used in the browser, the queries would be directed to AutoResponseView which will direct it to your ‘auto’ field instance. For ‘auto’ fields to work you must use the following code in your urls.py to register the url for AutoResponseView.

..code:: python

    urlpatterns += patterns("",
        url(r"^select2/", include("django_select2.urls")),
    )



    class MyForm(forms.ModelForm):
        loc = HeavySelect2MultipleChoiceField(
                widget=HeavySelect2MultipleWidget(
                        data_view='cities_json',
                        select2_options={
                                'placeholder': _('Type city name')
                                }
                        ),
                required=False)