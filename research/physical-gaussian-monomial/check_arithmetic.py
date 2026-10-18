"""Encoded phase, signed-pair and unused-descriptor obligations."""
import check_components
import check_phase_control
import check_unused_parameter


def run():
    return dict(components=check_components.run(),phases=check_phase_control.run(),
                unused_parameter=check_unused_parameter.run())
