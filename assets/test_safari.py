import random, unittest

import gen_stats, safari


class Safari(unittest.TestCase):
    def test_spawn_rare_flag_matches_pool(self):
        for seed in range(300):
            m = safari.spawn(random.Random(seed))
            self.assertEqual(m["rare"], m["id"] in safari.RARE)
            self.assertLessEqual(m["id"], safari.GEN5_MAX)

    def test_encounter_is_distinct(self):
        for seed in range(50):
            ids = [m["id"] for m in safari.encounter(random.Random(seed))]
            self.assertEqual(len(set(ids)), safari.WILD_COUNT)

    def test_block_links_cards_to_the_portfolio(self):
        out = safari.block([{"id": 7, "name": "Squirtle", "shiny": True, "rare": False}])
        self.assertIn('href="https://fakubwoy.github.io/portfolio/?wild=7&shiny=1"', out)
        self.assertIn('src="assets/cards/7s.svg"', out)

    def test_fit_caps_upscaling_and_big_sprites(self):
        self.assertEqual(safari.fit(30, 20), 2)
        self.assertEqual(safari.fit(208, 100), 0.5)

    def test_card_tags_rare_in_gold(self):
        gif = b"GIF89a" + (40).to_bytes(2, "little") + (40).to_bytes(2, "little")
        svg = safari.card({"id": 385, "name": "Jirachi", "shiny": False, "rare": True, "type": "steel"}, gif)
        self.assertIn(">RARE<", svg)
        self.assertIn(safari.GOLD, svg)
        self.assertIn(">#385<", svg)

    def test_streak(self):
        self.assertEqual(gen_stats.streak([1, 0, 2, 3, 0]), 2)
        self.assertEqual(gen_stats.streak([0, 1]), 1)
        self.assertEqual(gen_stats.streak([0, 0]), 0)


if __name__ == "__main__":
    unittest.main()
