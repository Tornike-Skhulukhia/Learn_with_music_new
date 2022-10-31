from django.test import TestCase
from .models import Song
from datetime import date


class TestSong(TestCase):
    def setUp(self):
        self.song = Song.objects.create(
            youtube_id="s3wNuru4U0I",
            title="USA For Africa - We Are The World (HQ official Video)",
            duration=426,
            published_at=date(2016, 2, 28),
        )

    def test_song_created(self):

        # just 1 song created
        self.assertEqual(Song.objects.count(), 1)

        song = Song.objects.first()

        self.assertEqual(song.youtube_id, "s3wNuru4U0I")
        self.assertEqual(
            song.title, "USA For Africa - We Are The World (HQ official Video)"
        )
        self.assertEqual(song.duration, 426)
        self.assertEqual(song.published_at, date(2016, 2, 28))

    def test_set_lyrics_without_timing_info(self):
        raw_lyrics = [
            "His palms are sweaty, knees weak, arms are heavy",
            "There's vomit on his sweater already, mom's spaghetti",
            "He's nervous, but on the surface he looks calm and ready",
            "To drop bombs, but he keeps on forgetting",
            "What he wrote down, the whole crowd goes so loud",
            "He opens his mouth, but the words won't come out",
            "He's choking, how? Everybody's joking now",
            "The clock's run out, time's up, over, blaow",
        ]

        self.song.set_lyrics_without_timing_info(
            raw_lyrics, initial_default_line_duration=2000
        )

        lyrics_and_timings = self.song.lyrics_and_timings

        # correct length
        self.assertEqual(len(lyrics_and_timings), 8)

        # line texts saved
        self.assertEqual(lyrics_and_timings[0]["text"], raw_lyrics[0])
        self.assertEqual(lyrics_and_timings[4]["text"], raw_lyrics[4])
        self.assertEqual(lyrics_and_timings[-1]["text"], raw_lyrics[-1])

        # initial timings are correct
        self.assertEqual(lyrics_and_timings[0]["start"], 0)
        self.assertEqual(lyrics_and_timings[0]["end"], 2000)

        self.assertEqual(lyrics_and_timings[4]["start"], 8000)
        self.assertEqual(lyrics_and_timings[4]["end"], 10000)

        self.assertEqual(lyrics_and_timings[7]["start"], 14000)
        self.assertEqual(lyrics_and_timings[7]["end"], 16000)

        # line numbers are correct
        self.assertEqual(lyrics_and_timings[0]["n"], 1)
        self.assertEqual(lyrics_and_timings[3]["n"], 4)
        self.assertEqual(lyrics_and_timings[7]["n"], 8)

    def test_update_existing_lyrics_timings_using_only_start_and_end_times(
        self,
    ):

        self.song.set_lyrics_without_timing_info(
            [
                "His palms are sweaty, knees weak, arms are heavy",
                "There's vomit on his sweater already, mom's spaghetti",
                "He's nervous, but on the surface he looks calm and ready",
                "To drop bombs, but he keeps on forgetting",
            ],
            initial_default_line_duration=2000,
        )

        # given new timings length is is not full, must raise exception
        with self.assertRaises(AssertionError):
            self.song.update_existing_lyrics_timings_using_only_start_and_end_times(
                new_start_and_end_times_list=[
                    {"start": 0, "end": 4500},
                    {"start": 4500, "end": 12800},
                ]
            )

        self.song.update_existing_lyrics_timings_using_only_start_and_end_times(
            new_start_and_end_times_list=[
                {"start": 0, "end": 1400},
                {"start": 1400, "end": 3700},
                {"start": 3700, "end": 14200},
                {"start": 14200, "end": 18000},
            ]
        )

        # make sure data was saved
        lyrics = self.song.lyrics_and_timings
        assert lyrics[0]["start"] == 0
        assert lyrics[0]["end"] == 1400

        assert lyrics[3]["start"] == 14200
        assert lyrics[3]["end"] == 18000

    def test_set_lyrics_using_timing_info_in_seconds(self):

        info = [
            # no timing for 0 to 1 seconds
            {
                "text": "His palms are sweaty, knees weak, arms are heavy",
                "start": 1,
                "duration": 5,
            },
            # no timing for 6 to 8.5 seconds
            {
                "text": "There's vomit on his sweater already, mom's spaghetti",
                "start": 8.5,
                "duration": 13,
            },
            {
                "text": "He's nervous, but on the surface he looks calm and ready",
                "start": 21.5,
                "duration": 4,
            },
            {
                "text": "small nonexistent text",
                "start": 25.5,
                "duration": 0.2,  # as this line is too short - 0.2 seconds, it must be merged with previous one
            },
            # no timing for 25.7 to 27 seconds
            {
                "text": "To drop bombs, but he keeps on forgetting",
                "start": 27,
                "duration": 3,
            },
        ]

        self.song.set_lyrics_using_timing_info_in_seconds(info)

        lyrics = self.song.lyrics_and_timings

        # correct number of final lines
        self.assertEqual(len(lyrics), 7)

        # make sure no rounding issues are coming up
        self.assertTrue(all(isinstance(i["start"], int) for i in lyrics))
        self.assertTrue(all(isinstance(i["end"], int) for i in lyrics))

        # missed times were filled in with "" - having texts
        self.assertEqual(lyrics[0]["text"], "")
        self.assertEqual(lyrics[0]["start"], 0)
        self.assertEqual(lyrics[0]["end"], 1000)  # stored as milliseconds

        self.assertEqual(lyrics[2]["text"], "")
        self.assertEqual(lyrics[2]["start"], 6000)
        self.assertEqual(lyrics[2]["end"], 8500)  # stored as milliseconds

        self.assertEqual(lyrics[5]["text"], "")
        self.assertEqual(lyrics[5]["start"], 25700)
        self.assertEqual(lyrics[5]["end"], 27000)  # stored as milliseconds

        # lines with very short durations, merged with previous ones
        self.assertEqual(
            lyrics[4]["text"], f'{info[2]["text"]} {info[3]["text"]}'
        )

        self.assertEqual(
            lyrics[4]["end"],
            (info[2]["start"] + info[2]["duration"] + info[3]["duration"])
            * 1000,
        )
