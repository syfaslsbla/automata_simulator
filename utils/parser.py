"""
utils/parser.py
===============
Utilitas untuk parsing dan validasi input DFA dari antarmuka pengguna.
"""

from typing import Dict, List, Set, Tuple, Optional
from core.dfa import DFA


def parse_dfa_from_form(
    states_str: str,
    alphabet_str: str,
    start_state: str,
    accept_states_str: str,
    transitions_str: str
) -> Tuple[Optional[DFA], Optional[str]]:
    """
    Parse dan validasi input DFA dari form GUI.

    Format input:
        states_str      : "q0,q1,q2"
        alphabet_str    : "a,b"
        start_state     : "q0"
        accept_states_str: "q2"
        transitions_str : "q0,a,q1\nq1,b,q2\n..."

    Returns:
        (DFA, None) jika berhasil,
        (None, pesan_error) jika gagal.
    """
    try:
        # Parse states
        states = {s.strip() for s in states_str.split(',') if s.strip()}
        if not states:
            return None, "Himpunan state tidak boleh kosong."

        # Parse alphabet
        alphabet = {a.strip() for a in alphabet_str.split(',') if a.strip()}
        if not alphabet:
            return None, "Alphabet tidak boleh kosong."

        # Validasi start_state
        start = start_state.strip()
        if not start:
            return None, "State awal tidak boleh kosong."
        if start not in states:
            return None, f"State awal '{start}' tidak ada dalam himpunan state."

        # Parse accept states
        accept_states = {s.strip() for s in accept_states_str.split(',') if s.strip()}
        if not accept_states:
            return None, "Himpunan accepting state tidak boleh kosong."
        for s in accept_states:
            if s not in states:
                return None, f"Accepting state '{s}' tidak ada dalam himpunan state."

        # Parse fungsi transisi
        transitions: Dict[Tuple[str, str], str] = {}
        for line in transitions_str.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) != 3:
                return None, (
                    f"Format transisi salah: '{line}'. "
                    f"Gunakan format: state_asal,simbol,state_tujuan"
                )
            src, sym, dst = parts
            if src not in states:
                return None, f"State asal '{src}' tidak ada dalam himpunan state."
            if sym not in alphabet:
                return None, f"Simbol '{sym}' tidak ada dalam alphabet."
            if dst not in states:
                return None, f"State tujuan '{dst}' tidak ada dalam himpunan state."
            key = (src, sym)
            if key in transitions:
                return None, (
                    f"DFA tidak deterministik: ada lebih dari satu transisi "
                    f"dari '{src}' dengan simbol '{sym}'."
                )
            transitions[key] = dst

        dfa = DFA(
            states=states,
            alphabet=alphabet,
            start_state=start,
            accept_states=accept_states,
            transitions=transitions
        )
        return dfa, None

    except Exception as e:
        return None, f"Error saat parsing DFA: {str(e)}"


def validate_input_string(input_str: str, alphabet: Set[str]) -> Optional[str]:
    """
    Validasi bahwa setiap karakter dalam input_str ada di alphabet.

    Returns:
        None jika valid, pesan error jika tidak valid.
    """
    for c in input_str:
        if c not in alphabet:
            return f"Karakter '{c}' tidak ada dalam alphabet {alphabet}."
    return None


def format_transition_table(dfa: DFA) -> List[List[str]]:
    """
    Buat tabel transisi DFA dalam format list-of-lists.

    Returns:
        Baris pertama: header (State | a | b | ...)
        Baris berikutnya: isi transisi
    """
    from typing import List
    sorted_alphabet = sorted(dfa.alphabet)
    header = ["State"] + sorted_alphabet

    rows = [header]
    for state in sorted(dfa.states):
        prefix = ""
        if state == dfa.start_state:
            prefix += "→ "
        if state in dfa.accept_states:
            prefix += "* "
        row = [prefix + state]
        for sym in sorted_alphabet:
            dest = dfa.transitions.get((state, sym), "-")
            row.append(dest)
        rows.append(row)
    return rows


def format_nfa_transition_table(nfa) -> List[List[str]]:
    """
    Buat tabel transisi NFA dalam format list-of-lists.
    Kolom tambahan untuk epsilon transitions.
    """
    from core.nfa import EPSILON
    from typing import List

    sorted_alphabet = sorted(nfa.alphabet) + [EPSILON]
    header = ["State"] + sorted_alphabet

    rows = [header]
    for state in sorted(nfa.states):
        prefix = ""
        if state == nfa.start_state:
            prefix += "→ "
        if state in nfa.accept_states:
            prefix += "* "
        row = [prefix + state]
        for sym in sorted_alphabet:
            dests = nfa.transitions.get((state, sym), set())
            row.append("{" + ", ".join(sorted(dests)) + "}" if dests else "∅")
        rows.append(row)
    return rows
