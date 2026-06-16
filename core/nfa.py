"""
core/nfa.py
===========
Modul NFA dan Thompson Construction untuk konversi Regex → NFA.

Algoritma yang digunakan:
- Thompson Construction: Setiap operator regex (concat, union, star)
  diimplementasikan sebagai NFA kecil yang digabungkan.
  Epsilon transition (ε) digunakan untuk menghubungkan sub-NFA.
- Epsilon-closure: BFS/DFS untuk menemukan semua state yang dapat
  dicapai dari sebuah state hanya dengan ε-transitions.
- Simulasi NFA: Subset construction (on-the-fly) menggunakan
  himpunan state aktif.
"""

from typing import Dict, List, Set, Optional, Tuple, FrozenSet


EPSILON = 'ε'  # Simbol epsilon untuk transisi kosong


class NFA:
    """
    Representasi NFA (Nondeterministic Finite Automaton).

    Perbedaan utama dengan DFA:
    - Transisi bisa ke BANYAK state untuk satu simbol.
    - Ada epsilon-transitions (transisi tanpa membaca simbol).

    Atribut:
        states           : Himpunan semua state
        alphabet         : Himpunan simbol alphabet (tidak termasuk ε)
        start_state      : State awal (satu state)
        accept_states    : Himpunan state penerima
        transitions      : Dict[(state, symbol)] → Set[state]
                           (berbeda DFA: satu key bisa ke banyak state)
    """

    def __init__(
        self,
        states: Set[str],
        alphabet: Set[str],
        start_state: str,
        accept_states: Set[str],
        transitions: Dict[Tuple[str, str], Set[str]]
    ):
        self.states = states
        self.alphabet = alphabet
        self.start_state = start_state
        self.accept_states = accept_states
        self.transitions = transitions

    def epsilon_closure(self, states: Set[str]) -> Set[str]:
        """
        Hitung epsilon-closure dari himpunan state.

        Definisi: ε-closure(T) = himpunan semua state yang dapat dicapai
        dari state mana pun di T hanya menggunakan ε-transitions.

        Algoritma: DFS/BFS dari setiap state di T, ikuti ε-transitions.

        Args:
            states: Himpunan state awal

        Returns:
            Himpunan state dalam ε-closure
        """
        closure = set(states)
        stack = list(states)
        while stack:
            s = stack.pop()
            for ns in self.transitions.get((s, EPSILON), set()):
                if ns not in closure:
                    closure.add(ns)
                    stack.append(ns)
        return closure

    def simulate(self, input_string: str) -> Tuple[bool, List[dict]]:
        """
        Simulasi NFA pada input_string menggunakan subset construction on-the-fly.

        Algoritma:
        1. Mulai dari ε-closure({start_state}).
        2. Untuk setiap simbol a dalam input_string:
            a. Hitung move(current_states, a) = union semua δ(q, a) untuk q ∈ current_states.
            b. Hitung ε-closure dari move tersebut.
        3. String diterima jika state_set akhir ∩ accept_states ≠ ∅.

        Returns:
            (accepted: bool, steps: list[dict])
        """
        current_states = self.epsilon_closure({self.start_state})
        steps = []

        steps.append({
            "step": 0,
            "current_states": sorted(current_states),
            "symbol": None,
            "next_states": None,
            "description": f"Mulai: ε-closure({{{self.start_state}}}) = {{{', '.join(sorted(current_states))}}}"
        })

        for i, char in enumerate(input_string):
            # Move: kumpulkan semua state yang dapat dicapai dengan char
            moved = set()
            for s in current_states:
                moved |= self.transitions.get((s, char), set())

            # Hitung epsilon-closure dari hasil move
            next_states = self.epsilon_closure(moved)

            steps.append({
                "step": i + 1,
                "current_states": sorted(current_states),
                "symbol": char,
                "next_states": sorted(next_states),
                "description": (
                    f"Baca '{char}': move = {{{', '.join(sorted(moved))}}} "
                    f"→ ε-closure = {{{', '.join(sorted(next_states))}}}"
                )
            })
            current_states = next_states

        # Cek apakah ada accepting state di current_states
        final_accepts = current_states & self.accept_states
        accepted = len(final_accepts) > 0

        steps.append({
            "step": len(input_string) + 1,
            "current_states": sorted(current_states),
            "symbol": None,
            "next_states": None,
            "description": (
                f"State akhir {{{', '.join(sorted(current_states))}}} ∩ "
                f"accept_states = {{{', '.join(sorted(final_accepts))}}} → "
                f"{'DITERIMA' if accepted else 'DITOLAK'}"
            )
        })
        return accepted, steps

    def to_dict(self) -> dict:
        """Serialisasi NFA ke dictionary."""
        trans = {}
        for (s, a), ns in self.transitions.items():
            trans[f"{s},{a}"] = sorted(ns)
        return {
            "states": sorted(self.states),
            "alphabet": sorted(self.alphabet),
            "start_state": self.start_state,
            "accept_states": sorted(self.accept_states),
            "transitions": trans
        }


