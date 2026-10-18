"""One bounded replay of the arithmetic-to-payload boundary."""
import check_callback
import check_words
import controls
from sources import compile_templates


def run():
    three, five = compile_templates(3), compile_templates(5)
    return {
        "source_checkpoints": check_callback.source_checkpoints(three),
        "binary_words": check_words.run(),
        "binary_counters": check_callback.counter_cases(),
        "matrix_preparation": check_callback.matrix_cases(three, extra=five[1]),
        "callbacks": [
            check_callback.one_callback(three[0], "good", variant=0),
            check_callback.one_callback(three[0], "good", variant=1),
            check_callback.one_callback(three[0], "good", variant=2),
            check_callback.one_callback(three[0], "pair_forward"),
            check_callback.one_callback(three[0], "pair_reverse"),
            check_callback.one_callback(three[0], "unit_reset", variant=1),
            check_callback.one_callback(three[0], "orientation_reset", variant=2),
            check_callback.one_callback(five[0], "good", variant=1),
            check_callback.one_callback(three[0], "good", width=3, root_size=2**600),
        ],
        "complete_payload_site": check_callback.payload_site(three[0]),
        "rejection_controls": controls.callback_controls(three[0]),
        "source_barrier": controls.source_barrier(),
        "large_source_codes": controls.large_source_codes(three[0]),
        "scope": "Closed binary arithmetic/index/offset callback and complete finite ADD site. Fixed source compilation and checker oracles remain outside execution. No selected global caller or multiplication-exponent claim.",
    }
