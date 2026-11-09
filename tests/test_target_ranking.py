import unittest
from target_ranking import TIERS, mapping_gate, spatial_component, tractability, priority, assign_ranks


class RankingTests(unittest.TestCase):
    def test_conservative_spatial_and_missing(self):
        rows = [dict(mouse='a', time_hours=48, difference=3), dict(mouse='b', time_hours=48, difference=1)]
        self.assertEqual(spatial_component(rows, 48), .5)
        rows[1]['difference'] = -1
        self.assertEqual(spatial_component(rows, 48), 0)
        rows[1]['difference'] = ''
        self.assertIsNone(spatial_component(rows, 48))
        self.assertIsNone(spatial_component(rows[:1], 48))
        rows[1] = rows[0].copy()
        self.assertIsNone(spatial_component(rows, 48))

    def test_mapping_reasons(self):
        r = dict(human_ensembl_id='h', homology_type='ortholog_one2one', high_confidence='1')
        self.assertEqual(mapping_gate([r], {'h': {'m'}}), ('h', []))
        self.assertEqual(mapping_gate([], {}), ('', ['no_stable_id_mapping']))
        bad = dict(r, human_ensembl_id='other', homology_type='ortholog_one2many', high_confidence='0')
        _, reasons = mapping_gate([r, bad], {'h': {'m', 'm2'}, 'other': {'m'}})
        self.assertEqual(set(reasons), {'multiple_human_targets', 'not_one_to_one', 'low_or_missing_confidence', 'multiple_mouse_ids'})

    def test_tractability_zero_missing_and_tiers(self):
        records = [dict(label=k, modality='SM', value=False) for k in TIERS]
        self.assertEqual(tractability(records), 0)
        self.assertIsNone(tractability([]))
        for record in records:
            record['value'] = True
            self.assertEqual(tractability(records), TIERS[record['label']])
            record['value'] = False
        with self.assertRaises(ValueError):
            tractability(records[:1])

    def test_priority_hand_calculation_and_missing(self):
        self.assertAlmostEqual(priority(.5, .8, .2), 53.)
        self.assertIsNone(priority(.5, None, .2))
        self.assertEqual(priority(0, 0, 0), 0)
        with self.assertRaises(ValueError):
            priority(float('nan'), 0, 0)

    def test_ties_and_safety_cannot_improve_score(self):
        rows = [dict(feature_id=fid, score=priority(.5, .8, .2), safety=safety)
                for fid, safety in [('b', 'reported'), ('a', None)]]
        assign_ranks(rows, 'score', 'rank')
        self.assertEqual([r['rank'] for r in rows], [2, 1])
        before = [dict(r) for r in rows]
        rows[0]['safety'] = None
        assign_ranks(rows, 'score', 'rank')
        self.assertEqual([(r['score'], r['rank']) for r in rows], [(r['score'], r['rank']) for r in before])
