from urllib.parse import urlparse, parse_qs


def _get_language_using_text(text):
    text = text.lower()

    counts = {
        "ge": 0,
        "en": 0,
        "ru": 0,
        "de": 0,
        "cn": 0,
    }

    for character in text:
        chr_code = ord(character)

        if chr_code <= 122:
            counts["en"] += 1
        elif 4303 <= chr_code <= 4336:
            counts["ge"] += 1
        elif 1072 <= chr_code <= 1103:
            counts["ru"] += 1
        elif character in "ßäöüäöü":
            counts["de"] += 1
        elif 19968 <= ord(character) <= 40959:
            counts["cn"] += 1

    # as most letters are same as english for german texts...
    if counts["de"] >= 5:
        return "de"

    keys, values = list(counts.keys()), list(counts.values())
    max_value = max(values)

    if max_value > 0:
        result_lang = keys[values.index(max_value)]

        return result_lang

    return "XX"


def _get_youtube_video_id_from_url(url):
    """
    Currently supported url format:
        https://www.youtube.com/watch?v=TO-_3tck2tg

    """

    query = parse_qs(urlparse(url).query)

    try:
        youtube_id = query["v"][0]

        assert len(youtube_id) == 11

        return youtube_id

    except Exception:
        return None
