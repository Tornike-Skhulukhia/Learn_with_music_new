from django.test import TestCase
from .models import Song, Language, SongTextLine
from datetime import date

# Create your tests here.
class TestSong(TestCase):
    def setUp(self):
        Song.objects.create(
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


class TestSongLine(TestCase):
    def setUp(self):
        song = Song.objects.create(
            youtube_id="Bllwo3U2T2Q",
            title="Eminem Till i Collapse (Official Music Video)",
            duration=317,
            published_at=date(2009, 12, 12),
        )

        self.lyrics = [
            "'Cause sometimes you just feel tired, feel weak",
            "(Yo left, yo left, yo left, right, left)",
            "And when you feel weak (Yo left)",
            "You feel like you wanna just give up (Yo left, yo left)",
            "But you gotta search within you (Right, left)",
            "Try to find that inner strength (Yo left, yo left)",
            "And just pull that shit out of you (Yo left)",
            "And get that motivation to not give up (Right, left, yo left)",
            "And not be a quitter, no matter how bad you wanna just fall",
            "(Yo left, yo left, right, left)",
            "Flat on your face and collapse",
            "",
            "'Til I collapse I'm spillin' these raps long as you feel 'em",
            "'Til the day that I drop you'll never say that I'm not killin' 'em",
            "'Cause when I am not, then I'ma stop pennin' 'em",
            "And I am not hip-hop and I'm just not Eminem",
            "Subliminal thoughts, when I'ma stop sendin' 'em?",
            "Women are caught in webs, spin 'em and hock venom",
            "Adrenaline shots of penicillin could not get the illin' to stop",
            "Amoxicillin's just not real enough",
            "The criminal, cop-killin', hip-hop villain",
            "A minimal swap to cop millions of Pac listeners",
            "You're comin' with me, feel it or not",
            "You're gonna fear it like I showed you the spirit of God lives in us",
            "You hear it a lot, lyrics to shock",
            "Is it a miracle or am I just product of pop fizzin' up?",
            "Fo' shizzle, my wizzle, this is the plot, listen up",
            "You bizzles forgot, Slizzle does not give a fuck",
        ]
        song.add_lyrics_with_raw_lyrics(self.lyrics)

    def test_lyrics_added(self):
        song = Song.objects.first()

        lines = list(song.songtextline_set.order_by("line_number").all())

        # first line saved correctly
        assert lines[0].line_number == 1
        assert lines[0].text == self.lyrics[0]
        assert lines[0].language == Language.objects.get(id="en")
        assert lines[0].start_time_millisecond == 0
        assert lines[0].song == song

        # last line saved correctly
        assert lines[-1].line_number == len(self.lyrics)
        assert lines[-1].text == self.lyrics[-1]
        assert lines[-1].language == Language.objects.get(id="en")
        assert lines[-1].start_time_millisecond == (len(self.lyrics) - 1) * 5000
        assert lines[-1].song == song

    def test_lyrics_attribute(self):
        song = Song.objects.first()

        lyrics = song.lyrics

        assert lyrics[0] == {
            "start": 0,
            "end": 5000,
            "text": self.lyrics[0],
        }

    def test_update_info_using_youtube_transcripts(self):
        song = Song.objects.first()

        transcripts = [
            {"text": "Hey there", "start": 7.58, "duration": 6.13},
            {"text": "how are you", "start": 14.08, "duration": 7.58},
        ]
        song._update_info_using_youtube_transcripts(transcripts)

        # make sure blanks were filled in correctly
        lyrics = song.lyrics

        assert lyrics == [
            {
                "start": 0,
                "end": 7580,
                "text": "",
            },
            {
                "start": 7580,
                "end": 13710,
                "text": "Hey there",
            },
            {
                "start": 13710,
                "end": 14080,
                "text": "",
            },
            {
                "start": 14080,
                "end": 21660,
                "text": "how are you",
            },
        ]
