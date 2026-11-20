"""Signed word multiplication, with a fixed base case and a bound file-backed child."""
from pathlib import Path
from hashlib import sha256
import subprocess
import sys


BASE_BITS = 8192
SOURCES = {
    "fft_word_sources.py": "46f40da411e3779b407bb11a0f7f1526b2d8611c1c6c1ab54f12f0cc00f8ebc2",
    "fft_word_engine.py": "4b2ed4bb244a4b7537432e33706caf2abe19e44ab50cbc0a78db135e9581dee1",
    "fft_word_codec.py": "d13f25fc215aa28570ca750afb7153f38d7fb62f92d28e404bb84396e2a90768",
    "fft_word_plan.py": "f8fff468b77753aa5f0d446c5d4381653659253051c1fcd066cd3b345cffd7c1",
}


def base_product(a, b):
    x, y = abs(a), abs(b)
    if not x or not y:
        return 0
    # Dyadic gauges and lifted operands often have long runs of zero low bits.
    shift_x = (x & -x).bit_length()-1
    shift_y = (y & -y).bit_length()-1
    x >>= shift_x
    y >>= shift_y
    if x < y:
        x, y = y, x
    if y == 1:
        acc = x
    else:
        multiples = [0]
        for _ in range(15):
            multiples.append(multiples[-1]+x)
        acc = 0
        for byte in y.to_bytes((y.bit_length()+7)//8,"big"):
            acc = (acc << 4)+multiples[byte >> 4]
            acc = (acc << 4)+multiples[byte & 15]
    acc <<= shift_x+shift_y
    return -acc if (a < 0) != (b < 0) else acc


def physical_product(a, b):
    width = max(1, a.bit_length(), b.bit_length())
    count = (width+7)//8
    packet = (f"{width:x}\n".encode("ascii") + abs(a).to_bytes(count, "little")
              + abs(b).to_bytes(count, "little"))
    reply = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--physical-word"],
                           input=packet, stdout=subprocess.PIPE, check=True).stdout
    if len(reply) != (2*width+7)//8:
        raise ArithmeticError("incomplete physical word")
    value = int.from_bytes(reply, "little")
    return -value if (a < 0) != (b < 0) else value


def product(a, b, trace):
    width = max(a.bit_length(), b.bit_length())
    trace.scalar_products += 1
    trace.max_scalar_operand = max(trace.max_scalar_operand, width)
    if width <= BASE_BITS:
        return base_product(a, b)
    trace.fast_words += 1
    return physical_product(a, b)


def physical_worker():
    """Bind the exact positive word on owned source tapes in a cold process."""
    paths = (parent/"research"/"physical-fft-word" for parent in Path(__file__).resolve().parents)
    source_dir = next((path for path in paths if (path/"fft_word_engine.py").is_file()), None)
    if source_dir is None:
        raise FileNotFoundError("research/physical-fft-word inside this source tree")
    if any(sha256((source_dir/name).read_bytes()).hexdigest()!=digest for name,digest in SOURCES.items()):
        raise ValueError("physical FFT word source changed")
    sys.path.insert(0, str(source_dir))
    from fft_word_sources import opened
    with opened():
        from cardinal_counts import Count
        from fft_word_engine import FftWord
        from records import Tape
        from session import erase_marker
        from words import BLANK, RIGHT

        def count_of(data, bits):
            tape = Tape()
            for i in range(bits):
                tape.append((data[i//8] >> (i%8)) & 1)
            tape.append(RIGHT)
            tape.rewind()
            encoded = Count(tape)
            tape.clear()
            erase_marker(tape)
            return encoded

        width = int(sys.stdin.buffer.readline(), 16)
        count = (width+7)//8
        first, second = (count_of(sys.stdin.buffer.read(count), width) for _ in range(2))
        encoded_width = count_of(width.to_bytes((width.bit_length()+7)//8, "little"), width.bit_length())
        owner = FftWord()
        output = owner.run(first, second, encoded_width)
        answer = bytearray()
        digit = 0
        for i in range(2*width):
            bit = output.read()
            if bit not in (0, 1):
                raise ArithmeticError("physical word bit expected")
            digit |= bit << (i%8)
            output.step(1)
            if i%8 == 7 or i+1 == 2*width:
                answer.append(digit)
                digit = 0
        if output.read() != BLANK:
            raise ArithmeticError("physical word extent")
        output.clear()
        erase_marker(output)
        owner.idle()
        for value in (first, second, encoded_width):
            value.close()
            erase_marker(value.tape)
        sys.stdout.buffer.write(answer)


if __name__ == "__main__" and sys.argv[1:] == ["--physical-word"]:
    physical_worker()
