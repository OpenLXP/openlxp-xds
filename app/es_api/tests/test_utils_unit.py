import json
from unittest.mock import patch

from configurations.models import XDSConfiguration, XDSUIConfiguration
from core.models import CourseSpotlight, SearchFilter, SearchSortOption
from django.test import SimpleTestCase, tag
from elasticsearch_dsl import Q, Search
from es_api.utils.queries import (add_search_aggregations, add_search_filters,
                                  add_search_sort, get_page_start, get_results,
                                  more_like_this, search_by_filters,
                                  search_by_keyword, spotlight_courses)


@tag('unit')
class UtilTests(SimpleTestCase):

    def test_get_results(self):
        """Test that calling get results on a Response Object returns a \
            dictionary with hits and a total"""
        with patch('elasticsearch_dsl.response') as response_obj:
            response_obj.return_value = {
                "hits": {
                    "total": {
                        "value": 1
                    }
                }
            }
            response_obj.hits.total.value = 1
            with patch('elasticsearch_dsl.response.hit.to_dict') as to_dict, \
                patch('es_api.utils.queries.SearchFilter.objects') as sfObj, \
                    patch('elasticsearch_dsl.response.aggregations.to_dict')\
                    as agg:
                agg.return_value = {}
                sfObj.return_value = []
                to_dict.return_value = {
                    "key": "value"
                }
                result_json = get_results(response_obj)
                result_dict = json.loads(result_json)
                self.assertEqual(result_dict.get("total"), 1)
                self.assertEqual(len(result_dict.get("hits")), 0)
                self.assertEqual(len(result_dict.get("aggregations")), 0)

    def test_more_like_this(self):
        """"Test that calling more_like_this returns whatever response elastic\
              search returns"""
        with patch('elasticsearch_dsl.Search.execute') as es_execute:
            resultVal = {
                "test": "test"
            }
            es_execute.return_value = {
                "test": "test"
            }
            result = more_like_this(1)
            self.assertEqual(result, resultVal)

    def test_search_by_keyword_error(self):
        """Test that calling search_by_keyword with a invalid page # \
             (e.g. string) value will throw an error"""
        with patch('es_api.utils.queries.XDSConfiguration.objects') as xdsCfg,\
            patch('elasticsearch_dsl.Search.execute') as es_execute,\
                patch('es_api.utils.queries.SearchFilter.objects') as sfObj:
            configObj = XDSConfiguration(target_xis_metadata_api="dsds")
            uiConfigObj = XDSUIConfiguration(search_results_per_page=10,
                                             xds_configuration=configObj)
            xdsCfg.xdsuiconfiguration = uiConfigObj
            xdsCfg.first.return_value = configObj
            sfObj.return_value = []
            sfObj.filter.return_value = []
            es_execute.return_value = {
                "test": "test"
            }

            self.assertRaises(ValueError, search_by_keyword, "test",
                              {"page": "hello"})

    def test_get_page_start_positive(self):
        """Test that calling the get_page_start returns the correct index when\
            called with correct values"""
        expected_result = 40
        expected_result2 = 1
        actual_result = get_page_start(6, 8)
        actual_result2 = get_page_start(2, 1)

        self.assertEqual(expected_result, actual_result)
        self.assertEqual(expected_result2, actual_result2)

    def test_get_page_start_negative(self):
        """Test that calling the get_page_start returns 0 when called with a\
            number <= 1"""
        expected_result = 0
        expected_result2 = 0
        actual_result = get_page_start(-4, 10)
        actual_result2 = get_page_start(1, 33)

        self.assertEqual(expected_result, actual_result)
        self.assertEqual(expected_result2, actual_result2)

    def test_add_search_filters_no_filter(self):
        """Test that when add_search_filters is called with an empty filter\
            object then no filter gets added to the search object"""
        q = Q("bool", should=[Q("match", Test="test")],
              minimum_should_match=1)
        s = Search(using='default', index='something').query(q)
        filters = {
            "page": 1
        }
        hasFilter = False
        result = add_search_filters(s, filters)
        result_dict = result.to_dict()

        if "filter" in result_dict['query']['bool']:
            hasFilter = True

        self.assertFalse(hasFilter)

    def test_add_search_filters_with_filters(self):
        """Test that when add_search_filters is called with a filter object\
            then the search object contains every filter passed in"""
        q = Q("bool", should=[Q("match", Test="test")],
              minimum_should_match=1)
        s = Search(using='default', index='something').query(q)
        filters = {
            "page": 1,
            "color": ["red", "blue"],
            "model": "nike",
            "type": "shirt"
        }
        hasFilter = False
        result = add_search_filters(s, filters)
        result_dict = result.to_dict()

        if "filter" in result_dict['query']['bool']:
            hasFilter = True

            for filtr in result_dict['query']['bool']['filter']:
                termObj = filtr['terms']

                for filter_name in termObj:
                    orig_name = filter_name.replace('.keyword', '')
                    self.assertEqual(termObj[filter_name], filters[orig_name])

        self.assertTrue(hasFilter)

    def test_add_search_aggregations_no_filters(self):
        """Test that when add_search_aggregations is called with an empty\
            filter object, no aggregations are added to the search object"""
        q = Q("bool", should=[Q("match", Test="test")],
              minimum_should_match=1)
        s = Search(using='default', index='something').query(q)
        filters = []
        hasAggs = False

        add_search_aggregations(filters, s)

        result_dict = s.to_dict()

        if 'aggs' in result_dict:
            hasAggs = True

        self.assertFalse(hasAggs)

    def test_add_search_aggregations_with_filters(self):
        """Test that when add_search_aggregations is called with a list of\
            filter object then aggregations are added to the search object"""
        q = Q("bool", should=[Q("match", Test="test")],
              minimum_should_match=1)
        s = Search(using='default', index='something').query(q)
        config = XDSConfiguration("test")
        uiConfig = XDSUIConfiguration(10, config)
        filterObj = SearchFilter(display_name='type',
                                 field_name='type',
                                 xds_ui_configuration=uiConfig)
        filterObj2 = SearchFilter(display_name='color',
                                  field_name='color',
                                  xds_ui_configuration=uiConfig)
        filters = [filterObj, filterObj2, ]
        hasAggs = False

        add_search_aggregations(filters, s)

        result_dict = s.to_dict()

        if 'aggs' in result_dict:
            hasAggs = True

            for filtr in filters:
                hasBucket = False

                if filtr.display_name in result_dict['aggs']:
                    hasBucket = True

                self.assertTrue(hasBucket)

        self.assertTrue(hasAggs)

    def test_add_search_sort_none(self):
        """Test that when add_search_sorts is called with no sort parameter\
            then the search object does not have a sort attribute"""
        q = Q("bool", should=[Q("match", Test="test")],
              minimum_should_match=1)
        s = Search(using='default', index='something').query(q)

        with patch('es_api.utils.queries.SearchSortOption.objects') as \
                sortOpts:
            sortOpts.filter.return_value = []
            filters = {"test": "Test"}
            hasSort = False

            result = add_search_sort(search=s, filters=filters)
            result_dict = result.to_dict()

            if 'sort' in result_dict:
                hasSort = True

            self.assertFalse(hasSort)

    def test_add_search_sort_selected(self):
        """Test that when add_search_sorts is called with a sort parameter\
            then the search object does have a sort attribute"""
        q = Q("bool", should=[Q("match", Test="test")],
              minimum_should_match=1)
        s = Search(using='default', index='something').query(q)

        with patch('es_api.utils.queries.SearchSortOption.objects') as \
                sortOpts:
            sortOption = SearchSortOption(display_name="test",
                                          field_name="test-field",
                                          xds_ui_configuration=None,
                                          active=True)
            sortOpts.filter.return_value = [sortOption]
            filters = {"sort": "test-field"}
            hasSort = False

            result = add_search_sort(search=s, filters=filters)
            result_dict = result.to_dict()

            if 'sort' in result_dict:
                hasSort = True

            self.assertTrue(hasSort)

    def test_spotlight_courses_non_empty(self):
        """Test that when spotlight_courses is called wwith documents
            configured then it returns an array with the documents"""
        with patch('es_api.utils.queries.CourseSpotlight.objects') as \
                spotlightObjs, patch('elasticsearch_dsl.Document.mget') as \
                mget:
            doc_1 = {
                "_source": {
                    "test": "val",
                    "test2": "val2"
                },
                "_id": "12312",
                "_index": "test-index"
            }
            doc_2 = {
                "_source": {
                    "test3": "val3",
                    "test4": "val4"
                },
                "_id": "43231",
                "_index": "test-index-2"
            }
            spotlight = CourseSpotlight(course_id=1)
            spotlightObjs.filter.return_value = [spotlight]
            instance_1 = mget.return_value
            mget.return_value = [instance_1, instance_1]
            instance_1.to_dict.side_effect = [doc_1, doc_2]
            result = spotlight_courses()

            self.assertEqual(len(result), 2)
            self.assertTrue('meta' in result[0])
            self.assertEqual(doc_1["_id"], result[0]["meta"]["id"])

    def test_spotlight_courses_empty(self):
        """Test that when spotlight_courses is called wwith no documents
            then it throws an error"""
        with patch('es_api.utils.queries.CourseSpotlight.objects') as \
                spotlightObjs, patch('elasticsearch_dsl.Document.mget') as \
                mget:
            spotlightObjs.filter.return_value = []
            mget.return_value = []
            result = spotlight_courses()

            self.assertEqual(len(result), 0)

    def test_search_by_filters(self):
        """Test that calling search_by_filters returns an JSON object"""
        with patch('es_api.utils.queries.XDSConfiguration.objects') as xdsCfg,\
                patch('elasticsearch_dsl.Search.execute') as es_execute:
            configObj = XDSConfiguration(target_xis_metadata_api="dsds")
            uiConfigObj = XDSUIConfiguration(search_results_per_page=10,
                                             xds_configuration=configObj)
            xdsCfg.xdsuiconfiguration = uiConfigObj
            xdsCfg.first.return_value = configObj
            expected_result = {
                "test": "test"
            }
            es_execute.return_value = expected_result
            result = search_by_filters(1, {'Course.CourseTitle': 'test'})

            self.assertEqual(result, expected_result)
