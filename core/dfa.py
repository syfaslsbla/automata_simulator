"""
core/dfa.py
===========
Modul inti untuk Deterministic Finite Automata (DFA).

Algoritma yang digunakan:
- Simulasi DFA: Membaca setiap karakter input satu per satu,
  melakukan transisi state berdasarkan fungsi transisi delta(q, a),
  dan mengecek apakah state akhir termasuk accepting states.
- Minimasi DFA: Algoritma Table-Filling (Myhill-Nerode) menggunakan
  pendekatan partisi untuk mengelompokkan state yang ekuivalen.
- Cek Ekuivalensi: Menggunakan product construction atau BFS/DFS
  pada perbedaan simetris dua DFA.
"""

from typing import Dict, List, Set, Optional, Tuple


class DFA:
    """
    Representasi DFA (Deterministic Finite Automaton).

    Atribut:
        states       : Himpunan semua state
        alphabet     : Himpunan simbol alphabet
        start_state  : State awal
        accept_states: Himpunan state penerima (final states)
        transitions  : Fungsi transisi delta: (state, symbol) -> state
    """

    def __init__(
        self,
        states: Set[str],
        alphabet: Set[str],
        start_state: str,
        accept_states: Set[str],
        transitions: Dict[Tuple[str, str], str]
    ):
        self.states = states
        self.alphabet = alphabet
        self.start_state = start_state
        self.accept_states = accept_states
        self.transitions = transitions

    # ------------------------------------------------------------------ #
    #  FITUR 1 – SIMULASI DFA                                             #
    # ------------------------------------------------------------------ #

    def simulate(self, input_string: str) -> Tuple[bool, List[dict]]:
        """
        Jalankan simulasi DFA terhadap input_string.

        Algoritma:
        1. Mulai dari start_state.
        2. Untuk setiap karakter c dalam input_string:
            a. Cari transisi delta(current_state, c).
            b. Jika tidak ada transisi → string ditolak (dead state).
            c. Pindah ke state berikutnya.
        3. Setelah semua karakter dibaca, cek apakah current_state
           ada di accept_states.

        Returns:
            (accepted: bool, steps: list[dict])
            steps berisi log setiap langkah perpindahan state.
        """
        current_state = self.start_state
        steps = []

        # Log langkah awal
        steps.append({
            "step": 0,
            "current_state": current_state,
            "symbol": None,
            "next_state": None,
            "description": f"Mulai dari state awal: {current_state}"
        })

        for i, char in enumerate(input_string):
            key = (current_state, char)
            if key not in self.transitions:
                # Dead state – tidak ada transisi untuk simbol ini
                steps.append({
                    "step": i + 1,
                    "current_state": current_state,
                    "symbol": char,
                    "next_state": "DEAD",
                    "description": f"Tidak ada transisi dari '{current_state}' dengan simbol '{char}'"
                })
                return False, steps

            next_state = self.transitions[key]
            steps.append({
                "step": i + 1,
                "current_state": current_state,
                "symbol": char,
                "next_state": next_state,
                "description": f"δ({current_state}, {char}) → {next_state}"
            })
            current_state = next_state

        accepted = current_state in self.accept_states
        steps.append({
            "step": len(input_string) + 1,
            "current_state": current_state,
            "symbol": None,
            "next_state": None,
            "description": (
                f"State akhir '{current_state}' adalah accepting state → DITERIMA"
                if accepted else
                f"State akhir '{current_state}' BUKAN accepting state → DITOLAK"
            )
        })
        return accepted, steps

    # ------------------------------------------------------------------ #
    #  FITUR 3 – MINIMASI DFA                                             #
    # ------------------------------------------------------------------ #

    def minimize(self) -> Tuple['DFA', Dict[str, str], List[Set[str]]]:
        """
        Minimasi DFA menggunakan algoritma Table-Filling (Myhill-Nerode).

        Algoritma Table-Filling:
        1. Buat tabel pasangan state (qi, qj) dengan i < j.
        2. Tandai pasangan (accepting, non-accepting) sebagai distinguishable.
        3. Iterasi: untuk setiap pasangan (p, q) yang belum ditandai,
           tandai jika terdapat simbol a sehingga
           (δ(p,a), δ(q,a)) sudah ditandai.
        4. Ulangi langkah 3 sampai tidak ada pasangan baru yang ditandai.
        5. Pasangan yang tidak ditandai → state-state yang ekuivalen
           (dapat digabungkan).
        6. Bangun DFA baru dari partisi state ekuivalen.

        Returns:
            (minimized_dfa, state_mapping, merged_groups)
            - minimized_dfa  : DFA hasil minimasi
            - state_mapping  : mapping state lama → state baru
            - merged_groups  : daftar grup state yang digabungkan
        """
        # Pastikan semua state terhubung (reachable dari start_state)
        reachable = self._get_reachable_states()
        states_list = sorted(reachable)
        n = len(states_list)

        # Tabel distinguishable: (i, j) -> bool (i < j)
        distinguishable: Dict[Tuple[int, int], bool] = {}
        idx = {s: i for i, s in enumerate(states_list)}

        def pair(a, b):
            i, j = idx[a], idx[b]
            return (min(i, j), max(i, j))

        # Langkah 2 – tandai pasangan (final, non-final)
        for p in states_list:
            for q in states_list:
                if p < q:
                    key = pair(p, q)
                    p_accept = p in self.accept_states
                    q_accept = q in self.accept_states
                    if p_accept != q_accept:
                        distinguishable[key] = True

        # Langkah 3 & 4 – iterasi sampai stabil
        changed = True
        while changed:
            changed = False
            for p in states_list:
                for q in states_list:
                    if p >= q:
                        continue
                    key = pair(p, q)
                    if distinguishable.get(key, False):
                        continue
                    for a in self.alphabet:
                        dp = self.transitions.get((p, a))
                        dq = self.transitions.get((q, a))
                        if dp is None or dq is None:
                            continue
                        if dp == dq:
                            continue
                        k2 = pair(dp, dq)
                        if distinguishable.get(k2, False):
                            distinguishable[key] = True
                            changed = True
                            break

        # Langkah 5 – bangun partisi (grup ekuivalen)
        parent = {s: s for s in states_list}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[ry] = rx

        for p in states_list:
            for q in states_list:
                if p < q:
                    key = pair(p, q)
                    if not distinguishable.get(key, False):
                        union(p, q)

        # Kumpulkan grup
        groups: Dict[str, Set[str]] = {}
        for s in states_list:
            root = find(s)
            groups.setdefault(root, set()).add(s)

        # Beri nama state baru
        merged_groups = list(groups.values())
        rep_to_name: Dict[str, str] = {}
        for i, (root, group) in enumerate(groups.items()):
            # Periksa apakah start_state ada di grup ini
            if self.start_state in group:
                rep_to_name[root] = "q0"
            else:
                rep_to_name[root] = f"q{i}"

        # Pastikan nama unik (q0 sudah dipakai)
        used_names = set(rep_to_name.values())
        counter = 0
        for root in groups:
            if rep_to_name[root] == "q0":
                continue
            while rep_to_name[root] in used_names - {rep_to_name[root]}:
                counter += 1
                rep_to_name[root] = f"q{counter}"

        # Mapping state lama → nama baru
        state_mapping: Dict[str, str] = {}
        for root, group in groups.items():
            new_name = rep_to_name[root]
            for s in group:
                state_mapping[s] = new_name

        # Langkah 6 – bangun DFA baru
        new_states = set(state_mapping.values())
        new_start = state_mapping[self.start_state]
        new_accept = {state_mapping[s] for s in self.accept_states if s in reachable}
        new_transitions: Dict[Tuple[str, str], str] = {}

        for root, group in groups.items():
            rep = next(iter(group))  # Wakil dari grup
            new_name = rep_to_name[root]
            for a in self.alphabet:
                if (rep, a) in self.transitions:
                    dest = self.transitions[(rep, a)]
                    if dest in reachable:
                        new_transitions[(new_name, a)] = state_mapping[dest]

        min_dfa = DFA(
            states=new_states,
            alphabet=self.alphabet,
            start_state=new_start,
            accept_states=new_accept,
            transitions=new_transitions
        )
        return min_dfa, state_mapping, merged_groups

    def _get_reachable_states(self) -> Set[str]:
        """BFS untuk menemukan semua state yang reachable dari start_state."""
        visited = set()
        queue = [self.start_state]
        while queue:
            s = queue.pop(0)
            if s in visited:
                continue
            visited.add(s)
            for a in self.alphabet:
                nxt = self.transitions.get((s, a))
                if nxt and nxt not in visited:
                    queue.append(nxt)
        return visited

    # ------------------------------------------------------------------ #
    #  FITUR 4 – CEK EKUIVALENSI DUA DFA                                  #
    # ------------------------------------------------------------------ #

    def is_equivalent_to(self, other: 'DFA') -> Tuple[bool, Optional[str]]:
        """
        Cek apakah dua DFA menerima bahasa yang sama.

        Algoritma (Product Construction + BFS):
        Buat automaton produk dari kedua DFA. State produk adalah pasangan
        (s1, s2) di mana s1 ∈ DFA1 dan s2 ∈ DFA2.
        Dua DFA ekuivalen ↔ tidak ada state produk (s1, s2) yang reachable
        di mana tepat satu dari s1 atau s2 adalah accepting state.

        Jika tidak ekuivalen, kembalikan counterexample (string yang
        diterima oleh salah satu DFA tapi tidak oleh yang lain).

        Returns:
            (is_equivalent: bool, counterexample: str | None)
        """
        # BFS pada automaton produk
        start = (self.start_state, other.start_state)
        visited = {}
        queue = [(start, "")]  # (state_pair, string_so_far)

        while queue:
            (s1, s2), path = queue.pop(0)
            if (s1, s2) in visited:
                continue
            visited[(s1, s2)] = path

            a1 = (s1 in self.accept_states)
            a2 = (s2 in other.accept_states)

            if a1 != a2:
                # Ditemukan state yang membedakan – tidak ekuivalen
                return False, path

            # Ekspansi ke state berikutnya
            combined_alphabet = self.alphabet | other.alphabet
            for sym in sorted(combined_alphabet):
                ns1 = self.transitions.get((s1, sym)) if sym in self.alphabet else None
                ns2 = other.transitions.get((s2, sym)) if sym in other.alphabet else None

                # Jika salah satu tidak punya transisi, anggap dead state
                ns1 = ns1 if ns1 else f"_dead_{self.start_state}"
                ns2 = ns2 if ns2 else f"_dead_{other.start_state}"

                if (ns1, ns2) not in visited:
                    queue.append(((ns1, ns2), path + sym))

        return True, None

    def to_dict(self) -> dict:
        """Serialisasi DFA ke dictionary (untuk keperluan GUI)."""
        return {
            "states": sorted(self.states),
            "alphabet": sorted(self.alphabet),
            "start_state": self.start_state,
            "accept_states": sorted(self.accept_states),
            "transitions": {f"{k[0]},{k[1]}": v for k, v in self.transitions.items()}
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DFA':
        """Deserialisasi DFA dari dictionary."""
        transitions = {
            (k.split(",")[0], k.split(",")[1]): v
            for k, v in data["transitions"].items()
        }
        return cls(
            states=set(data["states"]),
            alphabet=set(data["alphabet"]),
            start_state=data["start_state"],
            accept_states=set(data["accept_states"]),
            transitions=transitions
        )
