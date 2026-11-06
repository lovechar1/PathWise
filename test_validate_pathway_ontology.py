import json
import tempfile
import unittest
from pathlib import Path

from validate_pathway_ontology import ontology_ids, select_paths, validate_pathway


class ValidatePathwayOntologyTests(unittest.TestCase):
    def setUp(self):
        self.known = ontology_ids(
            {
                "categories": [
                    {"category": "biological pathways", "terms": [{"id": "example"}]},
                    {"category": "biological entities", "terms": [{"id": "cell"}]},
                    {"category": "relationship types", "terms": [{"id": "causes"}]},
                    {"category": "organisms", "terms": [{"id": "human"}]},
                ]
            }
        )

    def write_pathway(self, directory: str, data: dict) -> Path:
        path = Path(directory) / "example.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_valid_references_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_pathway(
                directory,
                {
                    "key_events": [
                        {
                            "biological_entity_id": "cell",
                            "species_annotation": {"human": "present"},
                        }
                    ],
                    "key_event_relationships": [
                        {"relationship": ["causes"], "active_in": ["human"]}
                    ],
                },
            )
            self.assertEqual(validate_pathway(path, self.known), [])

    def test_missing_references_are_collected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_pathway(
                directory,
                {
                    "key_events": [{"biological_entity_id": "missing_entity"}],
                    "key_event_relationships": [
                        {"relationship": ["missing_relationship"], "absent_in": ["cat"]}
                    ],
                },
            )
            missing = validate_pathway(path, self.known)
            self.assertEqual(
                {(item.category, item.value) for item in missing},
                {
                    ("biological entities", "missing_entity"),
                    ("relationship types", "missing_relationship"),
                    ("organisms", "cat"),
                },
            )

    def test_explicit_paths_take_precedence(self):
        paths = [Path("pathways/example.json")]
        self.assertEqual(select_paths(paths, "origin/main"), paths)


if __name__ == "__main__":
    unittest.main()
