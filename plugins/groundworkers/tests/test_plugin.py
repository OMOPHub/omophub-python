import unittest
from unittest.mock import AsyncMock, patch

import httpx
from examples.run_demo import Client
from groundworkers_omophub import Coding, Vocabulary


class PinningTests(unittest.TestCase):
    def setUp(self):
        self.api = Vocabulary("unused-test-key", "2026.2")

    def test_unpinned_release_rejected(self):
        with self.assertRaises(ValueError):
            Vocabulary("unused-test-key", "latest")

    @patch("groundworkers_omophub.httpx.request")
    def test_both_release_signals_checked(self, get):
        for header, metadata in [
            (None, "2026.2"),
            ("2026.1", "2026.2"),
            ("2026.2", "2026.1"),
        ]:
            with self.subTest(header=header, metadata=metadata):
                get.return_value = httpx.Response(
                    200,
                    headers={"X-Vocab-Release": header} if header else {},
                    json={"meta": {"vocab_release": metadata}},
                )
                with self.assertRaises(ValueError):
                    self.api.read("concepts/1")
                self.assertEqual(
                    get.call_args.kwargs["params"]["vocab_release"], "2026.2"
                )
                self.assertEqual(
                    get.call_args.kwargs["headers"]["X-Vocab-Release"], "2026.2"
                )
                self.assertFalse(get.call_args.kwargs["follow_redirects"])

    @patch("groundworkers_omophub.time.sleep")
    @patch("groundworkers_omophub.httpx.request")
    def test_retry_preserves_pin(self, get, sleep):
        get.side_effect = [
            httpx.Response(429, headers={"Retry-After": "2"}),
            httpx.Response(
                200, headers={"X-Vocab-Release": "2026.2"}, json={"meta": {}}
            ),
        ]
        self.api.read("concepts/1")
        sleep.assert_called_once_with(3)
        self.assertEqual(get.call_args_list[0], get.call_args_list[1])


class HostedToolTests(unittest.TestCase):
    def setUp(self):
        self.api = Vocabulary("unused-test-key", "2026.2")

    @patch("groundworkers_omophub.httpx.request")
    def test_fhir_post_pins_release_and_preserves_fields(self, request):
        payload = {
            "best_match": None,
            "alternatives": [],
            "unresolved": [{"input": {"code": "001"}}],
        }
        request.return_value = httpx.Response(
            200,
            headers={"X-Vocab-Release": "2026.2"},
            json={"meta": {"vocab_release": "2026.2"}, "data": payload},
        )
        coding = Coding.model_validate(
            {"system": "urn:example", "code": "001", "userSelected": True}
        )
        result = self.api.fhir_resolve_codeable_concept([coding])
        method, url = request.call_args.args
        options = request.call_args.kwargs
        self.assertEqual(
            (method, url),
            ("POST", "https://api.omophub.com/v1/fhir/resolve/codeable-concept"),
        )
        self.assertEqual(options["params"], {"vocab_release": "2026.2"})
        self.assertEqual(options["headers"]["X-Vocab-Release"], "2026.2")
        self.assertEqual(
            options["json"]["coding"],
            [{"system": "urn:example", "code": "001", "user_selected": True}],
        )
        self.assertEqual(result["data"], payload)

    @patch("groundworkers_omophub.httpx.request")
    def test_reject_record_text_and_ambiguous_seeds_before_transmission(self, request):
        with self.assertRaises(ValueError):
            self.api.fhir_resolve(display='{"resourceType":"Patient"}')
        with self.assertRaises(ValueError):
            self.api.fhir_resolve_codeable_concept(
                [Coding(system="urn:example", code="001", display="MRN: example")]
            )
        with self.assertRaises(ValueError):
            self.api.find_similar_concepts(concept_id=5, query="example")
        request.assert_not_called()

    @patch("groundworkers_omophub.httpx.request")
    def test_similarity_preserves_zero_threshold_and_degradation(self, request):
        data = {
            "similar_concepts": [],
            "search_metadata": {"algorithm_used": "lexical", "degraded_from": "hybrid"},
        }
        request.return_value = httpx.Response(
            200, headers={"X-Vocab-Release": "2026.2"}, json={"meta": {}, "data": data}
        )
        result = self.api.find_similar_concepts(
            query="example",
            algorithm="hybrid",
            similarity_threshold=0,
            vocabulary_ids="SNOMED, ICD10CM",
        )
        self.assertEqual(request.call_args.kwargs["json"]["similarity_threshold"], 0)
        self.assertEqual(
            request.call_args.kwargs["json"]["vocabulary_ids"], ["SNOMED", "ICD10CM"]
        )
        self.assertEqual(result["data"], data)


class CoverageTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_truncated_hierarchy(self):
        client = Client(None, "2026.2")
        client.call = AsyncMock(return_value={"truncated": True})
        with self.assertRaisesRegex(ValueError, "cap"):
            await client.rows("descendants", concept_id=1)

    async def test_rejects_short_final_page(self):
        client = Client(None, "2026.2")
        client.call = AsyncMock(
            return_value={
                "rows": [],
                "pagination": {"page": 1, "has_next": False, "total_items": 1},
            }
        )
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            await client.rows("relationships", concept_id=1)


class ReleaseComparisonTests(unittest.TestCase):
    def setUp(self):
        self.api = Vocabulary("test", "2026.2")

    @patch.object(Vocabulary, "relationships", autospec=True)
    @patch.object(Vocabulary, "by_code", autospec=True)
    def test_each_release_resolves_source_and_exhausts_pages(self, code, edges):
        code.side_effect = lambda api, _vocab, _term: {
            "concept": {"concept_id": 1 if api.release == "2024.2" else 2}
        }

        def get_page(api, source, kinds, page):
            baseline = api.release == "2024.2"
            self.assertEqual(source, 1 if baseline else 2)
            target, kind = (
                (9, "Maps to")
                if page == 1
                else (10, "Maps to" if baseline else "Maps to value")
            )
            return {
                "rows": [
                    {
                        "source": {"concept_id": source},
                        "relationship_id": kind,
                        "target": {"concept_id": target},
                    }
                ],
                "pagination": {
                    "page": page,
                    "total_items": 2,
                    "has_next": page == 1,
                    "total_pages": 2,
                },
            }

        edges.side_effect = get_page
        report = self.api.compare_mappings("ICD10CM", "D3A.022", "2024.2")
        self.assertEqual(
            [c.args[0].release for c in edges.call_args_list],
            ["2024.2", "2024.2", "2026.2", "2026.2"],
        )
        self.assertEqual(
            report["added"],
            [{"relationship_id": "Maps to value", "target_concept_id": 10}],
        )
        self.assertEqual(
            report["removed"], [{"relationship_id": "Maps to", "target_concept_id": 10}]
        )
        self.assertEqual(self.api.release, "2026.2")

    @patch.object(Vocabulary, "relationships")
    @patch.object(Vocabulary, "by_code")
    def test_missing_edges_fail_comparison(self, code, edges):
        code.return_value = {"concept": {"concept_id": 1}}
        edges.return_value = {
            "rows": [],
            "pagination": {
                "page": 1,
                "total_items": 2,
                "has_next": False,
                "total_pages": 1,
            },
        }
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            self.api.compare_mappings("ICD10CM", "D3A.022", "2024.2")

    def test_comparison_requires_two_explicit_releases(self):
        for release in ("latest", "2026.2"):
            with self.subTest(release=release), self.assertRaises(ValueError):
                self.api.compare_mappings("ICD10CM", "D3A.022", release)
