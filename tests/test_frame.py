import lingkernel
from lingkernel.frame import collapse_reading, frame_text

PLAIN = ("The bridge was finished in 1932. It carried trains for forty years, and then the "
         "city turned it into a footpath. People still argue about whether that was the right "
         "call, because the rail link was never replaced. Most residents walk it on weekends.")


def test_plain_text_is_identical_and_reads_like_measure():
    f = frame_text(PLAIN)
    assert f.identical and f.text == PLAIN and not f.edits.any
    r = lingkernel.read(PLAIN)
    assert r["raw"] == r["framed"]
    assert all(v == 0 for v in r["delta"].values())
    direct = lingkernel.measure(PLAIN)
    for k in lingkernel.KERNEL_KEYS:
        assert r["raw"][k] == direct[k]


def test_bullets_and_inline_bold_untouched():
    assert frame_text("Steps:\n- Boil water\n- Add salt\n1. Stir\n2. Serve").identical
    assert frame_text("This is **very** important.").identical


def test_code_block_removed():
    f = frame_text("Use this:\n```python\nprint('hi')\nx = 1\n```\nThat prints hi.")
    assert "print('hi')" not in f.text and f.edits.code_blocks == 1 and f.edits.code_lines == 4
    assert "That prints hi." in f.text


def test_unclosed_fence_flagged():
    f = frame_text("Here:\n```js\nfunction f() {")
    assert f.edits.unclosed_fence and "function" not in f.text


def test_headers_bold_lines_tables_links():
    assert frame_text("## Overview\nThe plan has two parts.").text == "The plan has two parts."
    assert frame_text("**Ingredients:**\nFlour and water.").text == "Flour and water."
    assert frame_text("First part.\n## Next\nSecond part.").text == "First part.\n\nSecond part."
    t = frame_text("Compare:\n| a | b |\n|---|---|\n| 1 | 2 |\nDone.")
    assert t.edits.table_lines == 3 and "|" not in t.text
    assert frame_text("See [the docs](https://example.com/a) for more.").text == "See the docs for more."


def test_language_and_length_gates():
    assert "non_latin_script" in frame_text("抱歉，您给出的句子似乎是混乱的字符和单词，我无法理解其含义。").reasons
    assert "no_letters" in frame_text("1120 = 4 * 280").reasons
    es = ("El puente fue terminado en mil novecientos treinta y dos y llevó trenes durante "
          "cuarenta años hasta que la ciudad lo convirtió en un paseo peatonal muy popular")
    assert "low_english_function_words" in frame_text(es).reasons
    f = frame_text("Hello! How can I help you today?")
    assert f.english and f.reasons == ["short_prose"]


def test_collapse_reading():
    assert collapse_reading({"collapse_subtype": "severe", "tail_incomplete_flag": False}) == "short_complete"
    tail = {"collapse_subtype": "severe", "tail_incomplete_flag": True}
    assert collapse_reading(tail, "Sure, here are the steps to") == "short_cut"
    assert collapse_reading(tail, "I can't help with that.") == "short_complete"
    assert collapse_reading({"collapse_subtype": "math"}) == "cut_code_or_math"
    assert collapse_reading({"collapse_subtype": "partial"}) == "cut_partial"
    r = lingkernel.read("I'm sorry, but I can't help with that.")
    assert r["raw"]["collapse_subtype"] == "severe" and r["collapse_reading"] == "short_complete"


def test_header_glue_reduced():
    t = ("## Background\nThe survey ran for two years. Results were mixed.\n\n"
         "## Findings\nMost sites improved. A few did not.")
    r = lingkernel.read(t)
    assert r["framed"]["delta_y"] < r["raw"]["delta_y"]


def test_special_token_marked_not_raised():
    r = lingkernel.read("This sentence contains <|endoftext|> and keeps going for a while longer here, "
                        "long enough to pass the length gate if the kernel could read it at all.")
    if r["kernel_error"]:  # only raised when tiktoken is installed
        assert not r["eligible"] and "kernel_error" in r["reasons"]


def test_read_row_is_flat():
    row = lingkernel.read_row(PLAIN)
    assert "raw_delta_y" in row and "framed_mu" in row and "edit_code_blocks" in row
