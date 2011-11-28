# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
"""
API views not coupled to models.
"""

from django.core.urlresolvers import reverse

from djangorestframework.response import Response
from djangorestframework.views import View
from djangorestframework import status

from lizard_annotation.models import Annotation
from lizard_annotation.models import AnnotationType
from lizard_annotation.models import AnnotationStatus
from lizard_annotation.models import AnnotationCategory

from lizard_annotation.forms import AnnotationForm
from lizard_annotation.forms import StatusForm
from lizard_annotation.forms import CategoryForm
from lizard_annotation.forms import TypeForm


"""
Beware that the djangorestframework trips if you name an attribute of
the view 'model', and also if one of the methods return a dict with a key
'model' in it. Hence the attribute 'document' on a number of classes
"""


class RootView(View):
    """
    Startpoint.
    """
    def get(self, request):
        return {
            "annotations grid": reverse(
                'lizard_annotation_api_annotation_grid'),
            "annotations": reverse(
                'lizard_annotation_api_annotation_root'),
            "annotation statuses": reverse(
                'lizard_annotation_api_annotation_status_root'),
            "annotation categories": reverse(
                'lizard_annotation_api_annotation_category_root'),
            "annotation types": reverse(
                'lizard_annotation_api_annotation_type_root'),
            }


class AnnotationGridView(View):
    """
    Show a (filtered) list of annotations with all annotation
    fields.

    Possible filters are:

    - annotation_type
    """
    def get(self, request):
        """
        Return annotationgrid.

        TODO Add some pagination if the grid gets really long.
        """
        # Handle additional filtering
        annotation_type = request.GET.get('type')
        if annotation_type:
            try:
                type_obj = AnnotationType.objects.get(
                    annotation_type=annotation_type)
            except AnnotationType.DoesNotExist:
                return Response(status.HTTP_404_NOT_FOUND)
            annotations = Annotation.objects.filter(
                annotation_type=type_obj)
        else:
            annotations = Annotation.objects.all()
        return {'annotations': [a.get_dict()
                                for a in annotations()]}


class DocumentRootView(View):
    """
    Baseview for root views.

    Subclasses must set the document attribute.
    """
    def get(self, request):
        """
        Read a document list. Assumes documents have a get_absolute_url()
        method implemented.
        """
        return [[d, d.get_absolute_url()]
                for d in self.document.objects.all()]

    def post(self, request, pk=None):
        """Create a document."""
        self.document(**self.CONTENT).save()
        return Response(status.HTTP_200_OK)


class AnnotationRootView(DocumentRootView):
    """
    View all annotations or create one.
    """
    document = Annotation
    form = AnnotationForm


class AnnotationTypeRootView(DocumentRootView):
    """
    View all types or create one.
    """
    document = AnnotationType
    form = TypeForm


class AnnotationCategoryRootView(DocumentRootView):
    """
    View all categories or create one.
    """
    document = AnnotationCategory
    form = CategoryForm


class AnnotationStatusRootView(DocumentRootView):
    """
    View all statuses or create one.
    """
    document = AnnotationStatus
    form = StatusForm


class DocumentView(View):
    """
    Baseview for detail views.

    Subclasses must set form and document attributes.
    """
    def get(self, request, pk):
        """Read a document."""
        try:
            obj = self.document.objects.get(pk=pk)
        except self.document.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        if request.GET.get('_format') == 'property':
            fields = request.GET.get('_fields')
            if fields:
                properties = fields.split(',')
            else:
                properties = None
            property_list = obj.get_property_list(properties=properties)
            return {'properties': property_list}

        return obj.get_dict(ref_urls=True)

    def put(self, request, pk):
        """Update a document."""
        try:
            obj = self.document.objects.get(pk=pk)
            obj.__dict__.update(self.CONTENT)
            obj.save()
            return Response(status.HTTP_200_OK)
        except self.document.DoesNotExist:
            obj = self.document(pk=pk, **self.CONTENT)
            obj.save()
            return Response(status.HTTP_201_CREATED)

    def delete(self, request, pk):
        """Delete a document."""
        self.document.objects.get(pk=pk).delete()
        return Response(status.HTTP_200_OK)


class AnnotationView(DocumentView):
    """
    Edit annotation details.

    Supply '_format=property' as get parameter to return a property,
    value list. Note that doing so breaks the prefilled forms. To get
    only a selection of fields supply a comma-separated list of the
    form '_fields=property1,property2'.
    """
    document = Annotation
    form = AnnotationForm


class AnnotationTypeView(DocumentView):
    """
    Edit annotation type details.
    """
    document = AnnotationType
    form = TypeForm


class AnnotationCategoryView(DocumentView):
    """
    Edit annotation category details.
    """
    document = AnnotationCategory
    form = CategoryForm


class AnnotationStatusView(DocumentView):
    """
    Edit annotation status details.
    """
    document = AnnotationStatus
    form = StatusForm
