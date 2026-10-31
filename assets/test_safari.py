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

    def test_block_links_sprites_to_the_portfolio(self):
        out = safari.block([{"id": 7, "name": "Squirtle", "shiny": True, "rare": False}])
        self.assertIn('href="https://fakubwoy.github.io/portfolio/?wild=7&shiny=1"', out)
        self.assertIn("/shiny/7.gif", out)

    def test_streak(self):
        self.assertEqual(gen_stats.streak([1, 0, 2, 3, 0]), 2)
        self.assertEqual(gen_stats.streak([0, 1]), 1)
        self.assertEqual(gen_stats.streak([0, 0]), 0)


if __name__ == "__main__":
    unittest.main()
