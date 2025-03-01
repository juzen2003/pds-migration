from typing import TYPE_CHECKING

from Parsers import bytes, repeat, rest_of_input
from VicarSyntax import VicarSyntax, maybe_bs, round_to_multiple_of

if TYPE_CHECKING:
    from typing import List, Optional, Tuple


def parse_pds3_tail(byte_str):
    # type: (str) -> Tuple[str, Tail]
    """Parse a PDS3 tail.  All the bytes go into the tail of the tail."""
    byte_str, res = rest_of_input(byte_str)
    if len(res) == 0:
        res = None
    return (byte_str, Tail(None, res))


def parse_pds4_tail(img_height, prefix_width, byte_str):
    # type: (int, int, str) -> Tuple[str, Tail]
    """
    Parse a PDS4 tail.  Some of the bytes may be parts of the binary
    prefixes.  The rest goes into the tail_bytes.  We determine what
    goes where from the integer arguments: the dimensions of the
    binary prefixes.
    """
    if prefix_width > 0:
        byte_str, prefs = repeat(img_height, bytes(prefix_width))(byte_str)
    else:
        prefs = None
    byte_str, rest = rest_of_input(byte_str)
    if len(rest) == 0:
        rest = None
    return byte_str, Tail(prefs, rest)


class Tail(VicarSyntax):
    """
    Represents the bytes in a VICAR file following the image area or
    EOL labels, if they exist.
    """

    def __init__(self,
                 binary_prefixes_at_tail,
                 tail_bytes):
        # type: (Optional[List[str]], Optional[str]) -> None
        VicarSyntax.__init__(self)
        if binary_prefixes_at_tail:
            for binary_prefix in binary_prefixes_at_tail:
                assert binary_prefix is not None
        self.binary_prefixes_at_tail = binary_prefixes_at_tail
        self.tail_bytes = tail_bytes

    def __eq__(self, other):
        return [self.binary_prefixes_at_tail,
                self.tail_bytes] == [other.binary_prefixes_at_tail,
                                     other.tail_bytes]

    def __repr__(self):
        return 'Tail(%r, %r)' % (self.binary_prefixes_at_tail,
                                     self.tail_bytes)

    def to_byte_string(self):
        if self.binary_prefixes_at_tail:
            binary_prefixes = ''.join(self.binary_prefixes_at_tail)
        else:
            binary_prefixes = ''
        return ''.join([binary_prefixes,
                        maybe_bs(self.tail_bytes)])

    def has_binary_prefixes(self):
        # type: () -> bool
        """
        Return True if binary prefixes are stored in the tail.
        """
        return self.binary_prefixes_at_tail is not None

    @staticmethod
    def create_with_padding(recsize,
                            binary_prefixes_at_tail,
                            tail_bytes):
        # type: (int, List[str], str) -> Tail
        """
        Create a tail from the parts, adding padding to make it a
        multiple of RECSIZE.
        """
        if tail_bytes is None:
            tail_bytes = ''
        unadjusted_length = Tail(binary_prefixes_at_tail,
                                 tail_bytes).to_byte_length()
        final_length = round_to_multiple_of(unadjusted_length, recsize)
        new_padding_length = final_length - unadjusted_length
        padded_tail_bytes = tail_bytes + new_padding_length * '\0'
        if len(padded_tail_bytes) == 0:
            padded_tail_bytes = None
        return Tail(binary_prefixes_at_tail,
                    padded_tail_bytes)


