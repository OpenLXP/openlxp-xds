import os

from elasticsearch_dsl import FacetedSearch, TermsFacet, DateHistogramFacet


class MetadataSearch(FacetedSearch):

    index = os.environ.get('ES_INDEX')
    # fields that should be searched
    fields = ['CourseTitle', 'CourseDescription']

    facets = {
        # use bucket aggregations to define facets
        'subject_matter': TermsFacet(field='Course.CourseSubjectMatter'),
        'course_provider': TermsFacet(field='Course.CourseProviderName')
    }

    # def search(self):
    #     # override methods to add custom pieces
    #     s = super().search()
    #     return s.filter('range', publish_from={'lte': 'now/h'})