# ======================================================================== #
#  THOMPSON CONSTRUCTION: Regular Expression → NFA                         #
# ======================================================================== #

class ThompsonConstruction:
    """
    Konversi Regular Expression ke NFA menggunakan Thompson Construction.

    Operator yang didukung (dalam urutan presedensi, terendah ke tertinggi):
        |   : Union / Alternation  (a|b  berarti a ATAU b)
        ·   : Concatenation         (ab   berarti a diikuti b)
        *   : Kleene Star           (a*   berarti nol atau lebih a)
        +   : One or More           (a+   = aa*)
        ?   : Zero or One           (a?   = a|ε)
        ( ) : Pengelompokan

    Aturan Thompson Construction:
    - Setiap literal karakter → NFA dua state (q_i --a--> q_f).
    - UNION(N1, N2)    : State baru dengan ε ke start N1 dan N2,
                         accept N1 dan N2 dengan ε ke state final baru.
    - CONCAT(N1, N2)   : Accept state N1 menjadi start N2 (ε-transition).
    - STAR(N)          : State baru dengan ε ke start N dan ke final baru;
                         accept N dengan ε kembali ke start N dan ke final baru.
    """

    def __init__(self):
        self._counter = 0

    def _new_state(self) -> str:
        """Buat nama state baru yang unik."""
        s = f"q{self._counter}"
        self._counter += 1
        return s

    def _make_literal(self, char: str) -> NFA:
        """
        NFA untuk satu karakter literal.

        Struktur:
            q_start --char--> q_accept
        """
        s = self._new_state()
        a = self._new_state()
        return NFA(
            states={s, a},
            alphabet={char} if char != EPSILON else set(),
            start_state=s,
            accept_states={a},
            transitions={(s, char): {a}}
        )

    def _make_epsilon(self) -> NFA:
        """NFA untuk string kosong (ε)."""
        return self._make_literal(EPSILON)

    def _make_union(self, n1: NFA, n2: NFA) -> NFA:
        """
        NFA untuk n1 | n2.

        Struktur:
            q_new_start --ε--> start(N1)
            q_new_start --ε--> start(N2)
            accept(N1)  --ε--> q_new_accept
            accept(N2)  --ε--> q_new_accept
        """
        new_start = self._new_state()
        new_accept = self._new_state()

        trans = {}
        # Salin transisi N1 dan N2
        for k, v in n1.transitions.items():
            trans[k] = set(v)
        for k, v in n2.transitions.items():
            trans[k] = set(v)

        # ε dari new_start ke start masing-masing NFA
        trans[(new_start, EPSILON)] = {n1.start_state, n2.start_state}

        # ε dari accept masing-masing ke new_accept
        for s in n1.accept_states:
            trans.setdefault((s, EPSILON), set()).add(new_accept)
        for s in n2.accept_states:
            trans.setdefault((s, EPSILON), set()).add(new_accept)

        return NFA(
            states=n1.states | n2.states | {new_start, new_accept},
            alphabet=n1.alphabet | n2.alphabet,
            start_state=new_start,
            accept_states={new_accept},
            transitions=trans
        )

    def _make_concat(self, n1: NFA, n2: NFA) -> NFA:
        """
        NFA untuk n1n2 (concatenation).

        Struktur:
            accept(N1) --ε--> start(N2)
        """
        trans = {}
        for k, v in n1.transitions.items():
            trans[k] = set(v)
        for k, v in n2.transitions.items():
            trans[k] = set(v)

        # ε dari setiap accept N1 ke start N2
        for s in n1.accept_states:
            trans.setdefault((s, EPSILON), set()).add(n2.start_state)

        return NFA(
            states=n1.states | n2.states,
            alphabet=n1.alphabet | n2.alphabet,
            start_state=n1.start_state,
            accept_states=n2.accept_states,
            transitions=trans
        )

    def _make_star(self, n: NFA) -> NFA:
        """
        NFA untuk n* (Kleene Star, nol atau lebih).

        Struktur:
            q_new_start --ε--> start(N)
            q_new_start --ε--> q_new_accept  (terima string kosong)
            accept(N)   --ε--> start(N)      (loop)
            accept(N)   --ε--> q_new_accept
        """
        new_start = self._new_state()
        new_accept = self._new_state()

        trans = {}
        for k, v in n.transitions.items():
            trans[k] = set(v)

        # ε dari new_start
        trans[(new_start, EPSILON)] = {n.start_state, new_accept}

        # ε dari accept(N) – loop dan ke new_accept
        for s in n.accept_states:
            trans.setdefault((s, EPSILON), set()).update({n.start_state, new_accept})

        return NFA(
            states=n.states | {new_start, new_accept},
            alphabet=n.alphabet,
            start_state=new_start,
            accept_states={new_accept},
            transitions=trans
        )

    def _make_plus(self, n: NFA) -> NFA:
        """NFA untuk n+ (satu atau lebih) = concat(N, star(N))."""
        return self._make_concat(n, self._make_star(n))

    def _make_question(self, n: NFA) -> NFA:
        """NFA untuk n? (nol atau satu) = union(N, epsilon)."""
        return self._make_union(n, self._make_epsilon())

    # ------------------------------------------------------------------ #
    #  PARSER REGEX                                                        #
    # ------------------------------------------------------------------ #

    def regex_to_nfa(self, regex: str) -> NFA:
        """
        Konversi regular expression ke NFA.

        Menggunakan recursive descent parser dengan presedensi:
        alternation (|) < concatenation < postfix (*, +, ?)

        Args:
            regex: String regular expression

        Returns:
            NFA yang ekuivalen dengan regex
        """
        self._counter = 0  # Reset counter state
        self._regex = regex
        self._pos = 0
        return self._parse_alternation()

    def _peek(self) -> Optional[str]:
        """Lihat karakter saat ini tanpa memajukan posisi."""
        if self._pos < len(self._regex):
            return self._regex[self._pos]
        return None

    def _consume(self, char: Optional[str] = None) -> str:
        """Konsumsi karakter saat ini."""
        c = self._regex[self._pos]
        if char is not None and c != char:
            raise ValueError(f"Expected '{char}' but got '{c}' at position {self._pos}")
        self._pos += 1
        return c

    def _parse_alternation(self) -> NFA:
        """Parse: expr | expr | ..."""
        nfa = self._parse_concat()
        while self._peek() == '|':
            self._consume('|')
            right = self._parse_concat()
            nfa = self._make_union(nfa, right)
        return nfa

    def _parse_concat(self) -> NFA:
        """Parse: expr expr ..."""
        nfa = self._parse_postfix()
        while self._peek() not in (None, ')', '|'):
            right = self._parse_postfix()
            nfa = self._make_concat(nfa, right)
        return nfa

    def _parse_postfix(self) -> NFA:
        """Parse: atom (* | + | ?)"""
        nfa = self._parse_atom()
        while self._peek() in ('*', '+', '?'):
            op = self._consume()
            if op == '*':
                nfa = self._make_star(nfa)
            elif op == '+':
                nfa = self._make_plus(nfa)
            elif op == '?':
                nfa = self._make_question(nfa)
        return nfa

    def _parse_atom(self) -> NFA:
        """Parse: literal | ( expr ) | ε """
        c = self._peek()
        if c == '(':
            self._consume('(')
            nfa = self._parse_alternation()
            self._consume(')')
            return nfa
        elif c == EPSILON or c == 'ε':
            self._consume()
            return self._make_epsilon()
        elif c is not None and c not in ('|', ')', '*', '+', '?'):
            self._consume()
            return self._make_literal(c)
        else:
            raise ValueError(
                f"Unexpected character '{c}' at position {self._pos} in regex '{self._regex}'"
            )


def test_regex_direct(regex: str, input_string: str) -> bool:
    """
    Uji string langsung terhadap regex menggunakan Python's re module
    sebagai referensi tambahan.

    Args:
        regex        : Regular expression
        input_string : String yang diuji

    Returns:
        True jika string cocok (full match), False jika tidak
    """
    import re
    # Ganti ε dengan string kosong untuk Python re
    py_regex = regex.replace('ε', '')
    try:
        return bool(re.fullmatch(py_regex, input_string))
    except re.error:
        return False
